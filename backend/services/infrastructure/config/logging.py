"""
Infrastructure - Observability Setup.

This module provides observability infrastructure including:
- Structured logging with context
- Metrics collection
- Distributed tracing
"""

import logging
import sys
from typing import Any, Dict, Optional
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime
import json
import traceback


# Context variables for request tracking
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_ctx: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
workspace_id_ctx: ContextVar[Optional[str]] = ContextVar("workspace_id", default=None)


@dataclass
class LogContext:
    """Structured log context."""

    request_id: Optional[str] = None
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    span_id: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        if self.request_id:
            result["request_id"] = self.request_id
        if self.user_id:
            result["user_id"] = self.user_id
        if self.workspace_id:
            result["workspace_id"] = self.workspace_id
        if self.span_id:
            result["span_id"] = self.span_id
        result.update(self.extra)
        return result


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add context from context variables
        ctx = LogContext(
            request_id=request_id_ctx.get(),
            user_id=user_id_ctx.get(),
            workspace_id=workspace_id_ctx.get(),
        )
        log_data.update(ctx.to_dict())

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data)


def setup_logging(
    level: str = "INFO",
    format: str = "json",
) -> logging.Logger:
    """
    Setup structured logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format: Log format (json, text)

    Returns:
        Configured root logger
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)

    # Set formatter
    if format == "json":
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

    root_logger.addHandler(handler)

    return root_logger


class Logger:
    """
    Structured logger with context support.

    Usage:
        logger = Logger(__name__)
        logger.info("Processing request", extra={"request_id": "123"})
    """

    def __init__(self, name: str):
        self._logger = logging.getLogger(name)

    def _log(
        self,
        level: int,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ):
        """Internal log method."""
        extra_data = extra or {}

        # Get context from context variables
        ctx = LogContext(
            request_id=request_id_ctx.get(),
            user_id=user_id_ctx.get(),
            workspace_id=workspace_id_ctx.get(),
            extra=extra_data,
        )

        # Create log record with extra data
        self._logger.log(
            level,
            message,
            extra={"extra_data": ctx.to_dict()},
            exc_info=exc_info,
        )

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self._log(logging.DEBUG, message, extra)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self._log(logging.INFO, message, extra)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self._log(logging.WARNING, message, extra)

    def error(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = True,
    ):
        """Log error message."""
        self._log(logging.ERROR, message, extra, exc_info)

    def critical(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = True,
    ):
        """Log critical message."""
        self._log(logging.CRITICAL, message, extra, exc_info)


def get_logger(name: str) -> Logger:
    """Get a structured logger."""
    return Logger(name)
