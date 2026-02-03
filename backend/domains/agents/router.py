"""
Agents Domain - Router
API routes for agent execution
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from dependencies import (
    get_agents,
    require_workspace_id,
    AgentService,
)
from infrastructure.database import get_supabase

router = APIRouter()


# Request/Response schemas
class CreateTaskRequest(BaseModel):
    agent_type: str
    input_data: Dict[str, Any]


class TaskResponse(BaseModel):
    id: str
    status: str
    agent_type: str


# Routes
@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    data: CreateTaskRequest,
    workspace_id: str = Depends(require_workspace_id),
    service: AgentService = Depends(get_agents)
):
    """Create a new agent task"""
    task = await service.create_task(
        workspace_id=workspace_id,
        agent_type=data.agent_type,
        input_data=data.input_data
    )

    if not task:
        raise HTTPException(status_code=400, detail="Failed to create task")

    return TaskResponse(
        id=task.id,
        status=task.status,
        agent_type=task.agent_type
    )


@router.get("/tasks/{task_id}")
async def get_task(
    task_id: str,
    service: AgentService = Depends(get_agents)
):
    """Get task status and result"""
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "id": task.id,
        "status": task.status,
        "agent_type": task.agent_type,
        "input": task.input_data,
        "output": task.output_data,
        "error": task.error_message,
        "created_at": task.created_at,
        "completed_at": task.completed_at,
    }


@router.post("/tasks/{task_id}/execute")
async def execute_task(
    task_id: str,
    service: AgentService = Depends(get_agents)
):
    """Execute a pending task"""
    result = await service.execute_task(task_id)

    return {
        "task_id": result.task_id,
        "status": result.status,
        "output": result.output,
        "error": result.error,
        "execution_time_ms": result.execution_time_ms,
    }


@router.get("/tasks")
async def list_tasks(
    workspace_id: str = Depends(require_workspace_id),
):
    """List tasks for workspace"""
    db = get_supabase()
    result = await db.select("agent_tasks", {"workspace_id": workspace_id})

    return result.data or []
