from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from typing import Any, Dict

from backend.services.move_service import MoveService, get_move_service

router = APIRouter(prefix="/v1/moves", tags=["moves"])


@router.post("/generate-weekly/{campaign_id}")
async def generate_weekly_moves(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    service: MoveService = Depends(get_move_service),
):
    """SOTA Endpoint: Triggers agentic move generation for a campaign."""
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found.")

    background_tasks.add_task(service.generate_weekly_moves, campaign_id)

    return {
        "status": "started",
        "campaign_id": campaign_id,
        "message": "Weekly move generation started in background.",
    }


@router.get("/generate-weekly/{campaign_id}/status")
async def get_moves_status(
    campaign_id: str, service: MoveService = Depends(get_move_service)
):
    """SOTA Endpoint: Retrieves status of move generation."""
    result = await service.get_moves_generation_status(campaign_id)
    if not result:
        raise HTTPException(status_code=404, detail="Status not found.")
    return result
