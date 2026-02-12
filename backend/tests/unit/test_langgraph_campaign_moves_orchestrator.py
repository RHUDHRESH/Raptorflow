from __future__ import annotations

import importlib

import pytest

from backend.agents.langgraph_campaign_moves_orchestrator import (
    langgraph_campaign_moves_orchestrator,
)


@pytest.mark.asyncio
async def test_campaign_moves_orchestrator_bundle(monkeypatch: pytest.MonkeyPatch) -> None:
    campaign_module = importlib.import_module("backend.services.campaign_service")
    move_module = importlib.import_module("backend.services.move_service")

    class FakeCampaignService:
        @staticmethod
        def get_campaign(workspace_id: str, campaign_id: str):
            assert workspace_id == "11111111-1111-1111-1111-111111111111"
            assert campaign_id == "22222222-2222-2222-2222-222222222222"
            return {
                "id": campaign_id,
                "workspace_id": workspace_id,
                "title": "Launch",
                "objective": "launch",
                "status": "active",
            }

        @staticmethod
        def list_campaigns(workspace_id: str):
            return [{"id": "c1", "workspace_id": workspace_id, "title": "C1"}]

    class FakeMoveService:
        @staticmethod
        def list_moves(workspace_id: str):
            return [
                {"id": "m1", "campaignId": "22222222-2222-2222-2222-222222222222"},
                {"id": "m2", "campaignId": "other"},
            ]

    monkeypatch.setattr(campaign_module, "campaign_service", FakeCampaignService())
    monkeypatch.setattr(move_module, "move_service", FakeMoveService())

    bundle = await langgraph_campaign_moves_orchestrator.campaign_moves_bundle(
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
    )
    campaigns = await langgraph_campaign_moves_orchestrator.list_campaigns(
        "11111111-1111-1111-1111-111111111111"
    )

    assert bundle["campaign"]["title"] == "Launch"
    assert len(bundle["moves"]) == 1
    assert campaigns[0]["id"] == "c1"

