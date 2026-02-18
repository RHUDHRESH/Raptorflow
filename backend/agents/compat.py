"""Temporary compatibility gateways for deprecated direct orchestrator imports."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Literal

from backend.agents.campaign_moves.orchestrator import langgraph_campaign_moves_orchestrator
from backend.agents.optional.orchestrator import langgraph_optional_orchestrator


class CampaignMovesGateway:
    async def list_campaigns(self, workspace_id: str) -> list[Dict[str, Any]]:
        return await langgraph_campaign_moves_orchestrator.list_campaigns(workspace_id)

    async def create_campaign(self, workspace_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await langgraph_campaign_moves_orchestrator.create_campaign(workspace_id, payload)

    async def get_campaign(self, workspace_id: str, campaign_id: str) -> Dict[str, Any] | None:
        return await langgraph_campaign_moves_orchestrator.get_campaign(workspace_id, campaign_id)

    async def update_campaign(
        self,
        workspace_id: str,
        campaign_id: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any] | None:
        return await langgraph_campaign_moves_orchestrator.update_campaign(
            workspace_id,
            campaign_id,
            payload,
        )

    async def delete_campaign(self, workspace_id: str, campaign_id: str) -> bool:
        return await langgraph_campaign_moves_orchestrator.delete_campaign(workspace_id, campaign_id)

    async def campaign_moves_bundle(self, workspace_id: str, campaign_id: str) -> Dict[str, Any]:
        return await langgraph_campaign_moves_orchestrator.campaign_moves_bundle(
            workspace_id,
            campaign_id,
        )

    async def list_moves(self, workspace_id: str) -> list[Dict[str, Any]]:
        return await langgraph_campaign_moves_orchestrator.list_moves(workspace_id)

    async def create_move(self, workspace_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await langgraph_campaign_moves_orchestrator.create_move(workspace_id, payload)

    async def update_move(
        self,
        workspace_id: str,
        move_id: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any] | None:
        return await langgraph_campaign_moves_orchestrator.update_move(
            workspace_id,
            move_id,
            payload,
        )

    async def delete_move(self, workspace_id: str, move_id: str) -> bool:
        return await langgraph_campaign_moves_orchestrator.delete_move(workspace_id, move_id)


class OptionalGateway:
    async def run(
        self,
        *,
        operation: Literal["search", "scraper"],
        payload: Dict[str, Any],
        executor: Callable[[], Awaitable[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        return await langgraph_optional_orchestrator.run(
            operation=operation,
            payload=payload,
            executor=executor,
        )


campaign_moves_gateway = CampaignMovesGateway()
optional_gateway = OptionalGateway()
