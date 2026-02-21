"""
Campaign API Router (Modular Architecture).

This router uses the new hexagonal architecture for campaign operations.
It delegates to the application service, keeping HTTP handling separate
from business logic.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Depends, status
from pydantic import BaseModel, Field

from backend.api.v1.workspace_guard import (
    enforce_bcm_ready,
    require_workspace_id,
)
from backend.bootstrap.dependencies import CampaignServiceDep
from backend.core.exceptions import NotFoundError, ValidationError
from backend.services.campaign.domain.entities import Campaign

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


# =============================================================================
# Request/Response Schemas
# =============================================================================


class CampaignCreate(BaseModel):
    """Request schema for creating a campaign."""

    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    objective: Optional[str] = None
    status: Optional[str] = None


class CampaignUpdate(BaseModel):
    """Request schema for updating a campaign."""

    name: Optional[str] = None
    description: Optional[str] = None
    objective: Optional[str] = None
    status: Optional[str] = None


class CampaignOut(BaseModel):
    """Response schema for a campaign."""

    id: str
    workspace_id: str
    title: str
    description: Optional[str] = None
    objective: str
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_domain(cls, campaign: Campaign) -> "CampaignOut":
        """Create from domain entity."""
        return cls(
            id=campaign.id,
            workspace_id=campaign.workspace_id,
            title=campaign.title,
            description=campaign.description,
            objective=campaign.objective,
            status=campaign.status,
            created_at=campaign.created_at.isoformat() if campaign.created_at else None,
            updated_at=campaign.updated_at.isoformat() if campaign.updated_at else None,
        )


class CampaignListOut(BaseModel):
    """Response schema for campaign list."""

    campaigns: List[CampaignOut]


# =============================================================================
# API Endpoints
# =============================================================================


@router.get("/", response_model=CampaignListOut)
async def list_campaigns(
    service: CampaignServiceDep,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> CampaignListOut:
    """List all campaigns for a workspace."""
    workspace_id = require_workspace_id(x_workspace_id)
    enforce_bcm_ready(workspace_id)

    try:
        campaigns = await service.list_campaigns(workspace_id)
        campaign_outs = [CampaignOut.from_domain(c) for c in campaigns]
        return CampaignListOut(campaigns=campaign_outs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=CampaignOut, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CampaignCreate,
    service: CampaignServiceDep,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> CampaignOut:
    """Create a new campaign."""
    workspace_id = require_workspace_id(x_workspace_id)
    enforce_bcm_ready(workspace_id)

    try:
        campaign = await service.create_campaign(
            workspace_id=workspace_id,
            title=payload.name,
            description=payload.description,
            objective=payload.objective,
            status=payload.status,
        )
        return CampaignOut.from_domain(campaign)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{campaign_id}", response_model=CampaignOut)
async def get_campaign(
    campaign_id: str,
    service: CampaignServiceDep,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> CampaignOut:
    """Get a specific campaign."""
    workspace_id = require_workspace_id(x_workspace_id)
    enforce_bcm_ready(workspace_id)

    try:
        UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign_id")

    try:
        campaign = await service.get_campaign(workspace_id, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return CampaignOut.from_domain(campaign)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{campaign_id}", response_model=CampaignOut)
async def update_campaign(
    campaign_id: str,
    updates: CampaignUpdate,
    service: CampaignServiceDep,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> CampaignOut:
    """Update an existing campaign."""
    workspace_id = require_workspace_id(x_workspace_id)
    enforce_bcm_ready(workspace_id)

    try:
        UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign_id")

    try:
        campaign = await service.update_campaign(
            workspace_id=workspace_id,
            campaign_id=campaign_id,
            title=updates.name,
            description=updates.description,
            objective=updates.objective,
            status=updates.status,
        )
        return CampaignOut.from_domain(campaign)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Campaign not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: str,
    service: CampaignServiceDep,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
):
    """Delete a campaign."""
    workspace_id = require_workspace_id(x_workspace_id)
    enforce_bcm_ready(workspace_id)

    try:
        UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign_id")

    try:
        deleted = await service.delete_campaign(workspace_id, campaign_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Campaign not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
