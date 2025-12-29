from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from core.auth import get_current_user, get_tenant_id
from core.cache import get_cache_manager
from core.vault import Vault
from models.radar_models import (
    RadarDossierRequest,
    RadarReconRequest,
    RadarSource,
    RadarSourceRequest,
    Signal,
    SignalResponse,
)
from services.radar_repository import RadarRepository
from services.radar_service import RadarService

router = APIRouter(prefix="/v1/radar", tags=["radar"])


async def get_radar_service():
    vault = Vault()
    return RadarService(vault)


async def get_cached_signals(cache_key: str):
    """Get cached signals or None if not found."""
    cache = get_cache_manager()
    return cache.get_json(cache_key)


async def set_cached_signals(
    cache_key: str, data: List[Dict[str, Any]], ttl: int = 300
):
    """Set cached signals."""
    cache = get_cache_manager()
    cache.set_json(cache_key, data, expiry_seconds=ttl)


@router.post("/scan/recon", response_model=List[SignalResponse])
async def scan_recon(
    request: RadarReconRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarService = Depends(get_radar_service),
):
    """Performs a competitive signals scan."""
    try:
        signals = await service.scan_recon(
            str(tenant_id), request.icp_id, request.source_urls
        )
        # Convert to SignalResponse format with all required fields
        response = [
            SignalResponse(
                id=signal["id"],
                tenant_id=signal["tenant_id"],
                category=signal["category"],
                title=signal["title"],
                content=signal["content"],
                strength=signal["strength"],
                freshness=signal["freshness"],
                evidence_count=len(signal.get("evidence", [])),
                action_suggestion=signal.get("action_suggestion"),
                source_competitor=signal.get("source_competitor"),
                cluster_id=signal.get("cluster_id"),
                created_at=signal["created_at"],
                updated_at=signal["updated_at"],
            )
            for signal in signals
        ]

        # Cache recent signals for 5 minutes
        cache_key = f"radar:{tenant_id}:signals:recent"
        await set_cached_signals(cache_key, [s.model_dump() for s in response], ttl=300)

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recon scan failed: {str(e)}")


@router.post("/scan/dossier", response_model=Dict[str, Any])
async def scan_dossier(
    request: RadarDossierRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    service: RadarService = Depends(get_radar_service),
):
    """Generates deep competitor dossiers with comprehensive intelligence."""
    try:
        dossier = await service.generate_dossier(
            str(tenant_id), request.campaign_id, request.signal_ids
        )
        # Ensure all required dossier fields are present
        response = {
            "id": dossier.get("id"),
            "tenant_id": dossier.get("tenant_id"),
            "campaign_id": dossier.get("campaign_id"),
            "title": dossier.get("title", "Competitive Intelligence Dossier"),
            "summary": dossier.get("summary", []),
            "pinned_signals": dossier.get("pinned_signals", []),
            "hypotheses": dossier.get("hypotheses", []),
            "recommended_experiments": dossier.get("recommended_experiments", []),
            "copy_snippets": dossier.get("copy_snippets", []),
            "market_narrative": dossier.get("market_narrative", {}),
            "created_at": dossier.get("created_at"),
            "updated_at": dossier.get("updated_at"),
            "is_published": dossier.get("is_published", False),
        }

        # Cache dossier for 10 minutes
        cache_key = f"radar:{tenant_id}:dossier:{request.campaign_id}"
        cache = get_cache_manager()
        cache.set_json(cache_key, response, expiry_seconds=600)

        return response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Dossier generation failed: {str(e)}"
        )


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
