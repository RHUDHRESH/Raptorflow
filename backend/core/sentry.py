"""
Sentry error tracking integration for RaptorFlow
Provides comprehensive error monitoring and performance tracking
"""

import logging
import os
from typing import Any, Dict, Optional

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.base import BaseHTTPMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

logger = logging.getLogger(__name__)


class SentryMiddleware:
    """Sentry error tracking middleware"""

    def __init__(self, app: FastAPI, dsn: Optional[str] = None):
        self.app = app
        self.dsn = dsn or os.getenv("SENTRY_DSN")
        self.environment = os.getenv("ENVIRONMENT", "development")

        if self.dsn:
            self._initialize_sentry()
            self._add_middleware()
        else:
            logger.warning("SENTRY_DSN not configured, error tracking disabled")

    def _initialize_sentry(self):
        """Initialize Sentry SDK"""

        # Configure logging integration
        logging_integration = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR,  # Send errors as events
        )

        # Initialize Sentry
        sentry_sdk.init(
            dsn=self.dsn,
            environment=self.environment,
            integrations=[
                FastApiIntegration(
                    auto_enabling_integrations=False, transaction_style="endpoint"
                ),
                logging_integration,
                RedisIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=0.1,  # Capture 10% of transactions for performance
            profiles_sample_rate=0.1,  # Capture 10% of profiles for performance
            send_default_pii=False,  # Don't send personally identifiable information
            attach_stacktrace=True,  # Include stack traces
            before_send=self._before_send,
            before_breadcrumb=self._before_breadcrumb,
        )

        logger.info("Sentry error tracking initialized")

    def _add_middleware(self):
        """Add Sentry middleware to FastAPI app"""

        class SentryContextMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next):
                # Add user context if available
                try:
                    # Try to get user from request state (set by auth middleware)
                    if hasattr(request.state, "user") and request.state.user:
                        user = request.state.user
                        sentry_sdk.set_user(
                            {
                                "id": user.get("id"),
                                "email": user.get("email"),
                                "subscription_tier": user.get("subscription_tier"),
                            }
                        )

                    # Add workspace context if available
                    if hasattr(request.state, "workspace") and request.state.workspace:
                        workspace = request.state.workspace
                        sentry_sdk.set_tag("workspace_id", workspace.get("id"))

                    # Add request context
                    sentry_sdk.set_context(
                        "request",
                        {
                            "method": request.method,
                            "url": str(request.url),
                            "user_agent": request.headers.get("user-agent"),
                            "client_ip": self._get_client_ip(request),
                        },
                    )

                except Exception as e:
                    logger.warning(f"Failed to set Sentry context: {e}")

                response = await call_next(request)
                return response

            def _get_client_ip(self, request: Request) -> str:
                """Get client IP address from request"""
                forwarded_for = request.headers.get("X-Forwarded-For")
                if forwarded_for:
                    return forwarded_for.split(",")[0].strip()

                real_ip = request.headers.get("X-Real-IP")
                if real_ip:
                    return real_ip

                return request.client.host if request.client else "unknown"

        self.app.add_middleware(SentryContextMiddleware)

    def _before_send(
        self, event: Dict[str, Any], hint: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Filter events before sending to Sentry"""

        # Filter out sensitive data
        if "request" in event and "data" in event["request"]:
            # Remove sensitive form data
            if "form" in event["request"]["data"]:
                sensitive_fields = ["password", "token", "secret", "key", "auth"]
                form_data = event["request"]["data"]["form"]

                for field in sensitive_fields:
                    if field in form_data:
                        form_data[field] = "[FILTERED]"

        # Filter out certain exceptions
        if "exception" in event:
            exception_type = event["exception"].get("values", [{}])[0].get("type")

            # Don't send certain expected exceptions
            ignored_exceptions = [
                "HTTPException",  # FastAPI HTTP exceptions
                "ValidationError",  # Pydantic validation errors
                "CircuitBreakerError",  # Circuit breaker errors
            ]

            if exception_type in ignored_exceptions:
                return None

        # Add custom tags
        event["tags"] = {
            **event.get("tags", {}),
            "service": "raptorflow-backend",
            "version": os.getenv("APP_VERSION", "unknown"),
        }

        return event

    def _before_breadcrumb(
        self, breadcrumb: Dict[str, Any], hint: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Filter breadcrumbs before adding to Sentry"""

        # Filter out sensitive breadcrumb data
        if breadcrumb.get("category") == "http":
            if "data" in breadcrumb:
                # Remove sensitive query parameters
                sensitive_params = ["token", "key", "secret", "password", "auth"]
                data = breadcrumb["data"]

                for param in sensitive_params:
                    if param in data:
                        data[param] = "[FILTERED]"

        return breadcrumb


def init_sentry(app: FastAPI) -> None:
    """Initialize Sentry error tracking"""
    SentryMiddleware(app)


def capture_exception(
    exception: Exception, context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Capture an exception and send to Sentry

    Args:
        exception: Exception to capture
        context: Additional context information

    Returns:
        Sentry event ID
    """
    if context:
        with sentry_sdk.configure_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)

    return sentry_sdk.capture_exception(exception)


def capture_message(message: str, level: str = "info") -> str:
    """
    Capture a message and send to Sentry

    Args:
        message: Message to capture
        level: Log level (info, warning, error)

    Returns:
        Sentry event ID
    """
    return sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id: str, email: Optional[str] = None, **kwargs) -> None:
    """Set user context for Sentry"""
    user_data = {"id": user_id}

    if email:
        user_data["email"] = email

    user_data.update(kwargs)

    sentry_sdk.set_user(user_data)


def set_tag(key: str, value: str) -> None:
    """Set a tag for Sentry"""
    sentry_sdk.set_tag(key, value)


def set_extra(key: str, value: Any) -> None:
    """Set extra data for Sentry"""
    sentry_sdk.set_extra(key, value)


def add_breadcrumb(
    message: str,
    category: Optional[str] = None,
    level: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
) -> None:
    """Add a breadcrumb to Sentry"""
    sentry_sdk.add_breadcrumb(
        message=message, category=category, level=level, data=data
    )


# Decorator for automatic error tracking
def track_errors(operation_name: Optional[str] = None):
    """
    Decorator to automatically track errors in functions

    Args:
        operation_name: Name of the operation for tracking
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            operation = operation_name or f"{func.__module__}.{func.__name__}"

            try:
                # Add breadcrumb for operation start
                add_breadcrumb(
                    message=f"Starting {operation}", category="function", level="info"
                )

                result = await func(*args, **kwargs)

                # Add breadcrumb for operation success
                add_breadcrumb(
                    message=f"Completed {operation}", category="function", level="info"
                )

                return result

            except Exception as e:
                # Capture exception with context
                context = {
                    "operation": operation,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                }

                capture_exception(e, context)

                # Add breadcrumb for operation error
                add_breadcrumb(
                    message=f"Error in {operation}: {str(e)}",
                    category="function",
                    level="error",
                )

                raise

        return wrapper

    return decorator


# Performance monitoring
def start_transaction(name: str, op: str = "function"):
    """Start a Sentry transaction for performance monitoring"""
    return sentry_sdk.start_transaction(name=name, op=op, sampled=True)


def get_health_status() -> Dict[str, Any]:
    """Get Sentry health status"""
    try:
        # Test Sentry connectivity
        test_event_id = capture_message("Sentry health check", level="info")

        return {
            "status": "healthy",
            "dsn_configured": bool(os.getenv("SENTRY_DSN")),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "test_event_id": test_event_id,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "dsn_configured": bool(os.getenv("SENTRY_DSN")),
        }
