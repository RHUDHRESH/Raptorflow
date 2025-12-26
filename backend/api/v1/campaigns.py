from typing import Any, Dict
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from core.auth import get_current_user
from core.exceptions import RaptorFlowError
from models.campaigns import GanttChart
from models.requests import CampaignCreateRequest, CampaignUpdateRequest
from models.responses import CampaignResponse, BaseResponseModel
from services.campaign_service import CampaignService, get_campaign_service

logger = logging.getLogger("raptorflow.api.campaigns")
router = APIRouter(prefix="/v1/campaigns", tags=["campaigns"])


@router.get("/{campaign_id}/gantt", response_model=GanttChart)
async def get_campaign_gantt(
    campaign_id: str,
    _current_user: dict = Depends(get_current_user),
    service: CampaignService = Depends(get_campaign_service),
):
    """SOTA Endpoint: Retrieves Gantt chart data for a campaign."""
    try:
        gantt = await service.get_gantt_chart(campaign_id)
        if not gantt:
            raise HTTPException(status_code=404, detail="Gantt data not found.")
        return gantt
    except RaptorFlowError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error getting Gantt chart for campaign {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/generate-arc/{campaign_id}")
async def generate_campaign_arc(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    _current_user: dict = Depends(get_current_user),
    service: CampaignService = Depends(get_campaign_service),
):
    """SOTA Endpoint: Triggers agentic inference for a 90-day strategic arc in the background."""
    try:
        # Check if campaign exists
        campaign = await service.get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found.")

        # Run in background
        background_tasks.add_task(service.generate_90_day_arc, campaign_id)

        return {
            "status": "started",
            "campaign_id": campaign_id,
            "message": "90-day arc generation started in background.",
        }
    except RaptorFlowError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error generating arc for campaign {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/generate-arc/{campaign_id}/status")
async def get_campaign_arc_status(
    campaign_id: str,
    _current_user: dict = Depends(get_current_user),
    service: CampaignService = Depends(get_campaign_service),
):
    """SOTA Endpoint: Retrieves status of the agentic inference for a campaign."""
    try:
        result = await service.get_arc_generation_status(campaign_id)
        if not result:
            raise HTTPException(
                status_code=404, detail="Status not found for this campaign."
            )
        return result
    except RaptorFlowError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error getting arc status for campaign {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{campaign_id}/pivot")
async def apply_campaign_pivot(
    campaign_id: str,
    pivot_data: CampaignUpdateRequest,
    _current_user: dict = Depends(get_current_user),
    service: CampaignService = Depends(get_campaign_service),
):
    """SOTA Endpoint: Applies a strategic pivot to a campaign's 90-day arc."""
    try:
        result = await service.apply_pivot(campaign_id, pivot_data.dict(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail="Campaign not found.")
        return result
    except RaptorFlowError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error applying pivot to campaign {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=BaseResponseModel)
async def create_campaign(
    campaign_data: CampaignCreateRequest,
    _current_user: dict = Depends(get_current_user),
    service: CampaignService = Depends(get_campaign_service),
):
    """SOTA Endpoint: Creates a new campaign."""
    try:
        result = await service.create_campaign(campaign_data.dict())
        return BaseResponseModel(
            success=True,
            message="Campaign created successfully",
            data=result
        )
    except RaptorFlowError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error creating campaign: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
