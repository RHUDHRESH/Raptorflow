"""
Generate Content Use Case Implementation.

This module implements the GenerateContentUseCase inbound port,
orchestrating the content generation workflow.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from raptorflow.domain.ai.models import (
    GenerationRequest,
    GenerationResult,
    GenerationConfig,
    TokenBudget,
    ExecutionStrategy,
    ModelTier,
)
from raptorflow.domain.ai.repositories import (
    ModelRepository,
    ExecutionPlannerPort,
)
from raptorflow.application.ports.inbound.ai import (
    GenerateContentCommand,
    GenerateContentResult,
)
from raptorflow.application.ports.outbound.repositories import (
    CachePort,
    MetricsPort,
    EventPublisher,
)


@dataclass
class OrchestrationConfig:
    """Configuration for AI orchestration."""

    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    enable_cost_tracking: bool = True
    max_parallel_executions: int = 3
    fallback_enabled: bool = True
    default_model: str = "gemini-2.0-flash"


class GenerateContentUseCaseImpl:
    """
    Implementation of content generation use case.

    This use case handles:
    - Request validation
    - Caching (if enabled)
    - Execution planning
    - AI generation
    - Metrics recording
    - Event publishing
    - Error handling with fallbacks
    """

    def __init__(
        self,
        model_repo: ModelRepository,
        planner: ExecutionPlannerPort,
        cache: Optional[CachePort] = None,
        metrics: Optional[MetricsPort] = None,
        event_publisher: Optional[EventPublisher] = None,
        config: Optional[OrchestrationConfig] = None,
    ):
        self._model_repo = model_repo
        self._planner = planner
        self._cache = cache
        self._metrics = metrics
        self._event_publisher = event_publisher
        self._config = config or OrchestrationConfig()

    async def execute(self, command: GenerateContentCommand) -> GenerateContentResult:
        """
        Execute content generation use case.

        Args:
            command: The generation command

        Returns:
            GenerateContentResult with generated content or error
        """
        start_time = time.perf_counter()

        try:
            # Validate command
            self._validate_command(command)

            # Get model capability
            model_name = command.model or self._config.default_model
            model = await self._model_repo.get_model(model_name)
            if not model:
                return GenerateContentResult(
                    success=False,
                    error_message=f"Model {model_name} not found",
                )

            # Create generation request
            request = GenerationRequest(
                workspace_id=command.workspace_id,
                user_id=command.user_id,
                prompt=command.prompt,
                config=GenerationConfig(
                    temperature=command.temperature,
                ),
                budget=TokenBudget(
                    max_input=4000,
                    max_output=command.max_tokens,
                ),
                context={
                    "content_type": command.content_type,
                    "tone": command.tone,
                },
            )

            # Check cache if enabled
            if self._config.enable_caching and self._cache:
                cached = await self._get_cached(request)
                if cached:
                    await self._record_cache_hit(cached)
                    return GenerateContentResult(
                        success=True,
                        content=cached.text,
                        request_id=request.id,
                        tokens_used=cached.total_tokens,
                        cost_usd=cached.cost_usd,
                        latency_ms=int((time.perf_counter() - start_time) * 1000),
                    )

            # Create execution plan
            plan = await self._planner.plan(request)

            # Execute generation
            # Note: This would call the AI provider adapter in real implementation
            # For now, we return a placeholder result
            result = GenerationResult(
                request_id=request.id,
                text=f"Generated content for: {command.prompt[:50]}...",
                input_tokens=100,
                output_tokens=50,
                model=model_name,
                provider=model.provider,
                cost_usd=0.001,
                latency_ms=500,
                finish_reason="stop",
            )

            # Cache result if enabled
            if self._config.enable_caching and self._cache and result.success:
                await self._cache_result(request, result)

            # Record metrics
            await self._record_generation_metrics(result)

            # Publish event
            await self._publish_generation_event(command, result)

            return GenerateContentResult(
                success=result.success,
                content=result.text,
                request_id=request.id,
                tokens_used=result.total_tokens,
                cost_usd=result.cost_usd,
                latency_ms=int((time.perf_counter() - start_time) * 1000),
            )

        except Exception as e:
            await self._record_error_metrics(str(e))
            return GenerateContentResult(
                success=False,
                error_message=str(e),
                latency_ms=int((time.perf_counter() - start_time) * 1000),
            )

    def _validate_command(self, command: GenerateContentCommand) -> None:
        """Validate the generation command."""
        if not command.workspace_id:
            raise ValueError("workspace_id is required")
        if not command.user_id:
            raise ValueError("user_id is required")
        if not command.prompt:
            raise ValueError("prompt is required")
        if command.temperature < 0 or command.temperature > 2:
            raise ValueError("temperature must be between 0 and 2")

    async def _get_cached(
        self,
        request: GenerationRequest,
    ) -> Optional[GenerationResult]:
        """Get cached result if available."""
        if not self._cache:
            return None

        cache_key = f"generation:{request.cache_key}"
        cached = await self._cache.get(cache_key)
        if cached:
            # Deserialize cached result (simplified)
            return None  # Would deserialize in real implementation
        return None

    async def _cache_result(
        self,
        request: GenerationRequest,
        result: GenerationResult,
    ) -> None:
        """Cache generation result."""
        if not self._cache:
            return

        cache_key = f"generation:{request.cache_key}"
        # Serialize and cache (simplified)
        await self._cache.set(
            cache_key,
            str(result.text),  # Would serialize full result
            self._config.cache_ttl_seconds,
        )

    async def _record_cache_hit(self, result: GenerationResult) -> None:
        """Record cache hit metrics."""
        if self._metrics:
            await self._metrics.increment(
                "generation.cache.hit",
                tags={"model": result.model},
            )

    async def _record_generation_metrics(
        self,
        result: GenerationResult,
    ) -> None:
        """Record generation metrics."""
        if self._metrics:
            await self._metrics.increment(
                "generation.count",
                tags={
                    "model": result.model,
                    "provider": result.provider,
                    "status": "success" if result.success else "error",
                },
            )
            await self._metrics.histogram(
                "generation.tokens",
                result.total_tokens,
                tags={"model": result.model},
            )
            await self._metrics.histogram(
                "generation.latency_ms",
                result.latency_ms,
                tags={"model": result.model},
            )
            if result.cost_usd > 0:
                await self._metrics.histogram(
                    "generation.cost_usd",
                    result.cost_usd,
                    tags={"model": result.model},
                )

    async def _record_error_metrics(self, error: str) -> None:
        """Record error metrics."""
        if self._metrics:
            await self._metrics.increment(
                "generation.error",
                tags={"error_type": error},
            )

    async def _publish_generation_event(
        self,
        command: GenerateContentCommand,
        result: GenerationResult,
    ) -> None:
        """Publish generation event."""
        if self._event_publisher:
            await self._event_publisher.publish(
                "content.generated",
                {
                    "workspace_id": command.workspace_id,
                    "user_id": command.user_id,
                    "request_id": str(result.request_id),
                    "tokens_used": result.total_tokens,
                    "cost_usd": result.cost_usd,
                    "success": result.success,
                },
            )


class GetGenerationHistoryUseCaseImpl:
    """Implementation of get generation history use case."""

    def __init__(
        self,
        generation_repo: "GenerationRepository",
    ):
        self._generation_repo = generation_repo

    async def execute(
        self,
        workspace_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Execute get generation history."""
        results = await self._generation_repo.get_by_workspace(
            workspace_id=workspace_id,
            limit=limit,
            offset=offset,
        )

        return [
            {
                "id": str(r.request_id),
                "text": r.text,
                "tokens": r.total_tokens,
                "cost_usd": r.cost_usd,
                "model": r.model,
                "created_at": r.created_at.isoformat(),
            }
            for r in results
        ]


class GetAvailableModelsUseCaseImpl:
    """Implementation of get available models use case."""

    def __init__(
        self,
        model_repo: ModelRepository,
    ):
        self._model_repo = model_repo

    async def execute(
        self,
        tier: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Execute get available models."""
        if tier:
            models = await self._model_repo.get_by_tier(ModelTier[tier.upper()])
        elif provider:
            models = await self._model_repo.get_by_provider(provider)
        else:
            models = await self._model_repo.get_available_models()

        return [
            {
                "name": m.name,
                "tier": m.tier.name,
                "provider": m.provider,
                "max_tokens": m.max_tokens,
                "supports_functions": m.supports_functions,
                "supports_vision": m.supports_vision,
                "description": m.description,
            }
            for m in models
        ]
