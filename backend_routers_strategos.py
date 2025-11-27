# backend/routers/strategos.py
# RaptorFlow Codex - Strategos Lord API Endpoints
# Phase 2A Week 5 - Execution Management & Resource Allocation

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging
from datetime import datetime

from agents.council_of_lords.strategos import StrategosLord, ExecutionStatus, ResourceType, PriorityLevel
from dependencies import get_current_user, get_current_workspace

logger = logging.getLogger(__name__)

# Get Strategos instance (singleton)
strategos: Optional[StrategosLord] = None

async def get_strategos() -> StrategosLord:
    """Get or initialize Strategos Lord"""
    global strategos
    if strategos is None:
        strategos = StrategosLord()
        await strategos.initialize()
    return strategos

router = APIRouter(prefix="/lords/strategos", tags=["Strategos Lord"])

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CreateExecutionPlanRequest(BaseModel):
    """Create execution plan"""
    plan_name: str
    description: Optional[str] = ""
    objectives: List[str]
    target_guilds: List[str]
    start_date: Optional[str] = None
    end_date: str

class AssignTaskRequest(BaseModel):
    """Assign execution task"""
    task_name: str
    description: str
    assigned_guild: str
    assigned_agent: str
    estimated_hours: float
    deadline: str
    priority: str  # critical, high, normal, low, deferred
    plan_id: Optional[str] = None
    dependencies: Optional[List[str]] = None

class AllocateResourceRequest(BaseModel):
    """Allocate resource"""
    resource_type: str  # agent, budget, time, compute, storage, bandwidth
    resource_name: str
    quantity: float
    unit: str
    assigned_to: str
    duration_hours: Optional[int] = 0

class TrackProgressRequest(BaseModel):
    """Track task progress"""
    task_id: str
    progress_percent: float
    actual_hours: float
    status: str  # planned, ready, active, in_progress, paused, blocked, completed, failed, cancelled
    blockers: Optional[List[str]] = None

class OptimizeTimelineRequest(BaseModel):
    """Optimize execution timeline"""
    plan_id: str

# ============================================================================
# EXECUTION PLAN ENDPOINTS
# ============================================================================

@router.post("/plans/create", response_model=Dict[str, Any])
async def create_execution_plan(
    request: CreateExecutionPlanRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    strategos_lord: StrategosLord = Depends(get_strategos)
):
    """
    Create execution plan.

    The Strategos Lord creates comprehensive execution plans with objectives,
    target guilds, timeline, and resource requirements.
    """
    logger.info(f"📋 Creating execution plan: {request.plan_name}")

    try:
        result = await strategos_lord.execute(
            task="create_execution_plan",
            parameters={
                "plan_name": request.plan_name,
                "description": request.description,
                "objectives": request.objectives,
                "target_guilds": request.target_guilds,
                "start_date": request.start_date or datetime.utcnow().isoformat(),
                "end_date": request.end_date,
                "tasks": []
            }
        )

        if result.get("success", True):
            return {
                "status": "success",
                "data": result,
                "execution_time": result.get("duration_seconds", 0)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Plan creation failed")
            )

    except Exception as e:
        logger.error(f"❌ Plan creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/plans", response_model=List[Dict[str, Any]])
async def list_execution_plans(
    status: Optional[str] = None,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    strategos_lord: StrategosLord = Depends(get_strategos)
):
    """List execution plans, optionally filtered by status."""
    plans = list(strategos_lord.execution_plans.values())
    if status:
        plans = [p for p in plans if p.status.value == status]
    return [p.to_dict() for p in plans]

@router.get("/plans/{plan_id}", response_model=Dict[str, Any])
async def get_execution_plan(
    plan_id: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    strategos_lord: StrategosLord = Depends(get_strategos)
):
    """Get execution plan details."""
    if plan_id not in strategos_lord.execution_plans:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {plan_id} not found"
        )

    return strategos_lord.execution_plans[plan_id].to_dict()

# ============================================================================
# TASK ASSIGNMENT ENDPOINTS
# ============================================================================

@router.post("/tasks/assign", response_model=Dict[str, Any])
async def assign_task(
    request: AssignTaskRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    strategos_lord: StrategosLord = Depends(get_strategos)
):
    """
    Assign execution task.

    The Strategos Lord assigns tasks to guilds/agents with estimated hours,
    deadline, priority, and dependencies.
    """
    logger.info(f"📌 Assigning task: {request.task_name}")

    try:
        result = await strategos_lord.execute(
            task="assign_task",
            parameters={
                "task_name": request.task_name,
                "description": request.description,
                "assigned_guild": request.assigned_guild,
                "assigned_agent": request.assigned_agent,
                "estimated_hours": request.estimated_hours,
                "deadline": request.deadline,
                "priority": request.priority,
                "plan_id": request.plan_id,
                "dependencies": request.dependencies or []
            }
        )

        if result.get("success", True):
            return {
                "status": "success",
                "data": result,
                "execution_time": result.get("duration_seconds", 0)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Task assignment failed")
            )

    except Exception as e:
        logger.error(f"❌ Task assignment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/tasks", response_model=List[Dict[str, Any]])
async def list_tasks(
    status: Optional[str] = None,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    strategos_lord: StrategosLord = Depends(get_strategos)
):
    """List execution tasks, optionally filtered by status."""
    tasks = list(strategos_lord.execution_tasks.values())
    if status:
        tasks = [t for t in tasks if t.status.value == status]
    return [t.to_dict() for t in tasks]

@router.get("/tasks/{task_id}", response_model=Dict[str, Any])
async def get_task(
    task_id: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    strategos_lord: StrategosLord = Depends(get_strategos)
):
    """Get task details."""
    if task_id not in strategos_lord.execution_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return strategos_lord.execution_tasks[task_id].to_dict()

# ============================================================================
# PROGRESS TRACKING ENDPOINTS
# ============================================================================

@router.post("/tasks/{task_id}/progress", response_model=Dict[str, Any])
async def track_progress(
    task_id: str,
    request: TrackProgressRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    strategos_lord: StrategosLord = Depends(get_strategos)
):
    """
    Track and update task progress.

    The Strategos Lord updates progress, hours worked, status, and blockers.
    """
    logger.info(f"📊 Tracking progress for task: {task_id}")

    try:
        result = await strategos_lord.execute(
            task="track_progress",
            parameters={
                "task_id": task_id,
                "progress_percent": request.progress_percent,
                "actual_hours": request.actual_hours,
                "status": request.status,
                "blockers": request.blockers or []
            }
        )

        if result.get("success", True):
            return {
                "status": "success",
                "data": result,
                "execution_time": result.get("duration_seconds", 0)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Progress tracking failed")
            )

    except Exception as e:
        logger.error(f"❌ Progress tracking error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# RESOURCE ALLOCATION ENDPOINTS
# ============================================================================

@router.post("/resources/allocate", response_model=Dict[str, Any])
async def allocate_resource(
    request: AllocateResourceRequest,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    strategos_lord: StrategosLord = Depends(get_strategos)
):
    """
    Allocate resource for execution.

    The Strategos Lord allocates resources (agents, budget, time, etc.)
    to support plan execution.
    """
    logger.info(f"💾 Allocating resource: {request.resource_name}")

    try:
        result = await strategos_lord.execute(
            task="allocate_resource",
            parameters={
                "resource_type": request.resource_type,
                "resource_name": request.resource_name,
                "quantity": request.quantity,
                "unit": request.unit,
                "assigned_to": request.assigned_to,
                "duration_hours": request.duration_hours
            }
        )

        if result.get("success", True):
            return {
                "status": "success",
                "data": result,
                "execution_time": result.get("duration_seconds", 0)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Resource allocation failed")
            )

    except Exception as e:
        logger.error(f"❌ Resource allocation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/resources/utilization", response_model=Dict[str, Any])
async def get_resource_utilization(
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    strategos_lord: StrategosLord = Depends(get_strategos)
):
    """Get resource utilization summary."""
    return await strategos_lord.get_resource_utilization()

# ============================================================================
# TIMELINE OPTIMIZATION ENDPOINTS
# ============================================================================

@router.post("/plans/{plan_id}/optimize-timeline", response_model=Dict[str, Any])
async def optimize_timeline(
    plan_id: str,
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    strategos_lord: StrategosLord = Depends(get_strategos)
):
    """
    Optimize execution timeline.

    The Strategos Lord analyzes the plan and provides optimization
    recommendations to reduce execution time.
    """
    logger.info(f"⏱️ Optimizing timeline for plan: {plan_id}")

    try:
        result = await strategos_lord.execute(
            task="optimize_timeline",
            parameters={
                "plan_id": plan_id
            }
        )

        if result.get("success", True):
            return {
                "status": "success",
                "data": result,
                "execution_time": result.get("duration_seconds", 0)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Timeline optimization failed")
            )

    except Exception as e:
        logger.error(f"❌ Timeline optimization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# STATUS & METRICS ENDPOINTS
# ============================================================================

@router.get("/active-plans", response_model=List[Dict[str, Any]])
async def get_active_plans(
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    strategos_lord: StrategosLord = Depends(get_strategos)
):
    """Get active execution plans."""
    return await strategos_lord.get_active_plans()

@router.get("/active-tasks", response_model=List[Dict[str, Any]])
async def get_active_tasks(
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    strategos_lord: StrategosLord = Depends(get_strategos)
):
    """Get active execution tasks."""
    return await strategos_lord.get_active_tasks()

@router.get("/status", response_model=Dict[str, Any])
async def get_strategos_status(
    current_user: str = Depends(get_current_user),
    current_workspace: str = Depends(get_current_workspace),
    strategos_lord: StrategosLord = Depends(get_strategos)
):
    """Get Strategos status and performance summary."""
    summary = await strategos_lord.get_performance_summary()

    return {
        "agent": {
            "name": strategos_lord.name,
            "role": strategos_lord.role.value,
            "status": strategos_lord.status.value
        },
        "performance": summary,
        "timestamp": datetime.utcnow().isoformat()
    }

# Import for type hints
from datetime import datetime
