"""Security checks for account creation and signing configuration."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from app.auth import create_access_token, decode_token, get_jwt_secret, settings
from app.routers.auth import register
from app.schemas import RegisterRequest


@pytest.mark.asyncio
async def test_public_admin_registration_is_rejected(client):
    response = await client.post(
        "/api/auth/register",
        json={"email": "intruder@example.com", "password": "long-enough-password", "role": "admin"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_untrusted_origin_has_no_cors_permission(client):
    response = await client.options(
        "/api/auth/login",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.headers.get("access-control-allow-origin") is None


def test_example_signing_secret_is_rejected(monkeypatch):
    monkeypatch.setattr(settings, "NEXTAUTH_SECRET", "change-me-to-a-random-string")
    with pytest.raises(RuntimeError, match="NEXTAUTH_SECRET"):
        get_jwt_secret()


def test_signed_token_round_trip_and_tamper_rejection():
    token = create_access_token("00000000-0000-0000-0000-000000000001", "admin", None)
    assert decode_token(token)["role"] == "admin"
    with pytest.raises(Exception):
        decode_token(token + "tampered")


@pytest.mark.asyncio
async def test_public_officer_listing_is_rejected(client):
    response = await client.get("/api/admin/officers")
    assert response.status_code == 401


def test_registration_only_accepts_officers_with_strong_password():
    with pytest.raises(ValidationError):
        RegisterRequest(email="admin@example.com", password="long-enough-password", role="admin", institution_id="a")
    with pytest.raises(ValidationError):
        RegisterRequest(email="officer@example.com", password="short", institution_id="a")


@pytest.mark.asyncio
async def test_admin_can_create_officer_for_approved_institution():
    institution_id = uuid.uuid4()
    db = AsyncMock()
    db.add = MagicMock()
    missing_user = MagicMock()
    missing_user.scalar_one_or_none.return_value = None
    approved_institution = MagicMock()
    approved_institution.scalar_one_or_none.return_value = SimpleNamespace(name="Verified Office", is_approved=True)
    db.execute.side_effect = [missing_user, approved_institution]

    async def assign_id(user):
        user.id = uuid.uuid4()

    db.refresh.side_effect = assign_id
    with patch("app.routers.auth.hash_password", return_value="hashed"):
        result = await register(
            RegisterRequest(email="officer@example.com", password="strong-password", institution_id=str(institution_id)),
            db=db,
            admin=SimpleNamespace(role="admin"),
        )

    assert result.role == "officer"
    assert result.institution_name == "Verified Office"
    assert result.institution_id == str(institution_id)
    assert db.add.call_args.args[0].password_hash == "hashed"
    db.commit.assert_awaited_once()
