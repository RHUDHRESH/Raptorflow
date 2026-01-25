"""
Celery-based background task processing for RaptorFlow
Replaces FastAPI BackgroundTasks with robust, persistent task queue
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

try:
    from celery import Celery, Task
    from celery.result import AsyncResult
    from kombu import Queue
except ImportError:
    Celery = None
    AsyncResult = None
    Queue = None

    class Task:  # type: ignore
        abstract = True

        def __call__(self, *args, **kwargs):
            raise RuntimeError("Celery is not installed; task execution unavailable")

logger = logging.getLogger(__name__)


# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True

def create_celery_app() -> Optional[Celery]:
    """Create and configure Celery application (or None if Celery missing)."""
    if Celery is None:
        logger.warning("Celery not installed; background task processing disabled.")
        return None

    celery_app = Celery(
        "raptorflow",
        broker=CELERY_BROKER_URL,
        backend=CELERY_RESULT_BACKEND,
        include=[
            "workers.tasks.ai_tasks",
            "workers.tasks.scraping_tasks",
            "workers.tasks.notification_tasks",
            "workers.tasks.analytics_tasks",
        ],
    )

    # Configure queues
    celery_app.conf.task_queues = (
        Queue("ai", routing_key="ai"),
        Queue("scraping", routing_key="scraping"),
        Queue("notifications", routing_key="notifications"),
        Queue("analytics", routing_key="analytics"),
    )

    # Task settings
    celery_app.conf.task_default_queue = "ai"
    celery_app.conf.task_default_exchange = "tasks"
    celery_app.conf.task_default_routing_key = "task.default"
    celery_app.conf.task_acks_late = True
    celery_app.conf.worker_max_tasks_per_child = 50
    celery_app.conf.worker_prefetch_multiplier = 1
    celery_app.conf.broker_connection_retry_on_startup = True

    # Celery configuration
    celery_app.conf.update(
        task_serializer=CELERY_TASK_SERIALIZER,
        result_serializer=CELERY_RESULT_SERIALIZER,
        accept_content=CELERY_ACCEPT_CONTENT,
        timezone=CELERY_TIMEZONE,
        enable_utc=CELERY_ENABLE_UTC,
        # Task routing
        task_routes={
            "workers.tasks.ai_tasks.*": {"queue": "ai"},
            "workers.tasks.scraping_tasks.*": {"queue": "scraping"},
            "workers.tasks.notification_tasks.*": {"queue": "notifications"},
            "workers.tasks.analytics_tasks.*": {"queue": "analytics"},
        },
        # Worker configuration
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        worker_max_tasks_per_child=50,
        # Task timeouts
        task_soft_time_limit=300,  # 5 minutes soft limit
        task_time_limit=600,  # 10 minutes hard limit
        # Result expiration
        result_expires=3600,  # 1 hour
        # Retry configuration
        task_reject_on_worker_lost=True,
        task_ignore_result=False,
        # Beat scheduler for periodic tasks
        beat_schedule={
            "cleanup-expired-tasks": {
                "task": "workers.tasks.maintenance.cleanup_expired_tasks",
                "schedule": 3600.0,  # Every hour
            },
            "health-check": {
                "task": "workers.tasks.maintenance.health_check",
                "schedule": 300.0,  # Every 5 minutes
            },
        },
    )

    return celery_app


celery_app = create_celery_app()


def celery_task(queue: str = "ai", retries: int = 3, retry_delay: int = 60):
    """Decorator for Celery tasks with default settings (no-op if Celery missing)."""
    def decorator(func):
        if celery_app is None or Celery is None:
            # Return original function; calls will execute directly and not enqueue
            return func
        return celery_app.task(
            name=f"raptorflow.{func.__name__}",
            bind=True,
            max_retries=retries,
            default_retry_delay=retry_delay,
            queue=queue,
        )(func)

    return decorator


class BaseTask(Task):
    """Base task with error handling and logging"""

    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        logger.info(f"Task {task_id} completed successfully")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        logger.error(f"Task {task_id} failed: {exc}")

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle task retry"""
        logger.warning(f"Task {task_id} retrying: {exc}")


# Register base task
if celery_app is not None:
    celery_app.Task = BaseTask


class TaskManager:
    """Manager for background tasks with monitoring and control"""

    def __init__(self):
        self.celery = celery_app

    async def submit_task(
        self,
        task_name: str,
        args: tuple = (),
        kwargs: Optional[Dict[str, Any]] = None,
        queue: Optional[str] = None,
        eta: Optional[datetime] = None,
        countdown: Optional[int] = None,
        expires: Optional[Union[datetime, int]] = None,
        retry: bool = True,
        retry_policy: Optional[Dict[str, Any]] = None,
    ) -> AsyncResult:
        """
        Submit a task to the queue

        Args:
            task_name: Name of the task to execute
            args: Positional arguments for the task
            kwargs: Keyword arguments for the task
            queue: Queue to route task to
            eta: Estimated time of arrival
            countdown: Countdown in seconds
            expires: Expiration time
            retry: Whether to retry on failure
            retry_policy: Custom retry policy

        Returns:
            AsyncResult object for tracking task
        """
        kwargs = kwargs or {}

        task_kwargs = {
            "args": args,
            "kwargs": kwargs,
            "queue": queue,
            "retry": retry,
        }

        if eta:
            task_kwargs["eta"] = eta
        if countdown:
            task_kwargs["countdown"] = countdown
        if expires:
            task_kwargs["expires"] = expires
        if retry_policy:
            task_kwargs["retry_policy"] = retry_policy

        if self.celery is None:
            logger.warning("Celery not installed; executing task synchronously (noop).")
            try:
                # Attempt to import and call task directly if available
                module_name, func_name = task_name.rsplit(".", 1) if "." in task_name else (None, task_name)
                if module_name:
                    module = __import__(module_name, fromlist=[func_name])
                    func = getattr(module, func_name, None)
                    if func:
                        await asyncio.to_thread(func, *args, **kwargs)
                return None
            except Exception as e:
                logger.error(f"Fallback task execution failed for {task_name}: {e}")
                return None

        try:
            result = self.celery.send_task(task_name, **task_kwargs)
            logger.info(f"Task {task_name} submitted with ID: {result.id}")
            return result
        except Exception as e:
            logger.error(f"Failed to submit task {task_name}: {e}")
            raise

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a task"""
        if self.celery is None or AsyncResult is None:
            return {"task_id": task_id, "status": "DISABLED", "result": None}
        try:
            result = AsyncResult(task_id, app=self.celery)

            return {
                "task_id": task_id,
                "status": result.status,
                "result": result.result if result.ready() else None,
                "traceback": result.traceback if result.failed() else None,
                "date_done": result.date_done,
                "runtime": result.runtime if result.ready() else None,
            }
        except Exception as e:
            logger.error(f"Failed to get task status {task_id}: {e}")
            return {"task_id": task_id, "status": "UNKNOWN", "error": str(e)}

    async def cancel_task(self, task_id: str, terminate: bool = False) -> bool:
        """Cancel a task"""
        if self.celery is None:
            logger.warning("Celery not installed; cancel_task is a no-op")
            return False
        try:
            self.celery.control.revoke(task_id, terminate=terminate)
            logger.info(f"Task {task_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False

    async def get_active_tasks(
        self, worker_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get list of active tasks"""
        if self.celery is None:
            return []
        try:
            inspect = self.celery.control.inspect()
            active_tasks = inspect.active()

            if worker_name and active_tasks:
                active_tasks = {worker_name: active_tasks.get(worker_name, [])}

            return active_tasks or []
        except Exception as e:
            logger.error(f"Failed to get active tasks: {e}")
            return []

    async def get_worker_stats(self) -> Dict[str, Any]:
        """Get worker statistics"""
        if self.celery is None:
            return {"workers": {}, "status": "disabled"}
        try:
            inspect = self.celery.control.inspect()
            stats = inspect.stats()

            return {
                "workers": stats or {},
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to get worker stats: {e}")
            return {"workers": {}, "error": str(e)}

    async def purge_queue(self, queue_name: Optional[str] = None) -> int:
        """Purge tasks from queue"""
        if self.celery is None:
            return 0
        try:
            if queue_name:
                purged = self.celery.control.purge()
                logger.info(f"Purged {purged} tasks from queue {queue_name}")
            else:
                purged = self.celery.control.purge()
                logger.info(f"Purged {purged} tasks from all queues")

            return purged
        except Exception as e:
            logger.error(f"Failed to purge queue: {e}")
            return 0

    async def scale_workers(self, worker_count: int) -> bool:
        """Scale number of workers (requires deployment integration)"""
        # This would integrate with your deployment system
        # For now, just log the request
        logger.info(f"Scale workers to {worker_count} requested")
        return True


# Global task manager instance
_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """Get global task manager instance"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager


# Convenience functions for common task types
async def submit_ai_task(
    task_name: str, user_id: str, workspace_id: str, **kwargs
) -> AsyncResult:
    """Submit AI-related task"""
    manager = get_task_manager()
    return await manager.submit_task(
        task_name=task_name,
        kwargs={"user_id": user_id, "workspace_id": workspace_id, **kwargs},
        queue="ai",
    )


async def submit_scraping_task(
    task_name: str, user_id: str, workspace_id: str, **kwargs
) -> AsyncResult:
    """Submit scraping-related task"""
    manager = get_task_manager()
    return await manager.submit_task(
        task_name=task_name,
        kwargs={"user_id": user_id, "workspace_id": workspace_id, **kwargs},
        queue="scraping",
    )


async def submit_notification_task(
    task_name: str, user_id: str, **kwargs
) -> AsyncResult:
    """Submit notification-related task"""
    manager = get_task_manager()
    return await manager.submit_task(
        task_name=task_name,
        kwargs={"user_id": user_id, **kwargs},
        queue="notifications",
    )


async def submit_analytics_task(task_name: str, **kwargs) -> AsyncResult:
    """Submit analytics-related task"""
    manager = get_task_manager()
    return await manager.submit_task(
        task_name=task_name, kwargs=kwargs, queue="analytics"
    )


# Health check
async def get_celery_health() -> Dict[str, Any]:
    """Get Celery health status"""
    manager = get_task_manager()
    if manager.celery is None:
        return {"status": "disabled", "broker_connected": False, "active_workers": 0, "active_tasks": 0}
    try:
        # Check broker connection
        inspect = manager.celery.control.inspect()
        stats = inspect.stats()

        # Get active tasks
        active_tasks = await manager.get_active_tasks()

        return {
            "status": "healthy" if stats else "unhealthy",
            "broker_connected": bool(stats),
            "active_workers": len(stats) if stats else 0,
            "active_tasks": len(active_tasks),
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


# FastAPI integration
class BackgroundTaskManager:
    """FastAPI integration for background tasks"""

    def __init__(self):
        self.task_manager = get_task_manager()

    async def add_task(self, task_name: str, *args, **kwargs) -> AsyncResult:
        """Add a background task (replaces FastAPI BackgroundTasks.add_task)"""
        return await self.task_manager.submit_task(task_name, args, kwargs)

    async def get_task_result(self, task_id: str) -> Any:
        """Get task result"""
        status = await self.task_manager.get_task_status(task_id)
        return status.get("result")

    async def is_task_ready(self, task_id: str) -> bool:
        """Check if task is ready"""
        status = await self.task_manager.get_task_status(task_id)
        return status.get("status") in ["SUCCESS", "FAILURE"]


# Global background task manager for FastAPI
_background_task_manager: Optional[BackgroundTaskManager] = None


def get_background_task_manager() -> BackgroundTaskManager:
    """Get global background task manager"""
    global _background_task_manager
    if _background_task_manager is None:
        _background_task_manager = BackgroundTaskManager()
    return _background_task_manager
