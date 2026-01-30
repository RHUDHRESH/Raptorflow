"""
AgentExecutor for Raptorflow agent system.
Handles agent execution, resource management, and performance optimization.
"""

import asyncio
import json
import logging
import traceback
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from backend.memory import AgentMemoryManager

from ..base import BaseAgent
from ..config import ModelTier
from ..exceptions import ExecutionError, ValidationError
from ..state import AgentState, AgentStateManager
from .metrics import AgentMetricsCollector
from .registry import AgentRegistry

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ExecutionMode(Enum):
    """Execution modes."""

    SYNC = "sync"
    ASYNC = "async"
    STREAMING = "streaming"
    BATCH = "batch"


@dataclass
class ExecutionContext:
    """Execution context for agent runs."""

    execution_id: str
    agent_id: str
    instance_id: str
    workspace_id: str
    user_id: str
    mode: ExecutionMode
    input_data: Dict[str, Any]
    config: Dict[str, Any]
    created_at: datetime
    timeout_seconds: int
    priority: str = "normal"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Execution result."""

    execution_id: str
    status: ExecutionStatus
    output_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    execution_time_ms: float
    tokens_used: int
    cost_estimate: float
    metrics: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)


@dataclass
class ResourceLimit:
    """Resource limits for execution."""

    max_memory_mb: int = 1024
    max_cpu_percent: float = 80.0
    max_execution_time_seconds: int = 300
    max_tokens_per_request: int = 10000
    max_cost_per_request: float = 1.0


@dataclass
class ExecutionConfig:
    """Executor configuration."""

    default_timeout_seconds: int = 300
    max_concurrent_executions: int = 50
    resource_limits: ResourceLimit = field(default_factory=ResourceLimit)
    enable_streaming: bool = True
    enable_caching: bool = True
    enable_retry: bool = True
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 5
    cleanup_interval_seconds: int = 60


class AgentExecutor:
    """Executes agents with resource management and performance optimization."""

    def __init__(
        self,
        registry: AgentRegistry,
        state_manager: AgentStateManager,
        memory_manager: AgentMemoryManager,
        metrics: AgentMetricsCollector,
        config: ExecutionConfig = None,
    ):
        self.registry = registry
        self.state_manager = state_manager
        self.memory_manager = memory_manager
        self.metrics = metrics
        self.config = config or ExecutionConfig()

        # Execution tracking
        self._executions: Dict[str, ExecutionContext] = {}
        self._results: Dict[str, ExecutionResult] = {}
        self._running_executions: Dict[str, asyncio.Task] = {}

        # Resource management
        self._resource_usage: Dict[str, Dict[str, Any]] = {}
        self._execution_queue: deque = deque()

        # Caching
        self._execution_cache: Dict[str, ExecutionResult] = {}
        self._cache_ttl_seconds = 3600  # 1 hour

        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)

        # Locks
        self._executor_lock = asyncio.Lock()

        # Background tasks
        self._background_tasks: Set[asyncio.Task] = set()
        self._running = False

        # Statistics
        self._stats = {
            "executions_started": 0,
            "executions_completed": 0,
            "executions_failed": 0,
            "executions_cancelled": 0,
            "executions_timed_out": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

        # Start background tasks
        self._start_background_tasks()

    async def execute(
        self,
        agent_id: str,
        input_data: Dict[str, Any],
        workspace_id: str,
        user_id: str,
        mode: ExecutionMode = ExecutionMode.SYNC,
        config: Dict[str, Any] = None,
        timeout_seconds: int = None,
        priority: str = "normal",
    ) -> Union[ExecutionResult, str]:
        """Execute an agent."""
        # Generate execution ID
        execution_id = str(uuid.uuid4())

        # Create execution context
        context = ExecutionContext(
            execution_id=execution_id,
            agent_id=agent_id,
            instance_id="",  # Will be set when creating instance
            workspace_id=workspace_id,
            user_id=user_id,
            mode=mode,
            input_data=input_data.copy(),
            config=config or {},
            created_at=datetime.now(),
            timeout_seconds=timeout_seconds or self.config.default_timeout_seconds,
            priority=priority,
        )

        # Store context
        self._executions[execution_id] = context

        # Check cache for sync executions
        if mode == ExecutionMode.SYNC and self.config.enable_caching:
            cache_key = self._generate_cache_key(agent_id, input_data, config)
            cached_result = self._execution_cache.get(cache_key)

            if cached_result:
                self._stats["cache_hits"] += 1
                await self._emit_event(
                    "cache_hit", {"execution_id": execution_id, "cache_key": cache_key}
                )
                return cached_result
            else:
                self._stats["cache_misses"] += 1

        # Execute based on mode
        if mode == ExecutionMode.SYNC:
            return await self._execute_sync(context)
        elif mode == ExecutionMode.ASYNC:
            task = asyncio.create_task(self._execute_async(context))
            self._running_executions[execution_id] = task
            return execution_id
        elif mode == ExecutionMode.STREAMING:
            return await self._execute_streaming(context)
        elif mode == ExecutionMode.BATCH:
            return await self._execute_batch(context)
        else:
            raise ValidationError(f"Unsupported execution mode: {mode}")

    async def get_execution_status(
        self, execution_id: str
    ) -> Optional[ExecutionResult]:
        """Get execution status."""
        return self._results.get(execution_id)

    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel an execution."""
        # Check if execution exists
        if execution_id not in self._executions:
            raise ExecutionError(f"Execution not found: {execution_id}")

        # Cancel running task
        if execution_id in self._running_executions:
            task = self._running_executions[execution_id]
            task.cancel()
            del self._running_executions[execution_id]

        # Update result
        if execution_id in self._results:
            result = self._results[execution_id]
            result.status = ExecutionStatus.CANCELLED
            result.completed_at = datetime.now()

        # Update statistics
        self._stats["executions_cancelled"] += 1

        # Emit event
        await self._emit_event("execution_cancelled", {"execution_id": execution_id})

        logger.info(f"Cancelled execution: {execution_id}")

        return True

    async def _execute_sync(self, context: ExecutionContext) -> ExecutionResult:
        """Execute agent synchronously."""
        try:
            # Update statistics
            self._stats["executions_started"] += 1

            # Create result
            result = ExecutionResult(
                execution_id=context.execution_id,
                status=ExecutionStatus.RUNNING,
                output_data=None,
                error_message=None,
                started_at=datetime.now(),
                completed_at=None,
                execution_time_ms=0.0,
                tokens_used=0,
                cost_estimate=0.0,
            )

            self._results[context.execution_id] = result

            # Execute with timeout
            try:
                async with asyncio.timeout(context.timeout_seconds):
                    output_data = await self._run_agent(context)

                    # Update result
                    result.status = ExecutionStatus.COMPLETED
                    result.output_data = output_data
                    result.completed_at = datetime.now()
                    result.execution_time_ms = (
                        result.completed_at - result.started_at
                    ).total_seconds() * 1000

                    # Cache result
                    if self.config.enable_caching:
                        cache_key = self._generate_cache_key(
                            context.agent_id, context.input_data, context.config
                        )
                        self._execution_cache[cache_key] = result

                    # Update statistics
                    self._stats["executions_completed"] += 1

                    # Emit event
                    await self._emit_event(
                        "execution_completed",
                        {
                            "execution_id": context.execution_id,
                            "agent_id": context.agent_id,
                            "execution_time_ms": result.execution_time_ms,
                        },
                    )

                    return result

            except asyncio.TimeoutError:
                result.status = ExecutionStatus.TIMEOUT
                result.error_message = "Execution timed out"
                result.completed_at = datetime.now()

                # Update statistics
                self._stats["executions_timed_out"] += 1

                # Emit event
                await self._emit_event(
                    "execution_timeout",
                    {
                        "execution_id": context.execution_id,
                        "timeout_seconds": context.timeout_seconds,
                    },
                )

                return result

        except Exception as e:
            # Create error result
            result = ExecutionResult(
                execution_id=context.execution_id,
                status=ExecutionStatus.FAILED,
                output_data=None,
                error_message=str(e),
                started_at=datetime.now(),
                completed_at=datetime.now(),
                execution_time_ms=0.0,
                tokens_used=0,
                cost_estimate=0.0,
            )

            self._results[context.execution_id] = result

            # Update statistics
            self._stats["executions_failed"] += 1

            # Emit event
            await self._emit_event(
                "execution_failed",
                {"execution_id": context.execution_id, "error": str(e)},
            )

            logger.error(f"Execution failed: {context.execution_id} - {e}")

            return result

    async def _execute_async(self, context: ExecutionContext):
        """Execute agent asynchronously."""
        try:
            await self._execute_sync(context)
        except Exception as e:
            logger.error(f"Async execution failed: {context.execution_id} - {e}")
        finally:
            # Clean up
            if context.execution_id in self._running_executions:
                del self._running_executions[context.execution_id]

    async def _execute_streaming(self, context: ExecutionContext) -> str:
        """Execute agent with streaming output."""
        # For now, return execution ID and handle streaming via separate mechanism
        # In production, would implement actual streaming
        task = asyncio.create_task(self._execute_async(context))
        self._running_executions[context.execution_id] = task

        return context.execution_id

    async def _execute_batch(self, context: ExecutionContext) -> List[ExecutionResult]:
        """Execute agent in batch mode."""
        # For now, treat as sync execution
        # In production, would handle batch processing
        result = await self._execute_sync(context)
        return [result]

    async def _run_agent(self, context: ExecutionContext) -> Dict[str, Any]:
        """Run the actual agent."""
        # Get agent info
        agent_info = await self.registry.get_agent_info(context.agent_id)

        if not agent_info:
            raise ExecutionError(f"Agent not found: {context.agent_id}")

        # Create instance
        instance_id = await self.registry.create_instance(
            context.agent_id, context.workspace_id, context.user_id, context.config
        )

        context.instance_id = instance_id

        try:
            # Instantiate agent
            agent_instance = agent_info.agent_class()

            # Prepare agent state
            agent_state = AgentState(
                {
                    "workspace_id": context.workspace_id,
                    "user_id": context.user_id,
                    "execution_id": context.execution_id,
                    "instance_id": instance_id,
                    "input_data": context.input_data,
                    "config": context.config,
                }
            )

            # Store execution state
            state_id = await self.state_manager.create_state(
                state_type=StateType.AGENT_STATE,
                owner_id=context.user_id,
                workspace_id=context.workspace_id,
                initial_data=agent_state,
                tags=["execution", context.agent_id],
            )

            # Execute agent
            try:
                result_state = await agent_instance.execute(agent_state)

                # Extract output data
                output_data = result_state.get("output", {})

                # Store result in memory
                await self.memory_manager.store_memory(
                    memory_type=MemoryType.EPISODIC,
                    agent_id=context.agent_id,
                    workspace_id=context.workspace_id,
                    content={
                        "execution_id": context.execution_id,
                        "input": context.input_data,
                        "output": output_data,
                        "agent_state": result_state,
                    },
                    tags=["execution_result", context.agent_id],
                )

                return output_data

            finally:
                # Clean up state
                await self.state_manager.delete_state(state_id, context.user_id)

        finally:
            # Clean up instance
            await self.registry.destroy_instance(instance_id)

    def _generate_cache_key(
        self, agent_id: str, input_data: Dict[str, Any], config: Dict[str, Any]
    ) -> str:
        """Generate cache key for execution."""
        # Create deterministic key from inputs
        cache_data = {"agent_id": agent_id, "input_data": input_data, "config": config}

        cache_str = json.dumps(cache_data, sort_keys=True, default=str)
        import hashlib

        return hashlib.sha256(cache_str.encode()).hexdigest()

    async def get_resource_usage(self, execution_id: str) -> Dict[str, Any]:
        """Get resource usage for execution."""
        return self._resource_usage.get(execution_id, {})

    async def list_executions(
        self,
        agent_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[ExecutionStatus] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List executions with optional filtering."""
        executions = []

        for execution_id, result in self._results.items():
            context = self._executions.get(execution_id)

            if not context:
                continue

            # Apply filters
            if agent_id and context.agent_id != agent_id:
                continue

            if workspace_id and context.workspace_id != workspace_id:
                continue

            if user_id and context.user_id != user_id:
                continue

            if status and result.status != status:
                continue

            # Convert to dict
            executions.append(
                {
                    "execution_id": execution_id,
                    "agent_id": context.agent_id,
                    "workspace_id": context.workspace_id,
                    "user_id": context.user_id,
                    "mode": context.mode.value,
                    "status": result.status.value,
                    "started_at": result.started_at.isoformat(),
                    "completed_at": (
                        result.completed_at.isoformat() if result.completed_at else None
                    ),
                    "execution_time_ms": result.execution_time_ms,
                    "tokens_used": result.tokens_used,
                    "cost_estimate": result.cost_estimate,
                    "error_message": result.error_message,
                }
            )

        # Sort by started_at (most recent first)
        executions.sort(key=lambda e: e["started_at"], reverse=True)

        return executions[:limit]

    async def clear_cache(self):
        """Clear execution cache."""
        self._execution_cache.clear()
        logger.info("Execution cache cleared")

    async def get_executor_statistics(self) -> Dict[str, Any]:
        """Get executor statistics."""
        # Count by status
        status_counts = defaultdict(int)
        for result in self._results.values():
            status_counts[result.status.value] += 1

        # Count by mode
        mode_counts = defaultdict(int)
        for context in self._executions.values():
            mode_counts[context.mode.value] += 1

        # Calculate average execution time
        completed_executions = [
            r for r in self._results.values() if r.status == ExecutionStatus.COMPLETED
        ]
        avg_execution_time = 0.0

        if completed_executions:
            total_time = sum(r.execution_time_ms for r in completed_executions)
            avg_execution_time = total_time / len(completed_executions)

        return {
            "total_executions": len(self._executions),
            "running_executions": len(self._running_executions),
            "execution_statuses": dict(status_counts),
            "execution_modes": dict(mode_counts),
            "cache_size": len(self._execution_cache),
            "average_execution_time_ms": avg_execution_time,
            "queue_size": len(self._execution_queue),
            "statistics": self._stats.copy(),
        }

    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit executor event."""
        event_data = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            **data,
        }

        # Call event handlers
        for handler in self._event_handlers[event_type]:
            try:
                await handler(event_data)
            except Exception as e:
                logger.error(f"Event handler failed: {e}")

    def add_event_handler(self, event_type: str, handler: Callable):
        """Add event handler."""
        self._event_handlers[event_type].append(handler)

    def _start_background_tasks(self):
        """Start background tasks."""
        self._running = True

        # Cleanup task
        self._background_tasks.add(asyncio.create_task(self._cleanup_loop()))

        # Cache cleanup task
        if self.config.enable_caching:
            self._background_tasks.add(asyncio.create_task(self._cache_cleanup_loop()))

    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            try:
                # Clean up old executions
                cutoff_time = datetime.now() - timedelta(hours=24)

                executions_to_remove = []
                for execution_id, result in self._results.items():
                    if result.completed_at and result.completed_at < cutoff_time:
                        executions_to_remove.append(execution_id)

                for execution_id in executions_to_remove:
                    if execution_id in self._executions:
                        del self._executions[execution_id]
                    if execution_id in self._results:
                        del self._results[execution_id]
                    if execution_id in self._resource_usage:
                        del self._resource_usage[execution_id]

                if executions_to_remove:
                    logger.info(
                        f"Cleaned up {len(executions_to_remove)} old executions"
                    )

                # Sleep for cleanup interval
                await asyncio.sleep(self.config.cleanup_interval_seconds)

            except Exception as e:
                logger.error(f"Cleanup loop failed: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute

    async def _cache_cleanup_loop(self):
        """Background cache cleanup loop."""
        while self._running:
            try:
                # Clean up expired cache entries
                # For simplicity, just clear cache periodically
                # In production, would implement TTL-based cleanup
                await asyncio.sleep(self._cache_ttl_seconds)

                # Clear cache
                old_size = len(self._execution_cache)
                await self.clear_cache()

                if old_size > 0:
                    logger.info(f"Cleaned up {old_size} cache entries")

            except Exception as e:
                logger.error(f"Cache cleanup loop failed: {e}")
                await asyncio.sleep(300)  # Retry after 5 minutes

    async def stop(self):
        """Stop executor."""
        self._running = False

        # Cancel running executions
        for execution_id, task in self._running_executions.items():
            task.cancel()

            # Update result
            if execution_id in self._results:
                result = self._results[execution_id]
                result.status = ExecutionStatus.CANCELLED
                result.completed_at = datetime.now()

        # Wait for tasks to complete
        await asyncio.gather(*self._background_tasks, return_exceptions=True)

        self._background_tasks.clear()
        self._running_executions.clear()

        logger.info("Agent executor stopped")
