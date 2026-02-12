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

from backend.agents.ai_runtime_profiles import (
    intensity_profile,
    normalize_execution_mode,
    normalize_intensity,
)
from backend.config import settings
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
    reasoning_depth: Optional[str],
    intensity: Optional[str],
    execution_mode: Optional[str],
) -> Dict[str, Any]:
    """Normalize generation settings from reasoning depth profile."""
    runtime_intensity = normalize_intensity(intensity or settings.AI_DEFAULT_INTENSITY)
    runtime_execution_mode = normalize_execution_mode(
        execution_mode or settings.AI_EXECUTION_MODE
    )
    intensity_cfg = (intensity_profile(runtime_intensity).get("muse") or {})

    default_depth = str(intensity_cfg.get("reasoning_depth") or "medium")
    depth = (reasoning_depth or default_depth).lower()
    profile = REASONING_DEPTH_PROFILES.get(depth, REASONING_DEPTH_PROFILES[default_depth])

    token_multiplier = float(intensity_cfg.get("token_multiplier") or 1.0)
    requested_tokens = int(max_tokens * token_multiplier)
    effective_max_tokens = min(requested_tokens, int(profile["max_tokens_cap"]))

    adjusted_temperature = float(temperature) + float(
        intensity_cfg.get("temperature_delta") or 0.0
    )
    effective_temperature = max(
        float(profile["temperature_min"]),
        min(adjusted_temperature, float(profile["temperature_max"])),
    )
    ensemble_cap = max(1, int(intensity_cfg.get("ensemble_cap") or 1))
    if runtime_execution_mode == "single":
        ensemble_size = 1
    elif runtime_execution_mode == "council":
        ensemble_size = min(2, ensemble_cap)
    else:
        ensemble_size = min(3, ensemble_cap)

    return {
        "reasoning_depth": depth,
        "intensity": runtime_intensity,
        "execution_mode": runtime_execution_mode,
        "profile": profile,
        "intensity_profile": intensity_cfg,
        "ensemble_size": ensemble_size,
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
    intensity: str
    execution_mode: str

    profile: Dict[str, Any]
    intensity_profile: Dict[str, Any]
    ensemble_size: int
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
            intensity=state.get("intensity"),
            execution_mode=state.get("execution_mode"),
        )
        return {
            "reasoning_depth": resolved["reasoning_depth"],
            "intensity": resolved["intensity"],
            "execution_mode": resolved["execution_mode"],
            "profile": resolved["profile"],
            "intensity_profile": resolved["intensity_profile"],
            "ensemble_size": resolved["ensemble_size"],
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
            fallback = self._build_deterministic_fallback(
                state,
                "Vertex AI service is not configured",
            )
            return {"llm_result": fallback}

        system_prompt = state.get("system_prompt")
        user_prompt = state["user_prompt"]
        workspace_id = state["workspace_id"]
        execution_mode = state.get("execution_mode", "single")
        ensemble_size = max(1, int(state.get("ensemble_size") or 1))

        try:
            if execution_mode == "single" or ensemble_size <= 1:
                result = await self._generate_single(
                    vertex_ai_service=vertex_ai_service,
                    workspace_id=workspace_id,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_tokens=state["effective_max_tokens"],
                    temperature=state["effective_temperature"],
                )
            elif execution_mode == "swarm":
                result = await self._generate_swarm(
                    vertex_ai_service=vertex_ai_service,
                    workspace_id=workspace_id,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_tokens=state["effective_max_tokens"],
                    temperature=state["effective_temperature"],
                    task=state["task"],
                    content_type=state["content_type"],
                    tone=state["tone"],
                    target_audience=state["target_audience"],
                )
            else:
                result = await self._generate_council(
                    vertex_ai_service=vertex_ai_service,
                    workspace_id=workspace_id,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_tokens=state["effective_max_tokens"],
                    temperature=state["effective_temperature"],
                    task=state["task"],
                    tone=state["tone"],
                    target_audience=state["target_audience"],
                )
        except Exception as exc:
            logger.warning("Muse generation failed; using deterministic fallback: %s", exc)
            result = self._build_deterministic_fallback(state, str(exc))

        if result.get("status") != "success":
            result = self._build_deterministic_fallback(
                state,
                result.get("error") or "Muse generation failed",
            )

        return {"llm_result": result}

    def _build_deterministic_fallback(self, state: MuseGraphState, reason: str) -> Dict[str, Any]:
        manifest = state.get("manifest") or {}
        foundation = manifest.get("foundation") if isinstance(manifest, dict) else {}
        company_name = "Your company"
        if isinstance(foundation, dict):
            company_name = str(
                foundation.get("company_name")
                or foundation.get("company")
                or foundation.get("name")
                or company_name
            )

        task = state.get("task", "Create content")
        content_type = state.get("content_type", "general")
        tone = state.get("tone", "professional")
        target = state.get("target_audience", "your audience")

        if content_type in {"social", "linkedin", "twitter"}:
            text = "\n".join(
                [
                    f"{company_name} update for {target}:",
                    "",
                    f"We are shipping a focused move: {task}.",
                    "Here is the promise: faster execution with clearer outcomes.",
                    "Proof point: our workflow is built around BCM + LangGraph orchestration.",
                    "CTA: Reply \"interested\" and we will share the full rollout checklist.",
                ]
            )
        elif content_type in {"email", "newsletter"}:
            text = "\n".join(
                [
                    f"Subject: {company_name} | Strategic update",
                    "",
                    f"Hi {target},",
                    "",
                    f"We're executing: {task}.",
                    "This is designed to improve speed and consistency across campaigns and moves.",
                    "If useful, reply to this email and we'll send the execution brief.",
                ]
            )
        else:
            text = "\n".join(
                [
                    f"{company_name} ({tone}):",
                    f"- Task: {task}",
                    f"- Audience: {target}",
                    "- Core message: convert strategy into repeatable execution.",
                    "- CTA: request the detailed plan and timeline.",
                ]
            )

        approx_tokens = max(60, min(220, len(text) // 4))
        return {
            "status": "success",
            "text": text,
            "input_tokens": 0,
            "output_tokens": approx_tokens,
            "total_tokens": approx_tokens,
            "cost_usd": 0.0,
            "generation_time_seconds": 0.0,
            "model": "deterministic-fallback",
            "model_type": "rule-based",
            "backend": "deterministic_fallback",
            "fallback_reason": reason,
        }

    async def _generate_single(
        self,
        *,
        vertex_ai_service: Any,
        workspace_id: str,
        system_prompt: Optional[str],
        user_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Dict[str, Any]:
        if system_prompt:
            return await vertex_ai_service.generate_with_system(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                workspace_id=workspace_id,
                user_id="langgraph-orchestrator",
                max_tokens=max_tokens,
                temperature=temperature,
            )
        return await vertex_ai_service.generate_text(
            prompt=user_prompt,
            workspace_id=workspace_id,
            user_id="langgraph-orchestrator",
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def _merge_ensemble_results(
        self,
        *,
        final_result: Dict[str, Any],
        all_results: list[Dict[str, Any]],
        mode: str,
        contributors: list[str],
    ) -> Dict[str, Any]:
        total_input_tokens = sum(int(r.get("input_tokens") or 0) for r in all_results)
        total_output_tokens = sum(int(r.get("output_tokens") or 0) for r in all_results)
        total_tokens = sum(int(r.get("total_tokens") or 0) for r in all_results)
        total_cost = sum(float(r.get("cost_usd") or 0.0) for r in all_results)
        total_time = sum(float(r.get("generation_time_seconds") or 0.0) for r in all_results)

        return {
            "status": "success",
            "text": final_result.get("text") or "",
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "total_tokens": total_tokens,
            "cost_usd": total_cost,
            "generation_time_seconds": total_time,
            "model": final_result.get("model"),
            "model_type": final_result.get("model_type"),
            "ensemble": {
                "mode": mode,
                "contributors": contributors,
                "count": len(contributors),
            },
        }

    async def _generate_council(
        self,
        *,
        vertex_ai_service: Any,
        workspace_id: str,
        system_prompt: Optional[str],
        user_prompt: str,
        max_tokens: int,
        temperature: float,
        task: str,
        tone: str,
        target_audience: str,
    ) -> Dict[str, Any]:
        draft_tokens = max(256, int(max_tokens * 0.65))
        draft_specs = [
            (
                "analyst",
                max(0.1, temperature - 0.12),
                "Focus on strategic clarity and directness. Keep claims concrete.",
            ),
            (
                "creative",
                min(0.95, temperature + 0.08),
                "Push originality while remaining brand-safe and actionable.",
            ),
        ]

        tasks = []
        for role, temp, instruction in draft_specs:
            draft_prompt = (
                f"{user_prompt}\n\n"
                f"[Council Role: {role}] {instruction}"
            )
            tasks.append(
                self._generate_single(
                    vertex_ai_service=vertex_ai_service,
                    workspace_id=workspace_id,
                    system_prompt=system_prompt,
                    user_prompt=draft_prompt,
                    max_tokens=draft_tokens,
                    temperature=temp,
                )
            )

        draft_results = await asyncio.gather(*tasks, return_exceptions=True)
        successful_drafts: list[tuple[str, Dict[str, Any]]] = []
        for idx, item in enumerate(draft_results):
            if isinstance(item, Exception):
                logger.warning("Council draft failed: %s", item)
                continue
            if item.get("status") == "success" and (item.get("text") or "").strip():
                successful_drafts.append((draft_specs[idx][0], item))

        if not successful_drafts:
            raise ServiceError("Council generation failed for all draft agents")
        if len(successful_drafts) == 1:
            role, only_result = successful_drafts[0]
            return self._merge_ensemble_results(
                final_result=only_result,
                all_results=[only_result],
                mode="council_fallback_single",
                contributors=[role],
            )

        synthesis_input = "\n\n".join(
            f"[{role.upper()} DRAFT]\n{result.get('text', '')}"
            for role, result in successful_drafts
        )
        synthesis_prompt = (
            f"Task: {task}\n"
            f"Target audience: {target_audience}\n"
            f"Tone: {tone}\n\n"
            "You are the council editor. Merge the drafts below into one final response. "
            "Keep what is strongest, remove redundancy, and improve factual clarity.\n\n"
            f"{synthesis_input}"
        )

        synthesis_result = await self._generate_single(
            vertex_ai_service=vertex_ai_service,
            workspace_id=workspace_id,
            system_prompt=system_prompt,
            user_prompt=synthesis_prompt,
            max_tokens=max_tokens,
            temperature=max(0.2, min(temperature, 0.85)),
        )
        if synthesis_result.get("status") != "success":
            best_role, best_result = successful_drafts[0]
            return self._merge_ensemble_results(
                final_result=best_result,
                all_results=[result for _, result in successful_drafts],
                mode="council_fallback_merge",
                contributors=[best_role for best_role, _ in successful_drafts],
            )

        return self._merge_ensemble_results(
            final_result=synthesis_result,
            all_results=[result for _, result in successful_drafts] + [synthesis_result],
            mode="council",
            contributors=[role for role, _ in successful_drafts] + ["editor"],
        )

    async def _generate_swarm(
        self,
        *,
        vertex_ai_service: Any,
        workspace_id: str,
        system_prompt: Optional[str],
        user_prompt: str,
        max_tokens: int,
        temperature: float,
        task: str,
        content_type: str,
        tone: str,
        target_audience: str,
    ) -> Dict[str, Any]:
        specialist_specs = [
            (
                "strategist",
                "Focus on positioning, message hierarchy, and strategic direction.",
            ),
            (
                "copywriter",
                "Write high-impact copy that is concrete and audience-aligned.",
            ),
            (
                "critic",
                "Find weak claims, ambiguity, and risk. Suggest fixes briefly.",
            ),
        ]

        specialist_tokens = max(220, int(max_tokens * 0.5))
        specialist_tasks = []
        for role, instruction in specialist_specs:
            specialist_prompt = (
                f"Task: {task}\n"
                f"Content type: {content_type}\n"
                f"Target audience: {target_audience}\n"
                f"Tone: {tone}\n\n"
                f"{user_prompt}\n\n"
                f"[Swarm Role: {role}] {instruction}"
            )
            specialist_tasks.append(
                self._generate_single(
                    vertex_ai_service=vertex_ai_service,
                    workspace_id=workspace_id,
                    system_prompt=system_prompt,
                    user_prompt=specialist_prompt,
                    max_tokens=specialist_tokens,
                    temperature=temperature,
                )
            )

        specialist_results = await asyncio.gather(*specialist_tasks, return_exceptions=True)
        successful_specialists: list[tuple[str, Dict[str, Any]]] = []
        for idx, item in enumerate(specialist_results):
            if isinstance(item, Exception):
                logger.warning("Swarm specialist failed: %s", item)
                continue
            if item.get("status") == "success" and (item.get("text") or "").strip():
                successful_specialists.append((specialist_specs[idx][0], item))

        if not successful_specialists:
            raise ServiceError("Swarm generation failed for all specialists")
        if len(successful_specialists) == 1:
            role, only_result = successful_specialists[0]
            return self._merge_ensemble_results(
                final_result=only_result,
                all_results=[only_result],
                mode="swarm_fallback_single",
                contributors=[role],
            )

        swarm_context = "\n\n".join(
            f"[{role.upper()} OUTPUT]\n{result.get('text', '')}"
            for role, result in successful_specialists
        )
        synthesis_prompt = (
            "You are the swarm coordinator. Combine specialist outputs into a coherent final answer. "
            "Preserve strategic logic, keep copy quality high, and apply critic corrections.\n\n"
            f"{swarm_context}"
        )

        synthesis_result = await self._generate_single(
            vertex_ai_service=vertex_ai_service,
            workspace_id=workspace_id,
            system_prompt=system_prompt,
            user_prompt=synthesis_prompt,
            max_tokens=max_tokens,
            temperature=max(0.2, min(temperature, 0.85)),
        )
        if synthesis_result.get("status") != "success":
            role, best_result = successful_specialists[0]
            return self._merge_ensemble_results(
                final_result=best_result,
                all_results=[result for _, result in successful_specialists],
                mode="swarm_fallback_merge",
                contributors=[role_name for role_name, _ in successful_specialists],
            )

        return self._merge_ensemble_results(
            final_result=synthesis_result,
            all_results=[result for _, result in successful_specialists] + [synthesis_result],
            mode="swarm",
            contributors=[role for role, _ in successful_specialists] + ["coordinator"],
        )

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
                "intensity": state.get("intensity", "medium"),
                "execution_mode": state.get("execution_mode", "single"),
                "ensemble": result.get("ensemble", {}),
                "memory_limit": int((state.get("profile") or {}).get("memory_limit", 0)),
                "effective_max_tokens": state.get("effective_max_tokens", 0),
                "effective_temperature": state.get("effective_temperature", 0.0),
                "orchestrator": "langgraph",
                "backend": result.get("backend", "vertex_ai"),
                "fallback_reason": result.get("fallback_reason", ""),
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
        intensity: Optional[Literal["low", "medium", "high"]] = None,
        execution_mode: Optional[Literal["single", "council", "swarm"]] = None,
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
                "intensity": intensity,
                "execution_mode": execution_mode,
            }
        )
        return final_state["response"]


langgraph_muse_orchestrator = LangGraphMuseOrchestrator()
