"""
Onboarding Migration API Endpoints

API endpoints for migrating from legacy onboarding status to the new Redis-based session system
with Business Context Manifest (BCM) integration.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel, Field

from ..services.onboarding_migration_service import (
    LegacyOnboardingStatus,
    MigrationResult,
    MigrationStats,
    MigrationStatus,
    OnboardingMigrationService,
    migrate_onboarding_status_batch,
    rollback_onboarding_status_batch,
)
from ..services.supabase_client import get_supabase_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/onboarding/migration", tags=["onboarding-migration"])

# Initialize services
migration_service = OnboardingMigrationService()
supabase_client = get_supabase_client()


# Pydantic models
class MigrationRequest(BaseModel):
    """Request model for user migration."""

    user_ids: List[str] = Field(..., description="List of user IDs to migrate")
    batch_size: int = Field(default=50, description="Batch size for processing")


class MigrationResponse(BaseModel):
    """Response model for migration operations."""

    success: bool
    total_users: int
    migrated_users: int
    failed_users: int
    results: List[Dict[str, Any]]
    stats: Optional[Dict[str, Any]]
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None


class RollbackRequest(BaseModel):
    """Request model for rollback operations."""

    user_ids: List[str] = Field(..., description="List of user IDs to rollback")


class RollbackResponse(BaseModel):
    """Response model for rollback operations."""

    success: bool
    total_users: int
    rolled_back_users: int
    failed_users: int
    results: List[Dict[str, Any]]
    error_message: Optional[str] = None
    processing_time_ms: Optional[float] = None


class ValidationResponse(BaseModel):
    """Response model for migration validation."""

    valid: bool
    user_id: str
    session_id: Optional[str]
    workspace_id: Optional[str]
    legacy_status: Optional[str]
    new_status: Optional[str]
    completion_percentage: Optional[float]
    bcm_generated: Optional[bool]
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]]


class StatsResponse(BaseModel):
    """Response model for migration statistics."""

    total_users: int
    migrated_users: int
    failed_users: int
    legacy_completed_users: int
    legacy_active_users: int
    avg_completion_time: Optional[float]
    migration_start_time: Optional[str]
    migration_end_time: Optional[str]
    total_migrations: Optional[int]
    completed_migrations: Optional[int]
    failed_migrations: Optional[int]


# API Endpoints
@router.post("/migrate")
async def migrate_users(request: MigrationRequest, background_tasks: BackgroundTasks):
    """
    Migrate users from legacy onboarding status to new session system.

    This endpoint:
    1. Validates user IDs exist and have legacy onboarding data
    2. Creates new Redis sessions for each user
    3. Migrates step data and progress
    4. Generates BCM for completed onboarding
    5. Updates migration logs and user status
    6. Returns comprehensive migration results

    Args:
        request: Migration request with user IDs and batch size

    Returns:
        MigrationResponse with detailed results and statistics
    """
    start_time = datetime.utcnow()

    try:
        # Validate user IDs
        if not request.user_ids:
            raise HTTPException(status_code=400, detail="No user IDs provided")

        # Validate user existence and legacy data
        valid_user_ids = []
        for user_id in request.user_ids:
            user_data = await supabase_client.execute(
                "SELECT id, onboarding_status, onboarding_step, has_completed_onboarding FROM users WHERE id = $1",
                [user_id],
            )

            if not user_data:
                logger.warning(f"User {user_id} not found, skipping")
                continue

            if (
                not user_data[0]["onboarding_status"]
                or user_data[0]["onboarding_status"] == "migrated"
            ):
                logger.warning(
                    f"User {user_id} has no legacy onboarding data, skipping"
                )
                continue

            valid_user_ids.append(user_id)

        if not valid_user_ids:
            raise HTTPException(
                status_code=400,
                detail="No valid users with legacy onboarding data found",
            )

        # Process migration in batches
        all_results = []
        batch_size = request.batch_size

        for i in range(0, len(valid_user_ids), batch_size):
            batch = valid_user_ids[i : i + batch_size]

            logger.info(
                f"Processing migration batch {i//batch_size + 1}/{(len(valid_user_ids) + batch_size - 1)//batch_size}"
            )

            try:
                batch_results = await migrate_onboarding_status_batch(batch)
                all_results.extend(batch_results)
            except Exception as e:
                logger.error(f"Failed to process batch {i//batch_size + 1}: {str(e)}")
                # Add failed results for this batch
                for user_id in batch:
                    all_results.append(
                        {"user_id": user_id, "success": False, "error": str(e)}
                    )

        # Calculate statistics
        migrated_count = sum(
            1 for result in all_results if result.get("success", False)
        )
        failed_count = len(all_results) - migrated_count

        # Get overall migration stats
        stats = await migration_service.get_migration_stats()

        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time_ms = (end_time - start_time).total_seconds() * 1000

        return MigrationResponse(
            success=failed_count == 0,
            total_users=len(request.user_ids),
            migrated_users=migrated_count,
            failed_users=failed_count,
            results=all_results,
            stats={
                "total_users": stats.total_users,
                "migrated_users": stats.migrated_users,
                "failed_users": stats.failed_users,
                "legacy_completed_users": stats.legacy_completed_users,
                "legacy_active_users": stats.legacy_active_users,
                "avg_completion_time": stats.avg_completion_time,
                "migration_start_time": (
                    stats.migration_start_time.isoformat()
                    if stats.migration_start_time
                    else None
                ),
                "migration_end_time": (
                    stats.migration_end_time.isoformat()
                    if stats.migration_end_time
                    else None
                ),
            },
            processing_time_ms=processing_time_ms,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


@router.post("/migrate/{user_id}")
async def migrate_single_user(user_id: str, background_tasks: BackgroundTasks):
    """
    Migrate a single user from legacy onboarding status to new session system.

    Args:
        user_id: The user's UUID

    Returns:
        MigrationResult with migration details
    """
    try:
        result = await migration_service.migrate_user(user_id)

        return {
            "success": True,
            "user_id": result.user_id,
            "session_id": result.session_id,
            "workspace_id": result.workspace_id,
            "legacy_status": result.legacy_status,
            "new_status": result.new_status,
            "current_step": result.current_step,
            "completion_percentage": result.completion_percentage,
            "bcm_generated": result.bcm_generated,
            "migrated_at": result.migrated_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Single user migration failed for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


@router.post("/rollback")
async def rollback_users(request: RollbackRequest, background_tasks: BackgroundTasks):
    """
    Rollback migration for specified users, restoring legacy onboarding status.

    This endpoint:
    1. Validates user IDs and migration status
    2. Deletes new session data
    3. Restores legacy onboarding status
    4. Updates migration logs
    5. Returns rollback results

    Args:
        request: Rollback request with user IDs

    Returns:
        RollbackResponse with detailed results
    """
    start_time = datetime.utcnow()

    try:
        # Validate user IDs
        if not request.user_ids:
            raise HTTPException(status_code=400, detail="No user IDs provided")

        # Process rollback in batches
        all_results = []

        for user_id in request.user_ids:
            try:
                success = await migration_service.rollback_user(user_id)
                all_results.append({"user_id": user_id, "success": success})
            except Exception as e:
                logger.error(f"Failed to rollback user {user_id}: {str(e)}")
                all_results.append(
                    {"user_id": user_id, "success": False, "error": str(e)}
                )

        # Calculate results
        rolled_back_count = sum(
            1 for result in all_results if result.get("success", False)
        )
        failed_count = len(all_results) - rolled_back_count

        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time_ms = (end_time - start_time).total_seconds() * 1000

        return RollbackResponse(
            success=failed_count == 0,
            total_users=len(request.user_ids),
            rolled_back_users=rolled_back_count,
            failed_users=failed_count,
            results=all_results,
            processing_time_ms=processing_time_ms,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rollback failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Rollback failed: {str(e)}")


@router.post("/rollback/{user_id}")
async def rollback_single_user(user_id: str, background_tasks: BackgroundTasks):
    """
    Rollback migration for a single user.

    Args:
        user_id: The user's UUID

    Returns:
        Success status
    """
    try:
        success = await migration_service.rollback_user(user_id)

        return {
            "success": success,
            "user_id": user_id,
            "message": (
                "Rollback completed successfully" if success else "Rollback failed"
            ),
        }

    except Exception as e:
        logger.error(f"Single user rollback failed for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Rollback failed: {str(e)}")


@router.get("/stats")
async def get_migration_stats() -> StatsResponse:
    """
    Get current migration statistics.

    Returns:
        StatsResponse with comprehensive migration statistics
    """
    try:
        stats = await migration_service.get_migration_stats()

        return StatsResponse(
            total_users=stats.total_users,
            migrated_users=stats.migrated_users,
            failed_users=stats.failed_users,
            legacy_completed_users=stats.legacy_completed_users,
            legacy_active_users=stats.legacy_active_users,
            avg_completion_time=stats.avg_completion_time,
            migration_start_time=(
                stats.migration_start_time.isoformat()
                if stats.migration_start_time
                else None
            ),
            migration_end_time=(
                stats.migration_end_time.isoformat()
                if stats.migration_end_time
                else None
            ),
            total_migrations=stats.total_migrations,
            completed_migrations=stats.completed_migrations,
            failed_migrations=stats.failed_migrations,
        )

    except Exception as e:
        logger.error(f"Failed to get migration stats: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get migration stats: {str(e)}"
        )


@router.get("/validate/{user_id}")
async def validate_migration(user_id: str) -> ValidationResponse:
    """
    Validate migration integrity for a user.

    Args:
        user_id: The user's UUID

    Returns:
        ValidationResponse with validation results
    """
    try:
        validation_result = await migration_service.validate_migration(user_id)

        return ValidationResponse(
            valid=validation_result["valid"],
            user_id=validation_result.get("user_id"),
            session_id=validation_result.get("session_id"),
            workspace_id=validation_result.get("workspace_id"),
            legacy_status=validation_result.get("legacy_status"),
            new_status=validation_result.get("new_status"),
            completion_percentage=validation_result.get("completion_percentage"),
            bcm_generated=validation_result.get("bcm_generated"),
            error_message=validation_result.get("error"),
            details=validation_result,
        )

    except Exception as e:
        logger.error(f"Failed to validate migration for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/health")
async def migration_health_check() -> Dict[str, Any]:
    """
    Health check for the migration system.

    Returns:
        Dictionary with health status of migration components
    """
    try:
        # Test database connection
        db_health = await supabase_client.execute("SELECT 1")

        # Test migration service
        stats = await migration_service.get_migration_stats()

        return {
            "healthy": True,
            "database": "connected",
            "migration_service": "operational",
            "total_users": stats.total_users,
            "migrated_users": stats.migrated_users,
            "failed_users": stats.failed_users,
            "checked_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Migration health check failed: {str(e)}")
        return {
            "healthy": False,
            "error": str(e),
            "checked_at": datetime.utcnow().isoformat(),
        }


@router.post("/cleanup")
async def cleanup_failed_migrations(
    older_than_days: int = Query(
        default=7, description="Clean up migration logs older than specified days"
    )
):
    """
    Clean up failed migration logs older than specified days.

    Args:
        older_than_days: Number of days old for cleanup

    Returns:
        Success status and cleanup count
    """
    try:
        await migration_service._cleanup_failed_migrations(older_than_days)

        return {
            "success": True,
            "message": f"Cleaned up migration logs older than {older_than_days} days",
            "cleaned_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to cleanup migration logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@router.get("/user/{user_id}/status")
async def get_user_migration_status(user_id: str) -> Dict[str, Any]:
    """
    Get detailed migration status for a specific user.

    Args:
        user_id: The user's UUID

    Returns:
        Dictionary with detailed migration status
    """
    try:
        # Check if user exists
        user_query = """
            SELECT id, email, full_name, onboarding_status, onboarding_step, has_completed_onboarding
            FROM users WHERE id = $1
        """

        user_result = await supabase_client.execute(user_query, [user_id])
        if not user_result:
            raise HTTPException(status_code=404, detail="User not found")

        user_data = user_result[0]

        # Check migration status
        migration_result = await migration_service.validate_migration(user_id)

        return {
            "user_id": user_id,
            "email": user_data["email"],
            "full_name": user_data["full_name"],
            "legacy_status": user_data["onboarding_status"],
            "legacy_step": user_data["onboarding_step"],
            "legacy_completed": user_data["has_completed_onboarding"],
            "migration_status": "migrated" if migration_result["valid"] else "legacy",
            "session_id": migration_result.get("session_id"),
            "workspace_id": migration_result.get("workspace_id"),
            "new_status": migration_result.get("new_status"),
            "current_step": migration_result.get("current_step"),
            "completion_percentage": migration_result.get("completion_percentage"),
            "bcm_generated": migration_result.get("bcm_generated"),
            "migrated_at": migration_result.get("migrated_at"),
            "validation": migration_result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user migration status for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/workspace/{workspace_id}/summary")
async def get_workspace_migration_summary(workspace_id: str) -> Dict[str, Any]:
    """
    Get migration summary for a workspace.

    Args:
        workspace_id: The workspace's UUID

    Returns:
        Dictionary with workspace migration summary
    """
    try:
        # Get workspace info
        workspace_query = """
            SELECT id, name, owner_id, created_at, updated_at
            FROM workspaces
            WHERE id = $1
        """

        workspace_result = await supabase_client.execute(
            workspace_query, [workspace_id]
        )
        if not workspace_result:
            raise HTTPException(status_code=404, detail="Workspace not found")

        workspace_data = workspace_result[0]

        # Get migration summary
        summary_query = """
            SELECT
                COUNT(*) as total_sessions,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_sessions,
                AVG(completion_percentage) as avg_completion,
                COUNT(CASE WHEN bcm_generated = TRUE THEN 1 END) as bcm_generated_sessions,
                COUNT(CASE WHEN bcm_finalized = TRUE THEN 1 END) as bcm_finalized_sessions,
                MAX(completed_at) as last_completion_at
            FROM onboarding_sessions
            WHERE workspace_id = $1
        """

        summary_result = await supabase_client.execute(summary_query, [workspace_id])
        summary_data = summary_result[0] if summary_result else {}

        return {
            "workspace_id": workspace_id,
            "workspace_name": workspace_data["name"],
            "owner_id": workspace_data["owner_id"],
            "total_sessions": summary_data.get("total_sessions", 0),
            "completed_sessions": summary_data.get("completed_sessions", 0),
            "active_sessions": summary_data.get("active_sessions", 0),
            "avg_completion": summary_data.get("avg_completion", 0),
            "bcm_generated_sessions": summary_data.get("bcm_generated_sessions", 0),
            "bcm_finalized_sessions": summary_data.get("bcm_finalized_sessions", 0),
            "last_completion_at": summary_data.get("last_completion_at"),
            "created_at": workspace_data["created_at"],
            "updated_at": workspace_data["updated_at"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get workspace migration summary for {workspace_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


@router.get("/progress")
async def get_migration_progress() -> Dict[str, Any]:
    """
    Get real-time migration progress.

    Returns:
        Dictionary with migration progress information
    """
    try:
        stats = await migration_service.get_migration_stats()

        # Calculate progress percentage
        total_users = stats.total_users
        migrated_users = stats.migrated_users
        progress_percentage = (
            (migrated_users / total_users * 100) if total_users > 0 else 0
        )

        return {
            "total_users": total_users,
            "migrated_users": migrated_users,
            "failed_users": stats.failed_users,
            "progress_percentage": progress_percentage,
            "legacy_completed_users": stats.legacy_completed_users,
            "legacy_active_users": stats.legacy_active_users,
            "migration_start_time": (
                stats.migration_start_time.isoformat()
                if stats.migration_start_time
                else None
            ),
            "migration_end_time": (
                stats.migration_end_time.isoformat()
                if stats.migration_end_time
                else None
            ),
            "estimated_completion_time": None,  # Could calculate based on current rate
            "processing_rate": 0,  # Users per minute
            "checked_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get migration progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")


@router.get("/legacy-status/{user_id}")
async def get_legacy_status(user_id: str) -> Dict[str, Any]:
    """
    Get legacy onboarding status for a user (before migration).

    Args:
        user_id: The user's UUID

    Returns:
        Dictionary with legacy status information
    """
    try:
        user_query = """
            SELECT id, email, full_name, onboarding_status, onboarding_step, has_completed_onboarding,
                   preferences, metadata, created_at, updated_at
            FROM users
            WHERE id = $1
        """

        result = await supabase_client.execute(user_query, [user_id])
        if not result:
            raise HTTPException(status_code=404, detail="User not found")

        user_data = result[0]

        return {
            "user_id": user_id,
            "email": user_data["email"],
            "full_name": user_data["full_name"],
            "onboarding_status": user_data["onboarding_status"],
            "onboarding_step": user_data["onboarding_step"],
            "has_completed_onboarding": user_data["has_completed_onboarding"],
            "preferences": user_data["preferences"],
            "metadata": user_data["metadata"],
            "created_at": user_data["created_at"],
            "updated_at": user_data["updated_at"],
        }

    except Exception as e:
        logger.error(f"Failed to get legacy status for {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get legacy status: {str(e)}"
        )


@router.get("/comparison")
async def get_legacy_vs_new_comparison() -> Dict[str, Any]:
    """
    Get comparison between legacy and new onboarding systems.

    Returns:
        Dictionary with comparison statistics
    """
    try:
        # Get legacy stats
        legacy_query = """
            SELECT
                COUNT(*) as total_users,
                COUNT(CASE WHEN has_completed_onboarding THEN 1 END) as completed_users,
                COUNT(CASE WHEN onboarding_status IN ('active', 'in_progress') THEN 1 END) as active_users,
                COUNT(CASE WHEN onboarding_status = 'none' THEN 1 END) as no_onboarding_users
            FROM users
        """

        legacy_result = await supabase_client.execute(legacy_query)
        legacy_data = legacy_result[0] if legacy_result else {}

        # Get new stats
        new_stats = await migration_service.get_migration_stats()

        return {
            "legacy_system": {
                "total_users": legacy_data["total_users"],
                "completed_users": legacy_data["completed_users"],
                "active_users": legacy_data["active_users"],
                "no_onboarding_users": legacy_data["no_onboarding_users"],
            },
            "new_system": {
                "total_users": new_stats.total_users,
                "migrated_users": new_stats.migrated_users,
                "failed_users": new_stats.failed_users,
                "legacy_completed_users": new_stats.legacy_completed_users,
                "legacy_active_users": new_stats.legacy_active_users,
            },
            "comparison": {
                "migration_rate": (
                    (new_stats.migrated_users / legacy_data["total_users"] * 100)
                    if legacy_data["total_users"] > 0
                    else 0
                ),
                "completion_rate_difference": (
                    (
                        (
                            new_stats.legacy_completed_users
                            - legacy_data["completed_users"]
                        )
                        / legacy_data["total_users"]
                        * 100
                    )
                    if legacy_data["total_users"] > 0
                    else 0
                ),
                "active_users_difference": (
                    (
                        (new_stats.legacy_active_users - legacy_data["active_users"])
                        / legacy_data["total_users"]
                        * 100
                    )
                    if legacy_data["total_users"] > 0
                    else 0
                ),
            },
            "checked_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get comparison: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get comparison: {str(e)}"
        )


# Background task for processing large migrations
@router.post("/migrate/batch")
async def migrate_large_batch(
    request: MigrationRequest, background_tasks: BackgroundTasks
):
    """
    Process a large migration batch in the background.

    Args:
        request: Migration request with user IDs and batch size

    Returns:
        Confirmation that background task was started
    """
    try:
        # Add to background queue
        background_tasks.add_task(
            self._process_large_migration_batch,
            args=[request.user_ids, request.batch_size],
            kwargs={},
        )

        return {
            "success": True,
            "message": f"Large batch migration started for {len(request.user_ids)} users",
            "batch_size": request.batch_size,
            "estimated_time": (len(request.user_ids) / request.batch_size)
            * 2,  # Rough estimate
        }

    except Exception as e:
        logger.error(f"Failed to start large batch migration: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start batch migration: {str(e)}"
        )


async def _process_large_migration_batch(user_ids: List[str], batch_size: int):
    """Background task to process large migration batch."""
    try:
        logger.info(f"Processing large migration batch of {len(user_ids)} users")

        # Process in smaller sub-batches
        for i in range(0, len(user_ids), batch_size):
            sub_batch = user_ids[i : i + batch_size]

            logger.info(
                f"Processing sub-batch {i//batch_size + 1}/{(len(user_ids) + batch_size - 1)//batch_size}"
            )

            try:
                results = await migrate_onboarding_status_batch(sub_batch)
                logger.info(
                    f"Sub-batch {i//batch_size + 1} completed: {sum(1 for r in results if r.get('success', False))}/{len(sub_batch)}"
                )

                # Add delay between sub-batches
                if i + batch_size < len(user_ids):
                    await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Sub-batch {i//batch_size + 1} failed: {str(e)}")

        logger.info("Large batch migration completed")

    except Exception as e:
        logger.error(f"Large batch migration failed: {str(e)}")


# Utility functions for admin operations
@router.get("/admin/users/unmigrated")
async def get_unmigrated_users() -> List[Dict[str, Any]]:
    """Get list of users who haven't been migrated yet."""
    try:
        query = """
            SELECT id, email, full_name, onboarding_status, onboarding_step, has_completed_onboarding
            FROM users
            WHERE onboarding_status NOT IN ('migrated', 'none')
            ORDER BY created_at DESC
        """

        result = await supabase_client.execute(query)
        return [
            {
                "user_id": row["id"],
                "email": row["email"],
                "full_name": row["full_name"],
                "onboarding_status": row["onboarding_status"],
                "onboarding_step": row["onboarding_step"],
                "has_completed_onboarding": row["has_completed_onboarding"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            for row in result
        ]

    except Exception as e:
        logger.error(f"Failed to get unmigrated users: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get unmigrated users: {str(e)}"
        )


@router.get("/admin/users/migrated")
async def get_migrated_users() -> List[Dict[str, Any]]:
    """Get list of users who have been migrated."""
    try:
        query = """
            SELECT u.id, u.email, u.full_name, os.session_id, os.status, os.current_step,
                   os.completion_percentage, os.bcm_generated, os.migrated_at
            FROM users u
            JOIN onboarding_sessions os ON u.id = os.user_id
            WHERE os.migrated_from_legacy = TRUE
            ORDER BY os.migrated_at DESC
        """

        result = await supabase_client.execute(query)
        return [
            {
                "user_id": row["id"],
                "email": row["email"],
                "full_name": row["full_name"],
                "session_id": row["session_id"],
                "status": row["status"],
                "current_step": row["current_step"],
                "completion_percentage": row["completion_percentage"],
                "bcm_generated": row["bcm_generated"],
                "migrated_at": row["migrated_at"],
            }
            for row in result
        ]

    except Exception as e:
        logger.error(f"Failed to get migrated users: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get migrated users: {str(e)}"
        )


@router.get("/admin/users/migration-details")
async def get_detailed_migration_details() -> Dict[str, Any]:
    """Get detailed migration information for admin dashboard."""
    try:
        # Get overall stats
        stats = await migration_service.get_migration_stats()

        # Get recent migration logs
        logs_query = """
            SELECT id, source_user_id, target_session_id, legacy_onboarding_status,
                   legacy_onboarding_step, legacy_has_completed_onboarding, status,
                   started_at, completed_at, error_message
            FROM onboarding_migration_log
            ORDER BY created_at DESC
            LIMIT 50
        """

        logs_result = await supabase_client.execute(logs_query)
        recent_logs = [
            {
                "log_id": row["id"],
                "user_id": row["source_user_id"],
                "session_id": row["target_session_id"],
                "legacy_status": row["legacy_onboarding_status"],
                "legacy_step": row["legacy_onboarding_step"],
                "legacy_completed": row["legacy_has_completed_onboarding"],
                "status": row["status"],
                "started_at": row["started_at"],
                "completed_at": row["completed_at"],
                "error_message": row["error_message"],
            }
            for row in logs_result
        ]

        return {
            "stats": {
                "total_users": stats.total_users,
                "migrated_users": stats.migrated_users,
                "failed_users": stats.failed_users,
                "legacy_completed_users": stats.legacy_completed_users,
                "legacy_active_users": stats.legacy_active_users,
                "avg_completion_time": stats.avg_completion_time,
                "migration_start_time": stats.migration_start_time,
                "migration_end_time": stats.migration_end_time,
                "total_migrations": stats.total_migrations,
                "completed_migrations": stats.completed_migrations,
                "failed_migrations": stats.failed_migrations,
            },
            "recent_logs": recent_logs,
            "checked_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get detailed migration details: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get migration details: {str(e)}"
        )


# Error handling middleware
@router.exception_handler
async def migration_error_handler(request, exc):
    """Global error handler for migration endpoints."""
    logger.error(f"Migration error: {exc}")

    if isinstance(exc, HTTPException):
        return {
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
        }
    else:
        return {
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat(),
        }
