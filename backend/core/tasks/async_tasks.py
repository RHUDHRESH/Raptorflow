"""
Background task queue for long-running operations
Uses asyncio for non-blocking task execution
"""

import asyncio
import logging
from typing import Callable, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Background task"""

    id: str
    name: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None


class TaskQueue:
    """Async task queue manager"""

    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.running_tasks: set[asyncio.Task] = set()

    async def enqueue(
        self, task_id: str, task_name: str, coro: Callable, *args, **kwargs
    ) -> Task:
        """Enqueue a background task."""
        task = Task(
            id=task_id,
            name=task_name,
            status=TaskStatus.PENDING,
            created_at=datetime.utcnow(),
        )

        self.tasks[task_id] = task

        asyncio_task = asyncio.create_task(
            self._execute_task(task, coro, *args, **kwargs)
        )
        self.running_tasks.add(asyncio_task)
        asyncio_task.add_done_callback(self.running_tasks.discard)

        logger.info(f"Task enqueued: {task_name} ({task_id})")
        return task

    async def _execute_task(self, task: Task, coro: Callable, *args, **kwargs) -> None:
        """Execute a background task"""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()

            logger.info(f"Task started: {task.name} ({task.id})")

            result = await coro(*args, **kwargs)

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.result = result

            logger.info(f"Task completed: {task.name} ({task.id})")

        except asyncio.CancelledError:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.utcnow()
            logger.warning(f"Task cancelled: {task.name} ({task.id})")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.error = str(e)
            logger.error(f"Task failed: {task.name} ({task.id}): {e}")

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks"""
        return list(self.tasks.values())

    def get_running_tasks(self) -> list[Task]:
        """Get currently running tasks"""
        return [
            task for task in self.tasks.values() if task.status == TaskStatus.RUNNING
        ]

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        task = self.tasks.get(task_id)
        if not task or task.status != TaskStatus.RUNNING:
            return False

        for asyncio_task in self.running_tasks:
            if asyncio_task.get_name() == task_id:
                asyncio_task.cancel()
                return True

        return False

    def cleanup_old_tasks(self, max_age_hours: int = 24) -> int:
        """Remove old completed tasks."""
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        removed = 0

        for task_id, task in list(self.tasks.items()):
            if (
                task.status
                in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
                and task.completed_at
                and task.completed_at < cutoff
            ):
                del self.tasks[task_id]
                removed += 1

        if removed > 0:
            logger.info(f"Cleaned up {removed} old tasks")

        return removed


task_queue = TaskQueue()


async def run_in_background(
    task_id: str, task_name: str, coro: Callable, *args, **kwargs
) -> Task:
    """Convenience function to run a coroutine in the background."""
    return await task_queue.enqueue(task_id, task_name, coro, *args, **kwargs)
