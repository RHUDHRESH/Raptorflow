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


def test_get_move_detail_endpoint():
    from api.v1.moves import get_move_service

    mock_service = MagicMock()
    mock_service.get_move_detail = AsyncMock(return_value={"id": "move-123"})

    app.dependency_overrides[get_move_service] = lambda: mock_service
    try:
        response = client.get("/v1/moves/move-123")
        assert response.status_code == 200
        assert response.json()["data"]["move"]["id"] == "move-123"
    finally:
        app.dependency_overrides.clear()


def test_get_move_rationale_endpoint():
    from api.v1.moves import get_move_service

    mock_service = MagicMock()
    mock_service.get_move_rationale = AsyncMock(return_value={"decree": "Test"})

    app.dependency_overrides[get_move_service] = lambda: mock_service
    try:
        response = client.get("/v1/moves/move-123/rationale")
        assert response.status_code == 200
        assert response.json()["data"]["decree"] == "Test"
    finally:
        app.dependency_overrides.clear()


def test_add_task_endpoint():
    from api.v1.moves import get_move_service

    mock_service = MagicMock()
    mock_service.add_task = AsyncMock(return_value={"id": "move-123"})

    app.dependency_overrides[get_move_service] = lambda: mock_service
    try:
        response = client.post(
            "/v1/moves/move-123/tasks",
            json={"label": "Task A"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["move"]["id"] == "move-123"
    finally:
        app.dependency_overrides.clear()


def test_update_task_endpoint():
    from api.v1.moves import get_move_service

    mock_service = MagicMock()
    mock_service.update_task = AsyncMock(return_value={"id": "move-123"})

    app.dependency_overrides[get_move_service] = lambda: mock_service
    try:
        response = client.put(
            "/v1/moves/move-123/tasks/task-1",
            json={"completed": True},
        )
        assert response.status_code == 200
        assert response.json()["data"]["move"]["id"] == "move-123"
    finally:
        app.dependency_overrides.clear()


def test_update_move_endpoint():
    from api.v1.moves import get_move_service

    mock_service = MagicMock()
    mock_service.update_move = AsyncMock(return_value={"id": "move-123"})

    app.dependency_overrides[get_move_service] = lambda: mock_service
    try:
        response = client.put("/v1/moves/move-123", json={"title": "Updated"})
        assert response.status_code == 200
        assert response.json()["data"]["move"]["id"] == "move-123"
    finally:
        app.dependency_overrides.clear()


def test_log_move_metric_endpoint():
    from api.v1.moves import get_move_service

    mock_service = MagicMock()
    mock_service.append_metric = AsyncMock(
        return_value={"move": {"id": "move-123"}, "rag": {"status": "green"}}
    )

    app.dependency_overrides[get_move_service] = lambda: mock_service
    try:
        response = client.post("/v1/moves/move-123/metrics", json={"leads": 5})
        assert response.status_code == 200
        assert response.json()["data"]["move"]["id"] == "move-123"
    finally:
        app.dependency_overrides.clear()
