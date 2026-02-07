"""Unit tests for onboarding step API (canonical)."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.mark.asyncio
async def test_update_step_success(client: TestClient):
    session_id = "test-session-id"
    step_id = 1

    with patch("api.v1.onboarding.validate_step_data", return_value=(True, [])), patch(
        "api.v1.onboarding.session_manager", new=AsyncMock()
    ) as mock_session:
        mock_session.save_step.return_value = True
        mock_session.refresh_session_ttl.return_value = True
        mock_session.get_progress.return_value = {"completed": 1, "total": 23}

        response = client.post(
            f"/api/onboarding/{session_id}/steps/{step_id}",
            json={"data": {"company_name": "Test Corp"}, "version": 1},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["session_id"] == session_id
        assert data["step_id"] == step_id


@pytest.mark.asyncio
async def test_update_step_invalid_id(client: TestClient):
    response = client.post(
        "/api/onboarding/test-session/steps/0", json={"data": {"foo": "bar"}}
    )

    assert response.status_code == 400
