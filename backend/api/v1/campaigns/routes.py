"""
Campaigns API

This is the canonical CRUD surface used by the Next.js frontend.
All operations are scoped by the tenant/workspace via `X-Workspace-Id`.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Depends, status
from pydantic import BaseModel, Field

from backend.ai.application.terminal_adapter import terminal_adapter
from backend.api.v1.workspace_guard import (
    enforce_bcm_ready,
    require_workspace_id,
)
from backend.services.exceptions import ServiceError
from backend.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


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


class CampaignMovesBundleOut(BaseModel):
    campaign: Optional[CampaignOut] = None
    moves: List[Dict[str, Any]] = Field(default_factory=list)


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
    workspace_id = require_workspace_id(x_workspace_id)
    enforce_bcm_ready(workspace_id)

    try:
        campaigns_data = await terminal_adapter.list_campaigns(
            workspace_id
        )
        campaigns = [CampaignOut(**row) for row in campaigns_data]
        return CampaignListOut(campaigns=campaigns)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=CampaignOut, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CampaignCreate,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> CampaignOut:
    workspace_id = require_workspace_id(x_workspace_id)
    enforce_bcm_ready(workspace_id)

    insert_row: Dict[str, Any] = {
        "title": payload.name,
        "description": payload.description,
        "objective": _normalize_objective(payload.objective),
        "status": _normalize_status(payload.status),
    }

    try:
        result = await terminal_adapter.create_campaign(
            workspace_id, insert_row
        )
        return CampaignOut(**result)
    except ServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{campaign_id}", response_model=CampaignOut)
async def get_campaign(
    campaign_id: str,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> CampaignOut:
    workspace_id = require_workspace_id(x_workspace_id)
    enforce_bcm_ready(workspace_id)
    try:
        UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign_id")

    result = await terminal_adapter.get_campaign(
        workspace_id, campaign_id
    )
    if not result:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return CampaignOut(**result)


@router.get("/{campaign_id}/moves-bundle", response_model=CampaignMovesBundleOut)
async def get_campaign_moves_bundle(
    campaign_id: str,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> CampaignMovesBundleOut:
    workspace_id = require_workspace_id(x_workspace_id)
    enforce_bcm_ready(workspace_id)
    try:
        UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign_id")

    bundle = await terminal_adapter.campaign_moves_bundle(
        workspace_id,
        campaign_id,
    )
    campaign = bundle.get("campaign")
    moves = bundle.get("moves") or []
    return CampaignMovesBundleOut(
        campaign=CampaignOut(**campaign) if campaign else None,
        moves=moves,
    )


@router.patch("/{campaign_id}", response_model=CampaignOut)
async def update_campaign(
    campaign_id: str,
    updates: CampaignUpdate,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> CampaignOut:
    workspace_id = require_workspace_id(x_workspace_id)
    enforce_bcm_ready(workspace_id)
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

    result = await terminal_adapter.update_campaign(
        workspace_id,
        campaign_id,
        update_row,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return CampaignOut(**result)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: str,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
):
    workspace_id = require_workspace_id(x_workspace_id)
    enforce_bcm_ready(workspace_id)
    try:
        UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign_id")

    deleted = await terminal_adapter.delete_campaign(
        workspace_id,
        campaign_id,
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return None
