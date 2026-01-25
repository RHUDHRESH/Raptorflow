"""
Enhanced resource management system for Raptorflow backend.
Provides automatic leak detection, cleanup automation, and resource monitoring.
"""

import asyncio
import gc
import logging

import psutil

try:
    import resource
except ImportError:

    class _DummyResource:
        RUSAGE_SELF = 0

        @staticmethod
        def getrusage(_):
            # Provide zeroed fields similar to resource.struct_rusage
            return type(
                "RUsage",
                (),
                {
                    "ru_maxrss": 0,
                    "ru_utime": 0,
                    "ru_stime": 0,
                    "ru_ixrss": 0,
                    "ru_idrss": 0,
                    "ru_isrss": 0,
                },
            )()

    resource = _DummyResource()
import threading
import time
import tracemalloc
import weakref
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources that can be managed."""

    MEMORY = "memory"
    FILE_HANDLE = "file_handle"
    NETWORK_CONNECTION = "network_connection"
    DATABASE_CONNECTION = "database_connection"
    ASYNC_TASK = "async_task"
    THREAD = "thread"
    PROCESS = "process"
    CACHE = "cache"
    LOCK = "lock"
    TEMPORARY_FILE = "temporary_file"


class ResourceStatus(Enum):
    """Status of a managed resource."""

    ACTIVE = "active"
    IDLE = "idle"
    LEAKED = "leaked"
    CLEANED_UP = "cleaned_up"
    ERROR = "error"


@dataclass
class ResourceInfo:
    """Information about a managed resource."""

    resource_id: str
    resource_type: ResourceType
    created_at: datetime
    last_accessed: datetime
    status: ResourceStatus
    size_bytes: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    cleanup_callback: Optional[Callable] = None
    owner: Optional[str] = None
    workspace_id: Optional[str] = None
    access_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type.value,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "status": self.status.value,
            "size_bytes": self.size_bytes,
            "metadata": self.metadata,
            "owner": self.owner,
            "workspace_id": self.workspace_id,
            "access_count": self.access_count,
        }


@dataclass
class ResourceLeak:
    """Information about a detected resource leak."""

    resource_id: str
    resource_type: ResourceType
    leak_detected_at: datetime
    leak_duration_seconds: float
    severity: str  # "low", "medium", "high", "critical"
    description: str
    suggested_action: str
    resource_info: ResourceInfo

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type.value,
            "leak_detected_at": self.leak_detected_at.isoformat(),
            "leak_duration_seconds": self.leak_duration_seconds,
            "severity": self.severity,
            "description": self.description,
            "suggested_action": self.suggested_action,
            "resource_info": self.resource_info.to_dict(),
        }


@dataclass
class ResourceQuota:
    """Resource quota configuration."""

    resource_type: ResourceType
    max_count: int
    max_size_bytes: Optional[int] = None
    max_age_seconds: Optional[int] = None
    workspace_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "resource_type": self.resource_type.value,
            "max_count": self.max_count,
            "max_size_bytes": self.max_size_bytes,
            "max_age_seconds": self.max_age_seconds,
            "workspace_id": self.workspace_id,
        }


class ResourceCleanupStrategy(ABC):
    """Abstract base class for resource cleanup strategies."""

    @abstractmethod
    async def cleanup(self, resource_info: ResourceInfo) -> bool:
        """Clean up a resource. Return True if successful."""
        pass

    @abstractmethod
    def can_handle(self, resource_type: ResourceType) -> bool:
        """Check if this strategy can handle the resource type."""
        pass


class MemoryCleanupStrategy(ResourceCleanupStrategy):
    """Cleanup strategy for memory resources."""

    async def cleanup(self, resource_info: ResourceInfo) -> bool:
        """Clean up memory resources."""
        try:
            # Force garbage collection
            gc.collect()

            # Clear memory if we have a reference
            if "memory_ref" in resource_info.metadata:
                memory_ref = resource_info.metadata["memory_ref"]
                if isinstance(memory_ref, weakref.ref):
                    obj = memory_ref()
                    if obj:
                        del obj

            return True
        except Exception as e:
            logger.error(f"Memory cleanup failed for {resource_info.resource_id}: {e}")
            return False

    def can_handle(self, resource_type: ResourceType) -> bool:
        """Check if this strategy can handle memory resources."""
        return resource_type == ResourceType.MEMORY


class FileHandleCleanupStrategy(ResourceCleanupStrategy):
    """Cleanup strategy for file handles."""

    async def cleanup(self, resource_info: ResourceInfo) -> bool:
        """Clean up file handle resources."""
        try:
            if "file_handle" in resource_info.metadata:
                file_handle = resource_info.metadata["file_handle"]
                if hasattr(file_handle, "close"):
                    file_handle.close()
                elif hasattr(file_handle, "terminate"):
                    file_handle.terminate()

            # Remove temporary files
            if resource_info.resource_type == ResourceType.TEMPORARY_FILE:
                import os

                file_path = resource_info.metadata.get("file_path")
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)

            return True
        except Exception as e:
            logger.error(
                f"File handle cleanup failed for {resource_info.resource_id}: {e}"
            )
            return False

    def can_handle(self, resource_type: ResourceType) -> bool:
        """Check if this strategy can handle file resources."""
        return resource_type in [ResourceType.FILE_HANDLE, ResourceType.TEMPORARY_FILE]


class AsyncTaskCleanupStrategy(ResourceCleanupStrategy):
    """Cleanup strategy for async tasks."""

    async def cleanup(self, resource_info: ResourceInfo) -> bool:
        """Clean up async task resources."""
        try:
            if "task" in resource_info.metadata:
                task = resource_info.metadata["task"]
                if isinstance(task, asyncio.Task):
                    if not task.done():
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass

            return True
        except Exception as e:
            logger.error(
                f"Async task cleanup failed for {resource_info.resource_id}: {e}"
            )
            return False

    def can_handle(self, resource_type: ResourceType) -> bool:
        """Check if this strategy can handle async tasks."""
        return resource_type == ResourceType.ASYNC_TASK


class ResourceManager:
    """Enhanced resource manager with leak detection and automatic cleanup."""

    def __init__(self, leak_check_interval: int = 60, cleanup_interval: int = 300):
        self.leak_check_interval = leak_check_interval
        self.cleanup_interval = cleanup_interval

        # Resource tracking
        self.resources: Dict[str, ResourceInfo] = {}
        self.resources_by_type: Dict[ResourceType, Set[str]] = defaultdict(set)
        self.resources_by_owner: Dict[str, Set[str]] = defaultdict(set)
        self.resources_by_workspace: Dict[str, Set[str]] = defaultdict(set)

        # Leak detection
        self.detected_leaks: List[ResourceLeak] = []
        self.leak_thresholds = {
            ResourceType.MEMORY: 3600,  # 1 hour
            ResourceType.FILE_HANDLE: 1800,  # 30 minutes
            ResourceType.NETWORK_CONNECTION: 600,  # 10 minutes
            ResourceType.DATABASE_CONNECTION: 300,  # 5 minutes
            ResourceType.ASYNC_TASK: 1800,  # 30 minutes
            ResourceType.THREAD: 3600,  # 1 hour
            ResourceType.TEMPORARY_FILE: 900,  # 15 minutes
        }

        # Quota management
        self.quotas: Dict[str, ResourceQuota] = {}
        self.quota_violations: List[Dict[str, Any]] = []

        # Cleanup strategies
        self.cleanup_strategies: List[ResourceCleanupStrategy] = [
            MemoryCleanupStrategy(),
            FileHandleCleanupStrategy(),
            AsyncTaskCleanupStrategy(),
        ]

        # Background tasks
        self._background_tasks: Set[asyncio.Task] = set()
        self._running = False
        self._lock = asyncio.Lock()

        # Metrics
        self.metrics = {
            "total_resources_created": 0,
            "total_resources_cleaned": 0,
            "total_leaks_detected": 0,
            "total_quota_violations": 0,
            "cleanup_success_rate": 0.0,
            "leak_detection_rate": 0.0,
        }

        # Memory tracking
        self._memory_tracking_enabled = False
        self._memory_baseline = None

        logger.info(
            f"Resource manager initialized with leak check interval: {leak_check_interval}s"
        )

    async def start(self):
        """Start the resource manager background tasks."""
        if self._running:
            return

        self._running = True

        # Start background tasks
        self._background_tasks.add(asyncio.create_task(self._leak_detection_loop()))
        self._background_tasks.add(asyncio.create_task(self._cleanup_loop()))
        self._background_tasks.add(asyncio.create_task(self._quota_monitoring_loop()))
        self._background_tasks.add(asyncio.create_task(self._metrics_collection_loop()))

        # Enable memory tracking
        if not tracemalloc.is_tracing():
            tracemalloc.start()
            self._memory_tracking_enabled = True
            self._memory_baseline = tracemalloc.get_traced_memory()

        logger.info("Resource manager started")

    async def stop(self):
        """Stop the resource manager and clean up all resources."""
        self._running = False

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        self._background_tasks.clear()

        # Clean up all resources
        await self.cleanup_all_resources()

        # Stop memory tracking
        if self._memory_tracking_enabled:
            tracemalloc.stop()
            self._memory_tracking_enabled = False

        logger.info("Resource manager stopped")

    def register_resource(
        self,
        resource_id: str,
        resource_type: ResourceType,
        owner: Optional[str] = None,
        workspace_id: Optional[str] = None,
        size_bytes: Optional[int] = None,
        cleanup_callback: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Register a resource for tracking."""
        try:
            # Check quotas
            if not self._check_quota(resource_type, workspace_id):
                violation = {
                    "timestamp": datetime.now().isoformat(),
                    "resource_type": resource_type.value,
                    "workspace_id": workspace_id,
                    "violation_type": "quota_exceeded",
                }
                self.quota_violations.append(violation)
                self.metrics["total_quota_violations"] += 1
                logger.warning(
                    f"Quota violation for {resource_type.value} in workspace {workspace_id}"
                )
                return False

            # Create resource info
            resource_info = ResourceInfo(
                resource_id=resource_id,
                resource_type=resource_type,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                status=ResourceStatus.ACTIVE,
                size_bytes=size_bytes,
                cleanup_callback=cleanup_callback,
                owner=owner,
                workspace_id=workspace_id,
                metadata=metadata or {},
            )

            # Store resource
            self.resources[resource_id] = resource_info
            self.resources_by_type[resource_type].add(resource_id)

            if owner:
                self.resources_by_owner[owner].add(resource_id)

            if workspace_id:
                self.resources_by_workspace[workspace_id].add(resource_id)

            self.metrics["total_resources_created"] += 1

            logger.debug(
                f"Registered resource {resource_id} of type {resource_type.value}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to register resource {resource_id}: {e}")
            return False

    def unregister_resource(self, resource_id: str) -> bool:
        """Unregister a resource from tracking."""
        try:
            if resource_id not in self.resources:
                return False

            resource_info = self.resources[resource_id]

            # Remove from tracking structures
            del self.resources[resource_id]
            self.resources_by_type[resource_info.resource_type].discard(resource_id)

            if resource_info.owner:
                self.resources_by_owner[resource_info.owner].discard(resource_id)

            if resource_info.workspace_id:
                self.resources_by_workspace[resource_info.workspace_id].discard(
                    resource_id
                )

            # Update status
            resource_info.status = ResourceStatus.CLEANED_UP
            self.metrics["total_resources_cleaned"] += 1

            logger.debug(f"Unregistered resource {resource_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to unregister resource {resource_id}: {e}")
            return False

    def access_resource(self, resource_id: str) -> bool:
        """Mark a resource as accessed."""
        try:
            if resource_id not in self.resources:
                return False

            resource_info = self.resources[resource_id]
            resource_info.last_accessed = datetime.now()
            resource_info.access_count += 1

            # Update status if it was idle
            if resource_info.status == ResourceStatus.IDLE:
                resource_info.status = ResourceStatus.ACTIVE

            return True

        except Exception as e:
            logger.error(f"Failed to access resource {resource_id}: {e}")
            return False

    async def cleanup_resource(self, resource_id: str) -> bool:
        """Clean up a specific resource."""
        try:
            if resource_id not in self.resources:
                return False

            resource_info = self.resources[resource_id]

            # Try custom cleanup callback first
            if resource_info.cleanup_callback:
                try:
                    if asyncio.iscoroutinefunction(resource_info.cleanup_callback):
                        await resource_info.cleanup_callback()
                    else:
                        resource_info.cleanup_callback()
                except Exception as e:
                    logger.error(
                        f"Custom cleanup callback failed for {resource_id}: {e}"
                    )

            # Try strategy-based cleanup
            cleanup_success = False
            for strategy in self.cleanup_strategies:
                if strategy.can_handle(resource_info.resource_type):
                    cleanup_success = await strategy.cleanup(resource_info)
                    if cleanup_success:
                        break

            # Update resource status
            if cleanup_success:
                resource_info.status = ResourceStatus.CLEANED_UP
                self.unregister_resource(resource_id)
            else:
                resource_info.status = ResourceStatus.ERROR

            return cleanup_success

        except Exception as e:
            logger.error(f"Failed to cleanup resource {resource_id}: {e}")
            return False

    async def cleanup_resources_by_type(self, resource_type: ResourceType) -> int:
        """Clean up all resources of a specific type."""
        resource_ids = list(self.resources_by_type.get(resource_type, set()))
        cleanup_count = 0

        # Clean up in parallel for better performance
        tasks = [self.cleanup_resource(rid) for rid in resource_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        cleanup_count = sum(1 for result in results if result is True)

        logger.info(
            f"Cleaned up {cleanup_count}/{len(resource_ids)} resources of type {resource_type.value}"
        )
        return cleanup_count

    async def cleanup_resources_by_owner(self, owner: str) -> int:
        """Clean up all resources owned by a specific owner."""
        resource_ids = list(self.resources_by_owner.get(owner, set()))
        cleanup_count = 0

        tasks = [self.cleanup_resource(rid) for rid in resource_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        cleanup_count = sum(1 for result in results if result is True)

        logger.info(
            f"Cleaned up {cleanup_count}/{len(resource_ids)} resources for owner {owner}"
        )
        return cleanup_count

    async def cleanup_all_resources(self) -> int:
        """Clean up all tracked resources."""
        resource_ids = list(self.resources.keys())
        cleanup_count = 0

        # Clean up in batches to avoid overwhelming the system
        batch_size = 50
        for i in range(0, len(resource_ids), batch_size):
            batch = resource_ids[i : i + batch_size]
            tasks = [self.cleanup_resource(rid) for rid in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            cleanup_count += sum(1 for result in results if result is True)

            # Small delay between batches
            if i + batch_size < len(resource_ids):
                await asyncio.sleep(0.1)

        logger.info(f"Cleaned up {cleanup_count}/{len(resource_ids)} total resources")
        return cleanup_count

    def set_quota(self, quota: ResourceQuota):
        """Set a resource quota."""
        quota_key = f"{quota.resource_type.value}_{quota.workspace_id or 'global'}"
        self.quotas[quota_key] = quota
        logger.info(f"Set quota for {quota.resource_type.value}: {quota.max_count}")

    def _check_quota(
        self, resource_type: ResourceType, workspace_id: Optional[str]
    ) -> bool:
        """Check if a resource can be created based on quotas."""
        quota_key = f"{resource_type.value}_{workspace_id or 'global'}"

        if quota_key not in self.quotas:
            return True  # No quota set

        quota = self.quotas[quota_key]
        current_count = len(self.resources_by_type.get(resource_type, set()))

        return current_count < quota.max_count

    async def _leak_detection_loop(self):
        """Background loop for detecting resource leaks."""
        while self._running:
            try:
                await asyncio.sleep(self.leak_check_interval)
                await self._detect_leaks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Leak detection loop error: {e}")

    async def _detect_leaks(self):
        """Detect resource leaks based on age and usage patterns."""
        now = datetime.now()
        new_leaks = []

        for resource_id, resource_info in self.resources.items():
            # Skip recently cleaned up resources
            if resource_info.status == ResourceStatus.CLEANED_UP:
                continue

            # Calculate age
            age_seconds = (now - resource_info.created_at).total_seconds()
            idle_seconds = (now - resource_info.last_accessed).total_seconds()

            # Get threshold for this resource type
            threshold = self.leak_thresholds.get(resource_info.resource_type, 3600)

            # Detect leak
            if age_seconds > threshold and idle_seconds > threshold / 2:
                severity = self._calculate_leak_severity(age_seconds, threshold)

                leak = ResourceLeak(
                    resource_id=resource_id,
                    resource_type=resource_info.resource_type,
                    leak_detected_at=now,
                    leak_duration_seconds=age_seconds,
                    severity=severity,
                    description=f"Resource {resource_id} has been active for {age_seconds:.0f}s without access",
                    suggested_action=self._get_suggested_action(
                        resource_info.resource_type, severity
                    ),
                    resource_info=resource_info,
                )

                new_leaks.append(leak)
                resource_info.status = ResourceStatus.LEAKED

        # Store new leaks
        if new_leaks:
            self.detected_leaks.extend(new_leaks)
            self.metrics["total_leaks_detected"] += len(new_leaks)

            # Log leaks
            for leak in new_leaks:
                logger.warning(
                    f"Resource leak detected: {leak.resource_id} ({leak.resource_type.value}) "
                    f"- {leak.severity} severity"
                )

    def _calculate_leak_severity(self, age_seconds: float, threshold: float) -> str:
        """Calculate leak severity based on age relative to threshold."""
        ratio = age_seconds / threshold

        if ratio > 5:
            return "critical"
        elif ratio > 3:
            return "high"
        elif ratio > 2:
            return "medium"
        else:
            return "low"

    def _get_suggested_action(self, resource_type: ResourceType, severity: str) -> str:
        """Get suggested action for a resource leak."""
        actions = {
            ResourceType.MEMORY: "Force garbage collection and clear memory references",
            ResourceType.FILE_HANDLE: "Close file handles and remove temporary files",
            ResourceType.NETWORK_CONNECTION: "Close network connections and sockets",
            ResourceType.DATABASE_CONNECTION: "Close database connections and return to pool",
            ResourceType.ASYNC_TASK: "Cancel async tasks and clean up coroutines",
            ResourceType.THREAD: "Join threads and clean up thread resources",
            ResourceType.TEMPORARY_FILE: "Delete temporary files and clear disk space",
        }

        base_action = actions.get(
            resource_type, "Clean up resource using appropriate strategy"
        )

        if severity == "critical":
            return f"URGENT: {base_action} - System stability at risk"
        elif severity == "high":
            return f"HIGH PRIORITY: {base_action} - Performance degradation likely"
        else:
            return base_action

    async def _cleanup_loop(self):
        """Background loop for automatic cleanup."""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._automatic_cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")

    async def _automatic_cleanup(self):
        """Perform automatic cleanup of old and leaked resources."""
        cleanup_count = 0

        # Clean up leaked resources
        leaked_resources = [
            rid
            for rid, rinfo in self.resources.items()
            if rinfo.status == ResourceStatus.LEAKED
        ]

        if leaked_resources:
            tasks = [self.cleanup_resource(rid) for rid in leaked_resources]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            cleanup_count += sum(1 for result in results if result is True)

        # Clean up very old resources
        now = datetime.now()
        very_old_threshold = timedelta(hours=24)

        very_old_resources = [
            rid
            for rid, rinfo in self.resources.items()
            if (now - rinfo.created_at) > very_old_threshold
            and rinfo.status == ResourceStatus.IDLE
        ]

        if very_old_resources:
            tasks = [self.cleanup_resource(rid) for rid in very_old_resources]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            cleanup_count += sum(1 for result in results if result is True)

        if cleanup_count > 0:
            logger.info(
                f"Automatic cleanup completed: {cleanup_count} resources cleaned"
            )

    async def _quota_monitoring_loop(self):
        """Background loop for quota monitoring."""
        while self._running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                self._monitor_quotas()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Quota monitoring loop error: {e}")

    def _monitor_quotas(self):
        """Monitor resource quotas and enforce limits."""
        for quota_key, quota in self.quotas.items():
            current_count = len(self.resources_by_type.get(quota.resource_type, set()))

            if current_count >= quota.max_count * 0.9:  # 90% warning threshold
                logger.warning(
                    f"Resource quota warning: {quota.resource_type.value} "
                    f"at {current_count}/{quota.max_count} ({current_count/quota.max_count*100:.1f}%)"
                )

    async def _metrics_collection_loop(self):
        """Background loop for collecting resource metrics."""
        while self._running:
            try:
                await asyncio.sleep(60)  # Collect every minute
                self._collect_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection loop error: {e}")

    def _collect_metrics(self):
        """Collect resource usage metrics."""
        try:
            # Calculate cleanup success rate
            if self.metrics["total_resources_created"] > 0:
                self.metrics["cleanup_success_rate"] = (
                    self.metrics["total_resources_cleaned"]
                    / self.metrics["total_resources_created"]
                    * 100
                )

            # Calculate leak detection rate
            active_resources = len(
                [
                    r
                    for r in self.resources.values()
                    if r.status == ResourceStatus.ACTIVE
                ]
            )

            if active_resources > 0:
                self.metrics["leak_detection_rate"] = (
                    len(self.detected_leaks) / active_resources * 100
                )

            # Memory usage
            if self._memory_tracking_enabled:
                current, peak = tracemalloc.get_traced_memory()
                self.metrics["memory_current_bytes"] = current
                self.metrics["memory_peak_bytes"] = peak

                if self._memory_baseline:
                    baseline_current, baseline_peak = self._memory_baseline
                    self.metrics["memory_growth_bytes"] = current - baseline_current

            # System resources
            process = psutil.Process()
            self.metrics["system_memory_percent"] = process.memory_percent()
            self.metrics["system_cpu_percent"] = process.cpu_percent()
            self.metrics["system_open_files"] = len(process.open_files())
            self.metrics["system_threads"] = process.num_threads()

        except Exception as e:
            logger.error(f"Metrics collection error: {e}")

    def get_resource_summary(self) -> Dict[str, Any]:
        """Get a summary of all managed resources."""
        summary = {
            "total_resources": len(self.resources),
            "resources_by_type": {
                rtype.value: len(resources)
                for rtype, resources in self.resources_by_type.items()
            },
            "resources_by_status": defaultdict(int),
            "total_leaks": len(self.detected_leaks),
            "quota_violations": len(self.quota_violations),
            "metrics": self.metrics.copy(),
        }

        # Count by status
        for resource_info in self.resources.values():
            summary["resources_by_status"][resource_info.status.value] += 1

        return dict(summary)

    def get_leaked_resources(
        self, severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get information about leaked resources."""
        leaked = self.detected_leaks.copy()

        if severity:
            leaked = [leak for leak in leaked if leak.severity == severity]

        return [leak.to_dict() for leak in leaked]

    def get_quota_status(self) -> Dict[str, Any]:
        """Get quota status and violations."""
        quota_status = {
            "quotas": {key: quota.to_dict() for key, quota in self.quotas.items()},
            "current_usage": {
                rtype.value: len(resources)
                for rtype, resources in self.resources_by_type.items()
            },
            "violations": self.quota_violations[-10:],  # Last 10 violations
        }

        return quota_status

    def add_cleanup_strategy(self, strategy: ResourceCleanupStrategy):
        """Add a custom cleanup strategy."""
        self.cleanup_strategies.append(strategy)
        logger.info(f"Added cleanup strategy: {strategy.__class__.__name__}")


# Global resource manager instance
_resource_manager: Optional[ResourceManager] = None


def get_resource_manager() -> ResourceManager:
    """Get or create the global resource manager instance."""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager


async def start_resource_manager():
    """Start the global resource manager."""
    manager = get_resource_manager()
    await manager.start()


async def stop_resource_manager():
    """Stop the global resource manager."""
    manager = get_resource_manager()
    if manager:
        await manager.stop()
