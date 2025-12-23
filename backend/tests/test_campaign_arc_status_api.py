from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_generate_arc_status_endpoint():
    """Verify that the status endpoint returns the current orchestrator state."""
    from backend.api.v1.campaigns import get_campaign_service

    mock_status = {
        "status": "planning",
        "orchestrator_status": "planning",
        "messages": ["Orchestrator initialized."],
    }

    mock_service = MagicMock()
    mock_service.get_arc_generation_status = AsyncMock(return_value=mock_status)

    app.dependency_overrides[get_campaign_service] = lambda: mock_service

    try:
        response = client.get("/v1/campaigns/generate-arc/test-campaign-id/status")
        assert response.status_code == 200
        assert response.json()["status"] == "planning"
        assert "messages" in response.json()
    finally:
        app.dependency_overrides.clear()


def test_generate_arc_status_not_found():
    """Verify that the status endpoint handles missing campaigns."""
    from backend.api.v1.campaigns import get_campaign_service

    mock_service = MagicMock()
    mock_service.get_arc_generation_status = AsyncMock(return_value=None)

    app.dependency_overrides[get_campaign_service] = lambda: mock_service

    try:
        response = client.get("/v1/campaigns/generate-arc/non-existent-id/status")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
