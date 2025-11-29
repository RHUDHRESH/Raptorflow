"""
Middleware for RaptorFlow backend.
Includes correlation ID handling for request tracing.
"""

import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

from backend.utils.logging_config import set_correlation_id


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle correlation ID for request tracing.

    - Extracts correlation ID from X-Correlation-ID header if present
    - Otherwise generates a new UUIDv4
    - Sets it in the response headers
    - Stores it in context var for logging
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract or generate correlation ID
        incoming_correlation_id = request.headers.get("X-Correlation-ID")

        if incoming_correlation_id:
            correlation_id = incoming_correlation_id
        else:
            correlation_id = str(uuid.uuid4())

        # Set in context for logging
        set_correlation_id(correlation_id)

        # Process the request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        return response
