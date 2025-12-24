from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.api.v1.blackbox_roi import get_blackbox_service
from backend.main import app

client = TestClient(app)


def test_get_campaign_roi_endpoint():
    mock_service = MagicMock()
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service
    mock_service.compute_roi.return_value = {"roi": 2.5}

    cid = str(uuid4())
    response = client.get(f"/v1/blackbox/roi/campaign/{cid}")

    assert response.status_code == 200
    assert response.json()["roi"] == 2.5
    app.dependency_overrides.clear()


def test_get_roi_matrix_endpoint():
    mock_service = MagicMock()
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service
    mock_service.get_roi_matrix_data.return_value = [{"campaign_id": "c1", "roi": 1.0}]

    response = client.get("/v1/blackbox/roi/matrix")

    assert response.status_code == 200
    assert len(response.json()) == 1
    app.dependency_overrides.clear()


def test_get_momentum_score_endpoint():
    mock_service = MagicMock()
    app.dependency_overrides[get_blackbox_service] = lambda: mock_service
    mock_service.calculate_momentum_score.return_value = 12.34

    response = client.get("/v1/blackbox/roi/momentum")

    assert response.status_code == 200
    assert response.json()["momentum_score"] == 12.34
    app.dependency_overrides.clear()
