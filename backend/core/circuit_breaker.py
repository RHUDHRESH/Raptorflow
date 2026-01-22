"""
Circuit Breaker Manager for Payment System
Implements circuit breaker pattern with fallback mechanisms
Addresses critical circuit breaker vulnerabilities identified in red team audit
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List, Union, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import redis
from functools import wraps
from collections import defaultdict, deque

from backend.core.audit_logger import audit_logger, EventType, LogLevel

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "CLOSED"           # Normal operation
    OPEN = "OPEN"               # Circuit is open, calls fail fast
    HALF_OPEN = "HALF_OPEN"     # Testing if service has recovered

class FailureType(Enum):
    """Types of failures"""
    TIMEOUT = "TIMEOUT"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    HTTP_ERROR = "HTTP_ERROR"
    RATE_LIMIT = "RATE_LIMIT"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNKNOWN = "UNKNOWN"

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5              # Failures before opening
    recovery_timeout: timedelta = timedelta(minutes=1)
    success_threshold: int = 3              # Successes in half-open to close
    timeout: timedelta = timedelta(seconds=30)
    max_requests: int = 100                 # Max requests per window
    request_window: timedelta = timedelta(minutes=1)
    fallback_enabled: bool = True
    monitoring_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CallResult:
    """Result of a circuit breaker call"""
    success: bool
    duration_ms: float
    error: Optional[str] = None
    error_type: Optional[FailureType] = None
    fallback_used: bool = False
    circuit_state: Optional[CircuitState] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CircuitMetrics:
    """Circuit breaker metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeouts: int = 0
    circuit_opens: int = 0
    fallback_calls: int = 0
    average_response_time: float = 0.0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_changes: List[Dict[str, Any]] = field(default_factory=list)

class CircuitBreaker:
    """
    Production-Ready Circuit Breaker
    Implements circuit breaker pattern with comprehensive monitoring
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig, redis_client: Optional[redis.Redis] = None):
        self.name = name
        self.config = config
        self.redis = redis_client
        
        # State
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change: datetime = datetime.now()
        
        # Metrics
        self.metrics = CircuitMetrics()
        
        # Request tracking
        self._request_history = deque(maxlen=1000)  # Last 1000 requests
        self._failure_history = deque(maxlen=100)   # Last 100 failures
        
        # Fallback functions
        self._fallback_functions: List[Callable] = []
        
        # Redis keys for distributed state
        if self.redis:
            self.state_key = f"circuit_breaker:{self.name}:state"
            self.metrics_key = f"circuit_breaker:{self.name}:metrics"
        
        logger.info(f"Circuit breaker '{name}' initialized")
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        """
        start_time = time.time()
        
        try:
            # Check circuit state
            if not await self._can_execute():
                # Circuit is open, try fallback
                return await self._execute_fallback(*args, **kwargs)
            
            # Execute the function
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Record success
                await self._record_success()
                
                duration_ms = (time.time() - start_time) * 1000
                
                return result
                
            except Exception as e:
                # Record failure
                failure_type = self._classify_error(e)
                await self._record_failure(failure_type, str(e))
                
                # Try fallback
                try:
                    fallback_result = await self._execute_fallback(*args, **kwargs)
                    return fallback_result
                except Exception as fallback_error:
                    # Fallback also failed
                    raise CircuitBreakerError(
                        f"Both primary and fallback failed: {str(e)}",
                        primary_error=e,
                        fallback_error=fallback_error,
                        circuit_state=self.state
                    )
        
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # Record metrics
            await self._record_call_metrics(
                success=False,
                duration_ms=duration_ms,
                error=str(e),
                fallback_used=hasattr(e, 'fallback_error')
            )
            
            raise
    
    async def _can_execute(self) -> bool:
        """Check if execution is allowed based on circuit state"""
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if datetime.now() - self.last_failure_time >= self.config.recovery_timeout:
                await self._transition_to_half_open()
                return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            return True
        else:
            return False
    
    async def _execute_fallback(self, *args, **kwargs) -> Any:
        """Execute fallback function"""
        if not self.config.fallback_enabled or not self._fallback_functions:
            raise CircuitBreakerError(
                "Circuit is open and no fallback available",
                circuit_state=self.state
            )
        
        # Try fallback functions in order
        last_error = None
        for fallback_func in self._fallback_functions:
            try:
                if asyncio.iscoroutinefunction(fallback_func):
                    result = await fallback_func(*args, **kwargs)
                else:
                    result = fallback_func(*args, **kwargs)
                
                # Record fallback usage
                self.metrics.fallback_calls += 1
                
                await audit_logger.log_event(
                    event_type=EventType.CIRCUIT_BREAKER_FALLBACK_USED,
                    level=LogLevel.WARNING,
                    request_data={
                        "circuit_name": self.name,
                        "state": self.state.value,
                        "fallback_function": fallback_func.__name__
                    }
                )
                
                return result
                
            except Exception as e:
                last_error = e
                continue
        
        # All fallbacks failed
        raise CircuitBreakerError(
            "All fallback functions failed",
            circuit_state=self.state,
            fallback_error=last_error
        )
    
    async def _record_success(self):
        """Record successful execution"""
        self.success_count += 1
        self.metrics.successful_requests += 1
        self.metrics.last_success_time = datetime.now()
        
        # Add to request history
        self._request_history.append({
            "timestamp": datetime.now(),
            "success": True
        })
        
        # Check if we should close the circuit (half-open state)
        if self.state == CircuitState.HALF_OPEN:
            if self.success_count >= self.config.success_threshold:
                await self._transition_to_closed()
        
        # Update metrics in Redis
        if self.redis:
            await self._update_redis_metrics()
    
    async def _record_failure(self, failure_type: FailureType, error_message: str):
        """Record failed execution"""
        self.failure_count += 1
        self.metrics.failed_requests += 1
        self.metrics.last_failure_time = datetime.now()
        
        # Add to request and failure history
        self._request_history.append({
            "timestamp": datetime.now(),
            "success": False,
            "error_type": failure_type.value,
            "error_message": error_message
        })
        
        self._failure_history.append({
            "timestamp": datetime.now(),
            "error_type": failure_type.value,
            "error_message": error_message
        })
        
        # Check if we should open the circuit
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                await self._transition_to_open()
        elif self.state == CircuitState.HALF_OPEN:
            # Any failure in half-open should open the circuit again
            await self._transition_to_open()
        
        # Update metrics in Redis
        if self.redis:
            await self._update_redis_metrics()
    
    def _classify_error(self, error: Exception) -> FailureType:
        """Classify error type"""
        error_str = str(error).lower()
        
        if "timeout" in error_str:
            return FailureType.TIMEOUT
        elif "connection" in error_str or "network" in error_str:
            return FailureType.CONNECTION_ERROR
        elif "rate limit" in error_str or "too many requests" in error_str:
            return FailureType.RATE_LIMIT
        elif "authentication" in error_str or "unauthorized" in error_str:
            return FailureType.AUTHENTICATION_ERROR
        elif "validation" in error_str or "invalid" in error_str:
            return FailureType.VALIDATION_ERROR
        elif hasattr(error, 'status_code') and 400 <= error.status_code < 500:
            return FailureType.HTTP_ERROR
        else:
            return FailureType.UNKNOWN
    
    async def _transition_to_open(self):
        """Transition circuit to open state"""
        old_state = self.state
        self.state = CircuitState.OPEN
        self.last_state_change = datetime.now()
        self.metrics.circuit_opens += 1
        
        # Record state change
        self.metrics.state_changes.append({
            "timestamp": datetime.now(),
            "from_state": old_state.value,
            "to_state": CircuitState.OPEN.value,
            "reason": f"Failure threshold ({self.config.failure_threshold}) reached"
        })
        
        await audit_logger.log_event(
            event_type=EventType.CIRCUIT_BREAKER_OPENED,
            level=LogLevel.WARNING,
            request_data={
                "circuit_name": self.name,
                "failure_count": self.failure_count,
                "failure_threshold": self.config.failure_threshold
            }
        )
        
        # Update Redis state
        if self.redis:
            await self._update_redis_state()
    
    async def _transition_to_half_open(self):
        """Transition circuit to half-open state"""
        old_state = self.state
        self.state = CircuitState.HALF_OPEN
        self.last_state_change = datetime.now()
        self.success_count = 0  # Reset success count for half-open
        
        # Record state change
        self.metrics.state_changes.append({
            "timestamp": datetime.now(),
            "from_state": old_state.value,
            "to_state": CircuitState.HALF_OPEN.value,
            "reason": "Recovery timeout elapsed"
        })
        
        await audit_logger.log_event(
            event_type=EventType.CIRCUIT_BREAKER_HALF_OPEN,
            level=LogLevel.INFO,
            request_data={
                "circuit_name": self.name,
                "recovery_timeout": self.config.recovery_timeout.total_seconds()
            }
        )
        
        # Update Redis state
        if self.redis:
            await self._update_redis_state()
    
    async def _transition_to_closed(self):
        """Transition circuit to closed state"""
        old_state = self.state
        self.state = CircuitState.CLOSED
        self.last_state_change = datetime.now()
        self.failure_count = 0  # Reset failure count
        self.success_count = 0  # Reset success count
        
        # Record state change
        self.metrics.state_changes.append({
            "timestamp": datetime.now(),
            "from_state": old_state.value,
            "to_state": CircuitState.CLOSED.value,
            "reason": f"Success threshold ({self.config.success_threshold}) reached in half-open"
        })
        
        await audit_logger.log_event(
            event_type=EventType.CIRCUIT_BREAKER_CLOSED,
            level=LogLevel.INFO,
            request_data={
                "circuit_name": self.name,
                "success_count": self.success_count,
                "success_threshold": self.config.success_threshold
            }
        )
        
        # Update Redis state
        if self.redis:
            await self._update_redis_state()
    
    async def _record_call_metrics(
        self,
        success: bool,
        duration_ms: float,
        error: Optional[str] = None,
        fallback_used: bool = False
    ):
        """Record call metrics"""
        self.metrics.total_requests += 1
        
        # Update average response time
        if self.metrics.total_requests == 1:
            self.metrics.average_response_time = duration_ms
        else:
            self.metrics.average_response_time = (
                (self.metrics.average_response_time * (self.metrics.total_requests - 1) + duration_ms) /
                self.metrics.total_requests
            )
        
        # Update Redis metrics
        if self.redis:
            await self._update_redis_metrics()
    
    async def _update_redis_state(self):
        """Update circuit state in Redis"""
        try:
            state_data = {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
                "last_state_change": self.last_state_change.isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            self.redis.setex(
                self.state_key,
                3600,  # 1 hour expiration
                json.dumps(state_data)
            )
        except Exception as e:
            logger.error(f"Error updating Redis state: {e}")
    
    async def _update_redis_metrics(self):
        """Update circuit metrics in Redis"""
        try:
            metrics_data = {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "timeouts": self.metrics.timeouts,
                "circuit_opens": self.metrics.circuit_opens,
                "fallback_calls": self.metrics.fallback_calls,
                "average_response_time": self.metrics.average_response_time,
                "last_failure_time": self.metrics.last_failure_time.isoformat() if self.metrics.last_failure_time else None,
                "last_success_time": self.metrics.last_success_time.isoformat() if self.metrics.last_success_time else None,
                "updated_at": datetime.now().isoformat()
            }
            
            self.redis.setex(
                self.metrics_key,
                3600,  # 1 hour expiration
                json.dumps(metrics_data)
            )
        except Exception as e:
            logger.error(f"Error updating Redis metrics: {e}")
    
    def add_fallback(self, fallback_func: Callable):
        """Add fallback function"""
        self._fallback_functions.append(fallback_func)
    
    def remove_fallback(self, fallback_func: Callable):
        """Remove fallback function"""
        if fallback_func in self._fallback_functions:
            self._fallback_functions.remove(fallback_func)
    
    async def force_open(self):
        """Force circuit to open state"""
        await self._transition_to_open()
    
    async def force_close(self):
        """Force circuit to closed state"""
        await self._transition_to_closed()
    
    def get_state(self) -> CircuitState:
        """Get current circuit state"""
        return self.state
    
    def get_metrics(self) -> CircuitMetrics:
        """Get circuit metrics"""
        return self.metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for circuit breaker"""
        try:
            # Calculate success rate
            success_rate = 0.0
            if self.metrics.total_requests > 0:
                success_rate = (self.metrics.successful_requests / self.metrics.total_requests) * 100
            
            # Calculate failure rate
            failure_rate = 0.0
            if self.metrics.total_requests > 0:
                failure_rate = (self.metrics.failed_requests / self.metrics.total_requests) * 100
            
            # Determine health status
            if self.state == CircuitState.OPEN:
                status = "unhealthy"
                message = f"Circuit is open due to {self.failure_count} failures"
            elif failure_rate > 50:
                status = "degraded"
                message = f"High failure rate: {failure_rate:.1f}%"
            elif success_rate < 80:
                status = "degraded"
                message = f"Low success rate: {success_rate:.1f}%"
            else:
                status = "healthy"
                message = "Circuit breaker is operational"
            
            return {
                "status": status,
                "message": message,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "metrics": {
                    "total_requests": self.metrics.total_requests,
                    "successful_requests": self.metrics.successful_requests,
                    "failed_requests": self.metrics.failed_requests,
                    "success_rate": round(success_rate, 2),
                    "failure_rate": round(failure_rate, 2),
                    "average_response_time": round(self.metrics.average_response_time, 2),
                    "circuit_opens": self.metrics.circuit_opens,
                    "fallback_calls": self.metrics.fallback_calls
                },
                "configuration": {
                    "failure_threshold": self.config.failure_threshold,
                    "recovery_timeout": self.config.recovery_timeout.total_seconds(),
                    "success_threshold": self.config.success_threshold,
                    "fallback_enabled": self.config.fallback_enabled
                },
                "last_state_change": self.last_state_change.isoformat(),
                "fallback_functions_count": len(self._fallback_functions)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "error": str(e)
            }

class CircuitBreakerManager:
    """
    Manager for multiple circuit breakers
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        logger.info("Circuit Breaker Manager initialized")
    
    def get_circuit_breaker(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
        """Get or create circuit breaker"""
        if name not in self._circuit_breakers:
            if config is None:
                config = CircuitBreakerConfig()
            
            self._circuit_breakers[name] = CircuitBreaker(name, config, self.redis)
        
        return self._circuit_breakers[name]
    
    def circuit_breaker(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: timedelta = timedelta(minutes=1),
        success_threshold: int = 3,
        timeout: timedelta = timedelta(seconds=30),
        fallback_enabled: bool = True
    ):
        """Decorator for circuit breaker protection"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                config = CircuitBreakerConfig(
                    failure_threshold=failure_threshold,
                    recovery_timeout=recovery_timeout,
                    success_threshold=success_threshold,
                    timeout=timeout,
                    fallback_enabled=fallback_enabled
                )
                
                circuit = self.get_circuit_breaker(name, config)
                
                # Add default fallback if enabled
                if fallback_enabled and not circuit._fallback_functions:
                    circuit.add_fallback(self._default_fallback)
                
                return await circuit.call(func, *args, **kwargs)
            
            return wrapper
        return decorator
    
    async def _default_fallback(self, *args, **kwargs):
        """Default fallback function"""
        raise CircuitBreakerError("Service unavailable and no fallback provided")
    
    async def get_all_metrics(self) -> Dict[str, Any]:
        """Get metrics for all circuit breakers"""
        metrics = {}
        
        for name, circuit in self._circuit_breakers.items():
            metrics[name] = circuit.get_metrics()
        
        return metrics
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Health check for all circuit breakers"""
        health_checks = {}
        
        for name, circuit in self._circuit_breakers.items():
            health_checks[name] = await circuit.health_check()
        
        # Calculate overall health
        total_circuits = len(health_checks)
        healthy_circuits = sum(1 for check in health_checks.values() if check["status"] == "healthy")
        degraded_circuits = sum(1 for check in health_checks.values() if check["status"] == "degraded")
        unhealthy_circuits = sum(1 for check in health_checks.values() if check["status"] == "unhealthy")
        
        overall_status = "healthy"
        if unhealthy_circuits > 0:
            overall_status = "unhealthy"
        elif degraded_circuits > 0:
            overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "total_circuits": total_circuits,
            "healthy_circuits": healthy_circuits,
            "degraded_circuits": degraded_circuits,
            "unhealthy_circuits": unhealthy_circuits,
            "circuit_breakers": health_checks
        }
    
    async def cleanup_expired_data(self) -> int:
        """Clean up expired circuit breaker data"""
        cleaned_count = 0
        
        if self.redis:
            try:
                # Clean up expired circuit breaker states
                pattern = "circuit_breaker:*:state"
                keys = self.redis.keys(pattern)
                
                for key in keys:
                    ttl = self.redis.ttl(key)
                    if ttl == -1:  # No expiration set
                        self.redis.expire(key, 3600)  # Set 1 hour expiration
                
                cleaned_count = len(keys)
                
            except Exception as e:
                logger.error(f"Error cleaning up circuit breaker data: {e}")
        
        return cleaned_count

class CircuitBreakerError(Exception):
    """Exception raised by circuit breaker"""
    
    def __init__(
        self,
        message: str,
        circuit_state: Optional[CircuitState] = None,
        primary_error: Optional[Exception] = None,
        fallback_error: Optional[Exception] = None
    ):
        super().__init__(message)
        self.circuit_state = circuit_state
        self.primary_error = primary_error
        self.fallback_error = fallback_error

# Global circuit breaker manager instance
circuit_breaker_manager = None

def get_circuit_breaker_manager(redis_client: Optional[redis.Redis] = None) -> CircuitBreakerManager:
    """Get or create circuit breaker manager instance"""
    global circuit_breaker_manager
    if circuit_breaker_manager is None:
        circuit_breaker_manager = CircuitBreakerManager(redis_client)
    return circuit_breaker_manager

# Decorator for standalone use
def circuit_breaker_protected(
    name: str,
    failure_threshold: int = 3,
    recovery_timeout: timedelta = timedelta(minutes=1),
    success_threshold: int = 3,
    timeout: timedelta = timedelta(seconds=30),
    fallback_enabled: bool = True
):
    """Standalone circuit breaker decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            manager = get_circuit_breaker_manager()
            circuit = manager.get_circuit_breaker(name, CircuitBreakerConfig(
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
                success_threshold=success_threshold,
                timeout=timeout,
                fallback_enabled=fallback_enabled
            ))
            
            return await circuit.call(func, *args, **kwargs)
        
        return wrapper
    return decorator
