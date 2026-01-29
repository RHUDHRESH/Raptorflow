"""
Logging System for Cognitive Engine

Comprehensive logging system with structured logging and multiple handlers.
Implements PROMPT 97 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import logging
import logging.handlers
import os
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Import metrics for logging metrics
from cognitive_metrics import MetricCategory, MetricType, get_metrics_collector


class LogLevel(Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(Enum):
    """Log formats."""

    SIMPLE = "simple"
    STRUCTURED = "structured"
    JSON = "json"
    DETAILED = "detailed"


@dataclass
class LogEntry:
    """Structured log entry."""

    timestamp: datetime
    level: LogLevel
    logger_name: str
    message: str
    module: str
    function: str
    line_number: int
    thread_id: int
    process_id: int
    user_id: Optional[str] = None
    workspace_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    execution_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    exception: Optional[Dict[str, Any]] = None


class StructuredFormatter(logging.Formatter):
    """Structured log formatter."""

    def __init__(self, format_type: LogFormat = LogFormat.STRUCTURED):
        super().__init__()
        self.format_type = format_type

    def format(self, record: logging.LogRecord) -> str:
        """Format log record."""
        # Create structured log entry
        log_entry = LogEntry(
            timestamp=datetime.fromtimestamp(record.created),
            level=LogLevel(record.levelname),
            logger_name=record.name,
            message=record.getMessage(),
            module=record.module,
            function=record.funcName,
            line_number=record.lineno,
            thread_id=record.thread,
            process_id=record.process,
            user_id=getattr(record, "user_id", None),
            workspace_id=getattr(record, "workspace_id", None),
            session_id=getattr(record, "session_id", None),
            request_id=getattr(record, "request_id", None),
            execution_id=getattr(record, "execution_id", None),
            metadata=getattr(record, "metadata", {}),
            exception=self._format_exception(record) if record.exc_info else None,
        )

        # Format based on type
        if self.format_type == LogFormat.JSON:
            return self._format_json(log_entry)
        elif self.format_type == LogFormat.STRUCTURED:
            return self._format_structured(log_entry)
        elif self.format_type == LogFormat.DETAILED:
            return self._format_detailed(log_entry)
        else:
            return self._format_simple(log_entry)

    def _format_json(self, entry: LogEntry) -> str:
        """Format as JSON."""
        return json.dumps(
            {
                "timestamp": entry.timestamp.isoformat(),
                "level": entry.level.value,
                "logger": entry.logger_name,
                "message": entry.message,
                "module": entry.module,
                "function": entry.function,
                "line": entry.line_number,
                "thread_id": entry.thread_id,
                "process_id": entry.process_id,
                "user_id": entry.user_id,
                "workspace_id": entry.workspace_id,
                "session_id": entry.session_id,
                "request_id": entry.request_id,
                "execution_id": entry.execution_id,
                "metadata": entry.metadata,
                "exception": entry.exception,
            }
        )

    def _format_structured(self, entry: LogEntry) -> str:
        """Format as structured text."""
        parts = [
            f"[{entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}]",
            f"[{entry.level.value}]",
            f"[{entry.logger_name}]",
            f"[{entry.module}:{entry.function}:{entry.line_number}]",
            entry.message,
        ]

        # Add context information
        context_parts = []
        if entry.user_id:
            context_parts.append(f"user:{entry.user_id}")
        if entry.workspace_id:
            context_parts.append(f"workspace:{entry.workspace_id}")
        if entry.session_id:
            context_parts.append(f"session:{entry.session_id}")
        if entry.request_id:
            context_parts.append(f"request:{entry.request_id}")
        if entry.execution_id:
            context_parts.append(f"execution:{entry.execution_id}")

        if context_parts:
            parts.append(f"[{' '.join(context_parts)}]")

        # Add metadata
        if entry.metadata:
            parts.append(f"metadata:{json.dumps(entry.metadata)}")

        # Add exception
        if entry.exception:
            parts.append(f"exception:{entry.exception}")

        return " ".join(parts)

    def _format_detailed(self, entry: LogEntry) -> str:
        """Format as detailed text."""
        lines = [
            f"Timestamp: {entry.timestamp.isoformat()}",
            f"Level: {entry.level.value}",
            f"Logger: {entry.logger_name}",
            f"Module: {entry.module}",
            f"Function: {entry.function}",
            f"Line: {entry.line_number}",
            f"Thread ID: {entry.thread_id}",
            f"Process ID: {entry.process_id}",
            f"Message: {entry.message}",
        ]

        # Add context information
        if entry.user_id:
            lines.append(f"User ID: {entry.user_id}")
        if entry.workspace_id:
            lines.append(f"Workspace ID: {entry.workspace_id}")
        if entry.session_id:
            lines.append(f"Session ID: {entry.session_id}")
        if entry.request_id:
            lines.append(f"Request ID: {entry.request_id}")
        if entry.execution_id:
            lines.append(f"Execution ID: {entry.execution_id}")

        # Add metadata
        if entry.metadata:
            lines.append("Metadata:")
            for key, value in entry.metadata.items():
                lines.append(f"  {key}: {value}")

        # Add exception
        if entry.exception:
            lines.append("Exception:")
            lines.append(f"  Type: {entry.exception.get('type', 'Unknown')}")
            lines.append(f"  Message: {entry.exception.get('message', 'No message')}")
            lines.append(
                f"  Traceback: {entry.exception.get('traceback', 'No traceback')}"
            )

        return "\n".join(lines)

    def _format_simple(self, entry: LogEntry) -> str:
        """Format as simple text."""
        return f"[{entry.timestamp.strftime('%H:%M:%S')}] [{entry.level.value}] {entry.logger_name}: {entry.message}"

    def _format_exception(self, record: logging.LogRecord) -> Optional[Dict[str, Any]]:
        """Format exception information."""
        if not record.exc_info:
            return None

        exc_type, exc_value, exc_tb = record.exc_info

        return {
            "type": exc_type.__name__ if exc_type else "Unknown",
            "message": str(exc_value) if exc_value else "No message",
            "traceback": "".join(
                traceback.format_exception(exc_type, exc_value, exc_tb)
            ),
        }


class CognitiveLogger:
    """
    Comprehensive logging system for cognitive engine.

    Provides structured logging with context and metrics integration.
    """

    def __init__(
        self,
        name: str = "cognitive_engine",
        level: LogLevel = LogLevel.INFO,
        log_format: LogFormat = LogFormat.STRUCTURED,
    ):
        """
        Initialize cognitive logger.

        Args:
            name: Logger name
            level: Log level
            log_format: Log format
        """
        self.name = name
        self.level = level
        self.log_format = log_format

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))

        # Setup handlers
        self.handlers: List[logging.Handler] = []
        self._setup_handlers()

        # Metrics collector
        self.metrics_collector = get_metrics_collector()

        # Context storage
        self.context: Dict[str, Any] = {}

    def _setup_handlers(self) -> None:
        """Setup log handlers."""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.level.value))
        console_handler.setFormatter(StructuredFormatter(self.log_format))
        self.logger.addHandler(console_handler)
        self.handlers.append(console_handler)

        # File handler
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{self.name}.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(getattr(logging, self.level.value))
        file_handler.setFormatter(StructuredFormatter(LogFormat.JSON))
        self.logger.addHandler(file_handler)
        self.handlers.append(file_handler)

        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"{self.name}_errors.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter(LogFormat.DETAILED))
        self.logger.addHandler(error_handler)
        self.handlers.append(error_handler)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self._log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self._log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self._log(LogLevel.CRITICAL, message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """Log exception message."""
        kwargs["exc_info"] = True
        self._log(LogLevel.ERROR, message, **kwargs)

    def _log(self, level: LogLevel, message: str, **kwargs) -> None:
        """Internal logging method."""
        # Create log record with extra context
        extra = {
            "user_id": self.context.get("user_id"),
            "workspace_id": self.context.get("workspace_id"),
            "session_id": self.context.get("session_id"),
            "request_id": self.context.get("request_id"),
            "execution_id": self.context.get("execution_id"),
            "metadata": kwargs.get("metadata", {}),
        }

        # Add any additional context
        for key, value in kwargs.items():
            if key not in ["exc_info", "metadata"]:
                extra[key] = value

        # Log the message
        getattr(self.logger, level.value.lower())(message, extra=extra)

        # Record metrics
        self._record_log_metric(level)

    def _record_log_metric(self, level: LogLevel) -> None:
        """Record logging metrics."""
        metric_name = f"log_{level.value.lower()}_count"
        self.metrics_collector.increment_counter(metric_name)

    def set_context(self, **kwargs) -> None:
        """Set logging context."""
        self.context.update(kwargs)

    def clear_context(self) -> None:
        """Clear logging context."""
        self.context.clear()

    def with_context(self, **kwargs):
        """Context manager for temporary context."""
        return LogContext(self, **kwargs)

    def add_handler(self, handler: logging.Handler) -> None:
        """Add a custom handler."""
        self.logger.addHandler(handler)
        self.handlers.append(handler)

    def remove_handler(self, handler: logging.Handler) -> bool:
        """Remove a handler."""
        if handler in self.handlers:
            self.logger.removeHandler(handler)
            self.handlers.remove(handler)
            return True
        return False

    def set_level(self, level: LogLevel) -> None:
        """Set log level."""
        self.level = level
        self.logger.setLevel(getattr(logging, level.value))

        # Update handler levels
        for handler in self.handlers:
            if (
                not isinstance(handler, logging.handlers.RotatingFileHandler)
                or "errors" not in handler.baseFilename
            ):
                handler.setLevel(getattr(logging, level.value))

    def set_format(self, log_format: LogFormat) -> None:
        """Set log format."""
        self.log_format = log_format

        # Update formatters
        for handler in self.handlers:
            handler.setFormatter(StructuredFormatter(log_format))

    def get_handler_info(self) -> List[Dict[str, Any]]:
        """Get information about handlers."""
        handler_info = []

        for handler in self.handlers:
            info = {
                "type": type(handler).__name__,
                "level": logging.getLevelName(handler.level),
                "formatter": (
                    type(handler.formatter).__name__ if handler.formatter else None
                ),
            }

            if isinstance(handler, logging.FileHandler):
                info["filename"] = handler.baseFilename
            elif isinstance(handler, logging.handlers.RotatingFileHandler):
                info["filename"] = handler.baseFilename
                info["max_bytes"] = handler.maxBytes
                info["backup_count"] = handler.backupCount
            elif isinstance(handler, logging.StreamHandler):
                info["stream"] = handler.stream.name

            handler_info.append(info)

        return handler_info

    def get_log_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        stats = {
            "logger_name": self.name,
            "level": self.level.value,
            "format": self.log_format.value,
            "handler_count": len(self.handlers),
            "context": self.context.copy(),
        }

        # Add metrics if available
        try:
            log_metrics = {
                "debug_count": self.metrics_collector.get_summary("log_debug_count"),
                "info_count": self.metrics_collector.get_summary("log_info_count"),
                "warning_count": self.metrics_collector.get_summary(
                    "log_warning_count"
                ),
                "error_count": self.metrics_collector.get_summary("log_error_count"),
                "critical_count": self.metrics_collector.get_summary(
                    "log_critical_count"
                ),
            }
            stats["log_metrics"] = log_metrics
        except:
            stats["log_metrics"] = {}

        return stats


class LogContext:
    """Context manager for temporary logging context."""

    def __init__(self, logger: CognitiveLogger, **kwargs):
        self.logger = logger
        self.context = kwargs
        self.old_context = {}

    def __enter__(self):
        self.old_context = self.logger.context.copy()
        self.logger.set_context(**self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.context = self.old_context


# Global logger instances
_loggers: Dict[str, CognitiveLogger] = {}


def get_logger(
    name: str = "cognitive_engine",
    level: LogLevel = LogLevel.INFO,
    log_format: LogFormat = LogFormat.STRUCTURED,
) -> CognitiveLogger:
    """Get or create a logger instance."""
    if name not in _loggers:
        _loggers[name] = CognitiveLogger(name, level, log_format)
    return _loggers[name]


def set_log_level(level: LogLevel, logger_name: str = None) -> None:
    """Set log level for all loggers or specific logger."""
    if logger_name:
        if logger_name in _loggers:
            _loggers[logger_name].set_level(level)
    else:
        for logger in _loggers.values():
            logger.set_level(level)


def set_log_format(log_format: LogFormat, logger_name: str = None) -> None:
    """Set log format for all loggers or specific logger."""
    if logger_name:
        if logger_name in _loggers:
            _loggers[logger_name].set_format(log_format)
    else:
        for logger in _loggers.values():
            logger.set_format(log_format)


def get_all_loggers() -> Dict[str, CognitiveLogger]:
    """Get all logger instances."""
    return _loggers.copy()


def get_logger_stats(logger_name: str = None) -> Dict[str, Any]:
    """Get logging statistics."""
    if logger_name and logger_name in _loggers:
        return _loggers[logger_name].get_log_stats()
    else:
        return {name: logger.get_log_stats() for name, logger in _loggers.items()}


# Decorators for automatic logging
def logged(logger_name: str = "cognitive_engine", level: LogLevel = LogLevel.INFO):
    """Decorator to automatically log function calls."""

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            async def wrapper(*args, **kwargs):
                logger = get_logger(logger_name, level)
                func_name = f"{func.__module__}.{func.__name__}"

                logger.info(
                    f"Starting {func_name}",
                    function=func.__name__,
                    module=func.__module__,
                )

                try:
                    result = await func(*args, **kwargs)
                    logger.info(
                        f"Completed {func_name}",
                        function=func.__name__,
                        module=func.__module__,
                    )
                    return result
                except Exception as e:
                    logger.exception(
                        f"Error in {func_name}: {str(e)}",
                        function=func.__name__,
                        module=func.__module__,
                    )
                    raise

            return wrapper
        else:

            def wrapper(*args, **kwargs):
                logger = get_logger(logger_name, level)
                func_name = f"{func.__module__}.{func.__name__}"

                logger.info(
                    f"Starting {func_name}",
                    function=func.__name__,
                    module=func.__module__,
                )

                try:
                    result = func(*args, **kwargs)
                    logger.info(
                        f"Completed {func_name}",
                        function=func.__name__,
                        module=func.__module__,
                    )
                    return result
                except Exception as e:
                    logger.exception(
                        f"Error in {func_name}: {str(e)}",
                        function=func.__name__,
                        module=func.__module__,
                    )
                    raise

            return wrapper

    return decorator


def debug_logged(logger_name: str = "cognitive_engine"):
    """Decorator to automatically debug log function calls."""
    return logged(logger_name, LogLevel.DEBUG)


def error_logged(logger_name: str = "cognitive_engine"):
    """Decorator to automatically error log function calls."""
    return logged(logger_name, LogLevel.ERROR)


# Utility functions
def setup_logging(config: Dict[str, Any] = None) -> None:
    """Setup logging configuration."""
    config = config or {}

    # Configure root logger
    root_level = config.get("level", LogLevel.INFO)
    log_format = config.get("format", LogFormat.STRUCTURED)

    # Set global defaults
    set_log_level(root_level)
    set_log_format(log_format)

    # Create default loggers
    default_loggers = [
        "cognitive_engine",
        "perception",
        "planning",
        "reflection",
        "critic",
        "api",
        "monitoring",
    ]

    for logger_name in default_loggers:
        get_logger(logger_name, root_level, log_format)


def configure_file_logging(
    log_dir: str = "logs", max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5
) -> None:
    """Configure file logging for all loggers."""
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    for logger in _loggers.values():
        # Remove existing file handlers
        file_handlers = [
            h
            for h in logger.handlers
            if isinstance(
                h, (logging.FileHandler, logging.handlers.RotatingFileHandler)
            )
        ]

        for handler in file_handlers:
            logger.remove_handler(handler)

        # Add new file handlers
        # Main log file
        main_handler = logging.handlers.RotatingFileHandler(
            log_path / f"{logger.name}.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        main_handler.setLevel(getattr(logging, logger.level.value))
        main_handler.setFormatter(StructuredFormatter(LogFormat.JSON))
        logger.add_handler(main_handler)

        # Error log file
        error_handler = logging.handlers.RotatingFileHandler(
            log_path / f"{logger.name}_errors.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter(LogFormat.DETAILED))
        logger.add_handler(error_handler)


def configure_syslog_logging(address: str = "localhost:514") -> None:
    """Configure syslog logging for all loggers."""
    try:
        import logging.handlers

        for logger in _loggers.values():
            syslog_handler = logging.handlers.SysLogHandler(address=address)
            syslog_handler.setLevel(getattr(logging, logger.level.value))
            syslog_handler.setFormatter(StructuredFormatter(LogFormat.STRUCTURED))
            logger.add_handler(syslog_handler)
    except ImportError:
        pass  # SysLogHandler not available


def configure_cloud_logging(service_name: str, config: Dict[str, Any] = None) -> None:
    """Configure cloud logging (placeholder for services like AWS CloudWatch, etc.)."""
    # This would integrate with cloud logging services
    pass


# Example usage
if __name__ == "__main__":
    # Setup logging
    setup_logging({"level": LogLevel.INFO, "format": LogFormat.STRUCTURED})

    # Get logger
    logger = get_logger("test")

    # Test logging
    logger.info("Test message", user_id="user123", workspace_id="ws456")

    # Test with context
    with logger.with_context(user_id="user123", workspace_id="ws456"):
        logger.info("Message with context")

    # Test decorator
    @logged()
    def test_function():
        return "test result"

    result = test_function()
    print(f"Result: {result}")
