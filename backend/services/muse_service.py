"""
Muse Service: LangGraph-first AI generation orchestration.

This service is intentionally thin and delegates generation flow to the
canonical `LangGraphMuseOrchestrator`.
"""

from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from backend.agents.langgraph_muse_orchestrator import (
    REASONING_DEPTH_PROFILES,
    langgraph_muse_orchestrator,
)
from backend.services.base_service import BaseService
from backend.services.registry import registry


class MuseService(BaseService):
    def __init__(self) -> None:
        super().__init__("muse_service")

    async def check_health(self) -> Dict[str, Any]:
        """Check if Muse dependencies are available."""
        try:
            from backend.services.vertex_ai_service import vertex_ai_service

            if not vertex_ai_service:
                return {"status": "disabled", "detail": "Vertex AI not configured"}

            vertex_health = await vertex_ai_service.check_health()
            return {
                "status": vertex_health.get("status", "unknown"),
                "engine": "vertex_ai",
                "orchestrator": "langgraph",
            }
        except Exception as exc:
            return {"status": "unhealthy", "error": str(exc), "orchestrator": "langgraph"}

    async def generate(
        self,
        workspace_id: str,
        task: str,
        content_type: str = "general",
        tone: str = "professional",
        target_audience: str = "general",
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 800,
        temperature: float = 0.7,
        reasoning_depth: Literal["low", "medium", "high"] = "medium",
        intensity: Optional[Literal["low", "medium", "high"]] = None,
        execution_mode: Optional[Literal["single", "council", "swarm"]] = None,
    ) -> Dict[str, Any]:
        """Generate content through the canonical LangGraph orchestration pipeline."""

        async def _execute() -> Dict[str, Any]:
            return await langgraph_muse_orchestrator.invoke(
                workspace_id=workspace_id,
                task=task,
                content_type=content_type,
                tone=tone,
                target_audience=target_audience,
                context=context,
                max_tokens=max_tokens,
                temperature=temperature,
                reasoning_depth=reasoning_depth,
                intensity=intensity,
                execution_mode=execution_mode,
            )

        return await self.execute_with_retry(_execute)


muse_service = MuseService()
registry.register(muse_service)
