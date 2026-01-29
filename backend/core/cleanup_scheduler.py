"""
Automated cleanup scheduler for Raptorflow backend.
Provides scheduled cleanup with configurable intervals and triggers.
"""

import asyncio
import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

import schedule
from metrics_collector import get_metrics_collector
from resources import ResourceType, get_resource_manager

logger = logging.getLogger(__name__)


class CleanupTriggerType(Enum):
    """Types of cleanup triggers."""

    SCHEDULED = "scheduled"
    THRESHOLD_BASED = "threshold_based"
    MANUAL = "manual"
    EVENT_DRIVEN = "event_driven"
    HEALTH_CHECK = "health_check"


class CleanupPriority(Enum):
    """Priority levels for cleanup tasks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CleanupTask:
    """A cleanup task definition."""

    task_id: str
    name: str
    description: str
    cleanup_function: Callable
    trigger_type: CleanupTriggerType
    priority: CleanupPriority
    enabled: bool = True
    schedule_expression: Optional[str] = None  # Cron-like expression
    threshold_condition: Optional[str] = None
    timeout_seconds: int = 300
    retry_count: int = 3
    retry_delay_seconds: int = 30
    tags: Dict[str, str] = field(default_factory=dict)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "trigger_type": self.trigger_type.value,
            "priority": self.priority.value,
            "enabled": self.enabled,
            "schedule_expression": self.schedule_expression,
            "threshold_condition": self.threshold_condition,
            "timeout_seconds": self.timeout_seconds,
            "retry_count": self.retry_count,
            "retry_delay_seconds": self.retry_delay_seconds,
            "tags": self.tags,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "run_count": self.run_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "average_duration_seconds": self.average_duration_seconds,
            "success_rate": (
                (self.success_count / self.run_count * 100) if self.run_count > 0 else 0
            ),
        }


@dataclass
class CleanupResult:
    """Result of a cleanup task execution."""

    task_id: str
    started_at: datetime
    completed_at: datetime
    success: bool
    message: str
    resources_cleaned: int = 0
    bytes_freed: int = 0
    error: Optional[str] = None
    execution_time_seconds: float = 0.0
    retry_attempt: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "success": self.success,
            "message": self.message,
            "resources_cleaned": self.resources_cleaned,
            "bytes_freed": self.bytes_freed,
            "error": self.error,
            "execution_time_seconds": self.execution_time_seconds,
            "retry_attempt": self.retry_attempt,
        }


class CleanupStrategy(ABC):
    """Abstract base class for cleanup strategies."""

    @abstractmethod
    async def execute(self, task: CleanupTask) -> CleanupResult:
        """Execute the cleanup strategy."""
        pass

    @abstractmethod
    def can_execute(self, task: CleanupTask) -> bool:
        """Check if this strategy can execute the task."""
        pass


class ResourceCleanupStrategy(CleanupStrategy):
    """Cleanup strategy for resource management."""

    async def execute(self, task: CleanupTask) -> CleanupResult:
        """Execute resource cleanup."""
        started_at = datetime.now()

        try:
            resource_manager = get_resource_manager()

            # Get resource type from task tags
            resource_type_str = task.tags.get("resource_type")
            if resource_type_str:
                resource_type = ResourceType(resource_type_str)
                cleaned_count = await resource_manager.cleanup_resources_by_type(
                    resource_type
                )
            else:
                cleaned_count = await resource_manager.cleanup_all_resources()

            completed_at = datetime.now()
            execution_time = (completed_at - started_at).total_seconds()

            return CleanupResult(
                task_id=task.task_id,
                started_at=started_at,
                completed_at=completed_at,
                success=True,
                message=f"Cleaned up {cleaned_count} resources",
                resources_cleaned=cleaned_count,
                execution_time_seconds=execution_time,
            )

        except Exception as e:
            completed_at = datetime.now()
            execution_time = (completed_at - started_at).total_seconds()

            return CleanupResult(
                task_id=task.task_id,
                started_at=started_at,
                completed_at=completed_at,
                success=False,
                message="Resource cleanup failed",
                error=str(e),
                execution_time_seconds=execution_time,
            )

    def can_execute(self, task: CleanupTask) -> bool:
        """Check if this strategy can execute the task."""
        return task.tags.get("cleanup_type") == "resource"


class MetricsCleanupStrategy(CleanupStrategy):
    """Cleanup strategy for metrics data."""

    async def execute(self, task: CleanupTask) -> CleanupResult:
        """Execute metrics cleanup."""
        started_at = datetime.now()

        try:
            metrics_collector = get_metrics_collector()

            # Get cleanup parameters from task tags
            days_to_keep = int(task.tags.get("days_to_keep", 7))
            cutoff_time = datetime.now() - timedelta(days=days_to_keep)

            # Clean up old metric values and aggregations
            cleaned_metrics = 0
            for metric_name in list(metrics_collector.metric_values.keys()):
                values = metrics_collector.metric_values[metric_name]
                original_count = len(values)

                # Remove old values
                while values and values[0].timestamp < cutoff_time:
                    values.popleft()

                cleaned_metrics += original_count - len(values)

            completed_at = datetime.now()
            execution_time = (completed_at - started_at).total_seconds()

            return CleanupResult(
                task_id=task.task_id,
                started_at=started_at,
                completed_at=completed_at,
                success=True,
                message=f"Cleaned up {cleaned_metrics} metric values older than {days_to_keep} days",
                resources_cleaned=cleaned_metrics,
                execution_time_seconds=execution_time,
            )

        except Exception as e:
            completed_at = datetime.now()
            execution_time = (completed_at - started_at).total_seconds()

            return CleanupResult(
                task_id=task.task_id,
                started_at=started_at,
                completed_at=completed_at,
                success=False,
                message="Metrics cleanup failed",
                error=str(e),
                execution_time_seconds=execution_time,
            )

    def can_execute(self, task: CleanupTask) -> bool:
        """Check if this strategy can execute the task."""
        return task.tags.get("cleanup_type") == "metrics"


class CacheCleanupStrategy(CleanupStrategy):
    """Cleanup strategy for cache management."""

    async def execute(self, task: CleanupTask) -> CleanupResult:
        """Execute cache cleanup."""
        started_at = datetime.now()

        try:
            # Get cache cleanup parameters
            max_size = int(task.tags.get("max_size", 1000))
            ttl_seconds = int(task.tags.get("ttl_seconds", 3600))

            # Simulate cache cleanup (in real implementation, this would interact with cache)
            cleaned_items = 0
            bytes_freed = 0

            # This is a placeholder for actual cache cleanup logic
            # In a real implementation, you would:
            # 1. Connect to your cache system (Redis, Memcached, etc.)
            # 2. Remove expired items
            # 3. Enforce size limits
            # 4. Track bytes freed

            completed_at = datetime.now()
            execution_time = (completed_at - started_at).total_seconds()

            return CleanupResult(
                task_id=task.task_id,
                started_at=started_at,
                completed_at=completed_at,
                success=True,
                message=f"Cache cleanup completed: {cleaned_items} items removed",
                resources_cleaned=cleaned_items,
                bytes_freed=bytes_freed,
                execution_time_seconds=execution_time,
            )

        except Exception as e:
            completed_at = datetime.now()
            execution_time = (completed_at - started_at).total_seconds()

            return CleanupResult(
                task_id=task.task_id,
                started_at=started_at,
                completed_at=completed_at,
                success=False,
                message="Cache cleanup failed",
                error=str(e),
                execution_time_seconds=execution_time,
            )

    def can_execute(self, task: CleanupTask) -> bool:
        """Check if this strategy can execute the task."""
        return task.tags.get("cleanup_type") == "cache"


class CleanupScheduler:
    """Automated cleanup scheduler with multiple trigger types."""

    def __init__(self, max_concurrent_tasks: int = 5):
        self.max_concurrent_tasks = max_concurrent_tasks

        # Task management
        self.tasks: Dict[str, CleanupTask] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running_tasks: Set[str] = set()

        # Cleanup strategies
        self.strategies: List[CleanupStrategy] = [
            ResourceCleanupStrategy(),
            MetricsCleanupStrategy(),
            CacheCleanupStrategy(),
        ]

        # Execution tracking
        self.execution_history: List[CleanupResult] = []
        self.max_history_size = 1000

        # Background tasks
        self._background_tasks: Set[asyncio.Task] = set()
        self._running = False
        self._scheduler_thread: Optional[threading.Thread] = None

        # Metrics
        self.scheduler_metrics = {
            "total_tasks_run": 0,
            "total_successful_runs": 0,
            "total_failed_runs": 0,
            "average_execution_time": 0.0,
            "total_resources_cleaned": 0,
            "total_bytes_freed": 0,
        }

        # Initialize default tasks
        self._initialize_default_tasks()

        logger.info(
            f"Cleanup scheduler initialized with max concurrent tasks: {max_concurrent_tasks}"
        )

    def _initialize_default_tasks(self):
        """Initialize default cleanup tasks."""
        default_tasks = [
            CleanupTask(
                task_id="resource_cleanup_hourly",
                name="Hourly Resource Cleanup",
                description="Clean up leaked and old resources every hour",
                cleanup_function=None,  # Will be handled by strategy
                trigger_type=CleanupTriggerType.SCHEDULED,
                priority=CleanupPriority.MEDIUM,
                schedule_expression="0 * * * *",  # Every hour
                tags={"cleanup_type": "resource", "resource_type": "all"},
            ),
            CleanupTask(
                task_id="metrics_cleanup_daily",
                name="Daily Metrics Cleanup",
                description="Clean up old metrics data daily",
                cleanup_function=None,
                trigger_type=CleanupTriggerType.SCHEDULED,
                priority=CleanupPriority.LOW,
                schedule_expression="0 2 * * *",  # Daily at 2 AM
                tags={"cleanup_type": "metrics", "days_to_keep": "7"},
            ),
            CleanupTask(
                task_id="cache_cleanup_6hourly",
                name="6-Hourly Cache Cleanup",
                description="Clean up cache every 6 hours",
                cleanup_function=None,
                trigger_type=CleanupTriggerType.SCHEDULED,
                priority=CleanupPriority.MEDIUM,
                schedule_expression="0 */6 * * *",  # Every 6 hours
                tags={"cleanup_type": "cache", "ttl_seconds": "21600"},
            ),
            CleanupTask(
                task_id="memory_cleanup_threshold",
                name="Memory Threshold Cleanup",
                description="Clean up when memory usage is high",
                cleanup_function=None,
                trigger_type=CleanupTriggerType.THRESHOLD_BASED,
                priority=CleanupPriority.HIGH,
                threshold_condition="memory_usage_percent > 85",
                tags={"cleanup_type": "resource", "resource_type": "memory"},
            ),
        ]

        for task in default_tasks:
            self.add_task(task)

    async def start(self):
        """Start the cleanup scheduler."""
        if self._running:
            return

        self._running = True

        # Start background workers
        for i in range(self.max_concurrent_tasks):
            self._background_tasks.add(asyncio.create_task(self._worker(f"worker-{i}")))

        # Start scheduler thread for time-based triggers
        self._scheduler_thread = threading.Thread(
            target=self._run_scheduler, daemon=True
        )
        self._scheduler_thread.start()

        # Start threshold monitoring
        self._background_tasks.add(asyncio.create_task(self._threshold_monitor_loop()))

        logger.info("Cleanup scheduler started")

    async def stop(self):
        """Stop the cleanup scheduler."""
        self._running = False

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        self._background_tasks.clear()

        # Wait for scheduler thread to finish
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self._scheduler_thread.join(timeout=5)

        logger.info("Cleanup scheduler stopped")

    def add_task(self, task: CleanupTask) -> bool:
        """Add a cleanup task."""
        try:
            self.tasks[task.task_id] = task

            # Schedule the task if it's time-based
            if (
                task.trigger_type == CleanupTriggerType.SCHEDULED
                and task.schedule_expression
            ):
                self._schedule_task(task)

            logger.info(f"Added cleanup task: {task.task_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to add task {task.task_id}: {e}")
            return False

    def remove_task(self, task_id: str) -> bool:
        """Remove a cleanup task."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info(f"Removed cleanup task: {task_id}")
            return True
        return False

    def enable_task(self, task_id: str) -> bool:
        """Enable a cleanup task."""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True
            logger.info(f"Enabled cleanup task: {task_id}")
            return True
        return False

    def disable_task(self, task_id: str) -> bool:
        """Disable a cleanup task."""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False
            logger.info(f"Disabled cleanup task: {task_id}")
            return True
        return False

    async def run_task_now(self, task_id: str) -> bool:
        """Run a task immediately."""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        await self.task_queue.put((task, CleanupTriggerType.MANUAL))

        logger.info(f"Queued task for immediate execution: {task_id}")
        return True

    def _schedule_task(self, task: CleanupTask):
        """Schedule a task using the schedule library."""
        if not task.schedule_expression:
            return

        try:
            # Parse cron expression (simplified)
            parts = task.schedule_expression.split()
            if len(parts) != 5:
                logger.warning(
                    f"Invalid schedule expression for task {task.task_id}: {task.schedule_expression}"
                )
                return

            minute, hour, day, month, weekday = parts

            # Create job function
            def job():
                if task.enabled and self._running:
                    asyncio.create_task(
                        self.task_queue.put((task, CleanupTriggerType.SCHEDULED))
                    )

            # Schedule the job
            if minute == "*" and hour == "*":
                schedule.every().minute.do(job)
            elif minute == "0" and hour == "*":
                schedule.every().hour.do(job)
            elif minute == "0" and hour != "*":
                schedule.every().day.at(f"{hour}:00").do(job)
            else:
                # More complex scheduling would require a proper cron parser
                logger.warning(
                    f"Complex scheduling not fully supported for task {task.task_id}"
                )

            logger.debug(
                f"Scheduled task {task.task_id} with expression: {task.schedule_expression}"
            )

        except Exception as e:
            logger.error(f"Failed to schedule task {task.task_id}: {e}")

    def _run_scheduler(self):
        """Run the scheduler in a separate thread."""
        while self._running:
            try:
                schedule.run_pending()
                time.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Scheduler thread error: {e}")

    async def _worker(self, worker_name: str):
        """Worker process for executing cleanup tasks."""
        logger.info(f"Started cleanup worker: {worker_name}")

        while self._running:
            try:
                # Get task from queue
                task, trigger_type = await asyncio.wait_for(
                    self.task_queue.get(), timeout=1.0
                )

                # Check if task is still enabled
                if not task.enabled:
                    continue

                # Check if task is already running
                if task.task_id in self.running_tasks:
                    continue

                # Execute the task
                await self._execute_task(task, trigger_type)

            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")

        logger.info(f"Stopped cleanup worker: {worker_name}")

    async def _execute_task(self, task: CleanupTask, trigger_type: CleanupTriggerType):
        """Execute a cleanup task."""
        self.running_tasks.add(task.task_id)

        try:
            started_at = datetime.now()

            # Find appropriate strategy
            strategy = None
            for s in self.strategies:
                if s.can_execute(task):
                    strategy = s
                    break

            if not strategy:
                logger.warning(f"No strategy found for task {task.task_id}")
                return

            # Execute with retry logic
            result = None
            for attempt in range(task.retry_count + 1):
                try:
                    result = await strategy.execute(task)
                    result.retry_attempt = attempt

                    if result.success:
                        break
                    else:
                        logger.warning(
                            f"Task {task.task_id} failed on attempt {attempt + 1}: {result.error}"
                        )

                        if attempt < task.retry_count:
                            await asyncio.sleep(task.retry_delay_seconds)

                except Exception as e:
                    logger.error(
                        f"Task {task.task_id} exception on attempt {attempt + 1}: {e}"
                    )

                    if attempt == task.retry_count:
                        result = CleanupResult(
                            task_id=task.task_id,
                            started_at=started_at,
                            completed_at=datetime.now(),
                            success=False,
                            message="Task execution failed",
                            error=str(e),
                            retry_attempt=attempt,
                        )

            # Update task statistics
            task.last_run = started_at
            task.run_count += 1

            if result and result.success:
                task.success_count += 1
            else:
                task.failure_count += 1

            # Update average duration
            if result:
                task.average_duration_seconds = (
                    task.average_duration_seconds * (task.run_count - 1)
                    + result.execution_time_seconds
                ) / task.run_count

            # Store result
            if result:
                self.execution_history.append(result)

                # Keep history size limited
                if len(self.execution_history) > self.max_history_size:
                    self.execution_history = self.execution_history[
                        -self.max_history_size :
                    ]

                # Update scheduler metrics
                self.scheduler_metrics["total_tasks_run"] += 1
                if result.success:
                    self.scheduler_metrics["total_successful_runs"] += 1
                else:
                    self.scheduler_metrics["total_failed_runs"] += 1

                self.scheduler_metrics[
                    "total_resources_cleaned"
                ] += result.resources_cleaned
                self.scheduler_metrics["total_bytes_freed"] += result.bytes_freed

                # Update average execution time
                total_runs = self.scheduler_metrics["total_tasks_run"]
                current_avg = self.scheduler_metrics["average_execution_time"]
                self.scheduler_metrics["average_execution_time"] = (
                    current_avg * (total_runs - 1) + result.execution_time_seconds
                ) / total_runs

            logger.info(
                f"Completed task {task.task_id}: {result.message if result else 'No result'}"
            )

        except Exception as e:
            logger.error(f"Failed to execute task {task.task_id}: {e}")
        finally:
            self.running_tasks.discard(task.task_id)

    async def _threshold_monitor_loop(self):
        """Monitor thresholds and trigger cleanup tasks."""
        while self._running:
            try:
                await asyncio.sleep(60)  # Check every minute

                # Check system thresholds
                await self._check_system_thresholds()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Threshold monitoring error: {e}")

    async def _check_system_thresholds(self):
        """Check system thresholds and trigger appropriate tasks."""
        try:
            # Get system metrics
            metrics_collector = get_metrics_collector()

            # Check memory usage
            memory_values = metrics_collector.get_metric_values(
                "system_memory_percent", limit=1
            )
            if memory_values:
                memory_percent = memory_values[-1]["value"]
                if memory_percent > 85:
                    # Trigger memory cleanup
                    memory_task = self.tasks.get("memory_cleanup_threshold")
                    if memory_task and memory_task.enabled:
                        await self.task_queue.put(
                            (memory_task, CleanupTriggerType.THRESHOLD_BASED)
                        )

            # Check resource count
            resource_values = metrics_collector.get_metric_values(
                "resource_count", limit=1
            )
            if resource_values:
                resource_count = resource_values[-1]["value"]
                if resource_count > 1000:  # Threshold for too many resources
                    # Trigger resource cleanup
                    resource_task = self.tasks.get("resource_cleanup_hourly")
                    if resource_task and resource_task.enabled:
                        await self.task_queue.put(
                            (resource_task, CleanupTriggerType.THRESHOLD_BASED)
                        )

        except Exception as e:
            logger.error(f"Threshold check error: {e}")

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific task."""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        status = task.to_dict()
        status["is_running"] = task_id in self.running_tasks

        return status

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all cleanup tasks."""
        return [
            {**task.to_dict(), "is_running": task_id in self.running_tasks}
            for task_id, task in self.tasks.items()
        ]

    def get_execution_history(
        self,
        task_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get execution history."""
        history = self.execution_history

        if task_id:
            history = [result for result in history if result.task_id == task_id]

        # Sort by completion time (most recent first)
        history.sort(key=lambda x: x.completed_at, reverse=True)

        return [result.to_dict() for result in history[:limit]]

    def get_scheduler_metrics(self) -> Dict[str, Any]:
        """Get scheduler metrics."""
        return {
            **self.scheduler_metrics,
            "total_tasks": len(self.tasks),
            "enabled_tasks": len([t for t in self.tasks.values() if t.enabled]),
            "running_tasks": len(self.running_tasks),
            "queued_tasks": self.task_queue.qsize(),
            "success_rate": (
                self.scheduler_metrics["total_successful_runs"]
                / self.scheduler_metrics["total_tasks_run"]
                * 100
                if self.scheduler_metrics["total_tasks_run"] > 0
                else 0
            ),
        }

    def add_strategy(self, strategy: CleanupStrategy):
        """Add a custom cleanup strategy."""
        self.strategies.append(strategy)
        logger.info(f"Added cleanup strategy: {strategy.__class__.__name__}")


# Global cleanup scheduler instance
_cleanup_scheduler: Optional[CleanupScheduler] = None


def get_cleanup_scheduler() -> CleanupScheduler:
    """Get or create the global cleanup scheduler instance."""
    global _cleanup_scheduler
    if _cleanup_scheduler is None:
        _cleanup_scheduler = CleanupScheduler()
    return _cleanup_scheduler


async def start_cleanup_scheduler():
    """Start the global cleanup scheduler."""
    scheduler = get_cleanup_scheduler()
    await scheduler.start()


async def stop_cleanup_scheduler():
    """Stop the global cleanup scheduler."""
    scheduler = get_cleanup_scheduler()
    if scheduler:
        await scheduler.stop()
