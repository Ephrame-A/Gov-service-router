"""Security checks for account creation and signing configuration."""

import pytest

from app.auth import create_access_token, decode_token, get_jwt_secret, settings


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
