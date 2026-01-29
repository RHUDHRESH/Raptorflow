"""
Google Cloud Tasks client for Raptorflow.

Provides task scheduling, delayed execution, and
distributed task processing capabilities.
"""

import json
import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from google.api_core import exceptions
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2

from gcp import get_gcp_client

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task status."""

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskPriority(Enum):
    """Task priority levels."""

    LOW = 50
    NORMAL = 100
    HIGH = 200
    URGENT = 255


@dataclass
class TaskConfig:
    """Task configuration."""

    task_id: str
    handler_url: str
    payload: Dict[str, Any]
    queue_name: str

    # Timing
    delay_seconds: int = 0
    schedule_time: Optional[datetime] = None

    # Retry configuration
    max_attempts: int = 3
    min_retry_seconds: int = 10
    max_retry_seconds: int = 3600

    # Priority and routing
    priority: TaskPriority = TaskPriority.NORMAL
    tag: Optional[str] = None

    # Headers
    headers: Dict[str, str] = None

    # Deadline
    deadline_seconds: int = 600  # 10 minutes

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.priority, int):
            self.priority = TaskPriority(self.priority)

        if self.headers is None:
            self.headers = {}


@dataclass
class TaskResult:
    """Result of task creation."""

    success: bool
    task_name: Optional[str] = None
    task_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class TaskInfo:
    """Task information."""

    task_name: str
    task_id: str
    queue_name: str
    status: TaskStatus
    created_at: datetime
    scheduled_at: datetime
    first_attempt_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    attempt_count: int = 0
    error_message: Optional[str] = None
    response_status: Optional[str] = None
    response_body: Optional[str] = None


class CloudTasksClient:
    """Google Cloud Tasks client for Raptorflow."""

    def __init__(self):
        self.gcp_client = get_gcp_client()
        self.logger = logging.getLogger("cloud_tasks_client")

        # Get Cloud Tasks client
        self.client = self.gcp_client.get_cloud_tasks_client()

        if not self.client:
            self.logger.warning("Cloud Tasks client not available")

        # Project and region
        self.project_id = self.gcp_client.get_project_id()
        self.region = self.gcp_client.get_region()

        # Default queue prefix
        self.queue_prefix = os.getenv("CLOUD_TASKS_QUEUE_PREFIX", "raptorflow")

        # Default handler URL
        self.default_handler_url = os.getenv("CLOUD_TASKS_HANDLER_URL", "")

    def _get_queue_path(self, queue_name: str) -> str:
        """Get full queue path."""
        return f"projects/{self.project_id}/locations/{self.region}/queues/{self.queue_prefix}-{queue_name}"

    def _get_task_path(self, queue_name: str, task_id: str) -> str:
        """Get full task path."""
        return f"{self._get_queue_path(queue_name)}/tasks/{task_id}"

    async def create_queue(
        self,
        queue_name: str,
        max_concurrent_tasks: int = 10,
        max_dispatches_per_second: float = 1.0,
        retry_config: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Create a Cloud Tasks queue."""
        try:
            queue_path = self._get_queue_path(queue_name)

            try:
                # Check if queue exists
                self.client.get_queue(name=queue_path)
                self.logger.info(f"Queue {queue_name} already exists")
                return True
            except exceptions.NotFound:
                pass

            # Create queue configuration
            queue = tasks_v2.Queue(
                name=queue_path,
                rate_limits=tasks_v2.RateLimits(
                    max_dispatches_per_second=max_dispatches_per_second,
                    max_concurrent_dispatches=max_concurrent_tasks,
                ),
            )

            # Add retry configuration
            if retry_config:
                retry_policy = tasks_v2.RetryPolicy(
                    max_attempts=retry_config.get("max_attempts", 3),
                    min_backoff=retry_config.get("min_backoff", "10s"),
                    max_backoff=retry_config.get("max_backoff", "3600s"),
                    max_doublings=retry_config.get("max_doublings", 16),
                )
                queue.retry_policy = retry_policy

            # Create queue
            self.client.create_queue(
                parent=f"projects/{self.project_id}/locations/{self.region}",
                queue=queue,
            )

            self.logger.info(f"Created queue: {queue_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create queue {queue_name}: {e}")
            return False

    async def delete_queue(self, queue_name: str) -> bool:
        """Delete a Cloud Tasks queue."""
        try:
            queue_path = self._get_queue_path(queue_name)
            self.client.delete_queue(name=queue_path)

            self.logger.info(f"Deleted queue: {queue_name}")
            return True

        except exceptions.NotFound:
            self.logger.warning(f"Queue {queue_name} not found for deletion")
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete queue {queue_name}: {e}")
            return False

    async def list_queues(self) -> List[str]:
        """List all queues."""
        try:
            parent = f"projects/{self.project_id}/locations/{self.region}"

            queues = []
            for queue in self.client.list_queues(parent=parent):
                # Extract queue name from full path
                queue_name = queue.name.split("/")[-1]
                if queue_name.startswith(f"{self.queue_prefix}-"):
                    queue_id = queue_name[len(f"{self.queue_prefix}-") :]
                    queues.append(queue_id)

            return queues

        except Exception as e:
            self.logger.error(f"Failed to list queues: {e}")
            return []

    async def create_task(self, config: TaskConfig) -> TaskResult:
        """Create a Cloud Task."""
        try:
            queue_path = self._get_queue_path(config.queue_name)

            # Prepare HTTP request
            http_request = tasks_v2.HttpRequest(
                http_method=tasks_v2.HttpMethod.POST,
                url=config.handler_url,
                headers={
                    "Content-Type": "application/json",
                    "X-CloudTasks-TaskName": config.task_id,
                    **config.headers,
                },
                body=json.dumps(config.payload).encode("utf-8"),
            )

            # Prepare task
            task = tasks_v2.Task(
                http_request=http_request,
                name=self._get_task_path(config.queue_name, config.task_id),
            )

            # Set schedule time
            if config.delay_seconds > 0:
                schedule_time = datetime.now() + timedelta(seconds=config.delay_seconds)
                timestamp = timestamp_pb2.Timestamp()
                timestamp.FromDatetime(schedule_time)
                task.schedule_time = timestamp
            elif config.schedule_time:
                timestamp = timestamp_pb2.Timestamp()
                timestamp.FromDatetime(config.schedule_time)
                task.schedule_time = timestamp

            # Set priority
            task.priority = config.priority.value

            # Set tag if provided
            if config.tag:
                task.tag = config.tag

            # Create task
            created_task = self.client.create_task(parent=queue_path, task=task)

            self.logger.info(
                f"Created task {config.task_id} in queue {config.queue_name}"
            )

            return TaskResult(
                success=True,
                task_name=created_task.name,
                task_id=config.task_id,
                created_at=datetime.now(),
            )

        except Exception as e:
            self.logger.error(f"Failed to create task {config.task_id}: {e}")
            return TaskResult(success=False, error_message=str(e))

    async def create_task_with_delay(
        self,
        handler_url: str,
        payload: Dict[str, Any],
        queue_name: str,
        delay_seconds: int,
        task_id: Optional[str] = None,
        **kwargs,
    ) -> TaskResult:
        """Create a task with delay."""
        if not task_id:
            task_id = str(uuid.uuid4())

        config = TaskConfig(
            task_id=task_id,
            handler_url=handler_url,
            payload=payload,
            queue_name=queue_name,
            delay_seconds=delay_seconds,
            **kwargs,
        )

        return await self.create_task(config)

    async def create_scheduled_task(
        self,
        handler_url: str,
        payload: Dict[str, Any],
        queue_name: str,
        schedule_time: datetime,
        task_id: Optional[str] = None,
        **kwargs,
    ) -> TaskResult:
        """Create a scheduled task."""
        if not task_id:
            task_id = str(uuid.uuid4())

        config = TaskConfig(
            task_id=task_id,
            handler_url=handler_url,
            payload=payload,
            queue_name=queue_name,
            schedule_time=schedule_time,
            **kwargs,
        )

        return await self.create_task(config)

    async def delete_task(self, queue_name: str, task_id: str) -> bool:
        """Delete a task."""
        try:
            task_path = self._get_task_path(queue_name, task_id)
            self.client.delete_task(name=task_path)

            self.logger.info(f"Deleted task {task_id} from queue {queue_name}")
            return True

        except exceptions.NotFound:
            self.logger.warning(f"Task {task_id} not found for deletion")
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete task {task_id}: {e}")
            return False

    async def get_task(self, queue_name: str, task_id: str) -> Optional[TaskInfo]:
        """Get task information."""
        try:
            task_path = self._get_task_path(queue_name, task_id)
            task = self.client.get_task(name=task_path)

            # Determine status
            status = TaskStatus.QUEUED
            if task.app_engine_http_request:
                status = TaskStatus.RUNNING

            # Parse timestamps
            created_at = task.create_time.ToDatetime()
            scheduled_at = (
                task.schedule_time.ToDatetime() if task.schedule_time else created_at
            )

            first_attempt_at = None
            completed_at = None

            if task.dispatch_deadline:
                completed_at = task.dispatch_deadline.ToDatetime()

            return TaskInfo(
                task_name=task.name,
                task_id=task_id,
                queue_name=queue_name,
                status=status,
                created_at=created_at,
                scheduled_at=scheduled_at,
                first_attempt_at=first_attempt_at,
                completed_at=completed_at,
                attempt_count=task.attempt_dispatch_count,
                error_message=None,
                response_status=None,
                response_body=None,
            )

        except exceptions.NotFound:
            self.logger.warning(f"Task {task_id} not found")
            return None
        except Exception as e:
            self.logger.error(f"Failed to get task {task_id}: {e}")
            return None

    async def list_tasks(
        self,
        queue_name: str,
        page_size: int = 100,
        filter_expression: Optional[str] = None,
    ) -> List[TaskInfo]:
        """List tasks in a queue."""
        try:
            queue_path = self._get_queue_path(queue_name)

            tasks = []
            request = tasks_v2.ListTasksRequest(parent=queue_path, page_size=page_size)

            if filter_expression:
                request.filter = filter_expression

            for task in self.client.list_tasks(request=request):
                # Extract task ID from full path
                task_id = task.name.split("/")[-1]

                # Determine status
                status = TaskStatus.QUEUED
                if task.app_engine_http_request:
                    status = TaskStatus.RUNNING

                # Parse timestamps
                created_at = task.create_time.ToDatetime()
                scheduled_at = (
                    task.schedule_time.ToDatetime()
                    if task.schedule_time
                    else created_at
                )

                task_info = TaskInfo(
                    task_name=task.name,
                    task_id=task_id,
                    queue_name=queue_name,
                    status=status,
                    created_at=created_at,
                    scheduled_at=scheduled_at,
                    attempt_count=task.attempt_dispatch_count,
                )

                tasks.append(task_info)

            return tasks

        except Exception as e:
            self.logger.error(f"Failed to list tasks for queue {queue_name}: {e}")
            return []

    async def run_task(
        self,
        handler_url: str,
        payload: Dict[str, Any],
        queue_name: str = "default",
        delay_seconds: int = 0,
        **kwargs,
    ) -> TaskResult:
        """Run a task immediately (convenience method)."""
        task_id = str(uuid.uuid4())

        config = TaskConfig(
            task_id=task_id,
            handler_url=handler_url,
            payload=payload,
            queue_name=queue_name,
            delay_seconds=delay_seconds,
            **kwargs,
        )

        return await self.create_task(config)

    async def cancel_task(self, queue_name: str, task_id: str) -> bool:
        """Cancel a task."""
        try:
            # Cloud Tasks doesn't have a direct cancel method
            # We delete the task instead
            return await self.delete_task(queue_name, task_id)

        except Exception as e:
            self.logger.error(f"Failed to cancel task {task_id}: {e}")
            return False

    async def get_queue_stats(self, queue_name: str) -> Dict[str, Any]:
        """Get queue statistics."""
        try:
            queue_path = self._get_queue_path(queue_name)
            queue = self.client.get_queue(name=queue_path)

            # Get task counts
            tasks = await self.list_tasks(queue_name, page_size=1000)

            status_counts = {}
            for task in tasks:
                status = task.status.value
                status_counts[status] = status_counts.get(status, 0) + 1

            return {
                "queue_name": queue_name,
                "queue_path": queue_path,
                "max_concurrent_tasks": queue.rate_limits.max_concurrent_dispatches,
                "max_dispatches_per_second": queue.rate_limits.max_dispatches_per_second,
                "total_tasks": len(tasks),
                "status_counts": status_counts,
                "retry_policy": {
                    "max_attempts": (
                        queue.retry_policy.max_attempts if queue.retry_policy else None
                    ),
                    "min_backoff": (
                        queue.retry_policy.min_backoff if queue.retry_policy else None
                    ),
                    "max_backoff": (
                        queue.retry_policy.max_backoff if queue.retry_policy else None
                    ),
                },
            }

        except Exception as e:
            self.logger.error(f"Failed to get queue stats for {queue_name}: {e}")
            return {}

    async def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all queues."""
        try:
            queues = await self.list_queues()

            queue_stats = {}
            total_tasks = 0

            for queue_name in queues:
                stats = await self.get_queue_stats(queue_name)
                queue_stats[queue_name] = stats
                total_tasks += stats.get("total_tasks", 0)

            return {
                "project_id": self.project_id,
                "region": self.region,
                "queue_prefix": self.queue_prefix,
                "total_queues": len(queues),
                "total_tasks": total_tasks,
                "queues": queue_stats,
            }

        except Exception as e:
            self.logger.error(f"Failed to get all stats: {e}")
            return {}

    async def purge_queue(self, queue_name: str) -> bool:
        """Purge all tasks from a queue."""
        try:
            queue_path = self._get_queue_path(queue_name)

            # Create purge request
            purge_request = tasks_v2.PurgeQueueRequest(name=queue_path)
            self.client.purge_queue(request=purge_request)

            self.logger.info(f"Purged queue: {queue_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to purge queue {queue_name}: {e}")
            return False

    async def pause_queue(self, queue_name: str) -> bool:
        """Pause a queue."""
        try:
            queue_path = self._get_queue_path(queue_name)
            queue = self.client.get_queue(name=queue_path)

            # Set state to PAUSED
            queue.state = tasks_v2.Queue.State.PAUSED
            self.client.update_queue(queue=queue, update_mask={"state"})

            self.logger.info(f"Paused queue: {queue_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to pause queue {queue_name}: {e}")
            return False

    async def resume_queue(self, queue_name: str) -> bool:
        """Resume a paused queue."""
        try:
            queue_path = self._get_queue_path(queue_name)
            queue = self.client.get_queue(name=queue_path)

            # Set state to RUNNING
            queue.state = tasks_v2.Queue.State.RUNNING
            self.client.update_queue(queue=queue, update_mask={"state"})

            self.logger.info(f"Resumed queue: {queue_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to resume queue {queue_name}: {e}")
            return False


# Global Cloud Tasks client instance
_cloud_tasks_client: Optional[CloudTasksClient] = None


def get_cloud_tasks_client() -> CloudTasksClient:
    """Get global Cloud Tasks client instance."""
    global _cloud_tasks_client
    if _cloud_tasks_client is None:
        _cloud_tasks_client = CloudTasksClient()
    return _cloud_tasks_client


# Convenience functions
async def create_task(
    handler_url: str,
    payload: Dict[str, Any],
    queue_name: str = "default",
    delay_seconds: int = 0,
    **kwargs,
) -> TaskResult:
    """Create a Cloud Task."""
    client = get_cloud_tasks_client()
    return await client.run_task(
        handler_url, payload, queue_name, delay_seconds, **kwargs
    )


async def create_delayed_task(
    handler_url: str,
    payload: Dict[str, Any],
    queue_name: str,
    delay_seconds: int,
    **kwargs,
) -> TaskResult:
    """Create a delayed Cloud Task."""
    client = get_cloud_tasks_client()
    return await client.create_task_with_delay(
        handler_url, payload, queue_name, delay_seconds, **kwargs
    )


async def create_scheduled_task(
    handler_url: str,
    payload: Dict[str, Any],
    queue_name: str,
    schedule_time: datetime,
    **kwargs,
) -> TaskResult:
    """Create a scheduled Cloud Task."""
    client = get_cloud_tasks_client()
    return await client.create_scheduled_task(
        handler_url, payload, queue_name, schedule_time, **kwargs
    )


async def delete_task(queue_name: str, task_id: str) -> bool:
    """Delete a Cloud Task."""
    client = get_cloud_tasks_client()
    return await client.delete_task(queue_name, task_id)


async def create_queue(queue_name: str, **kwargs) -> bool:
    """Create a Cloud Tasks queue."""
    client = get_cloud_tasks_client()
    return await client.create_queue(queue_name, **kwargs)


# Task decorator for background tasks
def background_task(
    queue_name: str = "default",
    delay_seconds: int = 0,
    priority: TaskPriority = TaskPriority.NORMAL,
):
    """Decorator for background task functions."""

    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # Extract task configuration
            task_id = str(uuid.uuid4())
            handler_url = os.getenv("CLOUD_TASKS_HANDLER_URL", "")

            if not handler_url:
                raise ValueError("CLOUD_TASKS_HANDLER_URL not configured")

            # Prepare payload
            payload = {
                "function": func.__name__,
                "module": func.__module__,
                "args": args,
                "kwargs": kwargs,
            }

            # Create task
            client = get_cloud_tasks_client()
            config = TaskConfig(
                task_id=task_id,
                handler_url=handler_url,
                payload=payload,
                queue_name=queue_name,
                delay_seconds=delay_seconds,
                priority=priority,
            )

            return await client.create_task(config)

        # Store wrapper for direct execution
        func._background_wrapper = wrapper
        func._queue_name = queue_name
        func._delay_seconds = delay_seconds
        func._priority = priority

        return wrapper

    return decorator


# Execute background task (called by task handler)
async def execute_background_task(task_data: Dict[str, Any]) -> Any:
    """Execute a background task from task data."""
    try:
        function_name = task_data["function"]
        module_name = task_data["module"]
        args = task_data["args"]
        kwargs = task_data["kwargs"]

        # Import module and get function
        module = __import__(module_name, fromlist=[function_name])
        func = getattr(module, function_name)

        # Execute function
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    except Exception as e:
        logger.error(f"Failed to execute background task: {e}")
        raise
