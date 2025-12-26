"""
Radar Notifications API Endpoints
"""

from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from core.auth import get_current_user, get_tenant_id
from models.radar_models import RadarNotificationRequest
from services.radar_notification_service import RadarNotificationService
from services.radar_repository import RadarRepository

router = APIRouter(prefix="/v1/radar/notifications", tags=["radar-notifications"])


async def get_notification_service():
    return RadarNotificationService()


@router.post("/process", response_model=List[Dict[str, Any]])
async def process_notifications(
    request: RadarNotificationRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarNotificationService = Depends(get_notification_service),
):
    """Process signals and generate notifications."""
    try:
        repository = RadarRepository()
        signals = await repository.fetch_signals(
            str(tenant_id), signal_ids=request.signal_ids
        )
        notifications = await service.process_signal_notifications(
            signals, request.tenant_preferences
        )
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/digest/daily", response_model=Dict[str, Any])
async def get_daily_digest(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarNotificationService = Depends(get_notification_service),
):
    """Get daily digest of important signals."""
    try:
        repository = RadarRepository()
        signals = await repository.fetch_signals(str(tenant_id), window_days=1)
        digest = await service.create_daily_digest(signals, str(tenant_id))
        return digest
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
