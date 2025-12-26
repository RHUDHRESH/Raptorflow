from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from core.auth import get_current_user, get_tenant_id
from core.vault import Vault
from models.radar_models import RadarDossierRequest, RadarReconRequest
from services.radar_service import RadarService

router = APIRouter(prefix="/v1/radar", tags=["radar"])


async def get_radar_service():
    vault = Vault()
    return RadarService(vault)


@router.post("/scan/recon", response_model=List[Dict[str, Any]])
async def scan_recon(
    request: RadarReconRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarService = Depends(get_radar_service),
):
    """Performs a competitive signals scan."""
    try:
        return await service.scan_recon(
            str(tenant_id), request.icp_id, request.source_urls
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan/dossier", response_model=Dict[str, Any])
async def scan_dossier(
    request: RadarDossierRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarService = Depends(get_radar_service),
):
    """Generates deep competitor dossiers."""
    try:
        return await service.generate_dossier(
            str(tenant_id), request.campaign_id, request.signal_ids
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
