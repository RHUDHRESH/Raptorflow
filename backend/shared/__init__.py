"""
Shared Utilities Module
Common utilities used across all domains
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string"""
    return dt.isoformat() if dt else None


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse ISO datetime string"""
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dict"""
    return data.get(key, default) if data else default


def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dict"""
    return {k: v for k, v in data.items() if v is not None}


class AppException(Exception):
    """Base application exception"""

    def __init__(self, message: str, code: str = "ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found"""

    def __init__(self, message: str = "Not found"):
        super().__init__(message, "NOT_FOUND", 404)


class ValidationException(AppException):
    """Validation error"""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, "VALIDATION_ERROR", 400)


class AuthenticationException(AppException):
    """Authentication error"""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, "UNAUTHORIZED", 401)


class AuthorizationException(AppException):
    """Authorization error"""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, "FORBIDDEN", 403)
