from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_campaign_gantt_endpoint():
    """Verify that the Gantt endpoint returns structured data."""
    from api.v1.campaigns import get_campaign_service

    mock_gantt = {
        "items": [
            {
                "task": "Test Task",
                "start_date": "2023-01-01T00:00:00",
                "end_date": "2023-01-31T00:00:00",
                "progress": 0.5,
            }
        ]
    }

    mock_service = MagicMock()
    mock_service.get_gantt_chart = AsyncMock(return_value=mock_gantt)

    # Use FastAPI dependency overrides
    app.dependency_overrides[get_campaign_service] = lambda: mock_service

    try:
        response = client.get("/v1/campaigns/test-id/gantt")
        assert response.status_code == 200
        assert "items" in response.json()
        assert response.json()["items"][0]["task"] == "Test Task"
    finally:
        app.dependency_overrides.clear()


def test_get_campaign_service():
    from api.v1.campaigns import get_campaign_service
    from services.campaign_service import CampaignService

    assert isinstance(get_campaign_service(), CampaignService)
