"""
LangGraph orchestration for BCM context operations.

Operations:
- seed
- rebuild
- reflect
"""

from __future__ import annotations

from typing import Any, Dict, Literal, Optional, TypedDict

from langgraph.graph import END, START, StateGraph


ContextOperation = Literal["seed", "rebuild", "reflect"]


class ContextGraphState(TypedDict, total=False):
    operation: ContextOperation
    workspace_id: str
    business_context: Dict[str, Any]
    row: Optional[Dict[str, Any]]
    result: Dict[str, Any]


def _compute_completion(manifest: Dict[str, Any]) -> int:
    sections = [
        "foundation",
        "icps",
        "competitive",
        "messaging",
        "channels",
        "market",
        "identity",
        "prompt_kit",
        "guardrails_v2",
    ]
    filled = 0
    for section in sections:
        value = manifest.get(section)
        if value:
            if isinstance(value, list) and len(value) > 0:
                filled += 1
            elif isinstance(value, dict) and any(v for v in value.values() if v):
                filled += 1
    return int((filled / len(sections)) * 100)


def format_bcm_row(row: Dict[str, Any]) -> Dict[str, Any]:
    manifest = row.get("manifest") or {}
    return {
        "manifest": manifest,
        "version": row.get("version", 0),
        "checksum": row.get("checksum", ""),
        "token_estimate": row.get("token_estimate", 0),
        "created_at": row.get("created_at"),
        "completion_pct": _compute_completion(manifest),
        "synthesized": (manifest.get("meta") or {}).get("synthesized", False),
    }


class LangGraphContextOrchestrator:
    def __init__(self) -> None:
        self._graph = self._build_graph().compile()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(ContextGraphState)

        graph.add_node("route_operation", self._route_operation)
        graph.add_node("seed", self._seed)
        graph.add_node("rebuild", self._rebuild)
        graph.add_node("reflect", self._reflect)

        graph.add_edge(START, "route_operation")
        graph.add_conditional_edges(
            "route_operation",
            self._operation_branch,
            {
                "seed": "seed",
                "rebuild": "rebuild",
                "reflect": "reflect",
            },
        )
        graph.add_edge("seed", END)
        graph.add_edge("rebuild", END)
        graph.add_edge("reflect", END)

        return graph

    async def _route_operation(self, state: ContextGraphState) -> ContextGraphState:
        return state

    def _operation_branch(self, state: ContextGraphState) -> str:
        return state["operation"]

    async def _seed(self, state: ContextGraphState) -> ContextGraphState:
        from backend.services import bcm_service

        row = await bcm_service.seed_from_business_context_async(
            state["workspace_id"],
            state["business_context"],
        )
        return {"row": row}

    async def _rebuild(self, state: ContextGraphState) -> ContextGraphState:
        from backend.services import bcm_service

        row = await bcm_service.rebuild_async(state["workspace_id"])
        return {"row": row}

    async def _reflect(self, state: ContextGraphState) -> ContextGraphState:
        from backend.services import bcm_reflector

        result = await bcm_reflector.reflect(state["workspace_id"])
        return {"result": result}

    async def seed(self, workspace_id: str, business_context: Dict[str, Any]) -> Dict[str, Any]:
        final_state = await self._graph.ainvoke(
            {
                "operation": "seed",
                "workspace_id": workspace_id,
                "business_context": business_context,
            }
        )
        return final_state["row"]

    async def rebuild(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        final_state = await self._graph.ainvoke(
            {
                "operation": "rebuild",
                "workspace_id": workspace_id,
            }
        )
        return final_state.get("row")

    async def reflect(self, workspace_id: str) -> Dict[str, Any]:
        final_state = await self._graph.ainvoke(
            {
                "operation": "reflect",
                "workspace_id": workspace_id,
            }
        )
        return final_state["result"]


langgraph_context_orchestrator = LangGraphContextOrchestrator()

