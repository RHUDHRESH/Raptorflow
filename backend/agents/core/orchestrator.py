"""
AgentOrchestrator for Raptorflow agent system.
Coordinates multi-agent workflows and manages complex task execution pipelines.
"""

import asyncio
import logging
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from backend.agents.config import ModelTier

from ..base import BaseAgent
from ..exceptions import OrchestrationError, ValidationError
from ..state import AgentState
from .dispatcher import AgentDispatcher, DispatchRequest, DispatchResult
from .memory import AgentMemoryManager
from .metrics import AgentMetricsCollector
from .registry import AgentRegistry
from .state import AgentStateManager

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TaskStatus(Enum):
    """Task execution status."""

    WAITING = "waiting"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskType(Enum):
    """Task types in workflow."""

    AGENT_TASK = "agent_task"
    CONDITION_TASK = "condition_task"
    PARALLEL_TASK = "parallel_task"
    SEQUENTIAL_TASK = "sequential_task"
    DATA_TASK = "data_task"
    CUSTOM_TASK = "custom_task"


@dataclass
class WorkflowTask:
    """Individual task in workflow."""

    task_id: str
    task_name: str
    task_type: TaskType
    agent_name: Optional[str]
    input_data: Dict[str, Any]
    output_schema: Optional[Dict[str, Any]]
    dependencies: List[str] = field(default_factory=list)
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    retry_config: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 300
    priority: str = "normal"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowDefinition:
    """Workflow definition."""

    workflow_id: str
    workflow_name: str
    description: str
    tasks: List[WorkflowTask]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    execution_strategy: str = "sequential"  # sequential, parallel, hybrid
    error_handling: str = "fail_fast"  # fail_fast, continue, retry
    timeout_seconds: int = 3600
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Workflow execution instance."""

    execution_id: str
    workflow_id: str
    workspace_id: str
    user_id: str
    input_data: Dict[str, Any]
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime]
    task_executions: Dict[str, "TaskExecution"] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskExecution:
    """Task execution instance."""

    task_id: str
    execution_id: str
    status: TaskStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    agent_result: Optional[DispatchResult]
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    retry_count: int = 0
    execution_time: float = 0.0


@dataclass
class OrchestrationPolicy:
    """Orchestration policy configuration."""

    max_concurrent_workflows: int = 10
    max_concurrent_tasks: int = 50
    default_timeout: int = 300
    max_retries: int = 3
    retry_backoff_seconds: int = 60
    checkpoint_interval: int = 30
    cleanup_interval_hours: int = 24


class AgentOrchestrator:
    """Orchestrates complex multi-agent workflows and task pipelines."""

    def __init__(
        self,
        dispatcher: AgentDispatcher,
        registry: AgentRegistry,
        state_manager: AgentStateManager,
        memory_manager: AgentMemoryManager,
        metrics: AgentMetricsCollector,
    ):
        self.dispatcher = dispatcher
        self.registry = registry
        self.state_manager = state_manager
        self.memory_manager = memory_manager
        self.metrics = metrics

        # Workflow storage
        self._workflows: Dict[str, WorkflowDefinition] = {}
        self._executions: Dict[str, WorkflowExecution] = {}
        self._execution_queue: deque = deque()

        # Task execution tracking
        self._task_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self._task_dependents: Dict[str, Set[str]] = defaultdict(set)
        self._ready_tasks: Set[str] = set()

        # Execution control
        self._running_workflows: Set[str] = set()
        self._running_tasks: Set[str] = set()
        self._paused_workflows: Set[str] = set()

        # Orchestration policy
        self.policy = OrchestrationPolicy()

        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)

        # Locks for thread safety
        self._orchestration_lock = asyncio.Lock()
        self._execution_lock = asyncio.Lock()

        # Background tasks
        self._background_tasks: Set[asyncio.Task] = set()

        # Start background cleanup task
        self._start_cleanup_task()

    async def register_workflow(self, workflow: WorkflowDefinition):
        """Register a new workflow definition."""
        async with self._orchestration_lock:
            # Validate workflow
            self._validate_workflow(workflow)

            # Store workflow
            self._workflows[workflow.workflow_id] = workflow

            # Build dependency graph
            self._build_dependency_graph(workflow)

            # Record metrics
            await self.metrics.record_workflow_registration(workflow)

            logger.info(f"Registered workflow: {workflow.workflow_name}")

    async def execute_workflow(
        self,
        workflow_id: str,
        workspace_id: str,
        user_id: str,
        input_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WorkflowExecution:
        """Execute a workflow."""
        try:
            async with self._execution_lock:
                # Get workflow definition
                workflow = self._workflows.get(workflow_id)
                if not workflow:
                    raise OrchestrationError(f"Workflow not found: {workflow_id}")

                # Check concurrent workflow limit
                if len(self._running_workflows) >= self.policy.max_concurrent_workflows:
                    raise OrchestrationError("Maximum concurrent workflows reached")

                # Create execution instance
                execution = WorkflowExecution(
                    execution_id=str(uuid.uuid4()),
                    workflow_id=workflow_id,
                    workspace_id=workspace_id,
                    user_id=user_id,
                    input_data=input_data,
                    status=WorkflowStatus.PENDING,
                    started_at=datetime.now(),
                    completed_at=None,
                    metadata=metadata or {},
                )

                # Initialize task executions
                for task in workflow.tasks:
                    execution.task_executions[task.task_id] = TaskExecution(
                        task_id=task.task_id,
                        execution_id=execution.execution_id,
                        status=TaskStatus.WAITING,
                        started_at=None,
                        completed_at=None,
                        agent_result=None,
                        output_data=None,
                        error_message=None,
                    )

                # Store execution
                self._executions[execution.execution_id] = execution
                self._execution_queue.append(execution.execution_id)

                # Start execution
                await self._start_workflow_execution(execution)

                logger.info(f"Started workflow execution: {execution.execution_id}")

                return execution

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            raise OrchestrationError(f"Workflow execution failed: {str(e)}")

    async def _start_workflow_execution(self, execution: WorkflowExecution):
        """Start workflow execution."""
        try:
            # Update status
            execution.status = WorkflowStatus.RUNNING
            self._running_workflows.add(execution.execution_id)

            # Emit event
            await self._emit_event("workflow_started", execution)

            # Get workflow definition
            workflow = self._workflows[execution.workflow_id]

            # Initialize ready tasks
            await self._initialize_ready_tasks(workflow, execution)

            # Start task execution loop
            asyncio.create_task(self._execute_workflow_loop(execution))

        except Exception as e:
            logger.error(f"Failed to start workflow execution: {e}")
            await self._fail_workflow_execution(execution, str(e))

    async def _initialize_ready_tasks(
        self, workflow: WorkflowDefinition, execution: WorkflowExecution
    ):
        """Initialize ready tasks for execution."""
        for task in workflow.tasks:
            if not task.dependencies:  # No dependencies, ready to run
                execution.task_executions[task.task_id].status = TaskStatus.READY
                self._ready_tasks.add(f"{execution.execution_id}:{task.task_id}")

    async def _execute_workflow_loop(self, execution: WorkflowExecution):
        """Main workflow execution loop."""
        try:
            workflow = self._workflows[execution.workflow_id]

            while True:
                # Check if workflow is complete
                if await self._is_workflow_complete(execution):
                    await self._complete_workflow_execution(execution)
                    break

                # Check if workflow should be paused
                if execution.execution_id in self._paused_workflows:
                    await asyncio.sleep(1)
                    continue

                # Get ready tasks
                ready_tasks = await self._get_ready_tasks(execution)

                # Execute tasks based on strategy
                if workflow.execution_strategy == "sequential":
                    await self._execute_sequential_tasks(execution, ready_tasks)
                elif workflow.execution_strategy == "parallel":
                    await self._execute_parallel_tasks(execution, ready_tasks)
                else:  # hybrid
                    await self._execute_hybrid_tasks(execution, ready_tasks)

                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"Workflow execution loop failed: {e}")
            await self._fail_workflow_execution(execution, str(e))

    async def _is_workflow_complete(self, execution: WorkflowExecution) -> bool:
        """Check if workflow execution is complete."""
        workflow = self._workflows[execution.workflow_id]

        for task in workflow.tasks:
            task_exec = execution.task_executions[task.task_id]
            if task_exec.status not in [TaskStatus.COMPLETED, TaskStatus.SKIPPED]:
                return False

        return True

    async def _get_ready_tasks(
        self, execution: WorkflowExecution
    ) -> List[WorkflowTask]:
        """Get tasks ready for execution."""
        workflow = self._workflows[execution.workflow_id]
        ready_tasks = []

        for task in workflow.tasks:
            task_exec = execution.task_executions[task.task_id]

            # Check if task is ready
            if task_exec.status == TaskStatus.READY:
                # Check dependencies
                dependencies_met = True
                for dep_id in task.dependencies:
                    dep_exec = execution.task_executions[dep_id]
                    if dep_exec.status != TaskStatus.COMPLETED:
                        dependencies_met = False
                        break

                if dependencies_met:
                    ready_tasks.append(task)

        return ready_tasks

    async def _execute_sequential_tasks(
        self, execution: WorkflowExecution, ready_tasks: List[WorkflowTask]
    ):
        """Execute tasks sequentially."""
        for task in ready_tasks:
            if execution.execution_id in self._paused_workflows:
                break

            await self._execute_task(execution, task)

    async def _execute_parallel_tasks(
        self, execution: WorkflowExecution, ready_tasks: List[WorkflowTask]
    ):
        """Execute tasks in parallel."""
        # Check concurrent task limit
        available_slots = self.policy.max_concurrent_tasks - len(self._running_tasks)
        tasks_to_execute = ready_tasks[:available_slots]

        # Create parallel execution tasks
        execution_tasks = []
        for task in tasks_to_execute:
            execution_tasks.append(
                asyncio.create_task(self._execute_task(execution, task))
            )

        # Wait for all tasks to complete
        if execution_tasks:
            await asyncio.gather(*execution_tasks, return_exceptions=True)

    async def _execute_hybrid_tasks(
        self, execution: WorkflowExecution, ready_tasks: List[WorkflowTask]
    ):
        """Execute tasks using hybrid strategy."""
        # Separate agent tasks from other tasks
        agent_tasks = [
            task for task in ready_tasks if task.task_type == TaskType.AGENT_TASK
        ]
        other_tasks = [
            task for task in ready_tasks if task.task_type != TaskType.AGENT_TASK
        ]

        # Execute other tasks sequentially (usually fast)
        for task in other_tasks:
            if execution.execution_id in self._paused_workflows:
                break
            await self._execute_task(execution, task)

        # Execute agent tasks in parallel (usually slow)
        if agent_tasks and execution.execution_id not in self._paused_workflows:
            await self._execute_parallel_tasks(execution, agent_tasks)

    async def _execute_task(self, execution: WorkflowExecution, task: WorkflowTask):
        """Execute a single task."""
        task_exec = execution.task_executions[task.task_id]
        task_key = f"{execution.execution_id}:{task.task_id}"

        try:
            # Update task status
            task_exec.status = TaskStatus.RUNNING
            task_exec.started_at = datetime.now()
            self._running_tasks.add(task_key)

            # Emit event
            await self._emit_event("task_started", execution, task)

            # Execute based on task type
            if task.task_type == TaskType.AGENT_TASK:
                await self._execute_agent_task(execution, task)
            elif task.task_type == TaskType.CONDITION_TASK:
                await self._execute_condition_task(execution, task)
            elif task.task_type == TaskType.DATA_TASK:
                await self._execute_data_task(execution, task)
            elif task.task_type == TaskType.CUSTOM_TASK:
                await self._execute_custom_task(execution, task)
            else:
                raise OrchestrationError(f"Unsupported task type: {task.task_type}")

            # Update task status
            task_exec.status = TaskStatus.COMPLETED
            task_exec.completed_at = datetime.now()
            task_exec.execution_time = (
                task_exec.completed_at - task_exec.started_at
            ).total_seconds()

            # Emit event
            await self._emit_event("task_completed", execution, task)

        except Exception as e:
            logger.error(f"Task execution failed: {e}")

            # Handle task failure
            await self._handle_task_failure(execution, task, str(e))

        finally:
            # Clean up
            self._running_tasks.discard(task_key)

    async def _execute_agent_task(
        self, execution: WorkflowExecution, task: WorkflowTask
    ):
        """Execute agent task."""
        if not task.agent_name:
            raise OrchestrationError("Agent task requires agent name")

        # Prepare input data
        input_data = task.input_data.copy()

        # Add data from dependent tasks
        for dep_id in task.dependencies:
            dep_exec = execution.task_executions[dep_id]
            if dep_exec.output_data:
                input_data[f"dep_{dep_id}"] = dep_exec.output_data

        # Create dispatch request
        dispatch_request = DispatchRequest(
            request_type=input_data.get("request_type", "general"),
            request_data=input_data,
            workspace_id=execution.workspace_id,
            user_id=execution.user_id,
            priority=task.priority,
            strategy="capability_match",
        )

        # Dispatch to agent
        dispatch_result = await self.dispatcher.dispatch(dispatch_request)

        # Store result
        task_exec = execution.task_executions[task.task_id]
        task_exec.agent_result = dispatch_result

        # Store output data
        task_exec.output_data = {
            "execution_id": dispatch_result.execution_id,
            "agent_name": dispatch_result.agent_name,
            "confidence_score": dispatch_result.confidence_score,
            "metadata": dispatch_result.routing_metadata,
        }

    async def _execute_condition_task(
        self, execution: WorkflowExecution, task: WorkflowTask
    ):
        """Execute condition task."""
        # Evaluate conditions
        conditions_met = True

        for condition in task.conditions:
            if not await self._evaluate_condition(execution, condition):
                conditions_met = False
                break

        # Store result
        task_exec = execution.task_executions[task.task_id]
        task_exec.output_data = {"conditions_met": conditions_met}

        # Skip dependent tasks if conditions not met
        if not conditions_met:
            await self._skip_dependent_tasks(execution, task.task_id)

    async def _execute_data_task(
        self, execution: WorkflowExecution, task: WorkflowTask
    ):
        """Execute data transformation task."""
        # Simple data transformation (in production, would use more sophisticated logic)
        input_data = task.input_data.copy()

        # Add data from dependent tasks
        for dep_id in task.dependencies:
            dep_exec = execution.task_executions[dep_id]
            if dep_exec.output_data:
                input_data[f"dep_{dep_id}"] = dep_exec.output_data

        # Apply transformation (placeholder)
        transformed_data = {
            "original_data": input_data,
            "transformed_at": datetime.now().isoformat(),
            "task_id": task.task_id,
        }

        # Store result
        task_exec = execution.task_executions[task.task_id]
        task_exec.output_data = transformed_data

    async def _execute_custom_task(
        self, execution: WorkflowExecution, task: WorkflowTask
    ):
        """Execute custom task."""
        # In production, would call custom task handlers
        # For now, simulate task execution
        await asyncio.sleep(0.1)

        # Store result
        task_exec = execution.task_executions[task.task_id]
        task_exec.output_data = {
            "custom_task_completed": True,
            "task_id": task.task_id,
            "executed_at": datetime.now().isoformat(),
        }

    async def _evaluate_condition(
        self, execution: WorkflowExecution, condition: Dict[str, Any]
    ) -> bool:
        """Evaluate task condition."""
        # Simple condition evaluation (in production, would use more sophisticated logic)
        condition_type = condition.get("type", "always_true")

        if condition_type == "always_true":
            return True
        elif condition_type == "always_false":
            return False
        elif condition_type == "task_success":
            task_id = condition.get("task_id")
            if task_id:
                task_exec = execution.task_executions[task_id]
                return task_exec.status == TaskStatus.COMPLETED
        elif condition_type == "data_exists":
            data_key = condition.get("data_key")
            return data_key in execution.results

        return True

    async def _skip_dependent_tasks(self, execution: WorkflowExecution, task_id: str):
        """Skip tasks that depend on a failed condition."""
        workflow = self._workflows[execution.workflow_id]

        for task in workflow.tasks:
            if task_id in task.dependencies:
                task_exec = execution.task_executions[task.task_id]
                task_exec.status = TaskStatus.SKIPPED
                await self._skip_dependent_tasks(
                    execution, task.task_id
                )  # Recursive skip

    async def _handle_task_failure(
        self, execution: WorkflowExecution, task: WorkflowTask, error_message: str
    ):
        """Handle task failure."""
        task_exec = execution.task_executions[task.task_id]
        task_exec.error_message = error_message

        # Check retry configuration
        retry_config = task.retry_config or {}
        max_retries = retry_config.get("max_retries", self.policy.max_retries)

        if task_exec.retry_count < max_retries:
            # Retry task
            task_exec.retry_count += 1
            task_exec.status = TaskStatus.READY

            # Add delay before retry
            backoff_seconds = retry_config.get(
                "backoff_seconds", self.policy.retry_backoff_seconds
            )
            await asyncio.sleep(backoff_seconds)

            logger.info(
                f"Retrying task {task.task_id} (attempt {task_exec.retry_count})"
            )
        else:
            # Mark task as failed
            task_exec.status = TaskStatus.FAILED

            # Handle based on error handling strategy
            workflow = self._workflows[execution.workflow_id]
            if workflow.error_handling == "fail_fast":
                await self._fail_workflow_execution(
                    execution, f"Task {task.task_id} failed: {error_message}"
                )
            elif workflow.error_handling == "continue":
                # Skip dependent tasks
                await self._skip_dependent_tasks(execution, task.task_id)

        # Emit event
        await self._emit_event("task_failed", execution, task)

    async def _complete_workflow_execution(self, execution: WorkflowExecution):
        """Complete workflow execution."""
        execution.status = WorkflowStatus.COMPLETED
        execution.completed_at = datetime.now()

        # Remove from running workflows
        self._running_workflows.discard(execution.execution_id)

        # Collect final results
        workflow = self._workflows[execution.workflow_id]
        for task in workflow.tasks:
            task_exec = execution.task_executions[task.task_id]
            if task_exec.output_data:
                execution.results[task.task_id] = task_exec.output_data

        # Emit event
        await self._emit_event("workflow_completed", execution)

        # Record metrics
        await self.metrics.record_workflow_completion(execution)

        logger.info(f"Completed workflow execution: {execution.execution_id}")

    async def _fail_workflow_execution(
        self, execution: WorkflowExecution, error_message: str
    ):
        """Fail workflow execution."""
        execution.status = WorkflowStatus.FAILED
        execution.completed_at = datetime.now()
        execution.errors.append(error_message)

        # Remove from running workflows
        self._running_workflows.discard(execution.execution_id)

        # Emit event
        await self._emit_event("workflow_failed", execution)

        # Record metrics
        await self.metrics.record_workflow_failure(execution)

        logger.error(
            f"Failed workflow execution: {execution.execution_id} - {error_message}"
        )

    async def pause_workflow(self, execution_id: str):
        """Pause workflow execution."""
        if execution_id in self._running_workflows:
            self._paused_workflows.add(execution_id)
            execution = self._executions[execution_id]
            execution.status = WorkflowStatus.PAUSED
            await self._emit_event("workflow_paused", execution)

    async def resume_workflow(self, execution_id: str):
        """Resume workflow execution."""
        if execution_id in self._paused_workflows:
            self._paused_workflows.remove(execution_id)
            execution = self._executions[execution_id]
            execution.status = WorkflowStatus.RUNNING
            await self._emit_event("workflow_resumed", execution)

    async def cancel_workflow(self, execution_id: str):
        """Cancel workflow execution."""
        if (
            execution_id in self._running_workflows
            or execution_id in self._paused_workflows
        ):
            execution = self._executions[execution_id]
            execution.status = WorkflowStatus.CANCELLED
            execution.completed_at = datetime.now()

            # Remove from tracking sets
            self._running_workflows.discard(execution_id)
            self._paused_workflows.discard(execution_id)

            # Cancel running tasks
            tasks_to_cancel = [
                task_key
                for task_key in self._running_tasks
                if task_key.startswith(execution_id)
            ]
            for task_key in tasks_to_cancel:
                self._running_tasks.discard(task_key)

            await self._emit_event("workflow_cancelled", execution)

    def _validate_workflow(self, workflow: WorkflowDefinition):
        """Validate workflow definition."""
        if not workflow.workflow_id:
            raise ValidationError("Workflow ID is required")

        if not workflow.workflow_name:
            raise ValidationError("Workflow name is required")

        if not workflow.tasks:
            raise ValidationError("Workflow must have at least one task")

        # Validate task dependencies
        task_ids = {task.task_id for task in workflow.tasks}
        for task in workflow.tasks:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    raise ValidationError(
                        f"Task {task.task_id} depends on non-existent task {dep_id}"
                    )

        # Check for circular dependencies
        if self._has_circular_dependencies(workflow):
            raise ValidationError("Workflow has circular dependencies")

    def _build_dependency_graph(self, workflow: WorkflowDefinition):
        """Build dependency graph for workflow."""
        # Clear existing dependencies
        self._task_dependencies.clear()
        self._task_dependents.clear()

        # Build new dependency graph
        for task in workflow.tasks:
            for dep_id in task.dependencies:
                self._task_dependencies[task.task_id].add(dep_id)
                self._task_dependents[dep_id].add(task.task_id)

    def _has_circular_dependencies(self, workflow: WorkflowDefinition) -> bool:
        """Check for circular dependencies using DFS."""
        visited = set()
        rec_stack = set()

        def has_cycle(task_id: str) -> bool:
            visited.add(task_id)
            rec_stack.add(task_id)

            for dep_id in self._task_dependencies[task_id]:
                if dep_id not in visited:
                    if has_cycle(dep_id):
                        return True
                elif dep_id in rec_stack:
                    return True

            rec_stack.remove(task_id)
            return False

        for task in workflow.tasks:
            if task.task_id not in visited:
                if has_cycle(task.task_id):
                    return True

        return False

    async def _emit_event(
        self,
        event_type: str,
        execution: WorkflowExecution,
        task: Optional[WorkflowTask] = None,
    ):
        """Emit orchestration event."""
        event_data = {
            "event_type": event_type,
            "execution_id": execution.execution_id,
            "workflow_id": execution.workflow_id,
            "timestamp": datetime.now().isoformat(),
        }

        if task:
            event_data["task_id"] = task.task_id
            event_data["task_type"] = task.task_type.value

        # Call event handlers
        for handler in self._event_handlers[event_type]:
            try:
                await handler(event_data)
            except Exception as e:
                logger.error(f"Event handler failed: {e}")

    def add_event_handler(self, event_type: str, handler: Callable):
        """Add event handler."""
        self._event_handlers[event_type].append(handler)

    def _start_cleanup_task(self):
        """Start background cleanup task."""

        async def cleanup():
            while True:
                try:
                    await asyncio.sleep(self.policy.cleanup_interval_hours * 3600)
                    await self._cleanup_old_executions()
                except Exception as e:
                    logger.error(f"Cleanup task failed: {e}")

        task = asyncio.create_task(cleanup())
        self._background_tasks.add(task)

    async def _cleanup_old_executions(self):
        """Clean up old workflow executions."""
        cutoff_time = datetime.now() - timedelta(days=7)

        executions_to_remove = []
        for execution_id, execution in self._executions.items():
            if execution.completed_at and execution.completed_at < cutoff_time:
                executions_to_remove.append(execution_id)

        for execution_id in executions_to_remove:
            del self._executions[execution_id]
            logger.info(f"Cleaned up old execution: {execution_id}")

    async def get_workflow_status(
        self, execution_id: str
    ) -> Optional[WorkflowExecution]:
        """Get workflow execution status."""
        return self._executions.get(execution_id)

    async def list_workflows(self) -> List[WorkflowDefinition]:
        """List all registered workflows."""
        return list(self._workflows.values())

    async def list_executions(
        self, workspace_id: Optional[str] = None
    ) -> List[WorkflowExecution]:
        """List workflow executions."""
        executions = list(self._executions.values())

        if workspace_id:
            executions = [
                exec for exec in executions if exec.workspace_id == workspace_id
            ]

        return executions

    async def get_orchestration_stats(self) -> Dict[str, Any]:
        """Get orchestration statistics."""
        return {
            "registered_workflows": len(self._workflows),
            "total_executions": len(self._executions),
            "running_workflows": len(self._running_workflows),
            "paused_workflows": len(self._paused_workflows),
            "running_tasks": len(self._running_tasks),
            "queued_executions": len(self._execution_queue),
            "background_tasks": len(self._background_tasks),
            "event_handlers": {
                event: len(handlers) for event, handlers in self._event_handlers.items()
            },
        }
