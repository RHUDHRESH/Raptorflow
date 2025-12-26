"""
RaptorFlow Async Concurrency Manager
Provides robust async/await handling with proper concurrency control and resource management.
"""

import asyncio
import logging
import time
import weakref
from typing import Dict, Any, Optional, List, Callable, Union, Coroutine
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from contextlib import asynccontextmanager

from core.enhanced_exceptions import (
    SystemError,
    TimeoutError as RaptorTimeoutError,
    handle_system_error,
    handle_timeout_error
)

logger = logging.getLogger("raptorflow.concurrency")


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class TaskMetrics:
    """Task execution metrics."""
    task_id: str
    name: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    error: Optional[str] = None
    retry_count: int = 0


@dataclass
class ConcurrencyConfig:
    """Concurrency management configuration."""
    max_concurrent_tasks: int = 100
    max_queue_size: int = 1000
    task_timeout: float = 300.0  # 5 minutes
    cleanup_interval: float = 60.0  # 1 minute
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff_factor: float = 2.0


class AsyncTaskManager:
    """
    Enhanced async task manager with proper concurrency control and resource cleanup.
    """
    
    def __init__(self, config: Optional[ConcurrencyConfig] = None):
        self.config = config or ConcurrencyConfig()
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._task_metrics: Dict[str, TaskMetrics] = {}
        self._task_queue: Optional[asyncio.Queue] = None
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        self._task_counter = 0
    
    async def initialize(self):
        """Initialize the task manager."""
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent_tasks)
        self._task_queue = asyncio.Queue(maxsize=self.config.max_queue_size)
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info(f"Async task manager initialized (max_concurrent={self.config.max_concurrent_tasks})")
    
    async def shutdown(self):
        """Shutdown the task manager and clean up resources."""
        logger.info("Shutting down async task manager...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all running tasks
        tasks_to_cancel = list(self._running_tasks.values())
        for task in tasks_to_cancel:
            task.cancel()
        
        # Wait for tasks to complete (with timeout)
        if tasks_to_cancel:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*tasks_to_cancel, return_exceptions=True),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                logger.warning("Some tasks did not complete gracefully during shutdown")
        
        # Clear resources
        self._running_tasks.clear()
        self._task_metrics.clear()
        
        logger.info("Async task manager shutdown complete")
    
    @asynccontextmanager
    async def managed_task(self, name: str, timeout: Optional[float] = None):
        """
        Context manager for managed task execution with proper cleanup.
        """
        task_id = self._generate_task_id()
        metrics = TaskMetrics(
            task_id=task_id,
            name=name,
            status=TaskStatus.PENDING,
            created_at=datetime.utcnow()
        )
        self._task_metrics[task_id] = metrics
        
        try:
            async with self._semaphore:
                metrics.status = TaskStatus.RUNNING
                metrics.started_at = datetime.utcnow()
                
                timeout = timeout or self.config.task_timeout
                start_time = time.time()
                
                try:
                    yield task_id
                    
                    # Update metrics on success
                    metrics.status = TaskStatus.COMPLETED
                    metrics.completed_at = datetime.utcnow()
                    metrics.duration = time.time() - start_time
                    
                except asyncio.TimeoutError as e:
                    metrics.status = TaskStatus.TIMEOUT
                    metrics.error = str(e)
                    metrics.completed_at = datetime.utcnow()
                    metrics.duration = time.time() - start_time
                    
                    logger.error(f"Task {name} timed out after {timeout}s")
                    raise handle_timeout_error(
                        f"Task {name} timed out",
                        timeout_seconds=timeout,
                        task_name=name
                    )
                
                except Exception as e:
                    metrics.status = TaskStatus.FAILED
                    metrics.error = str(e)
                    metrics.completed_at = datetime.utcnow()
                    metrics.duration = time.time() - start_time
                    
                    logger.error(f"Task {name} failed: {e}")
                    raise
                
        except asyncio.CancelledError:
            metrics.status = TaskStatus.CANCELLED
            metrics.completed_at = datetime.utcnow()
            logger.info(f"Task {name} was cancelled")
            raise
        
        finally:
            # Clean up metrics after completion
            await self._schedule_cleanup(task_id)
    
    async def submit_task(
        self,
        coro: Coroutine,
        name: str,
        timeout: Optional[float] = None,
        retries: Optional[int] = None
    ) -> str:
        """
        Submit a task for execution with retry logic.
        """
        task_id = self._generate_task_id()
        retries = retries or self.config.max_retries
        
        async def execute_with_retry():
            last_error = None
            
            for attempt in range(retries + 1):
                try:
                    async with self.managed_task(name, timeout) as tid:
                        result = await coro
                        return result
                        
                except Exception as e:
                    last_error = e
                    if attempt < retries:
                        delay = self.config.retry_delay * (self.config.retry_backoff_factor ** attempt)
                        logger.warning(f"Task {name} failed (attempt {attempt + 1}/{retries + 1}), retrying in {delay}s: {e}")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"Task {name} failed after {retries + 1} attempts: {e}")
                        raise
            
            raise last_error
        
        # Create and track the task
        task = asyncio.create_task(execute_with_retry())
        self._running_tasks[task_id] = task
        
        # Add completion callback
        task.add_done_callback(lambda t: self._task_completed(task_id, t))
        
        return task_id
    
    async def get_task_result(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Get the result of a task, waiting if necessary."""
        if task_id not in self._running_tasks:
            raise SystemError(f"Task {task_id} not found", component="task_manager")
        
        task = self._running_tasks[task_id]
        timeout = timeout or self.config.task_timeout
        
        try:
            result = await asyncio.wait_for(task, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            task.cancel()
            raise handle_timeout_error(
                f"Waiting for task {task_id} timed out",
                timeout_seconds=timeout,
                task_id=task_id
            )
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        if task_id not in self._running_tasks:
            return False
        
        task = self._running_tasks[task_id]
        task.cancel()
        
        # Update metrics
        if task_id in self._task_metrics:
            self._task_metrics[task_id].status = TaskStatus.CANCELLED
        
        return True
    
    async def wait_for_all_tasks(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Wait for all running tasks to complete."""
        if not self._running_tasks:
            return {"completed": 0, "failed": 0, "cancelled": 0}
        
        tasks = list(self._running_tasks.values())
        timeout = timeout or self.config.task_timeout * 2
        
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout
            )
            
            completed = sum(1 for r in results if not isinstance(r, (Exception, asyncio.CancelledError)))
            failed = sum(1 for r in results if isinstance(r, Exception))
            cancelled = sum(1 for r in results if isinstance(r, asyncio.CancelledError))
            
            return {"completed": completed, "failed": failed, "cancelled": cancelled}
            
        except asyncio.TimeoutError:
            # Cancel remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
            
            return {"completed": 0, "failed": 0, "cancelled": len(tasks)}
    
    def _generate_task_id(self) -> str:
        """Generate a unique task ID."""
        self._task_counter += 1
        return f"task_{int(time.time())}_{self._task_counter}"
    
    def _task_completed(self, task_id: str, task: asyncio.Task):
        """Handle task completion."""
        if task_id in self._running_tasks:
            del self._running_tasks[task_id]
    
    async def _schedule_cleanup(self, task_id: str):
        """Schedule cleanup of task metrics."""
        # Use weakref to avoid memory leaks
        cleanup_ref = weakref.ref(self)
        
        async def cleanup():
            manager = cleanup_ref()
            if manager and task_id in manager._task_metrics:
                # Keep metrics for a while, then clean up
                await asyncio.sleep(self.config.cleanup_interval)
                if task_id in manager._task_metrics:
                    del manager._task_metrics[task_id]
        
        asyncio.create_task(cleanup())
    
    async def _cleanup_loop(self):
        """Periodic cleanup of completed tasks."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                
                # Clean up completed tasks
                completed_tasks = [
                    task_id for task_id, task in self._running_tasks.items()
                    if task.done()
                ]
                
                for task_id in completed_tasks:
                    del self._running_tasks[task_id]
                
                if completed_tasks:
                    logger.debug(f"Cleaned up {len(completed_tasks)} completed tasks")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    def get_task_metrics(self) -> Dict[str, Any]:
        """Get current task metrics."""
        total_tasks = len(self._task_metrics)
        status_counts = {}
        
        for metrics in self._task_metrics.values():
            status = metrics.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_tasks": total_tasks,
            "running_tasks": len(self._running_tasks),
            "status_breakdown": status_counts,
            "config": {
                "max_concurrent_tasks": self.config.max_concurrent_tasks,
                "max_queue_size": self.config.max_queue_size,
                "task_timeout": self.config.task_timeout,
                "cleanup_interval": self.config.cleanup_interval
            }
        }


# Global task manager instance
_task_manager: Optional[AsyncTaskManager] = None


async def get_task_manager() -> AsyncTaskManager:
    """Get the global async task manager instance."""
    global _task_manager
    if _task_manager is None:
        _task_manager = AsyncTaskManager()
        await _task_manager.initialize()
    return _task_manager


# Utility functions and decorators
def async_task(
    name: Optional[str] = None,
    timeout: Optional[float] = None,
    retries: Optional[int] = None
):
    """Decorator for async functions with managed execution."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            task_name = name or func.__name__
            
            async def execute():
                return await func(*args, **kwargs)
            
            manager = await get_task_manager()
            task_id = await manager.submit_task(execute(), task_name, timeout, retries)
            return await manager.get_task_result(task_id)
        
        return wrapper
    return decorator


@asynccontextmanager
async def managed_async_context(name: str, timeout: Optional[float] = None):
    """Context manager for async operations with proper resource management."""
    manager = await get_task_manager()
    
    async with manager.managed_task(name, timeout) as task_id:
        yield task_id


async def run_with_timeout(
    coro: Coroutine,
    timeout: float,
    operation_name: str = "operation"
) -> Any:
    """Run a coroutine with timeout handling."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise handle_timeout_error(
            f"{operation_name} timed out",
            timeout_seconds=timeout,
            operation=operation_name
        )


async def gather_with_concurrency(
    coros: List[Coroutine],
    max_concurrent: int = 10,
    timeout: Optional[float] = None
) -> List[Any]:
    """Gather coroutines with concurrency control."""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def bounded_coro(coro):
        async with semaphore:
            return await coro
    
    bounded_coros = [bounded_coro(coro) for coro in coros]
    
    try:
        return await asyncio.wait_for(
            asyncio.gather(*bounded_coros, return_exceptions=True),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        raise handle_timeout_error(
            "Gather operation timed out",
            timeout_seconds=timeout,
            operation="gather_with_concurrency"
        )


if __name__ == "__main__":
    # Test async task manager
    async def test_task_manager():
        manager = AsyncTaskManager()
        await manager.initialize()
        
        async def sample_task(name: str, duration: float):
            await asyncio.sleep(duration)
            return f"Task {name} completed"
        
        # Submit tasks
        task_ids = []
        for i in range(5):
            task_id = await manager.submit_task(
                sample_task(f"task_{i}", 0.1),
                f"sample_task_{i}"
            )
            task_ids.append(task_id)
        
        # Wait for results
        results = []
        for task_id in task_ids:
            result = await manager.get_task_result(task_id)
            results.append(result)
        
        print(f"Results: {results}")
        print(manager.get_task_metrics())
        
        await manager.shutdown()
    
    asyncio.run(test_task_manager())
