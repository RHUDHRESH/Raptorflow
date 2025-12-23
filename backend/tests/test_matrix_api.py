import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_get_matrix_overview():
    """Verify that the matrix overview endpoint returns valid system state."""
    response = client.get("/v1/matrix/overview")
    assert response.status_code == 200
    data = response.json()
    assert "kill_switch_engaged" in data
    assert "active_agents" in data

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