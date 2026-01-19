"""
Error Handling and Recovery System
Comprehensive error handling, logging, and recovery mechanisms for Raptorflow
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import asyncio
import traceback
import functools
from collections import defaultdict, deque
import inspect

logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories"""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    AI_SERVICE = "ai_service"
    FILE_PROCESSING = "file_processing"
    WORKFLOW = "workflow"
    SYSTEM = "system"
    NETWORK = "network"
    BUSINESS_LOGIC = "business_logic"


class RecoveryAction(str, Enum):
    """Recovery action types"""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    MANUAL_INTERVENTION = "manual_intervention"
    IGNORE = "ignore"
    ESCALATE = "escalate"


@dataclass
class ErrorContext:
    """Error context information"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    workspace_id: Optional[str] = None
    request_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorRecord:
    """Error record for tracking and analysis"""
    id: str
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    exception_type: str
    stack_trace: str
    context: ErrorContext
    recovery_action: Optional[RecoveryAction] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "error_id": self.error_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "exception_type": self.exception_type,
            "stack_trace": self.stack_trace,
            "context": {
                "user_id": self.context.user_id,
                "session_id": self.context.session_id,
                "workspace_id": self.context.workspace_id,
                "request_id": self.context.request_id,
                "endpoint": self.context.endpoint,
                "method": self.context.method
            },
            "recovery_action": self.recovery_action.value if self.recovery_action else None,
            "recovery_attempted": self.recovery_attempted,
            "recovery_successful": self.recovery_successful,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "metadata": self.metadata
        }


@dataclass
class RecoveryStrategy:
    """Recovery strategy configuration"""
    action: RecoveryAction
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_multiplier: float = 2.0
    timeout: float = 30.0
    fallback_function: Optional[Callable] = None
    escalation_threshold: int = 5
    conditions: List[str] = field(default_factory=list)
    
    def should_retry(self, error_record: ErrorRecord) -> bool:
        """Determine if error should be retried"""
        return (
            self.action == RecoveryAction.RETRY and
            error_record.retry_count < self.max_retries and
            error_record.retry_count < self.escalation_threshold
        )
    
    def calculate_retry_delay(self, retry_count: int) -> float:
        """Calculate retry delay with exponential backoff"""
        return self.retry_delay * (self.backoff_multiplier ** retry_count)


class ErrorRecoverySystem:
    """Advanced error handling and recovery system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Error storage
        self.error_records: Dict[str, ErrorRecord] = {}
        self.error_history: deque = deque(maxlen=10000)
        
        # Recovery strategies
        self.recovery_strategies: Dict[ErrorCategory, RecoveryStrategy] = self._initialize_recovery_strategies()
        
        # Circuit breaker state
        self.circuit_breakers: Dict[str, Dict[str, Any]] = defaultdict(self._create_circuit_breaker)
        
        # Error statistics
        self.error_stats: Dict[str, Any] = defaultdict(int)
        
        # Recovery functions registry
        self.recovery_functions: Dict[str, Callable] = {}
        
        # Error handlers
        self.error_handlers: Dict[ErrorCategory, List[Callable]] = defaultdict(list)
        
        # Background tasks
        self.recovery_tasks: List[asyncio.Task] = []
    
    def _initialize_recovery_strategies(self) -> Dict[ErrorCategory, RecoveryStrategy]:
        """Initialize default recovery strategies"""
        return {
            ErrorCategory.VALIDATION: RecoveryStrategy(
                action=RecoveryAction.IGNORE,
                max_retries=0
            ),
            ErrorCategory.AUTHENTICATION: RecoveryStrategy(
                action=RecoveryAction.RETRY,
                max_retries=2,
                retry_delay=1.0
            ),
            ErrorCategory.AUTHORIZATION: RecoveryStrategy(
                action=RecoveryAction.IGNORE,
                max_retries=0
            ),
            ErrorCategory.DATABASE: RecoveryStrategy(
                action=RecoveryAction.RETRY,
                max_retries=3,
                retry_delay=2.0,
                backoff_multiplier=2.0
            ),
            ErrorCategory.EXTERNAL_API: RecoveryStrategy(
                action=RecoveryAction.CIRCUIT_BREAKER,
                max_retries=3,
                retry_delay=1.0,
                escalation_threshold=5
            ),
            ErrorCategory.AI_SERVICE: RecoveryStrategy(
                action=RecoveryAction.FALLBACK,
                max_retries=2,
                retry_delay=5.0,
                escalation_threshold=3
            ),
            ErrorCategory.FILE_PROCESSING: RecoveryStrategy(
                action=RecoveryAction.RETRY,
                max_retries=2,
                retry_delay=3.0
            ),
            ErrorCategory.WORKFLOW: RecoveryStrategy(
                action=RecoveryAction.GRACEFUL_DEGRADATION,
                max_retries=1
            ),
            ErrorCategory.SYSTEM: RecoveryStrategy(
                action=RecoveryAction.ESCALATE,
                max_retries=0
            ),
            ErrorCategory.NETWORK: RecoveryStrategy(
                action=RecoveryAction.RETRY,
                max_retries=5,
                retry_delay=1.0,
                backoff_multiplier=1.5
            ),
            ErrorCategory.BUSINESS_LOGIC: RecoveryStrategy(
                action=RecoveryAction.MANUAL_INTERVENTION,
                max_retries=0
            )
        }
    
    def _create_circuit_breaker(self) -> Dict[str, Any]:
        """Create circuit breaker state"""
        return {
            "state": "closed",  # closed, open, half_open
            "failure_count": 0,
            "failure_threshold": 5,
            "recovery_timeout": 60.0,
            "last_failure_time": None,
            "success_count": 0,
            "success_threshold": 3
        }
    
    def register_recovery_function(self, name: str, function: Callable):
        """Register a recovery function"""
        self.recovery_functions[name] = function
        self.logger.info(f"Registered recovery function: {name}")
    
    def register_error_handler(self, category: ErrorCategory, handler: Callable):
        """Register an error handler for a category"""
        self.error_handlers[category].append(handler)
        self.logger.info(f"Registered error handler for category: {category.value}")
    
    def handle_error(self, exception: Exception, context: ErrorContext = None) -> ErrorRecord:
        """Handle an error and create error record"""
        # Generate error ID
        error_id = f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(exception)}"
        
        # Determine error category and severity
        category = self._categorize_error(exception)
        severity = self._determine_severity(exception, category)
        
        # Create error record
        error_record = ErrorRecord(
            id=error_id,
            error_id=error_id,
            category=category,
            severity=severity,
            message=str(exception),
            exception_type=type(exception).__name__,
            stack_trace=traceback.format_exc(),
            context=context or ErrorContext(),
            max_retries=self.recovery_strategies[category].max_retries
        )
        
        # Store error record
        self.error_records[error_id] = error_record
        self.error_history.append(error_record)
        
        # Update statistics
        self.error_stats[f"total_errors"] += 1
        self.error_stats[f"category_{category.value}"] += 1
        self.error_stats[f"severity_{severity.value}"] += 1
        
        # Log error
        self._log_error(error_record)
        
        # Trigger error handlers
        await self._trigger_error_handlers(error_record)
        
        return error_record
    
    def _categorize_error(self, exception: Exception) -> ErrorCategory:
        """Categorize error based on exception type and message"""
        exception_type = type(exception).__name__.lower()
        message = str(exception).lower()
        
        # Database errors
        if any(keyword in exception_type for keyword in ["database", "db", "sql", "connection"]) or \
           any(keyword in message for keyword in ["database", "connection", "timeout", "deadlock"]):
            return ErrorCategory.DATABASE
        
        # Authentication/Authorization errors
        if any(keyword in exception_type for keyword in ["authentication", "auth", "permission", "unauthorized"]) or \
           any(keyword in message for keyword in ["unauthorized", "forbidden", "access denied", "permission"]):
            if "unauthorized" in message or "forbidden" in message:
                return ErrorCategory.AUTHORIZATION
            return ErrorCategory.AUTHENTICATION
        
        # Validation errors
        if any(keyword in exception_type for keyword in ["validation", "value", "type"]) or \
           any(keyword in message for keyword in ["invalid", "required", "missing", "malformed"]):
            return ErrorCategory.VALIDATION
        
        # Network errors
        if any(keyword in exception_type for keyword in ["network", "connection", "timeout", "http"]) or \
           any(keyword in message for keyword in ["network", "connection", "timeout", "unreachable"]):
            return ErrorCategory.NETWORK
        
        # File processing errors
        if any(keyword in exception_type for keyword in ["file", "io", "os"]) or \
           any(keyword in message for keyword in ["file", "directory", "permission denied", "not found"]):
            return ErrorCategory.FILE_PROCESSING
        
        # External API errors
        if any(keyword in exception_type for keyword in ["api", "http", "request"]) or \
           any(keyword in message for keyword in ["api", "http", "request", "external"]):
            return ErrorCategory.EXTERNAL_API
        
        # AI service errors
        if any(keyword in exception_type for keyword in ["ai", "ml", "model", "vertex"]) or \
           any(keyword in message for keyword in ["ai", "model", "prediction", "inference"]):
            return ErrorCategory.AI_SERVICE
        
        # System errors
        if any(keyword in exception_type for keyword in ["system", "os", "memory", "cpu"]) or \
           any(keyword in message for keyword in ["system", "memory", "disk", "resource"]):
            return ErrorCategory.SYSTEM
        
        # Default to business logic
        return ErrorCategory.BUSINESS_LOGIC
    
    def _determine_severity(self, exception: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity"""
        # Critical categories
        if category in [ErrorCategory.SYSTEM, ErrorCategory.DATABASE]:
            return ErrorSeverity.CRITICAL
        
        # High severity categories
        if category in [ErrorCategory.AI_SERVICE, ErrorCategory.EXTERNAL_API]:
            return ErrorSeverity.HIGH
        
        # Medium severity categories
        if category in [ErrorCategory.WORKFLOW, ErrorCategory.NETWORK]:
            return ErrorSeverity.MEDIUM
        
        # Low severity categories
        if category in [ErrorCategory.VALIDATION, ErrorCategory.AUTHENTICATION, ErrorCategory.AUTHORIZATION]:
            return ErrorSeverity.LOW
        
        # Default to medium
        return ErrorSeverity.MEDIUM
    
    def _log_error(self, error_record: ErrorRecord):
        """Log error with appropriate level"""
        log_message = f"[{error_record.error_id}] {error_record.category.value}/{error_record.severity.value}: {error_record.message}"
        
        if error_record.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error_record.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error_record.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    async def _trigger_error_handlers(self, error_record: ErrorRecord):
        """Trigger registered error handlers"""
        handlers = self.error_handlers.get(error_record.category, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(error_record)
                else:
                    handler(error_record)
            except Exception as e:
                self.logger.error(f"Error in error handler: {e}")
    
    async def attempt_recovery(self, error_record: ErrorRecord, function: Callable = None, *args, **kwargs) -> Tuple[bool, Any]:
        """Attempt error recovery"""
        strategy = self.recovery_strategies[error_record.category]
        
        # Check circuit breaker
        if strategy.action == RecoveryAction.CIRCUIT_BREAKER:
            circuit_breaker_key = f"{error_record.category.value}_{function.__name__ if function else 'unknown'}"
            if not self._check_circuit_breaker(circuit_breaker_key):
                return False, None
        
        # Increment retry count
        error_record.retry_count += 1
        
        try:
            # Execute recovery action
            if strategy.action == RecoveryAction.RETRY and function:
                # Calculate retry delay
                delay = strategy.calculate_retry_delay(error_record.retry_count - 1)
                await asyncio.sleep(delay)
                
                # Retry the function
                result = await self._execute_with_timeout(function, strategy.timeout, *args, **kwargs)
                
                # Mark recovery as successful
                error_record.recovery_attempted = True
                error_record.recovery_successful = True
                error_record.resolved_at = datetime.now()
                
                # Update circuit breaker
                if strategy.action == RecoveryAction.CIRCUIT_BREAKER:
                    self._record_circuit_breaker_success(circuit_breaker_key)
                
                return True, result
                
            elif strategy.action == RecoveryAction.FALLBACK and strategy.fallback_function:
                # Execute fallback function
                result = await self._execute_with_timeout(strategy.fallback_function, strategy.timeout, *args, **kwargs)
                error_record.recovery_attempted = True
                error_record.recovery_successful = True
                error_record.resolved_at = datetime.now()
                return True, result
                
            elif strategy.action == RecoveryAction.GRACEFUL_DEGRADATION:
                # Implement graceful degradation
                result = await self._graceful_degradation(error_record, *args, **kwargs)
                error_record.recovery_attempted = True
                error_record.recovery_successful = True
                error_record.resolved_at = datetime.now()
                return True, result
                
            elif strategy.action == RecoveryAction.MANUAL_INTERVENTION:
                # Escalate for manual intervention
                await self._escalate_for_manual_intervention(error_record)
                return False, None
                
            elif strategy.action == RecoveryAction.IGNORE:
                # Ignore error and continue
                return True, None
                
            elif strategy.action == RecoveryAction.ESCALATE:
                # Escalate error
                await self._escalate_error(error_record)
                return False, None
                
        except Exception as e:
            # Recovery failed
            self.logger.error(f"Recovery attempt failed for {error_record.error_id}: {e}")
            
            # Update circuit breaker
            if strategy.action == RecoveryAction.CIRCUIT_BREAKER:
                self._record_circuit_breaker_failure(circuit_breaker_key)
            
            # Check if should escalate
            if error_record.retry_count >= strategy.escalation_threshold:
                await self._escalate_error(error_record)
            
            return False, None
        
        return False, None
    
    async def _execute_with_timeout(self, function: Callable, timeout: float, *args, **kwargs) -> Any:
        """Execute function with timeout"""
        try:
            if asyncio.iscoroutinefunction(function):
                return await asyncio.wait_for(function(*args, **kwargs), timeout=timeout)
            else:
                # Run synchronous function in thread pool
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, functools.partial(function, *args, **kwargs))
        except asyncio.TimeoutError:
            raise Exception(f"Function execution timed out after {timeout} seconds")
    
    def _check_circuit_breaker(self, key: str) -> bool:
        """Check if circuit breaker allows execution"""
        circuit_breaker = self.circuit_breakers[key]
        
        if circuit_breaker["state"] == "closed":
            return True
        elif circuit_breaker["state"] == "open":
            # Check if recovery timeout has passed
            if circuit_breaker["last_failure_time"]:
                time_since_failure = datetime.now() - circuit_breaker["last_failure_time"]
                if time_since_failure.total_seconds() >= circuit_breaker["recovery_timeout"]:
                    circuit_breaker["state"] = "half_open"
                    circuit_breaker["success_count"] = 0
                    return True
            return False
        elif circuit_breaker["state"] == "half_open":
            return True
        
        return False
    
    def _record_circuit_breaker_success(self, key: str):
        """Record success in circuit breaker"""
        circuit_breaker = self.circuit_breakers[key]
        
        if circuit_breaker["state"] == "half_open":
            circuit_breaker["success_count"] += 1
            if circuit_breaker["success_count"] >= circuit_breaker["success_threshold"]:
                circuit_breaker["state"] = "closed"
                circuit_breaker["failure_count"] = 0
    
    def _record_circuit_breaker_failure(self, key: str):
        """Record failure in circuit breaker"""
        circuit_breaker = self.circuit_breakers[key]
        
        circuit_breaker["failure_count"] += 1
        circuit_breaker["last_failure_time"] = datetime.now()
        
        if circuit_breaker["failure_count"] >= circuit_breaker["failure_threshold"]:
            circuit_breaker["state"] = "open"
    
    async def _graceful_degradation(self, error_record: ErrorRecord, *args, **kwargs) -> Any:
        """Implement graceful degradation"""
        # Return a default/degraded response
        return {
            "status": "degraded",
            "message": "Service operating in degraded mode",
            "error_id": error_record.error_id,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _escalate_for_manual_intervention(self, error_record: ErrorRecord):
        """Escalate for manual intervention"""
        # Implementation would notify administrators
        self.logger.critical(f"Manual intervention required for error: {error_record.error_id}")
        
        # Could integrate with notification system, ticketing system, etc.
        pass
    
    async def _escalate_error(self, error_record: ErrorRecord):
        """Escalate error to higher priority"""
        # Implementation would send alerts, notifications, etc.
        self.logger.error(f"Error escalated: {error_record.error_id}")
        
        # Could integrate with alerting system
        pass
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        return dict(self.error_stats)
    
    def get_recent_errors(self, limit: int = 100) -> List[ErrorRecord]:
        """Get recent errors"""
        return list(self.error_history)[-limit:]
    
    def get_errors_by_category(self, category: ErrorCategory, limit: int = 50) -> List[ErrorRecord]:
        """Get errors by category"""
        return [record for record in self.error_history if record.category == category][-limit:]
    
    def get_errors_by_severity(self, severity: ErrorSeverity, limit: int = 50) -> List[ErrorRecord]:
        """Get errors by severity"""
        return [record for record in self.error_history if record.severity == severity][-limit:]
    
    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            key: {
                "state": cb["state"],
                "failure_count": cb["failure_count"],
                "failure_threshold": cb["failure_threshold"],
                "last_failure_time": cb["last_failure_time"].isoformat() if cb["last_failure_time"] else None
            }
            for key, cb in self.circuit_breakers.items()
        }
    
    def reset_circuit_breaker(self, key: str):
        """Reset circuit breaker"""
        if key in self.circuit_breakers:
            self.circuit_breakers[key] = self._create_circuit_breaker()
            self.logger.info(f"Circuit breaker reset: {key}")


# Decorator for automatic error handling
def handle_errors(category: ErrorCategory = None, recovery_strategy: RecoveryStrategy = None):
    """Decorator for automatic error handling"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Get error recovery system
                error_system = ErrorRecoverySystem()
                
                # Create context
                context = ErrorContext()
                
                # Extract context from function arguments if available
                if args and hasattr(args[0], '__dict__'):
                    # Try to get context from first argument (usually self)
                    obj = args[0]
                    if hasattr(obj, 'user_id'):
                        context.user_id = obj.user_id
                    if hasattr(obj, 'session_id'):
                        context.session_id = obj.session_id
                    if hasattr(obj, 'workspace_id'):
                        context.workspace_id = obj.workspace_id
                
                # Handle error
                error_record = error_system.handle_error(e, context)
                
                # Attempt recovery
                success, result = await error_system.attempt_recovery(error_record, func, *args, **kwargs)
                
                if success:
                    return result
                else:
                    # Re-raise if recovery failed
                    raise e
        
        return wrapper
    return decorator


# Global error recovery system instance
error_recovery_system = ErrorRecoverySystem()

# Export system
__all__ = ["ErrorRecoverySystem", "ErrorRecord", "ErrorContext", "RecoveryStrategy", "handle_errors", "error_recovery_system"]
