from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from main import app

from ..llm import LLMResponse

# Mock LLMCache and other dependencies to avoid external connections
with patch("backend.llm.LLMCache"), patch("backend.startup.initialize_app"), patch(
    "backend.redis_services_activation.activate_redis_services"
):
    client = TestClient(app)


@pytest.mark.asyncio
async def test_process_onboarding_step_api():
    """Test the POST /onboarding-universal/{session_id}/steps/{step_id} endpoint."""
    session_id = "test-session-id"
    step_id = "hello_world"

    payload = {
        "workspace_id": "test-workspace-id",
        "data": {"company_name": "Test Corp", "step_name": "Initial Greeting"},
    }

    mock_llm_response = LLMResponse(
        content="Hello Test Corp! Ready for Initial Greeting.", model="gemini-1.5-pro"
    )

    with patch(
        "backend.llm.llm_manager.generate", return_value=mock_llm_response
    ), patch("backend.llm.LLMCache"):

        response = client.post(
            f"/api/v1/onboarding-universal/{session_id}/steps/{step_id}", json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Test Corp" in data["output"]
        assert data["skill"] == "hello_world"


@pytest.mark.asyncio
async def test_process_onboarding_step_not_found():
    """Test handling of non-existent skill."""
    session_id = "test-session-id"
    step_id = "non_existent_skill"

    payload = {"workspace_id": "test-workspace-id", "data": {}}

    with patch("backend.llm.LLMCache"):
        response = client.post(
            f"/api/v1/onboarding-universal/{session_id}/steps/{step_id}", json=payload
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
