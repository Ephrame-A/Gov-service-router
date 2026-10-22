"""The local similarity fallback uses its own score threshold."""

from unittest.mock import AsyncMock, patch

import pytest

from app.agent.pipeline import _process_single_intent
from app.schemas import Candidate, Intent, QueryStatus, RerankResult


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("score", "expected"),
    [(0.637, QueryStatus.matched), (0.35, QueryStatus.no_match)],
)
async def test_fallback_score_threshold(score, expected):
    candidate = Candidate(
        service_id="00000000-0000-0000-0000-000000000001",
        service_name="Lost Passport Replacement",
        description="Replace a lost passport",
        department_name="Passport Services",
        institution_name="INVEA",
        similarity_score=score,
    )
    rerank = RerankResult(
        best_match_id=candidate.service_id,
        confidence=score,
        reasoning="Best local similarity match",
        used_fallback=True,
    )
    intent = Intent(category="immigration", sub_intent="replacement", query_text="I lost my passport")

    with (
        patch("app.agent.pipeline.retrieve_candidates", new=AsyncMock(return_value=[candidate])),
        patch("app.agent.pipeline.rerank_candidates", new=AsyncMock(return_value=rerank)),
    ):
        status, recommendation, _, _, _ = await _process_single_intent(intent.query_text, intent, AsyncMock())

    assert status == expected
    assert (recommendation is not None) == (expected == QueryStatus.matched)
