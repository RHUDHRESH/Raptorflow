"""
Logging configuration for Raptorflow backend.
Configures structured logging with JSON format, request tracking, and error reporting.
"""

import json
import logging
import logging.config
import sys
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for consistent log output."""

    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        # Create base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add request ID if available
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        # Add workspace ID if available
        if hasattr(record, "workspace_id"):
            log_entry["workspace_id"] = record.workspace_id

        # Add user ID if available
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id

        # Add execution ID if available
        if hasattr(record, "execution_id"):
            log_entry["execution_id"] = record.execution_id

        # Add agent ID if available
        if hasattr(record, "agent_id"):
            log_entry["agent_id"] = record.agent_id

        # Add exception details if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add extra fields if enabled
        if self.include_extra:
            extra_fields = {}
            for key, value in record.__dict__.items():
                if key not in [
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "lineno",
                    "funcName",
                    "created",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                    "getMessage",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                ] and not key.startswith("_"):
                    extra_fields[key] = value

            if extra_fields:
                log_entry["extra"] = extra_fields

        return json.dumps(log_entry, default=str, ensure_ascii=False)


class RequestTrackingFilter(logging.Filter):
    """Filter to add request tracking information to log records."""

    def __init__(self):
        super().__init__()
        self.request_context = {}

    def filter(self, record: logging.LogRecord) -> bool:
        """Add request context to log record."""
        # Add request ID from context
        request_id = self.request_context.get("request_id")
        if request_id:
            record.request_id = request_id

        # Add workspace ID from context
        workspace_id = self.request_context.get("workspace_id")
        if workspace_id:
            record.workspace_id = workspace_id

        # Add user ID from context
        user_id = self.request_context.get("user_id")
        if user_id:
            record.user_id = user_id

        # Add execution ID from context
        execution_id = self.request_context.get("execution_id")
        if execution_id:
            record.execution_id = execution_id

        # Add agent ID from context
        agent_id = self.request_context.get("agent_id")
        if agent_id:
            record.agent_id = agent_id

        return True

    def set_request_context(self, **kwargs):
        """Set request context for subsequent log entries."""
        self.request_context.update(kwargs)

    def clear_request_context(self):
        """Clear request context."""
        self.request_context.clear()


class ErrorReportingHandler(logging.Handler):
    """Handler for error reporting and alerting."""

    def __init__(self, level: int = logging.ERROR):
        super().__init__(level)
        self.error_callbacks = []

    def emit(self, record: logging.LogRecord):
        """Emit error record for reporting."""
        try:
            # Create error report
            error_report = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "request_id": getattr(record, "request_id", None),
                "workspace_id": getattr(record, "workspace_id", None),
                "user_id": getattr(record, "user_id", None),
                "execution_id": getattr(record, "execution_id", None),
                "agent_id": getattr(record, "agent_id", None),
            }

            # Add exception details if present
            if record.exc_info:
                error_report["exception"] = {
                    "type": record.exc_info[0].__name__,
                    "message": str(record.exc_info[1]),
                    "traceback": traceback.format_exception(*record.exc_info),
                }

            # Call error callbacks
            for callback in self.error_callbacks:
                try:
                    callback(error_report)
                except Exception as e:
                    # Don't let error reporting errors cause infinite loops
                    print(f"Error in error reporting callback: {e}", file=sys.stderr)

        except Exception as e:
            print(f"Error in error reporting handler: {e}", file=sys.stderr)

    def add_error_callback(self, callback):
        """Add error reporting callback."""
        self.error_callbacks.append(callback)


class LoggingConfig:
    """Logging configuration manager."""

    def __init__(self):
        self.request_filter = RequestTrackingFilter()
        self.error_handler = ErrorReportingHandler()
        self.configured = False

    def configure_logging(
        self,
        level: str = "INFO",
        format_type: str = "json",
        log_file: Optional[str] = None,
        enable_console: bool = True,
        enable_file: bool = False,
        enable_error_reporting: bool = True,
        module_levels: Optional[Dict[str, str]] = None,
    ):
        """Configure structured logging for the application."""

        # Default module log levels
        default_module_levels = {
            "": level,  # Root logger
            "uvicorn": "INFO",
            "uvicorn.access": "WARNING",
            "uvicorn.error": "INFO",
            "fastapi": "INFO",
            "sqlalchemy": "WARNING",
            "sqlalchemy.engine": "WARNING",
            "sqlalchemy.pool": "WARNING",
            "httpx": "WARNING",
            "websockets": "WARNING",
            "raptorflow": "INFO",
            "raptorflow.agents": "INFO",
            "raptorflow.database": "INFO",
            "raptorflow.cache": "INFO",
            "raptorflow.llm": "INFO",
            "raptorflow.api": "INFO",
        }

        # Override with provided module levels
        if module_levels:
            default_module_levels.update(module_levels)

        # Create logging configuration
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "class": "logging.Formatter",
                    "format": "%(message)s",
                },
                "json_compact": {
                    "class": "logging.Formatter",
                    "format": "%(message)s",
                },
                "console": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "json" if format_type == "json" else "console",
                    "stream": sys.stdout,
                },
                "console_compact": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "json_compact" if format_type == "json" else "console",
                    "stream": sys.stdout,
                },
            },
            "loggers": {},
        }

        # Add file handler if enabled
        if enable_file and log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            config["handlers"]["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "json",
                "filename": str(log_path),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            }

        # Configure loggers
        for logger_name, logger_level in default_module_levels.items():
            config["loggers"][logger_name] = {
                "level": logger_level,
                "handlers": [],
                "propagate": True,
            }

        # Root logger configuration
        root_handlers = []
        if enable_console:
            root_handlers.append("console")
        if enable_file and log_file:
            root_handlers.append("file")

        config["root"] = {"level": level, "handlers": root_handlers}

        # Apply configuration
        logging.config.dictConfig(config)

        self.configured = True

        # Log configuration success
        logger = logging.getLogger(__name__)
        logger.info(
            "Logging configured successfully",
            extra={
                "format_type": format_type,
                "level": level,
                "console_enabled": enable_console,
                "file_enabled": enable_file,
                "error_reporting_enabled": enable_error_reporting,
            },
        )

    def set_request_context(self, **kwargs):
        """Set request context for subsequent log entries."""
        if self.request_filter:
            self.request_filter.set_request_context(**kwargs)

    def clear_request_context(self):
        """Clear request context."""
        if self.request_filter:
            self.request_filter.clear_request_context()

    def add_error_callback(self, callback):
        """Add error reporting callback."""
        if self.error_handler:
            self.error_handler.add_error_callback(callback)

    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance."""
        return logging.getLogger(name)


# Global logging configuration instance
_logging_config = LoggingConfig()


def configure_logging(
    level: str = "INFO",
    format_type: str = "json",
    log_file: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = False,
    enable_error_reporting: bool = True,
    module_levels: Optional[Dict[str, str]] = None,
):
    """Configure logging for the application."""
    _logging_config.configure_logging(
        level=level,
        format_type=format_type,
        log_file=log_file,
        enable_console=enable_console,
        enable_file=enable_file,
        enable_error_reporting=enable_error_reporting,
        module_levels=module_levels,
    )


def set_request_context(**kwargs):
    """Set request context for logging."""
    _logging_config.set_request_context(**kwargs)


def clear_request_context():
    """Clear request context."""
    _logging_config.clear_request_context()


def add_error_callback(callback):
    """Add error reporting callback."""
    _logging_config.add_error_callback(callback)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return _logging_config.get_logger(name)


# Context manager for request tracking
class RequestContext:
    """Context manager for request tracking in logs."""

    def __init__(self, **kwargs):
        self.context = kwargs
        self.previous_context = {}

    def __enter__(self):
        # Store previous context
        if _logging_config.request_filter:
            self.previous_context = (
                _logging_config.request_filter.request_context.copy()
            )

        # Set new context
        set_request_context(**self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore previous context
        if _logging_config.request_filter:
            _logging_config.request_filter.request_context.clear()
            _logging_config.request_filter.request_context.update(self.previous_context)


# Decorator for automatic request ID tracking
def with_request_id(func):
    """Decorator to automatically add request ID to logs."""

    def wrapper(*args, **kwargs):
        # Generate or extract request ID
        request_id = kwargs.get("request_id") or str(uuid.uuid4())

        with RequestContext(request_id=request_id):
            return func(*args, **kwargs)

    return wrapper


# Default error callback for critical errors
def default_error_callback(error_report: Dict[str, Any]):
    """Default error callback for critical errors."""
    # Log to stderr for immediate visibility
    print(f"CRITICAL ERROR: {json.dumps(error_report, default=str)}", file=sys.stderr)

    # In production, this would send to error reporting service
    # e.g., Sentry, DataDog, Cloud Logging, etc.


# Configure default logging on import
if not _logging_config.configured:
    configure_logging(
        level="INFO",
        format_type="json",
        enable_console=True,
        enable_file=False,
        enable_error_reporting=True,
    )

    # Add default error callback
    add_error_callback(default_error_callback)
