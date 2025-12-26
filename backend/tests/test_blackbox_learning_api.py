from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from api.v1.blackbox_learning import get_blackbox_service
from main import app

client = TestClient(app)


@pytest.fixture
def mock_service():
    service = MagicMock()
    app.dependency_overrides[get_blackbox_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


def test_get_learning_feed(mock_service):
    mock_service.get_learning_feed.return_value = [{"id": "l1", "content": "Insight"}]

    response = client.get("/v1/blackbox/learning/feed?limit=5")
    assert response.status_code == 200
    assert response.json() == [{"id": "l1", "content": "Insight"}]
    mock_service.get_learning_feed.assert_called_once_with(limit=5)


def test_validate_insight(mock_service):
    learning_id = str(uuid4())
    response = client.post(
        f"/v1/blackbox/learning/validate/{learning_id}", json={"status": "approved"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "updated"
    mock_service.validate_insight.assert_called_once()


def test_get_evidence_package(mock_service):
    mock_service.get_evidence_package.return_value = [{"id": "t1"}]

    learning_id = str(uuid4())
    response = client.get(f"/v1/blackbox/learning/evidence/{learning_id}")
    assert response.status_code == 200
    assert response.json() == [{"id": "t1"}]
    mock_service.get_evidence_package.assert_called_once()


@pytest.mark.asyncio
async def test_trigger_learning_cycle(mock_service):
    mock_service.trigger_learning_cycle = AsyncMock(
        return_value={"status": "cycle_complete"}
    )

    move_id = str(uuid4())
    tenant_id = uuid4()
    response = client.post(
        f"/v1/blackbox/learning/cycle/{move_id}",
        headers={"X-Tenant-ID": str(tenant_id)},
    )
    assert response.status_code == 200
    assert response.json() == {"status": "cycle_complete"}
    mock_service.trigger_learning_cycle.assert_called_once_with(move_id, tenant_id)
