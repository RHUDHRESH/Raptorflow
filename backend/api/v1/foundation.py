"""
Foundation API (No-Auth Reconstruction Mode)

Stores the frontend Foundation state as JSON scoped by tenant/workspace.
This intentionally avoids Supabase Auth/RLS by using the service role on the backend.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from backend.core.supabase_mgr import get_supabase_client
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/foundation", tags=["foundation"])


def _require_tenant_id(x_workspace_id: Optional[str]) -> str:
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


class FoundationState(BaseModel):
    ricps: List[Dict[str, Any]] = Field(default_factory=list)
    messaging: Optional[Dict[str, Any]] = None
    channels: List[Dict[str, Any]] = Field(default_factory=list)


@router.get("/", response_model=FoundationState)
async def get_foundation(
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> FoundationState:
    tenant_id = _require_tenant_id(x_workspace_id)
    supabase = get_supabase_client()

    result = (
        supabase.table("foundation_state")
        .select("phase_progress")
        .eq("tenant_id", tenant_id)
        .single()
        .execute()
    )

    if not result.data:
        return FoundationState()

    phase_progress = result.data.get("phase_progress") or {}
    return FoundationState(
        ricps=phase_progress.get("ricps") or [],
        messaging=phase_progress.get("messaging"),
        channels=phase_progress.get("channels") or [],
    )


@router.put("/", response_model=FoundationState)
async def save_foundation(
    payload: FoundationState,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> FoundationState:
    tenant_id = _require_tenant_id(x_workspace_id)
    supabase = get_supabase_client()

    row = {
        "tenant_id": tenant_id,
        "phase_progress": {
            "ricps": payload.ricps,
            "messaging": payload.messaging,
            "channels": payload.channels,
        },
    }

    result = supabase.table("foundation_state").upsert(row).execute()
    if result.data is None:
        raise HTTPException(status_code=500, detail="Failed to save foundation state")

    return payload
