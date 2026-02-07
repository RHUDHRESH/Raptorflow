"""API tests for auth domain router."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.asyncio
async def test_signup_success(client: TestClient):
    mock_auth = AsyncMock()
    mock_auth.sign_up.return_value = {
        "success": True,
        "session": {"access_token": "token", "refresh_token": "refresh"},
        "user": {"id": "user-1", "email": "test@example.com"},
    }

    with patch("domains.auth.router.get_auth_service", return_value=mock_auth):
        response = client.post(
            "/api/auth/signup",
            json={"email": "test@example.com", "password": "secret"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["access_token"] == "token"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: TestClient):
    mock_auth = AsyncMock()
    mock_auth.sign_in.return_value = {"success": False, "error": "Invalid"}

    with patch("domains.auth.router.get_auth_service", return_value=mock_auth):
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "bad"},
        )

    assert response.status_code == 401


def test_me_requires_auth(client: TestClient):
    response = client.get("/api/auth/me")
    assert response.status_code in (401, 403)
