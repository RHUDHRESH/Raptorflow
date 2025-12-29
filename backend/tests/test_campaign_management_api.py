from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.v1.campaigns import get_campaign_service
from api.v1.campaigns import router as campaigns_router
from api.v1.moves import get_move_service
from api.v1.moves import router as moves_router
from core.auth import get_current_user, get_tenant_id
from services.campaign_service import CampaignService
from services.move_service import MoveService

test_app = FastAPI()
test_app.include_router(campaigns_router)
test_app.include_router(moves_router)

client = TestClient(test_app)


@pytest.fixture(autouse=True)
def mock_auth():
    test_app.dependency_overrides[get_current_user] = lambda: {
        "id": "test-user",
        "email": "test@example.com",
    }
    test_app.dependency_overrides[get_tenant_id] = lambda: UUID(
        "00000000-0000-0000-0000-000000000001"
    )
    yield
    test_app.dependency_overrides.clear()


def test_list_campaigns_invokes_service(monkeypatch):
    mock_service = CampaignService()
    sample = [
        {
            "id": "camp-1",
            "title": "Launch",
            "objective": "Grow",
            "status": "active",
            "workspace_id": "00000000-0000-0000-0000-000000000001",
            "campaign_tag": "launch-abc",
            "arc_data": {},
            "phase_order": [],
            "milestones": [],
            "move_count": 3,
        }
    ]

    async def fake_list(*args, **kwargs):
        assert kwargs.get("limit") == 20
        assert kwargs.get("offset") == 2
        return sample

    mock_service.list_campaigns = fake_list
    test_app.dependency_overrides[get_campaign_service] = lambda: mock_service
    response = client.get("/v1/campaigns?status=active&limit=20&offset=2")
    assert response.status_code == 200
    assert response.json()["data"]["campaigns"] == sample
    test_app.dependency_overrides.pop(get_campaign_service, None)


def test_get_campaign_detail_returns_data(monkeypatch):
    mock_service = CampaignService()
    detail = {"id": "camp-1", "moves": []}

    async def fake_detail(*args, **kwargs):
        return detail

    mock_service.get_campaign_with_moves = fake_detail
    test_app.dependency_overrides[get_campaign_service] = lambda: mock_service
    response = client.get("/v1/campaigns/camp-1")
    assert response.status_code == 200
    assert response.json()["data"]["campaign"] == detail
    test_app.dependency_overrides.pop(get_campaign_service, None)


def test_update_campaign_calls_service(monkeypatch):
    mock_service = CampaignService()
    updated = {"id": "camp-1", "phase_order": ["phase-1"]}

    async def fake_update(*args, **kwargs):
        return updated

    mock_service.update_campaign = fake_update
    test_app.dependency_overrides[get_campaign_service] = lambda: mock_service
    response = client.put(
        "/v1/campaigns/camp-1",
        json={"title": "Updated", "phase_order": ["phase-1"]},
    )
    assert response.status_code == 200
    assert response.json()["data"]["campaign"] == updated
    test_app.dependency_overrides.pop(get_campaign_service, None)


def test_delete_campaign_invokes_archive(monkeypatch):
    mock_service = CampaignService()

    async def fake_delete(*args, **kwargs):
        return None

    mock_service.soft_delete_campaign = fake_delete
    test_app.dependency_overrides[get_campaign_service] = lambda: mock_service
    response = client.delete("/v1/campaigns/camp-1")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "archived"
    test_app.dependency_overrides.pop(get_campaign_service, None)


def test_list_moves_uses_filters(monkeypatch):
    mock_service = MoveService()

    async def fake_list(workspace_id, campaign_id=None, status=None, **kwargs):
        assert workspace_id == "00000000-0000-0000-0000-000000000001"
        assert campaign_id == "camp-1"
        assert status == "pending"
        return [{"id": "move-1"}]

    mock_service.list_moves = fake_list
    test_app.dependency_overrides[get_move_service] = lambda: mock_service
    response = client.get("/v1/moves?campaign_id=camp-1&status=pending")
    assert response.status_code == 200
    assert response.json()["data"]["moves"] == [{"id": "move-1"}]
    test_app.dependency_overrides.pop(get_move_service, None)


def test_create_campaign_invokes_service():
    mock_service = CampaignService()

    async def fake_create(workspace_id, payload):
        assert workspace_id == "00000000-0000-0000-0000-000000000001"
        assert payload["title"] == "New Campaign"
        return {"id": "camp-new", "title": payload["title"]}

    mock_service.create_campaign = fake_create
    test_app.dependency_overrides[get_campaign_service] = lambda: mock_service
    response = client.post(
        "/v1/campaigns",
        json={
            "title": "New Campaign",
            "objective": "Reach more users",
            "status": "active",
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["id"] == "camp-new"
    test_app.dependency_overrides.pop(get_campaign_service, None)
