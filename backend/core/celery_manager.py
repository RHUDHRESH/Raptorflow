"""
Celery-based background task processing for RaptorFlow
Replaces FastAPI BackgroundTasks with robust, persistent task queue
"""

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

from celery import Celery, Task
from celery.result import AsyncResult
from kombu import Queue

logger = logging.getLogger(__name__)


# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True

# Create Celery app
celery_app = Celery(
    "raptorflow",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "workers.tasks.ai_tasks",
        "workers.tasks.scraping_tasks", 
        "workers.tasks.notification_tasks",
        "workers.tasks.analytics_tasks"
    ]
)

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
    
    # Queue definitions
    task_queues=(
        Queue("ai", routing_key="ai"),
        Queue("scraping", routing_key="scraping"),
        Queue("notifications", routing_key="notifications"),
        Queue("analytics", routing_key="analytics"),
    ),
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=50,
    
    # Task timeouts
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=600,       # 10 minutes hard limit
    
    # Result expiration
    result_expires=3600,       # 1 hour
    
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
            "schedule": 300.0,   # Every 5 minutes
        },
    },
)


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
        retry_policy: Optional[Dict[str, Any]] = None
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
            
        try:
            result = self.celery.send_task(task_name, **task_kwargs)
            logger.info(f"Task {task_name} submitted with ID: {result.id}")
            return result
        except Exception as e:
            logger.error(f"Failed to submit task {task_name}: {e}")
            raise
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a task"""
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
        try:
            self.celery.control.revoke(task_id, terminate=terminate)
            logger.info(f"Task {task_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
    
    async def get_active_tasks(self, worker_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of active tasks"""
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
    task_name: str,
    user_id: str,
    workspace_id: str,
    **kwargs
) -> AsyncResult:
    """Submit AI-related task"""
    manager = get_task_manager()
    return await manager.submit_task(
        task_name=task_name,
        kwargs={
            "user_id": user_id,
            "workspace_id": workspace_id,
            **kwargs
        },
        queue="ai"
    )


async def submit_scraping_task(
    task_name: str,
    user_id: str,
    workspace_id: str,
    **kwargs
) -> AsyncResult:
    """Submit scraping-related task"""
    manager = get_task_manager()
    return await manager.submit_task(
        task_name=task_name,
        kwargs={
            "user_id": user_id,
            "workspace_id": workspace_id,
            **kwargs
        },
        queue="scraping"
    )


async def submit_notification_task(
    task_name: str,
    user_id: str,
    **kwargs
) -> AsyncResult:
    """Submit notification-related task"""
    manager = get_task_manager()
    return await manager.submit_task(
        task_name=task_name,
        kwargs={
            "user_id": user_id,
            **kwargs
        },
        queue="notifications"
    )


async def submit_analytics_task(
    task_name: str,
    **kwargs
) -> AsyncResult:
    """Submit analytics-related task"""
    manager = get_task_manager()
    return await manager.submit_task(
        task_name=task_name,
        kwargs=kwargs,
        queue="analytics"
    )


# Health check
async def get_celery_health() -> Dict[str, Any]:
    """Get Celery health status"""
    try:
        manager = get_task_manager()
        
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
    
    async def add_task(
        self,
        task_name: str,
        *args,
        **kwargs
    ) -> AsyncResult:
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
