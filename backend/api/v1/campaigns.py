"""
Campaigns API (No-Auth Reconstruction Mode)

This is the canonical CRUD surface used by the Next.js frontend.
All operations are scoped by the tenant/workspace via `X-Workspace-Id`.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from backend.core.supabase_mgr import get_supabase_client
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


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


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    objective: Optional[str] = None
    status: Optional[str] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    objective: Optional[str] = None
    status: Optional[str] = None


class CampaignOut(BaseModel):
    id: str
    workspace_id: str
    title: str
    description: Optional[str] = None
    objective: str
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CampaignListOut(BaseModel):
    campaigns: List[CampaignOut]


_DEFAULT_OBJECTIVE = "acquire"
_DEFAULT_STATUS = "active"
_ALLOWED_OBJECTIVES = {"acquire", "convert", "launch", "proof", "retain", "reposition"}
_ALLOWED_STATUSES = {"planned", "active", "paused", "wrapup", "archived"}


def _normalize_objective(obj: Optional[str]) -> str:
    if not obj:
        return _DEFAULT_OBJECTIVE
    value = obj.strip().lower()
    if value not in _ALLOWED_OBJECTIVES:
        allowed = ", ".join(sorted(_ALLOWED_OBJECTIVES))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid objective '{obj}'. Allowed values: {allowed}",
        )
    return value


def _normalize_status(status_value: Optional[str]) -> str:
    if not status_value:
        return _DEFAULT_STATUS
    value = status_value.strip().lower()
    if value not in _ALLOWED_STATUSES:
        allowed = ", ".join(sorted(_ALLOWED_STATUSES))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{status_value}'. Allowed values: {allowed}",
        )
    return value


@router.get("/", response_model=CampaignListOut)
async def list_campaigns(
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> CampaignListOut:
    workspace_id = _require_workspace_id(x_workspace_id)
    supabase = get_supabase_client()

    result = (
        supabase.table("campaigns")
        .select("*")
        .eq("workspace_id", workspace_id)
        .order("created_at", desc=True)
        .execute()
    )

    campaigns = [CampaignOut(**row) for row in (result.data or [])]
    return CampaignListOut(campaigns=campaigns)


@router.post("/", response_model=CampaignOut, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CampaignCreate,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> CampaignOut:
    workspace_id = _require_workspace_id(x_workspace_id)
    supabase = get_supabase_client()

    insert_row: Dict[str, Any] = {
        "id": str(uuid4()),
        "workspace_id": workspace_id,
        "title": payload.name,
        "description": payload.description,
        "objective": _normalize_objective(payload.objective),
        "status": _normalize_status(payload.status),
    }

    result = supabase.table("campaigns").insert(insert_row).execute()
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create campaign",
        )

    return CampaignOut(**result.data[0])


@router.get("/{campaign_id}", response_model=CampaignOut)
async def get_campaign(
    campaign_id: str,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> CampaignOut:
    workspace_id = _require_workspace_id(x_workspace_id)
    supabase = get_supabase_client()
    try:
        UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign_id")

    result = (
        supabase.table("campaigns")
        .select("*")
        .eq("id", campaign_id)
        .eq("workspace_id", workspace_id)
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return CampaignOut(**result.data)


@router.patch("/{campaign_id}", response_model=CampaignOut)
async def update_campaign(
    campaign_id: str,
    updates: CampaignUpdate,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> CampaignOut:
    workspace_id = _require_workspace_id(x_workspace_id)
    supabase = get_supabase_client()
    try:
        UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign_id")

    update_row: Dict[str, Any] = {}
    if updates.name is not None:
        update_row["title"] = updates.name
    if updates.description is not None:
        update_row["description"] = updates.description
    if updates.objective is not None:
        update_row["objective"] = _normalize_objective(updates.objective)
    if updates.status is not None:
        update_row["status"] = _normalize_status(updates.status)

    if not update_row:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = (
        supabase.table("campaigns")
        .update(update_row)
        .eq("id", campaign_id)
        .eq("workspace_id", workspace_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return CampaignOut(**result.data[0])


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: str,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
):
    workspace_id = _require_workspace_id(x_workspace_id)
    supabase = get_supabase_client()
    try:
        UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign_id")

    result = (
        supabase.table("campaigns")
        .delete()
        .eq("id", campaign_id)
        .eq("workspace_id", workspace_id)
        .execute()
    )
    if result.data is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return None
