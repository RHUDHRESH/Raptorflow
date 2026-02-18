"""
Core shared exceptions.

These exceptions are used across the application layer.
"""

from typing import Any, Optional


class CoreError(Exception):
    """Base exception for all core errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DomainError(CoreError):
    """Base exception for domain-related errors."""

    pass


class ApplicationError(CoreError):
    """Base exception for application layer errors."""

    pass


class AdapterError(CoreError):
    """Base exception for adapter/infrastructure errors."""

    pass


class ValidationError(DomainError):
    """Raised when domain validation fails."""

    pass


class NotFoundError(DomainError):
    """Raised when a domain entity is not found."""

    pass


class ConflictError(DomainError):
    """Raised when a domain constraint is violated."""

    pass
