"""Fixture-based test runner for the query pipeline.

Run against live API (integration):
  pytest tests/test_fixture_queries.py -m integration

Run offline (mocked):
  pytest tests/test_fixture_queries.py -m "not integration"
"""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

FIXTURES = Path(__file__).parent / "test_queries.json"


@pytest.fixture
def queries():
    with open(FIXTURES) as f:
        return json.load(f)


@pytest.mark.asyncio
async def test_fixture_queries_structure(queries):
    """Every fixture entry has required fields."""
    assert len(queries) >= 20
    for entry in queries:
        assert "query" in entry
        assert "expected_status" in entry


@pytest.mark.asyncio
@pytest.mark.parametrize("index", range(25))
async def test_fixture_queries_offline(index, queries):
    """Verify pipeline routing logic for each fixture (mocked LLM)."""
    from app.agent.pipeline import run_pipeline
    from app.schemas import Candidate, Intent, IntentExtractionResult, RerankResult

    entry = queries[index % len(queries)]
    expected_status = entry["expected_status"]

    intent = Intent(
        category="general",
        sub_intent="inquiry",
        entities={},
        query_text=entry["query"],
    )
    intent_result = IntentExtractionResult(intents=[intent], is_multi_intent=False)

    candidate = Candidate(
        service_id="00000000-0000-0000-0000-000000000001",
        service_name=entry.get("expected_service") or "Unknown Service",
        description="Test service",
        department_name="Test Dept",
        institution_name="Test Inst",
        similarity_score=0.9,
    )

    if expected_status == "needs_clarification":
        rerank = RerankResult(
            best_match_id=str(candidate.service_id),
            confidence=0.5,
            reasoning="Ambiguous request.",
            is_ambiguous=True,
        )
    elif expected_status == "matched":
        rerank = RerankResult(
            best_match_id=str(candidate.service_id),
            confidence=0.9,
            reasoning="Good match.",
            is_ambiguous=False,
        )
    else:
        rerank = RerankResult(
            best_match_id=str(candidate.service_id),
            confidence=0.3,
            reasoning="Low confidence.",
            is_ambiguous=False,
        )

    mock_session = AsyncMock()
    mock_session.add = lambda x: None
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.execute = AsyncMock(return_value=AsyncMock(scalars=AsyncMock(return_value=AsyncMock(all=AsyncMock(return_value=[])))))

    with (
        patch("app.agent.pipeline.extract_intent", new=AsyncMock(return_value=intent_result)),
        patch("app.agent.pipeline.retrieve_candidates", new=AsyncMock(return_value=[candidate])),
        patch("app.agent.pipeline.rerank_candidates", new=AsyncMock(return_value=rerank)),
    ):
        result = await run_pipeline(entry["query"], None, mock_session)

    assert result.status.value == expected_status
