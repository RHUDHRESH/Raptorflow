"""
Central error definitions for RaptorFlow.

Standard exception types and error contract for the backend.
"""

__all__ = [
    "RaptorflowError",
    "PermissionDeniedError",
    "NotFoundError",
    "ValidationFailedError",
    "ConflictError",
    "BudgetExceededError",
]


class RaptorflowError(Exception):
    """
    Base exception class for all RaptorFlow domain errors.

    Provides consistent error structure with code, message, and optional details.
    """

    def __init__(self, message: str, *, code: str, details: dict | None = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class PermissionDeniedError(RaptorflowError):
    """Raised when a user or agent lacks permission to perform an action."""

    def __init__(self, message: str = "Permission denied", details: dict | None = None):
        super().__init__(message, code="PERMISSION_DENIED", details=details)


class NotFoundError(RaptorflowError):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Resource not found", details: dict | None = None):
        super().__init__(message, code="NOT_FOUND", details=details)


class ValidationFailedError(RaptorflowError):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Validation failed", details: dict | None = None):
        super().__init__(message, code="VALIDATION_FAILED", details=details)


class ConflictError(RaptorflowError):
    """Raised when an operation conflicts with existing state."""

    def __init__(self, message: str = "Conflict with existing state", details: dict | None = None):
        super().__init__(message, code="CONFLICT", details=details)


class BudgetExceededError(RaptorflowError):
    """Raised when an LLM call would exceed workspace budget."""

    def __init__(
        self,
        message: str = "Workspace LLM budget exceeded for this period.",
        details: dict | None = None
    ):
        super().__init__(message, code="LLM_BUDGET_EXCEEDED", details=details)
