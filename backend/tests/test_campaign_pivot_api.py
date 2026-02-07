from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_apply_pivot_endpoint_success():
    """Verify that the pivot endpoint returns 200."""
    from api.v1.campaigns import get_campaign_service

    mock_service = MagicMock()
    mock_service.apply_pivot = AsyncMock(
        return_value={"status": "success", "campaign_id": "test-id"}
    )

    app.dependency_overrides[get_campaign_service] = lambda: mock_service

    try:
        response = client.post(
            "/v1/campaigns/test-id/pivot",
            json={"title": "Test Pivot", "description": "Do something else"},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "success"
    finally:
        app.dependency_overrides.clear()


def test_apply_pivot_endpoint_not_found():
    """Verify that the endpoint handles missing campaigns."""
    from api.v1.campaigns import get_campaign_service

    mock_service = MagicMock()
    mock_service.apply_pivot = AsyncMock(return_value=None)

    app.dependency_overrides[get_campaign_service] = lambda: mock_service

    try:
        response = client.post(
            "/v1/campaigns/non-existent-id/pivot", json={"title": "Test"}
        )
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
