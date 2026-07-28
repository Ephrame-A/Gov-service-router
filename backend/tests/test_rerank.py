"""Unit tests for re-ranking."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agent.rerank import rerank_candidates
from app.schemas import Candidate, RerankResult


@pytest.mark.asyncio
async def test_rerank_empty_candidates():
    result = await rerank_candidates("test query", [])
    assert result.confidence == 0.0
    assert result.best_match_id == ""


@pytest.mark.asyncio
async def test_rerank_selects_best(sample_candidate):
    mock_response = MagicMock()
    mock_response.text = (
        '{"best_match_id": "00000000-0000-0000-0000-000000000001", '
        '"confidence": 0.91, "reasoning": "Best match for tax renewal.", "is_ambiguous": false}'
    )

    with patch("app.agent.rerank.genai.Client") as mock_client:
        mock_client.return_value.aio.models.generate_content = AsyncMock(return_value=mock_response)
        result = await rerank_candidates("my tax certificate expired", [sample_candidate])

    assert isinstance(result, RerankResult)
    assert result.confidence == 0.91
    assert not result.is_ambiguous


@pytest.mark.asyncio
async def test_rerank_ambiguous(sample_candidate):
    other = sample_candidate.model_copy(
        update={
            "service_id": "00000000-0000-0000-0000-000000000002",
            "service_name": "Driver's License Renewal",
        }
    )
    mock_response = MagicMock()
    mock_response.text = (
        '{"best_match_id": "00000000-0000-0000-0000-000000000001", '
        '"confidence": 0.55, "reasoning": "Could be license or tax.", "is_ambiguous": true}'
    )

    with patch("app.agent.rerank.genai.Client") as mock_client:
        mock_client.return_value.aio.models.generate_content = AsyncMock(return_value=mock_response)
        result = await rerank_candidates("I want to renew my license", [sample_candidate, other])

    assert result.is_ambiguous
    assert result.confidence < 0.75


@pytest.mark.asyncio
async def test_rerank_falls_back_on_llm_error(sample_candidate, caplog):
    with patch("app.agent.rerank.genai.Client") as mock_client:
        mock_client.return_value.aio.models.generate_content.side_effect = RuntimeError("boom")
        with caplog.at_level(logging.ERROR):
            result = await rerank_candidates("my tax certificate expired", [sample_candidate])

    assert result.best_match_id == sample_candidate.service_id
    assert "falling back" in caplog.text.lower()
