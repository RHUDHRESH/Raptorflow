"""
Core logging configuration.

Provides structured logging with appropriate levels for different environments.
"""

import logging
import sys
from typing import Optional


DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def configure_logging(
    level: Optional[str] = None,
    format_string: str = DEFAULT_FORMAT,
) -> None:
    """
    Configure logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Log format string
    """
    level = level or "INFO"

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        stream=sys.stdout,
    )

    _set_noisy_loggers_warning()


def _set_noisy_loggers_warning() -> None:
    """Set appropriate log levels for noisy third-party loggers."""
    noisy_loggers = [
        "httpx",
        "httpcore",
        "hpack",
        "urllib3",
        "asyncio",
        "PIL",
        "sentence_transformers",
    ]

    for logger_name in noisy_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class StructuredLogger:
    """
    Structured logger for better log analysis.

    Provides methods for structured logging with context.
    """

    def __init__(self, name: str):
        self._logger = logging.getLogger(name)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with context."""
        self._logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message with context."""
        self._logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context."""
        self._logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message with context."""
        self._logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with context."""
        self._logger.critical(message, extra=kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """Log exception with traceback."""
        self._logger.exception(message, extra=kwargs)
