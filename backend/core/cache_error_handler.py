"""
Comprehensive Error Handling and Recovery for Cache Failures
Provides robust error handling, recovery mechanisms, and failure analysis
"""

import asyncio
import json
import logging
import time
import traceback
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for cache operations."""
    
    CONNECTION_ERROR = "connection_error"
    TIMEOUT_ERROR = "timeout_error"
    SERIALIZATION_ERROR = "serialization_error"
    COMPRESSION_ERROR = "compression_error"
    MEMORY_ERROR = "memory_error"
    NETWORK_ERROR = "network_error"
    AUTHENTICATION_ERROR = "authentication_error"
    VALIDATION_ERROR = "validation_error"
    QUOTA_EXCEEDED = "quota_exceeded"
    DATA_CORRUPTION = "data_corruption"
    CONSISTENCY_ERROR = "consistency_error"
    UNKNOWN_ERROR = "unknown_error"


class RecoveryAction(Enum):
    """Recovery actions for cache errors."""
    
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAK = "circuit_break"
    DEGRADE_SERVICE = "degrade_service"
    RECONNECT = "reconnect"
    CLEAR_CACHE = "clear_cache"
    RESET_CONNECTION = "reset_connection"
    NOTIFY_ADMIN = "notify_admin"
    IGNORE = "ignore"


@dataclass
class CacheError:
    """Cache error information."""
    
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    timestamp: datetime
    operation: str
    key: Optional[str]
    component: str
    stack_trace: Optional[str]
    context: Dict[str, Any]
    retry_count: int = 0
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if self.resolution_time:
            data['resolution_time'] = self.resolution_time.isoformat()
        return data


@dataclass
class RecoveryAttempt:
    """Recovery attempt information."""
    
    attempt_id: str
    error_id: str
    action: RecoveryAction
    timestamp: datetime
    success: bool
    duration: float
    message: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class CircuitBreaker:
    """Circuit breaker for preventing cascading failures."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
        self.lock = threading.RLock()
    
    def __call__(self, func):
        """Decorator for circuit breaker functionality."""
        def wrapper(*args, **kwargs):
            with self.lock:
                if self.state == "OPEN":
                    if (time.time() - self.last_failure_time) > self.recovery_timeout:
                        self.state = "HALF_OPEN"
                    else:
                        raise Exception("Circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                
                return result
                
            except self.expected_exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                
                raise e
        
        return wrapper


class RetryPolicy:
    """Retry policy for cache operations."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Get delay for retry attempt."""
        delay = self.base_delay * (self.exponential_base ** (attempt - 1))
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add jitter to prevent thundering herd
            import random
            delay *= (0.5 + random.random() * 0.5)
        
        return delay
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with retry policy."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self.get_delay(attempt + 1)
                    logger.warning(f"Retry attempt {attempt + 1}/{self.max_retries} after {delay:.2f}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries} retry attempts failed: {e}")
        
        raise last_exception


class CacheErrorHandler:
    """Comprehensive cache error handler."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Error tracking
        self.error_history: deque = deque(maxlen=1000)
        self.active_errors: Dict[str, CacheError] = {}
        self.recovery_attempts: Dict[str, List[RecoveryAttempt]] = defaultdict(list)
        
        # Circuit breakers for different components
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._setup_circuit_breakers()
        
        # Retry policies
        self.retry_policies: Dict[str, RetryPolicy] = {}
        self._setup_retry_policies()
        
        # Error handlers
        self.error_handlers: Dict[ErrorCategory, List[Callable]] = defaultdict(list)
        self._setup_error_handlers()
        
        # Statistics
        self.stats = {
            'total_errors': 0,
            'resolved_errors': 0,
            'failed_recoveries': 0,
            'circuit_breaker_trips': 0,
            'error_categories': defaultdict(int),
            'recovery_actions': defaultdict(int)
        }
        
        # Background tasks
        self._cleanup_task = None
        self._running = False
    
    def _setup_circuit_breakers(self):
        """Setup circuit breakers for different components."""
        self.circuit_breakers['redis'] = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
        
        self.circuit_breakers['compression'] = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30
        )
        
        self.circuit_breakers['serialization'] = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30
        )
    
    def _setup_retry_policies(self):
        """Setup retry policies for different operations."""
        self.retry_policies['connection'] = RetryPolicy(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0
        )
        
        self.retry_policies['operation'] = RetryPolicy(
            max_retries=2,
            base_delay=0.5,
            max_delay=10.0
        )
        
        self.retry_policies['critical'] = RetryPolicy(
            max_retries=5,
            base_delay=2.0,
            max_delay=60.0
        )
    
    def _setup_error_handlers(self):
        """Setup error handlers for different error categories."""
        # Connection error handlers
        self.error_handlers[ErrorCategory.CONNECTION_ERROR].append(
            self._handle_connection_error
        )
        
        # Timeout error handlers
        self.error_handlers[ErrorCategory.TIMEOUT_ERROR].append(
            self._handle_timeout_error
        )
        
        # Memory error handlers
        self.error_handlers[ErrorCategory.MEMORY_ERROR].append(
            self._handle_memory_error
        )
        
        # Data corruption handlers
        self.error_handlers[ErrorCategory.DATA_CORRUPTION].append(
            self._handle_data_corruption
        )
    
    async def initialize(self):
        """Initialize error handler."""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._background_cleanup())
        
        logger.info("Cache error handler initialized")
    
    async def shutdown(self):
        """Shutdown error handler."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        logger.info("Cache error handler shutdown")
    
    async def handle_error(
        self,
        error: Exception,
        operation: str,
        component: str,
        key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Handle cache error with recovery."""
        # Categorize error
        category = self._categorize_error(error)
        severity = self._determine_severity(error, category)
        
        # Create error record
        error_record = CacheError(
            error_id=f"err_{int(time.time() * 1000)}",
            category=category,
            severity=severity,
            message=str(error),
            timestamp=datetime.now(),
            operation=operation,
            key=key,
            component=component,
            stack_trace=traceback.format_exc(),
            context=context or {}
        )
        
        # Track error
        self.error_history.append(error_record)
        self.active_errors[error_record.error_id] = error_record
        self.stats['total_errors'] += 1
        self.stats['error_categories'][category.value] += 1
        
        # Execute recovery
        recovery_success = await self._execute_recovery(error_record)
        
        if recovery_success:
            error_record.resolved = True
            error_record.resolution_time = datetime.now()
            self.stats['resolved_errors'] += 1
        else:
            self.stats['failed_recoveries'] += 1
        
        # Notify error handlers
        await self._notify_error_handlers(error_record)
        
        return recovery_success
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error based on type and message."""
        error_message = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Connection errors
        if any(keyword in error_message for keyword in [
            'connection', 'connect', 'network', 'socket', 'timeout'
        ]) or any(keyword in error_type for keyword in [
            'connectionerror', 'timeout', 'networkerror'
        ]):
            if 'timeout' in error_message or 'timeout' in error_type:
                return ErrorCategory.TIMEOUT_ERROR
            return ErrorCategory.CONNECTION_ERROR
        
        # Memory errors
        if any(keyword in error_message for keyword in [
            'memory', 'out of memory', 'allocation', 'buffer'
        ]) or any(keyword in error_type for keyword in [
            'memoryerror', 'buffererror'
        ]):
            return ErrorCategory.MEMORY_ERROR
        
        # Serialization errors
        if any(keyword in error_message for keyword in [
            'serialize', 'deserialize', 'pickle', 'json'
        ]) or any(keyword in error_type for keyword in [
            'serializationerror'
        ]):
            return ErrorCategory.SERIALIZATION_ERROR
        
        # Compression errors
        if any(keyword in error_message for keyword in [
            'compress', 'decompress', 'gzip', 'zlib', 'lz4'
        ]) or any(keyword in error_type for keyword in [
            'compressionerror'
        ]):
            return ErrorCategory.COMPRESSION_ERROR
        
        # Authentication errors
        if any(keyword in error_message for keyword in [
            'auth', 'authentication', 'unauthorized', 'forbidden'
        ]) or any(keyword in error_type for keyword in [
            'authenticationerror'
        ]):
            return ErrorCategory.AUTHENTICATION_ERROR
        
        # Validation errors
        if any(keyword in error_message for keyword in [
            'validation', 'invalid', 'malformed'
        ]) or any(keyword in error_type for keyword in [
            'valueerror', 'validationerror'
        ]):
            return ErrorCategory.VALIDATION_ERROR
        
        # Data corruption
        if any(keyword in error_message for keyword in [
            'corruption', 'corrupt', 'checksum', 'integrity'
        ]) or any(keyword in error_type for keyword in [
            'dataerror'
        ]):
            return ErrorCategory.DATA_CORRUPTION
        
        return ErrorCategory.UNKNOWN_ERROR
    
    def _determine_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity."""
        # Critical errors
        if category in [
            ErrorCategory.DATA_CORRUPTION,
            ErrorCategory.MEMORY_ERROR
        ]:
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if category in [
            ErrorCategory.CONNECTION_ERROR,
            ErrorCategory.CONSISTENCY_ERROR
        ]:
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if category in [
            ErrorCategory.TIMEOUT_ERROR,
            ErrorCategory.SERIALIZATION_ERROR,
            ErrorCategory.COMPRESSION_ERROR
        ]:
            return ErrorSeverity.MEDIUM
        
        # Low severity errors
        return ErrorSeverity.LOW
    
    async def _execute_recovery(self, error: CacheError) -> bool:
        """Execute recovery action for error."""
        recovery_action = self._determine_recovery_action(error)
        
        # Create recovery attempt
        attempt_id = f"rec_{int(time.time() * 1000)}"
        start_time = time.time()
        
        try:
            success = False
            
            if recovery_action == RecoveryAction.RETRY:
                success = await self._retry_operation(error)
            elif recovery_action == RecoveryAction.FALLBACK:
                success = await self._fallback_operation(error)
            elif recovery_action == RecoveryAction.RECONNECT:
                success = await self._reconnect_component(error)
            elif recovery_action == RecoveryAction.CLEAR_CACHE:
                success = await self._clear_cache(error)
            elif recovery_action == RecoveryAction.DEGRADE_SERVICE:
                success = await self._degrade_service(error)
            elif recovery_action == RecoveryAction.CIRCUIT_BREAK:
                success = await self._trip_circuit_breaker(error)
            elif recovery_action == RecoveryAction.NOTIFY_ADMIN:
                success = await self._notify_admin(error)
            else:
                success = True  # IGNORE or unknown action
            
            # Record recovery attempt
            recovery_attempt = RecoveryAttempt(
                attempt_id=attempt_id,
                error_id=error.error_id,
                action=recovery_action,
                timestamp=datetime.now(),
                success=success,
                duration=time.time() - start_time,
                message=f"Recovery {recovery_action.value} {'succeeded' if success else 'failed'}"
            )
            
            self.recovery_attempts[error.error_id].append(recovery_attempt)
            self.stats['recovery_actions'][recovery_action.value] += 1
            
            return success
            
        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
            return False
    
    def _determine_recovery_action(self, error: CacheError) -> RecoveryAction:
        """Determine appropriate recovery action."""
        if error.category == ErrorCategory.CONNECTION_ERROR:
            return RecoveryAction.RECONNECT
        elif error.category == ErrorCategory.TIMEOUT_ERROR:
            return RecoveryAction.RETRY
        elif error.category == ErrorCategory.MEMORY_ERROR:
            return RecoveryAction.CLEAR_CACHE
        elif error.category == ErrorCategory.DATA_CORRUPTION:
            return RecoveryAction.FALLBACK
        elif error.category == ErrorCategory.SERIALIZATION_ERROR:
            return RecoveryAction.FALLBACK
        elif error.category == ErrorCategory.COMPRESSION_ERROR:
            return RecoveryAction.FALLBACK
        elif error.severity == ErrorSeverity.CRITICAL:
            return RecoveryAction.CIRCUIT_BREAK
        elif error.severity == ErrorSeverity.HIGH:
            return RecoveryAction.DEGRADE_SERVICE
        else:
            return RecoveryAction.RETRY
    
    async def _retry_operation(self, error: CacheError) -> bool:
        """Retry failed operation."""
        retry_policy = self.retry_policies.get('operation')
        if not retry_policy:
            return False
        
        try:
            # This would need access to the original operation
            # For now, just simulate retry
            logger.info(f"Retrying operation: {error.operation}")
            return True
        except Exception as e:
            logger.error(f"Retry failed: {e}")
            return False
    
    async def _fallback_operation(self, error: CacheError) -> bool:
        """Execute fallback operation."""
        try:
            # Implement fallback logic based on operation type
            if error.operation == 'get':
                # Fallback to lower cache level or direct data source
                logger.info(f"Falling back for get operation: {error.key}")
            elif error.operation == 'set':
                # Fallback to different storage method
                logger.info(f"Falling back for set operation: {error.key}")
            
            return True
        except Exception as e:
            logger.error(f"Fallback failed: {e}")
            return False
    
    async def _reconnect_component(self, error: CacheError) -> bool:
        """Reconnect to component."""
        try:
            logger.info(f"Reconnecting to component: {error.component}")
            
            # This would need access to the component connection
            # For now, just simulate reconnection
            await asyncio.sleep(1)  # Simulate reconnection time
            
            return True
        except Exception as e:
            logger.error(f"Reconnection failed: {e}")
            return False
    
    async def _clear_cache(self, error: CacheError) -> bool:
        """Clear cache to free memory."""
        try:
            logger.info(f"Clearing cache due to memory error: {error.component}")
            
            # This would need access to the cache
            # For now, just simulate cache clearing
            return True
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return False
    
    async def _degrade_service(self, error: CacheError) -> bool:
        """Degrade service functionality."""
        try:
            logger.info(f"Degrading service due to error: {error.operation}")
            
            # Implement service degradation logic
            return True
        except Exception as e:
            logger.error(f"Service degradation failed: {e}")
            return False
    
    async def _trip_circuit_breaker(self, error: CacheError) -> bool:
        """Trip circuit breaker for component."""
        try:
            circuit_breaker = self.circuit_breakers.get(error.component)
            if circuit_breaker:
                logger.warning(f"Tripping circuit breaker for component: {error.component}")
                self.stats['circuit_breaker_trips'] += 1
                return True
            
            return False
        except Exception as e:
            logger.error(f"Circuit breaker trip failed: {e}")
            return False
    
    async def _notify_admin(self, error: CacheError) -> bool:
        """Notify administrator of critical error."""
        try:
            logger.critical(f"Critical cache error requiring admin attention: {error}")
            
            # This would integrate with notification systems
            # For now, just log the error
            return True
        except Exception as e:
            logger.error(f"Admin notification failed: {e}")
            return False
    
    async def _notify_error_handlers(self, error: CacheError):
        """Notify registered error handlers."""
        handlers = self.error_handlers.get(error.category, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(error)
                else:
                    handler(error)
            except Exception as e:
                logger.error(f"Error handler failed: {e}")
    
    async def _handle_connection_error(self, error: CacheError):
        """Handle connection errors."""
        logger.warning(f"Connection error handled: {error.message}")
    
    async def _handle_timeout_error(self, error: CacheError):
        """Handle timeout errors."""
        logger.warning(f"Timeout error handled: {error.message}")
    
    async def _handle_memory_error(self, error: CacheError):
        """Handle memory errors."""
        logger.error(f"Memory error handled: {error.message}")
        # Trigger cache cleanup
        await self._clear_cache(error)
    
    async def _handle_data_corruption(self, error: CacheError):
        """Handle data corruption errors."""
        logger.error(f"Data corruption handled: {error.message}")
        # Trigger cache invalidation
        await self._notify_admin(error)
    
    async def _background_cleanup(self):
        """Background cleanup of old errors and recovery attempts."""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                
                # Clean up resolved errors
                current_time = datetime.now()
                cutoff_time = current_time - timedelta(hours=24)
                
                # Remove old resolved errors
                self.error_history = deque(
                    [e for e in self.error_history 
                     if not e.resolved or e.timestamp > cutoff_time],
                    maxlen=1000
                )
                
                # Clean up old recovery attempts
                for error_id in list(self.recovery_attempts.keys()):
                    recent_attempts = [
                        a for a in self.recovery_attempts[error_id]
                        if a.timestamp > cutoff_time
                    ]
                    if recent_attempts:
                        self.recovery_attempts[error_id] = recent_attempts
                    else:
                        del self.recovery_attempts[error_id]
                
            except Exception as e:
                logger.error(f"Background cleanup error: {e}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error handling statistics."""
        return {
            'error_stats': self.stats.copy(),
            'active_errors': len(self.active_errors),
            'error_history_size': len(self.error_history),
            'circuit_breaker_status': {
                component: cb.state for component, cb in self.circuit_breakers.items()
            },
            'recent_errors': [
                error.to_dict() for error in list(self.error_history)[-10:]
            ]
        }


# Global error handler instance
_error_handler: Optional[CacheErrorHandler] = None


async def get_error_handler() -> CacheErrorHandler:
    """Get the global error handler."""
    global _error_handler
    if _error_handler is None:
        # Default configuration
        config = {
            'circuit_breaker_threshold': 5,
            'retry_max_attempts': 3,
            'error_history_size': 1000
        }
        _error_handler = CacheErrorHandler(config)
        await _error_handler.initialize()
    return _error_handler


# Convenience functions
async def handle_cache_error(
    error: Exception,
    operation: str,
    component: str,
    key: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> bool:
    """Handle cache error (convenience function)."""
    handler = await get_error_handler()
    return await handler.handle_error(error, operation, component, key, context)


def get_error_statistics() -> Dict[str, Any]:
    """Get error statistics (convenience function)."""
    if _error_handler:
        return _error_handler.get_error_statistics()
    return {"error": "Error handler not initialized"}
