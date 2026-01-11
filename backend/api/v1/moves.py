"""
Moves API endpoints
Handles HTTP requests for move operations
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...core.auth import get_current_user, get_workspace_id
from ...core.models import User
from ...services.move import MoveService

router = APIRouter(prefix="/moves", tags=["moves"])


# Pydantic models for request/response
class MoveCreate(BaseModel):
    name: str
    category: Optional[str] = None
    goal: Optional[str] = None
    target_icp_id: Optional[str] = None
    strategy: Optional[dict] = None
    execution_plan: Optional[List[str]] = None
    status: Optional[str] = None
    duration_days: Optional[int] = None
    success_metrics: Optional[List[str]] = None


class MoveUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    goal: Optional[str] = None
    target_icp_id: Optional[str] = None
    strategy: Optional[dict] = None
    execution_plan: Optional[List[str]] = None
    status: Optional[str] = None
    duration_days: Optional[int] = None
    success_metrics: Optional[List[str]] = None
    results: Optional[dict] = None


class MoveResponse(BaseModel):
    id: str
    workspace_id: str
    campaign_id: Optional[str]
    name: str
    category: str
    goal: Optional[str]
    target_icp_id: Optional[str]
    strategy: dict
    execution_plan: List[str]
    status: str
    duration_days: Optional[int]
    started_at: Optional[str]
    completed_at: Optional[str]
    success_metrics: List[str]
    results: dict
    created_at: str
    updated_at: str


# Dependency injection
def get_move_service() -> MoveService:
    return MoveService()


@router.get("/", response_model=List[MoveResponse])
async def list_moves(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    move_service: MoveService = Depends(get_move_service),
):
    """List all moves for workspace"""
    moves = await move_service.list_moves(workspace_id)
    return moves


@router.post("/", response_model=MoveResponse)
async def create_move(
    move_data: MoveCreate,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    move_service: MoveService = Depends(get_move_service),
):
    """Create new move"""
    try:
        move = await move_service.create_move(workspace_id, move_data.dict())
        return move
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{move_id}", response_model=MoveResponse)
async def get_move(
    move_id: str,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    move_service: MoveService = Depends(get_move_service),
):
    """Get move by ID with details"""
    move = await move_service.get_move_with_details(move_id, workspace_id)

    if not move:
        raise HTTPException(status_code=404, detail="Move not found")

    return move


@router.put("/{move_id}", response_model=MoveResponse)
async def update_move(
    move_id: str,
    move_data: MoveUpdate,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    move_service: MoveService = Depends(get_move_service),
):
    """Update move"""
    try:
        move = await move_service.update_move(
            move_id, workspace_id, move_data.dict(exclude_unset=True)
        )

        if not move:
            raise HTTPException(status_code=404, detail="Move not found")

        return move
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{move_id}")
async def delete_move(
    move_id: str,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    move_service: MoveService = Depends(get_move_service),
):
    """Delete move"""
    try:
        success = await move_service.delete_move(move_id, workspace_id)

        if not success:
            raise HTTPException(status_code=404, detail="Move not found")

        return {"message": "Move deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{move_id}/start", response_model=MoveResponse)
async def start_move(
    move_id: str,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    move_service: MoveService = Depends(get_move_service),
):
    """Start a move"""
    try:
        move = await move_service.start_move(move_id, workspace_id)

        if not move:
            raise HTTPException(status_code=404, detail="Move not found")

        return move
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{move_id}/pause", response_model=MoveResponse)
async def pause_move(
    move_id: str,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    move_service: MoveService = Depends(get_move_service),
):
    """Pause a move"""
    try:
        move = await move_service.pause_move(move_id, workspace_id)

        if not move:
            raise HTTPException(status_code=404, detail="Move not found")

        return move
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{move_id}/complete", response_model=MoveResponse)
async def complete_move(
    move_id: str,
    results: Optional[dict] = None,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    move_service: MoveService = Depends(get_move_service),
):
    """Complete a move"""
    try:
        move = await move_service.complete_move(move_id, workspace_id, results)

        if not move:
            raise HTTPException(status_code=404, detail="Move not found")

        return move
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{move_id}/generate-tasks")
async def generate_tasks(
    move_id: str,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    move_service: MoveService = Depends(get_move_service),
):
    """Generate tasks for a move"""
    try:
        tasks = await move_service.generate_tasks(move_id, workspace_id)
        return {"tasks": tasks, "count": len(tasks)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{move_id}/tasks")
async def get_move_tasks(
    move_id: str,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    move_service: MoveService = Depends(get_move_service),
):
    """Get tasks for a move"""
    try:
        move = await move_service.get_move_with_details(move_id, workspace_id)

        if not move:
            raise HTTPException(status_code=404, detail="Move not found")

        return {"tasks": move.get("tasks", [])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/analytics")
async def get_move_analytics(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    move_service: MoveService = Depends(get_move_service),
):
    """Get move analytics"""
    try:
        analytics = await move_service.get_move_analytics(workspace_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/active", response_model=List[MoveResponse])
async def get_active_moves(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    move_service: MoveService = Depends(get_move_service),
):
    """Get all active moves"""
    try:
        moves = await move_service.list_moves(workspace_id, {"status": "active"})
        return moves
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
