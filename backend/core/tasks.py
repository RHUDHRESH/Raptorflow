import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("raptorflow.tasks")


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    id: str
    func: Callable
    args: tuple
    kwargs: dict
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    retry_count: int = 0
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class BackgroundTaskQueue:
    """
    Production-grade background task queue with retry logic and priority handling.
    """

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.queue: List[Task] = []
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.failed_tasks: Dict[str, Task] = {}
        self._workers: List[asyncio.Task] = []
        self._shutdown = False
        self._lock = asyncio.Lock()

    async def start(self):
        """Start the background task workers."""
        logger.info(f"Starting background task queue with {self.max_workers} workers")
        self._workers = [
            asyncio.create_task(self._worker(f"worker-{i}"))
            for i in range(self.max_workers)
        ]

    async def stop(self):
        """Stop all workers gracefully."""
        logger.info("Stopping background task queue")
        self._shutdown = True

        # Wait for all running tasks to complete
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)

        # Cancel workers
        for worker in self._workers:
            worker.cancel()

        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)

        logger.info("Background task queue stopped")

    async def add_task(
        self,
        func: Callable,
        *args,
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        task_id: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Add a task to the queue."""
        if task_id is None:
            task_id = f"task-{datetime.utcnow().timestamp()}-{len(self.queue)}"

        task = Task(
            id=task_id,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            max_retries=max_retries,
        )

        async with self._lock:
            # Insert task in priority order
            inserted = False
            for i, existing_task in enumerate(self.queue):
                if task.priority.value > existing_task.priority.value:
                    self.queue.insert(i, task)
                    inserted = True
                    break

            if not inserted:
                self.queue.append(task)

        logger.debug(f"Added task {task_id} with priority {priority.name}")
        return task_id

    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a specific task."""
        async with self._lock:
            # Check queue
            for task in self.queue:
                if task.id == task_id:
                    return task.status

            # Check running tasks
            if task_id in self.running_tasks:
                return TaskStatus.RUNNING

            # Check completed tasks
            if task_id in self.completed_tasks:
                return TaskStatus.COMPLETED

            # Check failed tasks
            if task_id in self.failed_tasks:
                return TaskStatus.FAILED

        return None

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        async with self._lock:
            # Remove from queue if pending
            for i, task in enumerate(self.queue):
                if task.id == task_id:
                    self.queue.pop(i)
                    logger.info(f"Cancelled pending task {task_id}")
                    return True

            # Cancel if running
            if task_id in self.running_tasks:
                self.running_tasks[task_id].cancel()
                logger.info(f"Cancelled running task {task_id}")
                return True

        return False

    async def _get_next_task(self) -> Optional[Task]:
        """Get the next task from the queue."""
        async with self._lock:
            if self.queue:
                return self.queue.pop(0)
        return None

    async def _execute_task(self, task: Task):
        """Execute a single task with error handling and retry logic."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()

        try:
            logger.debug(f"Executing task {task.id}")
            result = await task.func(*task.args, **task.kwargs)

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()

            async with self._lock:
                self.completed_tasks[task.id] = task
                if task.id in self.running_tasks:
                    del self.running_tasks[task.id]

            logger.debug(f"Task {task.id} completed successfully")
            return result

        except Exception as e:
            task.error = str(e)
            task.retry_count += 1

            if task.retry_count < task.max_retries:
                task.status = TaskStatus.RETRY
                logger.warning(
                    f"Task {task.id} failed, retrying ({task.retry_count}/{task.max_retries}): {e}"
                )

                # Add back to queue with delay
                await asyncio.sleep(min(2**task.retry_count, 30))  # Exponential backoff
                async with self._lock:
                    self.queue.append(task)
                    if task.id in self.running_tasks:
                        del self.running_tasks[task.id]
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()

                async with self._lock:
                    self.failed_tasks[task.id] = task
                    if task.id in self.running_tasks:
                        del self.running_tasks[task.id]

                logger.error(
                    f"Task {task.id} failed permanently after {task.max_retries} retries: {e}"
                )

    async def _worker(self, worker_name: str):
        """Worker process that handles tasks from the queue."""
        logger.info(f"Worker {worker_name} started")

        while not self._shutdown:
            try:
                # Get next task
                task = await self._get_next_task()
                if not task:
                    await asyncio.sleep(0.1)
                    continue

                logger.debug(f"Worker {worker_name} processing task {task.id}")

                # Execute task
                asyncio_task = asyncio.create_task(self._execute_task(task))
                self.running_tasks[task.id] = asyncio_task

                # Wait for task completion
                await asyncio_task

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} encountered error: {e}")
                await asyncio.sleep(1)

        logger.info(f"Worker {worker_name} stopped")

    async def get_queue_stats(self) -> Dict[str, int]:
        """Get statistics about the queue."""
        async with self._lock:
            return {
                "pending": len(self.queue),
                "running": len(self.running_tasks),
                "completed": len(self.completed_tasks),
                "failed": len(self.failed_tasks),
                "total_workers": len(self._workers),
                "active_workers": sum(1 for w in self._workers if not w.done()),
            }


# Global task queue instance
_task_queue: Optional[BackgroundTaskQueue] = None


def get_task_queue() -> BackgroundTaskQueue:
    """Get the global task queue instance."""
    global _task_queue
    if _task_queue is None:
        _task_queue = BackgroundTaskQueue()
    return _task_queue


async def start_task_queue():
    """Start the global task queue."""
    queue = get_task_queue()
    await queue.start()


async def stop_task_queue():
    """Stop the global task queue."""
    queue = get_task_queue()
    await queue.stop()
