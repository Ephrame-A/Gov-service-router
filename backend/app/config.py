"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/govrouter"

    # Gemini LLM
    GEMINI_API_KEY: str = ""

    # Embeddings (uses Gemini embedding model by default)
    EMBEDDING_API_KEY: str = ""  # Falls back to GEMINI_API_KEY if empty
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    EMBEDDING_DIM: int = 768

    # Pipeline tuning
    CONFIDENCE_THRESHOLD: float = 0.75
    RETRIEVAL_TOP_K: int = 5

    # Auth (Phase 3)
    NEXTAUTH_SECRET: str = ""
    NEXTAUTH_URL: str = "http://localhost:3000"
    NEXT_PUBLIC_API_URL: str = "http://localhost:8000"

    @property
    def effective_embedding_api_key(self) -> str:
        return self.EMBEDDING_API_KEY or self.GEMINI_API_KEY

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
