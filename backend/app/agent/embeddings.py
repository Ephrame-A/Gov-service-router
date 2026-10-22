"""Local embedding generation using sentence-transformers (no API key required)."""

import asyncio
import logging
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@lru_cache
def _get_model() -> SentenceTransformer:
    model_name = settings.EMBEDDING_MODEL or "all-MiniLM-L6-v2"
    try:
        # Avoid a network metadata check on every API start when the model is cached.
        return SentenceTransformer(model_name, local_files_only=True)
    except Exception:
        pass
    try:
        return SentenceTransformer(model_name)
    except Exception as exc:
        logger.exception("Failed to load embedding model %s, falling back to all-MiniLM-L6-v2", model_name)
        return SentenceTransformer("all-MiniLM-L6-v2")


def encode_text(text: str) -> list[float]:
    """Encode text to a normalized embedding vector."""
    model = _get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


async def get_embedding(text: str) -> list[float]:
    """Generate an embedding vector locally without any external API."""
    return await asyncio.to_thread(encode_text, text)
