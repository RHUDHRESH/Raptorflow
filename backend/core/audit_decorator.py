"""
Audit logging decorator for automatic API endpoint logging
"""

import functools
import logging
import time
from typing import Any, Callable

from fastapi import Request, Response

from .audit import get_audit_logger

logger = logging.getLogger(__name__)


def audit_endpoint(
    action: str,
    resource_type: str,
    get_resource_id: Callable = None,
    include_request_body: bool = False,
    include_response_body: bool = False,
):
    """
    Decorator to automatically audit API endpoints

    Args:
        action: Action being performed (create, read, update, delete, etc.)
        resource_type: Type of resource being accessed
        get_resource_id: Function to extract resource ID from request/response
        include_request_body: Whether to include request body in audit log
        include_response_body: Whether to include response body in audit log
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Extract request from function arguments
            request = None
            user_id = None
            workspace_id = None

            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            # Get user and workspace from request state if available
            if request:
                user_id = getattr(request.state, "user", None)
                if user_id:
                    user_id = user_id.id
                workspace_id = getattr(request.state, "workspace_id", None)

            # Get client info
            client_ip = None
            user_agent = None
            if request:
                client_ip = (
                    request.headers.get("x-forwarded-for", "").split(",")[0].strip()
                    or request.headers.get("x-real-ip")
                    or (request.client.host if request.client else "unknown")
                )
                user_agent = request.headers.get("user-agent")

            # Prepare audit details
            details = {
                "endpoint": request.url.path if request else "unknown",
                "method": request.method if request else "unknown",
            }

            # Add request body if requested (excluding sensitive data)
            if include_request_body and request:
                try:
                    body = await request.body()
                    if body:
                        # Don't log sensitive data
                        body_str = body.decode("utf-8")
                        sensitive_fields = [
                            "password",
                            "token",
                            "secret",
                            "key",
                            "credit_card",
                        ]

                        for field in sensitive_fields:
                            if field in body_str.lower():
                                body_str = "[REDACTED - SENSITIVE DATA]"
                                break

                        details["request_body"] = body_str[:1000]  # Limit to 1000 chars
                except Exception:
                    pass  # Don't fail if we can't read body

            # Get resource ID if function provided
            resource_id = None
            if get_resource_id:
                try:
                    resource_id = get_resource_id(*args, **kwargs)
                except Exception:
                    pass

            # Execute the function
            start_time = time.time()
            success = True
            error_message = None
            response = None

            try:
                response = await func(*args, **kwargs)
                return response
            except Exception as e:
                success = False
                error_message = str(e)
                logger.error(f"API endpoint error: {e}")
                raise
            finally:
                # Add response info if requested
                if include_response_body and response and hasattr(response, "body"):
                    try:
                        response_body = response.body
                        if response_body:
                            details["response_body"] = response_body.decode("utf-8")[
                                :500
                            ]  # Limit to 500 chars
                    except Exception:
                        pass

                # Add execution time
                execution_time = time.time() - start_time
                details["execution_time_ms"] = int(execution_time * 1000)

                # Log the audit event
                audit_logger = get_audit_logger()
                await audit_logger.log_action(
                    user_id=user_id,
                    workspace_id=workspace_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=details,
                    ip_address=client_ip,
                    user_agent=user_agent,
                    success=success,
                    error_message=error_message,
                )

        return wrapper

    return decorator


# Convenience decorators for common actions
def audit_create(resource_type: str, **kwargs):
    """Audit create operations"""
    return audit_endpoint("create", resource_type, **kwargs)


def audit_read(resource_type: str, **kwargs):
    """Audit read operations"""
    return audit_endpoint("read", resource_type, **kwargs)


def audit_update(resource_type: str, **kwargs):
    """Audit update operations"""
    return audit_endpoint("update", resource_type, **kwargs)


def audit_delete(resource_type: str, **kwargs):
    """Audit delete operations"""
    return audit_endpoint("delete", resource_type, **kwargs)


def audit_access(resource_type: str, **kwargs):
    """Audit access operations"""
    return audit_endpoint("access", resource_type, **kwargs)
