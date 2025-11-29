"""
Structured logging configuration for RaptorFlow backend.
Uses structlog for consistent JSON logging with correlation IDs.
"""

import contextvars
from typing import Any, Optional
import uuid
import logging
import sys
import structlog


from backend.config.settings import get_settings


# Context variables for request-scoped logging context
correlation_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'correlation_id', default=None
)
workspace_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'workspace_id', default=None
)
user_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'user_id', default=None
)


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for the current request context."""
    correlation_id_ctx.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    """Get the correlation ID from the current request context."""
    return correlation_id_ctx.get()


def set_workspace_id(workspace_id: str) -> None:
    """Set the workspace ID for the current request context."""
    workspace_id_ctx.set(workspace_id)


def get_workspace_id() -> Optional[str]:
    """Get the workspace ID from the current request context."""
    return workspace_id_ctx.get()


def set_user_id(user_id: str) -> None:
    """Set the user ID for the current request context."""
    user_id_ctx.set(user_id)


def get_user_id() -> Optional[str]:
    """Get the user ID from the current request context."""
    return user_id_ctx.get()


def _add_request_context(logger: Any, method_name: str, event_dict: dict) -> dict:
    """
    Structlog processor to add request-scoped context to all log entries.
    """
    correlation_id = get_correlation_id()
    if correlation_id:
        event_dict['correlation_id'] = correlation_id

    workspace_id = get_workspace_id()
    if workspace_id:
        event_dict['workspace_id'] = workspace_id

    user_id = get_user_id()
    if user_id:
        event_dict['user_id'] = user_id

    # Also bind from new request context if available
    try:
        from backend.core.request_context import get_request_context
        ctx = get_request_context()
        if ctx:
            if ctx.workspace_id and 'workspace_id' not in event_dict:
                event_dict['workspace_id'] = ctx.workspace_id
            if ctx.user_id and 'user_id' not in event_dict:
                event_dict['user_id'] = ctx.user_id
            if ctx.correlation_id and 'correlation_id' not in event_dict:
                event_dict['correlation_id'] = ctx.correlation_id
    except ImportError:
        # Request context not available yet - ignore
        pass

    return event_dict


def _add_component_context(logger: Any, method_name: str, event_dict: dict) -> dict:
    """
    Structlog processor to ensure component is in context.
    """
    if 'component' not in event_dict:
        event_dict['component'] = 'unknown'
    return event_dict


def configure_logging():
    """
    Configures structured logging for the application.
    Outputs JSON logs in production, human-readable in development.
    Includes correlation ID and request context processors.
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

    # Structlog processors - now with request context
    shared_processors = [
        _add_request_context,  # Add correlation_id, workspace_id, user_id
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


def get_logger(component: str, name: str = None) -> Any:
    """
    Returns a structlog logger instance pre-bound with component.

    Args:
        component: Component name (e.g. "api", "bus", "agent")
        name: Optional logger name (usually __name__)

    Returns:
        structlog.BoundLogger instance
    """
    return structlog.get_logger(name).bind(component=component)


# Alias for backward compatibility
setup_logging = configure_logging
