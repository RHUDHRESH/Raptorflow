"""
FastAPI Routes - AI Endpoints.

This module provides FastAPI routes for AI generation endpoints,
integrating with the application use cases.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid

from raptorflow.application.ports.inbound.ai import (
    GenerateContentCommand,
    GenerateContentResult,
)
from raptorflow.application.use_cases.generate_content import (
    GenerateContentUseCaseImpl,
    GetAvailableModelsUseCaseImpl,
)
from raptorflow.domain.ai.models import ExecutionStrategy


# Request/Response Models
class GenerateContentRequest(BaseModel):
    """Request model for content generation."""

    workspace_id: str = Field(..., description="Workspace ID")
    user_id: str = Field(..., description="User ID")
    prompt: str = Field(..., min_length=1, description="Generation prompt")
    content_type: str = Field(default="general", description="Content type")
    tone: str = Field(default="professional", description="Tone")
    model: Optional[str] = Field(default=None, description="Model name")
    temperature: float = Field(default=0.7, ge=0, le=2, description="Temperature")
    max_tokens: int = Field(default=1000, ge=1, le=32000, description="Max tokens")
    strategy: str = Field(default="single", description="Execution strategy")


class GenerateContentResponse(BaseModel):
    """Response model for content generation."""

    success: bool
    content: str = ""
    request_id: Optional[str] = None
    tokens_used: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    error_message: str = ""


class ModelInfo(BaseModel):
    """Model information."""

    name: str
    tier: str
    provider: str
    max_tokens: int
    supports_functions: bool
    supports_vision: bool
    description: str


class GetModelsRequest(BaseModel):
    """Request model for getting models."""

    tier: Optional[str] = None
    provider: Optional[str] = None


# Router
router = APIRouter(prefix="/ai", tags=["AI"])


# Dependency injection helpers
# These would be provided by the DI container in production
_generate_content_use_case: Optional[GenerateContentUseCaseImpl] = None
_get_models_use_case: Optional[GetAvailableModelsUseCaseImpl] = None


def get_generate_content_use_case() -> GenerateContentUseCaseImpl:
    """Get generate content use case (from DI container)."""
    if _generate_content_use_case is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not initialized",
        )
    return _generate_content_use_case


def get_models_use_case() -> GetAvailableModelsUseCaseImpl:
    """Get models use case (from DI container)."""
    if _get_models_use_case is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not initialized",
        )
    return _get_models_use_case


def set_generate_content_use_case(use_case: GenerateContentUseCaseImpl):
    """Set generate content use case (for testing/initialization)."""
    global _generate_content_use_case
    _generate_content_use_case = use_case


def set_models_use_case(use_case: GetAvailableModelsUseCaseImpl):
    """Set models use case (for testing/initialization)."""
    global _get_models_use_case
    _get_models_use_case = use_case


# Routes
@router.post(
    "/generate",
    response_model=GenerateContentResponse,
    summary="Generate content",
    description="Generate content using AI with the specified parameters",
)
async def generate_content(
    request: GenerateContentRequest,
    use_case: GenerateContentUseCaseImpl = Depends(get_generate_content_use_case),
) -> GenerateContentResponse:
    """
    Generate content using AI.

    Supports various execution strategies:
    - single: Single model execution (default)
    - ensemble: Multiple models vote on result
    - pipeline: Sequential model pipeline
    - council: Multiple models debate
    - swarm: Multiple agents collaborate
    """
    # Map strategy string to enum
    strategy_map = {
        "single": ExecutionStrategy.SINGLE,
        "ensemble": ExecutionStrategy.ENSEMBLE,
        "pipeline": ExecutionStrategy.PIPELINE,
        "council": ExecutionStrategy.COUNCIL,
        "swarm": ExecutionStrategy.SWARM,
    }

    strategy = strategy_map.get(request.strategy.lower(), ExecutionStrategy.SINGLE)

    # Create command
    command = GenerateContentCommand(
        workspace_id=request.workspace_id,
        user_id=request.user_id,
        prompt=request.prompt,
        content_type=request.content_type,
        tone=request.tone,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )

    # Execute use case
    result: GenerateContentResult = await use_case.execute(command)

    # Map to response
    return GenerateContentResponse(
        success=result.success,
        content=result.content,
        request_id=str(result.request_id) if result.request_id else None,
        tokens_used=result.tokens_used,
        cost_usd=result.cost_usd,
        latency_ms=result.latency_ms,
        error_message=result.error_message,
    )


@router.post(
    "/generate/stream",
    summary="Stream generate content",
    description="Generate content with streaming response",
)
async def stream_generate_content(
    request: GenerateContentRequest,
) -> StreamingResponse:
    """
    Stream generate content.

    Note: Streaming is only supported for single strategy.
    """
    # This would use the orchestrator's stream method
    # For now, return an error response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Streaming not yet implemented",
    )


@router.get(
    "/models",
    response_model=List[ModelInfo],
    summary="Get available models",
    description="Get list of available AI models",
)
async def get_models(
    tier: Optional[str] = None,
    provider: Optional[str] = None,
    use_case: GetAvailableModelsUseCaseImpl = Depends(get_models_use_case),
) -> List[ModelInfo]:
    """
    Get available AI models.

    Can filter by:
    - tier: FAST, BALANCED, PREMIUM
    - provider: google, openai, etc.
    """
    models = await use_case.execute(tier=tier, provider=provider)
    return [ModelInfo(**m) for m in models]


@router.get(
    "/models/{model_name}",
    response_model=ModelInfo,
    summary="Get model info",
    description="Get information about a specific model",
)
async def get_model(
    model_name: str,
    use_case: GetAvailableModelsUseCaseImpl = Depends(get_models_use_case),
) -> ModelInfo:
    """Get information about a specific model."""
    models = await use_case.execute()

    for model in models:
        if model["name"] == model_name:
            return ModelInfo(**model)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Model {model_name} not found",
    )


# Health check
@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai"}
