from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from backend.core.auth import get_current_user, get_tenant_id
from backend.core.vault import Vault
from backend.services.radar_service import RadarService

router = APIRouter(prefix="/v1/radar", tags=["radar"])


async def get_radar_service():
    vault = Vault()
    return RadarService(vault)


@router.post("/scan/recon", response_model=List[Dict[str, Any]])
async def scan_recon(
    icp_id: str,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarService = Depends(get_radar_service),
):
    """Performs a competitive signals scan."""
    try:
        return await service.scan_recon(icp_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan/dossier", response_model=List[Dict[str, Any]])
async def scan_dossier(
    icp_id: str,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarService = Depends(get_radar_service),
):
    """Generates deep competitor dossiers."""
    try:
        return await service.generate_dossier(icp_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
