"""
Memory management jobs for Raptorflow.

Provides background jobs for memory indexing, cleanup,
and synchronization operations.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from infrastructure.cloud_monitoring import get_cloud_monitoring
from infrastructure.logging import get_cloud_logging

from .decorators import background_job, daily_job, hourly_job, job
from .models import JobResult, JobStatus

logger = logging.getLogger(__name__)


@dataclass
class MemoryIndexingResult:
    """Result of memory indexing operation."""

    total_memories: int
    indexed_memories: int
    failed_memories: int
    vector_index_size: int
    graph_index_size: int
    processing_time_seconds: float
    errors: List[str]


@dataclass
class MemoryCleanupResult:
    """Result of memory cleanup operation."""

    total_memories: int
    cleaned_memories: int
    expired_memories: int
    duplicate_memories: int
    orphaned_memories: int
    space_freed_mb: float
    processing_time_seconds: float
    errors: List[str]


@dataclass
class MemorySyncResult:
    """Result of memory synchronization operation."""

    vector_synced: int
    graph_synced: int
    database_synced: int
    conflicts_resolved: int
    processing_time_seconds: float
    errors: List[str]


class MemoryJobs:
    """Memory management job implementations."""

    def __init__(self):
        self.logger = logging.getLogger("memory_jobs")
        self.logging = get_cloud_logging()
        self.monitoring = get_cloud_monitoring()

    async def memory_indexing_job(self, workspace_id: str) -> MemoryIndexingResult:
        """Index memories for a workspace."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting memory indexing for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "job_type": "memory_indexing",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get memory service
            from memory.memory_service import get_memory_service

            memory_service = get_memory_service()

            # Get all memories for workspace
            memories = await memory_service.get_workspace_memories(workspace_id)
            total_memories = len(memories)

            indexed_memories = 0
            failed_memories = 0

            # Process memories in batches
            batch_size = 100
            for i in range(0, len(memories), batch_size):
                batch = memories[i : i + batch_size]

                try:
                    # Index batch
                    await memory_service.index_memories_batch(batch)
                    indexed_memories += len(batch)

                    # Log progress
                    progress = (i + len(batch)) / total_memories * 100
                    await self.logging.log_structured(
                        "INFO",
                        f"Memory indexing progress: {progress:.1f}%",
                        {
                            "workspace_id": workspace_id,
                            "progress_percentage": progress,
                            "indexed_count": indexed_memories,
                            "total_count": total_memories,
                        },
                    )

                except Exception as e:
                    failed_memories += len(batch)
                    errors.append(
                        f"Failed to index batch {i//batch_size + 1}: {str(e)}"
                    )
                    self.logger.error(f"Memory indexing batch failed: {e}")

            # Get index sizes
            vector_index_size = await memory_service.get_vector_index_size(workspace_id)
            graph_index_size = await memory_service.get_graph_index_size(workspace_id)

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Record metrics
            await self.monitoring.record_metric(
                "memory_indexing_total_memories",
                total_memories,
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "memory_indexing_success_rate",
                (indexed_memories / total_memories) * 100 if total_memories > 0 else 0,
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "memory_indexing_processing_time",
                processing_time,
                {"workspace_id": workspace_id},
            )

            result = MemoryIndexingResult(
                total_memories=total_memories,
                indexed_memories=indexed_memories,
                failed_memories=failed_memories,
                vector_index_size=vector_index_size,
                graph_index_size=graph_index_size,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Memory indexing completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "total_memories": total_memories,
                    "indexed_memories": indexed_memories,
                    "failed_memories": failed_memories,
                    "processing_time_seconds": processing_time,
                    "vector_index_size": vector_index_size,
                    "graph_index_size": graph_index_size,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Memory indexing failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Memory indexing failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def memory_cleanup_job(
        self, workspace_id: Optional[str] = None
    ) -> MemoryCleanupResult:
        """Clean up old and orphaned memories."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting memory cleanup for workspace: {workspace_id or 'all'}",
                {
                    "workspace_id": workspace_id,
                    "job_type": "memory_cleanup",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get memory service
            from memory.memory_service import get_memory_service

            memory_service = get_memory_service()

            # Get cleanup statistics
            cleanup_stats = await memory_service.get_cleanup_stats(workspace_id)
            total_memories = cleanup_stats.get("total_memories", 0)

            cleaned_memories = 0
            expired_memories = 0
            duplicate_memories = 0
            orphaned_memories = 0
            space_freed_mb = 0.0

            # Clean expired memories
            try:
                expired_result = await memory_service.cleanup_expired_memories(
                    workspace_id
                )
                expired_memories = expired_result.get("cleaned_count", 0)
                space_freed_mb += expired_result.get("space_freed_mb", 0.0)
                cleaned_memories += expired_memories
            except Exception as e:
                errors.append(f"Failed to cleanup expired memories: {str(e)}")

            # Clean duplicate memories
            try:
                duplicate_result = await memory_service.cleanup_duplicate_memories(
                    workspace_id
                )
                duplicate_memories = duplicate_result.get("cleaned_count", 0)
                space_freed_mb += duplicate_result.get("space_freed_mb", 0.0)
                cleaned_memories += duplicate_memories
            except Exception as e:
                errors.append(f"Failed to cleanup duplicate memories: {str(e)}")

            # Clean orphaned memories
            try:
                orphaned_result = await memory_service.cleanup_orphaned_memories(
                    workspace_id
                )
                orphaned_memories = orphaned_result.get("cleaned_count", 0)
                space_freed_mb += orphaned_result.get("space_freed_mb", 0.0)
                cleaned_memories += orphaned_memories
            except Exception as e:
                errors.append(f"Failed to cleanup orphaned memories: {str(e)}")

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Record metrics
            await self.monitoring.record_metric(
                "memory_cleanup_total_cleaned",
                cleaned_memories,
                {"workspace_id": workspace_id or "all"},
            )

            await self.monitoring.record_metric(
                "memory_cleanup_space_freed",
                space_freed_mb,
                {"workspace_id": workspace_id or "all"},
            )

            await self.monitoring.record_metric(
                "memory_cleanup_processing_time",
                processing_time,
                {"workspace_id": workspace_id or "all"},
            )

            result = MemoryCleanupResult(
                total_memories=total_memories,
                cleaned_memories=cleaned_memories,
                expired_memories=expired_memories,
                duplicate_memories=duplicate_memories,
                orphaned_memories=orphaned_memories,
                space_freed_mb=space_freed_mb,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Memory cleanup completed for workspace: {workspace_id or 'all'}",
                {
                    "workspace_id": workspace_id,
                    "total_memories": total_memories,
                    "cleaned_memories": cleaned_memories,
                    "expired_memories": expired_memories,
                    "duplicate_memories": duplicate_memories,
                    "orphaned_memories": orphaned_memories,
                    "space_freed_mb": space_freed_mb,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Memory cleanup failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Memory cleanup failed for workspace: {workspace_id or 'all'}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def memory_sync_job(
        self, workspace_id: Optional[str] = None
    ) -> MemorySyncResult:
        """Synchronize memory indices with database."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting memory sync for workspace: {workspace_id or 'all'}",
                {
                    "workspace_id": workspace_id,
                    "job_type": "memory_sync",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get memory service
            from memory.memory_service import get_memory_service

            memory_service = get_memory_service()

            vector_synced = 0
            graph_synced = 0
            database_synced = 0
            conflicts_resolved = 0

            # Sync vector index
            try:
                vector_result = await memory_service.sync_vector_index(workspace_id)
                vector_synced = vector_result.get("synced_count", 0)
                conflicts_resolved += vector_result.get("conflicts_resolved", 0)
            except Exception as e:
                errors.append(f"Failed to sync vector index: {str(e)}")

            # Sync graph index
            try:
                graph_result = await memory_service.sync_graph_index(workspace_id)
                graph_synced = graph_result.get("synced_count", 0)
                conflicts_resolved += graph_result.get("conflicts_resolved", 0)
            except Exception as e:
                errors.append(f"Failed to sync graph index: {str(e)}")

            # Sync database
            try:
                db_result = await memory_service.sync_database(workspace_id)
                database_synced = db_result.get("synced_count", 0)
                conflicts_resolved += db_result.get("conflicts_resolved", 0)
            except Exception as e:
                errors.append(f"Failed to sync database: {str(e)}")

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Record metrics
            await self.monitoring.record_metric(
                "memory_sync_total_synced",
                vector_synced + graph_synced + database_synced,
                {"workspace_id": workspace_id or "all"},
            )

            await self.monitoring.record_metric(
                "memory_sync_conflicts_resolved",
                conflicts_resolved,
                {"workspace_id": workspace_id or "all"},
            )

            await self.monitoring.record_metric(
                "memory_sync_processing_time",
                processing_time,
                {"workspace_id": workspace_id or "all"},
            )

            result = MemorySyncResult(
                vector_synced=vector_synced,
                graph_synced=graph_synced,
                database_synced=database_synced,
                conflicts_resolved=conflicts_resolved,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Memory sync completed for workspace: {workspace_id or 'all'}",
                {
                    "workspace_id": workspace_id,
                    "vector_synced": vector_synced,
                    "graph_synced": graph_synced,
                    "database_synced": database_synced,
                    "conflicts_resolved": conflicts_resolved,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Memory sync failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Memory sync failed for workspace: {workspace_id or 'all'}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def memory_optimization_job(
        self, workspace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Optimize memory storage and indices."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting memory optimization for workspace: {workspace_id or 'all'}",
                {
                    "workspace_id": workspace_id,
                    "job_type": "memory_optimization",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get memory service
            from memory.memory_service import get_memory_service

            memory_service = get_memory_service()

            optimization_results = {}

            # Optimize vector index
            try:
                vector_opt = await memory_service.optimize_vector_index(workspace_id)
                optimization_results["vector_optimization"] = vector_opt
            except Exception as e:
                errors.append(f"Failed to optimize vector index: {str(e)}")

            # Optimize graph index
            try:
                graph_opt = await memory_service.optimize_graph_index(workspace_id)
                optimization_results["graph_optimization"] = graph_opt
            except Exception as e:
                errors.append(f"Failed to optimize graph index: {str(e)}")

            # Optimize database storage
            try:
                db_opt = await memory_service.optimize_database_storage(workspace_id)
                optimization_results["database_optimization"] = db_opt
            except Exception as e:
                errors.append(f"Failed to optimize database storage: {str(e)}")

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Record metrics
            await self.monitoring.record_metric(
                "memory_optimization_processing_time",
                processing_time,
                {"workspace_id": workspace_id or "all"},
            )

            result = {
                "optimization_results": optimization_results,
                "processing_time_seconds": processing_time,
                "errors": errors,
            }

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Memory optimization completed for workspace: {workspace_id or 'all'}",
                {
                    "workspace_id": workspace_id,
                    "processing_time_seconds": processing_time,
                    "optimization_count": len(optimization_results),
                    "error_count": len(errors),
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Memory optimization failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Memory optimization failed for workspace: {workspace_id or 'all'}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def memory_backup_job(
        self, workspace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create backup of memory data."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting memory backup for workspace: {workspace_id or 'all'}",
                {
                    "workspace_id": workspace_id,
                    "job_type": "memory_backup",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get memory service
            from memory.memory_service import get_memory_service

            memory_service = get_memory_service()

            backup_results = {}

            # Backup vector index
            try:
                vector_backup = await memory_service.backup_vector_index(workspace_id)
                backup_results["vector_backup"] = vector_backup
            except Exception as e:
                errors.append(f"Failed to backup vector index: {str(e)}")

            # Backup graph index
            try:
                graph_backup = await memory_service.backup_graph_index(workspace_id)
                backup_results["graph_backup"] = graph_backup
            except Exception as e:
                errors.append(f"Failed to backup graph index: {str(e)}")

            # Backup database
            try:
                db_backup = await memory_service.backup_database(workspace_id)
                backup_results["database_backup"] = db_backup
            except Exception as e:
                errors.append(f"Failed to backup database: {str(e)}")

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Record metrics
            await self.monitoring.record_metric(
                "memory_backup_processing_time",
                processing_time,
                {"workspace_id": workspace_id or "all"},
            )

            result = {
                "backup_results": backup_results,
                "processing_time_seconds": processing_time,
                "errors": errors,
            }

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Memory backup completed for workspace: {workspace_id or 'all'}",
                {
                    "workspace_id": workspace_id,
                    "processing_time_seconds": processing_time,
                    "backup_count": len(backup_results),
                    "error_count": len(errors),
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Memory backup failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Memory backup failed for workspace: {workspace_id or 'all'}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise


# Create global instance
_memory_jobs = MemoryJobs()


# Job implementations with decorators
@job(
    name="memory_indexing_job",
    queue="memory",
    retries=2,
    timeout=1800,  # 30 minutes
    description="Index memories for workspace",
)
async def memory_indexing_job(workspace_id: str) -> Dict[str, Any]:
    """Memory indexing job."""
    result = await _memory_jobs.memory_indexing_job(workspace_id)
    return result.__dict__


@daily_job(
    hour=2,
    minute=0,
    queue="memory",
    retries=2,
    timeout=3600,  # 1 hour
    description="Daily memory cleanup",
)
async def memory_cleanup_job() -> Dict[str, Any]:
    """Daily memory cleanup job."""
    result = await _memory_jobs.memory_cleanup_job()
    return result.__dict__


@hourly_job(
    minute=30,
    queue="memory",
    retries=1,
    timeout=1800,  # 30 minutes
    description="Hourly memory sync",
)
async def memory_sync_job() -> Dict[str, Any]:
    """Hourly memory sync job."""
    result = await _memory_jobs.memory_sync_job()
    return result.__dict__


@weekly_job(
    day_of_week=0,  # Sunday
    hour=3,
    minute=0,
    queue="memory",
    retries=2,
    timeout=7200,  # 2 hours
    description="Weekly memory optimization",
)
async def memory_optimization_job() -> Dict[str, Any]:
    """Weekly memory optimization job."""
    result = await _memory_jobs.memory_optimization_job()
    return result


@daily_job(
    hour=4,
    minute=0,
    queue="memory",
    retries=2,
    timeout=3600,  # 1 hour
    description="Daily memory backup",
)
async def memory_backup_job() -> Dict[str, Any]:
    """Daily memory backup job."""
    result = await _memory_jobs.memory_backup_job()
    return result


@background_job(
    queue="memory",
    retries=1,
    timeout=600,  # 10 minutes
    description="Workspace-specific memory indexing",
)
async def workspace_memory_indexing_job(workspace_id: str) -> Dict[str, Any]:
    """Workspace-specific memory indexing job."""
    result = await _memory_jobs.memory_indexing_job(workspace_id)
    return result.__dict__


@background_job(
    queue="memory",
    retries=1,
    timeout=300,  # 5 minutes
    description="Workspace-specific memory cleanup",
)
async def workspace_memory_cleanup_job(workspace_id: str) -> Dict[str, Any]:
    """Workspace-specific memory cleanup job."""
    result = await _memory_jobs.memory_cleanup_job(workspace_id)
    return result.__dict__


@background_job(
    queue="memory",
    retries=1,
    timeout=300,  # 5 minutes
    description="Workspace-specific memory sync",
)
async def workspace_memory_sync_job(workspace_id: str) -> Dict[str, Any]:
    """Workspace-specific memory sync job."""
    result = await _memory_jobs.memory_sync_job(workspace_id)
    return result.__dict__


# Convenience functions
async def index_workspace_memories(workspace_id: str) -> MemoryIndexingResult:
    """Index memories for a specific workspace."""
    return await _memory_jobs.memory_indexing_job(workspace_id)


async def cleanup_workspace_memories(workspace_id: str) -> MemoryCleanupResult:
    """Clean up memories for a specific workspace."""
    return await _memory_jobs.memory_cleanup_job(workspace_id)


async def sync_workspace_memories(workspace_id: str) -> MemorySyncResult:
    """Sync memories for a specific workspace."""
    return await _memory_jobs.memory_sync_job(workspace_id)


async def optimize_workspace_memories(workspace_id: str) -> Dict[str, Any]:
    """Optimize memories for a specific workspace."""
    return await _memory_jobs.memory_optimization_job(workspace_id)


async def backup_workspace_memories(workspace_id: str) -> Dict[str, Any]:
    """Backup memories for a specific workspace."""
    return await _memory_jobs.memory_backup_job(workspace_id)


# Export all jobs
__all__ = [
    "MemoryJobs",
    "memory_indexing_job",
    "memory_cleanup_job",
    "memory_sync_job",
    "memory_optimization_job",
    "memory_backup_job",
    "workspace_memory_indexing_job",
    "workspace_memory_cleanup_job",
    "workspace_memory_sync_job",
    "index_workspace_memories",
    "cleanup_workspace_memories",
    "sync_workspace_memories",
    "optimize_workspace_memories",
    "backup_workspace_memories",
]
