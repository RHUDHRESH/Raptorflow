"""
BCM Context API Endpoints

Provides endpoints for Business Context Manifest (BCM) operations:
- Rebuild manifest from onboarding data
- Retrieve latest manifest
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime
import hashlib
import json

from backend.core.auth import get_current_user
from backend.integration.context_builder import build_business_context_manifest
from backend.memory.controller import MemoryController
from backend.core.supabase_mgr import get_supabase_client

router = APIRouter(
    prefix="/context",
    tags=["context"],
    dependencies=[Depends(get_current_user)]
)

class RebuildRequest(BaseModel):
    workspace_id: str
    force: bool = False

class ManifestResponse(BaseModel):
    manifest: Dict[str, Any]
    version_major: int
    version_minor: int 
    version_patch: int
    checksum: str
    created_at: datetime
    source: str

@router.post("/rebuild")
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
        # Get dependencies
        supabase = get_supabase_client()
        memory_controller = MemoryController()
        
        # Get current version if exists
        current_version = await _get_current_bcm_version(supabase, request.workspace_id)
        
        # Only rebuild if forced or data changed
        if not request.force and not await _has_data_changed(supabase, request.workspace_id, current_version):
            raise HTTPException(status_code=304, detail="BCM unchanged")
        
        # Build new BCM
        bcm = await build_business_context_manifest(
            workspace_id=request.workspace_id,
            db_client=supabase,
            memory_controller=memory_controller,
            version_major=current_version.get("version_major", 1),
            version_minor=current_version.get("version_minor", 0),
            version_patch=current_version.get("version_patch", 0) + 1
        )
        
        # Store in memory tiers
        await memory_controller.store_bcm(request.workspace_id, bcm["content"], "tier0")
        await memory_controller.store_bcm(request.workspace_id, bcm["content"], "tier1")
        await memory_controller.store_bcm(request.workspace_id, bcm["content"], "tier2")
        
        # Store in Supabase
        await supabase.table("business_context_manifests").insert({
            "workspace_id": request.workspace_id,
            "version_major": bcm["version_major"],
            "version_minor": bcm["version_minor"],
            "version_patch": bcm["version_patch"],
            "checksum": bcm["checksum"],
            "content": bcm["content"],
            "created_at": datetime.now().isoformat()
        }).execute()
        
        return ManifestResponse(
            manifest=bcm["content"],
            version_major=bcm["version_major"],
            version_minor=bcm["version_minor"],
            version_patch=bcm["version_patch"],
            checksum=bcm["checksum"],
            created_at=datetime.now(),
            source="api_rebuild"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BCM rebuild failed: {str(e)}")

@router.get("/manifest")
async def get_manifest(workspace_id: str, tier: str = "tier0") -> ManifestResponse:
    """
    Retrieve latest BCM for a workspace
    
    Args:
        workspace_id: Workspace UUID
        tier: Retrieval tier (tier0, tier1, tier2)
    
    Returns:
        ManifestResponse with latest BCM
    """
    try:
        memory_controller = MemoryController()
        supabase = get_supabase_client()
        
        # Try memory first
        bcm = await memory_controller.retrieve_bcm(workspace_id, tier)
        
        if not bcm:
            # Fallback to Supabase
            result = await supabase.table("business_context_manifests") \
                .select("*") \
                .eq("workspace_id", workspace_id) \
                .order("created_at", desc=True) \
                .limit(1) \
                .execute()
                
            if not result.data:
                raise HTTPException(status_code=404, detail="BCM not found")
                
            bcm = result.data[0]
            
            # Cache in memory
            await memory_controller.store_bcm(workspace_id, bcm["content"], tier)
        
        # Verify checksum
        current_checksum = hashlib.sha256(
            json.dumps(bcm["content"], sort_keys=True).encode()
        ).hexdigest()
        
        if current_checksum != bcm["checksum"]:
            raise HTTPException(status_code=422, detail="BCM checksum validation failed")
            
        return ManifestResponse(
            manifest=bcm["content"],
            version_major=bcm["version_major"],
            version_minor=bcm["version_minor"],
            version_patch=bcm["version_patch"],
            checksum=bcm["checksum"],
            created_at=bcm["created_at"],
            source="memory" if "source" not in bcm else bcm["source"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve BCM: {str(e)}")

async def _get_current_bcm_version(supabase, workspace_id: str) -> Dict[str, int]:
    """Get current BCM version if exists"""
    result = await supabase.table("business_context_manifests") \
        .select("version_major,version_minor,version_patch") \
        .eq("workspace_id", workspace_id) \
        .order("created_at", desc=True) \
        .limit(1) \
        .execute()
        
    return result.data[0] if result.data else {}

async def _has_data_changed(supabase, workspace_id: str, current_version: Dict[str, int]) -> bool:
    """Check if underlying data has changed since last BCM build"""
    # Implementation depends on your change detection strategy
    # Could check timestamps, hashes, or specific tables
    return True  # Placeholder - implement based on your needs
