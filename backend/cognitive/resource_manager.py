"""
Resource Leak Prevention and Cleanup Manager
Ensures proper cleanup of all resources
"""

import asyncio
import gc
import logging
import os
import signal
import threading
import time
import traceback
import weakref
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set

import psutil

logger = logging.getLogger(__name__)


@dataclass
class ResourceMetrics:
    """Resource usage metrics"""

    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    open_files: int = 0
    threads: int = 0
    active_sessions: int = 0
    cached_items: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


class ResourceTracker:
    """Tracks system resource usage"""

    def __init__(self):
        self.process = psutil.Process()
        self.metrics_history: List[ResourceMetrics] = []
        self.max_history_size = 1000

    def get_current_metrics(self) -> ResourceMetrics:
        """Get current resource metrics"""
        try:
            memory_info = self.process.memory_info()
            return ResourceMetrics(
                memory_mb=memory_info.rss / 1024 / 1024,
                cpu_percent=self.process.cpu_percent(),
                open_files=len(self.process.open_files()),
                threads=self.process.num_threads(),
                timestamp=datetime.now(),
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning(f"Could not get resource metrics: {e}")
            return ResourceMetrics()

    def record_metrics(self):
        """Record current metrics"""
        metrics = self.get_current_metrics()
        self.metrics_history.append(metrics)

        # Limit history size
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size :]

    def get_memory_trend(self, minutes: int = 5) -> float:
        """Get memory usage trend over last N minutes"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [m for m in self.metrics_history if m.timestamp > cutoff]

        if len(recent_metrics) < 2:
            return 0.0

        # Calculate trend (MB per minute)
        start_memory = recent_metrics[0].memory_mb
        end_memory = recent_metrics[-1].memory_mb
        time_diff = (
            recent_metrics[-1].timestamp - recent_metrics[0].timestamp
        ).total_seconds() / 60

        if time_diff == 0:
            return 0.0

        return (end_memory - start_memory) / time_diff

    def is_memory_leak_detected(self, threshold_mb_per_minute: float = 10.0) -> bool:
        """Check if memory leak is detected"""
        trend = self.get_memory_trend()
        return trend > threshold_mb_per_minute


class ResourceManager:
    """Manages resource cleanup and prevents leaks"""

    def __init__(self, cleanup_interval: int = 60):
        self.cleanup_interval = cleanup_interval
        self.resource_tracker = ResourceTracker()
        self.active_sessions: Dict[str, datetime] = {}
        self.active_tasks: Set[asyncio.Task] = set()
        self.active_executors: List[ThreadPoolExecutor] = []
        self.active_process_executors: List[ProcessPoolExecutor] = []
        self.cleanup_callbacks: List[Callable] = []
        self.weak_refs: Dict[str, weakref.ref] = {}
        self.cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        self._shutdown_event = asyncio.Event()

        # Register signal handlers
        self._register_signal_handlers()

    def _register_signal_handlers(self):
        """Register signal handlers for graceful shutdown"""

        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating cleanup")
            asyncio.create_task(self.shutdown())

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

    async def start(self):
        """Start resource manager"""
        self._running = True
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Resource manager started")

    async def stop(self):
        """Stop resource manager and cleanup all resources"""
        await self.shutdown()

    async def shutdown(self):
        """Graceful shutdown"""
        if not self._running:
            return

        self._running = False
        self._shutdown_event.set()

        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

        # Cancel all active tasks
        await self._cancel_all_tasks()

        # Shutdown all executors
        await self._shutdown_all_executors()

        # Run cleanup callbacks
        await self._run_cleanup_callbacks()

        # Force garbage collection
        await self._force_garbage_collection()

        logger.info("Resource manager shutdown complete")

    def register_session(self, session_id: str):
        """Register an active session"""
        self.active_sessions[session_id] = datetime.now()

    def unregister_session(self, session_id: str):
        """Unregister a session"""
        self.active_sessions.pop(session_id, None)

    def register_task(self, task: asyncio.Task):
        """Register an active task"""
        self.active_tasks.add(task)
        task.add_done_callback(lambda t: self.active_tasks.discard(t))

    def register_executor(self, executor: ThreadPoolExecutor):
        """Register a thread executor"""
        self.active_executors.append(executor)

    def register_process_executor(self, executor: ProcessPoolExecutor):
        """Register a process executor"""
        self.active_process_executors.append(executor)

    def register_cleanup_callback(self, callback: Callable):
        """Register a cleanup callback"""
        self.cleanup_callbacks.append(callback)

    def register_weak_ref(
        self, name: str, obj: Any, callback: Optional[Callable] = None
    ):
        """Register a weak reference for tracking"""

        def cleanup_callback(ref):
            logger.debug(f"Object {name} was garbage collected")
            self.weak_refs.pop(name, None)
            if callback:
                callback()

        self.weak_refs[name] = weakref.ref(obj, cleanup_callback)

    async def _cleanup_loop(self):
        """Main cleanup loop"""
        while self._running:
            try:
                await self._perform_cleanup()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(10)

    async def _perform_cleanup(self):
        """Perform cleanup operations"""
        # Record metrics
        self.resource_tracker.record_metrics()

        # Check for memory leaks
        if self.resource_tracker.is_memory_leak_detected():
            logger.warning("Memory leak detected, forcing garbage collection")
            await self._force_garbage_collection()

        # Clean up expired sessions
        await self._cleanup_expired_sessions()

        # Clean up completed tasks
        await self._cleanup_completed_tasks()

        # Log resource usage
        await self._log_resource_usage()

    async def _cleanup_expired_sessions(self, max_age_hours: int = 24):
        """Clean up expired sessions"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        expired_sessions = [
            session_id
            for session_id, created_at in self.active_sessions.items()
            if created_at < cutoff
        ]

        for session_id in expired_sessions:
            logger.warning(f"Cleaning up expired session: {session_id}")
            self.unregister_session(session_id)

    async def _cleanup_completed_tasks(self):
        """Clean up completed tasks"""
        completed_tasks = [task for task in self.active_tasks if task.done()]
        for task in completed_tasks:
            try:
                task.result()  # This will raise any exceptions
            except Exception as e:
                logger.error(f"Task completed with error: {e}")
            self.active_tasks.discard(task)

    async def _cancel_all_tasks(self):
        """Cancel all active tasks"""
        if not self.active_tasks:
            return

        logger.info(f"Cancelling {len(self.active_tasks)} active tasks")

        # Cancel all tasks
        for task in self.active_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.active_tasks, return_exceptions=True)

        self.active_tasks.clear()

    async def _shutdown_all_executors(self):
        """Shutdown all executors"""
        # Shutdown thread executors
        for executor in self.active_executors:
            logger.info("Shutting down thread executor")
            executor.shutdown(wait=True)
        self.active_executors.clear()

        # Shutdown process executors
        for executor in self.active_process_executors:
            logger.info("Shutting down process executor")
            executor.shutdown(wait=True)
        self.active_process_executors.clear()

    async def _run_cleanup_callbacks(self):
        """Run all cleanup callbacks"""
        for callback in self.cleanup_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logger.error(f"Cleanup callback error: {e}")
        self.cleanup_callbacks.clear()

    async def _force_garbage_collection(self):
        """Force garbage collection"""
        # Collect garbage multiple times
        for i in range(3):
            collected = gc.collect()
            if collected > 0:
                logger.info(
                    f"Garbage collection pass {i+1}: collected {collected} objects"
                )

    async def _log_resource_usage(self):
        """Log current resource usage"""
        metrics = self.resource_tracker.get_current_metrics()

        logger.info(
            f"Resource usage - "
            f"Memory: {metrics.memory_mb:.1f}MB, "
            f"CPU: {metrics.cpu_percent:.1f}%, "
            f"Files: {metrics.open_files}, "
            f"Threads: {metrics.threads}, "
            f"Sessions: {len(self.active_sessions)}, "
            f"Tasks: {len(self.active_tasks)}"
        )

        # Check for resource warnings
        if metrics.memory_mb > 1000:  # 1GB
            logger.warning(f"High memory usage: {metrics.memory_mb:.1f}MB")

        if metrics.open_files > 1000:
            logger.warning(f"High file handle count: {metrics.open_files}")

        if metrics.threads > 100:
            logger.warning(f"High thread count: {metrics.threads}")

    def get_resource_summary(self) -> Dict[str, Any]:
        """Get resource usage summary"""
        current_metrics = self.resource_tracker.get_current_metrics()
        memory_trend = self.resource_tracker.get_memory_trend()

        return {
            "current": {
                "memory_mb": current_metrics.memory_mb,
                "cpu_percent": current_metrics.cpu_percent,
                "open_files": current_metrics.open_files,
                "threads": current_metrics.threads,
                "active_sessions": len(self.active_sessions),
                "active_tasks": len(self.active_tasks),
                "active_executors": len(self.active_executors),
                "weak_refs": len(self.weak_refs),
            },
            "trends": {
                "memory_trend_mb_per_minute": memory_trend,
                "memory_leak_detected": self.resource_tracker.is_memory_leak_detected(),
            },
            "limits": {
                "max_memory_mb": 2048,  # 2GB
                "max_open_files": 10000,
                "max_threads": 500,
            },
        }


@asynccontextmanager
async def managed_resource(name: str, resource_manager: ResourceManager):
    """Context manager for managed resources"""
    try:
        logger.debug(f"Acquiring resource: {name}")
        yield
    finally:
        logger.debug(f"Releasing resource: {name}")
        # Cleanup is handled by the resource manager


# Global resource manager
resource_manager = ResourceManager()
