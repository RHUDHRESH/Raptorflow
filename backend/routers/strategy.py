"""
Strategy Router - API endpoints for strategy generation and management.
Implements ADAPT framework endpoints.
"""

import structlog
from typing import Annotated
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.main import get_current_user_and_workspace
from backend.graphs.strategy_graph import strategy_graph_runnable, StrategyGraphState
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id, generate_correlation_id

router = APIRouter()
logger = structlog.get_logger(__name__)


# --- Request/Response Models ---
class StrategyGenerateRequest(BaseModel):
    """Request to generate a new strategy."""
    goal: str
    timeframe_days: int = 90
    target_cohort_ids: list[UUID] = []
    constraints: dict = {}


class StrategyResponse(BaseModel):
    """Strategy response."""
    strategy_id: UUID
    workspace_id: UUID
    goal: str
    status: str
    adapt_stage: str
    insights: dict = {}
    campaign_ideas: list = []
    created_at: str
    updated_at: str


@router.post("/generate", response_model=StrategyResponse, summary="Generate Marketing Strategy", tags=["Strategy"])
async def generate_strategy(
    request: StrategyGenerateRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Generates a comprehensive marketing strategy using the ADAPT framework.
    """
    user_id = auth["user_id"]
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Generating strategy", workspace_id=workspace_id, goal=request.goal, correlation_id=correlation_id)
    
    try:
        # Invoke strategy graph
        initial_state = StrategyGraphState(
            user_id=user_id,
            workspace_id=workspace_id,
            correlation_id=correlation_id,
            goal=request.goal,
            timeframe_days=request.timeframe_days,
            target_cohort_ids=request.target_cohort_ids,
            constraints=request.constraints,
            adapt_stage="analyze",
            next_step="analyze"
        )
        
        final_state = await strategy_graph_runnable.ainvoke(initial_state)
        
        # Extract strategy from state
        strategy_data = {
            "workspace_id": str(workspace_id),
            "goal": request.goal,
            "status": "active",
            "adapt_stage": final_state.get("adapt_stage", "analyze"),
            "insights": final_state.get("insights", {}),
            "campaign_ideas": final_state.get("campaign_ideas", []),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Store in database
        strategy_record = await supabase_client.insert("global_strategies", strategy_data)

        logger.info("Strategy generated", strategy_id=strategy_record["id"], correlation_id=correlation_id)

        return {
            **StrategyResponse(**strategy_record).dict(),
            "correlation_id": correlation_id
        }

    except Exception as e:
        logger.error(f"Failed to generate strategy: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{strategy_id}", response_model=dict, summary="Get Strategy", tags=["Strategy"])
async def get_strategy(
    strategy_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Retrieves a specific strategy."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()

    strategy = await supabase_client.fetch_one(
        "global_strategies",
        {"id": str(strategy_id), "workspace_id": str(workspace_id)}
    )

    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )

    return {
        **StrategyResponse(**strategy).dict(),
        "correlation_id": correlation_id
    }


@router.get("/", response_model=dict, summary="List Strategies", tags=["Strategy"])
async def list_strategies(auth: Annotated[dict, Depends(get_current_user_and_workspace)]):
    """Lists all strategies for the workspace."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()

    strategies = await supabase_client.fetch_all(
        "global_strategies",
        {"workspace_id": str(workspace_id)}
    )

    return {
        "strategies": [StrategyResponse(**s).dict() for s in strategies],
        "total": len(strategies),
        "correlation_id": correlation_id
    }

