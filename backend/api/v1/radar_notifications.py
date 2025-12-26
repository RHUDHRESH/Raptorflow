"""
Radar Notifications API Endpoints
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from core.auth import get_current_user, get_tenant_id
from services.radar_notification_service import RadarNotificationService

router = APIRouter(prefix="/v1/radar/notifications", tags=["radar-notifications"])


async def get_notification_service():
    return RadarNotificationService()


@router.post("/process", response_model=List[Dict[str, Any]])
async def process_notifications(
    signal_ids: List[str],
    tenant_preferences: Optional[Dict[str, Any]] = None,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarNotificationService = Depends(get_notification_service),
):
    """Process signals and generate notifications."""
    try:
        # In real implementation, fetch signals from database
        mock_signals = []
        notifications = await service.process_signal_notifications(
            mock_signals, tenant_preferences
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
        # In real implementation, fetch signals from database
        mock_signals = []
        digest = await service.create_daily_digest(mock_signals, str(tenant_id))
        return digest
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
