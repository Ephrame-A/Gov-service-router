"""API endpoint tests."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.session import get_db
from app.main import app

from app.schemas import (
    Intent,
    IntentExtractionResult,
    QueryResponse,
    QueryStatus,
    RerankResult,
    ServiceRecommendation,
)


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_query_empty_text(client):
    response = await client.post("/api/query", json={"text": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_query_matched(client, sample_candidate, mock_intent_result, mock_rerank_result):
    mock_rec = ServiceRecommendation(
        institution="ERCA",
        department="Business Tax Division",
        service_name="Business Tax Certificate Renewal",
        required_documents=["Previous tax certificate"],
        confidence=0.91,
        explanation="Tax renewal match.",
    )
    mock_response = QueryResponse(
        status=QueryStatus.matched,
        recommendation=mock_rec,
        query_id="test-query-id",
        conversation_id="test-conv-id",
    )

    with patch("app.agent.pipeline.run_pipeline", new=AsyncMock(return_value=mock_response)):
        response = await client.post(
            "/api/query", json={"text": "my shop's tax certificate expired"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "matched"
    assert data["recommendation"]["service_name"] == "Business Tax Certificate Renewal"


@pytest.mark.asyncio
async def test_feedback_invalid_query_id(client):
    response = await client.post(
        "/api/feedback",
        json={"query_id": "not-a-uuid", "feedback": "correct"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_feedback_not_found(client):
    db = AsyncMock()
    db.execute.return_value = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = None
    async def fake_db():
        yield db
    app.dependency_overrides[get_db] = fake_db
    try:
        response = await client.post(
            "/api/feedback",
            json={"query_id": "00000000-0000-0000-0000-000000000099", "feedback": "correct"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    db = AsyncMock()
    db.execute.return_value = MagicMock()
    db.execute.return_value.scalar_one_or_none.return_value = None
    async def fake_db():
        yield db
    app.dependency_overrides[get_db] = fake_db
    try:
        response = await client.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": "wrongpass"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)
    assert response.status_code == 401
