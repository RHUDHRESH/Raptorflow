"""
AI Domain - Services.

Domain services that encapsulate business logic for the AI system.
These services operate on domain entities and use repository ports.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from .models import (
    GenerationRequest,
    GenerationResult,
    ExecutionStrategy,
    ModelTier,
    ModelCapability,
    ExecutionPlan,
)
from .repositories import (
    ModelRepository,
    ExecutionPlannerPort,
)


class AIServiceError(Exception):
    """Base exception for AI service errors."""

    pass


class ModelNotFoundError(AIServiceError):
    """Raised when requested model is not available."""

    pass


class ExecutionError(AIServiceError):
    """Raised when generation execution fails."""

    pass


@dataclass
class GenerationContext:
    """Context for generation requests."""

    workspace_id: str
    user_id: str
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class AIService:
    """
    Core AI generation service.

    This domain service orchestrates AI generation requests,
    handling caching, retries, and fallback logic.
    """

    def __init__(
        self,
        model_repository: ModelRepository,
        planner: ExecutionPlannerPort,
    ):
        self._model_repo = model_repository
        self._planner = planner

    async def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        """
        Execute generation request.

        Args:
            request: The generation request

        Returns:
            GenerationResult with the generated content

        Raises:
            ModelNotFoundError: If requested model not available
            ExecutionError: If generation fails
        """
        # Validate request
        self._validate_request(request)

        # Create execution plan
        plan = await self._planner.plan(request)

        # Execute based on strategy
        if request.strategy == ExecutionStrategy.SINGLE:
            return await self._execute_single(request, plan)
        elif request.strategy == ExecutionStrategy.ENSEMBLE:
            return await self._execute_ensemble(request, plan)
        elif request.strategy == ExecutionStrategy.PIPELINE:
            return await self._execute_pipeline(request, plan)
        elif request.strategy == ExecutionStrategy.COUNCIL:
            return await self._execute_council(request, plan)
        elif request.strategy == ExecutionStrategy.SWARM:
            return await self._execute_swarm(request, plan)
        else:
            raise ExecutionError(f"Unknown strategy: {request.strategy}")

    def _validate_request(self, request: GenerationRequest) -> None:
        """Validate generation request."""
        if not request.workspace_id:
            raise ExecutionError("workspace_id is required")
        if not request.prompt:
            raise ExecutionError("prompt is required")
        if request.budget.max_input < 100:
            raise ExecutionError("max_input must be at least 100")
        if request.budget.max_output < 1:
            raise ExecutionError("max_output must be at least 1")

    async def _execute_single(
        self,
        request: GenerationRequest,
        plan: ExecutionPlan,
    ) -> GenerationResult:
        """Execute single model generation."""
        # This will be implemented by the infrastructure adapter
        # Placeholder for now
        raise NotImplementedError("Use AIProviderAdapter for execution")

    async def _execute_ensemble(
        self,
        request: GenerationRequest,
        plan: ExecutionPlan,
    ) -> GenerationResult:
        """Execute ensemble generation with voting."""
        raise NotImplementedError("Ensemble execution not yet implemented")

    async def _execute_pipeline(
        self,
        request: GenerationRequest,
        plan: ExecutionPlan,
    ) -> GenerationResult:
        """Execute pipeline generation."""
        raise NotImplementedError("Pipeline execution not yet implemented")

    async def _execute_council(
        self,
        request: GenerationRequest,
        plan: ExecutionPlan,
    ) -> GenerationResult:
        """Execute council generation with debate."""
        raise NotImplementedError("Council execution not yet implemented")

    async def _execute_swarm(
        self,
        request: GenerationRequest,
        plan: ExecutionPlan,
    ) -> GenerationResult:
        """Execute swarm generation with agents."""
        raise NotImplementedError("Swarm execution not yet implemented")

    async def get_available_models(self) -> list[ModelCapability]:
        """Get all available models."""
        return await self._model_repo.get_available_models()

    async def get_model(self, name: str) -> Optional[ModelCapability]:
        """Get model by name."""
        return await self._model_repo.get_model(name)


class TokenBudgetService:
    """Service for managing token budgets and cost estimation."""

    def __init__(self, model_repository: ModelRepository):
        self._model_repo = model_repository

    async def estimate_cost(
        self,
        model_name: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Estimate cost for generation."""
        model = await self._model_repo.get_model(model_name)
        if not model:
            return 0.0

        input_cost = (input_tokens / 1000) * model.cost_per_1k_input
        output_cost = (output_tokens / 1000) * model.cost_per_1k_output
        return input_cost + output_cost

    def calculate_efficiency(
        self,
        input_tokens: int,
        output_tokens: int,
        budget: "TokenBudget",
    ) -> Dict[str, Any]:
        """Calculate token usage efficiency."""
        total_used = input_tokens + output_tokens
        budget_total = budget.max_input + budget.max_output

        return {
            "input_utilization": input_tokens / budget.max_input,
            "output_utilization": output_tokens / budget.max_output,
            "total_utilization": total_used / budget_total,
            "remaining_tokens": budget_total - total_used,
            "is_within_budget": total_used <= budget_total,
        }


class ModelRouter:
    """Service for routing requests to appropriate models."""

    def __init__(self, model_repository: ModelRepository):
        self._model_repo = model_repository

    async def select_model(
        self,
        strategy: ExecutionStrategy,
        tier: Optional[ModelTier] = None,
        preferred_provider: Optional[str] = None,
    ) -> ModelCapability:
        """Select appropriate model based on criteria."""
        if tier:
            models = await self._model_repo.get_by_tier(tier)
        elif preferred_provider:
            models = await self._model_repo.get_by_provider(preferred_provider)
        else:
            models = await self._model_repo.get_available_models()

        if not models:
            raise ModelNotFoundError("No models available")

        # Select first matching model
        return models[0]

    async def get_fallback_models(
        self,
        original_model: str,
    ) -> list[ModelCapability]:
        """Get fallback models in case of failure."""
        # Get all models and filter out the original
        all_models = await self._model_repo.get_available_models()
        return [m for m in all_models if m.name != original_model]
