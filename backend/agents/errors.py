"""
Custom exceptions for the Raptorflow agent system.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional


class RaptorflowError(Exception):
    """Base exception for all Raptorflow errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.cause = cause
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "cause": str(self.cause) if self.cause else None,
        }


class AgentExecutionError(RaptorflowError):
    """Raised when agent execution fails."""

    def __init__(
        self,
        message: str,
        agent_name: Optional[str] = None,
        workspace_id: Optional[str] = None,
        session_id: Optional[str] = None,
        execution_time_ms: Optional[float] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if agent_name:
            context["agent_name"] = agent_name
        if workspace_id:
            context["workspace_id"] = workspace_id
        if session_id:
            context["session_id"] = session_id
        if execution_time_ms:
            context["execution_time_ms"] = execution_time_ms

        super().__init__(message, "AGENT_EXECUTION_ERROR", context, kwargs.get("cause"))
        self.agent_name = agent_name
        self.workspace_id = workspace_id
        self.session_id = session_id
        self.execution_time_ms = execution_time_ms


class RoutingError(RaptorflowError):
    """Raised when request routing fails."""

    def __init__(
        self,
        message: str,
        request: Optional[str] = None,
        routing_confidence: Optional[float] = None,
        available_agents: Optional[List[str]] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if request:
            context["request"] = request
        if routing_confidence:
            context["routing_confidence"] = routing_confidence
        if available_agents:
            context["available_agents"] = available_agents

        super().__init__(message, "ROUTING_ERROR", context, kwargs.get("cause"))
        self.request = request
        self.routing_confidence = routing_confidence
        self.available_agents = available_agents or []


class ToolExecutionError(RaptorflowError):
    """Raised when tool execution fails."""

    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        tool_args: Optional[Dict[str, Any]] = None,
        execution_time_ms: Optional[float] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if tool_name:
            context["tool_name"] = tool_name
        if tool_args:
            context["tool_args"] = tool_args
        if execution_time_ms:
            context["execution_time_ms"] = execution_time_ms

        super().__init__(message, "TOOL_EXECUTION_ERROR", context, kwargs.get("cause"))
        self.tool_name = tool_name
        self.tool_args = tool_args
        self.execution_time_ms = execution_time_ms


class MemoryAccessError(RaptorflowError):
    """Raised when memory access fails."""

    def __init__(
        self,
        message: str,
        memory_type: Optional[str] = None,
        workspace_id: Optional[str] = None,
        query: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if memory_type:
            context["memory_type"] = memory_type
        if workspace_id:
            context["workspace_id"] = workspace_id
        if query:
            context["query"] = query

        super().__init__(message, "MEMORY_ACCESS_ERROR", context, kwargs.get("cause"))
        self.memory_type = memory_type
        self.workspace_id = workspace_id
        self.query = query


class ApprovalTimeoutError(RaptorflowError):
    """Raised when approval process times out."""

    def __init__(
        self,
        message: str,
        gate_id: Optional[str] = None,
        timeout_duration_hours: Optional[int] = None,
        risk_level: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if gate_id:
            context["gate_id"] = gate_id
        if timeout_duration_hours:
            context["timeout_duration_hours"] = timeout_duration_hours
        if risk_level:
            context["risk_level"] = risk_level

        super().__init__(
            message, "APPROVAL_TIMEOUT_ERROR", context, kwargs.get("cause")
        )
        self.gate_id = gate_id
        self.timeout_duration_hours = timeout_duration_hours
        self.risk_level = risk_level


class BudgetExceededError(RaptorflowError):
    """Raised when budget limits are exceeded."""

    def __init__(
        self,
        message: str,
        budget_limit: Optional[float] = None,
        current_spend: Optional[float] = None,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if budget_limit:
            context["budget_limit"] = budget_limit
        if current_spend:
            context["current_spend"] = current_spend
        if workspace_id:
            context["workspace_id"] = workspace_id
        if user_id:
            context["user_id"] = user_id

        super().__init__(message, "BUDGET_EXCEEDED_ERROR", context, kwargs.get("cause"))
        self.budget_limit = budget_limit
        self.current_spend = current_spend
        self.workspace_id = workspace_id
        self.user_id = user_id


class ConfigurationError(RaptorflowError):
    """Raised when configuration is invalid."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        expected_type: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if config_key:
            context["config_key"] = config_key
        if config_value is not None:
            context["config_value"] = str(config_value)
        if expected_type:
            context["expected_type"] = expected_type

        super().__init__(message, "CONFIGURATION_ERROR", context, kwargs.get("cause"))
        self.config_key = config_key
        self.config_value = config_value
        self.expected_type = expected_type


class ValidationError(RaptorflowError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Any] = None,
        validation_rule: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if field_name:
            context["field_name"] = field_name
        if field_value is not None:
            context["field_value"] = str(field_value)
        if validation_rule:
            context["validation_rule"] = validation_rule

        super().__init__(message, "VALIDATION_ERROR", context, kwargs.get("cause"))
        self.field_name = field_name
        self.field_value = field_value
        self.validation_rule = validation_rule


class AuthenticationError(RaptorflowError):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        auth_method: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if user_id:
            context["user_id"] = user_id
        if workspace_id:
            context["workspace_id"] = workspace_id
        if auth_method:
            context["auth_method"] = auth_method

        super().__init__(message, "AUTHENTICATION_ERROR", context, kwargs.get("cause"))
        self.user_id = user_id
        self.workspace_id = workspace_id
        self.auth_method = auth_method


class AuthorizationError(RaptorflowError):
    """Raised when authorization fails."""

    def __init__(
        self,
        message: str,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        required_permission: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if user_id:
            context["user_id"] = user_id
        if workspace_id:
            context["workspace_id"] = workspace_id
        if required_permission:
            context["required_permission"] = required_permission

        super().__init__(message, "AUTHORIZATION_ERROR", context, kwargs.get("cause"))
        self.user_id = user_id
        self.workspace_id = workspace_id
        self.required_permission = required_permission


class RateLimitError(RaptorflowError):
    """Raised when rate limits are exceeded."""

    def __init__(
        self,
        message: str,
        limit_type: Optional[str] = None,
        current_usage: Optional[int] = None,
        limit: Optional[int] = None,
        retry_after_seconds: Optional[int] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if limit_type:
            context["limit_type"] = limit_type
        if current_usage:
            context["current_usage"] = current_usage
        if limit:
            context["limit"] = limit
        if retry_after_seconds:
            context["retry_after_seconds"] = retry_after_seconds

        super().__init__(message, "RATE_LIMIT_ERROR", context, kwargs.get("cause"))
        self.limit_type = limit_type
        self.current_usage = current_usage
        self.limit = limit
        self.retry_after_seconds = retry_after_seconds


class ExternalServiceError(RaptorflowError):
    """Raised when external service calls fail."""

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        service_endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if service_name:
            context["service_name"] = service_name
        if service_endpoint:
            context["service_endpoint"] = service_endpoint
        if status_code:
            context["status_code"] = status_code
        if response_body:
            context["response_body"] = response_body[:500]  # Limit response body size

        super().__init__(
            message, "EXTERNAL_SERVICE_ERROR", context, kwargs.get("cause")
        )
        self.service_name = service_name
        self.service_endpoint = service_endpoint
        self.status_code = status_code
        self.response_body = response_body


class WorkflowError(RaptorflowError):
    """Raised when workflow execution fails."""

    def __init__(
        self,
        message: str,
        workflow_name: Optional[str] = None,
        step_name: Optional[str] = None,
        step_index: Optional[int] = None,
        completed_steps: Optional[List[str]] = None,
        **kwargs
    ):
        context = kwargs.get("context", {})
        if workflow_name:
            context["workflow_name"] = workflow_name
        if step_name:
            context["step_name"] = step_name
        if step_index is not None:
            context["step_index"] = step_index
        if completed_steps:
            context["completed_steps"] = completed_steps

        super().__init__(message, "WORKFLOW_ERROR", context, kwargs.get("cause"))
        self.workflow_name = workflow_name
        self.step_name = step_name
        self.step_index = step_index
        self.completed_steps = completed_steps or []


class ErrorCollector:
    """Utility class for collecting and analyzing errors."""

    def __init__(self):
        self.errors: List[RaptorflowError] = []
        self.error_counts: Dict[str, int] = {}

    def add_error(self, error: RaptorflowError) -> None:
        """Add an error to the collection."""
        self.errors.append(error)
        error_type = error.__class__.__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for the specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = [e for e in self.errors if e.timestamp > cutoff_time]

        error_types = {}
        for error in recent_errors:
            error_type = error.__class__.__name__
            error_types[error_type] = error_types.get(error_type, 0) + 1

        return {
            "total_errors": len(recent_errors),
            "error_types": error_types,
            "most_common": (
                max(error_types.items(), key=lambda x: x[1]) if error_types else None
            ),
            "time_period_hours": hours,
        }

    def clear_old_errors(self, hours: int = 24) -> int:
        """Clear errors older than specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        original_count = len(self.errors)
        self.errors = [e for e in self.errors if e.timestamp > cutoff_time]
        return original_count - len(self.errors)


# Global error collector
error_collector = ErrorCollector()


def handle_exception(
    exception: Exception, context: Optional[Dict[str, Any]] = None, reraise: bool = True
) -> RaptorflowError:
    """
    Handle and convert exceptions to RaptorflowError.

    Args:
        exception: Exception to handle
        context: Additional context
        reraise: Whether to reraise the exception

    Returns:
        RaptorflowError instance
    """
    if isinstance(exception, RaptorflowError):
        raptorflow_error = exception
    else:
        raptorflow_error = RaptorflowError(
            message=str(exception), context=context, cause=exception
        )

    # Add to error collector
    error_collector.add_error(raptorflow_error)

    if reraise:
        raise raptorflow_error

    return raptorflow_error


def create_error_response(error: RaptorflowError) -> Dict[str, Any]:
    """
    Create a standardized error response for APIs.

    Args:
        error: RaptorflowError instance

    Returns:
        Error response dictionary
    """
    return {"success": False, "error": error.to_dict()}
