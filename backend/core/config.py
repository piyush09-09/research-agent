from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    groq_api_key: str
    qdrant_path: str = "./qdrant_local"
    qdrant_url: Optional[str] = None
    qdrant_api_key: Optional[str] = None
    database_url: str = "sqlite+aiosqlite:///./research.db"
    langsmith_api_key: str = ""
    secret_key: str = "devsecretkey123"

    class Config:
        env_file = ".env"

settings = Settings()