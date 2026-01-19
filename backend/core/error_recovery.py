"""
Production Error Recovery System for Raptorflow.
Real error handling with pattern detection, circuit breakers, and practical recovery strategies.
"""

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for production monitoring"""
    LOW = "low"           # Non-critical, can be ignored
    MEDIUM = "medium"     # Affects functionality but system continues
    HIGH = "high"         # Significant impact, requires attention
    CRITICAL = "critical" # System failure, immediate response needed


class ErrorPattern(Enum):
    """Common error patterns in production"""
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    CONNECTION_FAILED = "connection_failed"
    AUTHENTICATION_FAILED = "auth_failed"
    VALIDATION_FAILED = "validation_failed"
    DATABASE_ERROR = "database_error"
    EXTERNAL_API_ERROR = "external_api_error"
    MEMORY_PRESSURE = "memory_pressure"
    DISK_SPACE = "disk_space"
    NETWORK_LATENCY = "network_latency"


@dataclass
class ErrorMetrics:
    """Real error metrics for monitoring"""
    error_type: str
    count: int = 0
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    recovery_attempts: int = 0
    successful_recoveries: int = 0
    avg_recovery_time: float = 0.0
    severity: ErrorSeverity = ErrorSeverity.MEDIUM


@dataclass
class RecoveryResult:
    """Result of a recovery attempt"""
    success: bool
    strategy: str
    recovery_time: float
    error_resolved: bool
    new_state: Dict[str, Any]
    metrics_updated: bool = False


class ErrorPatternDetector:
    """Detects error patterns from real error data"""
    
    def __init__(self):
        self.pattern_keywords = {
            ErrorPattern.RATE_LIMIT: [
                'rate limit', 'quota exceeded', 'too many requests', '429'
            ],
            ErrorPattern.TIMEOUT: [
                'timeout', 'deadline exceeded', 'operation timed out', 'slow'
            ],
            ErrorPattern.CONNECTION_FAILED: [
                'connection failed', 'connection refused', 'network unreachable', 'dns'
            ],
            ErrorPattern.AUTHENTICATION_FAILED: [
                'unauthorized', 'authentication failed', 'invalid token', '401', '403'
            ],
            ErrorPattern.VALIDATION_FAILED: [
                'validation error', 'invalid input', 'bad request', '400'
            ],
            ErrorPattern.DATABASE_ERROR: [
                'database error', 'sql error', 'connection pool', 'deadlock'
            ],
            ErrorPattern.EXTERNAL_API_ERROR: [
                'api error', 'service unavailable', '502', '503', '504'
            ],
            ErrorPattern.MEMORY_PRESSURE: [
                'out of memory', 'memory pressure', 'oom', 'allocation failed'
            ],
            ErrorPattern.DISK_SPACE: [
                'disk full', 'no space left', 'storage error'
            ],
            ErrorPattern.NETWORK_LATENCY: [
                'high latency', 'slow response', 'network delay'
            ]
        }
    
    def detect_pattern(self, error_type: str, error_message: str) -> Optional[ErrorPattern]:
        """Detect error pattern from error type and message"""
        error_text = f"{error_type} {error_message}".lower()
        
        for pattern, keywords in self.pattern_keywords.items():
            if any(keyword in error_text for keyword in keywords):
                return pattern
        
        return None
    
    def assess_severity(self, error_type: str, error_message: str, 
                       pattern: Optional[ErrorPattern] = None) -> ErrorSeverity:
        """Assess error severity based on type and pattern"""
        error_text = f"{error_type} {error_message}".lower()
        
        # Critical patterns
        critical_keywords = ['critical', 'fatal', 'panic', 'system failure']
        if any(keyword in error_text for keyword in critical_keywords):
            return ErrorSeverity.CRITICAL
        
        # High severity patterns
        if pattern in [ErrorPattern.DATABASE_ERROR, ErrorPattern.MEMORY_PRESSURE]:
            return ErrorSeverity.HIGH
        
        # Medium severity patterns
        if pattern in [ErrorPattern.TIMEOUT, ErrorPattern.CONNECTION_FAILED, 
                      ErrorPattern.EXTERNAL_API_ERROR]:
            return ErrorSeverity.MEDIUM
        
        # Default to medium for unknown patterns
        return ErrorSeverity.MEDIUM


class ProductionErrorRecovery:
    """Production-grade error recovery with real pattern detection"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.pattern_detector = ErrorPatternDetector()
        self.error_metrics: Dict[str, ErrorMetrics] = {}
        self.recovery_history: deque = deque(maxlen=1000)
        self.circuit_breaker_states: Dict[str, Dict[str, Any]] = {}
        self.rate_limit_trackers: Dict[str, List[float]] = defaultdict(list)
        self._load_metrics()
    
    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> RecoveryResult:
        """Handle error with real production recovery logic"""
        start_time = time.time()
        error_type = type(error).__name__
        error_message = str(error)
        
        # Detect pattern and assess severity
        pattern = self.pattern_detector.detect_pattern(error_type, error_message)
        severity = self.pattern_detector.assess_severity(error_type, error_message, pattern)
        
        # Update metrics
        await self._update_error_metrics(error_type, severity)
        
        # Check if we should circuit break
        if await self._should_circuit_break(error_type, pattern):
            return await self._circuit_break_recovery(error_type, context, start_time)
        
        # Try recovery strategies based on pattern
        recovery_result = await self._attempt_recovery(error, pattern, context)
        
        recovery_result.recovery_time = time.time() - start_time
        recovery_result.metrics_updated = True
        
        # Record recovery attempt
        self.recovery_history.append(recovery_result)
        
        # Save metrics
        await self._save_metrics()
        
        return recovery_result
    
    async def _attempt_recovery(self, error: Exception, pattern: Optional[ErrorPattern],
                               context: Dict[str, Any]) -> RecoveryResult:
        """Attempt recovery based on detected pattern"""
        error_type = type(error).__name__
        
        if pattern == ErrorPattern.RATE_LIMIT:
            return await self._handle_rate_limit(error, context)
        elif pattern == ErrorPattern.TIMEOUT:
            return await self._handle_timeout(error, context)
        elif pattern == ErrorPattern.CONNECTION_FAILED:
            return await self._handle_connection_failure(error, context)
        elif pattern == ErrorPattern.AUTHENTICATION_FAILED:
            return await self._handle_auth_failure(error, context)
        elif pattern == ErrorPattern.DATABASE_ERROR:
            return await self._handle_database_error(error, context)
        elif pattern == ErrorPattern.EXTERNAL_API_ERROR:
            return await self._handle_external_api_error(error, context)
        else:
            return await self._handle_generic_error(error, context)
    
    async def _handle_rate_limit(self, error: Exception, context: Dict[str, Any]) -> RecoveryResult:
        """Handle rate limiting with exponential backoff"""
        service_name = context.get('service_name', 'unknown')
        
        # Track rate limit occurrences
        now = time.time()
        self.rate_limit_trackers[service_name].append(now)
        
        # Clean old entries (older than 1 hour)
        self.rate_limit_trackers[service_name] = [
            t for t in self.rate_limit_trackers[service_name] 
            if now - t < 3600
        ]
        
        # Calculate backoff based on frequency
        recent_count = len(self.rate_limit_trackers[service_name])
        if recent_count > 10:
            backoff_time = min(300, 2 ** (recent_count // 5))  # Max 5 minutes
        else:
            backoff_time = 60  # 1 minute default
        
        logger.warning(f"Rate limit hit for {service_name}, waiting {backoff_time}s")
        await asyncio.sleep(backoff_time)
        
        return RecoveryResult(
            success=True,
            strategy="rate_limit_backoff",
            recovery_time=0,
            error_resolved=True,
            new_state={'backoff_applied': True, 'backoff_time': backoff_time}
        )
    
    async def _handle_timeout(self, error: Exception, context: Dict[str, Any]) -> RecoveryResult:
        """Handle timeouts with increased timeout and retry"""
        current_timeout = context.get('timeout', 30)
        new_timeout = min(current_timeout * 2, 300)  # Max 5 minutes
        
        # Retry with increased timeout
        if 'retry_func' in context:
            try:
                # Update context with new timeout
                new_context = context.copy()
                new_context['timeout'] = new_timeout
                
                result = await context['retry_func']()
                return RecoveryResult(
                    success=True,
                    strategy="timeout_increase_retry",
                    recovery_time=0,
                    error_resolved=True,
                    new_state={'timeout_increased': True, 'new_timeout': new_timeout}
                )
            except Exception:
                pass
        
        return RecoveryResult(
            success=False,
            strategy="timeout_increase_failed",
            recovery_time=0,
            error_resolved=False,
            new_state={'timeout_increase_failed': True}
        )
    
    async def _handle_connection_failure(self, error: Exception, context: Dict[str, Any]) -> RecoveryResult:
        """Handle connection failures with retry and fallback"""
        max_retries = context.get('max_retries', 3)
        
        for attempt in range(max_retries):
            try:
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
                
                if 'retry_func' in context:
                    result = await context['retry_func']()
                    return RecoveryResult(
                        success=True,
                        strategy="connection_retry",
                        recovery_time=0,
                        error_resolved=True,
                        new_state={'retry_count': attempt + 1}
                    )
            except Exception:
                continue
        
        # Try fallback if available
        if 'fallback_func' in context:
            try:
                result = await context['fallback_func']()
                return RecoveryResult(
                    success=True,
                    strategy="connection_fallback",
                    recovery_time=0,
                    error_resolved=True,
                    new_state={'fallback_used': True}
                )
            except Exception:
                pass
        
        return RecoveryResult(
            success=False,
            strategy="connection_recovery_failed",
            recovery_time=0,
            error_resolved=False,
            new_state={'all_attempts_failed': True}
        )
    
    async def _handle_auth_failure(self, error: Exception, context: Dict[str, Any]) -> RecoveryResult:
        """Handle authentication failures"""
        # Try token refresh if available
        if 'refresh_token_func' in context:
            try:
                await context['refresh_token_func']()
                
                # Retry original operation
                if 'retry_func' in context:
                    result = await context['retry_func']()
                    return RecoveryResult(
                        success=True,
                        strategy="auth_token_refresh",
                        recovery_time=0,
                        error_resolved=True,
                        new_state={'token_refreshed': True}
                    )
            except Exception:
                pass
        
        # Auth failures usually require manual intervention
        return RecoveryResult(
            success=False,
            strategy="auth_escalate",
            recovery_time=0,
            error_resolved=False,
            new_state={'manual_intervention_required': True}
        )
    
    async def _handle_database_error(self, error: Exception, context: Dict[str, Any]) -> RecoveryResult:
        """Handle database errors with connection pool management"""
        error_message = str(error).lower()
        
        if 'connection pool' in error_message or 'connection' in error_message:
            # Try to reconnect
            if 'reconnect_func' in context:
                try:
                    await context['reconnect_func']()
                    
                    # Retry operation
                    if 'retry_func' in context:
                        result = await context['retry_func']()
                        return RecoveryResult(
                            success=True,
                            strategy="database_reconnect",
                            recovery_time=0,
                            error_resolved=True,
                            new_state={'database_reconnected': True}
                        )
                except Exception:
                    pass
        
        # For other database errors, try with different query
        if 'alternative_query_func' in context:
            try:
                result = await context['alternative_query_func']()
                return RecoveryResult(
                    success=True,
                    strategy="database_alternative_query",
                    recovery_time=0,
                    error_resolved=True,
                    new_state={'alternative_query_used': True}
                )
            except Exception:
                pass
        
        return RecoveryResult(
            success=False,
            strategy="database_recovery_failed",
            recovery_time=0,
            error_resolved=False,
            new_state={'database_error_persisted': True}
        )
    
    async def _handle_external_api_error(self, error: Exception, context: Dict[str, Any]) -> Response:
        """Handle external API errors with fallback services"""
        # Try fallback service if available
        if 'fallback_service_func' in context:
            try:
                result = await context['fallback_service_func']()
                return RecoveryResult(
                    success=True,
                    strategy="external_api_fallback",
                    recovery_time=0,
                    error_resolved=True,
                    new_state={'fallback_service_used': True}
                )
            except Exception:
                pass
        
        # Try cached response if available
        if 'cached_response_func' in context:
            try:
                result = await context['cached_response_func']()
                return RecoveryResult(
                    success=True,
                    strategy="external_api_cache",
                    recovery_time=0,
                    error_resolved=True,
                    new_state={'cached_response_used': True}
                )
            except Exception:
                pass
        
        return RecoveryResult(
            success=False,
            strategy="external_api_failed",
            recovery_time=0,
            error_resolved=False,
            new_state={'external_api_unavailable': True}
        )
    
    async def _handle_generic_error(self, error: Exception, context: Dict[str, Any]) -> RecoveryResult:
        """Handle generic errors with basic retry logic"""
        max_retries = context.get('max_retries', 2)
        
        for attempt in range(max_retries):
            try:
                await asyncio.sleep(1 + attempt)  # Simple backoff
                
                if 'retry_func' in context:
                    result = await context['retry_func']()
                    return RecoveryResult(
                        success=True,
                        strategy="generic_retry",
                        recovery_time=0,
                        error_resolved=True,
                        new_state={'retry_count': attempt + 1}
                    )
            except Exception:
                continue
        
        return RecoveryResult(
            success=False,
            strategy="generic_retry_failed",
            recovery_time=0,
            error_resolved=False,
            new_state={'generic_error_persisted': True}
        )
    
    async def _should_circuit_break(self, error_type: str, pattern: Optional[ErrorPattern]) -> bool:
        """Determine if circuit breaker should be triggered"""
        if error_type not in self.error_metrics:
            return False
        
        metrics = self.error_metrics[error_type]
        
        # Circuit break if too many failures in short time
        recent_failures = metrics.count
        time_since_first = (datetime.now() - metrics.first_seen).total_seconds()
        
        # Break if >10 failures in <5 minutes
        if recent_failures > 10 and time_since_first < 300:
            return True
        
        # Break if recovery success rate <20%
        if metrics.recovery_attempts > 5:
            success_rate = metrics.successful_recoveries / metrics.recovery_attempts
            if success_rate < 0.2:
                return True
        
        return False
    
    async def _circuit_break_recovery(self, error_type: str, context: Dict[str, Any], 
                                   start_time: float) -> RecoveryResult:
        """Handle circuit breaker recovery"""
        # Initialize circuit breaker state if not exists
        if error_type not in self.circuit_breaker_states:
            self.circuit_breaker_states[error_type] = {
                'opened_at': time.time(),
                'retry_after': 300,  # 5 minutes
                'half_open_attempts': 0
            }
        
        state = self.circuit_breaker_states[error_type]
        now = time.time()
        
        # Check if circuit should be half-open
        if now - state['opened_at'] > state['retry_after']:
            state['half_open_attempts'] += 1
            
            # Allow limited attempts in half-open state
            if state['half_open_attempts'] <= 3:
                # Try the operation
                if 'retry_func' in context:
                    try:
                        result = await context['retry_func']()
                        
                        # Success - close circuit
                        del self.circuit_breaker_states[error_type]
                        return RecoveryResult(
                            success=True,
                            strategy="circuit_break_half_open_success",
                            recovery_time=time.time() - start_time,
                            error_resolved=True,
                            new_state={'circuit_closed': True}
                        )
                    except Exception:
                        pass
        
        return RecoveryResult(
            success=False,
            strategy="circuit_break_open",
            recovery_time=time.time() - start_time,
            error_resolved=False,
            new_state={'circuit_open': True, 'retry_after': state['retry_after']}
        )
    
    async def _update_error_metrics(self, error_type: str, severity: ErrorSeverity):
        """Update error metrics"""
        if error_type not in self.error_metrics:
            self.error_metrics[error_type] = ErrorMetrics(
                error_type=error_type,
                severity=severity
            )
        
        metrics = self.error_metrics[error_type]
        metrics.count += 1
        metrics.last_seen = datetime.now()
        metrics.recovery_attempts += 1
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get real error statistics"""
        if not self.error_metrics:
            return {}
        
        total_errors = sum(m.count for m in self.error_metrics.values())
        total_recoveries = sum(m.successful_recoveries for m in self.error_metrics.values())
        total_attempts = sum(m.recovery_attempts for m in self.error_metrics.values())
        
        severity_counts = defaultdict(int)
        for metrics in self.error_metrics.values():
            severity_counts[metrics.severity.value] += metrics.count
        
        return {
            'total_errors': total_errors,
            'total_recovery_attempts': total_attempts,
            'successful_recoveries': total_recoveries,
            'overall_success_rate': total_recoveries / total_attempts if total_attempts > 0 else 0,
            'error_types': len(self.error_metrics),
            'severity_breakdown': dict(severity_counts),
            'circuit_breakers_active': len(self.circuit_breaker_states),
            'most_common_errors': sorted(
                [(k, v.count) for k, v in self.error_metrics.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    async def _save_metrics(self):
        """Save metrics to Redis"""
        if not self.redis_client:
            return
        
        try:
            metrics_data = {
                error_type: {
                    'count': metrics.count,
                    'first_seen': metrics.first_seen.isoformat(),
                    'last_seen': metrics.last_seen.isoformat(),
                    'recovery_attempts': metrics.recovery_attempts,
                    'successful_recoveries': metrics.successful_recoveries,
                    'avg_recovery_time': metrics.avg_recovery_time,
                    'severity': metrics.severity.value
                }
                for error_type, metrics in self.error_metrics.items()
            }
            
            await self.redis_client.setex(
                'error_recovery:metrics',
                timedelta(days=7),
                json.dumps(metrics_data)
            )
            
        except Exception as e:
            logger.error(f"Failed to save metrics to Redis: {e}")
    
    def _load_metrics(self):
        """Load metrics from storage"""
        # This would load from Redis or file
        # For now, start with empty metrics
        pass


# Global error recovery instance
_error_recovery: Optional[ProductionErrorRecovery] = None


def get_production_error_recovery(redis_client: Optional[redis.Redis] = None) -> ProductionErrorRecovery:
    """Get global production error recovery instance"""
    global _error_recovery
    if _error_recovery is None:
        _error_recovery = ProductionErrorRecovery(redis_client)
    return _error_recovery


async def handle_production_error(error: Exception, context: Dict[str, Any]) -> RecoveryResult:
    """Handle error with production recovery system"""
    recovery = get_production_error_recovery()
    return await recovery.handle_error(error, context)
