"""
Parallel Executor for Integration Components

Parallel execution engine for independent cognitive steps.
Implements PROMPT 68 from STREAM_3_COGNATIVE_ENGINE.
"""

import asyncio
import time
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from .models import ExecutionPlan, PlanStep


class ExecutionMode(Enum):
    """Execution modes for parallel processing."""

    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    ADAPTIVE = "adaptive"


class TaskStatus(Enum):
    """Status of parallel tasks."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class ParallelTask:
    """A task for parallel execution."""

    task_id: str
    step: PlanStep
    dependencies: Set[str]
    status: TaskStatus
    result: Any = None
    error: Optional[Exception] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time_ms: int = 0
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParallelExecutionResult:
    """Result of parallel execution."""

    execution_id: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    cancelled_tasks: int
    total_execution_time_ms: int
    task_results: Dict[str, Any]
    errors: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


class ParallelExecutor:
    """
    Parallel execution engine for independent cognitive steps.

    Manages dependency resolution and concurrent task execution.
    """

    def __init__(
        self, max_concurrent_tasks: int = 10, default_timeout_seconds: int = 300
    ):
        """
        Initialize the parallel executor.

        Args:
            max_concurrent_tasks: Maximum concurrent tasks
            default_timeout_seconds: Default timeout for tasks
        """
        self.max_concurrent_tasks = max_concurrent_tasks
        self.default_timeout_seconds = default_timeout_seconds

        # Task management
        self.active_tasks: Dict[str, ParallelTask] = {}
        self.task_semaphore = asyncio.Semaphore(max_concurrent_tasks)

        # Execution statistics
        self.stats = {
            "total_executions": 0,
            "total_tasks": 0,
            "parallel_efficiency": 0.0,
            "average_execution_time_ms": 0.0,
        }

    async def execute_parallel(
        self,
        plan: ExecutionPlan,
        context: Dict[str, Any] = None,
        mode: ExecutionMode = ExecutionMode.PARALLEL,
    ) -> ParallelExecutionResult:
        """
        Execute plan steps in parallel where possible.

        Args:
            plan: Execution plan to execute
            context: Execution context
            mode: Execution mode

        Returns:
            Parallel execution result
        """
        execution_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            # Build dependency graph
            dependency_graph = self._build_dependency_graph(plan.steps)

            # Execute based on mode
            if mode == ExecutionMode.PARALLEL:
                result = await self._execute_parallel_mode(
                    plan, dependency_graph, context
                )
            elif mode == ExecutionMode.SEQUENTIAL:
                result = await self._execute_sequential_mode(plan, context)
            elif mode == ExecutionMode.ADAPTIVE:
                result = await self._execute_adaptive_mode(
                    plan, dependency_graph, context
                )
            else:
                raise ValueError(f"Unknown execution mode: {mode}")

            # Calculate execution time
            total_execution_time_ms = int((time.time() - start_time) * 1000)

            # Update statistics
            self._update_stats(result, total_execution_time_ms)

            result.execution_id = execution_id
            result.total_execution_time_ms = total_execution_time_ms

            return result

        except Exception as e:
            return ParallelExecutionResult(
                execution_id=execution_id,
                total_tasks=0,
                completed_tasks=0,
                failed_tasks=0,
                cancelled_tasks=0,
                total_execution_time_ms=int((time.time() - start_time) * 1000),
                task_results={},
                errors=[{"error": str(e), "traceback": traceback.format_exc()}],
                metadata={"mode": mode.value},
            )

    async def _execute_parallel_mode(
        self,
        plan: ExecutionPlan,
        dependency_graph: Dict[str, Set[str]],
        context: Dict[str, Any],
    ) -> ParallelExecutionResult:
        """Execute in parallel mode (maximum concurrency)."""
        task_results = {}
        errors = []

        # Create tasks for all steps
        for step in plan.steps:
            task = ParallelTask(
                task_id=str(uuid.uuid4()),
                step=step,
                dependencies=dependency_graph.get(step.id, set()),
                status=TaskStatus.PENDING,
                max_retries=3,
            )
            self.active_tasks[task.task_id] = task

        # Execute tasks with dependency resolution
        completed_tasks = set()
        failed_tasks = set()

        while len(completed_tasks) + len(failed_tasks) < len(plan.steps):
            # Find tasks ready to execute
            ready_tasks = self._get_ready_tasks(
                self.active_tasks, completed_tasks, failed_tasks
            )

            if not ready_tasks:
                # Check if we're stuck (circular dependencies or all failed)
                remaining_tasks = (
                    set(self.active_tasks.keys()) - completed_tasks - failed_tasks
                )
                if remaining_tasks:
                    # Tasks are blocked by failed dependencies
                    for task_id in remaining_tasks:
                        task = self.active_tasks[task_id]
                        task.status = TaskStatus.FAILED
                        task.error = Exception("Blocked by failed dependencies")
                        failed_tasks.add(task_id)
                    break
                else:
                    break

            # Execute ready tasks in parallel
            execution_tasks = []
            for task in ready_tasks:
                execution_task = self._execute_single_task(task, context)
                execution_tasks.append(execution_task)

            # Wait for all tasks to complete
            task_results_list = await asyncio.gather(
                *execution_tasks, return_exceptions=True
            )

            # Process results
            for i, task in enumerate(ready_tasks):
                result = task_results_list[i]

                if isinstance(result, Exception):
                    # Task failed
                    task.status = TaskStatus.FAILED
                    task.error = result
                    task.end_time = datetime.now()
                    task.execution_time_ms = (
                        int((task.end_time - task.start_time).total_seconds() * 1000)
                        if task.start_time
                        else 0
                    )
                    failed_tasks.add(task.task_id)
                    errors.append(
                        {
                            "task_id": task.task_id,
                            "step_id": task.step.id,
                            "error": str(result),
                            "traceback": traceback.format_exc(),
                        }
                    )
                else:
                    # Task completed successfully
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    task.end_time = datetime.now()
                    task.execution_time_ms = (
                        int((task.end_time - task.start_time).total_seconds() * 1000)
                        if task.start_time
                        else 0
                    )
                    completed_tasks.add(task.task_id)
                    task_results[task.task_id] = result

        # Build final result
        return ParallelExecutionResult(
            execution_id="",  # Will be set by caller
            total_tasks=len(plan.steps),
            completed_tasks=len(completed_tasks),
            failed_tasks=len(failed_tasks),
            cancelled_tasks=0,
            total_execution_time_ms=0,  # Will be set by caller
            task_results=task_results,
            errors=errors,
            metadata={"mode": "parallel"},
        )

    async def _execute_sequential_mode(
        self, plan: ExecutionPlan, context: Dict[str, Any]
    ) -> ParallelExecutionResult:
        """Execute in sequential mode (one at a time)."""
        task_results = {}
        errors = []

        for step in plan.steps:
            task = ParallelTask(
                task_id=str(uuid.uuid4()),
                step=step,
                dependencies=set(),
                status=TaskStatus.PENDING,
                max_retries=3,
            )

            try:
                result = await self._execute_single_task(task, context)
                task.status = TaskStatus.COMPLETED
                task.result = result
                task_results[task.task_id] = result

            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = e
                errors.append(
                    {
                        "task_id": task.task_id,
                        "step_id": step.id,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                )

        return ParallelExecutionResult(
            execution_id="",  # Will be set by caller
            total_tasks=len(plan.steps),
            completed_tasks=len(
                [
                    t
                    for t in self.active_tasks.values()
                    if t.status == TaskStatus.COMPLETED
                ]
            ),
            failed_tasks=len(
                [t for t in self.active_tasks.values() if t.status == TaskStatus.FAILED]
            ),
            cancelled_tasks=0,
            total_execution_time_ms=0,  # Will be set by caller
            task_results=task_results,
            errors=errors,
            metadata={"mode": "sequential"},
        )

    async def _execute_adaptive_mode(
        self,
        plan: ExecutionPlan,
        dependency_graph: Dict[str, Set[str]],
        context: Dict[str, Any],
    ) -> ParallelExecutionResult:
        """Execute in adaptive mode (intelligent parallelization)."""
        # Analyze dependency structure to determine optimal strategy
        parallel_groups = self._analyze_dependencies(dependency_graph)

        task_results = {}
        errors = []
        completed_groups = set()

        for group in parallel_groups:
            # Execute group in parallel
            group_tasks = []
            for step_id in group:
                step = next(s for s in plan.steps if s.id == step_id)
                task = ParallelTask(
                    task_id=str(uuid.uuid4()),
                    step=step,
                    dependencies=set(),
                    status=TaskStatus.PENDING,
                    max_retries=3,
                )
                self.active_tasks[task.task_id] = task
                group_tasks.append(task)

            # Execute group tasks in parallel
            execution_tasks = []
            for task in group_tasks:
                execution_task = self._execute_single_task(task, context)
                execution_tasks.append(execution_task)

            # Wait for group to complete
            group_results = await asyncio.gather(
                *execution_tasks, return_exceptions=True
            )

            # Process group results
            for i, task in enumerate(group_tasks):
                result = group_results[i]

                if isinstance(result, Exception):
                    task.status = TaskStatus.FAILED
                    task.error = result
                    errors.append(
                        {
                            "task_id": task.task_id,
                            "step_id": task.step.id,
                            "error": str(result),
                            "traceback": traceback.format_exc(),
                        }
                    )
                else:
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    task_results[task.task_id] = result

            completed_groups.add(tuple(group))

        return ParallelExecutionResult(
            execution_id="",  # Will be set by caller
            total_tasks=len(plan.steps),
            completed_tasks=len(
                [
                    t
                    for t in self.active_tasks.values()
                    if t.status == TaskStatus.COMPLETED
                ]
            ),
            failed_tasks=len(
                [t for t in self.active_tasks.values() if t.status == TaskStatus.FAILED]
            ),
            cancelled_tasks=0,
            total_execution_time_ms=0,  # Will be set by caller
            task_results=task_results,
            errors=errors,
            metadata={"mode": "adaptive", "parallel_groups": len(parallel_groups)},
        )

    async def _execute_single_task(
        self, task: ParallelTask, context: Dict[str, Any]
    ) -> Any:
        """Execute a single task."""
        async with self.task_semaphore:
            task.status = TaskStatus.RUNNING
            task.start_time = datetime.now()

            try:
                # Get timeout for this task
                timeout = (
                    task.step.estimated_time_seconds or self.default_timeout_seconds
                )

                # Execute task with timeout
                result = await asyncio.wait_for(
                    self._execute_step(task.step, context), timeout=timeout
                )

                return result

            except asyncio.TimeoutError:
                task.status = TaskStatus.TIMEOUT
                task.error = Exception("Task execution timeout")
                raise

            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = e
                raise

            finally:
                task.end_time = datetime.now()
                if task.start_time:
                    task.execution_time_ms = int(
                        (task.end_time - task.start_time).total_seconds() * 1000
                    )

    async def _execute_step(self, step: PlanStep, context: Dict[str, Any]) -> Any:
        """Execute a single step."""
        # This would integrate with the actual agent/step execution
        # For now, simulate execution
        await asyncio.sleep(0.1)  # Simulate processing time

        # Return mock result
        return {
            "step_id": step.id,
            "agent": step.agent,
            "tools": step.tools,
            "inputs": step.inputs,
            "output": f"Mock output for step {step.id}",
            "execution_time": step.estimated_time_seconds,
        }

    def _build_dependency_graph(self, steps: List[PlanStep]) -> Dict[str, Set[str]]:
        """Build dependency graph from steps."""
        graph = {}

        for step in steps:
            graph[step.id] = set(step.dependencies)

        return graph

    def _get_ready_tasks(
        self, tasks: Dict[str, ParallelTask], completed: Set[str], failed: Set[str]
    ) -> List[ParallelTask]:
        """Get tasks that are ready to execute."""
        ready_tasks = []

        for task in tasks.values():
            if task.status != TaskStatus.PENDING:
                continue

            if task.task_id in completed or task.task_id in failed:
                continue

            # Check if all dependencies are completed
            if task.dependencies.issubset(completed):
                ready_tasks.append(task)

        return ready_tasks

    def _analyze_dependencies(
        self, dependency_graph: Dict[str, Set[str]]
    ) -> List[List[str]]:
        """Analyze dependencies to find optimal parallel groups."""
        # Find strongly connected components
        visited = set()
        groups = []

        for node in dependency_graph:
            if node not in visited:
                group = []
                self._dfs_visit(node, dependency_graph, visited, group)
                if group:
                    groups.append(group)

        return groups

    def _dfs_visit(
        self, node: str, graph: Dict[str, Set[str]], visited: Set[str], group: List[str]
    ) -> None:
        """DFS visit for finding connected components."""
        visited.add(node)
        group.append(node)

        for neighbor in graph.get(node, set()):
            if neighbor not in visited:
                self._dfs_visit(neighbor, graph, visited, group)

    def _update_stats(
        self, result: ParallelExecutionResult, execution_time_ms: int
    ) -> None:
        """Update execution statistics."""
        self.stats["total_executions"] += 1
        self.stats["total_tasks"] += result.total_tasks

        # Calculate parallel efficiency
        if result.total_tasks > 1:
            theoretical_sequential_time = execution_time_ms * result.total_tasks
            actual_parallel_time = execution_time_ms
            self.stats["parallel_efficiency"] = theoretical_sequential_time / max(
                actual_parallel_time, 1
            )

        # Update average execution time
        total_time = (
            self.stats["average_execution_time_ms"]
            * (self.stats["total_executions"] - 1)
            + execution_time_ms
        )
        self.stats["average_execution_time_ms"] = (
            total_time / self.stats["total_executions"]
        )

    def get_executor_stats(self) -> Dict[str, Any]:
        """Get executor statistics."""
        return {
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "default_timeout_seconds": self.default_timeout_seconds,
            "active_tasks": len(self.active_tasks),
            "available_permits": self.task_semaphore._value,
            **self.stats,
        }

    async def cancel_all_tasks(self) -> int:
        """Cancel all active tasks."""
        cancelled_count = 0

        for task in self.active_tasks.values():
            if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                task.status = TaskStatus.CANCELLED
                cancelled_count += 1

        return cancelled_count

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a specific task."""
        task = self.active_tasks.get(task_id)
        if task and task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            task.status = TaskStatus.CANCELLED
            return True
        return False

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        task = self.active_tasks.get(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "step_id": task.step.id,
            "step_description": task.step.description,
            "status": task.status.value,
            "dependencies": list(task.dependencies),
            "retry_count": task.retry_count,
            "max_retries": task.max_retries,
            "start_time": task.start_time.isoformat() if task.start_time else None,
            "execution_time_ms": task.execution_time_ms,
            "error": str(task.error) if task.error else None,
        }

    def get_all_task_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all tasks."""
        return {
            task_id: self.get_task_status(task_id)
            for task_id in self.active_tasks.keys()
        }
