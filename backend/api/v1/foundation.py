"""
Foundation API (No-Auth Reconstruction Mode)

Manages the workspace foundation data in the canonical `foundations` table.
All operations scoped by X-Workspace-Id header.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from backend.core.supabase_mgr import get_supabase_client
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/foundation", tags=["foundation"])


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


class FoundationOut(BaseModel):
    id: Optional[str] = None
    workspace_id: Optional[str] = None
    company_info: Dict[str, Any] = Field(default_factory=dict)
    mission: Optional[str] = None
    vision: Optional[str] = None
    value_proposition: Optional[str] = None
    brand_voice: Dict[str, Any] = Field(default_factory=dict)
    messaging: Dict[str, Any] = Field(default_factory=dict)
    status: str = "draft"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class FoundationUpdate(BaseModel):
    company_info: Optional[Dict[str, Any]] = None
    mission: Optional[str] = None
    vision: Optional[str] = None
    value_proposition: Optional[str] = None
    brand_voice: Optional[Dict[str, Any]] = None
    messaging: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


@router.get("/", response_model=FoundationOut)
async def get_foundation(
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> FoundationOut:
    workspace_id = _require_workspace_id(x_workspace_id)
    supabase = get_supabase_client()

    result = (
        supabase.table("foundations")
        .select("*")
        .eq("workspace_id", workspace_id)
        .limit(1)
        .execute()
    )

    if not result.data:
        return FoundationOut(workspace_id=workspace_id)

    return FoundationOut(**result.data[0])


@router.put("/", response_model=FoundationOut)
async def save_foundation(
    payload: FoundationUpdate,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> FoundationOut:
    workspace_id = _require_workspace_id(x_workspace_id)
    supabase = get_supabase_client()

    row = {"workspace_id": workspace_id}
    update_data = payload.model_dump(exclude_none=True)
    row.update(update_data)

    result = (
        supabase.table("foundations")
        .upsert(row, on_conflict="workspace_id")
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save foundation")

    return FoundationOut(**result.data[0])
