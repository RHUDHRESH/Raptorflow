from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from core.auth import get_current_user
from services.move_service import MoveService, get_move_service

router = APIRouter(prefix="/v1/moves", tags=["moves"])


@router.post("/generate-weekly/{campaign_id}")
async def generate_weekly_moves(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    _current_user: dict = Depends(get_current_user),
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
    campaign_id: str,
    _current_user: dict = Depends(get_current_user),
    service: MoveService = Depends(get_move_service),
):
    """SOTA Endpoint: Retrieves status of move generation."""
    result = await service.get_moves_generation_status(campaign_id)
    if not result:
        raise HTTPException(status_code=404, detail="Status not found.")
    return result


@router.patch("/{move_id}/status")
async def update_move_status(
    move_id: str,
    status_update: Dict[str, Any],
    _current_user: dict = Depends(get_current_user),
    service: MoveService = Depends(get_move_service),
):
    """SOTA Endpoint: Updates the status and result of a specific move."""
    await service.update_move_status(
        move_id, status_update.get("status"), status_update.get("result")
    )
    return {"status": "updated", "move_id": move_id}
