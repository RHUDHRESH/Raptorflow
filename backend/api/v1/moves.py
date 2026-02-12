"""
Moves API (No-Auth Reconstruction Mode)

The frontend Move model does not match the current DB schema 1:1.
We store the canonical UI move as JSON under `tool_requirements.ui_move`
while also populating required DB columns to satisfy constraints.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from backend.agents import langgraph_campaign_moves_orchestrator
from backend.services.exceptions import ServiceError

router = APIRouter(prefix="/moves", tags=["moves"])


def _require_workspace_id(x_workspace_id: Optional[str]) -> str:
    if not x_workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Workspace-Id header",
        )
    try:
        UUID(x_workspace_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-Workspace-Id header (must be UUID)",
        )
    return x_workspace_id


class MoveModel(BaseModel):
    id: str
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    status: str
    duration: int
    goal: str
    tone: str
    context: str
    attachments: Optional[List[str]] = None
    createdAt: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    execution: List[Dict[str, Any]] = Field(default_factory=list)
    progress: Optional[int] = None
    icp: Optional[str] = None
    campaignId: Optional[str] = None
    metrics: Optional[List[str]] = None
    workspaceId: Optional[str] = None


class MoveListOut(BaseModel):
    moves: List[MoveModel]


@router.get("/", response_model=MoveListOut)
async def list_moves(
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> MoveListOut:
    workspace_id = _require_workspace_id(x_workspace_id)
    
    try:
        moves_data = await langgraph_campaign_moves_orchestrator.list_moves(workspace_id)
        # Validate/Convert to Pydantic models to ensure schema compliance
        moves = []
        for m in moves_data:
            try:
                moves.append(MoveModel(**m))
            except Exception as e:
                # Log error but skip malformed move to avoid breaking the whole list
                print(f"Skipping malformed move {m.get('id')}: {e}")
                continue
                
        return MoveListOut(moves=moves)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=MoveModel, status_code=status.HTTP_201_CREATED)
async def create_move(
    move: MoveModel,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> MoveModel:
    workspace_id = _require_workspace_id(x_workspace_id)

    try:
        result = await langgraph_campaign_moves_orchestrator.create_move(
            workspace_id,
            move.model_dump(),
        )
        return MoveModel(**result)
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


class MovePatch(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    duration: Optional[int] = None
    goal: Optional[str] = None
    tone: Optional[str] = None
    context: Optional[str] = None
    attachments: Optional[List[str]] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    execution: Optional[List[Dict[str, Any]]] = None
    progress: Optional[int] = None
    icp: Optional[str] = None
    campaignId: Optional[str] = None
    metrics: Optional[List[str]] = None


@router.patch("/{move_id}", response_model=MoveModel)
async def update_move(
    move_id: str,
    patch: MovePatch,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> MoveModel:
    workspace_id = _require_workspace_id(x_workspace_id)
    try:
        UUID(move_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid move_id")

    try:
        result = await langgraph_campaign_moves_orchestrator.update_move(
            workspace_id, 
            move_id, 
            patch.model_dump(exclude_unset=True)
        )
        if not result:
            raise HTTPException(status_code=404, detail="Move not found")
        return MoveModel(**result)
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{move_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_move(
    move_id: str,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
):
    workspace_id = _require_workspace_id(x_workspace_id)
    try:
        UUID(move_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid move_id")

    try:
        deleted = await langgraph_campaign_moves_orchestrator.delete_move(workspace_id, move_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Move not found")
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return None
