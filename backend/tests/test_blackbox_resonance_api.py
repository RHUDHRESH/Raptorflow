from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from api.v1.blackbox_roi import get_blackbox_service
from main import app
from services.blackbox_service import AttributionModel

client = TestClient(app)


def test_get_outcomes_by_campaign_endpoint():
    mock_service = MagicMock()
    mock_service.get_outcomes_by_campaign.return_value = [
        {"id": str(uuid4()), "value": 100.0}
    ]
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service

    campaign_id = uuid4()
    tenant_id = uuid4()
    response = client.get(
        f"/v1/blackbox/roi/outcomes/campaign/{campaign_id}",
        headers={"X-Tenant-ID": str(tenant_id)},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_service.get_outcomes_by_campaign.assert_called_with(campaign_id, tenant_id)

    app.dependency_overrides.clear()


def test_get_outcomes_by_move_endpoint():
    mock_service = MagicMock()
    mock_service.get_outcomes_by_move.return_value = [
        {"id": str(uuid4()), "value": 50.0}
    ]
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service

    move_id = uuid4()
    tenant_id = uuid4()
    response = client.get(
        f"/v1/blackbox/roi/outcomes/move/{move_id}",
        headers={"X-Tenant-ID": str(tenant_id)},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_service.get_outcomes_by_move.assert_called_with(move_id, tenant_id)

    app.dependency_overrides.clear()


def test_get_evidence_package_endpoint():
    mock_service = MagicMock()
    mock_service.get_evidence_package.return_value = [
        {"id": str(uuid4()), "agent_id": "test-agent"}
    ]
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service

    learning_id = uuid4()
    tenant_id = uuid4()
    response = client.get(
        f"/v1/blackbox/roi/evidence/{learning_id}",
        headers={"X-Tenant-ID": str(tenant_id)},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_service.get_evidence_package.assert_called_with(learning_id)

    app.dependency_overrides.clear()


def test_get_campaign_roi_endpoint():
    mock_service = MagicMock()
    mock_service.compute_roi.return_value = {"roi": 1.5}
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service

    campaign_id = uuid4()
    tenant_id = uuid4()
    response = client.get(
        f"/v1/blackbox/roi/campaign/{campaign_id}",
        headers={"X-Tenant-ID": str(tenant_id)},
    )
    assert response.status_code == 200
    assert response.json()["roi"] == 1.5
    mock_service.compute_roi.assert_called_with(
        campaign_id=campaign_id,
        tenant_id=tenant_id,
        model=AttributionModel.LINEAR,
    )

    app.dependency_overrides.clear()


def test_get_roi_matrix_endpoint():
    mock_service = MagicMock()
    mock_service.get_roi_matrix_data.return_value = [{"campaign_id": "test"}]
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service

    tenant_id = uuid4()
    response = client.get(
        "/v1/blackbox/roi/matrix", headers={"X-Tenant-ID": str(tenant_id)}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_service.get_roi_matrix_data.assert_called_with(tenant_id)

    app.dependency_overrides.clear()


def test_get_momentum_score_endpoint():
    mock_service = MagicMock()
    mock_service.calculate_momentum_score.return_value = 0.85
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service

    response = client.get("/v1/blackbox/roi/momentum")
    assert response.status_code == 200
    assert response.json()["momentum_score"] == 0.85

    app.dependency_overrides.clear()


def test_get_telemetry_by_move_endpoint():
    mock_service = MagicMock()
    mock_service.get_telemetry_by_move.return_value = [
        {"id": str(uuid4()), "agent_id": "test"}
    ]
    # Note: Using blackbox_telemetry provider here
    from api.v1.blackbox_telemetry import get_blackbox_service as get_tele_service

    app.dependency_overrides[get_tele_service] = lambda: mock_service

    move_id = uuid4()
    tenant_id = uuid4()
    response = client.get(
        f"/v1/blackbox/telemetry/move/{move_id}",
        headers={"X-Tenant-ID": str(tenant_id)},
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_service.get_telemetry_by_move.assert_called_with(str(move_id), tenant_id)

    app.dependency_overrides.clear()


def test_get_learnings_by_move_endpoint():
    mock_service = MagicMock()
    mock_service.get_learnings_by_move.return_value = [
        {"id": str(uuid4()), "content": "test learning"}
    ]
    from api.v1.blackbox_learning import get_blackbox_service as get_learn_service

    app.dependency_overrides[get_learn_service] = lambda: mock_service

    move_id = uuid4()
    response = client.get(f"/v1/blackbox/learning/move/{move_id}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_service.get_learnings_by_move.assert_called_with(move_id)

    app.dependency_overrides.clear()


def test_trigger_specialist_analysis_endpoint():
    mock_service = MagicMock()
    mock_service.trigger_learning_cycle = AsyncMock(
        return_value={"status": "cycle_complete"}
    )
    from api.v1.blackbox_learning import get_blackbox_service as get_learn_service

    app.dependency_overrides[get_learn_service] = lambda: mock_service

    move_id = uuid4()
    tenant_id = uuid4()
    response = client.post(
        f"/v1/blackbox/learning/cycle/{move_id}",
        headers={"X-Tenant-ID": str(tenant_id)},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "cycle_complete"
    mock_service.trigger_learning_cycle.assert_called_with(str(move_id), tenant_id)

    app.dependency_overrides.clear()


def test_run_specialist_agent_endpoint():
    mock_service = MagicMock()
    mock_service.get_telemetry_by_move.return_value = []
    mock_service.get_outcomes_by_move.return_value = []

    from api.v1.blackbox_specialist import get_blackbox_service as get_spec_service

    app.dependency_overrides[get_spec_service] = lambda: mock_service

    move_id = uuid4()
    # Mocking the agent run would be complex, so we just test the entry point
    # We expect a 404 if we provide a bogus agent_id
    tenant_id = uuid4()
    response = client.post(
        f"/v1/blackbox/specialist/run/bogus_agent/{move_id}",
        headers={"X-Tenant-ID": str(tenant_id)},
    )
    assert response.status_code == 404

    app.dependency_overrides.clear()
