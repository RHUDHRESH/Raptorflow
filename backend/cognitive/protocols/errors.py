"""
Error Handling for Protocol Standardization

Standardized error handling and recovery for cognitive processing.
Implements PROMPT 74 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import logging
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from messages import AgentMessage, MessageFormat, MessageType


class ErrorSeverity(Enum):
    """Severity levels for cognitive errors."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    FATAL = "fatal"


class ErrorCategory(Enum):
    """Categories of cognitive errors."""

    VALIDATION = "validation"
    PROCESSING = "processing"
    COMMUNICATION = "communication"
    RESOURCE = "resource"
    AUTHORIZATION = "authorization"
    INTEGRATION = "integration"
    SYSTEM = "system"
    USER_INPUT = "user_input"
    EXTERNAL_SERVICE = "external_service"
    TIMEOUT = "timeout"


class RecoveryStrategy(Enum):
    """Recovery strategies for errors."""

    RETRY = "retry"
    FALLBACK = "fallback"
    ESCALATION = "escalation"
    USER_INTERVENTION = "user_intervention"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    IGNORE = "ignore"
    ABORT = "abort"


@dataclass
class CognitiveError:
    """Standardized cognitive error."""

    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: str
    context: Dict[str, Any]
    timestamp: datetime
    stack_trace: str
    recovery_strategies: List[RecoveryStrategy]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize error ID and timestamp."""
        if not self.error_id:
            self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "error_id": self.error_id,
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "stack_trace": self.stack_trace,
            "recovery_strategies": [s.value for s in self.recovery_strategies],
            "metadata": self.metadata,
        }

    @classmethod
    def from_exception(
        cls,
        error: Exception,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Dict[str, Any] = None,
        recovery_strategies: List[RecoveryStrategy] = None,
    ) -> "CognitiveError":
        """Create CognitiveError from exception."""
        return cls(
            error_id=str(uuid.uuid4()),
            category=category,
            severity=severity,
            message=str(error),
            details=error.__class__.__name__,
            context=context or {},
            timestamp=datetime.now(),
            stack_trace=traceback.format_exc(),
            recovery_strategies=recovery_strategies or [],
            metadata={
                "exception_type": type(error).__name__,
                "exception_module": error.__class__.__module__,
            },
        )


@dataclass
class ErrorReport:
    """Complete error report for analysis."""

    report_id: str
    errors: List[CognitiveError]
    session_id: str
    agent_id: str
    workflow_id: str
    start_time: datetime
    end_time: datetime
    total_errors: int
    error_rate: float
    recovery_attempts: int
    successful_recoveries: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class ErrorHandler:
    """
    Standardized error handling and recovery for cognitive processing.

    Provides consistent error classification and recovery strategies.
    """

    def __init__(self, notification_client=None, escalation_client=None):
        """
        Initialize the error handler.

        Args:
            notification_client: Client for error notifications
            escalation_client: Client for error escalation
        """
        self.notification_client = notification_client
        self.escalation_client = escalation_client

        # Error classification rules
        self.classification_rules = []
        self._setup_classification_rules()

        # Recovery strategies registry
        self.recovery_strategies: Dict[RecoveryStrategy, Callable] = {}
        self._setup_recovery_strategies()

        # Error tracking
        self.error_history: List[Dict[str, Any]] = []
        self.active_errors: Dict[str, CognitiveError] = {}

        # Statistics
        self.stats = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_severity": {},
            "recovery_attempts": 0,
            "successful_recoveries": 0,
            "escalations": 0,
            "user_interventions": 0,
        }

        # Error thresholds
        self.thresholds = {
            "error_rate_threshold": 0.1,  # 10%
            "critical_error_threshold": 5,  # 5 critical errors
            "escalation_threshold": 3,  # 3 errors in 5 minutes
            "user_intervention_threshold": 2,  # 2 unrecoverable errors
        }

        # Setup logging
        self.logger = logging.getLogger("cognitive_errors")

    async def handle_error(
        self,
        error: Union[Exception, CognitiveError],
        context: Dict[str, Any] = None,
        recovery_strategies: List[RecoveryStrategy] = None,
    ) -> Dict[str, Any]:
        """
        Handle an error with appropriate recovery strategies.

        Args:
            error: The error to handle
            context: Error context
            recovery_strategies: Specific recovery strategies to try

        Returns:
            Error handling result
        """
        # Convert exception to CognitiveError if needed
        if isinstance(error, Exception):
            cognitive_error = await self._classify_error(error, context)
        else:
            cognitive_error = error

        # Add to active errors
        self.active_errors[cognitive_error.error_id] = cognitive_error

        # Update statistics
        self._update_stats(cognitive_error)

        # Determine recovery strategies
        strategies = recovery_strategies or cognitive_error.recovery_strategies

        # Try recovery strategies
        recovery_result = await self._attempt_recovery(cognitive_error, strategies)

        # Check if escalation is needed
        if not recovery_result["recovered"] and self._should_escalate(cognitive_error):
            await self._escalate_error(cognitive_error)

        # Remove from active errors
        self.active_errors.pop(cognitive_error.error_id, None)

        return recovery_result

    async def classify_error(
        self, error: Exception, context: Dict[str, Any] = None
    ) -> CognitiveError:
        """Classify an exception into a CognitiveError."""
        return await self._classify_error(error, context)

    async def create_error_report(
        self,
        session_id: str,
        agent_id: str,
        workflow_id: str,
        errors: List[CognitiveError],
    ) -> ErrorReport:
        """Create an error report for analysis."""
        report_id = str(uuid.uuid4())
        start_time = (
            min(error.timestamp for error in errors) if errors else datetime.now()
        )
        end_time = (
            max(error.timestamp for error in errors) if errors else datetime.now()
        )

        # Calculate recovery statistics
        recovery_attempts = sum(len(error.recovery_strategies) for error in errors)
        successful_recoveries = sum(
            1 for error in errors if error.metadata.get("recovered", False)
        )

        return ErrorReport(
            report_id=report_id,
            errors=errors,
            session_id=session_id,
            agent_id=agent_id,
            workflow_id=workflow_id,
            start_time=start_time,
            end_time=end_time,
            total_errors=len(errors),
            error_rate=len(errors) / max(1, len(errors)),  # Simplified
            recovery_attempts=recovery_attempts,
            successful_recoveries=successful_recoveries,
            metadata={
                "created_at": datetime.now().isoformat(),
                "error_types": list(set(error.details for error in errors)),
            },
        )

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error handling statistics."""
        return self.stats

    def get_active_errors(self) -> List[CognitiveError]:
        """Get currently active errors."""
        return list(self.active_errors.values())

    def get_error_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get error history."""
        return self.error_history[-limit:]

    def set_threshold(self, threshold_name: str, value: Any) -> None:
        """Set error handling threshold."""
        if threshold_name in self.thresholds:
            self.thresholds[threshold_name] = value

    def get_threshold(self, threshold_name: str) -> Any:
        """Get error handling threshold."""
        return self.thresholds.get(threshold_name)

    async def _classify_error(
        self, error: Exception, context: Dict[str, Any] = None
    ) -> CognitiveError:
        """Classify an exception into a CognitiveError."""
        # Find matching classification rule
        for rule in self.classification_rules:
            if self._matches_rule(error, rule):
                return CognitiveError(
                    error_id=str(uuid.uuid4()),
                    category=rule["category"],
                    severity=rule["severity"],
                    message=str(error),
                    details=error.__class__.__name__,
                    context=context or {},
                    timestamp=datetime.now(),
                    stack_trace=traceback.format_exc(),
                    recovery_strategies=rule["recovery_strategies"],
                    metadata={
                        "rule_matched": rule["name"],
                        "exception_type": type(error).__name__,
                    },
                )

        # Default classification
        return CognitiveError(
            error_id=str(uuid.uuid4()),
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            message=str(error),
            details=error.__class__.__name__,
            context=context or {},
            timestamp=datetime.now(),
            stack_trace=traceback.format_exc(),
            recovery_strategies=[RecoveryStrategy.RETRY],
            metadata={
                "default_classification": True,
                "exception_type": type(error).__name__,
            },
        )

    def _matches_rule(self, error: Exception, rule: Dict[str, Any]) -> bool:
        """Check if error matches a classification rule."""
        # Check exception type
        if "exception_types" in rule:
            if type(error).__name__ not in rule["exception_types"]:
                return False

        # Check error message patterns
        if "message_patterns" in rule:
            error_message = str(error).lower()
            for pattern in rule["message_patterns"]:
                if pattern.lower() in error_message:
                    return True
            return False

        # Check context conditions
        if "context_conditions" in rule:
            # This would check context conditions
            pass

        return True

    async def _attempt_recovery(
        self, error: CognitiveError, strategies: List[RecoveryStrategy]
    ) -> Dict[str, Any]:
        """Attempt recovery using specified strategies."""
        recovery_result = {
            "recovered": False,
            "strategy_used": None,
            "attempts": 0,
            "error": None,
            "metadata": {},
        }

        for strategy in strategies:
            try:
                recovery_result["attempts"] += 1

                # Get recovery function
                recovery_func = self.recovery_strategies.get(strategy)
                if not recovery_func:
                    continue

                # Attempt recovery
                if asyncio.iscoroutinefunction(recovery_func):
                    result = await recovery_func(error)
                else:
                    result = recovery_func(error)

                if result.get("success", False):
                    recovery_result["recovered"] = True
                    recovery_result["strategy_used"] = strategy.value
                    recovery_result["metadata"] = result.get("metadata", {})
                    self.stats["successful_recoveries"] += 1
                    break

            except Exception as recovery_error:
                recovery_result["error"] = recovery_error
                self.logger.error(
                    f"Recovery strategy {strategy.value} failed: {recovery_error}"
                )
                continue

        self.stats["recovery_attempts"] += recovery_result["attempts"]

        return recovery_result

    def _should_escalate(self, error: CognitiveError) -> bool:
        """Determine if error should be escalated."""
        # Check severity
        if error.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.FATAL]:
            return True

        # Check recovery strategies exhausted
        if not error.recovery_strategies:
            return True

        # Check error rate threshold
        recent_errors = [
            e
            for e in self.error_history[-100:]  # Last 100 errors
            if datetime.fromisoformat(e["timestamp"])
            > datetime.now() - timedelta(minutes=5)
        ]

        if len(recent_errors) >= self.thresholds["escalation_threshold"]:
            return True

        return False

    async def _escalate_error(self, error: CognitiveError) -> None:
        """Escalate an error to higher level."""
        self.stats["escalations"] += 1

        # Create escalation message
        escalation_data = {
            "error_id": error.error_id,
            "severity": error.severity.value,
            "category": error.category.value,
            "message": error.message,
            "context": error.context,
            "timestamp": error.timestamp.isoformat(),
            "escalation_reason": "Automatic escalation based on error severity and recovery failure",
        }

        # Send escalation
        if self.escalation_client:
            await self.escalation_client.escalate(
                title=f"Cognitive Error Escalation: {error.category.value}",
                message=error.message,
                data=escalation_data,
                priority="high",
            )

        # Log escalation
        self.logger.error(f"Error escalated: {error.error_id} - {error.message}")

    def _update_stats(self, error: CognitiveError) -> None:
        """Update error statistics."""
        self.stats["total_errors"] += 1

        # Category statistics
        category = error.category.value
        self.stats["errors_by_category"][category] = (
            self.stats["errors_by_category"].get(category, 0) + 1
        )

        # Severity statistics
        severity = error.severity.value
        self.stats["errors_by_severity"][severity] = (
            self.stats["errors_by_severity"].get(severity, 0) + 1
        )

        # Add to history
        self.error_history.append(error.to_dict())

    def _setup_classification_rules(self) -> None:
        """Setup default error classification rules."""
        # Validation errors
        self.classification_rules.append(
            {
                "name": "validation_error",
                "exception_types": ["ValueError", "TypeError", "ValidationError"],
                "category": ErrorCategory.VALIDATION,
                "severity": ErrorSeverity.MEDIUM,
                "recovery_strategies": [
                    RecoveryStrategy.USER_INTERVENTION,
                    RecoveryStrategy.FALLBACK,
                ],
            }
        )

        # Communication errors
        self.classification_rules.append(
            {
                "name": "communication_error",
                "exception_types": ["ConnectionError", "TimeoutError"],
                "message_patterns": ["connection", "timeout", "network"],
                "category": ErrorCategory.COMMUNICATION,
                "severity": ErrorSeverity.HIGH,
                "recovery_strategies": [
                    RecoveryStrategy.RETRY,
                    RecoveryStrategy.FALLBACK,
                ],
            }
        )

        # Resource errors
        self.classification_rules.append(
            {
                "name": "resource_error",
                "exception_types": ["MemoryError", "ResourceWarning"],
                "message_patterns": ["memory", "resource", "disk", "cpu"],
                "category": ErrorCategory.RESOURCE,
                "severity": ErrorSeverity.HIGH,
                "recovery_strategies": [
                    RecoveryStrategy.GRACEFUL_DEGRADATION,
                    RecoveryStrategy.ESCALATION,
                ],
            }
        )

        # Authorization errors
        self.classification_rules.append(
            {
                "name": "authorization_error",
                "exception_types": ["PermissionError", "AuthorizationError"],
                "message_patterns": ["permission", "authorized", "access denied"],
                "category": ErrorCategory.AUTHORIZATION,
                "severity": ErrorSeverity.HIGH,
                "recovery_strategies": [
                    RecoveryStrategy.USER_INTERVENTION,
                    RecoveryStrategy.ESCALATION,
                ],
            }
        )

        # System errors
        self.classification_rules.append(
            {
                "name": "system_error",
                "exception_types": ["SystemError", "OSError"],
                "category": ErrorCategory.SYSTEM,
                "severity": ErrorSeverity.CRITICAL,
                "recovery_strategies": [
                    RecoveryStrategy.ESCALATION,
                    RecoveryStrategy.ABORT,
                ],
            }
        )

    def _setup_recovery_strategies(self) -> None:
        """Setup default recovery strategies."""
        self.recovery_strategies[RecoveryStrategy.RETRY] = self._retry_recovery
        self.recovery_strategies[RecoveryStrategy.FALLBACK] = self._fallback_recovery
        self.recovery_strategies[RecoveryStrategy.ESCALATION] = (
            self._escalation_recovery
        )
        self.recovery_strategies[RecoveryStrategy.USER_INTERVENTION] = (
            self._user_intervention_recovery
        )
        self.recovery_strategies[RecoveryStrategy.GRACEFUL_DEGRADATION] = (
            self._graceful_degradation_recovery
        )
        self.recovery_strategies[RecoveryStrategy.IGNORE] = self._ignore_recovery
        self.recovery_strategies[RecoveryStrategy.ABORT] = self._abort_recovery

    async def _retry_recovery(self, error: CognitiveError) -> Dict[str, Any]:
        """Retry recovery strategy."""
        return {
            "success": False,
            "metadata": {
                "strategy": "retry",
                "message": "Retry recovery not implemented in base handler",
            },
        }

    async def _fallback_recovery(self, error: CognitiveError) -> Dict[str, Any]:
        """Fallback recovery strategy."""
        return {
            "success": False,
            "metadata": {
                "strategy": "fallback",
                "message": "Fallback recovery not implemented in base handler",
            },
        }

    async def _escalation_recovery(self, error: CognitiveError) -> Dict[str, Any]:
        """Escalation recovery strategy."""
        return {
            "success": False,
            "metadata": {
                "strategy": "escalation",
                "message": "Escalation recovery not implemented in base handler",
            },
        }

    async def _user_intervention_recovery(
        self, error: CognitiveError
    ) -> Dict[str, Any]:
        """User intervention recovery strategy."""
        self.stats["user_interventions"] += 1

        # Create user intervention request
        intervention_data = {
            "error_id": error.error_id,
            "severity": error.severity.value,
            "category": error.category.value,
            "message": error.message,
            "context": error.context,
            "timestamp": error.timestamp.isoformat(),
        }

        if self.notification_client:
            await self.notification_client.notify(
                title="User Intervention Required",
                message=f"Error requires user intervention: {error.message}",
                data=intervention_data,
                priority="high",
            )

        return {
            "success": False,
            "metadata": {
                "strategy": "user_intervention",
                "message": "User intervention requested",
                "intervention_data": intervention_data,
            },
        }

    async def _graceful_degradation_recovery(
        self, error: CognitiveError
    ) -> Dict[str, Any]:
        """Graceful degradation recovery strategy."""
        return {
            "success": True,
            "metadata": {
                "strategy": "graceful_degradation",
                "message": "Switched to degraded mode",
                "degraded_mode": True,
            },
        }

    async def _ignore_recovery(self, error: CognitiveError) -> Dict[str, Any]:
        """Ignore recovery strategy."""
        return {
            "success": True,
            "metadata": {
                "strategy": "ignore",
                "message": "Error ignored",
                "ignored": True,
            },
        }

    async def _abort_recovery(self, error: CognitiveError) -> Dict[str, Any]:
        """Abort recovery strategy."""
        return {
            "success": False,
            "metadata": {
                "strategy": "abort",
                "message": "Operation aborted due to error",
                "aborted": True,
            },
        }

    def add_classification_rule(self, rule: Dict[str, Any]) -> None:
        """Add a custom classification rule."""
        self.classification_rules.append(rule)

    def remove_classification_rule(self, rule_name: str) -> bool:
        """Remove a classification rule."""
        for i, rule in enumerate(self.classification_rules):
            if rule.get("name") == rule_name:
                self.classification_rules.pop(i)
                return True
        return False

    def add_recovery_strategy(self, strategy: RecoveryStrategy, func: Callable) -> None:
        """Add a custom recovery strategy."""
        self.recovery_strategies[strategy] = func

    def remove_recovery_strategy(self, strategy: RecoveryStrategy) -> bool:
        """Remove a recovery strategy."""
        if strategy in self.recovery_strategies:
            del self.recovery_strategies[strategy]
            return True
        return False

    def create_error_message(
        self, error: CognitiveError, to_agent: str = None
    ) -> AgentMessage:
        """Create an error message for communication."""
        return MessageFormat.create_error(
            from_agent="error_handler",
            to_agent=to_agent or "broadcast",
            error=error.message,
            correlation_id=error.error_id,
            metadata={
                "error_id": error.error_id,
                "category": error.category.value,
                "severity": error.severity.value,
                "context": error.context,
            },
        )

    def get_error_summary(self, error_id: str = None) -> Dict[str, Any]:
        """Get summary of errors."""
        if error_id:
            error = self.active_errors.get(error_id)
            if error:
                return error.to_dict()
            else:
                # Search history
                for historic_error in self.error_history:
                    if historic_error["error_id"] == error_id:
                        return historic_error
                return {}

        # Return overall summary
        return {
            "total_errors": self.stats["total_errors"],
            "active_errors": len(self.active_errors),
            "errors_by_category": self.stats["errors_by_category"],
            "errors_by_severity": self.stats["errors_by_severity"],
            "recovery_success_rate": self.stats["successful_recoveries"]
            / max(self.stats["recovery_attempts"], 1),
            "escalation_count": self.stats["escalations"],
            "user_intervention_count": self.stats["user_interventions"],
        }
