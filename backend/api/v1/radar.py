from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from core.auth import get_current_user, get_tenant_id
from core.vault import Vault
from models.radar_models import (
    RadarDossierRequest,
    RadarReconRequest,
    RadarSource,
    RadarSourceRequest,
)
from services.radar_repository import RadarRepository
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


@router.get("/signals", response_model=List[Dict[str, Any]])
async def list_signals(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
):
    """List recent radar signals for a tenant."""
    try:
        repository = RadarRepository()
        signals = await repository.fetch_signals(
            str(tenant_id), window_days=90, limit=200
        )
        return [
            {
                "id": signal.id,
                "category": (
                    signal.category.value
                    if hasattr(signal.category, "value")
                    else signal.category
                ),
                "title": signal.title,
                "content": signal.content,
                "strength": (
                    signal.strength.value
                    if hasattr(signal.strength, "value")
                    else signal.strength
                ),
                "freshness": (
                    signal.freshness.value
                    if hasattr(signal.freshness, "value")
                    else signal.freshness
                ),
                "action_suggestion": signal.action_suggestion,
                "source_competitor": signal.source_competitor,
                "source_url": signal.source_url,
                "cluster_id": signal.cluster_id,
                "created_at": signal.created_at.isoformat(),
                "updated_at": signal.updated_at.isoformat(),
                "metadata": signal.metadata,
            }
            for signal in signals
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dossiers", response_model=List[Dict[str, Any]])
async def list_dossiers(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
):
    """List recent radar dossiers for a tenant."""
    try:
        repository = RadarRepository()
        return await repository.fetch_dossiers(str(tenant_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dossiers/{dossier_id}", response_model=Dict[str, Any])
async def get_dossier(
    dossier_id: str,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
):
    """Get a single radar dossier."""
    try:
        repository = RadarRepository()
        dossier = await repository.fetch_dossier(str(tenant_id), dossier_id)
        if not dossier:
            raise HTTPException(status_code=404, detail="Dossier not found")
        return dossier
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources", response_model=List[RadarSource])
async def list_sources(
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
):
    """List radar sources for a tenant."""
    try:
        repository = RadarRepository()
        return await repository.fetch_sources(str(tenant_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sources", response_model=RadarSource)
async def create_source(
    request: RadarSourceRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
):
    """Create a radar source for automated scans."""
    try:
        repository = RadarRepository()
        source = RadarSource(
            tenant_id=str(tenant_id),
            name=request.name,
            type=request.type,
            url=request.url,
            scan_frequency=request.scan_frequency,
            is_active=request.is_active,
            config=request.config,
        )
        return await repository.create_source(source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sources/{source_id}", response_model=Dict[str, Any])
async def delete_source(
    source_id: str,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
):
    """Delete a radar source."""
    try:
        repository = RadarRepository()
        await repository.delete_source(str(tenant_id), source_id)
        return {"status": "deleted", "source_id": source_id}
    except Exception:
        raise HTTPException(status_code=404, detail="Source not found")
