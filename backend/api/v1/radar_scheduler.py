"""
Radar Scheduler API Endpoints
"""

from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from core.auth import get_current_user, get_tenant_id
from models.radar_models import RadarManualScanRequest
from services.radar_scheduler_service import RadarSchedulerService

router = APIRouter(prefix="/v1/radar/scheduler", tags=["radar-scheduler"])


async def get_scheduler_service():
    return RadarSchedulerService()


@router.post("/start", response_model=Dict[str, Any])
async def start_scheduler(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarSchedulerService = Depends(get_scheduler_service),
):
    """Start automated scanning scheduler."""
    try:
        await service.start_scheduler(str(tenant_id))
        return {"status": "started", "tenant_id": str(tenant_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", response_model=Dict[str, Any])
async def stop_scheduler(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarSchedulerService = Depends(get_scheduler_service),
):
    """Stop automated scanning scheduler."""
    try:
        await service.stop_scheduler(str(tenant_id))
        return {"status": "stopped", "tenant_id": str(tenant_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan/manual", response_model=Dict[str, Any])
async def schedule_manual_scan(
    request: RadarManualScanRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarSchedulerService = Depends(get_scheduler_service),
):
    """Schedule a manual scan job."""
    try:
        job = await service.schedule_manual_scan(
            str(tenant_id), request.source_ids, request.scan_type
        )
        return {
            "job_id": job.id,
            "status": job.status,
            "source_count": len(request.source_ids),
            "scan_type": request.scan_type,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=Dict[str, Any])
async def get_source_health(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarSchedulerService = Depends(get_scheduler_service),
):
    """Get health status of all sources."""
    try:
        health = await service.get_source_health(tenant_id=str(tenant_id))
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=Dict[str, Any])
async def get_scheduler_status(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarSchedulerService = Depends(get_scheduler_service),
):
    """Get scheduler status."""
    try:
        status = await service.get_scheduler_status(str(tenant_id))
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
