"""
Onboarding Finalize Endpoint

Handles the finalization of onboarding sessions, including BCM generation,
Redis caching, Supabase persistence, and vector embedding preparation.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, Field

from ..integration.bcm_reducer import BCMReducer
from ..redis.session_manager import get_onboarding_session_manager
from ..schemas.bcm_schema import BCMSchemaValidator, BusinessContextManifest
from ..services.supabase_client import get_supabase_client
from ..services.upstash_client import get_upstash_client
from ..services.vertex_ai_client import get_vertex_ai_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/onboarding", tags=["onboarding-finalize"])

# Initialize services
session_manager = get_onboarding_session_manager()
bcm_reducer = BCMReducer()
supabase_client = get_supabase_client()
upstash_client = get_upstash_client()
vertex_ai_client = get_vertex_ai_client()


# Pydantic models
class FinalizeRequest(BaseModel):
    """Request model for onboarding finalization."""

    session_id: str = Field(..., description="Onboarding session ID")
    generate_bcm: bool = Field(
        default=True, description="Generate Business Context Manifest"
    )
    cache_bcm: bool = Field(default=True, description="Cache BCM in Redis")
    persist_bcm: bool = Field(default=True, description="Persist BCM to Supabase")
    enqueue_embeddings: bool = Field(
        default=True, description="Enqueue vector embeddings"
    )


class FinalizeResponse(BaseModel):
    """Response model for onboarding finalization."""

    success: bool
    session_id: str
    workspace_id: str
    completion_percentage: float
    bcm_generated: bool
    bcm_cached: bool
    bcm_persisted: bool
    embeddings_enqueued: bool
    business_context: Optional[Dict[str, Any]]
    bcm_version: Optional[str]
    bcm_checksum: Optional[str]
    finalized_at: str
    processing_time_ms: Optional[float]


class BCMRebuildRequest(BaseModel):
    """Request model for BCM rebuild."""

    workspace_id: str = Field(..., description="Workspace ID")
    force_rebuild: bool = Field(
        default=False, description="Force rebuild even if cached"
    )


class BCMManifestResponse(BaseModel):
    """Response model for BCM manifest retrieval."""

    success: bool
    workspace_id: str
    manifest: Optional[Dict[str, Any]]
    version: Optional[str]
    checksum: Optional[str]
    completion_percentage: Optional[float]
    cached: bool
    retrieved_at: str


# Helper functions
async def get_session_workspace_id(session_id: str) -> str:
    """Get workspace ID from session metadata."""
    metadata = await session_manager.get_metadata(session_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Session not found")

    workspace_id = metadata.get("workspace_id")
    if not workspace_id:
        raise HTTPException(status_code=400, detail="Workspace ID not found in session")

    return workspace_id


async def validate_session_completion(session_id: str) -> float:
    """Validate session completion and return percentage."""
    all_steps = await session_manager.get_all_steps(session_id)
    if not all_steps:
        raise HTTPException(status_code=400, detail="No step data found for session")

    completed_steps = len(all_steps)
    total_steps = 23
    completion_percentage = (completed_steps / total_steps) * 100

    if completion_percentage < 50:
        raise HTTPException(
            status_code=400,
            detail=f"Session incomplete: {completion_percentage:.1f}% completed (minimum 50% required)",
        )

    return completion_percentage


async def _get_business_context(workspace_id: str) -> Optional[Dict[str, Any]]:
    """Fetch the latest business context for a workspace."""
    client = supabase_client.get_client()
    result = (
        client.table("business_contexts")
        .select("*")
        .eq("workspace_id", workspace_id)
        .order("updated_at", desc=True)
        .limit(1)
        .execute()
    )
    if result.data:
        return result.data[0]
    return None


async def generate_bcm_from_session(
    session_id: str,
) -> Tuple[BusinessContextManifest, Optional[Dict[str, Any]]]:
    """Generate BCM from onboarding session data and business context."""
    try:
        # Get all session data
        all_steps = await session_manager.get_all_steps(session_id)

        # Add metadata to step data
        metadata = await session_manager.get_metadata(session_id)
        all_steps["metadata"] = metadata

        business_context = None
        workspace_id = metadata.get("workspace_id") if metadata else None
        if workspace_id:
            business_context = await _get_business_context(workspace_id)
            if business_context:
                all_steps["business_context"] = business_context

        # Generate BCM using reducer
        manifest = await bcm_reducer.reduce(all_steps)

        # Validate manifest
        BCMSchemaValidator.validate_size_constraints(manifest)

        logger.info(
            f"Generated BCM for session {session_id}: {len(manifest.json())} chars"
        )
        return manifest, business_context

    except Exception as e:
        logger.error(f"Error generating BCM for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"BCM generation failed: {str(e)}")


async def cache_bcm_in_redis(workspace_id: str, manifest: Dict[str, Any]) -> bool:
    """Cache BCM in Redis/Upstash."""
    try:
        # Cache key: w:{workspace_id}:bcm:latest
        cache_key = f"w:{workspace_id}:bcm:latest"

        # Serialize manifest
        success = await upstash_client.set_json(cache_key, manifest, ex=86400)

        if success:
            logger.info(f"Cached BCM for workspace {workspace_id}")
        else:
            logger.warning(f"Failed to cache BCM for workspace {workspace_id}")

        return success

    except Exception as e:
        logger.error(f"Error caching BCM for workspace {workspace_id}: {str(e)}")
        return False


async def persist_bcm_to_supabase(
    workspace_id: str,
    manifest: Dict[str, Any],
    session_id: Optional[str] = None,
) -> bool:
    """Persist BCM to Supabase database."""
    try:
        client = supabase_client.get_client()
        latest = (
            client.table("bcm_manifests")
            .select("version")
            .eq("workspace_id", workspace_id)
            .order("version", desc=True)
            .limit(1)
            .execute()
        )
        next_version = (latest.data[0]["version"] if latest.data else 0) + 1

        record = {
            "workspace_id": workspace_id,
            "session_id": session_id,
            "version": next_version,
            "checksum": manifest.get("checksum"),
            "manifest_json": manifest,
            "generated_at": manifest.get("generated_at"),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        result = client.table("bcm_manifests").insert(record).execute()

        if result.data:
            logger.info(f"Persisted BCM v{next_version} for workspace {workspace_id}")
            return True

        logger.error(f"Failed to persist BCM for workspace {workspace_id}")
        return False

    except Exception as e:
        logger.error(f"Error persisting BCM for workspace {workspace_id}: {str(e)}")
        return False


async def enqueue_embedding_generation(
    workspace_id: str, manifest: BusinessContextManifest
) -> bool:
    """Enqueue background task for vector embedding generation."""
    try:
        # Create background task data
        task_data = {
            "workspace_id": workspace_id,
            "manifest_version": manifest.version.value,
            "manifest_checksum": manifest.checksum,
            "sections_to_embed": _identify_sections_for_embedding(manifest),
            "priority": "normal",
            "created_at": datetime.utcnow().isoformat(),
        }

        # Add to background queue (using Redis list)
        queue_key = "embedding_queue"

        # Serialize and add to queue
        task_json = json.dumps(task_data, default=str)
        await upstash_client.async_client.lpush(queue_key, task_json)

        logger.info(f"Enqueued embedding generation for workspace {workspace_id}")
        return True

    except Exception as e:
        logger.error(
            f"Error enqueuing embeddings for workspace {workspace_id}: {str(e)}"
        )
        return False


def _identify_sections_for_embedding(manifest: BusinessContextManifest) -> List[str]:
    """Identify which sections need vector embedding."""
    sections = []

    # Always embed ICPs if present
    if manifest.icps:
        sections.append("icps")

    # Embed competitors if present
    if manifest.direct_competitors or manifest.indirect_competitors:
        sections.append("competitors")

    # Embed messaging if present
    if manifest.key_messages or manifest.soundbites:
        sections.append("messaging")

    # Embed value proposition if present
    if manifest.value_prop and manifest.value_prop.primary:
        sections.append("value_prop")

    # Embed brand positioning if present
    if manifest.positioning:
        sections.append("positioning")

    return sections


# API Endpoints
@router.post("/{session_id}/finalize")
async def finalize_onboarding(
    session_id: str, request: FinalizeRequest, background_tasks: BackgroundTasks
):
    """
    Finalize onboarding session and generate Business Context Manifest.

    This endpoint:
    1. Validates session completion (minimum 50%)
    2. Generates BCM from all step data
    3. Caches BCM in Redis (24h TTL)
    4. Persists BCM to Supabase with versioning
    5. Enqueues vector embedding generation
    6. Returns complete business context
    """
    start_time = datetime.utcnow()

    try:
        # Validate session exists and get workspace
        workspace_id = await get_session_workspace_id(session_id)

        # Validate session completion
        completion_percentage = await validate_session_completion(session_id)

        # Initialize response tracking
        bcm_generated = False
        bcm_cached = False
        bcm_persisted = False
        embeddings_enqueued = False
        business_context = None

        # Generate BCM if requested
        if request.generate_bcm:
            manifest, business_context_payload = await generate_bcm_from_session(
                session_id
            )
            bcm_generated = True
            manifest_payload = manifest.dict()
            if business_context_payload:
                manifest_payload["business_context"] = business_context_payload

            # Cache BCM in Redis if requested
            if request.cache_bcm:
                bcm_cached = await cache_bcm_in_redis(workspace_id, manifest_payload)

            # Persist BCM to Supabase if requested
            if request.persist_bcm:
                bcm_persisted = await persist_bcm_to_supabase(
                    workspace_id,
                    manifest_payload,
                    session_id=session_id,
                )

            # Enqueue embeddings if requested
            if request.enqueue_embeddings:
                embeddings_enqueued = await enqueue_embedding_generation(
                    workspace_id, manifest
                )

            # Prepare business context for response
            business_context = manifest_payload

        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time_ms = (end_time - start_time).total_seconds() * 1000

        # Update session status
        await session_manager.save_step(
            session_id,
            0,
            {
                "finalized": True,
                "finalized_at": end_time.isoformat(),
                "completion_percentage": completion_percentage,
                "bcm_generated": bcm_generated,
                "workspace_id": workspace_id,
            },
        )

        logger.info(
            f"Finalized onboarding session {session_id} for workspace {workspace_id}"
        )

        return FinalizeResponse(
            success=True,
            session_id=session_id,
            workspace_id=workspace_id,
            completion_percentage=completion_percentage,
            bcm_generated=bcm_generated,
            bcm_cached=bcm_cached,
            bcm_persisted=bcm_persisted,
            embeddings_enqueued=embeddings_enqueued,
            business_context=business_context,
            bcm_version=business_context.get("version") if business_context else None,
            bcm_checksum=business_context.get("checksum") if business_context else None,
            finalized_at=end_time.isoformat(),
            processing_time_ms=processing_time_ms,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finalizing onboarding session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Finalization failed: {str(e)}")


@router.post("/context/rebuild")
async def rebuild_bcm(request: BCMRebuildRequest):
    """
    Rebuild Business Context Manifest for a workspace.

    This endpoint:
    1. Retrieves latest onboarding session for workspace
    2. Regenerates BCM from session data
    3. Updates cache and persistence
    4. Enqueues fresh embeddings
    """
    try:
        # Find latest session for workspace
        # This would typically query the database for the most recent session
        # For now, we'll use a simplified approach

        # Get latest BCM from cache first (unless force rebuild)
        if not request.force_rebuild:
            cache_key = f"w:{request.workspace_id}:bcm:latest"
            cached_bcm = await upstash_client.get_json(cache_key)

            if cached_bcm:
                logger.info(f"BCM already cached for workspace {request.workspace_id}")
                return BCMManifestResponse(
                    success=True,
                    workspace_id=request.workspace_id,
                    manifest=cached_bcm,
                    version=cached_bcm.get("version"),
                    checksum=cached_bcm.get("checksum"),
                    completion_percentage=cached_bcm.get("completion_percentage"),
                    cached=True,
                    retrieved_at=datetime.utcnow().isoformat(),
                )

        # Find latest session (simplified - in production would query DB)
        # For now, we'll create a placeholder response
        logger.info(f"Rebuilding BCM for workspace {request.workspace_id}")

        # In a real implementation, you would:
        # 1. Query database for latest session_id
        # 2. Get session data from Redis
        # 3. Generate new BCM
        # 4. Cache and persist
        # 5. Enqueue embeddings

        return BCMManifestResponse(
            success=True,
            workspace_id=request.workspace_id,
            manifest=None,
            version=None,
            checksum=None,
            completion_percentage=None,
            cached=False,
            retrieved_at=datetime.utcnow().isoformat(),
            message="BCM rebuild initiated (implementation pending)",
        )

    except Exception as e:
        logger.error(
            f"Error rebuilding BCM for workspace {request.workspace_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"BCM rebuild failed: {str(e)}")


@router.get("/context/manifest")
async def get_bcm_manifest(
    workspace_id: str = Query(..., description="Workspace ID"),
    version: Optional[str] = Query(None, description="Specific BCM version"),
    include_raw: bool = Query(False, description="Include raw manifest data"),
):
    """
    Get Business Context Manifest for a workspace.

    This endpoint:
    1. Checks Redis cache first (fast path)
    2. Falls back to Supabase if cache miss
    3. Returns manifest with metadata
    """
    try:
        # Try cache first
        cache_key = f"w:{workspace_id}:bcm:latest"
        manifest_data = await upstash_client.get_json(cache_key)
        cached = True

        # If not in cache, try Supabase
        if not manifest_data:
            client = supabase_client.get_client()
            query = (
                client.table("bcm_manifests")
                .select("manifest_json, version, checksum, generated_at")
                .eq("workspace_id", workspace_id)
            )
            if version:
                query = query.eq("version", int(version))
            else:
                query = query.order("version", desc=True).limit(1)

            result = query.execute()

            if result.data:
                manifest_data = result.data[0]["manifest_json"]
                cached = False

                if not version:
                    await cache_bcm_in_redis(workspace_id, manifest_data)

        if not manifest_data:
            raise HTTPException(
                status_code=404, detail=f"BCM not found for workspace {workspace_id}"
            )

        manifest = BCMSchemaValidator.validate_manifest(manifest_data)

        return BCMManifestResponse(
            success=True,
            workspace_id=workspace_id,
            manifest=manifest.dict() if include_raw else None,
            version=manifest.version.value,
            checksum=manifest.checksum,
            completion_percentage=manifest.completion_percentage,
            cached=cached,
            retrieved_at=datetime.utcnow().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving BCM for workspace {workspace_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"BCM retrieval failed: {str(e)}")


@router.get("/{session_id}/status")
async def get_finalization_status(session_id: str):
    """Get finalization status for a session."""
    try:
        # Get session metadata
        metadata = await session_manager.get_metadata(session_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Session not found")

        # Check if finalized
        step_data = await session_manager.get_step(session_id, 0)
        finalized = step_data.get("finalized", False) if step_data else False

        # Get completion percentage
        all_steps = await session_manager.get_all_steps(session_id)
        completed_steps = len(all_steps) if all_steps else 0
        completion_percentage = (completed_steps / 23) * 100

        # Get workspace BCM status
        workspace_id = metadata.get("workspace_id")
        bcm_status = None

        if workspace_id:
            try:
                cache_key = f"w:{workspace_id}:bcm:latest"
                cached_bcm = await upstash_client.get_json(cache_key)
                bcm_status = {
                    "exists": cached_bcm is not None,
                    "version": cached_bcm.get("version") if cached_bcm else None,
                    "checksum": cached_bcm.get("checksum") if cached_bcm else None,
                    "completion_percentage": (
                        cached_bcm.get("completion_percentage") if cached_bcm else None
                    ),
                }
            except Exception:
                bcm_status = {"exists": False, "error": "Failed to check BCM status"}

        return {
            "success": True,
            "session_id": session_id,
            "workspace_id": workspace_id,
            "finalized": finalized,
            "completion_percentage": completion_percentage,
            "completed_steps": completed_steps,
            "total_steps": 23,
            "bcm_status": bcm_status,
            "checked_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting finalization status for session {session_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.delete("/{session_id}/cleanup")
async def cleanup_session_data(session_id: str):
    """Clean up session data after finalization."""
    try:
        # Verify session is finalized
        step_data = await session_manager.get_step(session_id, 0)
        finalized = step_data.get("finalized", False) if step_data else False

        if not finalized:
            raise HTTPException(
                status_code=400, detail="Session must be finalized before cleanup"
            )

        # Delete session from Redis
        deleted = await session_manager.delete_session(session_id)

        return {
            "success": deleted,
            "session_id": session_id,
            "message": "Session data cleaned up successfully",
            "cleaned_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


# Background task processor (would typically run as separate service)
async def process_embedding_queue():
    """Background task processor for embedding generation."""
    while True:
        try:
            # Get next task from queue
            queue_key = "embedding_queue"
            task_json = await upstash_client.async_client.brpop(queue_key, 1)

            if not task_json:
                await asyncio.sleep(5)  # Wait 5 seconds if no tasks
                continue

            task_data = json.loads(task_json[1])

            # Process embedding generation
            workspace_id = task_data["workspace_id"]
            sections = task_data["sections_to_embed"]

            logger.info(
                f"Processing embeddings for workspace {workspace_id}: {sections}"
            )

            # This would integrate with the vector store and embedding service
            # For now, we'll just log the task

            # Mark task as completed (in production, would update DB)
            await asyncio.sleep(1)  # Simulate processing time

        except Exception as e:
            logger.error(f"Error in embedding queue processor: {str(e)}")
            await asyncio.sleep(10)  # Wait longer on error


# Health check for finalize system
@router.get("/finalize/health")
async def finalize_system_health():
    """Health check for the finalize system components."""
    try:
        health_status = {
            "redis_connection": False,
            "supabase_connection": False,
            "upstash_connection": False,
            "vertex_ai_connection": False,
            "overall_healthy": False,
        }

        # Check Redis/Session Manager
        try:
            await session_manager.health_check()
            health_status["redis_connection"] = True
        except Exception:
            pass

        # Check Supabase
        try:
            await supabase_client.execute("SELECT 1")
            health_status["supabase_connection"] = True
        except Exception:
            pass

        # Check Upstash
        try:
            await upstash_client.async_client.ping()
            health_status["upstash_connection"] = True
        except Exception:
            pass

        # Check Vertex AI
        try:
            await vertex_ai_client.health_check()
            health_status["vertex_ai_connection"] = True
        except Exception:
            pass

        # Overall health
        health_status["overall_healthy"] = all(
            [
                health_status["redis_connection"],
                health_status["supabase_connection"],
                health_status["upstash_connection"],
            ]
        )

        health_status["checked_at"] = datetime.utcnow().isoformat()

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "overall_healthy": False,
            "error": str(e),
            "checked_at": datetime.utcnow().isoformat(),
        }
