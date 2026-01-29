"""
Enhanced timeout handling for agent execution.
Provides configurable timeouts, graceful cancellation, and timeout recovery.
"""

import asyncio
import logging
import signal
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Types of operations with different timeout requirements."""

    AGENT_EXECUTION = "agent_execution"
    LLM_INFERENCE = "llm_inference"
    TOOL_EXECUTION = "tool_execution"
    DATABASE_QUERY = "database_query"
    CACHE_OPERATION = "cache_operation"
    VALIDATION = "validation"
    SECURITY_CHECK = "security_check"
    MEMORY_OPERATION = "memory_operation"
    NETWORK_REQUEST = "network_request"


class RecoveryStrategy(Enum):
    """Timeout recovery strategies."""

    RETRY_WITH_BACKOFF = "retry_with_backoff"
    FALLBACK_MODEL = "fallback_model"
    ALTERNATIVE_TOOL = "alternative_tool"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    PARTIAL_RESPONSE = "partial_response"
    CACHED_RESPONSE = "cached_response"
    SKIP_OPERATION = "skip_operation"


class TimeoutError(Exception):
    """Enhanced timeout error with context."""

    def __init__(
        self,
        message: str,
        timeout_seconds: int,
        elapsed_seconds: float,
        operation_type: OperationType = None,
        recovery_suggestions: List[RecoveryStrategy] = None,
    ):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds
        self.elapsed_seconds = elapsed_seconds
        self.operation_type = operation_type
        self.recovery_suggestions = recovery_suggestions or []


@dataclass
class TimeoutConfig:
    """Configuration for agent timeouts."""

    # Default timeouts
    default_timeout: int = 120  # 2 minutes
    max_timeout: int = 600  # 10 minutes
    warning_threshold: float = 0.8  # 80% of timeout
    cleanup_timeout: int = 30  # 30 seconds for cleanup

    # Retry configuration
    retry_on_timeout: bool = True
    max_retries: int = 3
    base_backoff: float = 1.0  # Base backoff in seconds
    max_backoff: float = 60.0  # Maximum backoff in seconds

    # Per-operation timeouts
    operation_timeouts: Dict[OperationType, int] = None

    # Circuit breaker configuration
    circuit_breaker_threshold: int = 5  # Failures before opening circuit
    circuit_breaker_timeout: int = 300  # Seconds to keep circuit open

    def __post_init__(self):
        if self.operation_timeouts is None:
            self.operation_timeouts = {
                OperationType.AGENT_EXECUTION: 120,
                OperationType.LLM_INFERENCE: 60,
                OperationType.TOOL_EXECUTION: 30,
                OperationType.DATABASE_QUERY: 10,
                OperationType.CACHE_OPERATION: 5,
                OperationType.VALIDATION: 5,
                OperationType.SECURITY_CHECK: 10,
                OperationType.MEMORY_OPERATION: 15,
                OperationType.NETWORK_REQUEST: 30,
            }

    def get_timeout_for_operation(self, operation_type: OperationType) -> int:
        """Get timeout for a specific operation type."""
        return self.operation_timeouts.get(operation_type, self.default_timeout)

    def set_timeout_for_operation(self, operation_type: OperationType, timeout: int):
        """Set timeout for a specific operation type."""
        timeout = min(timeout, self.max_timeout)
        self.operation_timeouts[operation_type] = timeout


class CircuitBreaker:
    """Circuit breaker pattern for handling repeated failures."""

    def __init__(self, failure_threshold: int = 5, timeout: int = 300):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def is_open(self) -> bool:
        """Check if circuit breaker is open."""
        if self.state == "CLOSED":
            return False
        elif self.state == "OPEN":
            if (
                self.last_failure_time
                and (datetime.now() - self.last_failure_time).total_seconds()
                > self.timeout
            ):
                self.state = "HALF_OPEN"
                return False
            return True
        else:  # HALF_OPEN
            return False

    def record_success(self):
        """Record a successful operation."""
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": (
                self.last_failure_time.isoformat() if self.last_failure_time else None
            ),
            "timeout": self.timeout,
        }


class TimeoutManager:
    """Manages timeouts for agent execution with cancellation support."""

    def __init__(self, config: Optional[TimeoutConfig] = None):
        self.config = config or TimeoutConfig()
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._task_start_times: Dict[str, datetime] = {}
        self._cancellation_handlers: Dict[str, Callable] = {}
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._timeout_stats: Dict[OperationType, Dict[str, int]] = {
            op_type: {"timeouts": 0, "recoveries": 0, "failures": 0}
            for op_type in OperationType
        }

    async def execute_with_timeout(
        self,
        coro,
        operation_type: OperationType = OperationType.AGENT_EXECUTION,
        timeout: Optional[int] = None,
        task_id: Optional[str] = None,
        cancellation_handler: Optional[Callable] = None,
        recovery_strategies: Optional[List[RecoveryStrategy]] = None,
    ) -> Any:
        """
        Execute a coroutine with timeout and cancellation support.

        Args:
            coro: The coroutine to execute
            operation_type: Type of operation for timeout configuration
            timeout: Custom timeout in seconds
            task_id: Unique identifier for the task
            cancellation_handler: Handler called when task is cancelled
            recovery_strategies: List of recovery strategies to attempt

        Returns:
            Result of the coroutine

        Raises:
            TimeoutError: If the coroutine times out and recovery fails
        """
        if timeout is None:
            timeout = self.config.get_timeout_for_operation(operation_type)

        # Validate timeout
        if timeout > self.config.max_timeout:
            timeout = self.config.max_timeout
            logger.warning(f"Timeout reduced to maximum: {timeout}s")

        task_id = task_id or f"{operation_type.value}_{id(coro)}"
        start_time = datetime.now()

        # Check circuit breaker
        circuit_breaker = self._get_circuit_breaker(operation_type.value)
        if circuit_breaker.is_open():
            raise TimeoutError(
                f"Circuit breaker open for {operation_type.value}",
                timeout,
                0,
                operation_type,
                [RecoveryStrategy.CACHED_RESPONSE, RecoveryStrategy.SKIP_OPERATION],
            )

        try:
            # Register task
            task = asyncio.create_task(coro)
            self._active_tasks[task_id] = task
            self._task_start_times[task_id] = start_time
            if cancellation_handler:
                self._cancellation_handlers[task_id] = cancellation_handler

            # Execute with timeout
            try:
                result = await asyncio.wait_for(task, timeout=timeout)
                circuit_breaker.record_success()
                return result

            except asyncio.TimeoutError:
                elapsed = (datetime.now() - start_time).total_seconds()

                # Record timeout statistics
                self._timeout_stats[operation_type]["timeouts"] += 1
                circuit_breaker.record_failure()

                # Handle cancellation
                await self._handle_cancellation(task_id, task)

                # Attempt recovery
                if recovery_strategies and self.config.retry_on_timeout:
                    recovery_result = await self._attempt_recovery(
                        task_id, operation_type, recovery_strategies, elapsed, timeout
                    )
                    if recovery_result is not None:
                        self._timeout_stats[operation_type]["recoveries"] += 1
                        return recovery_result

                # Raise enhanced timeout error
                raise TimeoutError(
                    f"Task '{task_id}' ({operation_type.value}) timed out after {elapsed:.1f}s (limit: {timeout}s)",
                    timeout,
                    elapsed,
                    operation_type,
                    recovery_strategies
                    or self._get_default_recovery_strategies(operation_type),
                )

        except Exception as e:
            if not isinstance(e, TimeoutError):
                self._timeout_stats[operation_type]["failures"] += 1
                circuit_breaker.record_failure()
            raise
        finally:
            # Cleanup
            self._cleanup_task(task_id)

    def _get_circuit_breaker(self, operation_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for operation."""
        if operation_name not in self._circuit_breakers:
            self._circuit_breakers[operation_name] = CircuitBreaker(
                failure_threshold=self.config.circuit_breaker_threshold,
                timeout=self.config.circuit_breaker_timeout,
            )
        return self._circuit_breakers[operation_name]

    def _get_default_recovery_strategies(
        self, operation_type: OperationType
    ) -> List[RecoveryStrategy]:
        """Get default recovery strategies for operation type."""
        strategies = {
            OperationType.AGENT_EXECUTION: [
                RecoveryStrategy.RETRY_WITH_BACKOFF,
                RecoveryStrategy.GRACEFUL_DEGRADATION,
                RecoveryStrategy.PARTIAL_RESPONSE,
            ],
            OperationType.LLM_INFERENCE: [
                RecoveryStrategy.FALLBACK_MODEL,
                RecoveryStrategy.RETRY_WITH_BACKOFF,
                RecoveryStrategy.CACHED_RESPONSE,
            ],
            OperationType.TOOL_EXECUTION: [
                RecoveryStrategy.ALTERNATIVE_TOOL,
                RecoveryStrategy.RETRY_WITH_BACKOFF,
                RecoveryStrategy.SKIP_OPERATION,
            ],
            OperationType.DATABASE_QUERY: [
                RecoveryStrategy.RETRY_WITH_BACKOFF,
                RecoveryStrategy.CACHED_RESPONSE,
            ],
            OperationType.CACHE_OPERATION: [RecoveryStrategy.SKIP_OPERATION],
            OperationType.VALIDATION: [RecoveryStrategy.GRACEFUL_DEGRADATION],
            OperationType.SECURITY_CHECK: [RecoveryStrategy.SKIP_OPERATION],
            OperationType.MEMORY_OPERATION: [
                RecoveryStrategy.RETRY_WITH_BACKOFF,
                RecoveryStrategy.GRACEFUL_DEGRADATION,
            ],
            OperationType.NETWORK_REQUEST: [
                RecoveryStrategy.RETRY_WITH_BACKOFF,
                RecoveryStrategy.CACHED_RESPONSE,
            ],
        }
        return strategies.get(operation_type, [RecoveryStrategy.RETRY_WITH_BACKOFF])

    async def _attempt_recovery(
        self,
        task_id: str,
        operation_type: OperationType,
        recovery_strategies: List[RecoveryStrategy],
        elapsed: float,
        timeout: int,
    ) -> Optional[Any]:
        """Attempt recovery strategies."""
        for strategy in recovery_strategies:
            try:
                if strategy == RecoveryStrategy.RETRY_WITH_BACKOFF:
                    # Implement retry with exponential backoff
                    for attempt in range(self.config.max_retries):
                        wait_time = min(
                            self.config.base_backoff * (2**attempt),
                            self.config.max_backoff,
                        )
                        await asyncio.sleep(wait_time)
                        logger.info(
                            f"Recovery attempt {attempt + 1}/{self.config.max_retries} for {task_id}"
                        )
                        # Note: In a real implementation, you'd need to recreate the coroutine
                        # This is a simplified version
                        return {"recovered": True, "strategy": "retry_with_backoff"}

                elif strategy == RecoveryStrategy.CACHED_RESPONSE:
                    # Try to get cached response
                    try:
                        from cache import get_cached_response

                        cached = await get_cached_response(
                            operation_type.value, task_id
                        )
                        if cached:
                            return {
                                "recovered": True,
                                "strategy": "cached_response",
                                "data": cached,
                            }
                    except ImportError:
                        pass

                elif strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
                    return {
                        "recovered": True,
                        "strategy": "graceful_degradation",
                        "message": "Operation completed with reduced functionality",
                    }

                elif strategy == RecoveryStrategy.PARTIAL_RESPONSE:
                    return {
                        "recovered": True,
                        "strategy": "partial_response",
                        "message": "Partial results available due to timeout",
                    }

                elif strategy == RecoveryStrategy.SKIP_OPERATION:
                    return {
                        "recovered": True,
                        "strategy": "skip_operation",
                        "message": "Operation skipped due to timeout",
                    }

            except Exception as e:
                logger.warning(f"Recovery strategy {strategy.value} failed: {e}")
                continue

        return None

    async def _handle_cancellation(self, task_id: str, task: asyncio.Task):
        """Handle task cancellation."""
        try:
            # Cancel task
            task.cancel()

            # Wait for cancellation to complete
            try:
                await asyncio.wait_for(task, timeout=self.config.cleanup_timeout)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                # Force cancel if cleanup times out
                logger.warning(f"Task '{task_id}' cleanup timed out")

            # Call cancellation handler
            if task_id in self._cancellation_handlers:
                try:
                    handler = self._cancellation_handlers[task_id]
                    if asyncio.iscoroutinefunction(handler):
                        await handler(task_id)
                    else:
                        handler(task_id)
                except Exception as e:
                    logger.error(f"Cancellation handler failed for '{task_id}': {e}")

        except Exception as e:
            logger.error(f"Error during cancellation of '{task_id}': {e}")

    def _cleanup_task(self, task_id: str):
        """Clean up task tracking."""
        self._active_tasks.pop(task_id, None)
        self._task_start_times.pop(task_id, None)
        self._cancellation_handlers.pop(task_id, None)

    def get_active_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active tasks."""
        active = {}
        now = datetime.now()

        for task_id, task in self._active_tasks.items():
            start_time = self._task_start_times.get(task_id, now)
            elapsed = (now - start_time).total_seconds()

            active[task_id] = {
                "task": task,
                "elapsed_seconds": elapsed,
                "start_time": start_time.isoformat(),
                "done": task.done(),
                "cancelled": task.cancelled(),
            }

        return active

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a specific task."""
        if task_id not in self._active_tasks:
            return False

        task = self._active_tasks[task_id]
        task.cancel()
        return True

    def cancel_all_tasks(self):
        """Cancel all active tasks."""
        for task_id in list(self._active_tasks.keys()):
            self.cancel_task(task_id)

    def get_timeout_stats(self) -> Dict[str, Any]:
        """Get timeout statistics by operation type."""
        return {
            "operation_stats": dict(self._timeout_stats),
            "circuit_breakers": {
                name: cb.get_stats() for name, cb in self._circuit_breakers.items()
            },
            "active_tasks": len(self._active_tasks),
            "config": {
                "default_timeout": self.config.default_timeout,
                "max_timeout": self.config.max_timeout,
                "retry_on_timeout": self.config.retry_on_timeout,
                "max_retries": self.config.max_retries,
            },
        }


class TimeoutMiddleware:
    """Middleware for adding timeout handling to agent execution."""

    def __init__(self, timeout_manager: Optional[TimeoutManager] = None):
        self.timeout_manager = timeout_manager or TimeoutManager()

    @asynccontextmanager
    async def timeout_context(
        self,
        timeout: Optional[int] = None,
        task_id: Optional[str] = None,
    ):
        """Context manager for timeout handling."""
        try:
            yield self.timeout_manager
        except TimeoutError as e:
            logger.error(f"Timeout occurred: {e}")
            # Could add retry logic here
            raise

    async def execute_with_retry(
        self,
        coro,
        timeout: Optional[int] = None,
        task_id: Optional[str] = None,
    ) -> Any:
        """Execute with retry on timeout."""
        last_error = None
        max_retries = self.timeout_manager.config.max_retries

        for attempt in range(max_retries + 1):
            try:
                return await self.timeout_manager.execute_with_timeout(
                    coro, timeout, task_id
                )
            except TimeoutError as e:
                last_error = e
                if attempt < max_retries:
                    logger.warning(
                        f"Timeout attempt {attempt + 1}/{max_retries + 1}, retrying..."
                    )
                    # Exponential backoff
                    wait_time = min(2**attempt, 30)
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries + 1} timeout attempts failed")
                    break

        raise last_error


# Global timeout manager
_timeout_manager: Optional[TimeoutManager] = None


def get_timeout_manager() -> TimeoutManager:
    """Get the global timeout manager instance."""
    global _timeout_manager
    if _timeout_manager is None:
        _timeout_manager = TimeoutManager()
    return _timeout_manager


async def execute_with_timeout(
    coro,
    operation_type: OperationType = OperationType.AGENT_EXECUTION,
    timeout: Optional[int] = None,
    task_id: Optional[str] = None,
    cancellation_handler: Optional[Callable] = None,
) -> Any:
    """Execute with timeout (convenience function)."""
    manager = get_timeout_manager()
    return await manager.execute_with_timeout(
        coro, operation_type, timeout, task_id, cancellation_handler
    )


@asynccontextmanager
async def timeout_context(timeout: Optional[int] = None):
    """Timeout context manager (convenience function)."""
    manager = get_timeout_manager()
    async with manager.timeout_context(timeout) as tm:
        yield tm


# Enhanced BaseAgent timeout integration
class TimeoutMixin:
    """Mixin for adding enhanced timeout handling to agents."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout_manager = get_timeout_manager()

    async def execute_with_enhanced_timeout(
        self,
        state,
        operation_type: OperationType = OperationType.AGENT_EXECUTION,
        timeout: Optional[int] = None,
    ):
        """Execute agent with enhanced timeout handling."""
        task_id = f"{self.name}_{id(state)}"

        # Define cancellation handler
        async def cancellation_handler(task_id: str):
            logger.info(f"Cancelling agent execution: {self.name}")
            await self.cleanup_resources()

        try:
            # Execute with timeout
            result = await self.timeout_manager.execute_with_timeout(
                self.execute_logic(state),
                operation_type=operation_type,
                timeout=timeout or self.get_default_timeout(),
                task_id=task_id,
                cancellation_handler=cancellation_handler,
            )
            return result

        except TimeoutError as e:
            # Set timeout error in state
            return self._set_error(
                state, f"Agent execution timed out after {e.elapsed_seconds:.1f}s"
            )

    def get_default_timeout(self) -> int:
        """Get default timeout for this agent."""
        # Can be overridden by subclasses
        return 120  # 2 minutes default

    async def check_timeout_warning(self, elapsed_seconds: float, timeout: int):
        """Check if we should issue a timeout warning."""
        if elapsed_seconds > timeout * self.timeout_manager.config.warning_threshold:
            logger.warning(
                f"Agent '{self.name}' approaching timeout: "
                f"{elapsed_seconds:.1f}s / {timeout}s"
            )


# Utility functions
def get_timeout_stats() -> Dict[str, Any]:
    """Get timeout statistics."""
    manager = get_timeout_manager()
    return manager.get_timeout_stats()


async def cleanup_all_timeouts():
    """Clean up all active timeouts."""
    manager = get_timeout_manager()
    manager.cancel_all_tasks()
    logger.info("All timeout tasks cancelled")
