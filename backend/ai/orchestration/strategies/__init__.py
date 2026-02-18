"""
Orchestration Strategies - Multi-agent generation patterns.

Implements three execution modes:
- Single: One model, one generation
- Council: Multiple specialized roles debate and synthesize
- Swarm: Parallel specialists coordinated by a synthesizer
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

from backend.ai.types import ExecutionMode, GenerationRequest, GenerationResult
from backend.ai.backends.base import BaseAIBackend

logger = logging.getLogger(__name__)


class OrchestrationStrategy(ABC):
    """Base class for orchestration strategies."""

    @property
    @abstractmethod
    def mode(self) -> ExecutionMode:
        pass

    @abstractmethod
    async def execute(
        self,
        backend: BaseAIBackend,
        request: GenerationRequest,
        ensemble_size: int,
    ) -> GenerationResult:
        pass

    def _merge_results(
        self,
        final_result: GenerationResult,
        all_results: List[GenerationResult],
        mode: str,
        contributors: List[str],
    ) -> GenerationResult:
        """Merge multiple results into one with aggregate metrics."""
        total_input = sum(r.input_tokens for r in all_results)
        total_output = sum(r.output_tokens for r in all_results)
        total_cost = sum(r.cost_usd for r in all_results)
        total_time = sum(r.generation_time_seconds for r in all_results)

        return GenerationResult(
            status="success",
            text=final_result.text,
            input_tokens=total_input,
            output_tokens=total_output,
            total_tokens=total_input + total_output,
            cost_usd=total_cost,
            generation_time_seconds=total_time,
            model=final_result.model,
            model_type=final_result.model_type,
            backend=final_result.backend,
            ensemble={
                "mode": mode,
                "contributors": contributors,
                "count": len(contributors),
            },
            metadata=final_result.metadata,
        )


class SingleStrategy(OrchestrationStrategy):
    """Simple single-model generation."""

    @property
    def mode(self) -> ExecutionMode:
        return ExecutionMode.SINGLE

    async def execute(
        self,
        backend: BaseAIBackend,
        request: GenerationRequest,
        ensemble_size: int,
    ) -> GenerationResult:
        return await backend.generate_async(request)


class CouncilStrategy(OrchestrationStrategy):
    """
    Council-based generation with debate and synthesis.

    Process:
    1. Analyst generates strategic draft
    2. Creative generates original draft
    3. Editor synthesizes both into final output
    """

    ROLES: List[Tuple[str, str]] = [
        ("analyst", "Focus on strategic clarity and directness. Keep claims concrete."),
        ("creative", "Push originality while remaining brand-safe and actionable."),
    ]

    @property
    def mode(self) -> ExecutionMode:
        return ExecutionMode.COUNCIL

    async def execute(
        self,
        backend: BaseAIBackend,
        request: GenerationRequest,
        ensemble_size: int,
    ) -> GenerationResult:
        draft_tokens = max(256, int(request.max_tokens * 0.65))
        temperature = request.temperature

        tasks = []
        role_names = []
        for role, instruction in self.ROLES[:ensemble_size]:
            role_prompt = f"{request.prompt}\n\n[Council Role: {role}] {instruction}"
            role_request = GenerationRequest(
                prompt=role_prompt,
                workspace_id=request.workspace_id,
                user_id=request.user_id,
                max_tokens=draft_tokens,
                temperature=max(0.1, temperature - 0.12)
                if role == "analyst"
                else min(0.95, temperature + 0.08),
                system_prompt=request.system_prompt,
            )
            tasks.append(backend.generate_async(role_request))
            role_names.append(role)

        draft_results = await asyncio.gather(*tasks, return_exceptions=True)

        successful: List[Tuple[str, GenerationResult]] = []
        for idx, result in enumerate(draft_results):
            if isinstance(result, Exception):
                logger.warning("Council draft failed: %s", result)
                continue
            if result.success and result.text.strip():
                successful.append((role_names[idx], result))

        if not successful:
            return GenerationResult(
                status="error",
                error="Council generation failed for all draft agents",
            )

        if len(successful) == 1:
            return self._merge_results(
                successful[0][1],
                [r for _, r in successful],
                "council_fallback_single",
                [successful[0][0]],
            )

        synthesis_input = "\n\n".join(
            f"[{role.upper()} DRAFT]\n{result.text}" for role, result in successful
        )

        synthesis_prompt = (
            f"Task: {request.metadata.get('task', 'Generate content')}\n"
            f"Target audience: {request.metadata.get('target_audience', 'general')}\n"
            f"Tone: {request.metadata.get('tone', 'professional')}\n\n"
            "You are the council editor. Merge the drafts below into one final response. "
            "Keep what is strongest, remove redundancy, and improve factual clarity.\n\n"
            f"{synthesis_input}"
        )

        synthesis_request = GenerationRequest(
            prompt=synthesis_prompt,
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            max_tokens=request.max_tokens,
            temperature=max(0.2, min(temperature, 0.85)),
            system_prompt=request.system_prompt,
        )

        synthesis_result = await backend.generate_async(synthesis_request)

        if not synthesis_result.success:
            return self._merge_results(
                successful[0][1],
                [r for _, r in successful],
                "council_fallback_merge",
                [role for role, _ in successful],
            )

        return self._merge_results(
            synthesis_result,
            [r for _, r in successful] + [synthesis_result],
            "council",
            [role for role, _ in successful] + ["editor"],
        )


class SwarmStrategy(OrchestrationStrategy):
    """
    Swarm-based generation with parallel specialists.

    Process:
    1. Strategist focuses on positioning and message hierarchy
    2. Copywriter writes high-impact copy
    3. Critic identifies weak claims and risks
    4. Coordinator synthesizes all outputs
    """

    SPECIALISTS: List[Tuple[str, str]] = [
        (
            "strategist",
            "Focus on positioning, message hierarchy, and strategic direction.",
        ),
        ("copywriter", "Write high-impact copy that is concrete and audience-aligned."),
        ("critic", "Find weak claims, ambiguity, and risk. Suggest fixes briefly."),
    ]

    @property
    def mode(self) -> ExecutionMode:
        return ExecutionMode.SWARM

    async def execute(
        self,
        backend: BaseAIBackend,
        request: GenerationRequest,
        ensemble_size: int,
    ) -> GenerationResult:
        specialist_tokens = max(220, int(request.max_tokens * 0.5))

        tasks = []
        role_names = []
        for role, instruction in self.SPECIALISTS[:ensemble_size]:
            role_prompt = (
                f"Task: {request.metadata.get('task', request.prompt)}\n"
                f"Content type: {request.metadata.get('content_type', 'general')}\n"
                f"Target audience: {request.metadata.get('target_audience', 'general')}\n"
                f"Tone: {request.metadata.get('tone', 'professional')}\n\n"
                f"{request.prompt}\n\n"
                f"[Swarm Role: {role}] {instruction}"
            )
            role_request = GenerationRequest(
                prompt=role_prompt,
                workspace_id=request.workspace_id,
                user_id=request.user_id,
                max_tokens=specialist_tokens,
                temperature=request.temperature,
                system_prompt=request.system_prompt,
            )
            tasks.append(backend.generate_async(role_request))
            role_names.append(role)

        specialist_results = await asyncio.gather(*tasks, return_exceptions=True)

        successful: List[Tuple[str, GenerationResult]] = []
        for idx, result in enumerate(specialist_results):
            if isinstance(result, Exception):
                logger.warning("Swarm specialist failed: %s", result)
                continue
            if result.success and result.text.strip():
                successful.append((role_names[idx], result))

        if not successful:
            return GenerationResult(
                status="error",
                error="Swarm generation failed for all specialists",
            )

        if len(successful) == 1:
            return self._merge_results(
                successful[0][1],
                [r for _, r in successful],
                "swarm_fallback_single",
                [successful[0][0]],
            )

        swarm_context = "\n\n".join(
            f"[{role.upper()} OUTPUT]\n{result.text}" for role, result in successful
        )

        synthesis_prompt = (
            "You are the swarm coordinator. Combine specialist outputs into a coherent final answer. "
            "Preserve strategic logic, keep copy quality high, and apply critic corrections.\n\n"
            f"{swarm_context}"
        )

        synthesis_request = GenerationRequest(
            prompt=synthesis_prompt,
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            max_tokens=request.max_tokens,
            temperature=max(0.2, min(request.temperature, 0.85)),
            system_prompt=request.system_prompt,
        )

        synthesis_result = await backend.generate_async(synthesis_request)

        if not synthesis_result.success:
            return self._merge_results(
                successful[0][1],
                [r for _, r in successful],
                "swarm_fallback_merge",
                [role for role, _ in successful],
            )

        return self._merge_results(
            synthesis_result,
            [r for _, r in successful] + [synthesis_result],
            "swarm",
            [role for role, _ in successful] + ["coordinator"],
        )


STRATEGY_MAP: Dict[ExecutionMode, OrchestrationStrategy] = {
    ExecutionMode.SINGLE: SingleStrategy(),
    ExecutionMode.COUNCIL: CouncilStrategy(),
    ExecutionMode.SWARM: SwarmStrategy(),
}


def get_strategy(mode: ExecutionMode) -> OrchestrationStrategy:
    """Get the orchestration strategy for a given mode."""
    return STRATEGY_MAP.get(mode, STRATEGY_MAP[ExecutionMode.SINGLE])


__all__ = [
    "OrchestrationStrategy",
    "SingleStrategy",
    "CouncilStrategy",
    "SwarmStrategy",
    "get_strategy",
    "STRATEGY_MAP",
]
