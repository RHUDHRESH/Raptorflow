"""
Google Cloud Logging integration for Raptorflow.

Provides structured logging with Cloud Logging integration,
context management, and log aggregation.
"""

import json
import logging
import os
import sys
import threading
import traceback
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from google.api_core import exceptions
from google.cloud import logging as cloud_logging
from google.cloud.logging import Client as LoggingClient
from google.cloud.logging import handlers as cloud_handlers
from google.cloud.logging import LogEntry

from .gcp import get_gcp_client

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogSeverity(Enum):
    """Cloud Logging severity levels."""

    DEFAULT = "DEFAULT"
    DEBUG = "DEBUG"
    INFO = "INFO"
    NOTICE = "NOTICE"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    ALERT = "ALERT"
    EMERGENCY = "EMERGENCY"


@dataclass
class LogContext:
    """Log context information."""

    request_id: Optional[str] = None
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    session_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    component: Optional[str] = None
    function: Optional[str] = None
    line_number: Optional[int] = None
    file_name: Optional[str] = None
    custom_fields: Dict[str, Any] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if self.custom_fields is None:
            self.custom_fields = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        context_dict = {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "session_id": self.session_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "component": self.component,
            "function": self.function,
            "line_number": self.line_number,
            "file_name": self.file_name,
        }

        # Add custom fields
        context_dict.update(self.custom_fields)

        # Remove None values
        return {k: v for k, v in context_dict.items() if v is not None}


class CloudLogging:
    """Google Cloud Logging manager for Raptorflow."""

    def __init__(self):
        self.gcp_client = get_gcp_client()
        self.logger = logging.getLogger("cloud_logging")

        # Get Cloud Logging client
        self.client = self.gcp_client.get_logging_client()

        if not self.client:
            self.logger.warning("Cloud Logging client not available, using standard logging")

        # Project ID
        self.project_id = self.gcp_client.get_project_id()

        # Default log name
        self.log_name = os.getenv("CLOUD_LOG_NAME", "raptorflow")

        # Context storage (thread-local)
        self._context = threading.local()

        # Root logger configuration
        self.root_logger = logging.getLogger()
        self._configured = False

    def configure_logging(
        self,
        level: LogLevel = LogLevel.INFO,
        enable_cloud_logging: bool = True,
        enable_console_logging: bool = True,
        log_format: str = "json",
        custom_handlers: Optional[List[logging.Handler]] = None,
    ):
        """Configure logging for the application."""
        try:
            # Clear existing handlers
            self.root_logger.handlers.clear()

            # Set log level
            log_level = getattr(logging, level.value)
            self.root_logger.setLevel(log_level)

            # Add console handler
            if enable_console_logging:
                console_handler = self._create_console_handler(log_format)
                self.root_logger.addHandler(console_handler)

            # Add Cloud Logging handler
            if enable_cloud_logging and self.client:
                cloud_handler = self._create_cloud_handler()
                self.root_logger.addHandler(cloud_handler)

            # Add custom handlers
            if custom_handlers:
                for handler in custom_handlers:
                    self.root_logger.addHandler(handler)

            self._configured = True
            self.logger.info(f"Logging configured with level: {level.value}")

        except Exception as e:
            self.logger.error(f"Failed to configure logging: {e}")
            raise

    def _create_console_handler(self, log_format: str) -> logging.Handler:
        """Create console logging handler."""
        if log_format == "json":
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(JsonFormatter())
        else:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)

        return handler

    def _create_cloud_handler(self) -> logging.Handler:
        """Create Cloud Logging handler."""
        handler = cloud_handlers.CloudLoggingHandler(
            client=self.client, name=self.log_name
        )

        # Set formatter for structured logging
        handler.setFormatter(CloudLoggingFormatter())

        return handler

    def set_context(self, **kwargs):
        """Set logging context."""
        if not hasattr(self._context, "data"):
            self._context.data = LogContext()

        # Update context
        for key, value in kwargs.items():
            if hasattr(self._context.data, key):
                setattr(self._context.data, key, value)
            else:
                self._context.data.custom_fields[key] = value

    def get_context(self) -> LogContext:
        """Get current logging context."""
        if not hasattr(self._context, "data"):
            self._context.data = LogContext()

        return self._context.data

    def clear_context(self):
        """Clear logging context."""
        self._context.data = LogContext()

    @contextmanager
    def context(self, **kwargs):
        """Context manager for logging context."""
        old_context = self.get_context()

        try:
            self.set_context(**kwargs)
            yield
        finally:
            # Restore old context
            self._context.data = old_context

    def log_with_context(self, level: LogLevel, message: str, **context):
        """Log message with context."""
        if not self._configured:
            self.configure_logging()

        # Get logger
        logger_instance = logging.getLogger()

        # Set context temporarily
        with self.context(**context):
            # Log the message
            log_method = getattr(logger_instance, level.value.lower())
            log_method(message)

    def log_structured(
        self, level: LogLevel, message: str, payload: Dict[str, Any], **context
    ):
        """Log structured message with payload."""
        if not self._configured:
            self.configure_logging()

        # Get current context
        current_context = self.get_context()

        # Merge with provided context
        merged_context = current_context.to_dict()
        merged_context.update(context)

        # Create log entry
        log_entry = {
            "message": message,
            "payload": payload,
            "context": merged_context,
            "timestamp": datetime.utcnow().isoformat(),
            "severity": LogSeverity[level.value].value,
        }

        # Log the structured entry
        logger_instance = logging.getLogger()
        log_method = getattr(logger_instance, level.value.lower())
        log_method(json.dumps(log_entry))

    def log_exception(self, message: str, exception: Exception, **context):
        """Log exception with full traceback."""
        if not self._configured:
            self.configure_logging()

        # Get exception info
        exc_type, exc_value, exc_traceback = sys.exc_info()

        # Create payload with exception details
        payload = {
            "exception_type": exc_type.__name__ if exc_type else None,
            "exception_message": str(exception),
            "exception_module": exc_type.__module__ if exc_type else None,
            "traceback": traceback.format_exception(exc_type, exc_value, exc_traceback),
        }

        # Log as error
        self.log_structured(LogLevel.ERROR, message, payload, **context)

    def log_performance(self, operation: str, duration_ms: float, **context):
        """Log performance metric."""
        payload = {
            "operation": operation,
            "duration_ms": duration_ms,
            "performance_metric": True,
        }

        self.log_structured(
            LogLevel.INFO, f"Performance: {operation}", payload, **context
        )

    def log_api_request(
        self, method: str, path: str, status_code: int, duration_ms: float, **context
    ):
        """Log API request."""
        payload = {
            "api_request": True,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
        }

        # Determine log level based on status code
        if status_code >= 500:
            level = LogLevel.ERROR
        elif status_code >= 400:
            level = LogLevel.WARNING
        else:
            level = LogLevel.INFO

        self.log_structured(level, f"API Request: {method} {path}", payload, **context)

    def log_user_action(self, action: str, **context):
        """Log user action."""
        payload = {"user_action": True, "action": action}

        self.log_structured(LogLevel.INFO, f"User Action: {action}", payload, **context)

    def log_security_event(
        self, event_type: str, severity: LogLevel = LogLevel.WARNING, **context
    ):
        """Log security event."""
        payload = {"security_event": True, "event_type": event_type}

        self.log_structured(
            severity, f"Security Event: {event_type}", payload, **context
        )

    def log_business_event(self, event_type: str, **context):
        """Log business event."""
        payload = {"business_event": True, "event_type": event_type}

        self.log_structured(
            LogLevel.INFO, f"Business Event: {event_type}", payload, **context
        )

    def create_logger(self, name: str) -> logging.Logger:
        """Create a logger with Cloud Logging integration."""
        logger_instance = logging.getLogger(name)

        if not self._configured:
            self.configure_logging()

        return logger_instance

    def async_log(self, level: LogLevel, message: str, **context):
        """Async logging (for use in async contexts)."""
        self.log_with_context(level, message, **context)

    def get_log_entries(
        self,
        filter_expression: Optional[str] = None,
        max_results: int = 100,
        order_by: str = "timestamp desc",
    ) -> List[Dict[str, Any]]:
        """Get log entries from Cloud Logging."""
        try:
            # Build filter
            if filter_expression:
                filter_expr = filter_expression
            else:
                filter_expr = (
                    f'logName="projects/{self.project_id}/logs/{self.log_name}"'
                )

            # List entries
            entries = []
            for entry in self.client.list_entries(
                filter_=filter_expr, max_results=max_results, order_by=order_by
            ):
                # Convert to dictionary
                entry_dict = {
                    "timestamp": (
                        entry.timestamp.isoformat() if entry.timestamp else None
                    ),
                    "severity": entry.severity.name if entry.severity else None,
                    "message": entry.payload,
                    "resource": (
                        {
                            "type": entry.resource.type,
                            "labels": dict(entry.resource.labels),
                        }
                        if entry.resource
                        else None
                    ),
                    "labels": dict(entry.labels) if entry.labels else None,
                }

                entries.append(entry_dict)

            return entries

        except Exception as e:
            self.logger.error(f"Failed to get log entries: {e}")
            return []

    def get_log_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get logging statistics."""
        try:
            # Build filter for recent logs
            filter_expr = (
                f'timestamp>="{datetime.now() - timedelta(hours=hours).isoformat()}"'
            )
            filter_expr += (
                f' AND logName="projects/{self.project_id}/logs/{self.log_name}"'
            )

            # Get entries
            entries = self.get_log_entries(filter_expr, max_results=1000)

            # Calculate stats
            stats = {
                "total_entries": len(entries),
                "time_period_hours": hours,
                "severity_counts": {},
                "top_messages": {},
                "error_rate": 0.0,
            }

            error_count = 0

            for entry in entries:
                # Count by severity
                severity = entry.get("severity", "UNKNOWN")
                stats["severity_counts"][severity] = (
                    stats["severity_counts"].get(severity, 0) + 1
                )

                # Count errors
                if severity in ["ERROR", "CRITICAL", "ALERT", "EMERGENCY"]:
                    error_count += 1

                # Count by message
                message = entry.get("message", "")
                if len(message) > 100:
                    message = message[:100] + "..."
                stats["top_messages"][message] = (
                    stats["top_messages"].get(message, 0) + 1
                )

            # Calculate error rate
            if stats["total_entries"] > 0:
                stats["error_rate"] = (error_count / stats["total_entries"]) * 100

            # Sort top messages
            stats["top_messages"] = dict(
                sorted(stats["top_messages"].items(), key=lambda x: x[1], reverse=True)[
                    :10
                ]
            )

            return stats

        except Exception as e:
            self.logger.error(f"Failed to get log stats: {e}")
            return {}

    def export_logs(
        self,
        output_file: str,
        filter_expression: Optional[str] = None,
        format: str = "json",
    ) -> bool:
        """Export logs to file."""
        try:
            entries = self.get_log_entries(filter_expression)

            if format == "json":
                with open(output_file, "w") as f:
                    json.dump(entries, f, indent=2, default=str)
            else:
                with open(output_file, "w") as f:
                    for entry in entries:
                        f.write(
                            f"{entry['timestamp']} - {entry['severity']} - {entry['message']}\n"
                        )

            self.logger.info(f"Exported {len(entries)} log entries to {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export logs: {e}")
            return False

    def flush_logs(self):
        """Flush all log handlers."""
        try:
            for handler in self.root_logger.handlers:
                handler.flush()

            self.logger.info("Flushed all log handlers")

        except Exception as e:
            self.logger.error(f"Failed to flush logs: {e}")


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record):
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields
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
            ]:
                log_entry[key] = value

        return json.dumps(log_entry)


class CloudLoggingFormatter(logging.Formatter):
    """Cloud Logging formatter with context support."""

    def __init__(self):
        super().__init__()
        self.cloud_logging = get_cloud_logging()

    def format(self, record):
        """Format log record for Cloud Logging."""
        # Get current context
        context = self.cloud_logging.get_context()

        # Create log entry
        log_entry = {
            "message": record.getMessage(),
            "severity": record.levelname,
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add context
        context_dict = context.to_dict()
        if context_dict:
            log_entry["context"] = context_dict

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields
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
            ]:
                log_entry[key] = value

        return json.dumps(log_entry)


# Global Cloud Logging instance
_cloud_logging: Optional[CloudLogging] = None


def get_cloud_logging() -> CloudLogging:
    """Get global Cloud Logging instance."""
    global _cloud_logging
    if _cloud_logging is None:
        _cloud_logging = CloudLogging()
    return _cloud_logging


def configure_logging(
    level: LogLevel = LogLevel.INFO,
    enable_cloud_logging: bool = True,
    enable_console_logging: bool = True,
    log_format: str = "json",
):
    """Configure logging for the application."""
    cloud_logging = get_cloud_logging()
    cloud_logging.configure_logging(
        level, enable_cloud_logging, enable_console_logging, log_format
    )


def log_with_context(level: LogLevel, message: str, **context):
    """Log message with context."""
    cloud_logging = get_cloud_logging()
    cloud_logging.log_with_context(level, message, **context)


def log_structured(level: LogLevel, message: str, payload: Dict[str, Any], **context):
    """Log structured message with payload."""
    cloud_logging = get_cloud_logging()
    cloud_logging.log_structured(level, message, payload, **context)


def log_exception(message: str, exception: Exception, **context):
    """Log exception with full traceback."""
    cloud_logging = get_cloud_logging()
    cloud_logging.log_exception(message, exception, **context)


def log_performance(operation: str, duration_ms: float, **context):
    """Log performance metric."""
    cloud_logging = get_cloud_logging()
    cloud_logging.log_performance(operation, duration_ms, **context)


def log_api_request(
    method: str, path: str, status_code: int, duration_ms: float, **context
):
    """Log API request."""
    cloud_logging = get_cloud_logging()
    cloud_logging.log_api_request(method, path, status_code, duration_ms, **context)


def log_user_action(action: str, **context):
    """Log user action."""
    cloud_logging = get_cloud_logging()
    cloud_logging.log_user_action(action, **context)


def log_security_event(
    event_type: str, severity: LogLevel = LogLevel.WARNING, **context
):
    """Log security event."""
    cloud_logging = get_cloud_logging()
    cloud_logging.log_security_event(event_type, severity, **context)


def log_business_event(event_type: str, **context):
    """Log business event."""
    cloud_logging = get_cloud_logging()
    cloud_logging.log_business_event(event_type, **context)


def set_logging_context(**kwargs):
    """Set logging context."""
    cloud_logging = get_cloud_logging()
    cloud_logging.set_context(**kwargs)


def get_logging_context() -> LogContext:
    """Get current logging context."""
    cloud_logging = get_cloud_logging()
    return cloud_logging.get_context()


def clear_logging_context():
    """Clear logging context."""
    cloud_logging = get_cloud_logging()
    cloud_logging.clear_context()


@contextmanager
def logging_context(**kwargs):
    """Context manager for logging context."""
    cloud_logging = get_cloud_logging()
    with cloud_logging.context(**kwargs):
        yield


def create_logger(name: str) -> logging.Logger:
    """Create a logger with Cloud Logging integration."""
    cloud_logging = get_cloud_logging()
    return cloud_logging.create_logger(name)


# Decorators for automatic context logging
def log_function_calls(level: LogLevel = LogLevel.DEBUG):
    """Decorator to log function calls."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            cloud_logging = get_cloud_logging()

            with cloud_logging.context(
                function=func.__name__,
                module=func.__module__,
                line_number=func.__code__.co_firstlineno,
                file_name=func.__code__.co_filename,
            ):
                start_time = datetime.now()

                try:
                    result = func(*args, **kwargs)
                    duration_ms = (datetime.now() - start_time).total_seconds() * 1000

                    cloud_logging.log_performance(
                        f"function_call:{func.__name__}", duration_ms, success=True
                    )

                    return result

                except Exception as e:
                    duration_ms = (datetime.now() - start_time).total_seconds() * 1000

                    cloud_logging.log_performance(
                        f"function_call:{func.__name__}",
                        duration_ms,
                        success=False,
                        error=str(e),
                    )

                    cloud_logging.log_exception(f"Function {func.__name__} failed", e)

                    raise

        return wrapper

    return decorator


def log_api_calls(level: LogLevel = LogLevel.INFO):
    """Decorator to log API calls."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            cloud_logging = get_cloud_logging()

            start_time = datetime.now()

            try:
                result = func(*args, **kwargs)
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000

                # Try to extract request info from args
                method = "UNKNOWN"
                path = "UNKNOWN"
                status_code = 200

                if args and hasattr(args[0], "method"):
                    method = args[0].method
                if args and hasattr(args[0], "path"):
                    path = args[0].path

                cloud_logging.log_api_request(method, path, status_code, duration_ms)

                return result

            except Exception as e:
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000

                cloud_logging.log_api_request(method, path, 500, duration_ms)
                cloud_logging.log_exception(f"API call failed", e)

                raise

        return wrapper

    return decorator
