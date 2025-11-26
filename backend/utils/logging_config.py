"""
Structured logging configuration for RaptorFlow backend.
Uses structlog for consistent JSON logging with correlation IDs.
"""

import logging
import sys
import structlog
from typing import Any

from backend.config.settings import get_settings


def configure_logging():
    """
    Configures structured logging for the application.
    Outputs JSON logs in production, human-readable in development.
    """
    settings = get_settings()
    
    # Determine if we're in development
    is_dev = settings.ENVIRONMENT == "development" or settings.DEBUG
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # Structlog processors
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if is_dev:
        # Development: Human-readable console output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer()
        ]
    else:
        # Production: JSON output for log aggregation
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> Any:
    """
    Returns a structlog logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        structlog.BoundLogger instance
    """
    return structlog.get_logger(name)


# Alias for backward compatibility
setup_logging = configure_logging
