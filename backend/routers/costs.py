"""
Cost Tracking Router

API endpoints for retrieving AI agent cost logs and summaries.
Provides secure access to cost tracking data for workspaces.
"""

import structlog
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from backend.utils.auth import get_current_user_and_workspace
from backend.services.cost_tracker import cost_tracker
from backend.models.cost import CostLog

router = APIRouter()
logger = structlog.get_logger(__name__)


# --- Response Models ---

class CostLogResponse(BaseModel):
    """Simplified response model for cost logs."""
    id: UUID
    correlation_id: UUID
    agent_name: str
    action_name: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    created_at: str

    @classmethod
    def from_cost_log(cls, cost_log: CostLog) -> "CostLogResponse":
        """Convert a CostLog model to response format."""
        return cls(
            id=cost_log.id,
            correlation_id=cost_log.correlation_id,
            agent_name=cost_log.agent_name,
            action_name=cost_log.action_name,
            input_tokens=cost_log.input_tokens,
            output_tokens=cost_log.output_tokens,
            estimated_cost_usd=float(cost_log.estimated_cost_usd),
            created_at=cost_log.created_at.isoformat() if cost_log.created_at else None,
        )


class WorkspaceCostsResponse(BaseModel):
    """Response model for workspace cost summary."""
    workspace_id: UUID
    cost_logs: List[CostLogResponse]
    total_cost_usd: float
    total_logs: int


@router.get("/costs/{workspace_id}", response_model=WorkspaceCostsResponse, summary="Get Workspace Costs", tags=["Cost Tracking"])
async def get_workspace_costs(
    workspace_id: UUID,
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of cost logs to return (1-1000)"),
    offset: Optional[int] = Query(None, ge=0, description="Number of cost logs to skip"),
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Retrieve cost tracking logs for a specific workspace.

    This endpoint returns all AI agent cost logs for the authenticated workspace,
    ordered by creation time (newest first). The logs include estimated costs
    for each AI operation performed by agents in the workspace.

    **Authentication Required:** The user must have access to the specified workspace.

    **Parameters:**
    - workspace_id: UUID of the workspace
    - limit: Optional limit on number of results (max 1000)
    - offset: Optional offset for pagination

    **Returns:**
    - List of cost logs with details
    - Total estimated cost for the workspace
    - Count of cost log entries
    """
    # Verify workspace access
    if auth["workspace_id"] != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to view costs for this workspace"
        )

    logger.info(
        "Retrieving cost logs for workspace",
        workspace_id=str(workspace_id),
        user_id=auth["user_id"],
        limit=limit,
        offset=offset,
    )

    try:
        # Retrieve cost logs
        cost_logs = await cost_tracker.get_costs_for_workspace(
            workspace_id=workspace_id,
            limit=limit,
            offset=offset
        )

        # Calculate total cost
        total_cost = await cost_tracker.get_total_cost_for_workspace(workspace_id)

        # Convert to response format
        cost_log_responses = [CostLogResponse.from_cost_log(log) for log in cost_logs]

        response = WorkspaceCostsResponse(
            workspace_id=workspace_id,
            cost_logs=cost_log_responses,
            total_cost_usd=float(total_cost),
            total_logs=len(cost_log_responses),
        )

        logger.info(
            "Successfully retrieved cost logs",
            workspace_id=str(workspace_id),
            total_logs=len(cost_logs),
            total_cost=float(total_cost),
        )

        return response

    except Exception as e:
        logger.error(
            "Failed to retrieve workspace costs",
            workspace_id=str(workspace_id),
            user_id=auth["user_id"],
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cost logs: {str(e)}"
        )


@router.get("/costs/{workspace_id}/total", summary="Get Workspace Total Cost", tags=["Cost Tracking"])
async def get_workspace_total_cost(
    workspace_id: UUID,
    auth: dict = Depends(get_current_user_and_workspace),
):
    """
    Get the total estimated cost for a workspace.

    This endpoint provides a quick summary of the total AI operation costs
    for the authenticated workspace without returning individual logs.

    **Authentication Required:** The user must have access to the specified workspace.

    **Returns:**
    - Total estimated cost in USD
    """
    # Verify workspace access
    if auth["workspace_id"] != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You do not have permission to view costs for this workspace"
        )

    logger.info(
        "Retrieving total cost for workspace",
        workspace_id=str(workspace_id),
        user_id=auth["user_id"],
    )

    try:
        total_cost = await cost_tracker.get_total_cost_for_workspace(workspace_id)

        return {
            "workspace_id": str(workspace_id),
            "total_cost_usd": float(total_cost),
        }

    except Exception as e:
        logger.error(
            "Failed to retrieve total cost",
            workspace_id=str(workspace_id),
            user_id=auth["user_id"],
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve total cost: {str(e)}"
        )
