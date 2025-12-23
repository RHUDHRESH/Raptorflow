import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_matrix_overview_endpoint():
    """Verify GET /v1/matrix/overview returns 200."""
    response = client.get("/v1/matrix/overview")
    assert response.status_code == 200
    assert "active_agents" in response.json()

def test_matrix_kill_switch_endpoint():
    """Verify POST /v1/matrix/kill-switch returns 200."""
    response = client.post("/v1/matrix/kill-switch")
    assert response.status_code == 200
    assert response.json()["status"] == "halted"

def test_matrix_drift_endpoint():
    """Verify GET /v1/matrix/mlops/drift returns 200."""
    response = client.get("/v1/matrix/mlops/drift")
    assert response.status_code == 200
    assert "is_drifting" in response.json()

def test_matrix_burn_endpoint():
    """Verify GET /v1/matrix/governance/burn returns 200."""
    response = client.get("/v1/matrix/governance/burn")
    assert response.status_code == 200
    assert "daily_burn_usd" in response.json()
