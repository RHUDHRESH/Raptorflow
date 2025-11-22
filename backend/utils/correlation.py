"""
Correlation ID utilities for distributed tracing
"""

import uuid
from contextvars import ContextVar
from typing import Optional

# Context variable to store correlation ID for async contexts
_correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


def generate_correlation_id() -> str:
    """Generate a new correlation ID"""
    return str(uuid.uuid4())


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID from context"""
    return _correlation_id.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID in context"""
    _correlation_id.set(correlation_id)


def clear_correlation_id() -> None:
    """Clear correlation ID from context"""
    _correlation_id.set(None)

