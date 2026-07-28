"""Unit tests for local embedding generation."""

import logging
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.agent.embeddings import encode_text, get_embedding


def test_encode_text():
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])

    with patch("app.agent.embeddings._get_model", return_value=mock_model):
        result = encode_text("test query")

    assert result == [0.1, 0.2, 0.3]
    mock_model.encode.assert_called_once_with("test query", normalize_embeddings=True)


@pytest.mark.asyncio
async def test_get_embedding_async():
    with patch("app.agent.embeddings.encode_text", return_value=[0.5, 0.6]):
        result = await get_embedding("hello")
    assert result == [0.5, 0.6]


def test_get_model_falls_back_when_model_load_fails(caplog):
    with patch("app.agent.embeddings.SentenceTransformer", side_effect=[RuntimeError("boom"), MagicMock()]) as mock_model:
        with caplog.at_level(logging.ERROR):
            with patch("app.agent.embeddings._get_model.cache_clear"):
                from app.agent import embeddings

                embeddings._get_model.cache_clear()
                result = embeddings._get_model()

    assert result is not None
    assert "falling back" in caplog.text.lower()
