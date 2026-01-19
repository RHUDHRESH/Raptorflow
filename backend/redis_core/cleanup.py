"""
Redis cleanup and maintenance utilities.

Provides automated cleanup of expired data, maintenance tasks,
and resource optimization for Redis instances.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .client import get_redis
from .keys import get_ttl_for_service
from .ttl_manager import get_ttl_manager

logger = logging.getLogger(__name__)


class CleanupTaskType(Enum):
    """Cleanup task types."""
    EXPIRED_SESSIONS = "expired_sessions"
    OLD_CACHE = "old_cache"
    STALE_LOCKS = "stale_locks"
    ORPHANED_TTL = "orphaned_ttl"
    MEMORY_FRAGMENTS = "memory_fragments"
    UNUSED_KEYS = "unused_keys"
    RATE_LIMIT_DATA = "rate_limit_data"
    QUEUE_CLEANUP = "queue_cleanup"
    METRICS_CLEANUP = "metrics_cleanup"


@dataclass
class CleanupTask:
    """Cleanup task configuration."""
    task_type: CleanupTaskType
    name: str
    description: str
    enabled: bool = True
    schedule_interval_seconds: int = 3600  # 1 hour
    last_run: Optional[datetime] = None
    cleanup_threshold: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.task_type, str):
            self.task_type = CleanupTaskType(self.task_type)


@dataclass
class CleanupResult:
    """Result of a cleanup operation."""
    task_type: CleanupTaskType
    task_name: str
    success: bool
    items_processed: int
    items_deleted: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    memory_freed_bytes: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CleanupStats:
    """Cleanup statistics."""
    total_tasks_run: int = 0
    total_items_processed: int = 0
    total_items_deleted: int = 0
    total_errors: int = 0
    total_warnings: int = 0
    total_memory_freed_bytes: int = 0
    last_cleanup: Optional[datetime] = None
    task_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class RedisCleanup:
    """Redis cleanup and maintenance manager."""

    def __init__(self):
        self.redis = get_redis()
        self.ttl_manager = get_ttl_manager()

        # Cleanup configuration
        self.cleanup_tasks: Dict[CleanupTaskType, CleanupTask] = {}
        self._setup_default_tasks()

        # Cleanup state
        self._running = False
        self._cleanup_task: Optional[asyncio.Task] = None
        self.cleanup_interval_seconds = 3600  # 1 hour

        # Statistics
        self.stats = CleanupStats()

        # Event handlers
        self.cleanup_callbacks: List[callable] = []

    def _setup_default_tasks(self):
        """Setup default cleanup tasks."""
        # Expired sessions cleanup
        self.cleanup_tasks[CleanupTaskType.EXPIRED_SESSIONS] = CleanupTask(
            task_type=CleanupTaskType.EXPIRED_SESSIONS,
            name="Expired Sessions Cleanup",
            description="Remove expired session data",
            schedule_interval_seconds=1800,  # 30 minutes
            cleanup_threshold={
                "max_age_hours": 24,
                "batch_size": 1000
            }
        )

        # Old cache cleanup
        self.cleanup_tasks[CleanupTaskType.OLD_CACHE] = CleanupTask(
            task_type=CleanupTaskType.OLD_CACHE,
            name="Old Cache Cleanup",
            description="Remove old cache entries",
            schedule_interval_seconds=7200,  # 2 hours
            cleanup_threshold={
                "max_age_hours": 24,
                "cache_types": ["default", "user", "workspace"]
            }
        )

        # Stale locks cleanup
        self.cleanup_tasks[CleanupTaskType.STALE_LOCKS] = CleanupTask(
            task_type=CleanupTaskType.STALE_LOCKS,
            name="Stale Locks Cleanup",
            description="Remove expired distributed locks",
            schedule_interval_seconds=600,  # 10 minutes
            cleanup_threshold={
                "max_age_minutes": 30,
                "lock_prefix": "lock:"
            }
        )

        # Orphaned TTL entries cleanup
        self.cleanup_tasks[CleanupTaskType.ORPHANED_TTL] = CleanupTask(
            task_type=CleanupTaskType.ORPHANED_TTL,
            name="Orphaned TTL Entries Cleanup",
            description="Remove TTL entries for non-existent keys",
            schedule_interval_seconds=3600,  # 1 hour
            cleanup_threshold={
                "batch_size": 1000
            }
        )

        # Rate limit data cleanup
        self.cleanup_tasks[CleanupTaskType.RATE_LIMIT_DATA] = CleanupTask(
            task_type=CleanupTaskType.RATE_LIMIT_DATA,
            name="Rate Limit Data Cleanup",
            description="Clean up old rate limit data",
            schedule_interval_seconds=3600,  # 1 hour
            cleanup_threshold={
                "max_age_hours": 1,
                "rate_limit_prefix": "rl:"
            }
        )

        # Queue cleanup
        self.cleanup_tasks[CleanupTaskType.QUEUE_CLEANUP] = CleanupTask(
            task_type=CleanupTaskType.QUEUE_CLEANUP,
            name="Queue Cleanup",
            description="Clean up old queue data",
            schedule_interval_seconds=1800,  # 30 minutes
            cleanup_threshold={
                "max_age_hours": 24,
                "queue_prefix": "queue:"
            }
        )

        # Metrics cleanup
        self.cleanup_tasks[CleanupTaskType.METRICS_CLEANUP] = CleanupTask(
            task_type=CleanupTaskType.METRICS_CLEANUP,
            name="Metrics Cleanup",
            description="Clean up old metrics data",
            schedule_interval_seconds=86400,  # 24 hours
            cleanup_threshold={
                "max_age_days": 7,
                "metrics_prefix": "metrics:"
            }
        )

    def add_cleanup_task(self, task: CleanupTask):
        """Add a cleanup task."""
        self.cleanup_tasks[task.task_type] = task
        logger.info(f"Added cleanup task: {task.name}")

    def remove_cleanup_task(self, task_type: CleanupTaskType):
        """Remove a cleanup task."""
        if task_type in self.cleanup_tasks:
            del self.cleanup_tasks[task_type]
            logger.info(f"Removed cleanup task: {task_type.value}")

    def enable_task(self, task_type: CleanupTaskType):
        """Enable a cleanup task."""
        if task_type in self.cleanup_tasks:
            self.cleanup_tasks[task_type].enabled = True
            logger.info(f"Enabled cleanup task: {task_type.value}")

    def disable_task(self, task_type: CleanupTaskType):
        """Disable a cleanup task."""
        if task_type in self.cleanup_tasks:
            self.cleanup_tasks[task_type].enabled = False
            logger.info(f"Disabled cleanup task: {task_type.value}")

    async def start_cleanup_scheduler(self):
        """Start the cleanup scheduler."""
        if self._running:
            return

        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info("Started Redis cleanup scheduler")

        try:
            await self._cleanup_task
        except asyncio.CancelledError:
            pass
        finally:
            self._running = False
            self._cleanup_task = None
            logger.info("Stopped Redis cleanup scheduler")

    async def stop_cleanup_scheduler(self):
        """Stop the scheduler."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None

        self._running = False
        logger.info("Stopped Redis cleanup scheduler")

    async def _cleanup_loop(self):
        """Main cleanup loop."""
        while self._running:
            try:
                # Run all enabled cleanup tasks
                for task in list(self.cleanup_tasks.values()):
                    if task.enabled:
                        await self._run_cleanup_task(task)

                # Update statistics
                self.stats.last_cleanup = datetime.now()

                # Sleep until next cleanup cycle
                await asyncio.sleep(self.cleanup_interval_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute

    async def _run_cleanup_task(self, task: CleanupTask) -> CleanupResult:
        """Run a specific cleanup task."""
        start_time = datetime.now()

        try:
            logger.info(f"Running cleanup task: {task.name}")

            # Route to specific cleanup method
            if task.task_type == CleanupTaskType.EXPIRED_SESSIONS:
                result = await self._cleanup_expired_sessions(task)
            elif task.task_type == CleanupTaskType.OLD_CACHE:
                result = await self._cleanup_old_cache(task)
            elif task.task_type == CleanupTaskType.STALE_LOCKS:
                result = await self._cleanup_stale_locks(task)
            elif task.task_type == CleanupTaskType.ORPHANED_TTL:
                result = await self._cleanup_orphaned_ttl(task)
            elif task.task_type == CleanupTaskType.RATE_LIMIT_DATA:
                result = await self._cleanup_rate_limit_data(task)
            elif task.task_type == CleanupTaskType.QUEUE_CLEANUP:
                result = await self._cleanup_queue_data(task)
            elif task.task_type == CleanupTaskType.METRICS_CLEANUP:
                result = await self._cleanup_metrics_data(task)
            else:
                result = CleanupResult(
                    task_type=task.task_type,
                    task_name=task.name,
                    success=False,
                    items_processed=0,
                    items_deleted=0,
                    errors=[f"Unknown task type: {task.task_type}"]
                )

            # Update task last run time
            task.last_run = datetime.now()

            # Update statistics
            self.stats.total_tasks_run += 1
            self.stats.total_items_processed += result.items_processed
            self.stats.total_items_deleted += result.items_deleted
            self.stats.total_errors += len(result.errors)
            self.stats.total_warnings += len(result.warnings)
            self.stats.total_memory_freed_bytes += result.memory_freed_bytes

            # Update task-specific stats
            if task.task_type.value not in self.stats.task_stats:
                self.stats.task_stats[task.task_type.value] = {
                    "total_runs": 0,
                    "total_processed": 0,
                    "total_deleted": 0,
                    "total_errors": 0,
                    "total_warnings": 0,
                    "last_run": None
                }

            task_stats = self.stats.task_stats[task.task_type.value]
            task_stats["total_runs"] += 1
            task_stats["total_processed"] += result.items_processed
            task_stats["total_deleted"] += result.items_deleted
            task_stats["total_errors"] += len(result.errors)
            task_stats["total_warnings"] += len(result.warnings)
            task_stats["last_run"] = task.last_run.isoformat() if task.last_run else None

            # Call cleanup callbacks
            for callback in self.cleanup_callbacks:
                try:
                    await callback(result)
                except Exception as e:
                    logger.error(f"Cleanup callback error: {e}")

            logger.info(f"Completed cleanup task {task.name}: {result.items_deleted} items deleted")

            return result

        except Exception as e:
            logger.error(f"Cleanup task {task.name} failed: {e}")

            return CleanupResult(
                task_type=task.task_type,
                task_name=task.name,
                success=False,
                items_processed=0,
                items_deleted=0,
                errors=[str(e)]
            )

    async def _cleanup_expired_sessions(self, task: CleanupTask) -> CleanupResult:
        """Clean up expired session data."""
        max_age_hours = task.cleanup_threshold.get("max_age_hours", 24)
        batch_size = task.cleanup_threshold.get("batch_size", 1000)

        try:
            # Get session TTL manager
            ttl_manager = get_ttl_manager()

            # Get expired sessions
            expired_entries = await ttl_manager.get_expired_keys("session")

            # Filter by age
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            recent_expired = [
                entry for entry in expired_entries
                if entry.expires_at > cutoff_time
            ]

            if not recent_expired:
                return CleanupResult(
                    task_type=task.task_type,
                    task_name=task.name,
                    success=True,
                    items_processed=0,
                    items_deleted=0
                )

            # Delete expired sessions in batches
            deleted_count = 0
            processed_count = 0
            errors = []

            for i in range(0, len(recent_expired), batch_size):
                batch = recent_expired[i:i + batch_size]

                for entry in batch:
                    try:
                        # Delete session key
                        session_key = f"session:{entry.key}"
                        await self.redis.delete(session_key)

                        # Remove from TTL index
                        await ttl_manager._remove_from_ttl_index(entry.key)

                        deleted_count += 1

                    except Exception as e:
                        errors.append(f"Failed to delete session {entry.key}: {e}")

                processed_count += len(batch)

                # Small delay to avoid overwhelming Redis
                if i + batch_size < len(recent_expired):
                    await asyncio.sleep(0.01)

            return CleanupResult(
                task_type=task.task_type,
                task_name=task.name,
                success=True,
                items_processed=processed_count,
                items_deleted=deleted_count,
                errors=errors
            )

        except Exception as e:
            return CleanupResult(
                task_type=task.task_type,
                task_name=task.name,
                success=False,
                items_processed=0,
                items_deleted=0,
                errors=[str(e)]
            )

    async def _cleanup_old_cache(self, task: CleanupTask) -> CleanupResult:
        """Clean up old cache entries."""
        max_age_hours = task.cleanup_threshold.get("max_age_hours", 24)
        cache_types = task.cleanup_threshold.get("cache_types", ["default"])

        try:
            # Get TTL manager
            ttl_manager = get_ttl_manager()

            deleted_count = 0
            processed_count = 0
            errors = []

            for cache_type in cache_types:
                # Get keys for this cache type
                keys = await ttl_manager.get_keys_by_service(cache_type)

                for key in keys:
                    try:
                        # Check TTL
                        ttl = await self.redis.ttl(key)

                        if ttl > 0:
                            # Convert TTL to hours
                            ttl_hours = ttl / 3600

                            if ttl_hours > max_age_hours:
                                # Delete old cache entry
                                await self.redis.delete(key)
                                await ttl_manager._remove_from_ttl_index(key)

                                deleted_count += 1

                        processed_count += 1

                    except Exception as e:
                        errors.append(f"Failed to process cache key {key}: {e}")

                # Small delay between cache types
                await asyncio.sleep(0.01)

            return CleanupResult(
                task_type=task.task_type,
                task_name=task.name,
                success=True,
                items_processed=processed_count,
                items_deleted=deleted_count,
                errors=errors
            )

        except Exception as e:
            return CleanupResult(
                task_type=task.task_type,
                task_name=task.name,
                success=False,
                items_processed=0,
                items_deleted=0,
                errors=[str(e)]
            )

    async def _cleanup_stale_locks(self, task: CleanupTask) -> CleanupResult:
        """Clean up stale distributed locks."""
        max_age_minutes = task.cleanup_threshold.get("max_age_minutes", 30)
        lock_prefix = task.cleanup_threshold.get("lock_prefix", "lock:")

        try:
            deleted_count = 0
            processed_count = 0
            errors = []

            known_locks = [
                "lock:agent_execution",
                "lock:queue_processing",
                "lock:cache_write",
                "lock:rate_limit_check"
            ]

            for lock_key in known_locks:
                try:
                    exists = await self.redis.exists(lock_key)

                    if exists:
                        lock_data = await self.redis.get(lock_key)

                        if lock_data:
                            parts = lock_data.split(":")
                            if len(parts) >= 3:
                                try:
                                    lock_timestamp = float(parts[2])
                                    current_time = datetime.now().timestamp()

                                    age_minutes = (current_time - lock_timestamp) / 60

                                    if age_minutes > max_age_minutes:
                                        await self.redis.delete(lock_key)
                                        deleted_count += 1

                                except (ValueError, IndexError):
                                    pass

                        processed_count += 1

                except Exception as e:
                    errors.append(f"Failed to process lock {lock_key}: {e}")

                await asyncio.sleep(0.01)

            return CleanupResult(
                task_type=task.task_type,
                task_name=task.name,
                success=True,
                items_processed=processed_count,
                items_deleted=deleted_count,
                errors=errors
            )

        except Exception as e:
            return CleanupResult(
                task_type=task.task_type,
                task_name=task.name,
                success=False,
                items_processed=0,
                items_deleted=0,
                errors=[str(e)]
            )

    async def _cleanup_orphaned_ttl(self, task: CleanupTask) -> CleanupResult:
        """Clean up orphaned TTL entries."""
        try:
            ttl_manager = get_ttl_manager()
            orphaned_count = await ttl_manager.cleanup_orphaned_ttl_entries()

            return CleanupResult(
                task_type=task.task_type,
                task_name=task.name,
                success=True,
                items_processed=orphaned_count,
                items_deleted=orphaned_count,
                errors=[]
            )

        except Exception as e:
            return CleanupResult(
                task_type=task.task_type,
                task_name=task.name,
                success=False,
                items_processed=0,
                items_deleted=0,
                errors=[str(e)]
            )

    async def _cleanup_rate_limit_data(self, task: CleanupTask) -> CleanupResult:
        """Clean up old rate limit data."""
        max_age_hours = task.cleanup_threshold.get("max_age_hours", 1)
        rate_limit_prefix = task.cleanup_threshold.get("rate_limit_prefix", "rl:")

        try:
            deleted_count = 0
            processed_count = 0
            errors = []

            known_rate_limit_keys = [
                "rl:user:api",
                "rl:user:agents",
                "rl:user:muse_generate",
                "rl:user:upload",
                "rl:user:export"
            ]

            for key in known_rate_limit_keys:
                try:
                    exists = await self.redis.exists(key)

                    if exists:
                        data = await self.redis.get_json(key)

                        if data:
                            if "timestamps" in data and data["timestamps"]:
                                oldest_timestamp = min(data["timestamps"])
                                current_time = datetime.now().timestamp()

                                age_hours = (current_time - oldest_timestamp) / 3600

                                if age_hours > max_age_hours:
                                    await self.redis.delete(key)
                                    deleted_count += 1

                        processed_count += 1

                except Exception as e:
                    errors.append(f"Failed to process rate limit key {key}: {e}")

                await asyncio.sleep(0.01)

            return CleanupResult(
                task_type=task.task_type,
                task_name=task.name,
                success=True,
                items_processed=processed_count,
                items_deleted=deleted_count,
                errors=errors
            )

        except Exception as e:
            return CleanupResult(
                task_type=task.task_type,
                task_name=task.name,
                success=False,
                items_processed=0,
                items_deleted=0,
                errors=[str(e)]
            )

    async def _cleanup_queue_data(self, task: CleanupTask) -> CleanupResult:
        """Clean up old queue data."""
        max_age_hours = task.cleanup_threshold.get("max_age_hours", 24)

        try:
            deleted_count = 0
            processed_count = 0
            errors = []

            known_queue_keys = [
                "queue:default",
                "queue:priority",
                "queue:processing",
                "queue:failed"
            ]

            for queue_key in known_queue_keys:
                try:
                    exists = await self.redis.exists(queue_key)

                    if exists:
                        length = await self.redis.llen(queue_key)

                        if length > 0:
                            oldest_item = await self.redis.lindex(queue_key, -1)
                            if oldest_item:
                                parts = oldest_item.split("|")
                                if len(parts) >= 3:
                                    try:
                                        timestamp = float(parts[2])
                                        current_time = datetime.now().timestamp()

                                        age_hours = (current_time - timestamp) / 3600

                                        if age_hours > max_age_hours:
                                            await self.redis.ltrim(queue_key, 1, 0)
                                            deleted_count += length
                                            length = 0

                                    except (ValueError, IndexError):
                                        pass

                            processed_count += 1

                    elif not exists:
                        processed_count += 1

                except Exception as e:
                    errors.append(f"Failed to process queue {queue_key}: {e}")

                await asyncio.sleep(0.01)

            return CleanupResult(
                task_type=task.task_type,
                task_name=task.name,
                success=True,
                items_processed=processed_count,
                items_deleted=deleted_count,
                errors=errors
            )

        except Exception as e:
            return CleanupResult(
                task_type=task.task_type,
                task_name=task.name,
                success=False,
                items_processed=0,
                items_deleted=0,
                errors=[str(e)]
            )

    async def _cleanup_metrics_data(self, task: CleanupTask) -> CleanupResult:
        """Clean up old metrics data."""
        max_age_days = task.cleanup_threshold.get("max_age_days", 7)

        try:
            deleted_count = 0
            processed_count = 0
            errors = []

            known_metrics_keys = [
                "metrics:ops_per_sec",
                "metrics:memory_usage",
                "metrics:hit_rate",
                "metrics:error_rate"
            ]

            for metrics_key in known_metrics_keys:
                try:
                    exists = await self.redis.exists(metrics_key)

                    if exists:
                        data = await self.redis.get_json(metrics_key)

                        if data:
                            if "timestamp" in data:
                                timestamp = data["timestamp"]
                                current_time = datetime.now().timestamp()

                                age_days = (current_time - timestamp) / (24 * 3600)

                                if age_days > max_age_days:
                                    await self.redis.delete(metrics_key)
                                    deleted_count += 1

                                processed_count += 1

                    elif not exists:
                        processed_count += 1

                except Exception as e:
                    errors.append(f"Failed to process metrics key {metrics_key}: {e}")

                await asyncio.sleep(0.01)

            return CleanupResult(
                task_type=task.task_type,
                task_name=task.name,
                success=True,
                items_processed=processed_count,
                items_deleted=deleted_count,
                errors=errors
            )

        except Exception as e:
            return CleanupResult(
                task_type=task.task_type,
                task_name=task.name,
                success=False,
                items_processed=0,
                items_deleted=0,
                errors=[str(e)]
            )

    async def run_manual_cleanup(self, task_types: List[CleanupTaskType]) -> Dict[str, CleanupResult]:
        """Run manual cleanup for specified task types."""
        results = {}

        for task_type in task_types:
            if task_type in self.cleanup_tasks:
                task = self.cleanup_tasks[task_type]
                result = await self._run_cleanup_task(task)
                results[task_type.value] = result
            else:
                results[task_type.value] = CleanupResult(
                    task_type=task_type,
                    task_name="Unknown",
                    success=False,
                    items_processed=0,
                    items_deleted=0,
                    errors=[f"Task type {task_type.value} not found"]
                )

        return results

    async def run_all_cleanup(self) -> Dict[str, CleanupResult]:
        """Run all enabled cleanup tasks."""
        enabled_tasks = [
            task for task in self.cleanup_tasks.values()
            if task.enabled
        ]

        task_types = [task.task_type for task in enabled_tasks]
        return await self.run_manual_cleanup(task_types)

    async def force_cleanup(self, task_type: CleanupTaskType) -> CleanupResult:
        """Force run a cleanup task regardless of schedule."""
        if task_type in self.cleanup_tasks:
            task = self.cleanup_tasks[task_type]
            return await self._run_cleanup_task(task)
        else:
            return CleanupResult(
                task_type=task_type,
                task_name="Unknown",
                success=False,
                items_processed=0,
                items_deleted=0,
                errors=[f"Task type {task_type.value} not found"]
            )

    def get_cleanup_stats(self) -> CleanupStats:
        """Get cleanup statistics."""
        return self.stats

    def get_task_list(self) -> List[Dict[str, Any]]:
        """Get list of cleanup tasks."""
        return [
            {
                "task_type": task.task_type.value,
                "name": task.name,
                "description": task.description,
                "enabled": task.enabled,
                "schedule_interval_seconds": task.schedule_interval_seconds,
                "last_run": task.last_run.isoformat() if task.last_run else None,
                "cleanup_threshold": task.cleanup_threshold
            }
            for task in self.cleanup_tasks.values()
        ]

    def add_cleanup_callback(self, callback: callable):
        """Add cleanup callback."""
        self.cleanup_callbacks.append(callback)

    def remove_cleanup_callback(self, callback: callable):
        """Remove cleanup callback."""
        if callback in self.cleanup_callbacks:
            self.cleanup_callbacks.remove(callback)

    def is_running(self) -> bool:
        """Check if cleanup scheduler is running."""
        return self._running

    def get_cleanup_interval(self) -> int:
        """Get cleanup interval in seconds."""
        return self.cleanup_interval_seconds

    def set_cleanup_interval(self, seconds: int):
        """Set cleanup interval in seconds."""
        self.cleanup_interval_seconds = max(60, seconds)  # Minimum 1 minute


# Global cleanup instance
_redis_cleanup = RedisCleanup()


def get_redis_cleanup() -> RedisCleanup:
    """Get global Redis cleanup instance."""
    return _redis_cleanup


# Convenience functions
async def cleanup_expired_sessions() -> CleanupResult:
    """Clean up expired sessions."""
    return await _redis_cleanup.force_cleanup(CleanupTaskType.EXPIRED_SESSIONS)


async def cleanup_old_cache() -> CleanupResult:
    """Clean up old cache entries."""
    return await _redis_cleanup.force_cleanup(CleanupTaskType.OLD_CACHE)


async def cleanup_stale_locks() -> CleanupResult:
    """Clean up stale distributed locks."""
    return await _redis_cleanup.force_cleanup(CleanupTaskType.STALE_LOCKS)


async def cleanup_all() -> Dict[str, CleanupResult]:
    """Run all cleanup tasks."""
    return await _redis_cleanup.run_all_cleanup()


async def start_cleanup_scheduler():
    """Start cleanup scheduler."""
    await _redis_cleanup.start_cleanup_scheduler()


async def stop_cleanup_scheduler():
    """Stop cleanup scheduler."""
    await _redis_cleanup.stop_cleanup_scheduler()


async def get_cleanup_stats() -> CleanupStats:
    """Get cleanup statistics."""
    return _redis_cleanup.get_cleanup_stats()