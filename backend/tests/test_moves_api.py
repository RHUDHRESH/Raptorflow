from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_generate_moves_endpoint_success():
    """Verify that the generate-moves endpoint triggers inference and returns 200."""
    from api.v1.moves import get_move_service

    mock_service = MagicMock()
    mock_service.get_campaign = AsyncMock(return_value=MagicMock())
    mock_service.generate_weekly_moves = AsyncMock(
        return_value={"status": "started", "campaign_id": "test-id"}
    )

    app.dependency_overrides[get_move_service] = lambda: mock_service

    try:
        response = client.post("/v1/moves/generate-weekly/test-id")
        assert response.status_code == 200
        assert response.json()["status"] == "started"
    finally:
        app.dependency_overrides.clear()


def test_get_moves_status_endpoint():
    """Verify that the moves status endpoint returns correctly."""
    from api.v1.moves import get_move_service

    mock_service = MagicMock()
    mock_service.get_moves_generation_status = AsyncMock(
        return_value={"status": "execution", "messages": []}
    )

    app.dependency_overrides[get_move_service] = lambda: mock_service

    try:
        response = client.get("/v1/moves/generate-weekly/test-id/status")
        assert response.status_code == 200
        assert response.json()["status"] == "execution"
    finally:
        app.dependency_overrides.clear()


def test_update_move_status_endpoint():
    """Verify that the move status PATCH endpoint returns 200."""
    from api.v1.moves import get_move_service

    mock_service = MagicMock()
    mock_service.update_move_status = AsyncMock()

    app.dependency_overrides[get_move_service] = lambda: mock_service

    try:
        response = client.patch(
            "/v1/moves/test-move-id/status",
            json={"status": "completed", "result": {"success": True}},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "updated"
    finally:
        app.dependency_overrides.clear()
