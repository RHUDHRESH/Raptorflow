"""
BCM Context API Endpoints

Provides endpoints for Business Context Manifest (BCM) operations:
- Rebuild manifest from onboarding data
- Retrieve latest manifest
- Get version history
- Export manifest
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime
import hashlib
import json
import logging

from ..core.auth import get_current_user
from ..services.bcm_service import BCMService
from ..services.supabase_client import get_supabase_admin

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/context", tags=["context"], dependencies=[Depends(get_current_user)]
)


class RebuildRequest(BaseModel):
    workspace_id: str
    force: bool = False


class ManifestResponse(BaseModel):
    success: bool
    manifest: Optional[Dict[str, Any]] = None
    version: Optional[str] = None
    checksum: Optional[str] = None
    generated_at: Optional[datetime] = None
    source: str
    error: Optional[str] = None


class VersionHistoryResponse(BaseModel):
    success: bool
    versions: List[Dict[str, Any]]
    total_count: int


@router.post("/rebuild", response_model=ManifestResponse)
async def rebuild_bcm(request: RebuildRequest):
    """
    Trigger BCM recomputation from onboarding data

    Args:
        workspace_id: Workspace UUID
        force: If True, forces rebuild even if data unchanged

    Returns:
        ManifestResponse with new BCM
    """
    try:
        # Initialize BCM service
        bcm_service = BCMService()

        # Validate workspace access
        supabase = get_supabase_admin()
        workspace = (
            supabase.table("workspaces")
            .select("owner_id")
            .eq("id", request.workspace_id)
            .single()
            .execute()
        )
        if not workspace.data:
            raise HTTPException(status_code=404, detail="Workspace not found")

        # Rebuild BCM
        result = await bcm_service.rebuild_manifest(request.workspace_id, request.force)

        if result.get("success"):
            return ManifestResponse(
                success=True,
                manifest=result.get("bcm"),
                version="1.0.0",  # Would be calculated from actual version
                checksum=result.get("checksum"),
                generated_at=(
                    datetime.fromisoformat(result.get("generated_at"))
                    if result.get("generated_at")
                    else None
                ),
                source="api_rebuild",
            )
        else:
            return ManifestResponse(
                success=False,
                source="api_rebuild",
                error=result.get("reason", "Unknown error"),
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"BCM rebuild failed: {e}")
        raise HTTPException(status_code=500, detail=f"BCM rebuild failed: {str(e)}")


@router.get("/manifest", response_model=ManifestResponse)
async def get_manifest(
    workspace_id: str = Query(...),
    tier: str = Query("tier0", regex="^(tier0|tier1|tier2)$"),
    use_fallback: bool = Query(True),
):
    """
    Retrieve latest BCM for a workspace

    Args:
        workspace_id: Workspace UUID
        tier: Retrieval tier (tier0, tier1, tier2)
        use_fallback: Whether to fallback to database on cache miss

    Returns:
        ManifestResponse with latest BCM
    """
    try:
        # Initialize BCM service
        bcm_service = BCMService()

        # Validate workspace access
        supabase = get_supabase_admin()
        workspace = (
            supabase.table("workspaces")
            .select("owner_id")
            .eq("id", workspace_id)
            .single()
            .execute()
        )
        if not workspace.data:
            raise HTTPException(status_code=404, detail="Workspace not found")

        # Get manifest
        manifest = await bcm_service.get_latest_manifest(workspace_id, use_fallback)

        if manifest:
            # Verify checksum
            current_checksum = hashlib.sha256(
                json.dumps(manifest, sort_keys=True).encode()
            ).hexdigest()

            stored_checksum = manifest.get("checksum")
            if stored_checksum and current_checksum != stored_checksum:
                logger.warning(f"BCM checksum mismatch for workspace {workspace_id}")

            return ManifestResponse(
                success=True,
                manifest=manifest,
                version=manifest.get("version", "1.0.0"),
                checksum=manifest.get("checksum"),
                generated_at=(
                    datetime.fromisoformat(manifest.get("generated_at"))
                    if manifest.get("generated_at")
                    else None
                ),
                source=f"cache_{tier}" if use_fallback else "cache_only",
            )
        else:
            return ManifestResponse(
                success=False, source="cache", error="BCM not found"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve BCM: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve BCM: {str(e)}")


@router.get("/history", response_model=VersionHistoryResponse)
async def get_version_history(
    workspace_id: str = Query(...), limit: int = Query(10, ge=1, le=100)
):
    """
    Get version history for BCM

    Args:
        workspace_id: Workspace UUID
        limit: Maximum number of versions to return

    Returns:
        VersionHistoryResponse with version list
    """
    try:
        # Initialize BCM service
        bcm_service = BCMService()

        # Validate workspace access
        supabase = get_supabase_admin()
        workspace = (
            supabase.table("workspaces")
            .select("owner_id")
            .eq("id", workspace_id)
            .single()
            .execute()
        )
        if not workspace.data:
            raise HTTPException(status_code=404, detail="Workspace not found")

        # Get version history
        versions = await bcm_service.get_version_history(workspace_id, limit)

        return VersionHistoryResponse(
            success=True, versions=versions, total_count=len(versions)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get version history: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get version history: {str(e)}"
        )


@router.get("/export")
async def export_manifest(
    workspace_id: str = Query(...),
    format: str = Query("json", regex="^(json|markdown)$"),
):
    """
    Export BCM in specified format

    Args:
        workspace_id: Workspace UUID
        format: Export format (json or markdown)

    Returns:
        StreamingResponse with exported data
    """
    try:
        # Initialize BCM service
        bcm_service = BCMService()

        # Validate workspace access
        supabase = get_supabase_admin()
        workspace = (
            supabase.table("workspaces")
            .select("owner_id")
            .eq("id", workspace_id)
            .single()
            .execute()
        )
        if not workspace.data:
            raise HTTPException(status_code=404, detail="Workspace not found")

        # Export manifest
        export_data = await bcm_service.export_manifest(workspace_id, format)

        # Set appropriate content type
        content_type = "application/json" if format == "json" else "text/markdown"
        filename = (
            f"bcm_{workspace_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        )

        return StreamingResponse(
            iter([export_data]),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export BCM: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export BCM: {str(e)}")


@router.get("/stats")
async def get_cache_stats(workspace_id: str = Query(None)):
    """
    Get cache statistics

    Args:
        workspace_id: Optional workspace ID for specific stats

    Returns:
        Cache statistics
    """
    try:
        # Initialize BCM service
        bcm_service = BCMService()

        # Get cache stats
        stats = bcm_service.get_cache_stats()

        # If workspace specified, add workspace-specific info
        if workspace_id:
            # Validate workspace access
            supabase = get_supabase_admin()
            workspace = (
                supabase.table("workspaces")
                .select("owner_id")
                .eq("id", workspace_id)
                .single()
                .execute()
            )
            if workspace.data:
                # Add workspace-specific stats
                manifest = await bcm_service.get_latest_manifest(
                    workspace_id, use_fallback=False
                )
                stats["workspace_cached"] = manifest is not None
            else:
                stats["workspace_cached"] = False

        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get cache stats: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Perform health check on BCM components

    Returns:
        Health status of all components
    """
    try:
        # Initialize BCM service
        bcm_service = BCMService()

        # Get health status
        health = bcm_service.health_check()

        return {
            "success": True,
            "health": health,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
