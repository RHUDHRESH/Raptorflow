"""
Canonical LangGraph orchestration for Muse generation.

Design goals:
- single graph-based orchestration runtime
- no hidden fallback orchestration frameworks
- modular nodes with explicit responsibilities
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, Literal, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from backend.services.exceptions import ServiceError, ServiceUnavailableError

logger = logging.getLogger(__name__)


REASONING_DEPTH_PROFILES: Dict[str, Dict[str, Any]] = {
    "low": {
        "max_tokens_cap": 500,
        "temperature_min": 0.2,
        "temperature_max": 0.5,
        "memory_limit": 3,
    },
    "medium": {
        "max_tokens_cap": 1000,
        "temperature_min": 0.3,
        "temperature_max": 0.8,
        "memory_limit": 6,
    },
    "high": {
        "max_tokens_cap": 1800,
        "temperature_min": 0.4,
        "temperature_max": 0.9,
        "memory_limit": 10,
    },
}


def resolve_generation_profile(
    *,
    max_tokens: int,
    temperature: float,
    reasoning_depth: str,
) -> Dict[str, Any]:
    """Normalize generation settings from reasoning depth profile."""
    depth = (reasoning_depth or "medium").lower()
    profile = REASONING_DEPTH_PROFILES.get(depth, REASONING_DEPTH_PROFILES["medium"])
    effective_max_tokens = min(int(max_tokens), int(profile["max_tokens_cap"]))
    effective_temperature = max(
        float(profile["temperature_min"]),
        min(float(temperature), float(profile["temperature_max"])),
    )
    return {
        "reasoning_depth": depth,
        "profile": profile,
        "effective_max_tokens": effective_max_tokens,
        "effective_temperature": effective_temperature,
    }


class MuseGraphState(TypedDict, total=False):
    workspace_id: str
    task: str
    content_type: str
    tone: str
    target_audience: str
    context: Dict[str, Any]
    max_tokens: int
    temperature: float
    reasoning_depth: str

    profile: Dict[str, Any]
    effective_max_tokens: int
    effective_temperature: float

    manifest: Optional[Dict[str, Any]]
    memories: Optional[list[Dict[str, Any]]]
    system_prompt: Optional[str]
    user_prompt: str
    prompt_for_log: str

    llm_result: Dict[str, Any]
    generation_id: str
    response: Dict[str, Any]


class LangGraphMuseOrchestrator:
    """Single orchestration entrypoint for Muse generation."""

    def __init__(self) -> None:
        self._graph = self._build_graph().compile()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(MuseGraphState)

        graph.add_node("resolve_profile", self._resolve_profile)
        graph.add_node("load_workspace_context", self._load_workspace_context)
        graph.add_node("compile_prompt", self._compile_prompt)
        graph.add_node("run_generation", self._run_generation)
        graph.add_node("log_generation", self._log_generation)
        graph.add_node("assemble_response", self._assemble_response)

        graph.add_edge(START, "resolve_profile")
        graph.add_edge("resolve_profile", "load_workspace_context")
        graph.add_edge("load_workspace_context", "compile_prompt")
        graph.add_edge("compile_prompt", "run_generation")
        graph.add_edge("run_generation", "log_generation")
        graph.add_edge("log_generation", "assemble_response")
        graph.add_edge("assemble_response", END)

        return graph

    async def _resolve_profile(self, state: MuseGraphState) -> MuseGraphState:
        resolved = resolve_generation_profile(
            max_tokens=state.get("max_tokens", 800),
            temperature=state.get("temperature", 0.7),
            reasoning_depth=state.get("reasoning_depth", "medium"),
        )
        return {
            "reasoning_depth": resolved["reasoning_depth"],
            "profile": resolved["profile"],
            "effective_max_tokens": resolved["effective_max_tokens"],
            "effective_temperature": resolved["effective_temperature"],
        }

    async def _load_workspace_context(self, state: MuseGraphState) -> MuseGraphState:
        from backend.services import bcm_service, bcm_memory

        workspace_id = state["workspace_id"]
        profile = state["profile"]
        memories: Optional[list[Dict[str, Any]]] = None
        manifest = bcm_service.get_manifest_fast(workspace_id)

        if manifest:
            try:
                memories = bcm_memory.get_relevant_memories(
                    workspace_id,
                    limit=int(profile["memory_limit"]),
                ) or None
            except Exception as exc:
                logger.warning("Memory fetch failed for workspace %s: %s", workspace_id, exc)

        return {
            "manifest": manifest,
            "memories": memories,
        }

    async def _compile_prompt(self, state: MuseGraphState) -> MuseGraphState:
        manifest = state.get("manifest")
        task = state["task"]
        content_type = state.get("content_type", "general")
        tone = state.get("tone", "professional")
        target_audience = state.get("target_audience", "general")
        context = state.get("context") or {}

        if manifest:
            from backend.services.prompt_compiler import (
                build_user_prompt,
                get_or_compile_system_prompt,
            )

            system_prompt = get_or_compile_system_prompt(
                workspace_id=state["workspace_id"],
                manifest=manifest,
                content_type=content_type,
                target_icp=target_audience if target_audience != "general" else None,
                memories=state.get("memories"),
            )
            user_prompt = build_user_prompt(
                task=task,
                content_type=content_type,
                tone=tone,
                target_audience=target_audience,
            )
            prompt_for_log = f"[system]{system_prompt[:500]}[/system]\n{user_prompt}"
            return {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "prompt_for_log": prompt_for_log,
            }

        fallback_prompt = "\n".join(
            [
                f"Task: {task}",
                f"Type: {content_type}",
                f"Tone: {tone}",
                f"Target audience: {target_audience}",
                f"Context: {json.dumps(context)}",
            ]
        )
        return {
            "system_prompt": None,
            "user_prompt": fallback_prompt,
            "prompt_for_log": fallback_prompt,
        }

    async def _run_generation(self, state: MuseGraphState) -> MuseGraphState:
        from backend.services.vertex_ai_service import vertex_ai_service

        if not vertex_ai_service:
            raise ServiceUnavailableError(
                "Vertex AI unavailable. Configure VERTEX_AI_PROJECT_ID/credentials."
            )

        system_prompt = state.get("system_prompt")
        user_prompt = state["user_prompt"]
        workspace_id = state["workspace_id"]

        if system_prompt:
            result = await vertex_ai_service.generate_with_system(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                workspace_id=workspace_id,
                user_id="langgraph-orchestrator",
                max_tokens=state["effective_max_tokens"],
                temperature=state["effective_temperature"],
            )
        else:
            result = await vertex_ai_service.generate_text(
                prompt=user_prompt,
                workspace_id=workspace_id,
                user_id="langgraph-orchestrator",
                max_tokens=state["effective_max_tokens"],
                temperature=state["effective_temperature"],
            )

        if result.get("status") != "success":
            raise ServiceError(result.get("error") or "Muse generation failed")

        return {"llm_result": result}

    async def _log_generation(self, state: MuseGraphState) -> MuseGraphState:
        from backend.services import bcm_generation_logger
        from backend.services.bcm_reflector import reflect, should_auto_reflect

        result = state["llm_result"]
        manifest = state.get("manifest")
        workspace_id = state["workspace_id"]

        gen_log = bcm_generation_logger.log_generation(
            workspace_id=workspace_id,
            content_type=state.get("content_type", "general"),
            prompt_used=state["prompt_for_log"],
            output=result.get("text") or "",
            bcm_version=(manifest or {}).get("version", 0),
            tokens_used=int(result.get("total_tokens") or 0),
            cost_usd=float(result.get("cost_usd") or 0.0),
        )

        try:
            if should_auto_reflect(workspace_id):
                asyncio.create_task(reflect(workspace_id))
        except Exception as exc:
            logger.warning("Auto-reflection check failed: %s", exc)

        return {"generation_id": gen_log.get("id", "") if gen_log else ""}

    async def _assemble_response(self, state: MuseGraphState) -> MuseGraphState:
        result = state["llm_result"]
        response = {
            "success": True,
            "content": result.get("text") or "",
            "tokens_used": int(result.get("total_tokens") or 0),
            "cost_usd": float(result.get("cost_usd") or 0.0),
            "metadata": {
                "model": result.get("model"),
                "model_type": result.get("model_type"),
                "generation_time_seconds": result.get("generation_time_seconds"),
                "structured_prompt": bool(state.get("manifest")),
                "generation_id": state.get("generation_id", ""),
                "reasoning_depth": state.get("reasoning_depth", "medium"),
                "memory_limit": int((state.get("profile") or {}).get("memory_limit", 0)),
                "effective_max_tokens": state.get("effective_max_tokens", 0),
                "effective_temperature": state.get("effective_temperature", 0.0),
                "orchestrator": "langgraph",
            },
        }
        return {"response": response}

    async def invoke(
        self,
        *,
        workspace_id: str,
        task: str,
        content_type: str = "general",
        tone: str = "professional",
        target_audience: str = "general",
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 800,
        temperature: float = 0.7,
        reasoning_depth: Literal["low", "medium", "high"] = "medium",
    ) -> Dict[str, Any]:
        final_state = await self._graph.ainvoke(
            {
                "workspace_id": workspace_id,
                "task": task,
                "content_type": content_type,
                "tone": tone,
                "target_audience": target_audience,
                "context": context or {},
                "max_tokens": max_tokens,
                "temperature": temperature,
                "reasoning_depth": reasoning_depth,
            }
        )
        return final_state["response"]


langgraph_muse_orchestrator = LangGraphMuseOrchestrator()

