"""API tests for onboarding session endpoints (canonical)."""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.asyncio
async def test_create_session_success(client: TestClient):
    mock_manager = AsyncMock()
    mock_manager.set_metadata.return_value = True
    mock_manager.update_progress.return_value = True
    mock_manager.get_progress.return_value = {"completed": 0, "total": 23}
    mock_manager.get_metadata.return_value = {
        "session_id": "test_session",
        "user_id": "user123",
        "workspace_id": "workspace456",
    }

    with patch("api.v1.onboarding.session_manager", mock_manager):
        response = client.post(
            "/api/onboarding/session?workspace_id=workspace456&user_id=user123"
        )

    assert response.status_code == 200
    data = response.json()
    assert data["workspace_id"] == "workspace456"
    assert data["user_id"] == "user123"
    assert "session_id" in data
    assert "progress" in data
    assert "metadata" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_session_health(client: TestClient):
    mock_manager = AsyncMock()
    mock_manager.get_metadata.return_value = {
        "session_id": "test_session",
        "user_id": "user123",
        "workspace_id": "workspace456",
        "started_at": datetime.utcnow().isoformat(),
    }
    mock_manager.get_session_summary.return_value = {"stats": {"completed_steps": 5}}
    mock_manager.health_check.return_value = {"overall_healthy": True}

    with patch("api.v1.onboarding.session_manager", mock_manager):
        response = client.get("/api/onboarding/test_session/health")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["session_id"] == "test_session"
