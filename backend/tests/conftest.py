"""Pytest configuration and shared fixtures."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas import Candidate, Intent, IntentExtractionResult, RerankResult

FIXTURES_DIR = Path(__file__).parent


@pytest.fixture
def test_queries():
    with open(FIXTURES_DIR / "test_queries.json") as f:
        return json.load(f)


@pytest.fixture
def sample_candidate():
    return Candidate(
        service_id="00000000-0000-0000-0000-000000000001",
        service_name="Business Tax Certificate Renewal",
        description="Renewal of expired business tax certificates.",
        department_name="Business Tax Division",
        institution_name="ERCA",
        similarity_score=0.92,
        office_address="Mexico Square, Addis Ababa",
        working_hours="Mon-Fri 8:30-17:00",
        contact_phone="+251-11-662-9080",
        required_documents=["Previous tax certificate", "Business license"],
    )


@pytest.fixture
def mock_intent_result():
    return IntentExtractionResult(
        intents=[
            Intent(
                category="taxation",
                sub_intent="renewal",
                entities={},
                query_text="my shop's tax certificate expired",
            )
        ],
        is_multi_intent=False,
    )


@pytest.fixture
def mock_rerank_result():
    return RerankResult(
        best_match_id="00000000-0000-0000-0000-000000000001",
        confidence=0.91,
        reasoning="You mentioned renewing a business tax certificate.",
        is_ambiguous=False,
    )


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
