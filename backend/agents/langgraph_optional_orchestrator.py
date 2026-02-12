"""
LangGraph boundary for optional modules (search/scraper).

Responsibilities:
- enforce module feature flags
- standardize execution metadata
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from backend.config import settings
from backend.services.exceptions import ServiceUnavailableError


OptionalModuleOperation = Literal["search", "scraper"]


class OptionalModuleState(TypedDict, total=False):
    operation: OptionalModuleOperation
    executor: Callable[[], Awaitable[Dict[str, Any]]]
    payload: Dict[str, Any]
    result: Dict[str, Any]


class LangGraphOptionalOrchestrator:
    def __init__(self) -> None:
        self._graph = self._build_graph().compile()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(OptionalModuleState)
        graph.add_node("check_enabled", self._check_enabled)
        graph.add_node("execute", self._execute)
        graph.add_node("finalize", self._finalize)

        graph.add_edge(START, "check_enabled")
        graph.add_edge("check_enabled", "execute")
        graph.add_edge("execute", "finalize")
        graph.add_edge("finalize", END)
        return graph

    async def _check_enabled(self, state: OptionalModuleState) -> OptionalModuleState:
        op = state["operation"]
        if op == "search" and not settings.ENABLE_SEARCH_MODULE:
            raise ServiceUnavailableError("Search module is disabled by configuration.")
        if op == "scraper" and not settings.ENABLE_SCRAPER_MODULE:
            raise ServiceUnavailableError("Scraper module is disabled by configuration.")
        return state

    async def _execute(self, state: OptionalModuleState) -> OptionalModuleState:
        result = await state["executor"]()
        return {"result": result}

    async def _finalize(self, state: OptionalModuleState) -> OptionalModuleState:
        result = dict(state.get("result") or {})
        result.setdefault("orchestrator", "langgraph")
        result.setdefault("module", state["operation"])
        return {"result": result}

    async def run(
        self,
        *,
        operation: OptionalModuleOperation,
        payload: Dict[str, Any],
        executor: Callable[[], Awaitable[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        final_state = await self._graph.ainvoke(
            {"operation": operation, "payload": payload, "executor": executor}
        )
        return final_state["result"]


langgraph_optional_orchestrator = LangGraphOptionalOrchestrator()

