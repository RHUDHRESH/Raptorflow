from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from api.v1.blackbox_telemetry import get_blackbox_service
from main import app

client = TestClient(app)


def test_log_telemetry_endpoint():
    mock_service = MagicMock()
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service

    tenant_id = uuid4()
    payload = {
        "tenant_id": str(tenant_id),
        "move_id": str(uuid4()),
        "agent_id": "api-test-agent",
        "trace": {"api": "test"},
        "tokens": 20,
        "latency": 0.2,
    }

    response = client.post(
        "/v1/blackbox/telemetry",
        json=payload,
        headers={"X-Tenant-ID": str(tenant_id)},
    )
    assert response.status_code == 201
    mock_service.log_telemetry.assert_called_once()

    app.dependency_overrides.clear()


def test_get_agent_audit_log_endpoint():
    mock_service = MagicMock()
    mock_service.get_agent_audit_log.return_value = [{"id": "test"}]
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service

    tenant_id = uuid4()
    response = client.get(
        "/v1/blackbox/telemetry/audit/test-agent",
        headers={"X-Tenant-ID": str(tenant_id)},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_service.get_agent_audit_log.assert_called_with("test-agent", tenant_id)

    app.dependency_overrides.clear()


def test_calculate_move_cost_endpoint():
    mock_service = MagicMock()
    mock_service.calculate_move_cost.return_value = 500
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service

    move_id = uuid4()
    tenant_id = uuid4()
    response = client.get(
        f"/v1/blackbox/telemetry/cost/{move_id}",
        headers={"X-Tenant-ID": str(tenant_id)},
    )
    assert response.status_code == 200
    assert response.json()["total_tokens"] == 500
    mock_service.calculate_move_cost.assert_called_with(move_id, tenant_id)

    app.dependency_overrides.clear()
