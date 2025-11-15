from app.services.llm_service import run_llm

async def run_pipeline(input_data):
    # Step 1 — Pre-process
    text = input_data.text if hasattr(input_data, "text") else None

    # Step 2 — Pipeline logic
    response = await run_llm(text)

    # Step 3 — Post-process
    return response
