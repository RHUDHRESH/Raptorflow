"""
Plan Executor for Integration Components

Executes cognitive engine plans with proper error handling and monitoring.
Implements PROMPT 64 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .models import ExecutionPlan, PlanStep, RiskLevel


class ExecutionStatus(Enum):
    """Status of plan execution."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class StepStatus(Enum):
    """Status of individual step execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


@dataclass
class StepResult:
    """Result of executing a plan step."""

    step_id: str
    status: StepStatus
    output: Any
    error: Optional[str]
    execution_time_ms: int
    tokens_used: int
    cost_usd: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionResult:
    """Result of plan execution."""

    execution_id: str
    plan_id: str
    status: ExecutionStatus
    step_results: List[StepResult]
    completed_steps: List[str]
    failed_steps: List[str]
    skipped_steps: List[str]
    total_execution_time_ms: int
    total_tokens_used: int
    total_cost_usd: float
    final_output: Any
    error: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class PlanExecutor:
    """
    Executes cognitive engine plans with proper error handling and monitoring.

    Manages step dependencies, parallel execution, and failure recovery.
    """

    def __init__(self, agent_registry=None, monitoring_client=None):
        """
        Initialize the plan executor.

        Args:
            agent_registry: Registry of available agents
            monitoring_client: Client for execution monitoring
        """
        self.agent_registry = agent_registry
        self.monitoring_client = monitoring_client

        # Active executions
        self.active_executions: Dict[str, ExecutionResult] = {}

        # Execution configuration
        self.default_config = {
            "max_parallel_steps": 5,
            "step_timeout_seconds": 300,
            "max_retries": 3,
            "retry_delay_seconds": 5,
            "enable_parallel_execution": True,
            "enable_monitoring": True,
            "enable_caching": True,
        }

        # Step execution hooks
        self.step_hooks: Dict[str, List[Callable]] = {
            "before": [],
            "after": [],
            "error": [],
            "retry": [],
        }

    async def execute_plan(
        self,
        plan: ExecutionPlan,
        workspace_id: str,
        user_id: str,
        config: Dict[str, Any] = None,
    ) -> ExecutionResult:
        """
        Execute an execution plan.

        Args:
            plan: Execution plan to execute
            workspace_id: Workspace ID
            user_id: User ID
            config: Execution configuration overrides

        Returns:
            Execution result
        """
        # Merge configuration
        execution_config = {**self.default_config}
        if config:
            execution_config.update(config)

        # Create execution result
        execution_id = str(uuid.uuid4())
        result = ExecutionResult(
            execution_id=execution_id,
            plan_id=plan.metadata.get("plan_id", "unknown"),
            status=ExecutionStatus.PENDING,
            step_results=[],
            completed_steps=[],
            failed_steps=[],
            skipped_steps=[],
            total_execution_time_ms=0,
            total_tokens_used=0,
            total_cost_usd=0.0,
            final_output=None,
            error=None,
            metadata={
                "workspace_id": workspace_id,
                "user_id": user_id,
                "config": execution_config,
            },
        )

        self.active_executions[execution_id] = result

        try:
            # Start execution
            result.status = ExecutionStatus.RUNNING
            await self._monitor_execution_start(execution_id, plan)

            # Execute plan
            await self._execute_plan_steps(plan, result, execution_config)

            # Complete execution
            result.status = ExecutionStatus.COMPLETED
            result.completed_at = datetime.now()

            # Calculate final output
            result.final_output = await self._calculate_final_output(result)

            await self._monitor_execution_complete(execution_id, result)

        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.error = str(e)
            result.completed_at = datetime.now()

            await self._monitor_execution_error(execution_id, result, e)

        finally:
            # Clean up
            self.active_executions.pop(execution_id, None)

        return result

    async def _execute_plan_steps(
        self, plan: ExecutionPlan, result: ExecutionResult, config: Dict[str, Any]
    ) -> None:
        """Execute all steps in the plan."""
        # Build dependency graph
        step_graph = self._build_dependency_graph(plan.steps)

        # Execute steps in dependency order
        completed_steps = set()
        failed_steps = set()

        while len(completed_steps) + len(failed_steps) < len(plan.steps):
            # Find steps ready to execute
            ready_steps = self._get_ready_steps(
                plan.steps, completed_steps, failed_steps, step_graph
            )

            if not ready_steps:
                # Check if we're stuck (circular dependencies or all failed)
                if failed_steps:
                    remaining_steps = (
                        set(step.id for step in plan.steps)
                        - completed_steps
                        - failed_steps
                    )
                    if remaining_steps:
                        # Steps are blocked by failed dependencies
                        for step_id in remaining_steps:
                            result.skipped_steps.append(step_id)
                        break
                else:
                    # Circular dependency - shouldn't happen with valid plans
                    raise Exception("Circular dependency detected in plan steps")

            # Execute ready steps (parallel if enabled)
            if config.get("enable_parallel_execution", True):
                await self._execute_steps_parallel(
                    ready_steps, plan, result, completed_steps, failed_steps, config
                )
            else:
                await self._execute_steps_sequential(
                    ready_steps, plan, result, completed_steps, failed_steps, config
                )

    def _build_dependency_graph(self, steps: List[PlanStep]) -> Dict[str, List[str]]:
        """Build dependency graph from steps."""
        graph = {}

        for step in steps:
            graph[step.id] = step.dependencies.copy()

        return graph

    def _get_ready_steps(
        self,
        steps: List[PlanStep],
        completed_steps: Set[str],
        failed_steps: Set[str],
        step_graph: Dict[str, List[str]],
    ) -> List[PlanStep]:
        """Get steps that are ready to execute."""
        ready_steps = []

        for step in steps:
            if step.id in completed_steps or step.id in failed_steps:
                continue

            # Check if all dependencies are completed
            dependencies = step_graph.get(step.id, [])
            if all(dep in completed_steps for dep in dependencies):
                ready_steps.append(step)

        return ready_steps

    async def _execute_steps_parallel(
        self,
        steps: List[PlanStep],
        plan: ExecutionPlan,
        result: ExecutionResult,
        completed_steps: Set[str],
        failed_steps: Set[str],
        config: Dict[str, Any],
    ) -> None:
        """Execute steps in parallel."""
        # Limit parallel execution
        max_parallel = config.get("max_parallel_steps", 5)
        steps_chunks = [
            steps[i : i + max_parallel] for i in range(0, len(steps), max_parallel)
        ]

        for chunk in steps_chunks:
            # Execute chunk in parallel
            tasks = []
            for step in chunk:
                task = self._execute_single_step(step, plan, result, config)
                tasks.append(task)

            # Wait for all tasks to complete
            step_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for i, step_result in enumerate(step_results):
                step = chunk[i]

                if isinstance(step_result, Exception):
                    # Step failed with exception
                    await self._handle_step_failure(
                        step, step_result, result, failed_steps, config
                    )
                else:
                    # Step completed successfully
                    await self._handle_step_success(
                        step, step_result, result, completed_steps
                    )

    async def _execute_steps_sequential(
        self,
        steps: List[PlanStep],
        plan: ExecutionPlan,
        result: ExecutionResult,
        completed_steps: Set[str],
        failed_steps: Set[str],
        config: Dict[str, Any],
    ) -> None:
        """Execute steps sequentially."""
        for step in steps:
            try:
                step_result = await self._execute_single_step(
                    step, plan, result, config
                )
                await self._handle_step_success(
                    step, step_result, result, completed_steps
                )

            except Exception as e:
                await self._handle_step_failure(step, e, result, failed_steps, config)

    async def _execute_single_step(
        self,
        step: PlanStep,
        plan: ExecutionPlan,
        result: ExecutionResult,
        config: Dict[str, Any],
    ) -> StepResult:
        """Execute a single plan step."""
        step_start = time.time()

        try:
            # Run before hooks
            await self._run_step_hooks("before", step, result)

            # Get agent for this step
            agent = await self._get_agent(step.agent)
            if not agent:
                raise Exception(f"Agent {step.agent} not found")

            # Execute step with timeout
            timeout = config.get("step_timeout_seconds", 300)
            step_output = await asyncio.wait_for(
                agent.execute(step.inputs, step.tools), timeout=timeout
            )

            # Calculate metrics
            execution_time_ms = int((time.time() - step_start) * 1000)
            tokens_used = step.estimated_tokens  # TODO: Get actual from agent
            cost_usd = step.estimated_cost  # TODO: Get actual from agent

            # Create step result
            step_result = StepResult(
                step_id=step.id,
                status=StepStatus.COMPLETED,
                output=step_output,
                error=None,
                execution_time_ms=execution_time_ms,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                metadata={"agent": step.agent, "tools": step.tools},
            )

            # Run after hooks
            await self._run_step_hooks("after", step, result)

            return step_result

        except asyncio.TimeoutError:
            execution_time_ms = int((time.time() - step_start) * 1000)

            step_result = StepResult(
                step_id=step.id,
                status=StepStatus.FAILED,
                output=None,
                error="Step execution timeout",
                execution_time_ms=execution_time_ms,
                tokens_used=0,
                cost_usd=0.0,
                metadata={"timeout": True},
            )

            await self._run_step_hooks("error", step, result)

            return step_result

        except Exception as e:
            execution_time_ms = int((time.time() - step_start) * 1000)

            step_result = StepResult(
                step_id=step.id,
                status=StepStatus.FAILED,
                output=None,
                error=str(e),
                execution_time_ms=execution_time_ms,
                tokens_used=0,
                cost_usd=0.0,
                metadata={"exception": type(e).__name__},
            )

            await self._run_step_hooks("error", step, result)

            return step_result

    async def _handle_step_success(
        self,
        step: PlanStep,
        step_result: StepResult,
        result: ExecutionResult,
        completed_steps: Set[str],
    ) -> None:
        """Handle successful step execution."""
        result.step_results.append(step_result)
        result.completed_steps.append(step.id)
        completed_steps.add(step.id)

        # Update totals
        result.total_execution_time_ms += step_result.execution_time_ms
        result.total_tokens_used += step_result.tokens_used
        result.total_cost_usd += step_result.cost_usd

        # Store step output for dependent steps
        step.outputs = step_result.output

    async def _handle_step_failure(
        self,
        step: PlanStep,
        error: Exception,
        result: ExecutionResult,
        failed_steps: Set[str],
        config: Dict[str, Any],
    ) -> None:
        """Handle failed step execution."""
        max_retries = config.get("max_retries", 3)

        # Check if we should retry
        retry_count = step.metadata.get("retry_count", 0)
        if retry_count < max_retries:
            # Schedule retry
            step.metadata["retry_count"] = retry_count + 1
            step.metadata["last_error"] = str(error)

            # Run retry hooks
            await self._run_step_hooks("retry", step, result)

            # Add back to execution queue (handled by main loop)
            return

        # Max retries exceeded, mark as failed
        step_result = StepResult(
            step_id=step.id,
            status=StepStatus.FAILED,
            output=None,
            error=str(error),
            execution_time_ms=0,
            tokens_used=0,
            cost_usd=0.0,
            metadata={"retry_count": retry_count, "final_failure": True},
        )

        result.step_results.append(step_result)
        result.failed_steps.append(step.id)
        failed_steps.add(step.id)

    async def _get_agent(self, agent_name: str) -> Optional[Any]:
        """Get agent by name."""
        if not self.agent_registry:
            # Return mock agent for now
            return MockAgent(agent_name)

        return await self.agent_registry.get_agent(agent_name)

    async def _calculate_final_output(self, result: ExecutionResult) -> Any:
        """Calculate final output from step results."""
        # Get outputs from completed steps
        outputs = {}
        for step_result in result.step_results:
            if step_result.status == StepStatus.COMPLETED:
                outputs[step_result.step_id] = step_result.output

        # Return combined output
        return {
            "step_outputs": outputs,
            "execution_summary": {
                "total_steps": len(result.step_results),
                "completed_steps": len(result.completed_steps),
                "failed_steps": len(result.failed_steps),
                "total_time_ms": result.total_execution_time_ms,
                "total_cost_usd": result.total_cost_usd,
            },
        }

    async def _monitor_execution_start(
        self, execution_id: str, plan: ExecutionPlan
    ) -> None:
        """Monitor execution start."""
        if self.monitoring_client:
            await self.monitoring_client.track_execution_start(execution_id, plan)

    async def _monitor_execution_complete(
        self, execution_id: str, result: ExecutionResult
    ) -> None:
        """Monitor execution completion."""
        if self.monitoring_client:
            await self.monitoring_client.track_execution_complete(execution_id, result)

    async def _monitor_execution_error(
        self, execution_id: str, result: ExecutionResult, error: Exception
    ) -> None:
        """Monitor execution error."""
        if self.monitoring_client:
            await self.monitoring_client.track_execution_error(
                execution_id, result, error
            )

    async def _run_step_hooks(
        self, hook_type: str, step: PlanStep, result: ExecutionResult
    ) -> None:
        """Run step hooks."""
        hooks = self.step_hooks.get(hook_type, [])

        for hook in hooks:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(step, result)
                else:
                    hook(step, result)
            except Exception as e:
                # Log hook error but don't fail execution
                print(f"Step hook error: {e}")

    def add_step_hook(self, hook_type: str, hook: Callable) -> None:
        """Add a step execution hook."""
        if hook_type not in self.step_hooks:
            self.step_hooks[hook_type] = []
        self.step_hooks[hook_type].append(hook)

    def remove_step_hook(self, hook_type: str, hook: Callable) -> None:
        """Remove a step execution hook."""
        if hook_type in self.step_hooks:
            self.step_hooks[hook_type] = [
                h for h in self.step_hooks[hook_type] if h != hook
            ]

    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an active execution."""
        result = self.active_executions.get(execution_id)
        if not result:
            return None

        return {
            "execution_id": execution_id,
            "status": result.status.value,
            "completed_steps": len(result.completed_steps),
            "failed_steps": len(result.failed_steps),
            "total_steps": len(result.step_results),
            "execution_time_ms": result.total_execution_time_ms,
            "total_cost_usd": result.total_cost_usd,
        }

    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel an active execution."""
        result = self.active_executions.get(execution_id)
        if result and result.status == ExecutionStatus.RUNNING:
            result.status = ExecutionStatus.CANCELLED
            result.completed_at = datetime.now()
            return True
        return False

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        total_executions = len(self.active_executions)
        running_executions = sum(
            1
            for result in self.active_executions.values()
            if result.status == ExecutionStatus.RUNNING
        )

        return {
            "active_executions": total_executions,
            "running_executions": running_executions,
            "step_hooks_count": sum(len(hooks) for hooks in self.step_hooks.values()),
        }


class MockAgent:
    """Mock agent for testing."""

    def __init__(self, name: str):
        self.name = name

    async def execute(self, inputs: Dict[str, Any], tools: List[str]) -> Any:
        """Mock execution."""
        await asyncio.sleep(0.1)  # Simulate processing time
        return {
            "agent": self.name,
            "inputs": inputs,
            "tools": tools,
            "output": f"Mock output from {self.name}",
        }
