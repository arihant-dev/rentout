from pydantic import BaseSettings # type: ignore

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:password@db:5432/unicorn"
    REDIS_URL: str = "redis://redis:6379/0"
    N8N_WEBHOOK_URL: str = "http://n8n:5678/webhook"
    GOOGLE_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    ALLOW_ORIGINS: list = ["http://localhost", "http://localhost:3000"]
    class Config:
        env_file = ".env"

settings = Settings()