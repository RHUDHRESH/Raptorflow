"""
Retry Manager for Integration Components

Intelligent retry logic with exponential backoff and alternative strategies.
Implements PROMPT 69 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import random
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from ..models import PlanStep


class RetryStrategy(Enum):
    """Retry strategies."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    JITTER = "jitter"
    IMMEDIATE = "immediate"


class RetryDecision(Enum):
    """Retry decision outcomes."""
    RETRY = "retry"
    ABANDON = "abandon"
    ESCALATE = "escalate"
    USE_ALTERNATIVE = "use_alternative"


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    backoff_multiplier: float = 2.0
    jitter_factor: float = 0.1
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    retry_on_exceptions: List[type] = None
    stop_on_exceptions: List[type] = None
    alternative_strategies: List[Callable] = None


@dataclass
class RetryAttempt:
    """Information about a retry attempt."""
    attempt_number: int
    timestamp: datetime
    delay_seconds: float
    strategy: RetryStrategy
    error: Optional[Exception]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetryResult:
    """Result of retry operations."""
    success: bool
    final_result: Any
    total_attempts: int
    total_time_seconds: float
    retry_attempts: List[RetryAttempt]
    final_error: Optional[Exception]
    used_alternative: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class RetryManager:
    """
    Intelligent retry logic with exponential backoff and alternative strategies.

    Handles various failure scenarios with appropriate retry strategies.
    """

    def __init__(self, default_config: RetryConfig = None):
        """
        Initialize the retry manager.

        Args:
            default_config: Default retry configuration
        """
        self.default_config = default_config or RetryConfig()

        # Retry statistics
        self.stats = {
            "total_retries": 0,
            "successful_retries": 0,
            "abandoned_retries": 0,
            "escalated_retries": 0",
            "alternative_used": 0,
            "average_attempts": 0.0,
            "average_delay_seconds": 0.0
        }

        # Exception classification
        self.retryable_exceptions = {
            ConnectionError,
            TimeoutError,
            OSError,
            IOError,
            RuntimeError
        }

        self.non_retryable_exceptions = {
            KeyboardInterrupt,
            SystemExit,
            MemoryError,
            OverflowError,
            ValueError,
            TypeError,
            AttributeError
        }

        # Rate limiting
        self.rate_limiters: Dict[str, Dict[str, Any]] = {}

    async def retry_with_config(self, func: Callable, *args,
                             config: RetryConfig = None, **kwargs) -> RetryResult:
        """
        Execute function with retry logic using specific config.

        Args:
            func: Function to execute
            args: Function arguments
            config: Retry configuration
            kwargs: Function keyword arguments

        Returns:
            Retry result
        """
        retry_config = config or self.default_config
        retry_attempts = []
        total_time = 0.0

        for attempt in range(retry_config.max_retries + 1):
            start_time = time.time()

            try:
                # Execute function
                result = await func(*args, **kwargs)

                # Success
                if attempt > 0:
                    self.stats["successful_retries"] += 1

                return RetryResult(
                    success=True,
                    final_result=result,
                    total_attempts=attempt + 1,
                    total_time_seconds=total_time,
                    retry_attempts=retry_attempts,
                    final_error=None,
                    used_alternative=False,
                    metadata={
                        "strategy": retry_config.strategy.value,
                        "max_retries": retry_config.max_retries
                    }
                )

            except Exception as e:
                error = e
                execution_time = time.time() - start_time
                total_time += execution_time

                # Check if we should retry
                retry_decision = await self._should_retry(
                    error, attempt, retry_config, retry_attempts
                )

                if retry_decision == RetryDecision.ABANDON:
                    self.stats["abandoned_retries"] += 1
                    return RetryResult(
                        success=False,
                        final_result=None,
                        total_attempts=attempt + 1,
                        total_time_seconds=total_time,
                        retry_attempts=retry_attempts,
                        final_error=error,
                        used_alternative=False,
                        metadata={
                            "abandoned_reason": str(error),
                            "attempt": attempt + 1
                        }
                    )

                elif retry_decision == RetryDecision.ESCALATE:
                    self.stats["escalated_retries"] += 1
                    return RetryResult(
                        success=False,
                        final_result=None,
                        total_attempts=attempt + 1,
                        total_time_seconds=total_time,
                        retry_attempts=retry_attempts,
                        final_error=error,
                        used_alternative=False,
                        metadata={
                            "escalated_reason": str(error),
                            "attempt": attempt + 1
                        }
                    )

                elif retry_decision == RetryDecision.USE_ALTERNATIVE:
                    # Try alternative strategy
                    if retry_config.alternative_strategies:
                        for alt_strategy in retry_config.alternative_strategies:
                            try:
                                # Execute alternative strategy
                                alt_result = await alt_strategy(*args, **kwargs)
                                self.stats["alternative_used"] += 1

                                return RetryResult(
                                    success=True,
                                    final_result=alt_result,
                                    total_attempts=attempt + 1,
                                    total_time_seconds=total_time,
                                    retry_attempts=retry_attempts,
                                    final_error=None,
                                    used_alternative=True,
                                    metadata={
                                        "alternative_strategy": alt_strategy.__name__,
                                        "attempt": attempt + 1
                                    }
                                )

                            except Exception as alt_error:
                                # Alternative failed, continue with normal retry
                                pass

                # Calculate delay for next retry
                delay = self._calculate_delay(
                    attempt, retry_config, retry_attempts
                )

                # Create retry attempt record
                retry_attempt = RetryAttempt(
                    attempt_number=attempt + 1,
                    timestamp=datetime.now(),
                    delay_seconds=delay,
                    strategy=retry_config.strategy,
                    error=error,
                    metadata={
                        "function": func.__name__,
                        "args_count": len(args),
                        "kwargs_count": len(kwargs)
                    }
                )

                retry_attempts.append(retry_attempt)
                self.stats["total_retries"] += 1

                # Wait before retry
                if delay > 0:
                    await asyncio.sleep(delay)

        # Should not reach here, but handle gracefully
        return RetryResult(
            success=False,
            final_result=None,
            total_attempts=retry_config.max_retries + 1,
            total_time_seconds=total_time,
            retry_attempts=retry_attempts,
            final_error=Exception("Max retries exceeded"),
            used_alternative=False,
            metadata={"exhausted_retries": True}
        )

    async def retry(self, func: Callable, *args, **kwargs) -> RetryResult:
        """Execute function with default retry logic."""
        return await self.retry_with_config(func, *args, **kwargs)

    async def retry_with_backoff(self, func: Callable, *args,
                               max_retries: int = 3, base_delay: float = 1.0,
                               max_delay: float = 60.0, backoff_multiplier: float = 2.0,
                               jitter: bool = True, **kwargs) -> RetryResult:
        """Execute function with exponential backoff retry."""
        config = RetryConfig(
            max_retries=max_retries,
            base_delay_seconds=base_delay,
            max_delay_seconds=max_delay,
            backoff_multiplier=backoff_multiplier,
            jitter_factor=0.1 if jitter else 0.0,
            strategy=RetryStrategy.EXPONENTIAL_BACKOFF
        )

        return await self.retry_with_config(func, *args, config=config, **kwargs)

    async def retry_with_linear_backoff(self, func: Callable, *args,
                                     max_retries: int = 3, base_delay: float = 1.0,
                                     max_delay: float = 30.0, **kwargs) -> RetryResult:
        """Execute function with linear backoff retry."""
        config = RetryConfig(
            max_retries=max_retries,
            base_delay_seconds=base_delay,
            max_delay_seconds=max_delay,
            backoff_multiplier=1.0,
            strategy=RetryStrategy.LINEAR_BACKOFF
        )

        return await self.retry_with_config(func, *args, config=config, **kwargs)

    async def retry_with_fixed_delay(self, func: Callable, *args,
                                   delay_seconds: float = 1.0,
                                   max_retries: int = 3, **kwargs) -> RetryResult:
        """Execute function with fixed delay retry."""
        config = RetryConfig(
            max_retries=max_retries,
            base_delay_seconds=delay_seconds,
            max_delay_seconds=delay_seconds,
            backoff_multiplier=1.0,
            strategy=RetryStrategy.FIXED_DELAY
        )

        return await self.retry_with_config(func, *args, config=config, **kwargs)

    async def retry_with_jitter(self, func: Callable, *args,
                             max_retries: int = 3, base_delay: float = 1.0,
                             max_delay: float = 60.0, jitter_factor: float = 0.1,
                             **kwargs) -> RetryResult:
        """Execute function with jittered retry."""
        config = RetryConfig(
            max_retries=max_retries,
            base_delay_seconds=base_delay,
            max_delay_seconds=max_delay,
            jitter_factor=jitter_factor,
            strategy=RetryStrategy.JITTER
        )

        return await self.retry_with_config(func, *args, config=config, **kwargs)

    async def retry_immediate(self, func: Callable, *args, **kwargs) -> RetryResult:
        """Execute function with immediate retry (no delay)."""
        config = RetryConfig(
            max_retries=3,
            base_delay_seconds=0.0,
            max_delay_seconds=0.0,
            backoff_multiplier=1.0,
            strategy=RetryStrategy.IMMEDIATE
        )

        return await self.retry_with_config(func, *args, config=config, **kwargs)

    def _should_retry(self, error: Exception, attempt: int,
                    config: RetryConfig, retry_attempts: List[RetryAttempt]) -> RetryDecision:
        """Determine if we should retry based on error and attempt."""
        # Check if we've reached max retries
        if attempt >= config.max_retries:
            return RetryDecision.ABANDON

        # Check stop-on exceptions
        if config.stop_on_exceptions and type(error) in config.stop_on_exceptions:
            return RetryDecision.ABANDON

        # Check non-retryable exceptions
        if type(error) in self.non_retryable_exceptions:
            return RetryDecision.ABANDON

        # Check retry-on exceptions
        if config.retry_on_exceptions and type(error) not in config.retry_on_exceptions:
            return RetryDecision.ABANDON

        # Check if error suggests escalation
        if self._should_escalate(error, attempt, config):
            return RetryDecision.ESCALATE

        # Check if error suggests alternative strategy
        if self._should_use_alternative(error, attempt, config):
            return RetryDecision.USE_ALTERNATIVE

        # Default to retry
        return RetryDecision.RETRY

    def _should_escalate(self, error: error, attempt: int, config: RetryConfig) -> bool:
        """Check if error suggests escalation."""
        # Escalate after certain number of retries
        if attempt >= 2:
            return True

        # Escalate for certain error types
        escalation_errors = [
            MemoryError,
            OverflowError,
            SystemError
        ]

        return type(error) in escalation_errors

    def _should_use_alternative(self, error: error, attempt: int, config: config: RetryConfig) -> bool:
        """Check if error suggests using alternative strategy."""
        # Use alternative after certain number of retries
        if attempt >= 1 and config.alternative_strategies:
            return True

        # Use alternative for certain error types
        alternative_errors = [
            ConnectionError,
            TimeoutError
        ]

        return type(error) in alternative_errors

    def _calculate_delay(self, attempt: int, config: RetryConfig,
                        retry_attempts: List[RetryAttempt]) -> float:
        """Calculate delay for next retry based on strategy."""
        if config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = config.base_delay_seconds * (config.backoff_multiplier ** attempt)
        elif config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = config.base_delay_seconds * (attempt + 1)
        elif config.strategy == RetryStrategy.FIXED_DELAY:
            delay = config.base_delay_seconds
        elif config.strategy == RetryStrategy.JITTER:
            delay = config.base_delay_seconds * (attempt + 1)
            # Add jitter
            jitter_range = delay * config.jitter_factor
            jitter = random.uniform(-jitter_range, jitter_range)
            delay += jitter
        elif config.strategy == RetryStrategy.IMMEDIATE:
            delay = 0.0
        else:
            delay = config.base_delay_seconds

        # Apply max delay limit
        delay = min(delay, config.max_delay_seconds)

        return delay

    def add_rate_limiter(self, name: str, max_requests: int, time_window_seconds: int = 60) -> None:
        """Add a rate limiter."""
        self.rate_limiters[name] = {
            "max_requests": max_requests,
            "time_window_seconds": time_window,
            "requests": [],
            "last_reset": time.time()
        }

    def check_rate_limit(self, name: str) -> bool:
        """Check if rate limit allows request."""
        limiter = self.rate_limiters.get(name)
        if not limiter:
            return True

        now = time.time()

        # Reset window if needed
        if now - limiter["last_reset"] > limiter["time_window_seconds"]:
            limiter["requests"] = []
            limiter["last_reset"] = now

        # Check if under limit
        return len(limiter["requests"]) < limiter["max_requests"]

    def record_request(self, name: str) -> None:
        """Record a request in the rate limiter."""
        limiter = self.rate_limiters.get(name)
        if limiter:
            limiter["requests"].append(time.time())

    def get_retry_stats(self) -> Dict[str, Any]:
        """Get retry statistics."""
        if self.stats["total_retries"] > 0:
            self.stats["average_attempts"] = self.stats["total_retries"] / max(
                self.stats["successful_retries"] + self.stats["abandoned_retries"] + self.stats["escalated_retries"], 1
            )

        if self.stats["total_retries"] > 0:
            total_delay = sum(
                attempt.delay_seconds for attempt in self.stats.get("retry_attempts", [])
            )
            self.stats["average_delay_seconds"] = total_delay / len(self.stats["retry_attempts"])

        return self.stats

    def create_retry_config(self, **kwargs) -> RetryConfig:
        """Create a retry configuration."""
        return RetryConfig(**kwargs)

    def classify_exception(self, error: Exception) -> str:
        """Classify an exception type for retry logic."""
        if type(error) in self.retryable_exceptions:
            return "retryable"
        elif type(error) in self.non_retryable_exceptions:
            return "non_retryable"
        else:
            return "unknown"

    def is_retryable(self, error: Exception) -> bool:
        """Check if an exception is retryable."""
        return self.classify_exception(error) == "retryable"

    def is_non_retryable(self, error: Exception) -> bool:
        """Check if an exception is non-retryable."""
        return self.classify_exception(error) == "non_retryable"

    def get_error_pattern(self, error: Exception) -> str:
        """Get error pattern for matching."""
        error_type = type(error).__name__
        error_message = str(error).lower()

        # Common error patterns
        if "connection" in error_message:
            return "connection"
        elif "timeout" in error_message:
            return "timeout"
        elif "permission" in error_message:
            return "permission"
        elif "not found" in error_message:
            return "not_found"
        elif "invalid" in error_message:
            return "invalid"
        elif "failed" in error_message:
            return "failure"
        else:
            return "general"

    def get_retry_recommendation(self, error: Exception, attempt: int,
                                  config: RetryConfig) -> str:
        """Get recommendation for retry strategy."""
        error_type = type(error).__name__
        error_message = str(error).lower()

        # Connection errors
        if "connection" in error_message:
            if attempt < 2:
                return "Retry with exponential backoff"
            else:
                return "Use alternative connection method"

        # Timeout errors
        elif "timeout" in error_message:
            if attempt < 3:
                return "Retry with longer timeout"
            else:
                return "Escalate to higher timeout"

        # Permission errors
        elif "permission" in error_message:
            return "Check permissions and retry"

        # Resource errors
        elif "resource" in error_message:
            if attempt < 2:
                return "Retry after resource cleanup"
            else:
                return "Escalate resource issue"

        # General recommendation
        if attempt < config.max_retries:
            return f"Retry (attempt {attempt + 1}/{config.max_retries})"
        else:
            return "Max retries reached, investigate root cause"

    def create_retry_report(self, result: RetryResult) -> Dict[str, Any]:
        """Create a detailed retry report."""
        report = {
            "success": result.success,
            "total_attempts": result.total_attempts,
            "total_time_seconds": result.total_time_seconds,
            "final_error": str(result.final_error) if result.final_error else None,
            "used_alternative": result.used_alternative,
            "metadata": result.metadata
        }

        if result.retry_attempts:
            report["retry_details"] = [
                {
                    "attempt": attempt.attempt_number,
                    "delay_seconds": attempt.delay_seconds,
                    "strategy": attempt.strategy.value,
                    "error": str(attempt.error) if attempt.error else None,
                    "timestamp": attempt.timestamp.isoformat()
                }
                for attempt in result.retry_attempts
            ]

        return report
