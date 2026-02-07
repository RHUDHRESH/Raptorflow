from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_generate_arc_endpoint_success():
    """Verify that the generate-arc endpoint triggers inference and returns 200."""
    from api.v1.campaigns import get_campaign_service

    mock_service = MagicMock()
    mock_service.get_campaign = AsyncMock(return_value=MagicMock())
    mock_service.generate_90_day_arc = AsyncMock()

    app.dependency_overrides[get_campaign_service] = lambda: mock_service

    try:
        response = client.post("/v1/campaigns/generate-arc/test-campaign-id")
        assert response.status_code == 200
        assert response.json()["status"] == "started"
        assert response.json()["campaign_id"] == "test-campaign-id"
    finally:
        app.dependency_overrides.clear()


def test_generate_arc_endpoint_not_found():
    """Verify that the endpoint handles service errors gracefully."""
    from api.v1.campaigns import get_campaign_service

    mock_service = MagicMock()
    mock_service.get_campaign = AsyncMock(return_value=None)
    mock_service.generate_90_day_arc = AsyncMock(return_value=None)

    app.dependency_overrides[get_campaign_service] = lambda: mock_service

    try:
        response = client.post("/v1/campaigns/generate-arc/non-existent-id")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
