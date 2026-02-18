"""
LangGraph orchestration for campaign and move domain operations.

Provides a single orchestration boundary for:
- campaign CRUD
- move CRUD
- campaign-to-moves bundle retrieval
"""

from __future__ import annotations

from typing import Any, Dict, Literal, Optional, TypedDict

from langgraph.graph import END, START, StateGraph


CampaignMoveOperation = Literal[
    "list_campaigns",
    "create_campaign",
    "get_campaign",
    "update_campaign",
    "delete_campaign",
    "list_moves",
    "create_move",
    "update_move",
    "delete_move",
    "campaign_moves_bundle",
]


class CampaignMoveState(TypedDict, total=False):
    operation: CampaignMoveOperation
    workspace_id: str
    campaign_id: str
    move_id: str
    payload: Dict[str, Any]
    result: Any


class LangGraphCampaignMovesOrchestrator:
    def __init__(self) -> None:
        self._graph = self._build_graph().compile()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(CampaignMoveState)

        graph.add_node("route_operation", self._route_operation)
        graph.add_node("list_campaigns", self._list_campaigns)
        graph.add_node("create_campaign", self._create_campaign)
        graph.add_node("get_campaign", self._get_campaign)
        graph.add_node("update_campaign", self._update_campaign)
        graph.add_node("delete_campaign", self._delete_campaign)
        graph.add_node("list_moves", self._list_moves)
        graph.add_node("create_move", self._create_move)
        graph.add_node("update_move", self._update_move)
        graph.add_node("delete_move", self._delete_move)
        graph.add_node("campaign_moves_bundle", self._campaign_moves_bundle)

        graph.add_edge(START, "route_operation")
        graph.add_conditional_edges(
            "route_operation",
            self._operation_branch,
            {
                "list_campaigns": "list_campaigns",
                "create_campaign": "create_campaign",
                "get_campaign": "get_campaign",
                "update_campaign": "update_campaign",
                "delete_campaign": "delete_campaign",
                "list_moves": "list_moves",
                "create_move": "create_move",
                "update_move": "update_move",
                "delete_move": "delete_move",
                "campaign_moves_bundle": "campaign_moves_bundle",
            },
        )

        graph.add_edge("list_campaigns", END)
        graph.add_edge("create_campaign", END)
        graph.add_edge("get_campaign", END)
        graph.add_edge("update_campaign", END)
        graph.add_edge("delete_campaign", END)
        graph.add_edge("list_moves", END)
        graph.add_edge("create_move", END)
        graph.add_edge("update_move", END)
        graph.add_edge("delete_move", END)
        graph.add_edge("campaign_moves_bundle", END)

        return graph

    async def _route_operation(self, state: CampaignMoveState) -> CampaignMoveState:
        return state

    def _operation_branch(self, state: CampaignMoveState) -> str:
        return state["operation"]

    async def _list_campaigns(self, state: CampaignMoveState) -> CampaignMoveState:
        from backend.services.campaign_service import campaign_service

        return {"result": campaign_service.list_campaigns(state["workspace_id"])}

    async def _create_campaign(self, state: CampaignMoveState) -> CampaignMoveState:
        from backend.services.campaign_service import campaign_service

        return {
            "result": campaign_service.create_campaign(
                state["workspace_id"],
                state["payload"],
            )
        }

    async def _get_campaign(self, state: CampaignMoveState) -> CampaignMoveState:
        from backend.services.campaign_service import campaign_service

        return {
            "result": campaign_service.get_campaign(
                state["workspace_id"],
                state["campaign_id"],
            )
        }

    async def _update_campaign(self, state: CampaignMoveState) -> CampaignMoveState:
        from backend.services.campaign_service import campaign_service

        return {
            "result": campaign_service.update_campaign(
                state["workspace_id"],
                state["campaign_id"],
                state["payload"],
            )
        }

    async def _delete_campaign(self, state: CampaignMoveState) -> CampaignMoveState:
        from backend.services.campaign_service import campaign_service

        return {
            "result": campaign_service.delete_campaign(
                state["workspace_id"],
                state["campaign_id"],
            )
        }

    async def _list_moves(self, state: CampaignMoveState) -> CampaignMoveState:
        from backend.services.move_service import move_service

        return {"result": move_service.list_moves(state["workspace_id"])}

    async def _create_move(self, state: CampaignMoveState) -> CampaignMoveState:
        from backend.services.move_service import move_service

        return {
            "result": move_service.create_move(
                state["workspace_id"],
                state["payload"],
            )
        }

    async def _update_move(self, state: CampaignMoveState) -> CampaignMoveState:
        from backend.services.move_service import move_service

        return {
            "result": move_service.update_move(
                state["workspace_id"],
                state["move_id"],
                state["payload"],
            )
        }

    async def _delete_move(self, state: CampaignMoveState) -> CampaignMoveState:
        from backend.services.move_service import move_service

        return {
            "result": move_service.delete_move(
                state["workspace_id"],
                state["move_id"],
            )
        }

    async def _campaign_moves_bundle(self, state: CampaignMoveState) -> CampaignMoveState:
        from backend.services.campaign_service import campaign_service
        from backend.services.move_service import move_service

        campaign = campaign_service.get_campaign(state["workspace_id"], state["campaign_id"])
        if not campaign:
            return {"result": {"campaign": None, "moves": []}}
        moves = move_service.list_moves(state["workspace_id"])
        linked_moves = [move for move in moves if move.get("campaignId") == state["campaign_id"]]
        return {"result": {"campaign": campaign, "moves": linked_moves}}

    async def _invoke(self, payload: CampaignMoveState) -> Any:
        final_state = await self._graph.ainvoke(payload)
        return final_state.get("result")

    async def list_campaigns(self, workspace_id: str) -> list[Dict[str, Any]]:
        result = await self._invoke({"operation": "list_campaigns", "workspace_id": workspace_id})
        return result or []

    async def create_campaign(self, workspace_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._invoke(
            {"operation": "create_campaign", "workspace_id": workspace_id, "payload": payload}
        )

    async def get_campaign(self, workspace_id: str, campaign_id: str) -> Optional[Dict[str, Any]]:
        return await self._invoke(
            {"operation": "get_campaign", "workspace_id": workspace_id, "campaign_id": campaign_id}
        )

    async def update_campaign(
        self,
        workspace_id: str,
        campaign_id: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        return await self._invoke(
            {
                "operation": "update_campaign",
                "workspace_id": workspace_id,
                "campaign_id": campaign_id,
                "payload": payload,
            }
        )

    async def delete_campaign(self, workspace_id: str, campaign_id: str) -> bool:
        result = await self._invoke(
            {
                "operation": "delete_campaign",
                "workspace_id": workspace_id,
                "campaign_id": campaign_id,
            }
        )
        return bool(result)

    async def list_moves(self, workspace_id: str) -> list[Dict[str, Any]]:
        result = await self._invoke({"operation": "list_moves", "workspace_id": workspace_id})
        return result or []

    async def create_move(self, workspace_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._invoke(
            {"operation": "create_move", "workspace_id": workspace_id, "payload": payload}
        )

    async def update_move(
        self,
        workspace_id: str,
        move_id: str,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        return await self._invoke(
            {
                "operation": "update_move",
                "workspace_id": workspace_id,
                "move_id": move_id,
                "payload": payload,
            }
        )

    async def delete_move(self, workspace_id: str, move_id: str) -> bool:
        result = await self._invoke(
            {
                "operation": "delete_move",
                "workspace_id": workspace_id,
                "move_id": move_id,
            }
        )
        return bool(result)

    async def campaign_moves_bundle(self, workspace_id: str, campaign_id: str) -> Dict[str, Any]:
        result = await self._invoke(
            {
                "operation": "campaign_moves_bundle",
                "workspace_id": workspace_id,
                "campaign_id": campaign_id,
            }
        )
        return result or {"campaign": None, "moves": []}


langgraph_campaign_moves_orchestrator = LangGraphCampaignMovesOrchestrator()

