"""
Circuit Breaker Pattern Implementation for PhonePe API
Provides resilience and fault tolerance for external API calls
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import deque
import statistics

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, calls fail fast
    HALF_OPEN = "half_open" # Testing if service has recovered

@dataclass
class CallResult:
    """Result of an API call"""
    success: bool
    duration_ms: int
    error: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5                    # Number of failures before opening
    recovery_timeout: timedelta = timedelta(minutes=2)  # Time to wait before trying again
    expected_response_time: timedelta = timedelta(seconds=5)  # Expected response time
    half_open_max_calls: int = 3                 # Max calls in half-open state
    monitoring_window: timedelta = timedelta(minutes=10)  # Window for metrics
    slow_call_threshold: timedelta = timedelta(seconds=3)   # Slow call threshold
    slow_call_percentage_threshold: float = 0.5  # % of slow calls to trigger opening

class CircuitBreakerMetrics:
    """Metrics collection for circuit breaker"""
    
    def __init__(self, window_size: timedelta):
        self.window_size = window_size
        self.calls: deque = deque(maxlen=1000)  # Store recent calls
        self._lock = asyncio.Lock()

    async def add_call(self, result: CallResult):
        """Add a call result to metrics"""
        async with self._lock:
            self.calls.append(result)
            # Remove old calls outside window
            cutoff = datetime.now() - self.window_size
            while self.calls and self.calls[0].timestamp < cutoff:
                self.calls.popleft()

    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        async with self._lock:
            if not self.calls:
                return {
                    "total_calls": 0,
                    "success_rate": 0.0,
                    "failure_rate": 0.0,
                    "avg_response_time": 0.0,
                    "slow_call_rate": 0.0,
                    "calls_per_minute": 0.0
                }

            total_calls = len(self.calls)
            successful_calls = sum(1 for call in self.calls if call.success)
            failed_calls = total_calls - successful_calls
            
            # Response times
            response_times = [call.duration_ms for call in self.calls]
            avg_response_time = statistics.mean(response_times) if response_times else 0
            
            # Slow calls
            slow_calls = sum(1 for call in self.calls if call.duration_ms > 3000)  # 3 seconds threshold
            slow_call_rate = slow_calls / total_calls if total_calls > 0 else 0
            
            # Calls per minute
            if len(self.calls) >= 2:
                time_span = (self.calls[-1].timestamp - self.calls[0].timestamp).total_seconds() / 60
                calls_per_minute = total_calls / time_span if time_span > 0 else 0
            else:
                calls_per_minute = 0

            return {
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": failed_calls,
                "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
                "failure_rate": failed_calls / total_calls if total_calls > 0 else 0,
                "avg_response_time": avg_response_time,
                "slow_calls": slow_calls,
                "slow_call_rate": slow_call_rate,
                "calls_per_minute": calls_per_minute,
                "last_call_time": self.calls[-1].timestamp.isoformat() if self.calls else None
            }

class CircuitBreaker:
    """Advanced circuit breaker implementation"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
        
        # Metrics
        self.metrics = CircuitBreakerMetrics(config.monitoring_window)
        
        # Call history for analysis
        self.call_history: List[CallResult] = []
        
        # Event callbacks
        self.state_change_callbacks: List[Callable[[CircuitState, CircuitState], None]] = []

    def add_state_change_callback(self, callback: Callable[[CircuitState, CircuitState], None]):
        """Add callback for state changes"""
        self.state_change_callbacks.append(callback)

    def _change_state(self, new_state: CircuitState):
        """Change circuit state and notify callbacks"""
        old_state = self.state
        self.state = new_state
        
        logger.info(f"Circuit breaker '{self.name}' state changed from {old_state.value} to {new_state.value}")
        
        # Notify callbacks
        for callback in self.state_change_callbacks:
            try:
                callback(old_state, new_state)
            except Exception as e:
                logger.error(f"State change callback failed: {e}")

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        start_time = time.time()
        
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._change_state(CircuitState.HALF_OPEN)
                self.half_open_calls = 0
            else:
                raise Exception(f"Circuit breaker '{self.name}' is OPEN - service unavailable")

        # Execute the call
        try:
            result = await func(*args, **kwargs)
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Record successful call
            call_result = CallResult(
                success=True,
                duration_ms=duration_ms,
                response_data=result if isinstance(result, dict) else None
            )
            await self._on_success(call_result)
            
            return result
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Record failed call
            call_result = CallResult(
                success=False,
                duration_ms=duration_ms,
                error=str(e)
            )
            await self._on_failure(call_result)
            
            raise

    async def _on_success(self, result: CallResult):
        """Handle successful call"""
        # Reset failure count
        self.failure_count = 0
        
        # Add to metrics
        await self.metrics.add_call(result)
        self.call_history.append(result)
        
        # Keep history manageable
        if len(self.call_history) > 1000:
            self.call_history = self.call_history[-500:]
        
        # If in half-open state, check if we can close
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.config.half_open_max_calls:
                self._change_state(CircuitState.CLOSED)
                logger.info(f"Circuit breaker '{self.name}' closed after successful recovery")

    async def _on_failure(self, result: CallResult):
        """Handle failed call"""
        # Add to metrics
        await self.metrics.add_call(result)
        self.call_history.append(result)
        
        # Keep history manageable
        if len(self.call_history) > 1000:
            self.call_history = self.call_history[-500:]
        
        # Update failure count
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        # Check if we should open the circuit
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self._change_state(CircuitState.OPEN)
                logger.warning(f"Circuit breaker '{self.name}' opened after {self.failure_count} failures")
        elif self.state == CircuitState.HALF_OPEN:
            self._change_state(CircuitState.OPEN)
            logger.warning(f"Circuit breaker '{self.name}' re-opened after failure in half-open state")

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = datetime.now() - self.last_failure_time
        return time_since_failure >= self.config.recovery_timeout

    async def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status"""
        metrics = await self.metrics.get_metrics()
        
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "half_open_calls": self.half_open_calls,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout.total_seconds(),
                "expected_response_time": self.config.expected_response_time.total_seconds(),
                "half_open_max_calls": self.config.half_open_max_calls
            },
            "metrics": metrics
        }

    def force_open(self):
        """Force the circuit to open (for testing/maintenance)"""
        self._change_state(CircuitState.OPEN)

    def force_close(self):
        """Force the circuit to close (for testing/recovery)"""
        self.failure_count = 0
        self.half_open_calls = 0
        self._change_state(CircuitState.CLOSED)

class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()

    async def get_circuit_breaker(self, name: str, config: CircuitBreakerConfig = None) -> CircuitBreaker:
        """Get or create a circuit breaker"""
        async with self._lock:
            if name not in self.circuit_breakers:
                if config is None:
                    config = CircuitBreakerConfig()
                self.circuit_breakers[name] = CircuitBreaker(name, config)
            return self.circuit_breakers[name]

    async def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers"""
        status = {}
        for name, cb in self.circuit_breakers.items():
            status[name] = await cb.get_status()
        return status

    async def health_check(self) -> Dict[str, Any]:
        """Overall health check"""
        all_status = await self.get_all_status()
        
        open_circuits = [name for name, status in all_status.items() if status["state"] == "open"]
        half_open_circuits = [name for name, status in all_status.items() if status["state"] == "half_open"]
        
        overall_health = "healthy"
        if open_circuits:
            overall_health = "unhealthy"
        elif half_open_circuits:
            overall_health = "degraded"
        
        return {
            "overall_health": overall_health,
            "total_circuits": len(all_status),
            "open_circuits": len(open_circuits),
            "half_open_circuits": len(half_open_circuits),
            "closed_circuits": len(all_status) - len(open_circuits) - len(half_open_circuits),
            "open_circuit_names": open_circuits,
            "half_open_circuit_names": half_open_circuits,
            "details": all_status
        }

# Decorator for circuit breaker protection
def circuit_breaker_protected(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: timedelta = timedelta(minutes=2),
    expected_response_time: timedelta = timedelta(seconds=5)
):
    """Decorator to protect functions with circuit breaker"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get circuit breaker from registry
            config = CircuitBreakerConfig(
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                expected_response_time=expected_response_time
            )
            cb = await circuit_breaker_registry.get_circuit_breaker(name, config)
            
            # Call with circuit breaker protection
            return await cb.call(func, *args, **kwargs)
        
        return wrapper
    return decorator

# Global registry instance
circuit_breaker_registry = CircuitBreakerRegistry()

# Predefined circuit breakers for PhonePe endpoints
PHONEPE_CIRCUIT_BREAKERS = {
    "payment_initiation": CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=timedelta(minutes=1),
        expected_response_time=timedelta(seconds=3)
    ),
    "payment_status": CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout=timedelta(minutes=2),
        expected_response_time=timedelta(seconds=2)
    ),
    "refund_processing": CircuitBreakerConfig(
        failure_threshold=3,
        recovery_timeout=timedelta(minutes=5),
        expected_response_time=timedelta(seconds=5)
    ),
    "webhook_validation": CircuitBreakerConfig(
        failure_threshold=10,
        recovery_timeout=timedelta(minutes=1),
        expected_response_time=timedelta(seconds=1)
    ),
    "oauth_token": CircuitBreakerConfig(
        failure_threshold=2,
        recovery_timeout=timedelta(minutes=1),
        expected_response_time=timedelta(seconds=2)
    )
}

async def initialize_phonepe_circuit_breakers():
    """Initialize PhonePe circuit breakers"""
    for name, config in PHONEPE_CIRCUIT_BREAKERS.items():
        await circuit_breaker_registry.get_circuit_breaker(f"phonepe_{name}", config)
    
    logger.info("PhonePe circuit breakers initialized")
