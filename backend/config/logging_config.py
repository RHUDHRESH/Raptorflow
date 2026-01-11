"""
Logging configuration for Raptorflow backend.
"""

import json
import logging
import logging.config
import sys
from datetime import datetime
from typing import Any, Dict

from pythonjsonlogger import jsonlogger

from .settings import get_settings


def configure_logging() -> None:
    """Configure structured logging for the application."""
    settings = get_settings()

    # Create logging configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": jsonlogger.JsonFormatter,
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S",
                "extra": {
                    "environment": settings.ENVIRONMENT.value,
                    "service": settings.APP_NAME,
                    "version": settings.APP_VERSION,
                },
            },
            "pretty": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "json" if settings.LOG_FORMAT == "json" else "pretty",
                "stream": sys.stdout,
            },
            "error_console": {
                "class": "logging.StreamHandler",
                "level": "ERROR",
                "formatter": "json" if settings.LOG_FORMAT == "json" else "pretty",
                "stream": sys.stderr,
            },
        },
        "loggers": {
            "": {  # Root logger
                "level": settings.LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "error": {
                "level": "ERROR",
                "handlers": ["error_console"],
                "propagate": False,
            },
            "uvicorn": {"level": "INFO", "handlers": ["console"], "propagate": False},
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "fastapi": {"level": "INFO", "handlers": ["console"], "propagate": False},
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
            "redis": {"level": "WARNING", "handlers": ["console"], "propagate": False},
            "google.cloud": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

    # Apply configuration
    logging.config.dictConfig(config)

    # Set up request ID logging middleware
    setup_request_id_logging()


def setup_request_id_logging() -> None:
    """Set up request ID logging context."""
    import logging

    class RequestIdFilter(logging.Filter):
        """Filter to add request ID to log records."""

        def filter(self, record):
            # Try to get request ID from context (would be set by middleware)
            record.request_id = getattr(record, "request_id", None)
            record.user_id = getattr(record, "user_id", None)
            record.workspace_id = getattr(record, "workspace_id", None)
            return True

    # Add filter to all handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.addFilter(RequestIdFilter())


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)


class StructuredLogger:
    """Structured logger with additional context."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.base_context = {}

    def with_context(self, **kwargs) -> "StructuredLogger":
        """Create a new logger with additional context."""
        new_logger = StructuredLogger(self.logger.name)
        new_logger.base_context = {**self.base_context, **kwargs}
        return new_logger

    def _log(self, level: int, message: str, **kwargs):
        """Log a message with context."""
        extra = {**self.base_context, **kwargs}
        self.logger.log(level, message, extra=extra)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self._log(logging.CRITICAL, message, **kwargs)

    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        kwargs["exc_info"] = True
        self._log(logging.ERROR, message, **kwargs)


def get_structured_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)


# Logging middleware for FastAPI
async def logging_middleware(request, call_next):
    """FastAPI middleware to add logging context."""
    import uuid
    from time import time

    from fastapi import Request, Response

    # Generate request ID
    request_id = str(uuid.uuid4())

    # Set logging context
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.request_id = request_id
        return record

    logging.setLogRecordFactory(record_factory)

    # Log request
    start_time = time()
    logger = get_structured_logger("request")

    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        user_agent=request.headers.get("user-agent"),
        ip=request.client.host if request.client else None,
    )

    try:
        # Process request
        response = await call_next(request)

        # Log response
        duration = time() - start_time
        logger.info(
            "Request completed",
            status_code=response.status_code,
            duration=duration,
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response

    except Exception as e:
        # Log error
        duration = time() - start_time
        logger.exception(
            "Request failed",
            error=str(e),
            duration=duration,
        )
        raise

    finally:
        # Restore original record factory
        logging.setLogRecordFactory(old_factory)
