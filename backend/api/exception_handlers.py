"""
FastAPI exception handlers for RaptorFlow.

Maps domain exceptions to canonical HTTP error responses.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from backend.utils.logging_config import get_logger
from backend.core.errors import RaptorflowError
from backend.api.error_responses import build_error_response

logger = get_logger("api")


async def raptorflow_error_handler(request: Request, exc: RaptorflowError) -> JSONResponse:
    """
    Handle RaptorflowError exceptions.

    Maps domain errors to appropriate HTTP status codes and logs the error.
    """
    logger.warning(
        "raptorflow_error",
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )

    # Map domain error codes to HTTP status codes
    status_map = {
        "PERMISSION_DENIED": 403,
        "NOT_FOUND": 404,
        "VALIDATION_FAILED": 422,
        "CONFLICT": 409,
        "LLM_BUDGET_EXCEEDED": 402,  # Payment required (like insufficient funds)
    }
    status_code = status_map.get(exc.code, 400)  # Default to 400 for unknown codes

    body = build_error_response(
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )
    return JSONResponse(status_code=status_code, content=body.dict())


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTPException errors.

    Wraps standard HTTPException in our canonical error format for consistency.
    """
    logger.info(
        "http_exception",
        status_code=exc.status_code,
        detail=str(exc.detail),
    )

    body = build_error_response(
        code="HTTP_ERROR",
        message=str(exc.detail),
        details={"status_code": exc.status_code},
    )
    return JSONResponse(status_code=exc.status_code, content=body.dict())


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unhandled exceptions.

    Logs the error and returns a generic 500 response without leaking internal details.
    """
    logger.error(
        "unhandled_exception",
        error_type=type(exc).__name__,
        message=str(exc),
    )

    body = build_error_response(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred.",
        details={},
    )
    return JSONResponse(status_code=500, content=body.dict())
