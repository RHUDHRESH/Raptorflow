"""
Raptorflow Base Classes and Utilities
====================================

Core base classes and utilities for the Raptorflow AI agent system.
Provides foundation for agents, workflows, tools, and other components.

Features:
- Base agent class with common functionality
- Base workflow class with state management
- Base tool class with validation and error handling
- Common utilities and helpers
- Exception classes and error handling
- Performance monitoring and metrics
- Logging and debugging utilities
"""

import asyncio
import json
import time
import traceback
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union

import structlog

# External imports
from pydantic import BaseModel, ValidationError

# Local imports
from config import settings
from llm import LLMManager, LLMRequest, LLMResponse
from state import StateManager, StateStatus, StateType

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class ComponentStatus(str, Enum):
    """Component status values."""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    STOPPED = "stopped"
    ARCHIVED = "archived"


class ComponentType(str, Enum):
    """Component types."""

    AGENT = "agent"
    WORKFLOW = "workflow"
    TOOL = "tool"
    SERVICE = "service"
    MONITOR = "monitor"
    HANDLER = "handler"


class ExecutionStatus(str, Enum):
    """Execution status values."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class Priority(str, Enum):
    """Priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


@dataclass
class ComponentConfig:
    """Base component configuration."""

    id: str
    name: str
    type: ComponentType
    description: str = ""
    version: str = "1.0.0"
    enabled: bool = True
    priority: Priority = Priority.MEDIUM
    timeout: int = 300  # 5 minutes
    retry_attempts: int = 3
    retry_delay: float = 1.0
    max_concurrent: int = 1
    workspace: Optional[str] = None
    owner: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionContext:
    """Execution context for components."""

    id: str
    component_id: str
    workspace: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    timeout: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "id": self.id,
            "component_id": self.component_id,
            "workspace": self.workspace,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "start_time": self.start_time.isoformat(),
            "timeout": self.timeout,
            "metadata": self.metadata,
        }


@dataclass
class ExecutionResult:
    """Execution result for components."""

    id: str
    context_id: str
    component_id: str
    status: ExecutionStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_traceback: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "id": self.id,
            "context_id": self.context_id,
            "component_id": self.component_id,
            "status": self.status.value,
            "data": self.data,
            "error": self.error,
            "error_traceback": self.error_traceback,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "metadata": self.metadata,
        }


class RaptorflowException(Exception):
    """Base exception for Raptorflow components."""

    def __init__(
        self,
        message: str,
        component_id: str = None,
        error_code: str = None,
        context: Dict[str, Any] = None,
    ):
        super().__init__(message)
        self.component_id = component_id
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = datetime.now()


class ComponentError(RaptorflowException):
    """Exception for component-related errors."""

    pass


class ExecutionError(RaptorflowException):
    """Exception for execution-related errors."""

    pass


class ValidationError(RaptorflowException):
    """Exception for validation errors."""

    pass


class TimeoutError(RaptorflowException):
    """Exception for timeout errors."""

    pass


class RateLimitError(RaptorflowException):
    """Exception for rate limiting errors."""

    pass


class PerformanceMonitor:
    """Performance monitoring utility."""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.counters: Dict[str, int] = {}
        self.timers: Dict[str, float] = {}

    def record_metric(self, name: str, value: float):
        """Record a metric value."""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)

        # Keep only last 1000 values
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]

    def increment_counter(self, name: str, value: int = 1):
        """Increment a counter."""
        self.counters[name] = self.counters.get(name, 0) + value

    def start_timer(self, name: str):
        """Start a timer."""
        self.timers[name] = time.time()

    def end_timer(self, name: str) -> float:
        """End a timer and return duration."""
        if name in self.timers:
            duration = time.time() - self.timers[name]
            self.record_metric(f"{name}_duration", duration)
            del self.timers[name]
            return duration
        return 0.0

    def get_stats(self, name: str) -> Dict[str, float]:
        """Get statistics for a metric."""
        if name not in self.metrics or not self.metrics[name]:
            return {}

        values = self.metrics[name]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "sum": sum(values),
        }

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics and counters."""
        return {
            "metrics": {name: self.get_stats(name) for name in self.metrics},
            "counters": self.counters.copy(),
            "active_timers": list(self.timers.keys()),
        }


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """Decorator for retrying failed operations."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        sleep_time = delay * (backoff**attempt)
                        logger.warning(
                            f"Operation failed, retrying in {sleep_time}s",
                            attempt=attempt + 1,
                            error=str(e),
                        )
                        await asyncio.sleep(sleep_time)
                    else:
                        logger.error(
                            "Operation failed after all retries",
                            attempts=max_retries,
                            error=str(e),
                        )

            raise last_exception

        return wrapper

    return decorator


def timeout_handler(timeout: int):
    """Decorator for handling timeouts."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except asyncio.TimeoutError:
                raise TimeoutError(f"Operation timed out after {timeout} seconds")

        return wrapper

    return decorator


def performance_monitor(monitor: PerformanceMonitor, operation_name: str):
    """Decorator for performance monitoring."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            monitor.increment_counter(f"{operation_name}_calls")
            monitor.start_timer(operation_name)

            try:
                result = await func(*args, **kwargs)
                monitor.increment_counter(f"{operation_name}_success")
                return result
            except Exception as e:
                monitor.increment_counter(f"{operation_name}_error")
                raise
            finally:
                monitor.end_timer(operation_name)

        return wrapper

    return decorator


class BaseComponent(ABC):
    """Base class for all Raptorflow components."""

    def __init__(self, config: ComponentConfig):
        self.config = config
        self.status = ComponentStatus.INITIALIZING
        self.state_manager = StateManager()
        self.llm_manager = LLMManager()
        self.performance_monitor = PerformanceMonitor()
        self._initialized = False
        self._lock = asyncio.Lock()

        # Component state
        self.execution_count = 0
        self.success_count = 0
        self.error_count = 0
        self.last_execution = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    async def initialize(self):
        """Initialize the component."""
        async with self._lock:
            if self._initialized:
                return

            try:
                await self._on_initialize()
                self.status = ComponentStatus.ACTIVE
                self._initialized = True
                self.updated_at = datetime.now()

                # Save initial state
                await self._save_state()

                logger.info(
                    "Component initialized",
                    component_id=self.config.id,
                    component_type=self.config.type.value,
                )

            except Exception as e:
                self.status = ComponentStatus.ERROR
                logger.error(
                    "Component initialization failed",
                    component_id=self.config.id,
                    error=str(e),
                )
                raise ComponentError(
                    f"Initialization failed: {e}", component_id=self.config.id
                )

    async def execute(self, context: ExecutionContext, **kwargs) -> ExecutionResult:
        """Execute the component with given context."""
        if not self._initialized:
            await self.initialize()

        async with self._lock:
            self.execution_count += 1
            self.last_execution = datetime.now()

            # Create execution result
            result = ExecutionResult(
                id=str(uuid.uuid4()),
                context_id=context.id,
                component_id=self.config.id,
                status=ExecutionStatus.RUNNING,
                start_time=datetime.now(),
            )

            try:
                # Set status to busy
                self.status = ComponentStatus.BUSY
                await self._save_state()

                # Execute with timeout
                timeout = context.timeout or self.config.timeout
                if timeout:
                    result.data = await asyncio.wait_for(
                        self._execute_with_monitoring(context, **kwargs),
                        timeout=timeout,
                    )
                else:
                    result.data = await self._execute_with_monitoring(context, **kwargs)

                # Mark as successful
                result.status = ExecutionStatus.COMPLETED
                self.success_count += 1

                logger.info(
                    "Component execution successful",
                    component_id=self.config.id,
                    execution_id=result.id,
                )

            except asyncio.TimeoutError:
                result.status = ExecutionStatus.TIMEOUT
                result.error = f"Execution timed out after {timeout} seconds"
                self.error_count += 1

                logger.error(
                    "Component execution timed out",
                    component_id=self.config.id,
                    execution_id=result.id,
                    timeout=timeout,
                )

            except Exception as e:
                result.status = ExecutionStatus.FAILED
                result.error = str(e)
                result.error_traceback = traceback.format_exc()
                self.error_count += 1

                logger.error(
                    "Component execution failed",
                    component_id=self.config.id,
                    execution_id=result.id,
                    error=str(e),
                )

            finally:
                # Finalize result
                result.end_time = datetime.now()
                result.duration = (result.end_time - result.start_time).total_seconds()

                # Update component status
                if self.status == ComponentStatus.BUSY:
                    self.status = ComponentStatus.ACTIVE

                self.updated_at = datetime.now()
                await self._save_state()

                # Save execution result
                await self._save_execution_result(result)

                return result

    @performance_monitor(performance_monitor, "component_execution")
    async def _execute_with_monitoring(
        self, context: ExecutionContext, **kwargs
    ) -> Dict[str, Any]:
        """Execute component with performance monitoring."""
        return await self._execute(context, **kwargs)

    @abstractmethod
    async def _execute(self, context: ExecutionContext, **kwargs) -> Dict[str, Any]:
        """Abstract method for component execution."""
        pass

    @abstractmethod
    async def _on_initialize(self):
        """Abstract method for component initialization."""
        pass

    async def _save_state(self):
        """Save component state to state manager."""
        try:
            state_data = {
                "config": self.config.__dict__,
                "status": self.status.value,
                "execution_count": self.execution_count,
                "success_count": self.success_count,
                "error_count": self.error_count,
                "last_execution": (
                    self.last_execution.isoformat() if self.last_execution else None
                ),
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
                "performance_metrics": self.performance_monitor.get_all_metrics(),
            }

            await self.state_manager.set_state(
                (
                    StateType.AGENT
                    if self.config.type == ComponentType.AGENT
                    else StateType.SYSTEM
                ),
                self.config.id,
                state_data,
            )

        except Exception as e:
            logger.error(
                "Failed to save component state",
                component_id=self.config.id,
                error=str(e),
            )

    async def _save_execution_result(self, result: ExecutionResult):
        """Save execution result to state manager."""
        try:
            await self.state_manager.set_state(
                StateType.SYSTEM,
                f"execution_{result.id}",
                result.to_dict(),
                ttl=86400,  # 24 hours
            )

        except Exception as e:
            logger.error(
                "Failed to save execution result", execution_id=result.id, error=str(e)
            )

    async def get_state(self) -> Optional[Dict[str, Any]]:
        """Get component state from state manager."""
        try:
            state_type = (
                StateType.AGENT
                if self.config.type == ComponentType.AGENT
                else StateType.SYSTEM
            )
            return await self.state_manager.get_state(state_type, self.config.id)
        except Exception as e:
            logger.error(
                "Failed to get component state",
                component_id=self.config.id,
                error=str(e),
            )
            return None

    async def get_execution_history(self, limit: int = 10) -> List[ExecutionResult]:
        """Get execution history."""
        try:
            # Get execution results from state manager
            pattern = f"execution_*"
            state_type = StateType.SYSTEM
            execution_ids = await self.state_manager.list_states(state_type, pattern)

            results = []
            for execution_id in execution_ids[:limit]:
                state_data = await self.state_manager.get_state(
                    state_type, execution_id
                )
                if state_data and state_data.get("component_id") == self.config.id:
                    # Reconstruct ExecutionResult
                    result = ExecutionResult(
                        id=state_data["id"],
                        context_id=state_data["context_id"],
                        component_id=state_data["component_id"],
                        status=ExecutionStatus(state_data["status"]),
                        data=state_data.get("data"),
                        error=state_data.get("error"),
                        start_time=datetime.fromisoformat(state_data["start_time"]),
                        end_time=(
                            datetime.fromisoformat(state_data["end_time"])
                            if state_data.get("end_time")
                            else None
                        ),
                        duration=state_data["duration"],
                        tokens_used=state_data.get("tokens_used", 0),
                        cost=state_data.get("cost", 0.0),
                        metadata=state_data.get("metadata", {}),
                    )
                    results.append(result)

            return sorted(results, key=lambda x: x.start_time, reverse=True)

        except Exception as e:
            logger.error(
                "Failed to get execution history",
                component_id=self.config.id,
                error=str(e),
            )
            return []

    def get_metrics(self) -> Dict[str, Any]:
        """Get component metrics."""
        return {
            "component_id": self.config.id,
            "component_type": self.config.type.value,
            "status": self.status.value,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_count / max(self.execution_count, 1),
            "last_execution": (
                self.last_execution.isoformat() if self.last_execution else None
            ),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "performance_metrics": self.performance_monitor.get_all_metrics(),
        }

    async def stop(self):
        """Stop the component."""
        async with self._lock:
            self.status = ComponentStatus.STOPPED
            self.updated_at = datetime.now()
            await self._save_state()

            logger.info("Component stopped", component_id=self.config.id)

    async def cleanup(self):
        """Cleanup component resources."""
        await self.stop()

        if hasattr(self.state_manager, "close"):
            await self.state_manager.close()


class BaseAgent(BaseComponent):
    """Base class for AI agents."""

    def __init__(self, config: ComponentConfig):
        super().__init__(config)
        self.config.type = ComponentType.AGENT
        self.memory = []
        self.tools = []
        self.capabilities = []

    async def add_memory(self, content: str, role: str = "user"):
        """Add memory entry."""
        self.memory.append(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Keep only last 100 memories
        if len(self.memory) > 100:
            self.memory = self.memory[-100:]

    async def get_memory(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent memory entries."""
        return self.memory[-limit:]

    async def clear_memory(self):
        """Clear agent memory."""
        self.memory.clear()

    def add_tool(self, tool):
        """Add a tool to the agent."""
        self.tools.append(tool)

    def add_capability(self, capability: str):
        """Add a capability to the agent."""
        self.capabilities.append(capability)

    async def _execute(self, context: ExecutionContext, **kwargs) -> Dict[str, Any]:
        """Execute agent with LLM integration."""
        # Build LLM request from memory and context
        messages = []

        # Add system message
        if self.config.description:
            messages.append(
                {
                    "role": "system",
                    "content": self.config.description,
                }
            )

        # Add memory
        for memory in await self.get_memory():
            messages.append(
                {
                    "role": memory["role"],
                    "content": memory["content"],
                }
            )

        # Add current input
        input_text = kwargs.get("input", "")
        if input_text:
            messages.append(
                {
                    "role": "user",
                    "content": input_text,
                }
            )

        # Create LLM request
        llm_request = LLMRequest(
            messages=[
                {"role": msg["role"], "content": msg["content"]} for msg in messages
            ],
            model="gpt-4",  # Default model
            temperature=0.7,
            max_tokens=2048,
        )

        # Generate response
        response = await self.llm_manager.generate(llm_request)

        # Add to memory
        await self.add_memory(response.content, "assistant")

        return {
            "response": response.content,
            "model": response.model,
            "tokens_used": response.usage.get("total_tokens", 0),
            "cost": response.cost,
            "metadata": response.metadata,
        }


class BaseWorkflow(BaseComponent):
    """Base class for workflows."""

    def __init__(self, config: ComponentConfig):
        super().__init__(config)
        self.config.type = ComponentType.WORKFLOW
        self.nodes = []
        self.edges = []
        self.current_node = None
        self.execution_path = []

    def add_node(self, node_id: str, node_type: str, config: Dict[str, Any]):
        """Add a node to the workflow."""
        self.nodes.append(
            {
                "id": node_id,
                "type": node_type,
                "config": config,
            }
        )

    def add_edge(self, from_node: str, to_node: str, condition: Optional[str] = None):
        """Add an edge to the workflow."""
        self.edges.append(
            {
                "from": from_node,
                "to": to_node,
                "condition": condition,
            }
        )

    async def _execute(self, context: ExecutionContext, **kwargs) -> Dict[str, Any]:
        """Execute workflow."""
        # Simple linear execution for now
        results = []

        for node in self.nodes:
            self.current_node = node["id"]
            self.execution_path.append(node["id"])

            # Execute node
            node_result = await self._execute_node(node, context, **kwargs)
            results.append(
                {
                    "node_id": node["id"],
                    "result": node_result,
                }
            )

        return {
            "workflow_id": self.config.id,
            "execution_path": self.execution_path,
            "results": results,
            "status": "completed",
        }

    async def _execute_node(
        self, node: Dict[str, Any], context: ExecutionContext, **kwargs
    ) -> Dict[str, Any]:
        """Execute a single node."""
        # This should be implemented by subclasses
        return {"status": "completed", "data": {}}


class BaseRouter:
    """Base class for routing components."""

    def __init__(self):
        self.routes = []

    def add_route(self, pattern: str, handler: callable, priority: int = 1):
        """Add a route to the router."""
        self.routes.append(
            {"pattern": pattern, "handler": handler, "priority": priority}
        )

    async def route(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route a request to the appropriate handler."""
        # Simple routing logic - can be extended
        for route in sorted(self.routes, key=lambda x: x["priority"], reverse=True):
            if self._matches_pattern(request_data, route["pattern"]):
                return await route["handler"](request_data)

        raise ValueError("No matching route found")

    def _matches_pattern(self, data: Dict[str, Any], pattern: str) -> bool:
        """Check if data matches the pattern."""
        # Simple pattern matching - can be extended
        return pattern in data.get("type", "").lower()


class BaseService(BaseComponent):
    """Base class for services."""

    def __init__(self, config: ComponentConfig):
        super().__init__(config)
        self.config.type = ComponentType.SERVICE
        self.endpoints = []

    def add_endpoint(self, path: str, method: str, handler: Callable):
        """Add an endpoint to the service."""
        self.endpoints.append(
            {
                "path": path,
                "method": method,
                "handler": handler,
            }
        )

    async def _execute(self, context: ExecutionContext, **kwargs) -> Dict[str, Any]:
        """Execute service operation."""
        # This should be implemented by subclasses
        return {"status": "completed", "data": {}}


# Export main components
__all__ = [
    "BaseComponent",
    "BaseAgent",
    "BaseWorkflow",
    "BaseService",
    "ComponentConfig",
    "ExecutionContext",
    "ExecutionResult",
    "ComponentStatus",
    "ComponentType",
    "ExecutionStatus",
    "Priority",
    "RaptorflowException",
    "ComponentError",
    "ExecutionError",
    "ValidationError",
    "TimeoutError",
    "RateLimitError",
    "PerformanceMonitor",
    "retry_on_failure",
    "timeout_handler",
    "performance_monitor",
]
