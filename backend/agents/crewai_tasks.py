"""
S.W.A.R.M. Phase 1: CrewAI Task Management System
Advanced task management with dependency handling and scheduling
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from crewai import Task
from pydantic import BaseModel

from models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.crewai.tasks")


class TaskStatus(Enum):
    """Task lifecycle status."""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Task priority levels."""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class TaskDependency:
    """Task dependency relationship."""

    task_id: str
    depends_on: str
    dependency_type: str = "completion"  # completion, success, data
    required_data: Optional[Dict[str, Any]] = None


@dataclass
class TaskMetrics:
    """Task execution metrics."""

    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    token_usage: Dict[str, int] = field(default_factory=dict)
    retry_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None


class EnhancedTask:
    """
    Enhanced task with advanced dependency management and monitoring.
    """

    def __init__(
        self,
        task_id: str,
        description: str,
        expected_output: str,
        agent: Any,
        priority: TaskPriority = TaskPriority.MEDIUM,
        max_retries: int = 3,
        timeout: Optional[float] = None,
        callback: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        self.task_id = task_id
        self.description = description
        self.expected_output = expected_output
        self.agent = agent
        self.priority = priority
        self.max_retries = max_retries
        self.timeout = timeout
        self.callback = callback
        self.metadata = metadata or {}

        # CrewAI task instance
        self.crewai_task = Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            **kwargs,
        )

        # State tracking
        self.status = TaskStatus.PENDING
        self.dependencies: List[TaskDependency] = []
        self.dependents: Set[str] = set()
        self.result: Optional[str] = None
        self.metrics = TaskMetrics()
        self._lock = asyncio.Lock()

    def add_dependency(self, depends_on: str, dependency_type: str = "completion"):
        """Add a dependency to this task."""
        dependency = TaskDependency(
            task_id=self.task_id, depends_on=depends_on, dependency_type=dependency_type
        )
        self.dependencies.append(dependency)
        logger.info(f"Task {self.task_id} depends on {depends_on}")

    def add_dependent(self, dependent_task_id: str):
        """Add a task that depends on this task."""
        self.dependents.add(dependent_task_id)
        logger.info(f"Task {self.task_id} is dependency for {dependent_task_id}")

    def is_ready(self, task_manager: "CrewTaskManager") -> bool:
        """Check if task is ready to execute based on dependencies."""
        if self.status != TaskStatus.PENDING:
            return False

        for dep in self.dependencies:
            dep_task = task_manager.get_task(dep.depends_on)
            if not dep_task:
                logger.warning(
                    f"Dependency task {dep.depends_on} not found for {self.task_id}"
                )
                return False

            if dep.dependency_type == "completion":
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
            elif dep.dependency_type == "success":
                if (
                    dep_task.status != TaskStatus.COMPLETED
                    or dep_task.metrics.error_count > 0
                ):
                    return False
            elif dep.dependency_type == "data":
                if not dep_task.result or dep_task.status != TaskStatus.COMPLETED:
                    return False

        return True

    def get_dependency_data(self, task_manager: "CrewTaskManager") -> Dict[str, Any]:
        """Get data from completed dependencies."""
        dependency_data = {}

        for dep in self.dependencies:
            if dep.dependency_type == "data":
                dep_task = task_manager.get_task(dep.depends_on)
                if dep_task and dep_task.result:
                    dependency_data[dep.depends_on] = dep_task.result

        return dependency_data

    async def execute(self, task_manager: "CrewTaskManager") -> str:
        """Execute the task with error handling and retries."""
        async with self._lock:
            if self.status != TaskStatus.READY:
                raise ValueError(f"Task {self.task_id} is not ready for execution")

            self.status = TaskStatus.RUNNING
            self.metrics.started_at = datetime.now()

            logger.info(f"Executing task {self.task_id}")

            for attempt in range(self.max_retries + 1):
                try:
                    # Get dependency data
                    context = self.get_dependency_data(task_manager)

                    # Execute with timeout
                    if self.timeout:
                        result = await asyncio.wait_for(
                            self._execute_with_context(context), timeout=self.timeout
                        )
                    else:
                        result = await self._execute_with_context(context)

                    self.result = result
                    self.status = TaskStatus.COMPLETED
                    self.metrics.completed_at = datetime.now()
                    self.metrics.execution_time = (
                        self.metrics.completed_at - self.metrics.started_at
                    ).total_seconds()

                    logger.info(f"Task {self.task_id} completed successfully")

                    # Call callback if provided
                    if self.callback:
                        await self.callback(self)

                    return result

                except asyncio.TimeoutError:
                    self.metrics.error_count += 1
                    self.metrics.last_error = f"Timeout after {self.timeout}s"
                    logger.error(
                        f"Task {self.task_id} timed out (attempt {attempt + 1})"
                    )

                except Exception as e:
                    self.metrics.error_count += 1
                    self.metrics.last_error = str(e)
                    logger.error(
                        f"Task {self.task_id} failed (attempt {attempt + 1}): {str(e)}"
                    )

                if attempt < self.max_retries:
                    self.metrics.retry_count += 1
                    # Exponential backoff
                    await asyncio.sleep(2**attempt)

            # All retries failed
            self.status = TaskStatus.FAILED
            self.metrics.completed_at = datetime.now()
            self.metrics.execution_time = (
                self.metrics.completed_at - self.metrics.started_at
            ).total_seconds()

            logger.error(
                f"Task {self.task_id} failed after {self.max_retries + 1} attempts"
            )
            raise RuntimeError(
                f"Task {self.task_id} execution failed: {self.metrics.last_error}"
            )

    async def _execute_with_context(self, context: Dict[str, Any]) -> str:
        """Execute the CrewAI task with context."""
        # Add context to task description if available
        if context:
            enhanced_description = f"{self.description}\n\nContext from dependencies:\n"
            for dep_id, dep_result in context.items():
                enhanced_description += f"- {dep_id}: {dep_result}\n"

            # Update CrewAI task description
            self.crewai_task.description = enhanced_description

        # Execute the CrewAI task
        result = self.crewai_task.execute()
        return result


class CrewTaskManager:
    """
    Advanced task management system for CrewAI integration.
    Handles dependencies, priorities, scheduling, and monitoring.
    """

    def __init__(self, max_concurrent_tasks: int = 5):
        self.tasks: Dict[str, EnhancedTask] = {}
        self.task_queue: List[str] = []
        self.running_tasks: Set[str] = set()
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
        self.max_concurrent_tasks = max_concurrent_tasks
        self._scheduler_running = False
        self._scheduler_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    def create_task(
        self,
        description: str,
        expected_output: str,
        agent: Any,
        task_id: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: Optional[List[str]] = None,
        max_retries: int = 3,
        timeout: Optional[float] = None,
        callback: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        """Create an enhanced task with dependency tracking."""
        if not task_id:
            task_id = str(uuid.uuid4())

        if task_id in self.tasks:
            raise ValueError(f"Task {task_id} already exists")

        task = EnhancedTask(
            task_id=task_id,
            description=description,
            expected_output=expected_output,
            agent=agent,
            priority=priority,
            max_retries=max_retries,
            timeout=timeout,
            callback=callback,
            metadata=metadata,
            **kwargs,
        )

        self.tasks[task_id] = task

        # Add dependencies
        if dependencies:
            for dep_id in dependencies:
                task.add_dependency(dep_id)
                if dep_id in self.tasks:
                    self.tasks[dep_id].add_dependent(task_id)

        # Add to queue based on priority
        self._add_to_queue(task_id)

        logger.info(f"Created task {task_id} with priority {priority.name}")
        return task_id

    def _add_to_queue(self, task_id: str):
        """Add task to queue based on priority."""
        task = self.tasks[task_id]

        # Insert in priority order
        inserted = False
        for i, queued_id in enumerate(self.task_queue):
            queued_task = self.tasks[queued_id]
            if task.priority.value < queued_task.priority.value:
                self.task_queue.insert(i, task_id)
                inserted = True
                break

        if not inserted:
            self.task_queue.append(task_id)

    def get_task(self, task_id: str) -> Optional[EnhancedTask]:
        """Get task by ID."""
        return self.tasks.get(task_id)

    def get_task_status(self, task_id: str) -> TaskStatus:
        """Get current status of a task."""
        task = self.get_task(task_id)
        return task.status if task else TaskStatus.FAILED

    def get_ready_tasks(self) -> List[str]:
        """Get list of tasks ready to execute."""
        ready_tasks = []

        for task_id in self.task_queue:
            if task_id in self.running_tasks or task_id in self.completed_tasks:
                continue

            task = self.tasks[task_id]
            if task.is_ready(self):
                ready_tasks.append(task_id)

        return ready_tasks

    async def start_scheduler(self):
        """Start the task scheduler."""
        if self._scheduler_running:
            return

        self._scheduler_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Task scheduler started")

    async def stop_scheduler(self):
        """Stop the task scheduler."""
        self._scheduler_running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("Task scheduler stopped")

    async def _scheduler_loop(self):
        """Main scheduler loop."""
        while self._scheduler_running:
            try:
                await self._schedule_tasks()
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                await asyncio.sleep(1)

    async def _schedule_tasks(self):
        """Schedule ready tasks for execution."""
        async with self._lock:
            # Check if we can start more tasks
            if len(self.running_tasks) >= self.max_concurrent_tasks:
                return

            # Get ready tasks
            ready_tasks = self.get_ready_tasks()

            # Start tasks up to concurrency limit
            for task_id in ready_tasks:
                if len(self.running_tasks) >= self.max_concurrent_tasks:
                    break

                task = self.tasks[task_id]
                task.status = TaskStatus.READY
                self.running_tasks.add(task_id)

                # Start task execution
                asyncio.create_task(self._execute_task(task_id))

                logger.info(f"Scheduled task {task_id} for execution")

    async def _execute_task(self, task_id: str):
        """Execute a single task."""
        try:
            task = self.tasks[task_id]
            result = await task.execute(self)

            # Mark as completed
            self.completed_tasks.add(task_id)
            self.running_tasks.discard(task_id)

            # Remove from queue
            if task_id in self.task_queue:
                self.task_queue.remove(task_id)

            logger.info(f"Task {task_id} completed successfully")

        except Exception as e:
            # Mark as failed
            self.failed_tasks.add(task_id)
            self.running_tasks.discard(task_id)

            logger.error(f"Task {task_id} failed: {str(e)}")

    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> str:
        """Wait for a specific task to complete."""
        start_time = datetime.now()

        while True:
            task = self.get_task(task_id)
            if not task:
                raise ValueError(f"Task {task_id} not found")

            if task.status in [
                TaskStatus.COMPLETED,
                TaskStatus.FAILED,
                TaskStatus.CANCELLED,
            ]:
                if task.status == TaskStatus.COMPLETED:
                    return task.result
                else:
                    raise RuntimeError(
                        f"Task {task_id} failed: {task.metrics.last_error}"
                    )

            if timeout and (datetime.now() - start_time).total_seconds() > timeout:
                raise asyncio.TimeoutError(
                    f"Task {task_id} did not complete within {timeout}s"
                )

            await asyncio.sleep(0.1)

    async def wait_for_all_tasks(
        self, timeout: Optional[float] = None
    ) -> Dict[str, str]:
        """Wait for all tasks to complete."""
        start_time = datetime.now()

        while True:
            total_tasks = len(self.tasks)
            completed_tasks = len(self.completed_tasks) + len(self.failed_tasks)

            if completed_tasks >= total_tasks:
                results = {}
                for task_id, task in self.tasks.items():
                    if task.status == TaskStatus.COMPLETED:
                        results[task_id] = task.result
                    else:
                        results[task_id] = f"Failed: {task.metrics.last_error}"
                return results

            if timeout and (datetime.now() - start_time).total_seconds() > timeout:
                raise asyncio.TimeoutError(f"Not all tasks completed within {timeout}s")

            await asyncio.sleep(0.1)

    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive task management metrics."""
        total_tasks = len(self.tasks)
        completed_tasks = len(self.completed_tasks)
        failed_tasks = len(self.failed_tasks)
        running_tasks = len(self.running_tasks)

        # Calculate execution times
        execution_times = []
        for task in self.tasks.values():
            if task.metrics.execution_time:
                execution_times.append(task.metrics.execution_time)

        avg_execution_time = (
            sum(execution_times) / len(execution_times) if execution_times else 0
        )

        # Calculate success rate
        success_rate = completed_tasks / total_tasks if total_tasks > 0 else 0

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "running_tasks": running_tasks,
            "pending_tasks": total_tasks
            - completed_tasks
            - failed_tasks
            - running_tasks,
            "success_rate": success_rate,
            "average_execution_time": avg_execution_time,
            "queue_length": len(self.task_queue),
            "concurrency_limit": self.max_concurrent_tasks,
        }

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        task = self.get_task(task_id)
        if not task or task.status in [TaskStatus.RUNNING, TaskStatus.COMPLETED]:
            return False

        task.status = TaskStatus.CANCELLED
        if task_id in self.task_queue:
            self.task_queue.remove(task_id)

        logger.info(f"Cancelled task {task_id}")
        return True
