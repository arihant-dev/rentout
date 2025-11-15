import os
import asyncio
from typing import Optional

try:
    import openai # type: ignore
except Exception:
    openai = None

try:
    import httpx # type: ignore
except Exception:
    httpx = None

try:
    from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT # type: ignore
except Exception:
    Anthropic = None

try:
    from google.cloud import aiplatform
except Exception:
    aiplatform = None


async def run_llm(text: str, provider: Optional[str] = None, model: Optional[str] = None) -> str:
    """Run a text prompt against a configured LLM provider.

    Provider selection order:
    - `provider` argument (if provided)
    - `LLM_PROVIDER` environment variable
    - defaults to `anthropic` if available

    Supported providers (implemented here): `openai`, `huggingface`, `anthropic`, `google`.
    This function is intentionally small and provider adapters are lightweight; add more
    providers as needed.

    Environment variables used by adapters:
    - `OPENAI_API_KEY`
    - `HUGGINGFACE_API_KEY` and `HUGGINGFACE_MODEL`
    - `ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL`
    - Google: relies on `GOOGLE_APPLICATION_CREDENTIALS` and `GOOGLE_PROJECT`/`GOOGLE_REGION`
    """

    if not text:
        return "No text provided"

    provider = (provider or os.getenv("LLM_PROVIDER") or "anthropic").lower()
    model = model or os.getenv("LLM_MODEL")

    if provider == "openai":
        if openai is None:
            raise RuntimeError("openai package is not installed")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in environment")
        openai.api_key = api_key

        async def _call_openai():
            # run blocking SDK call in a thread
            def _sync():
                params = {
                    "model": model or "gpt-4o-mini",
                    "messages": [{"role": "user", "content": text}],
                }
                resp = openai.ChatCompletion.create(**params)
                return resp.choices[0].message["content"]

            return await asyncio.to_thread(_sync)

        return await _call_openai()

    if provider == "huggingface":
        if httpx is None:
            raise RuntimeError("httpx is required for the Hugging Face adapter")
        hf_key = os.getenv("HUGGINGFACE_API_KEY")
        if not hf_key:
            raise RuntimeError("HUGGINGFACE_API_KEY is not set in environment")
        hf_model = model or os.getenv("HUGGINGFACE_MODEL") or "gpt2"
        url = f"https://api-inference.huggingface.co/models/{hf_model}"

        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {"Authorization": f"Bearer {hf_key}"}
            payload = {"inputs": text}
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            # HF returns different shapes depending on model; handle common cases
            if isinstance(data, dict) and "error" in data:
                raise RuntimeError(f"Hugging Face error: {data['error']}")
            if isinstance(data, list):
                # often a list of completions
                first = data[0]
                if isinstance(first, dict) and "generated_text" in first:
                    return first["generated_text"]
                # some models return a single string
                if isinstance(first, str):
                    return first
            if isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"]
            return str(data)

    if provider == "anthropic":
        if Anthropic is None:
            raise RuntimeError("anthropic package is not installed")
        api_key = os.getenv("ANTHROPIC_API_KEY") or ""
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set in environment")
        anthropic_model = model or os.getenv("ANTHROPIC_MODEL") or "claude-2.1"

        async def _call_anthropic():
            def _sync():
                client = Anthropic(api_key=api_key)
                prompt = HUMAN_PROMPT + text + AI_PROMPT
                # anthropic SDK expects `max_tokens_to_sample` (not `max_tokens_to_generate`)
                resp = client.completions.create(model=anthropic_model, prompt=prompt, max_tokens_to_sample=512)
                # `resp` usually contains a `completion` key
                try:
                    # resp may be a dict-like object
                    return resp.get("completion") or resp.get("text") or str(resp)
                except Exception:
                    # fallback to string conversion
                    return str(resp)

            return await asyncio.to_thread(_sync)

        return await _call_anthropic()

    if provider in ("google", "vertex", "vertexai"):
        if aiplatform is None:
            raise RuntimeError("google-cloud-aiplatform package is not installed")

        project = os.getenv("GOOGLE_PROJECT")
        region = os.getenv("GOOGLE_REGION", "us-central1")
        gmodel = model or os.getenv("GOOGLE_MODEL")
        if not gmodel:
            raise RuntimeError("GOOGLE_MODEL must be set for Vertex AI provider")

        async def _call_vertex():
            def _sync():
                aiplatform.init(project=project, location=region)
                endpoint = aiplatform.PredictionClient()
                # Implementation detail: user must configure correct model/endpoint
                # We'll call the text generation API via `aiplatform` high-level utilities when available.
                # For now, use `aiplatform` built-in `TextGenerationModel` if present.
                try:
                    from google.cloud.aiplatform.models import TextGenerationModel # type: ignore

                    model_obj = TextGenerationModel.from_pretrained(gmodel)
                    resp = model_obj.predict([text])
                    # `resp` may be a list-like
                    if isinstance(resp, (list, tuple)):
                        return str(resp[0])
                    return str(resp)
                except Exception as e:
                    raise RuntimeError(f"Vertex AI call failed: {e}")

            return await asyncio.to_thread(_sync)

        return await _call_vertex()

    raise ValueError(f"Unsupported LLM provider: {provider}")

