"""Unit tests for intent extraction."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agent.intent import extract_intent
from app.schemas import IntentExtractionResult


@pytest.mark.asyncio
async def test_extract_intent_single():
    mock_response = MagicMock()
    mock_response.text = (
        '{"is_multi_intent": false, "intents": ['
        '{"category": "taxation", "sub_intent": "renewal", "entities": {}, '
        '"query_text": "my shop tax certificate expired"}]}'
    )

    with patch("app.agent.intent.genai.Client") as mock_client:
        mock_client.return_value.aio.models.generate_content = AsyncMock(return_value=mock_response)
        result = await extract_intent("my shop tax certificate expired")

    assert isinstance(result, IntentExtractionResult)
    assert not result.is_multi_intent
    assert len(result.intents) == 1
    assert result.intents[0].category == "taxation"


@pytest.mark.asyncio
async def test_extract_intent_multi():
    mock_response = MagicMock()
    mock_response.text = (
        '{"is_multi_intent": true, "intents": ['
        '{"category": "immigration", "sub_intent": "renewal", "entities": {}, "query_text": "renew my passport"},'
        '{"category": "business", "sub_intent": "new_application", "entities": {}, "query_text": "register my business"}'
        ']}'
    )

    with patch("app.agent.intent.genai.Client") as mock_client:
        mock_client.return_value.aio.models.generate_content = AsyncMock(return_value=mock_response)
        result = await extract_intent("renew my passport and register my business")

    assert result.is_multi_intent
    assert len(result.intents) == 2


@pytest.mark.parametrize(
    "text,expected_category",
    [
        ("my shop's tax certificate expired", "taxation"),
        ("I want to get a passport", "immigration"),
        ("renew my driving license", "transport"),
        ("I need a birth certificate for my baby", "civil_registration"),
        ("I want to register a new company", "business"),
        ("how to import electronics into Ethiopia", "customs"),
        ("my water meter is broken", "utilities"),
        ("I want to invest in Ethiopia", "investment"),
        ("transfer car ownership to another person", "transport"),
        ("I need to build a house and need permission", "land"),
    ],
)
@pytest.mark.asyncio
async def test_extract_intent_categories(text, expected_category):
    """Verify intent extraction returns structured output for diverse queries."""
    mock_response = MagicMock()
    mock_response.text = (
        f'{{"is_multi_intent": false, "intents": ['
        f'{{"category": "{expected_category}", "sub_intent": "inquiry", "entities": {{}}, "query_text": "{text}"}}'
        f"]}}"
    )

    with patch("app.agent.intent.genai.Client") as mock_client:
        mock_client.return_value.aio.models.generate_content = AsyncMock(return_value=mock_response)
        result = await extract_intent(text)

    assert result.intents[0].category == expected_category


@pytest.mark.asyncio
async def test_extract_intent_falls_back_on_llm_error(caplog):
    with patch("app.agent.intent.genai.Client") as mock_client:
        mock_client.return_value.aio.models.generate_content.side_effect = RuntimeError("boom")
        with caplog.at_level(logging.ERROR):
            result = await extract_intent("I need help with a passport")

    assert result.intents[0].category == "general"
    assert "falling back" in caplog.text.lower()
