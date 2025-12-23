from fastapi import APIRouter, Depends, HTTPException
from backend.services.campaign_service import CampaignService, get_campaign_service
from backend.models.campaigns import GanttChart

router = APIRouter(prefix="/v1/campaigns", tags=["campaigns"])

@router.get("/{campaign_id}/gantt", response_model=GanttChart)
async def get_campaign_gantt(
    campaign_id: str,
    service: CampaignService = Depends(get_campaign_service)
):
    """SOTA Endpoint: Retrieves Gantt chart data for a campaign."""
    gantt = await service.get_gantt_chart(campaign_id)
    if not gantt:
        raise HTTPException(status_code=404, detail="Gantt data not found.")
    return gantt
