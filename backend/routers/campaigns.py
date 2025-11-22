"""
Campaigns Router - API endpoints for campaign/move creation, tasks, and tracking.
"""

import structlog
from typing import Annotated
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.main import get_current_user_and_workspace
from backend.models.campaign import MoveRequest, MoveResponse, Task
from backend.graphs.strategy_graph import strategy_graph_runnable, StrategyGraphState
from backend.agents.execution.scheduler_agent import scheduler_agent
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id, generate_correlation_id

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/create", response_model=MoveResponse, summary="Create Campaign", tags=["Campaigns"])
async def create_campaign(
    request: MoveRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Creates a new marketing campaign (Move)."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Creating campaign", name=request.name, correlation_id=correlation_id)
    
    try:
        # Use strategy graph to generate campaign plan
        initial_state = StrategyGraphState(
            user_id=auth["user_id"],
            workspace_id=workspace_id,
            correlation_id=correlation_id,
            goal=request.goal,
            timeframe_days=request.timeframe_days,
            target_cohort_ids=request.target_cohort_ids,
            channels=request.channels,
            constraints=request.constraints,
            adapt_stage="design",
            next_step="campaign_plan"
        )
        
        final_state = await strategy_graph_runnable.ainvoke(initial_state)
        campaign_plan = final_state.get("campaign_plan")
        
        # Create move record
        move_data = {
            "workspace_id": str(workspace_id),
            "name": request.name,
            "goal": request.goal,
            "status": "planning",
            "start_date": datetime.utcnow().isoformat(),
            "target_cohort_ids": [str(cid) for cid in request.target_cohort_ids],
            "channels": request.channels,
            "lines_of_operation": campaign_plan.get("lines_of_operation", []) if campaign_plan else [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        move_record = await supabase_client.insert("moves", move_data)
        
        logger.info("Campaign created", move_id=move_record["id"], correlation_id=correlation_id)
        return MoveResponse(**move_record)
        
    except Exception as e:
        logger.error(f"Failed to create campaign: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{move_id}", response_model=MoveResponse, summary="Get Campaign", tags=["Campaigns"])
async def get_campaign(
    move_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Retrieves a specific campaign."""
    workspace_id = auth["workspace_id"]
    
    move = await supabase_client.fetch_one(
        "moves",
        {"id": str(move_id), "workspace_id": str(workspace_id)}
    )
    
    if not move:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
    
    return MoveResponse(**move)


@router.get("/{move_id}/tasks/today", response_model=list[Task], summary="Get Today's Tasks", tags=["Campaigns"])
async def get_todays_tasks(
    move_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Retrieves today's tasks for a campaign."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    
    try:
        tasks = await scheduler_agent.generate_daily_checklist(
            workspace_id,
            move_id,
            datetime.now(),
            correlation_id
        )
        
        return tasks
        
    except Exception as e:
        logger.error(f"Failed to get tasks: {e}", correlation_id=correlation_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{move_id}/task/{task_id}/complete", summary="Mark Task Complete", tags=["Campaigns"])
async def complete_task(
    move_id: UUID,
    task_id: UUID,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Marks a task as complete."""
    workspace_id = auth["workspace_id"]
    
    try:
        await supabase_client.update(
            "tasks",
            {"id": str(task_id), "move_id": str(move_id)},
            {"status": "completed", "updated_at": datetime.utcnow().isoformat()}
        )
        
        return {"status": "success", "message": "Task marked complete"}
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=list[MoveResponse], summary="List Campaigns", tags=["Campaigns"])
async def list_campaigns(auth: Annotated[dict, Depends(get_current_user_and_workspace)]):
    """Lists all campaigns for the workspace."""
    workspace_id = auth["workspace_id"]
    
    moves = await supabase_client.fetch_all(
        "moves",
        {"workspace_id": str(workspace_id)}
    )
    
    return [MoveResponse(**m) for m in moves]


