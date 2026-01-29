"""
BCM API Endpoints

REST API endpoints for Business Context Manifest operations including
creation, retrieval, versioning, and management with comprehensive error handling.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..services.bcm_storage_orchestrator import BCMStorageOrchestrator
from ..integration.bcm_reducer import BusinessContextManifest


# Pydantic models for API requests/responses
class BCMCreateRequest(BaseModel):
    """Request model for BCM creation."""

    workspace_id: str = Field(..., description="Workspace identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    raw_step_data: Dict[str, Any] = Field(..., description="Raw onboarding step data")
    force_rebuild: bool = Field(False, description="Force rebuild even if BCM exists")


class BCMCreateResponse(BaseModel):
    """Response model for BCM creation."""

    success: bool
    bcm: Optional[BusinessContextManifest] = None
    version: Optional[str] = None
    version_type: Optional[str] = None
    reason: Optional[str] = None
    stored_in_redis: bool = False
    stored_in_database: bool = False
    token_count: int = 0
    compression_applied: bool = False
    generation_time_ms: float = 0.0
    workspace_id: str
    user_id: Optional[str] = None
    error: Optional[str] = None


class BCMInfoResponse(BaseModel):
    """Response model for BCM information."""

    workspace_id: str
    has_bcm: bool
    latest_version: Optional[str] = None
    version_count: int = 0
    cache_available: bool = False
    cache_hit_rate: float = 0.0
    database_available: bool = False
    token_count: int = 0
    last_updated: Optional[str] = None
    error: Optional[str] = None


class BCMHealthResponse(BaseModel):
    """Response model for health check."""

    service: str
    components: Dict[str, Any]
    metrics: Dict[str, Any]


class BCMCleanupRequest(BaseModel):
    """Request model for BCM cleanup."""

    workspace_id: str = Field(..., description="Workspace identifier")
    keep_latest: int = Field(5, description="Number of latest versions to keep")


class BCMCleanupResponse(BaseModel):
    """Response model for BCM cleanup."""

    success: bool
    database_deleted: int = 0
    redis_invalidated: int = 0
    total_deleted: int = 0
    error: Optional[str] = None


# Create router
router = APIRouter(prefix="/api/v1/bcm", tags=["bcm"])

# Global service instance (in production, use dependency injection)
bcm_service: Optional[BCMStorageOrchestrator] = None


def get_bcm_service() -> BCMStorageOrchestrator:
    """Get BCM service instance."""
    global bcm_service
    if bcm_service is None:
        # Initialize with environment variables or defaults
        import os

        bcm_service = BCMStorageOrchestrator(
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            supabase_url=os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("SUPABASE_KEY"),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
        )
    return bcm_service


@router.post("/create", response_model=BCMCreateResponse)
async def create_bcm(
    request: BCMCreateRequest,
    service: BCMStorageOrchestrator = Depends(get_bcm_service),
):
    """
    Create a Business Context Manifest from raw onboarding data.

    - **workspace_id**: Workspace identifier
    - **raw_step_data**: Raw onboarding step data from Redis session
    - **user_id**: User identifier (optional)
    - **force_rebuild**: Force rebuild even if BCM exists
    """
    try:
        result = await service.create_bcm(
            raw_step_data=request.raw_step_data,
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            force_rebuild=request.force_rebuild,
        )

        return BCMCreateResponse(**result)

    except Exception as e:
        logging.error(f"Error creating BCM: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workspace_id}", response_model=BusinessContextManifest)
async def get_bcm(
    workspace_id: str = Path(..., description="Workspace identifier"),
    version: Optional[str] = Query(None, description="Specific version to retrieve"),
    use_cache: bool = Query(True, description="Whether to try cache first"),
    service: BCMStorageOrchestrator = Depends(get_bcm_service),
):
    """
    Retrieve a Business Context Manifest.

    - **workspace_id**: Workspace identifier
    - **version**: Specific version to retrieve (optional)
    - **use_cache**: Whether to try cache first
    """
    try:
        bcm = await service.get_bcm(
            workspace_id=workspace_id, version=version, use_cache=use_cache
        )

        if bcm is None:
            raise HTTPException(status_code=404, detail="BCM not found")

        return bcm

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error retrieving BCM: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workspace_id}/info", response_model=BCMInfoResponse)
async def get_bcm_info(
    workspace_id: str = Path(..., description="Workspace identifier"),
    service: BCMStorageOrchestrator = Depends(get_bcm_service),
):
    """
    Get comprehensive BCM information for a workspace.

    - **workspace_id**: Workspace identifier
    """
    try:
        info = service.get_workspace_bcm_info(workspace_id)
        return BCMInfoResponse(**info)

    except Exception as e:
        logging.error(f"Error getting BCM info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workspace_id}/history")
async def get_bcm_history(
    workspace_id: str = Path(..., description="Workspace identifier"),
    limit: int = Query(10, description="Maximum number of versions to return"),
    service: BCMStorageOrchestrator = Depends(get_bcm_service),
):
    """
    Get version history for a workspace's BCM.

    - **workspace_id**: Workspace identifier
    - **limit**: Maximum number of versions to return
    """
    try:
        history = service.database_storage.get_bcm_history(workspace_id, limit)
        return {
            "workspace_id": workspace_id,
            "history": history,
            "total_count": len(history),
        }

    except Exception as e:
        logging.error(f"Error getting BCM history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workspace_id}/versions")
async def get_bcm_versions(
    workspace_id: str = Path(..., description="Workspace identifier"),
    service: BCMStorageOrchestrator = Depends(get_bcm_service),
):
    """
    Get all available versions for a workspace's BCM.

    - **workspace_id**: Workspace identifier
    """
    try:
        # Get all versions from database
        result = (
            service.database_storage.client.table("business_context_manifests")
            .select("version_string", "created_at", "updated_at")
            .eq("workspace_id", workspace_id)
            .order("created_at", desc=True)
            .execute()
        )

        return {
            "workspace_id": workspace_id,
            "versions": result.data if result.data else [],
            "total_count": len(result.data) if result.data else 0,
        }

    except Exception as e:
        logging.error(f"Error getting BCM versions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workspace_id}/cleanup", response_model=BCMCleanupResponse)
async def cleanup_bcm(
    workspace_id: str = Path(..., description="Workspace identifier"),
    request: BCMCleanupRequest = None,
    keep_latest: int = Query(5, description="Number of latest versions to keep"),
    service: BCMStorageOrchestrator = Depends(get_bcm_service),
):
    """
    Clean up old BCM versions for a workspace.

    - **workspace_id**: Workspace identifier
    - **keep_latest**: Number of latest versions to keep
    """
    try:
        # Use request body if provided, otherwise use query parameter
        versions_to_keep = request.keep_latest if request else keep_latest

        result = service.cleanup_workspace(workspace_id, versions_to_keep)
        return BCMCleanupResponse(**result)

    except Exception as e:
        logging.error(f"Error cleaning up BCM: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{workspace_id}")
async def delete_bcm(
    workspace_id: str = Path(..., description="Workspace identifier"),
    version: Optional[str] = Query(None, description="Specific version to delete"),
    service: BCMStorageOrchestrator = Depends(get_bcm_service),
):
    """
    Delete BCM from database.

    - **workspace_id**: Workspace identifier
    - **version**: Specific version to delete (optional)
    """
    try:
        success = service.database_storage.delete_bcm(workspace_id, version)

        if not success:
            raise HTTPException(
                status_code=404, detail="BCM not found or deletion failed"
            )

        # Also invalidate from Redis
        service.redis_storage.invalidate_bcm(workspace_id)

        return {
            "success": True,
            "message": f"BCM deleted for workspace {workspace_id}",
            "version": version,
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting BCM: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workspace_id}/export")
async def export_bcm(
    workspace_id: str = Path(..., description="Workspace identifier"),
    format_type: str = Query("json", description="Export format (json, yaml, csv)"),
    service: BCMStorageOrchestrator = Depends(get_bcm_service),
):
    """
    Export BCM in specified format.

    - **workspace_id**: Workspace identifier
    - **format_type**: Export format (json, yaml, csv)
    """
    try:
        exported_data = service.export_bcm(workspace_id, format_type)

        if exported_data is None:
            raise HTTPException(status_code=404, detail="BCM not found")

        # Return appropriate content type
        if format_type == "json":
            return JSONResponse(
                content=json.loads(exported_data), media_type="application/json"
            )
        else:
            return JSONResponse(
                content={"data": exported_data, "format": format_type},
                media_type="application/json",
            )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error exporting BCM: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{workspace_id}/validate")
async def validate_bcm(
    workspace_id: str = Path(..., description="Workspace identifier"),
    service: BCMStorageOrchestrator = Depends(get_bcm_service),
):
    """
    Validate BCM structure and content.

    - **workspace_id**: Workspace identifier
    """
    try:
        bcm = await service.get_bcm(workspace_id)

        if bcm is None:
            raise HTTPException(status_code=404, detail="BCM not found")

        validation = service.validate_bcm(bcm)
        return validation

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error validating BCM: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=BCMHealthResponse)
async def health_check(service: BCMStorageOrchestrator = Depends(get_bcm_service)):
    """
    Perform comprehensive health check on all BCM components.
    """
    try:
        health = service.health_check()
        return BCMHealthResponse(**health)

    except Exception as e:
        logging.error(f"Error during health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics(service: BCMStorageOrchestrator = Depends(get_bcm_service)):
    """
    Get comprehensive service metrics.
    """
    try:
        metrics = service.get_service_metrics()
        return metrics

    except Exception as e:
        logging.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workspaces")
async def list_workspaces_with_bcm(
    service: BCMStorageOrchestrator = Depends(get_bcm_service),
):
    """
    List all workspaces that have BCMs stored.
    """
    try:
        workspaces = service.database_storage.list_workspaces_with_bcm()
        return {"workspaces": workspaces, "total_count": len(workspaces)}

    except Exception as e:
        logging.error(f"Error listing workspaces: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-create")
async def batch_create_bcms(
    workspace_data: List[BCMCreateRequest],
    service: BCMStorageOrchestrator = Depends(get_bcm_service),
):
    """
    Create multiple BCMs in batch.

    - **workspace_data**: List of workspace data dictionaries
    """
    try:
        # Convert requests to the format expected by the service
        batch_data = []
        for request in workspace_data:
            batch_data.append(
                {
                    "workspace_id": request.workspace_id,
                    "raw_step_data": request.raw_step_data,
                    "user_id": request.user_id,
                }
            )

        results = await service.batch_create_bcms(batch_data)

        return {
            "success": True,
            "results": results,
            "total_processed": len(results),
            "successful": sum(1 for r in results if r.get("success", False)),
        }

    except Exception as e:
        logging.error(f"Error in batch BCM creation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workspace_id}/integrity")
async def verify_integrity(
    workspace_id: str = Path(..., description="Workspace identifier"),
    service: BCMStorageOrchestrator = Depends(get_bcm_service),
):
    """
    Verify data integrity for all BCM versions in a workspace.

    - **workspace_id**: Workspace identifier
    """
    try:
        integrity = service.database_storage.verify_data_integrity(workspace_id)
        return integrity

    except Exception as e:
        logging.error(f"Error verifying data integrity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logging.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
