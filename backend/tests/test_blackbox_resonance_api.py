from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.api.v1.blackbox_roi import get_blackbox_service
from backend.main import app

client = TestClient(app)


def test_get_outcomes_by_campaign_endpoint():
    mock_service = MagicMock()
    mock_service.get_outcomes_by_campaign.return_value = [
        {"id": str(uuid4()), "value": 100.0}
    ]
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service

    campaign_id = uuid4()
    response = client.get(f"/v1/blackbox/roi/outcomes/campaign/{campaign_id}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_service.get_outcomes_by_campaign.assert_called_with(campaign_id)

    app.dependency_overrides.clear()


def test_get_outcomes_by_move_endpoint():
    mock_service = MagicMock()
    mock_service.get_outcomes_by_move.return_value = [
        {"id": str(uuid4()), "value": 50.0}
    ]
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service

    move_id = uuid4()
    response = client.get(f"/v1/blackbox/roi/outcomes/move/{move_id}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_service.get_outcomes_by_move.assert_called_with(move_id)

    app.dependency_overrides.clear()


def test_get_evidence_package_endpoint():
    mock_service = MagicMock()
    mock_service.get_evidence_package.return_value = [
        {"id": str(uuid4()), "agent_id": "test-agent"}
    ]
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service

    learning_id = uuid4()
    response = client.get(f"/v1/blackbox/roi/evidence/{learning_id}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_service.get_evidence_package.assert_called_with(learning_id)

    app.dependency_overrides.clear()


def test_get_campaign_roi_endpoint():
    mock_service = MagicMock()
    mock_service.compute_roi.return_value = {"roi": 1.5}
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service

    campaign_id = uuid4()
    response = client.get(f"/v1/blackbox/roi/campaign/{campaign_id}")
    assert response.status_code == 200
    assert response.json()["roi"] == 1.5
    mock_service.compute_roi.assert_called()

    app.dependency_overrides.clear()


def test_get_roi_matrix_endpoint():
    mock_service = MagicMock()
    mock_service.get_roi_matrix_data.return_value = [{"campaign_id": "test"}]
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service

    response = client.get("/v1/blackbox/roi/matrix")
    assert response.status_code == 200
    assert len(response.json()) == 1

    app.dependency_overrides.clear()


def test_get_momentum_score_endpoint():
    mock_service = MagicMock()
    mock_service.calculate_momentum_score.return_value = 0.85
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service

    response = client.get("/v1/blackbox/roi/momentum")
    assert response.status_code == 200
    assert response.json()["momentum_score"] == 0.85

    app.dependency_overrides.clear()
