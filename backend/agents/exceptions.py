"""
Custom exceptions for Raptorflow agents.
"""

from typing import Any, Dict, Optional


class RaptorflowError(Exception):
    """Base exception for all Raptorflow errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging."""
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None,
        }


class ConfigurationError(RaptorflowError):
    """Configuration-related errors."""

    pass


class DatabaseError(RaptorflowError):
    """Database operation errors."""

    pass


class ExecutionError(RaptorflowError):
    """Execution-related errors."""

    pass


class LLMError(RaptorflowError):
    """LLM-related errors."""

    pass


class RoutingError(RaptorflowError):
    """Routing and classification errors."""

    pass


class ToolError(RaptorflowError):
    """Tool execution errors."""

    pass


class WorkspaceError(RaptorflowError):
    """Workspace isolation errors."""

    pass


class CostError(RaptorflowError):
    """Cost tracking and budget errors."""

    pass


class ValidationError(RaptorflowError):
    """Input validation errors."""

    pass


class AuthenticationError(RaptorflowError):
    """Authentication and authorization errors."""

    pass


class AuthorizationError(RaptorflowError):
    """Authorization errors."""

    pass


class TimeoutError(RaptorflowError):
    """Operation timeout errors."""

    pass


class RateLimitError(RaptorflowError):
    """Rate limiting errors."""

    pass


class RegistryError(RaptorflowError):
    """Agent registry errors."""

    pass


class MemoryError(RaptorflowError):
    """Memory-related errors."""

    pass


class MetricsError(RaptorflowError):
    """Metrics collection and reporting errors."""

    pass


class MonitoringError(RaptorflowError):
    """Monitoring and health check errors."""

    pass


class NetworkError(RaptorflowError):
    """Network connectivity errors."""

    pass


class OrchestrationError(RaptorflowError):
    """Orchestration and workflow errors."""

    pass


class SecurityError(RaptorflowError):
    """Security-related errors."""

    pass
