"""
Analytics Router - API endpoints for metrics collection and insights.
"""

import structlog
from typing import Annotated, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.main import get_current_user_and_workspace
from backend.agents.analytics.analytics_agent import analytics_agent
from backend.agents.analytics.insight_agent import insight_agent
from backend.agents.analytics.campaign_review_agent import campaign_review_agent
from backend.utils.correlation import generate_correlation_id

router = APIRouter()
logger = structlog.get_logger(__name__)


# --- Response Models ---
class MetricsResponse(BaseModel):
    workspace_id: UUID
    move_id: Optional[UUID] = None
    metrics: dict
    collected_at: str


class InsightsResponse(BaseModel):
    insights: list
    anomalies: list
    analyzed_period_days: int
    data_points: int


@router.post("/collect", response_model=MetricsResponse, summary="Collect Metrics", tags=["Analytics"])
async def collect_metrics(
    move_id: Optional[UUID] = None,
    platforms: Optional[list[str]] = None,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """Collects metrics from all connected platforms."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Collecting metrics", workspace_id=workspace_id, correlation_id=correlation_id)
    
    try:
        metrics = await analytics_agent.collect_metrics(
            workspace_id,
            move_id,
            platforms,
            correlation_id
        )
        
        return MetricsResponse(
            workspace_id=workspace_id,
            move_id=move_id,
            metrics=metrics,
            collected_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to collect metrics: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/workspace/{workspace_id}", summary="Get Workspace Metrics", tags=["Analytics"])
async def get_workspace_metrics(
    workspace_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Retrieves aggregated metrics for entire workspace."""
    if auth["workspace_id"] != workspace_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized")
    
    correlation_id = generate_correlation_id()
    
    try:
        metrics = await analytics_agent.collect_metrics(workspace_id, None, None, correlation_id)
        return {"workspace_id": str(workspace_id), "metrics": metrics}
        
    except Exception as e:
        logger.error(f"Failed to get workspace metrics: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/move/{move_id}", summary="Get Campaign Metrics", tags=["Analytics"])
async def get_move_metrics(
    move_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Retrieves metrics for a specific campaign."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    
    try:
        metrics = await analytics_agent.collect_metrics(workspace_id, move_id, None, correlation_id)
        return {"move_id": str(move_id), "metrics": metrics}
        
    except Exception as e:
        logger.error(f"Failed to get move metrics: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/move/{move_id}/insights", response_model=InsightsResponse, summary="Get Campaign Insights", tags=["Analytics"])
async def get_move_insights(
    move_id: UUID,
    time_period_days: int = 30,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """Generates insights for a campaign."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    
    try:
        analysis = await insight_agent.analyze_performance(
            workspace_id,
            move_id,
            time_period_days,
            correlation_id
        )
        
        return InsightsResponse(**analysis)
        
    except Exception as e:
        logger.error(f"Failed to generate insights: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/move/{move_id}/pivot", summary="Get Pivot Suggestion", tags=["Analytics"])
async def get_pivot_suggestion(
    move_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Suggests strategic pivot based on performance."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    
    try:
        pivot = await insight_agent.suggest_pivot(workspace_id, move_id, correlation_id)
        return {"pivot": pivot}
        
    except Exception as e:
        logger.error(f"Failed to suggest pivot: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/move/{move_id}/post-mortem", summary="Generate Campaign Post-Mortem", tags=["Analytics"])
async def generate_post_mortem(
    move_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Generates comprehensive post-mortem report for completed campaign."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    
    try:
        report = await campaign_review_agent.generate_post_mortem(workspace_id, move_id, correlation_id)
        return {"report": report}
        
    except Exception as e:
        logger.error(f"Failed to generate post-mortem: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/learnings", summary="Get Cross-Campaign Learnings", tags=["Analytics"])
async def get_learnings(
    timeframe_days: int = 90,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """Extracts learnings across all recent campaigns."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    
    try:
        learnings = await campaign_review_agent.extract_learnings(workspace_id, timeframe_days, correlation_id)
        return {"learnings": learnings, "timeframe_days": timeframe_days}
        
    except Exception as e:
        logger.error(f"Failed to extract learnings: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


