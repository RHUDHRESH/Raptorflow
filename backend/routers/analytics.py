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
from backend.graphs.execution_analytics_graph import (
    execution_analytics_graph_runnable,
    ExecutionAnalyticsGraphState
)
from backend.services.supabase_client import supabase_client
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


@router.get("/move/{move_id}/insights", response_model=dict, summary="Get Campaign Insights", tags=["Analytics"])
async def get_move_insights(
    move_id: UUID,
    time_period_days: int = 30,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)] = None
):
    """
    Generates insights for a campaign using the Analytics Supervisor.
    Calls the analytics graph to collect metrics and analyze performance.
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Generating campaign insights via analytics graph",
                move_id=move_id,
                time_period_days=time_period_days,
                correlation_id=correlation_id)

    try:
        # Use analytics graph to collect metrics and generate insights
        initial_state = ExecutionAnalyticsGraphState(
            user_id=auth["user_id"],
            workspace_id=workspace_id,
            correlation_id=correlation_id,
            move_id=move_id,
            action="analyze_performance",
            content_id=None,
            platform=None,
            scheduled_time=None,
            metrics_data=None,
            insights=None,
            next_step="insights"
        )

        final_state = await execution_analytics_graph_runnable.ainvoke(initial_state)

        insights = final_state.get("insights", {})

        logger.info("Campaign insights generated successfully",
                   move_id=move_id,
                   correlation_id=correlation_id)

        return {
            "move_id": str(move_id),
            "insights": insights.get("insights", []),
            "anomalies": insights.get("anomalies", []),
            "analyzed_period_days": time_period_days,
            "data_points": insights.get("data_points", 0),
            "correlation_id": correlation_id
        }

    except Exception as e:
        logger.error(f"Failed to generate insights: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


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
    """
    Generates and stores a comprehensive post-mortem report for completed campaign.
    Analyzes performance, learnings, and recommendations for future campaigns.
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Generating campaign post-mortem",
                move_id=move_id,
                correlation_id=correlation_id)

    try:
        # Generate post-mortem report
        report = await campaign_review_agent.generate_post_mortem(
            workspace_id,
            move_id,
            correlation_id
        )

        # Store post-mortem in database
        post_mortem_data = {
            "workspace_id": str(workspace_id),
            "move_id": str(move_id),
            "report": report,
            "generated_at": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id
        }

        # Store in a post_mortems table or update the move record
        try:
            await supabase_client.insert("post_mortems", post_mortem_data)
        except Exception as db_error:
            # If post_mortems table doesn't exist, store in move metadata
            logger.warning(f"Failed to insert into post_mortems table: {db_error}. Storing in move metadata.")
            await supabase_client.update(
                "moves",
                {"id": str(move_id), "workspace_id": str(workspace_id)},
                {"post_mortem": report, "updated_at": datetime.utcnow().isoformat()}
            )

        logger.info("Post-mortem generated and stored successfully",
                   move_id=move_id,
                   correlation_id=correlation_id)

        return {
            "status": "success",
            "move_id": str(move_id),
            "report": report,
            "correlation_id": correlation_id
        }

    except Exception as e:
        logger.error(f"Failed to generate post-mortem: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


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



