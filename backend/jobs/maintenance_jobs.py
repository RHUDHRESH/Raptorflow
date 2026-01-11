"""
Maintenance jobs for Raptorflow.

Provides background jobs for system maintenance,
cleanup operations, and database optimization.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..infrastructure.cloud_monitoring import get_cloud_monitoring
from ..infrastructure.logging import get_cloud_logging
from .decorators import background_job, daily_job, hourly_job, job, weekly_job
from .models import JobResult, JobStatus

logger = logging.getLogger(__name__)


@dataclass
class SessionCleanupResult:
    """Result of session cleanup operation."""

    total_sessions: int
    expired_sessions: int
    inactive_sessions: int
    orphaned_sessions: int
    cleaned_sessions: int
    space_freed_mb: float
    processing_time_seconds: float
    errors: List[str]


@dataclass
class ExecutionCleanupResult:
    """Result of execution cleanup operation."""

    total_executions: int
    old_executions: int
    failed_executions: int
    completed_executions: int
    cleaned_executions: int
    space_freed_mb: float
    processing_time_seconds: float
    errors: List[str]


@dataclass
class DatabaseMaintenanceResult:
    """Result of database maintenance operation."""

    tables_optimized: List[str]
    indexes_rebuilt: List[str]
    statistics_updated: List[str]
    space_freed_mb: float
    performance_improvement: float
    processing_time_seconds: float
    errors: List[str]


@dataclass
class SystemMaintenanceResult:
    """Result of system maintenance operation."""

    cache_cleared: bool
    logs_rotated: bool
    temp_files_cleaned: bool
    disk_space_freed_mb: float
    memory_optimized: bool
    processing_time_seconds: float
    errors: List[str]


class MaintenanceJobs:
    """Maintenance job implementations."""

    def __init__(self):
        self.logger = logging.getLogger("maintenance_jobs")
        self.logging = get_cloud_logging()
        self.monitoring = get_cloud_monitoring()

    async def cleanup_expired_sessions_job(self) -> SessionCleanupResult:
        """Clean up expired user sessions."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                "Starting expired sessions cleanup",
                {
                    "job_type": "cleanup_expired_sessions",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get session service
            from ..redis.session import get_session_service

            session_service = get_session_service()

            # Get session statistics
            session_stats = await session_service.get_session_statistics()
            total_sessions = session_stats.get("total_sessions", 0)

            # Clean expired sessions
            expired_result = await session_service.cleanup_expired_sessions()
            expired_sessions = expired_result.get("cleaned_count", 0)
            space_freed_mb = expired_result.get("space_freed_mb", 0.0)

            # Clean inactive sessions (older than 30 days)
            inactive_result = await session_service.cleanup_inactive_sessions(days=30)
            inactive_sessions = inactive_result.get("cleaned_count", 0)
            space_freed_mb += inactive_result.get("space_freed_mb", 0.0)

            # Clean orphaned sessions
            orphaned_result = await session_service.cleanup_orphaned_sessions()
            orphaned_sessions = orphaned_result.get("cleaned_count", 0)
            space_freed_mb += orphaned_result.get("space_freed_mb", 0.0)

            cleaned_sessions = expired_sessions + inactive_sessions + orphaned_sessions

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Record metrics
            await self.monitoring.record_metric(
                "session_cleanup_total_cleaned",
                cleaned_sessions,
                {"cleanup_type": "expired"},
            )

            await self.monitoring.record_metric(
                "session_cleanup_space_freed",
                space_freed_mb,
                {"cleanup_type": "expired"},
            )

            await self.monitoring.record_metric(
                "session_cleanup_processing_time",
                processing_time,
                {"cleanup_type": "expired"},
            )

            result = SessionCleanupResult(
                total_sessions=total_sessions,
                expired_sessions=expired_sessions,
                inactive_sessions=inactive_sessions,
                orphaned_sessions=orphaned_sessions,
                cleaned_sessions=cleaned_sessions,
                space_freed_mb=space_freed_mb,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                "Expired sessions cleanup completed",
                {
                    "total_sessions": total_sessions,
                    "cleaned_sessions": cleaned_sessions,
                    "expired_sessions": expired_sessions,
                    "inactive_sessions": inactive_sessions,
                    "orphaned_sessions": orphaned_sessions,
                    "space_freed_mb": space_freed_mb,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Session cleanup failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                "Expired sessions cleanup failed",
                {"error": str(e), "processing_time_seconds": processing_time},
            )

            raise

    async def cleanup_old_executions_job(
        self, days: int = 30
    ) -> ExecutionCleanupResult:
        """Clean up old agent executions."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting old executions cleanup for {days} days",
                {
                    "days": days,
                    "job_type": "cleanup_old_executions",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get execution service
            from ..agents.core.execution import get_execution_service

            execution_service = get_execution_service()

            # Get execution statistics
            execution_stats = await execution_service.get_execution_statistics()
            total_executions = execution_stats.get("total_executions", 0)

            # Clean old executions
            cleanup_result = await execution_service.cleanup_old_executions(days)
            old_executions = cleanup_result.get("cleaned_count", 0)
            space_freed_mb = cleanup_result.get("space_freed_mb", 0.0)

            # Clean failed executions
            failed_result = await execution_service.cleanup_failed_executions(days)
            failed_executions = failed_result.get("cleaned_count", 0)
            space_freed_mb += failed_result.get("space_freed_mb", 0.0)

            # Clean completed executions
            completed_result = await execution_service.cleanup_completed_executions(
                days
            )
            completed_executions = completed_result.get("cleaned_count", 0)
            space_freed_mb += completed_result.get("space_freed_mb", 0.0)

            cleaned_executions = (
                old_executions + failed_executions + completed_executions
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Record metrics
            await self.monitoring.record_metric(
                "execution_cleanup_total_cleaned",
                cleaned_executions,
                {"cleanup_type": "old", "days": days},
            )

            await self.monitoring.record_metric(
                "execution_cleanup_space_freed",
                space_freed_mb,
                {"cleanup_type": "old", "days": days},
            )

            await self.monitoring.record_metric(
                "execution_cleanup_processing_time",
                processing_time,
                {"cleanup_type": "old", "days": days},
            )

            result = ExecutionCleanupResult(
                total_executions=total_executions,
                old_executions=old_executions,
                failed_executions=failed_executions,
                completed_executions=completed_executions,
                cleaned_executions=cleaned_executions,
                space_freed_mb=space_freed_mb,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Old executions cleanup completed for {days} days",
                {
                    "days": days,
                    "total_executions": total_executions,
                    "cleaned_executions": cleaned_executions,
                    "old_executions": old_executions,
                    "failed_executions": failed_executions,
                    "completed_executions": completed_executions,
                    "space_freed_mb": space_freed_mb,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Execution cleanup failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Old executions cleanup failed for {days} days",
                {
                    "days": days,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def vacuum_database_job(self) -> DatabaseMaintenanceResult:
        """Vacuum and optimize database."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                "Starting database vacuum",
                {"job_type": "vacuum_database", "started_at": start_time.isoformat()},
            )

            # Get database service
            from ..core.database import get_database_service

            database_service = get_database_service()

            # Get database statistics before vacuum
            before_stats = await database_service.get_database_statistics()

            # Vacuum database
            vacuum_result = await database_service.vacuum_database()

            # Optimize tables
            tables_optimized = []
            tables = await database_service.get_table_list()

            for table in tables:
                try:
                    await database_service.optimize_table(table)
                    tables_optimized.append(table)
                except Exception as e:
                    errors.append(f"Failed to optimize table {table}: {str(e)}")

            # Rebuild indexes
            indexes_rebuilt = []
            indexes = await database_service.get_index_list()

            for index in indexes:
                try:
                    await database_service.rebuild_index(index)
                    indexes_rebuilt.append(index)
                except Exception as e:
                    errors.append(f"Failed to rebuild index {index}: {str(e)}")

            # Update statistics
            statistics_updated = []
            for table in tables:
                try:
                    await database_service.update_table_statistics(table)
                    statistics_updated.append(table)
                except Exception as e:
                    errors.append(
                        f"Failed to update statistics for table {table}: {str(e)}"
                    )

            # Get database statistics after vacuum
            after_stats = await database_service.get_database_statistics()

            # Calculate improvements
            space_freed_mb = before_stats.get("total_size_mb", 0) - after_stats.get(
                "total_size_mb", 0
            )
            performance_improvement = vacuum_result.get("performance_improvement", 0.0)

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Record metrics
            await self.monitoring.record_metric(
                "database_vacuum_space_freed", space_freed_mb, {"operation": "vacuum"}
            )

            await self.monitoring.record_metric(
                "database_vacuum_performance_improvement",
                performance_improvement,
                {"operation": "vacuum"},
            )

            await self.monitoring.record_metric(
                "database_vacuum_processing_time",
                processing_time,
                {"operation": "vacuum"},
            )

            result = DatabaseMaintenanceResult(
                tables_optimized=tables_optimized,
                indexes_rebuilt=indexes_rebuilt,
                statistics_updated=statistics_updated,
                space_freed_mb=space_freed_mb,
                performance_improvement=performance_improvement,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                "Database vacuum completed",
                {
                    "tables_optimized": len(tables_optimized),
                    "indexes_rebuilt": len(indexes_rebuilt),
                    "statistics_updated": len(statistics_updated),
                    "space_freed_mb": space_freed_mb,
                    "performance_improvement": performance_improvement,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Database vacuum failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                "Database vacuum failed",
                {"error": str(e), "processing_time_seconds": processing_time},
            )

            raise

    async def system_maintenance_job(self) -> SystemMaintenanceResult:
        """Perform system-wide maintenance."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                "Starting system maintenance",
                {
                    "job_type": "system_maintenance",
                    "started_at": start_time.isoformat(),
                },
            )

            cache_cleared = False
            logs_rotated = False
            temp_files_cleaned = False
            disk_space_freed_mb = 0.0
            memory_optimized = False

            # Clear caches
            try:
                from ..redis.cache import get_cache_service

                cache_service = get_cache_service()
                await cache_service.clear_all_caches()
                cache_cleared = True
            except Exception as e:
                errors.append(f"Failed to clear caches: {str(e)}")

            # Rotate logs
            try:
                from ..infrastructure.logging import get_cloud_logging

                logging_service = get_cloud_logging()
                await logging_service.rotate_logs()
                logs_rotated = True
            except Exception as e:
                errors.append(f"Failed to rotate logs: {str(e)}")

            # Clean temporary files
            try:
                from ..core.file_service import get_file_service

                file_service = get_file_service()
                cleanup_result = await file_service.cleanup_temp_files()
                temp_files_cleaned = True
                disk_space_freed_mb += cleanup_result.get("space_freed_mb", 0.0)
            except Exception as e:
                errors.append(f"Failed to clean temporary files: {str(e)}")

            # Optimize memory
            try:
                import gc
                import sys

                # Force garbage collection
                collected = gc.collect()

                # Get memory usage before and after
                memory_before = sys.getsizeof(gc.get_objects())
                gc.collect()
                memory_after = sys.getsizeof(gc.get_objects())

                memory_optimized = memory_after < memory_before

            except Exception as e:
                errors.append(f"Failed to optimize memory: {str(e)}")

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Record metrics
            await self.monitoring.record_metric(
                "system_maintenance_disk_space_freed",
                disk_space_freed_mb,
                {"operation": "maintenance"},
            )

            await self.monitoring.record_metric(
                "system_maintenance_processing_time",
                processing_time,
                {"operation": "maintenance"},
            )

            result = SystemMaintenanceResult(
                cache_cleared=cache_cleared,
                logs_rotated=logs_rotated,
                temp_files_cleaned=temp_files_cleaned,
                disk_space_freed_mb=disk_space_freed_mb,
                memory_optimized=memory_optimized,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                "System maintenance completed",
                {
                    "cache_cleared": cache_cleared,
                    "logs_rotated": logs_rotated,
                    "temp_files_cleaned": temp_files_cleaned,
                    "disk_space_freed_mb": disk_space_freed_mb,
                    "memory_optimized": memory_optimized,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"System maintenance failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                "System maintenance failed",
                {"error": str(e), "processing_time_seconds": processing_time},
            )

            raise

    async def backup_system_job(self) -> Dict[str, Any]:
        """Create system backup."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                "Starting system backup",
                {"job_type": "backup_system", "started_at": start_time.isoformat()},
            )

            backup_results = {}

            # Backup database
            try:
                from ..core.database import get_database_service

                database_service = get_database_service()
                db_backup = await database_service.create_backup()
                backup_results["database"] = db_backup
            except Exception as e:
                errors.append(f"Failed to backup database: {str(e)}")

            # Backup Redis data
            try:
                from ..redis.client import get_redis_client

                redis_client = get_redis_client()
                redis_backup = await redis_client.create_backup()
                backup_results["redis"] = redis_backup
            except Exception as e:
                errors.append(f"Failed to backup Redis: {str(e)}")

            # Backup file storage
            try:
                from ..infrastructure.storage import get_cloud_storage

                storage_service = get_cloud_storage()
                storage_backup = await storage_service.create_backup()
                backup_results["storage"] = storage_backup
            except Exception as e:
                errors.append(f"Failed to backup storage: {str(e)}")

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Record metrics
            await self.monitoring.record_metric(
                "system_backup_processing_time",
                processing_time,
                {"operation": "backup"},
            )

            result = {
                "backup_results": backup_results,
                "processing_time_seconds": processing_time,
                "errors": errors,
            }

            # Log completion
            await self.logging.log_structured(
                "INFO",
                "System backup completed",
                {
                    "backup_count": len(backup_results),
                    "processing_time_seconds": processing_time,
                    "error_count": len(errors),
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"System backup failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                "System backup failed",
                {"error": str(e), "processing_time_seconds": processing_time},
            )

            raise

    async def health_check_job(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                "Starting comprehensive health check",
                {"job_type": "health_check", "started_at": start_time.isoformat()},
            )

            health_results = {}

            # Check database health
            try:
                from ..core.database import get_database_service

                database_service = get_database_service()
                db_health = await database_service.health_check()
                health_results["database"] = db_health
            except Exception as e:
                errors.append(f"Database health check failed: {str(e)}")
                health_results["database"] = {"status": "unhealthy", "error": str(e)}

            # Check Redis health
            try:
                from ..redis.client import get_redis_client

                redis_client = get_redis_client()
                redis_health = await redis_client.health_check()
                health_results["redis"] = redis_health
            except Exception as e:
                errors.append(f"Redis health check failed: {str(e)}")
                health_results["redis"] = {"status": "unhealthy", "error": str(e)}

            # Check storage health
            try:
                from ..infrastructure.storage import get_cloud_storage

                storage_service = get_cloud_storage()
                storage_health = await storage_service.health_check()
                health_results["storage"] = storage_health
            except Exception as e:
                errors.append(f"Storage health check failed: {str(e)}")
                health_results["storage"] = {"status": "unhealthy", "error": str(e)}

            # Check agent system health
            try:
                from ..agents.core.registry import get_agent_registry

                agent_registry = get_agent_registry()
                agent_health = await agent_registry.health_check()
                health_results["agents"] = agent_health
            except Exception as e:
                errors.append(f"Agent system health check failed: {str(e)}")
                health_results["agents"] = {"status": "unhealthy", "error": str(e)}

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Calculate overall health
            healthy_services = sum(
                1
                for service in health_results.values()
                if service.get("status") == "healthy"
            )
            total_services = len(health_results)
            overall_health = (
                "healthy"
                if healthy_services == total_services
                else "degraded" if healthy_services > 0 else "unhealthy"
            )

            # Record metrics
            await self.monitoring.record_metric(
                "health_check_processing_time",
                processing_time,
                {"operation": "health_check"},
            )

            await self.monitoring.record_metric(
                "health_check_healthy_services",
                healthy_services,
                {"total_services": total_services},
            )

            result = {
                "overall_health": overall_health,
                "healthy_services": healthy_services,
                "total_services": total_services,
                "health_results": health_results,
                "processing_time_seconds": processing_time,
                "errors": errors,
            }

            # Log completion
            await self.logging.log_structured(
                "INFO",
                "Comprehensive health check completed",
                {
                    "overall_health": overall_health,
                    "healthy_services": healthy_services,
                    "total_services": total_services,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Health check failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                "Comprehensive health check failed",
                {"error": str(e), "processing_time_seconds": processing_time},
            )

            raise


# Create global instance
_maintenance_jobs = MaintenanceJobs()


# Job implementations with decorators
@daily_job(
    hour=3,
    minute=0,
    queue="maintenance",
    retries=2,
    timeout=1800,  # 30 minutes
    description="Clean up expired sessions",
)
async def cleanup_expired_sessions_job() -> Dict[str, Any]:
    """Clean up expired sessions job."""
    result = await _maintenance_jobs.cleanup_expired_sessions_job()
    return result.__dict__


@daily_job(
    hour=4,
    minute=0,
    queue="maintenance",
    retries=2,
    timeout=3600,  # 1 hour
    description="Clean up old executions",
)
async def cleanup_old_executions_job(days: int = 30) -> Dict[str, Any]:
    """Clean up old executions job."""
    result = await _maintenance_jobs.cleanup_old_executions_job(days)
    return result.__dict__


@weekly_job(
    day_of_week=6,  # Saturday
    hour=2,
    minute=0,
    queue="maintenance",
    retries=2,
    timeout=7200,  # 2 hours
    description="Vacuum database",
)
async def vacuum_database_job() -> Dict[str, Any]:
    """Vacuum database job."""
    result = await _maintenance_jobs.vacuum_database_job()
    return result.__dict__


@daily_job(
    hour=5,
    minute=0,
    queue="maintenance",
    retries=2,
    timeout=1800,  # 30 minutes
    description="System maintenance",
)
async def system_maintenance_job() -> Dict[str, Any]:
    """System maintenance job."""
    result = await _maintenance_jobs.system_maintenance_job()
    return result.__dict__


@daily_job(
    hour=6,
    minute=0,
    queue="maintenance",
    retries=2,
    timeout=3600,  # 1 hour
    description="System backup",
)
async def backup_system_job() -> Dict[str, Any]:
    """System backup job."""
    result = await _maintenance_jobs.backup_system_job()
    return result


@hourly_job(
    minute=0,
    queue="maintenance",
    retries=1,
    timeout=300,  # 5 minutes
    description="Health check",
)
async def health_check_job() -> Dict[str, Any]:
    """Health check job."""
    result = await _maintenance_jobs.health_check_job()
    return result


# Convenience functions
async def cleanup_sessions() -> SessionCleanupResult:
    """Clean up expired sessions."""
    return await _maintenance_jobs.cleanup_expired_sessions_job()


async def cleanup_executions(days: int = 30) -> ExecutionCleanupResult:
    """Clean up old executions."""
    return await _maintenance_jobs.cleanup_old_executions_job(days)


async def vacuum_database() -> DatabaseMaintenanceResult:
    """Vacuum and optimize database."""
    return await _maintenance_jobs.vacuum_database_job()


async def perform_system_maintenance() -> SystemMaintenanceResult:
    """Perform system maintenance."""
    return await _maintenance_jobs.system_maintenance_job()


async def backup_system() -> Dict[str, Any]:
    """Create system backup."""
    return await _maintenance_jobs.backup_system_job()


async def check_system_health() -> Dict[str, Any]:
    """Check system health."""
    return await _maintenance_jobs.health_check_job()


# Export all jobs
__all__ = [
    "MaintenanceJobs",
    "cleanup_expired_sessions_job",
    "cleanup_old_executions_job",
    "vacuum_database_job",
    "system_maintenance_job",
    "backup_system_job",
    "health_check_job",
    "cleanup_sessions",
    "cleanup_executions",
    "vacuum_database",
    "perform_system_maintenance",
    "backup_system",
    "check_system_health",
]
