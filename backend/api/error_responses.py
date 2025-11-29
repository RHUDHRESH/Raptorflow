"""
Error response models and utilities for RaptorFlow API.

Defines the canonical JSON error envelope that all API errors return.
"""

from pydantic import BaseModel
from typing import Any, Optional

from backend.utils.logging_config import get_correlation_id


class ErrorBody(BaseModel):
    """The error body structure within the API response."""
    code: str
    message: str
    details: dict[str, Any] = {}


class ErrorResponse(BaseModel):
    """Canonical error response envelope for all API errors."""
    error: ErrorBody
    correlation_id: Optional[str] = None


def build_error_response(
    code: str,
    message: str,
    details: dict | None = None,
) -> ErrorResponse:
    """
    Build a standardized ErrorResponse.

    Args:
        code: Error code (e.g., 'NOT_FOUND', 'PERMISSION_DENIED')
        message: Human-readable error message
        details: Optional dict of additional error details

    Returns:
        ErrorResponse object ready for JSON serialization
    """
    cid = get_correlation_id()
    return ErrorResponse(
        error=ErrorBody(code=code, message=message, details=details or {}),
        correlation_id=cid,
    )
