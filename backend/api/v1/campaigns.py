from typing import Any, Dict, List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status


from backend.models.campaigns import GanttChart
from backend.services.campaign_service import CampaignService, get_campaign_service

router = APIRouter(prefix="/v1/campaigns", tags=["campaigns"])


@router.get("/{campaign_id}/gantt", response_model=GanttChart)
async def get_campaign_gantt(
    campaign_id: str, service: CampaignService = Depends(get_campaign_service)
):
    """SOTA Endpoint: Retrieves Gantt chart data for a campaign."""
    gantt = await service.get_gantt_chart(campaign_id)
    if not gantt:
        raise HTTPException(status_code=404, detail="Gantt data not found.")
    return gantt


@router.post("/generate-arc/{campaign_id}")
async def generate_campaign_arc(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    service: CampaignService = Depends(get_campaign_service),
):
    """SOTA Endpoint: Triggers agentic inference for a 90-day strategic arc in the background."""
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


@router.get("/generate-arc/{campaign_id}/status")
async def get_campaign_arc_status(
    campaign_id: str, service: CampaignService = Depends(get_campaign_service)
):
    """SOTA Endpoint: Retrieves status of the agentic inference for a campaign."""
    result = await service.get_arc_generation_status(campaign_id)
    if not result:
        raise HTTPException(status_code=404, detail="Status not found for this campaign.")
    return result


@router.post("/{campaign_id}/pivot")
async def apply_campaign_pivot(
    campaign_id: str,
    pivot_data: Dict[str, Any],
    service: CampaignService = Depends(get_campaign_service),
):
    """SOTA Endpoint: Applies a strategic pivot to a campaign's 90-day arc."""
    result = await service.apply_pivot(campaign_id, pivot_data)
    if not result:
        raise HTTPException(status_code=404, detail="Campaign not found.")
    return result
