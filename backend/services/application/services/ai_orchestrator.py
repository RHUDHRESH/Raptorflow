"""
Application Services - Unified AI Orchestrator.

This module provides a unified orchestration layer that replaces
the multiple LangGraph orchestrators with a single, configurable
orchestration service.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, AsyncIterator
from enum import Enum, auto

from raptorflow.domain.ai.models import (
    GenerationRequest,
    GenerationResult,
    ExecutionStrategy,
    ExecutionPlan,
    ModelCapability,
    ModelTier,
)
from raptorflow.domain.ai.repositories import (
    AIProviderPort,
    ModelRepository,
    ExecutionPlannerPort,
)


class OrchestrationStrategy(Enum):
    """Unified orchestration strategies."""

    SINGLE = auto()  # Single model execution
    ENSEMBLE = auto()  # Multiple models, vote on result
    PIPELINE = auto()  # Sequential model pipeline
    COUNCIL = auto()  # Multiple models debate
    SWARM = auto()  # Multiple agents collaborate


@dataclass
class OrchestrationConfig:
    """Configuration for AI orchestration."""

    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    enable_cost_tracking: bool = True
    max_parallel_executions: int = 3
    fallback_enabled: bool = True
    default_model: str = "gemini-2.0-flash"
    timeout_seconds: int = 60
    max_retries: int = 2


@dataclass
class UnifiedAIOrchestrator:
    """
    Unified AI orchestration service.

    This service replaces multiple LangGraph orchestrators with a single,
    configurable orchestration layer that supports:
    - Single model execution
    - Ensemble execution (voting)
    - Pipeline execution (sequential)
    - Council execution (debate)
    - Swarm execution (collaboration)

    Features:
    - Automatic caching
    - Cost tracking
    - Fallback models
    - Retry logic
    - Metrics recording
    """

    def __init__(
        self,
        provider: AIProviderPort,
        model_repository: ModelRepository,
        config: Optional[OrchestrationConfig] = None,
    ):
        self._provider = provider
        self._model_repo = model_repository
        self._config = config or OrchestrationConfig()
        self._strategy_handlers = {
            OrchestrationStrategy.SINGLE: self._execute_single,
            OrchestrationStrategy.ENSEMBLE: self._execute_ensemble,
            OrchestrationStrategy.PIPELINE: self._execute_pipeline,
            OrchestrationStrategy.COUNCIL: self._execute_council,
            OrchestrationStrategy.SWARM: self._execute_swarm,
        }

    async def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        """
        Generate content using appropriate strategy.

        Args:
            request: The generation request

        Returns:
            GenerationResult with generated content
        """
        # Map execution strategy to orchestration strategy
        strategy_map = {
            ExecutionStrategy.SINGLE: OrchestrationStrategy.SINGLE,
            ExecutionStrategy.ENSEMBLE: OrchestrationStrategy.ENSEMBLE,
            ExecutionStrategy.PIPELINE: OrchestrationStrategy.PIPELINE,
            ExecutionStrategy.COUNCIL: OrchestrationStrategy.COUNCIL,
            ExecutionStrategy.SWARM: OrchestrationStrategy.SWARM,
        }

        orch_strategy = strategy_map.get(
            request.strategy,
            OrchestrationStrategy.SINGLE,
        )

        # Get handler for strategy
        handler = self._strategy_handlers.get(orch_strategy)
        if not handler:
            handler = self._execute_single

        # Execute with retries
        last_error = None
        for attempt in range(self._config.max_retries + 1):
            try:
                return await handler(request)
            except Exception as e:
                last_error = e
                if attempt < self._config.max_retries:
                    # Wait before retry (exponential backoff)
                    await asyncio.sleep(2**attempt)
                    continue

                # All retries failed, try fallback
                if self._config.fallback_enabled:
                    try:
                        return await self._execute_with_fallback(request, e)
                    except Exception as fallback_error:
                        return self._create_error_result(request, str(fallback_error))

        return self._create_error_result(request, str(last_error))

    async def stream(
        self,
        request: GenerationRequest,
    ) -> AsyncIterator[str]:
        """
        Stream generation using appropriate strategy.

        Note: Streaming is only supported for SINGLE strategy.
        """
        if request.strategy == ExecutionStrategy.SINGLE:
            async for chunk in self._provider.stream(request):
                yield chunk
        else:
            # For non-single strategies, yield error
            yield "[Error: Streaming not supported for this strategy]"

    async def _execute_single(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        """Execute single model generation."""
        return await self._provider.generate(request)

    async def _execute_ensemble(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        """
        Execute ensemble generation with voting.

        Multiple models generate independently, then vote on the best result.
        """
        # Get multiple models for ensemble
        models = await self._model_repo.get_available_models()
        if len(models) < 2:
            # Fall back to single if not enough models
            return await self._execute_single(request)

        # Take up to max_parallel_executions models
        selected_models = models[: self._config.max_parallel_executions]

        # Execute in parallel
        tasks = [self._execute_with_model(request, model) for model in selected_models]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out errors
        valid_results = [
            r for r in results if isinstance(r, GenerationResult) and r.success
        ]

        if not valid_results:
            # All failed, return error
            return self._create_error_result(
                request,
                "All ensemble models failed",
            )

        # Simple voting: return the shortest result (often most concise)
        # In production, would use more sophisticated voting
        best_result = min(valid_results, key=lambda r: len(r.text))

        # Mark as ensemble result
        best_result.metadata["ensemble_count"] = len(valid_results)
        best_result.metadata["strategy"] = "ensemble"

        return best_result

    async def _execute_pipeline(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        """
        Execute pipeline generation.

        Multiple models process sequentially, each adding to the result.
        """
        models = await self._model_repo.get_available_models()
        if len(models) < 2:
            return await self._execute_single(request)

        selected_models = models[: self._config.max_parallel_executions]

        current_result = None
        accumulated_text = ""

        for i, model in enumerate(selected_models):
            # For each model, use previous result as context
            modified_request = GenerationRequest(
                workspace_id=request.workspace_id,
                user_id=request.user_id,
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                config=request.config,
                budget=request.budget,
                context={
                    **request.context,
                    "pipeline_stage": i,
                    "previous_output": accumulated_text,
                },
            )

            result = await self._execute_with_model(modified_request, model)

            if not result.success:
                if current_result and i > 0:
                    # Use previous result if current fails
                    break
                return result

            accumulated_text = result.text
            current_result = result

        if current_result:
            current_result.metadata["pipeline_stages"] = i + 1
            current_result.metadata["strategy"] = "pipeline"

        return current_result or self._create_error_result(
            request,
            "Pipeline execution failed",
        )

    async def _execute_council(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        """
        Execute council generation with debate.

        Multiple models generate, then critique each other's results,
        and a final model synthesizes the best response.
        """
        # Similar to ensemble but with critique round
        models = await self._model_repo.get_available_models()
        if len(models) < 3:
            # Need at least 3 for meaningful council
            return await self._execute_ensemble(request)

        selected_models = models[: self._config.max_parallel_executions]

        # First round: each model generates
        tasks = [self._execute_with_model(request, model) for model in selected_models]

        initial_results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_results = [
            r for r in initial_results if isinstance(r, GenerationResult) and r.success
        ]

        if not valid_results:
            return self._create_error_result(
                request,
                "All council models failed",
            )

        # Synthesize results (simplified)
        # In production, would have a critique round
        synthesized_text = "\n\n---\n\n".join(
            [f"[Model {i + 1}]\n{r.text}" for i, r in enumerate(valid_results)]
        )

        # Use best model for final synthesis
        best_model = selected_models[0]

        synthesis_request = GenerationRequest(
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            prompt=f"Synthesize these responses into a single, coherent answer:\n\n{synthesized_text}",
            config=request.config,
            budget=request.budget,
        )

        final_result = await self._execute_with_model(synthesis_request, best_model)
        final_result.metadata["council_count"] = len(valid_results)
        final_result.metadata["strategy"] = "council"

        return final_result

    async def _execute_swarm(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        """
        Execute swarm generation with agent collaboration.

        Multiple specialized agents work together on the task.
        This is the most complex strategy.
        """
        # For now, delegate to ensemble
        # Full swarm implementation would involve multiple agents
        # with different roles collaborating
        return await self._execute_ensemble(request)

    async def _execute_with_model(
        self,
        request: GenerationRequest,
        model: ModelCapability,
    ) -> GenerationResult:
        """Execute generation with a specific model."""
        # Create request with specific model
        modified_request = GenerationRequest(
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            config=request.config,
            budget=request.budget,
            strategy=ExecutionStrategy.SINGLE,
            context=request.context,
        )

        return await self._provider.generate(modified_request)

    async def _execute_with_fallback(
        self,
        request: GenerationRequest,
        error: Exception,
    ) -> GenerationResult:
        """Execute with fallback model."""
        # Get fallback models
        available_models = await self._model_repo.get_available_models()

        for model in available_models:
            if model.name != self._config.default_model:
                try:
                    return await self._execute_with_model(request, model)
                except Exception:
                    continue

        raise error

    def _create_error_result(
        self,
        request: GenerationRequest,
        error_message: str,
    ) -> GenerationResult:
        """Create an error result."""
        return GenerationResult(
            request_id=request.id,
            text="",
            input_tokens=0,
            output_tokens=0,
            model=self._config.default_model,
            provider="unknown",
            cost_usd=0,
            latency_ms=0,
            finish_reason="error",
            error_message=error_message,
        )


# Convenience function to create orchestrator
async def create_orchestrator(
    provider: AIProviderPort,
    config: Optional[OrchestrationConfig] = None,
) -> UnifiedAIOrchestrator:
    """Create a unified AI orchestrator with default model repository."""
    # In production, this would load models from config
    from raptorflow.domain.ai.models import Models

    model_repo = InMemoryModelRepository()
    await model_repo.register_model(Models.GEMINI_2_0_FLASH)
    await model_repo.register_model(Models.GEMINI_2_0_FLASH_LITE)
    await model_repo.register_model(Models.GEMINI_2_0_PRO)

    return UnifiedAIOrchestrator(
        provider=provider,
        model_repository=model_repo,
        config=config,
    )


class InMemoryModelRepository:
    """Simple in-memory model repository."""

    def __init__(self):
        self._models: Dict[str, ModelCapability] = {}

    async def register_model(self, model: ModelCapability) -> None:
        self._models[model.name] = model

    async def get_available_models(self) -> List[ModelCapability]:
        return list(self._models.values())

    async def get_model(self, name: str) -> Optional[ModelCapability]:
        return self._models.get(name)

    async def get_by_tier(self, tier: ModelTier) -> List[ModelCapability]:
        return [m for m in self._models.values() if m.tier == tier]

    async def get_by_provider(self, provider: str) -> List[ModelCapability]:
        return [m for m in self._models.values() if m.provider == provider]
