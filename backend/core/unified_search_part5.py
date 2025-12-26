"""
Part 5: Fault Tolerance and Error Handling System
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements comprehensive fault tolerance, retry mechanisms, circuit breakers,
and intelligent error recovery for maximum system reliability.
"""

import asyncio
import logging
import random
import time
from typing import Any, Dict, List, Optional, Set, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import traceback

from backend.core.unified_search_part1 import (
    SearchProvider, SearchQuery, SearchResult, SearchSession
)

logger = logging.getLogger("raptorflow.unified_search.fault_tolerance")


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorType(Enum):
    """Types of errors that can occur."""
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    AUTHENTICATION_ERROR = "authentication_error"
    PARSING_ERROR = "parsing_error"
    VALIDATION_ERROR = "validation_error"
    PROVIDER_ERROR = "provider_error"
    SYSTEM_ERROR = "system_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class ErrorInfo:
    """Detailed error information for analysis."""
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    provider: Optional[SearchProvider] = None
    url: Optional[str] = None
    query: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    stack_trace: Optional[str] = None
    retry_count: int = 0
    recovery_action: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            'error_type': self.error_type.value,
            'severity': self.severity.value,
            'message': self.message,
            'provider': self.provider.value if self.provider else None,
            'url': self.url,
            'query': self.query,
            'timestamp': self.timestamp.isoformat(),
            'retry_count': self.retry_count,
            'recovery_action': self.recovery_action,
            'context': self.context
        }


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, calls fail immediately
    HALF_OPEN = "half_open"  # Testing if service has recovered


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_threshold: int = 3,
        timeout: float = 30.0
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.timeout = timeout
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await asyncio.wait_for(func(*args, **kwargs), timeout=self.timeout)
            self._on_success()
            return result
            
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        if self.last_failure_time is None:
            return False
        
        time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call."""
        self.last_success_time = datetime.now()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._reset()
        else:
            # In CLOSED state, just reset failure count
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            logger.warning("Circuit breaker transitioning to OPEN from HALF_OPEN")
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker transitioning to OPEN after {self.failure_count} failures")
    
    def _reset(self):
        """Reset circuit breaker to closed state."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info("Circuit breaker reset to CLOSED")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'failure_threshold': self.failure_threshold,
            'success_threshold': self.success_threshold,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'last_success_time': self.last_success_time.isoformat() if self.last_success_time else None
        }


class RetryPolicy:
    """Retry policy with exponential backoff and jitter."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_errors: Optional[Set[ErrorType]] = None
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        
        if retryable_errors is None:
            self.retryable_errors = {
                ErrorType.NETWORK_ERROR,
                ErrorType.TIMEOUT_ERROR,
                ErrorType.RATE_LIMIT_ERROR,
                ErrorType.PROVIDER_ERROR
            }
        else:
            self.retryable_errors = retryable_errors
    
    def should_retry(self, error_info: ErrorInfo, attempt: int) -> bool:
        """Determine if operation should be retried."""
        if attempt >= self.max_attempts:
            return False
        
        return error_info.error_type in self.retryable_errors
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        delay = self.base_delay * (self.exponential_base ** (attempt - 1))
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add ±25% jitter
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)


class ErrorClassifier:
    """Classify errors and determine appropriate recovery actions."""
    
    def __init__(self):
        self.error_patterns = {
            ErrorType.NETWORK_ERROR: [
                'connection', 'network', 'dns', 'resolve', 'unreachable',
                'connection refused', 'connection reset', 'connection timeout'
            ],
            ErrorType.TIMEOUT_ERROR: [
                'timeout', 'timed out', 'deadline', 'time limit'
            ],
            ErrorType.RATE_LIMIT_ERROR: [
                'rate limit', 'too many requests', 'quota exceeded', '429'
            ],
            ErrorType.AUTHENTICATION_ERROR: [
                'unauthorized', 'authentication', 'auth', '401', 'forbidden', '403'
            ],
            ErrorType.PARSING_ERROR: [
                'parse', 'json', 'xml', 'invalid format', 'malformed'
            ],
            ErrorType.VALIDATION_ERROR: [
                'validation', 'invalid', 'bad request', '400'
            ],
            ErrorType.PROVIDER_ERROR: [
                'provider', 'service unavailable', '503', 'internal error', '500'
            ]
        }
    
    def classify_error(self, exception: Exception, context: Dict[str, Any]) -> ErrorInfo:
        """Classify exception and create error info."""
        error_message = str(exception).lower()
        stack_trace = traceback.format_exc()
        
        # Determine error type
        error_type = self._determine_error_type(error_message, exception)
        
        # Determine severity
        severity = self._determine_severity(error_type, exception, context)
        
        # Determine recovery action
        recovery_action = self._determine_recovery_action(error_type, context)
        
        return ErrorInfo(
            error_type=error_type,
            severity=severity,
            message=str(exception),
            provider=context.get('provider'),
            url=context.get('url'),
            query=context.get('query'),
            stack_trace=stack_trace,
            context=context,
            recovery_action=recovery_action
        )
    
    def _determine_error_type(self, message: str, exception: Exception) -> ErrorType:
        """Determine error type based on message and exception."""
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if pattern in message:
                    return error_type
        
        # Check exception type
        exception_type = type(exception).__name__.lower()
        if 'timeout' in exception_type:
            return ErrorType.TIMEOUT_ERROR
        elif 'connection' in exception_type:
            return ErrorType.NETWORK_ERROR
        elif 'json' in exception_type or 'parse' in exception_type:
            return ErrorType.PARSING_ERROR
        elif 'value' in exception_type:
            return ErrorType.VALIDATION_ERROR
        
        return ErrorType.UNKNOWN_ERROR
    
    def _determine_severity(self, error_type: ErrorType, exception: Exception, context: Dict[str, Any]) -> ErrorSeverity:
        """Determine error severity."""
        # Critical errors
        if error_type in [ErrorType.AUTHENTICATION_ERROR, ErrorType.SYSTEM_ERROR]:
            return ErrorSeverity.CRITICAL
        
        # High severity
        if error_type in [ErrorType.PROVIDER_ERROR, ErrorType.RATE_LIMIT_ERROR]:
            return ErrorSeverity.HIGH
        
        # Medium severity
        if error_type in [ErrorType.NETWORK_ERROR, ErrorType.TIMEOUT_ERROR]:
            return ErrorSeverity.MEDIUM
        
        # Low severity
        return ErrorSeverity.LOW
    
    def _determine_recovery_action(self, error_type: ErrorType, context: Dict[str, Any]) -> Optional[str]:
        """Determine appropriate recovery action."""
        actions = {
            ErrorType.NETWORK_ERROR: "retry_with_backoff",
            ErrorType.TIMEOUT_ERROR: "retry_with_longer_timeout",
            ErrorType.RATE_LIMIT_ERROR: "wait_and_retry",
            ErrorType.AUTHENTICATION_ERROR: "refresh_credentials",
            ErrorType.PARSING_ERROR: "fallback_parser",
            ErrorType.VALIDATION_ERROR: "sanitize_input",
            ErrorType.PROVIDER_ERROR: "switch_provider",
            ErrorType.SYSTEM_ERROR: "escalate"
        }
        
        return actions.get(error_type)


class FaultTolerantExecutor:
    """Fault-tolerant executor with retry, circuit breaker, and fallback mechanisms."""
    
    def __init__(self):
        self.circuit_breakers: Dict[SearchProvider, CircuitBreaker] = {}
        self.retry_policy = RetryPolicy()
        self.error_classifier = ErrorClassifier()
        self.error_history: List[ErrorInfo] = []
        self.fallback_providers: Dict[SearchProvider, List[SearchProvider]] = {
            SearchProvider.BRAVE: [SearchProvider.DUCKDUCKGO, SearchProvider.NATIVE],
            SearchProvider.SERPER: [SearchProvider.BRAVE, SearchProvider.DUCKDUCKGO],
            SearchProvider.DUCKDUCKGO: [SearchProvider.NATIVE],
            SearchProvider.NATIVE: [SearchProvider.DUCKDUCKGO]
        }
        
    def get_circuit_breaker(self, provider: SearchProvider) -> CircuitBreaker:
        """Get or create circuit breaker for provider."""
        if provider not in self.circuit_breakers:
            self.circuit_breakers[provider] = CircuitBreaker()
        return self.circuit_breakers[provider]
    
    async def execute_with_fault_tolerance(
        self,
        provider: SearchProvider,
        func: Callable,
        query: SearchQuery,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with comprehensive fault tolerance."""
        circuit_breaker = self.get_circuit_breaker(provider)
        
        for attempt in range(1, self.retry_policy.max_attempts + 1):
            try:
                result = await circuit_breaker.call(func, *args, **kwargs)
                return result
                
            except Exception as e:
                context = {
                    'provider': provider,
                    'query': query.text,
                    'attempt': attempt,
                    'max_attempts': self.retry_policy.max_attempts
                }
                
                error_info = self.error_classifier.classify_error(e, context)
                error_info.retry_count = attempt - 1
                self.error_history.append(error_info)
                
                # Log error
                logger.warning(f"Search attempt {attempt} failed for {provider}: {e}")
                
                # Check if we should retry
                if not self.retry_policy.should_retry(error_info, attempt):
                    break
                
                # Wait before retry
                delay = self.retry_policy.get_delay(attempt)
                await asyncio.sleep(delay)
        
        # All attempts failed, try fallback providers
        return await self._try_fallback_providers(provider, func, query, *args, **kwargs)
    
    async def _try_fallback_providers(
        self,
        failed_provider: SearchProvider,
        func: Callable,
        query: SearchQuery,
        *args,
        **kwargs
    ) -> Any:
        """Try fallback providers when primary fails."""
        fallbacks = self.fallback_providers.get(failed_provider, [])
        
        for fallback_provider in fallbacks:
            logger.info(f"Trying fallback provider: {fallback_provider}")
            
            try:
                circuit_breaker = self.get_circuit_breaker(fallback_provider)
                result = await circuit_breaker.call(func, *args, **kwargs)
                
                # Log successful fallback
                logger.info(f"Fallback to {fallback_provider} succeeded")
                return result
                
            except Exception as e:
                logger.warning(f"Fallback provider {fallback_provider} also failed: {e}")
                continue
        
        # All fallbacks failed
        raise Exception(f"All providers failed for query: {query.text}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        if not self.error_history:
            return {}
        
        # Count errors by type and severity
        error_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        provider_errors = defaultdict(int)
        
        recent_errors = [
            error for error in self.error_history
            if (datetime.now() - error.timestamp).total_seconds() <= 3600  # Last hour
        ]
        
        for error in recent_errors:
            error_counts[error.error_type.value] += 1
            severity_counts[error.severity.value] += 1
            if error.provider:
                provider_errors[error.provider.value] += 1
        
        # Circuit breaker stats
        circuit_stats = {}
        for provider, breaker in self.circuit_breakers.items():
            circuit_stats[provider.value] = breaker.get_stats()
        
        return {
            'total_errors': len(recent_errors),
            'error_types': dict(error_counts),
            'severity_distribution': dict(severity_counts),
            'provider_errors': dict(provider_errors),
            'circuit_breakers': circuit_stats,
            'error_rate': len(recent_errors) / 3600  # Errors per second
        }
    
    def clear_error_history(self, older_than_hours: int = 24):
        """Clear old error history."""
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        self.error_history = [
            error for error in self.error_history
            if error.timestamp > cutoff_time
        ]


class HealthChecker:
    """Health checking for search providers and system components."""
    
    def __init__(self):
        self.health_status: Dict[str, Dict[str, Any]] = {}
        self.last_check_time: Optional[datetime] = None
        
    async def check_provider_health(self, provider: SearchProvider) -> Dict[str, Any]:
        """Check health of a specific provider."""
        health_info = {
            'provider': provider.value,
            'status': 'unknown',
            'response_time_ms': 0,
            'error_message': None,
            'last_check': datetime.now().isoformat(),
            'consecutive_failures': 0,
            'last_success_time': None
        }
        
        try:
            # This would be implemented by each provider
            # For now, simulate health check
            start_time = time.time()
            
            # Simulate health check
            await asyncio.sleep(0.1)
            
            response_time = (time.time() - start_time) * 1000
            
            health_info.update({
                'status': 'healthy',
                'response_time_ms': response_time,
                'last_success_time': datetime.now().isoformat()
            })
            
        except Exception as e:
            health_info.update({
                'status': 'unhealthy',
                'error_message': str(e)
            })
        
        self.health_status[provider.value] = health_info
        return health_info
    
    async def check_all_providers_health(self, providers: List[SearchProvider]) -> Dict[str, Dict[str, Any]]:
        """Check health of all providers."""
        tasks = [self.check_provider_health(provider) for provider in providers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_report = {}
        for i, provider in enumerate(providers):
            if isinstance(results[i], Exception):
                health_report[provider.value] = {
                    'provider': provider.value,
                    'status': 'error',
                    'error_message': str(results[i]),
                    'last_check': datetime.now().isoformat()
                }
            else:
                health_report[provider.value] = results[i]
        
        self.last_check_time = datetime.now()
        return health_report
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health."""
        if not self.health_status:
            return {
                'status': 'unknown',
                'message': 'No health data available',
                'last_check': None
            }
        
        healthy_count = sum(1 for info in self.health_status.values() if info['status'] == 'healthy')
        total_count = len(self.health_status)
        
        if healthy_count == total_count:
            system_status = 'healthy'
        elif healthy_count > 0:
            system_status = 'degraded'
        else:
            system_status = 'unhealthy'
        
        return {
            'status': system_status,
            'healthy_providers': healthy_count,
            'total_providers': total_count,
            'health_percentage': (healthy_count / total_count) * 100 if total_count > 0 else 0,
            'last_check': self.last_check_time.isoformat() if self.last_check_time else None,
            'provider_details': self.health_status
        }


# Global fault tolerance components
fault_executor = FaultTolerantExecutor()
health_checker = HealthChecker()
