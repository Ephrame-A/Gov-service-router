"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

# backend/app/config.py -> project root is two levels up
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/govrouter"

    # Gemini LLM (intent extraction + re-ranking only)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # Local embeddings (sentence-transformers — no API key required)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    # Pipeline tuning
    CONFIDENCE_THRESHOLD: float = 0.75
    FALLBACK_CONFIDENCE_THRESHOLD: float = 0.60
    RETRIEVAL_TOP_K: int = 5

    # Auth
    NEXTAUTH_SECRET: str = ""
    NEXTAUTH_URL: str = "http://localhost:3000"
    NEXT_PUBLIC_API_URL: str = "http://localhost:8000"

    model_config = {
        # Load from project root (.env) or backend/.env when running locally
        "env_file": (
            PROJECT_ROOT / ".env",
            BACKEND_ROOT / ".env",
        ),
        "env_file_encoding": "utf-8",
    }

    @property
    def llm_enabled(self) -> bool:
        return bool(self.GEMINI_API_KEY.strip())

    @property
    def gemini_model(self) -> str:
        """Model ID for the Gemini API (no 'models/' prefix)."""
        return self.GEMINI_MODEL.removeprefix("models/")


@lru_cache
def get_settings() -> Settings:
    return Settings()
