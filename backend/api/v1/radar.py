from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from backend.services.radar_service import RadarService
from backend.core.vault import Vault

router = APIRouter(prefix="/v1/radar", tags=["radar"])

async def get_radar_service():
    vault = Vault()
    # Assuming Vault doesn't need async initialize if not present in other files
    # or handle it if it does.
    return RadarService(vault)

@router.post("/scan/recon", response_model=List[Dict[str, Any]])
async def scan_recon(icp_id: str, service: RadarService = Depends(get_radar_service)):
    """Performs a competitive signals scan."""
    try:
        return await service.scan_recon(icp_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scan/dossier", response_model=List[Dict[str, Any]])
async def scan_dossier(icp_id: str, service: RadarService = Depends(get_radar_service)):
    """Generates deep competitor dossiers."""
    try:
        return await service.generate_dossier(icp_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
