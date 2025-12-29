from typing import Dict, List
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from core.auth import get_current_user
from main import app


class MockUser:
    def __init__(
        self, user_id: str = "test_user", tenant_id: str = "test_tenant"
    ) -> None:
        self.id = user_id
        self.tenant_id = tenant_id
        self.email = "test@example.com"


@pytest.fixture(autouse=True)
def mock_cache(monkeypatch):
    class DummyCache:
        def __init__(self):
            self.store: Dict[str, Dict[str, object]] = {}

        def set_json(
            self, key: str, value: Dict[str, object], expiry_seconds: int = 3600
        ):
            self.store[key] = value
            return True

        def get_json(self, key: str):
            return self.store.get(key)

    monkeypatch.setattr("core.cache.get_cache_manager", lambda: DummyCache())
    yield


@pytest.fixture(autouse=True)
def mock_auth():
    app.dependency_overrides[get_current_user] = lambda: MockUser()
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_council_nodes(monkeypatch):
    async def fake_debate(state):
        return {"parallel_thoughts": [], "last_agent": "debate"}

    async def fake_critique(state):
        return {
            "debate_history": [{"round_number": 1, "proposals": [], "critiques": []}],
            "last_agent": "critique",
        }

    async def fake_consensus(state):
        return {
            "consensus_metrics": {"alignment": 0.8, "confidence": 0.7, "risk": 0.1},
            "last_agent": "consensus",
        }

    async def fake_synthesis(state):
        return {
            "final_strategic_decree": "Win the quarter",
            "rejected_paths": [{"path": "Alt", "reason": "low ROI"}],
            "last_agent": "synthesis",
        }

    async def fake_reasoning(state):
        return {"reasoning_chain_id": "chain-123", "last_agent": "logger"}

    async def fake_rejections(state):
        return {"last_agent": "rejector"}

    async def fake_campaign(state):
        return {
            "campaign_id": "camp-123",
            "campaign_data": {
                "title": "Campaign",
                "objective": "Reach users",
                "arc_data": {"phases": ["Plan", "Execute"]},
            },
            "last_agent": "campaign",
        }

    async def fake_decomp(state):
        return {
            "suggested_moves": [
                {"title": "Move 1", "description": "Do it", "type": "ops"}
            ]
        }

    async def fake_refiner(state):
        return {
            "refined_moves": [
                {
                    "title": "Move 1",
                    "description": "Do it",
                    "type": "ops",
                    "tool_requirements": ["tool"],
                    "muse_prompt": "Create",
                }
            ]
        }

    async def fake_success(state):
        return {
            "evaluated_moves": [
                {
                    "title": "Move 1",
                    "description": "Do it",
                    "type": "ops",
                    "confidence_score": 80,
                }
            ]
        }

    async def fake_kill(state):
        return {"approved_moves": [{"title": "Move 1"}], "discarded_moves": []}

    monkeypatch.setattr("services.council_service.council_debate_node", fake_debate)
    monkeypatch.setattr("services.council_service.cross_critique_node", fake_critique)
    monkeypatch.setattr(
        "services.council_service.consensus_scorer_node", fake_consensus
    )
    monkeypatch.setattr("services.council_service.synthesis_node", fake_synthesis)
    monkeypatch.setattr(
        "services.council_service.reasoning_chain_logger_node", fake_reasoning
    )
    monkeypatch.setattr(
        "services.council_service.rejection_logger_node", fake_rejections
    )
    monkeypatch.setattr(
        "services.council_service.campaign_arc_generator_node", fake_campaign
    )
    monkeypatch.setattr("services.council_service.move_decomposition_node", fake_decomp)
    monkeypatch.setattr("services.council_service.move_refiner_node", fake_refiner)
    monkeypatch.setattr("services.council_service.success_predictor_node", fake_success)
    monkeypatch.setattr("services.council_service.kill_switch_monitor_node", fake_kill)
    yield


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_generate_move_plan_returns_expected_keys(async_client):
    response = await async_client.post(
        "/council/generate_move_plan",
        json={"workspace_id": "ws-1", "objective": "Grow", "details": "More details"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "decree" in data
    assert "consensus_metrics" in data
    assert "proposed_moves" in data
    assert "refined_moves" in data
    assert "approved_moves" in data
    assert "discarded_moves" in data
    assert "debate_history" in data
    assert data["approved_moves"]


@pytest.mark.asyncio
async def test_generate_campaign_plan_returns_campaign_data(async_client):
    response = await async_client.post(
        "/council/generate_campaign_plan",
        json={
            "workspace_id": "ws-1",
            "objective": "Grow",
            "details": "More details",
            "target_icp": "founders",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["campaign_data"]["title"] == "Campaign"
    assert data["campaign_data"]["objective"] == "Reach users"
    assert data["refined_moves"]
    assert data["rationale"]["reasoning_chain_id"] == "chain-123"


@pytest.mark.asyncio
async def test_moves_create_calls_save_move(monkeypatch, async_client):
    saved_moves: List[Dict[str, object]] = []

    async def fake_save_move(campaign_id, data):
        saved_moves.append(data)
        return "move-1"

    monkeypatch.setattr("db.save_reasoning_chain", AsyncMock(return_value="chain-xyz"))
    monkeypatch.setattr("db.save_move", fake_save_move)

    response = await async_client.post(
        "/moves/create",
        json={
            "workspace_id": "ws-1",
            "campaign_id": None,
            "rationale": {
                "final_decree": "Test",
                "consensus_metrics": {"alignment": 0.9},
                "reasoning_chain_id": "chain-xyz",
            },
            "moves": [
                {
                    "title": "Move A",
                    "description": "Execute",
                    "move_type": "ops",
                    "priority": 3,
                    "tool_requirements": ["tool"],
                    "muse_prompt": "Create",
                }
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"]
    assert body["reasoning_chain_id"] == "chain-xyz"
    assert saved_moves[0]["reasoning_chain_id"] == "chain-xyz"


@pytest.mark.asyncio
async def test_campaigns_create_persists_data(monkeypatch, async_client):
    monkeypatch.setattr("db.save_campaign", AsyncMock(return_value="camp-xyz"))
    monkeypatch.setattr("db.save_move", AsyncMock(return_value="move-abc"))

    response = await async_client.post(
        "/campaigns/create",
        json={
            "workspace_id": "ws-1",
            "campaign_data": {
                "title": "Campaign X",
                "objective": "Test",
                "arc_data": {"phases": ["Plan"]},
                "status": "draft",
            },
            "moves": [
                {
                    "title": "Move B",
                    "description": "Execute",
                    "move_type": "ops",
                }
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["campaign_id"] == "camp-xyz"
    assert body["move_ids"][0] == "move-abc"
