import os
from typing import List

from dotenv import load_dotenv  # type: ignore

# Load .env in development; safe to call even if .env missing
load_dotenv()


class Settings:
    """Simple settings loader that uses environment variables.

    This avoids runtime dependency on Pydantic and prevents pydantic-settings
    initialization errors during startup. If you prefer Pydantic's validation
    features, we can revert to a pydantic-based Settings later and pin
    compatible package versions in `requirements.txt`.
    """

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://postgres:password@db:5432/unicorn"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    N8N_WEBHOOK_URL: str = os.getenv("N8N_WEBHOOK_URL", "http://n8n:5678/webhook")
    # Optional n8n REST API base URL and API key (if using n8n's REST API)
    N8N_API_URL: str = os.getenv("N8N_API_URL", "http://n8n:5678")
    N8N_API_KEY: str = os.getenv("N8N_API_KEY", "")
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    # Allow origins may be provided as a comma-separated env var
    ALLOW_ORIGINS: List[str] = (
        os.getenv("ALLOW_ORIGINS", "http://localhost,http://localhost:3000").split(",")
    )


settings = Settings()