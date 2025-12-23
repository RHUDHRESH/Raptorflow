import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from backend.main import app
from backend.api.v1.matrix import get_matrix_service

# Mock the service
mock_service = MagicMock()
mock_service.get_aggregated_overview = AsyncMock(return_value={
    "health_report": {"status": "healthy"},
    "cost_report": {"daily_burn": 10.0}
})
mock_service.halt_system = AsyncMock(return_value=True)

# Override dependency
app.dependency_overrides[get_matrix_service] = lambda: mock_service

client = TestClient(app)

def test_get_matrix_overview():
    """Verify that the matrix overview endpoint returns valid system state."""
    response = client.get("/v1/matrix/overview?workspace_id=ws_1")
    assert response.status_code == 200
    data = response.json()
    assert "health_report" in data
    assert "cost_report" in data

def test_post_kill_switch():
    """Verify that the global kill-switch endpoint works."""
    response = client.post("/v1/matrix/kill-switch")
    assert response.status_code == 200
    assert response.json()["status"] == "halted"

def test_get_drift_report():
    """Verify that the drift report endpoint returns valid metrics."""
    response = client.get("/v1/matrix/mlops/drift")
    assert response.status_code == 200
    data = response.json()
    assert "is_drifting" in data
    assert "metrics" in data

def test_get_governance_burn():
    """Verify that the financial burn endpoint returns valid data."""
    response = client.get("/v1/matrix/governance/burn")
    assert response.status_code == 200
    data = response.json()
    assert "daily_burn_usd" in data