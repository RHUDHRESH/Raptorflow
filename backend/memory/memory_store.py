"""
Memory store with TTL management and cleanup operations.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from working_memory import get_working_memory

from .exceptions import DatabaseError, ValidationError
from .redis_client import get_redis_client

logger = logging.getLogger(__name__)


@dataclass
class MemoryCleanupTask:
    """Memory cleanup task configuration."""

    task_id: str
    workspace_id: str
    task_type: str  # 'expired_sessions', 'expired_items', 'cleanup_workspace'
    scheduled_at: datetime
    executed_at: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class MemoryStore:
    """High-level memory store with TTL management and cleanup."""

    def __init__(self):
        self.redis_client = None
        self.working_memory = None
        self.cleanup_tasks: Dict[str, MemoryCleanupTask] = {}
        self.cleanup_interval = 300  # 5 minutes
        self.default_ttl = 3600  # 1 hour
        self.session_ttl = 86400  # 24 hours
        self.item_ttl = 1800  # 30 minutes

        # Cleanup configuration
        self.max_cleanup_tasks = 100
        self.cleanup_task_ttl = 3600  # 1 hour

        # Cleanup callbacks
        self.cleanup_callbacks: Dict[str, List[Callable]] = {
            "before_cleanup": [],
            "after_cleanup": [],
            "on_error": [],
        }

    async def initialize(self):
        """Initialize memory store."""
        try:
            self.redis_client = await get_redis_client()
            self.working_memory = await get_working_memory()

            # Start cleanup scheduler
            asyncio.create_task(self._cleanup_scheduler())

            logger.info("Memory store initialized")

        except Exception as e:
            logger.error(f"Failed to initialize memory store: {e}")
            raise DatabaseError(f"Memory store initialization failed: {str(e)}")

    async def store(
        self,
        key: str,
        value: Any,
        workspace_id: str,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Store a value with automatic TTL management."""
        try:
            # Validate inputs
            if not key or not workspace_id:
                raise ValidationError("Key and workspace_id are required")

            # Set default TTL
            ttl = ttl or self.default_ttl

            # Add metadata
            if metadata is None:
                metadata = {}

            metadata.update(
                {
                    "stored_at": datetime.now().isoformat(),
                    "ttl": ttl,
                    "tags": tags or [],
                    "workspace_id": workspace_id,
                }
            )

            # Store in Redis
            success = await self.redis_client.set(
                key=key, value=value, ttl=ttl, workspace_id=workspace_id
            )

            if success:
                logger.debug(
                    f"Stored key {key} for workspace {workspace_id} with TTL {ttl}s"
                )

            return success

        except Exception as e:
            logger.error(f"Failed to store key {key}: {e}")
            raise DatabaseError(f"Memory store operation failed: {str(e)}")

    async def retrieve(
        self, key: str, workspace_id: str, update_access: bool = True
    ) -> Optional[Any]:
        """Retrieve a value with access tracking."""
        try:
            # Validate inputs
            if not key or not workspace_id:
                raise ValidationError("Key and workspace_id are required")

            # Get from Redis
            value = await self.redis_client.get(key, workspace_id=workspace_id)

            if value is None:
                return None

            # Update access metadata if requested
            if update_access and isinstance(value, dict):
                value["last_accessed"] = datetime.now().isoformat()
                value["access_count"] = value.get("access_count", 0) + 1

                # Update in Redis
                await self.redis_client.set(
                    key=key,
                    value=value,
                    workspace_id=workspace_id,
                    ttl=value.get("ttl"),
                )

            return value

        except Exception as e:
            logger.error(f"Failed to retrieve key {key}: {e}")
            raise DatabaseError(f"Memory retrieve operation failed: {str(e)}")

    async def delete(self, key: str, workspace_id: str) -> bool:
        """Delete a value."""
        try:
            # Validate inputs
            if not key or not workspace_id:
                raise ValidationError("Key and workspace_id are required")

            # Delete from Redis
            success = await self.redis_client.delete(key, workspace_id=workspace_id)

            if success:
                logger.debug(f"Deleted key {key} for workspace {workspace_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            raise DatabaseError(f"Memory delete operation failed: {str(e)}")

    async def exists(self, key: str, workspace_id: str) -> bool:
        """Check if a key exists."""
        try:
            # Validate inputs
            if not key or not workspace_id:
                raise ValidationError("Key and workspace_id are required")

            return await self.redis_client.exists(key, workspace_id=workspace_id)

        except Exception as e:
            logger.error(f"Failed to check existence of key {key}: {e}")
            raise DatabaseError(f"Memory exists operation failed: {str(e)}")

    async def set_ttl(self, key: str, workspace_id: str, ttl: int) -> bool:
        """Set TTL for a key."""
        try:
            # Validate inputs
            if not key or not workspace_id:
                raise ValidationError("Key and workspace_id are required")

            if ttl <= 0:
                raise ValidationError("TTL must be positive")

            success = await self.redis_client.expire(
                key, ttl, workspace_id=workspace_id
            )

            if success:
                # Update metadata
                value = await self.retrieve(key, workspace_id, update_access=False)
                if value and isinstance(value, dict):
                    value["ttl"] = ttl
                    value["ttl_updated_at"] = datetime.now().isoformat()
                    await self.redis_client.set(
                        key=key, value=value, workspace_id=workspace_id, ttl=ttl
                    )

            return success

        except Exception as e:
            logger.error(f"Failed to set TTL for key {key}: {e}")
            raise DatabaseError(f"Memory TTL operation failed: {str(e)}")

    async def get_ttl(self, key: str, workspace_id: str) -> int:
        """Get TTL for a key."""
        try:
            # Validate inputs
            if not key or not workspace_id:
                raise ValidationError("Key and workspace_id are required")

            return await self.redis_client.ttl(key, workspace_id=workspace_id)

        except Exception as e:
            logger.error(f"Failed to get TTL for key {key}: {e}")
            raise DatabaseError(f"Memory TTL operation failed: {str(e)}")

    async def list_keys(
        self, workspace_id: str, pattern: str = "*", include_metadata: bool = False
    ) -> List[Dict[str, Any]]:
        """List keys for a workspace."""
        try:
            # Validate inputs
            if not workspace_id:
                raise ValidationError("Workspace ID is required")

            # Get keys
            keys = await self.redis_client.keys(pattern, workspace_id=workspace_id)

            if not include_metadata:
                return [{"key": key} for key in keys]

            # Get metadata for each key
            key_info = []
            for key in keys:
                value = await self.retrieve(key, workspace_id, update_access=False)
                if value and isinstance(value, dict):
                    key_info.append(
                        {
                            "key": key,
                            "metadata": {
                                "stored_at": value.get("stored_at"),
                                "ttl": value.get("ttl"),
                                "tags": value.get("tags", []),
                                "access_count": value.get("access_count", 0),
                                "last_accessed": value.get("last_accessed"),
                            },
                        }
                    )
                else:
                    key_info.append({"key": key, "metadata": {}})

            return key_info

        except Exception as e:
            logger.error(f"Failed to list keys for workspace {workspace_id}: {e}")
            raise DatabaseError(f"Memory list operation failed: {str(e)}")

    async def cleanup_workspace(
        self, workspace_id: str, force: bool = False
    ) -> Dict[str, Any]:
        """Clean up all memory for a workspace."""
        try:
            # Validate inputs
            if not workspace_id:
                raise ValidationError("Workspace ID is required")

            # Run cleanup callbacks
            await self._run_cleanup_callbacks(
                "before_cleanup", {"workspace_id": workspace_id, "force": force}
            )

            cleanup_result = {
                "workspace_id": workspace_id,
                "cleaned_keys": 0,
                "cleaned_sessions": 0,
                "errors": [],
            }

            try:
                # Flush workspace in Redis
                cleaned_keys = await self.redis_client.flush_workspace(workspace_id)
                cleanup_result["cleaned_keys"] = cleaned_keys

                # Clean up working memory sessions
                cleaned_sessions = await self.working_memory.cleanup_expired_sessions(
                    workspace_id
                )
                cleanup_result["cleaned_sessions"] = cleaned_sessions

                logger.info(
                    f"Cleaned workspace {workspace_id}: {cleaned_keys} keys, {cleaned_sessions} sessions"
                )

            except Exception as e:
                cleanup_result["errors"].append(str(e))
                logger.error(f"Error during workspace cleanup: {e}")

            # Run cleanup callbacks
            await self._run_cleanup_callbacks("after_cleanup", cleanup_result)

            return cleanup_result

        except Exception as e:
            logger.error(f"Failed to cleanup workspace {workspace_id}: {e}")
            raise DatabaseError(f"Memory workspace cleanup failed: {str(e)}")

    async def schedule_cleanup(
        self,
        workspace_id: str,
        task_type: str = "expired_sessions",
        delay_seconds: int = 0,
    ) -> str:
        """Schedule a cleanup task."""
        try:
            # Validate inputs
            if not workspace_id:
                raise ValidationError("Workspace ID is required")

            if task_type not in [
                "expired_sessions",
                "expired_items",
                "cleanup_workspace",
            ]:
                raise ValidationError(f"Invalid task type: {task_type}")

            # Generate task ID
            task_id = f"{workspace_id}:{task_type}:{datetime.now().timestamp()}"

            # Create task
            task = MemoryCleanupTask(
                task_id=task_id,
                workspace_id=workspace_id,
                task_type=task_type,
                scheduled_at=datetime.now() + timedelta(seconds=delay_seconds),
                status="pending",
            )

            # Store task
            self.cleanup_tasks[task_id] = task

            logger.info(
                f"Scheduled cleanup task {task_id} for workspace {workspace_id}"
            )
            return task_id

        except Exception as e:
            logger.error(f"Failed to schedule cleanup task: {e}")
            raise DatabaseError(f"Cleanup task scheduling failed: {str(e)}")

    async def execute_cleanup_task(self, task_id: str) -> Dict[str, Any]:
        """Execute a scheduled cleanup task."""
        try:
            # Get task
            task = self.cleanup_tasks.get(task_id)
            if not task:
                raise ValidationError(f"Cleanup task {task_id} not found")

            # Update status
            task.status = "running"
            task.executed_at = datetime.now()

            try:
                result = None

                if task.task_type == "expired_sessions":
                    result = await self._cleanup_expired_sessions(task.workspace_id)
                elif task.task_type == "expired_items":
                    result = await self._cleanup_expired_items(task.workspace_id)
                elif task.task_type == "cleanup_workspace":
                    result = await self.cleanup_workspace(task.workspace_id)

                task.status = "completed"
                task.result = result

                logger.info(f"Completed cleanup task {task_id}")

            except Exception as e:
                task.status = "failed"
                task.error = str(e)

                # Run error callbacks
                await self._run_cleanup_callbacks(
                    "on_error", {"task_id": task_id, "error": str(e)}
                )

                logger.error(f"Failed cleanup task {task_id}: {e}")
                raise

            return {
                "task_id": task_id,
                "status": task.status,
                "result": task.result,
                "error": task.error,
                "executed_at": (
                    task.executed_at.isoformat() if task.executed_at else None
                ),
            }

        except Exception as e:
            logger.error(f"Failed to execute cleanup task {task_id}: {e}")
            raise DatabaseError(f"Cleanup task execution failed: {str(e)}")

    async def get_cleanup_tasks(
        self, workspace_id: Optional[str] = None, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get cleanup tasks."""
        tasks = []

        for task_id, task in self.cleanup_tasks.items():
            if workspace_id and task.workspace_id != workspace_id:
                continue

            if status and task.status != status:
                continue

            tasks.append(
                {
                    "task_id": task.task_id,
                    "workspace_id": task.workspace_id,
                    "task_type": task.task_type,
                    "scheduled_at": task.scheduled_at.isoformat(),
                    "executed_at": (
                        task.executed_at.isoformat() if task.executed_at else None
                    ),
                    "status": task.status,
                    "result": task.result,
                    "error": task.error,
                }
            )

        return tasks

    async def get_memory_stats(self, workspace_id: str) -> Dict[str, Any]:
        """Get memory statistics for a workspace."""
        try:
            # Get Redis stats
            redis_stats = await self.redis_client.get_workspace_stats(workspace_id)

            # Get working memory stats
            working_memory_stats = await self.working_memory.get_workspace_stats(
                workspace_id
            )

            # Get cleanup task stats
            cleanup_tasks = await self.get_cleanup_tasks(workspace_id)
            cleanup_stats = {
                "total_tasks": len(cleanup_tasks),
                "pending_tasks": len(
                    [t for t in cleanup_tasks if t["status"] == "pending"]
                ),
                "running_tasks": len(
                    [t for t in cleanup_tasks if t["status"] == "running"]
                ),
                "completed_tasks": len(
                    [t for t in cleanup_tasks if t["status"] == "completed"]
                ),
                "failed_tasks": len(
                    [t for t in cleanup_tasks if t["status"] == "failed"]
                ),
            }

            return {
                "workspace_id": workspace_id,
                "redis": redis_stats,
                "working_memory": working_memory_stats,
                "cleanup": cleanup_stats,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(
                f"Failed to get memory stats for workspace {workspace_id}: {e}"
            )
            raise DatabaseError(f"Memory stats retrieval failed: {str(e)}")

    async def _cleanup_scheduler(self):
        """Background task to run scheduled cleanups."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)

                # Get pending tasks
                pending_tasks = [
                    task
                    for task in self.cleanup_tasks.values()
                    if task.status == "pending" and task.scheduled_at <= datetime.now()
                ]

                # Execute tasks
                for task in pending_tasks:
                    try:
                        await self.execute_cleanup_task(task.task_id)
                    except Exception as e:
                        logger.error(
                            f"Failed to execute cleanup task {task.task_id}: {e}"
                        )

                # Clean up old tasks
                await self._cleanup_old_tasks()

            except Exception as e:
                logger.error(f"Cleanup scheduler error: {e}")
                await asyncio.sleep(self.cleanup_interval)

    async def _cleanup_old_tasks(self):
        """Clean up old cleanup tasks."""
        cutoff_time = datetime.now() - timedelta(hours=24)

        old_tasks = [
            task_id
            for task_id, task in self.cleanup_tasks.items()
            if task.status in ["completed", "failed"]
            and task.executed_at
            and task.executed_at < cutoff_time
        ]

        for task_id in old_tasks:
            del self.cleanup_tasks[task_id]

        if old_tasks:
            logger.debug(f"Cleaned up {len(old_tasks)} old cleanup tasks")

    async def _cleanup_expired_sessions(self, workspace_id: str) -> Dict[str, Any]:
        """Clean up expired sessions."""
        return {
            "cleaned_sessions": await self.working_memory.cleanup_expired_sessions(
                workspace_id
            )
        }

    async def _cleanup_expired_items(self, workspace_id: str) -> Dict[str, Any]:
        """Clean up expired items."""
        return {
            "cleaned_items": await self.redis_client.cleanup_expired_keys(workspace_id)
        }

    async def _run_cleanup_callbacks(self, callback_type: str, data: Dict[str, Any]):
        """Run cleanup callbacks."""
        for callback in self.cleanup_callbacks.get(callback_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Cleanup callback {callback_type} failed: {e}")

    def add_cleanup_callback(self, callback_type: str, callback: Callable):
        """Add a cleanup callback."""
        if callback_type not in self.cleanup_callbacks:
            self.cleanup_callbacks[callback_type] = []

        self.cleanup_callbacks[callback_type].append(callback)
        logger.info(f"Added cleanup callback for {callback_type}")


# Global memory store instance
_memory_store: Optional[MemoryStore] = None


async def get_memory_store() -> MemoryStore:
    """Get or create memory store instance."""
    global _memory_store

    if _memory_store is None:
        _memory_store = MemoryStore()
        await _memory_store.initialize()

    return _memory_store
