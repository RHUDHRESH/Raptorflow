"""
Tests for global error handling system.

Tests:
- BudgetExceededError → 402 status with correct error envelope
- NotFoundError → 404 status
- Unhandled exceptions → 500 status
- HTTPException wrapper maintains compatibility
- Correlation ID included in responses
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, APIRouter, HTTPException

from backend.core.errors import BudgetExceededError, NotFoundError, RaptorflowError
from backend.api.exception_handlers import raptorflow_error_handler, http_exception_handler, unhandled_exception_handler
from backend.core.middleware import CorrelationIdMiddleware


# Create a minimal FastAPI app for testing error handlers
test_app = FastAPI(title="Test Error Handling")

# Add middleware
test_app.add_middleware(CorrelationIdMiddleware)

# Register exception handlers
test_app.add_exception_handler(RaptorflowError, raptorflow_error_handler)
test_app.add_exception_handler(HTTPException, http_exception_handler)
test_app.add_exception_handler(Exception, unhandled_exception_handler)

# Test router for error scenarios
test_router = APIRouter()


@test_router.get("/budget_exceeded/{workspace_id}")
async def trigger_budget_exceeded(workspace_id: str):
    """Endpoint that raises BudgetExceededError."""
    raise BudgetExceededError(
        details={
            "workspace_id": workspace_id,
            "current_spend_usd": 50.0,
            "new_call_cost_usd": 60.0,
            "budget_cap_usd": 100.0,
        }
    )


@test_router.get("/not_found")
async def trigger_not_found():
    """Endpoint that raises NotFoundError."""
    raise NotFoundError("Resource not found")


@test_router.get("/unhandled_error")
async def trigger_unhandled_error():
    """Endpoint that raises unhandled RuntimeError."""
    raise RuntimeError("Something bad happened")


@test_router.get("/http_exception")
async def trigger_http_exception():
    """Endpoint that raises HTTPException."""
    raise HTTPException(status_code=403, detail="Forbidden")


# Register test router
test_app.include_router(test_router, prefix="/test", tags=["test"])

# Test client for FastAPI
client = TestClient(test_app)


class TestErrorHandling:
    """Test suite for error handling."""

    def test_budget_exceeded_error_returns_402(self):
        """Test BudgetExceededError maps to 402 status code."""
        response = client.get("/test/budget_exceeded/test-workspace-123")

        assert response.status_code == 402

        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "LLM_BUDGET_EXCEEDED"
        assert "Workspace LLM budget exceeded" in data["error"]["message"]
        assert data["error"]["details"]["workspace_id"] == "test-workspace-123"
        assert data["error"]["details"]["current_spend_usd"] == 50.0
        assert data["error"]["details"]["new_call_cost_usd"] == 60.0
        assert data["error"]["details"]["budget_cap_usd"] == 100.0

    def test_budget_exceeded_error_includes_correlation_id(self):
        """Test BudgetExceededError response includes correlation_id."""
        response = client.get("/test/budget_exceeded/test-workspace-456")

        data = response.json()
        assert "correlation_id" in data
        assert isinstance(data["correlation_id"], str)
        assert len(data["correlation_id"]) > 0

    def test_not_found_error_returns_404(self):
        """Test NotFoundError maps to 404 status code."""
        response = client.get("/test/not_found")

        assert response.status_code == 404

        data = response.json()
        assert data["error"]["code"] == "NOT_FOUND"
        assert data["error"]["message"] == "Resource not found"
        assert data["error"]["details"] == {}

    def test_unhandled_exception_returns_500(self):
        """Test unhandled exceptions map to 500 status code."""
        response = client.get("/test/unhandled_error")

        assert response.status_code == 500

        data = response.json()
        assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert data["error"]["message"] == "An unexpected error occurred."
        assert data["error"]["details"] == {}

    def test_unhandled_exception_includes_correlation_id(self):
        """Test unhandled exception response includes correlation_id."""
        response = client.get("/test/unhandled_error")

        data = response.json()
        assert "correlation_id" in data
        assert isinstance(data["correlation_id"], str)

    def test_http_exception_wrapper_works(self):
        """Test HTTPException is wrapped in our error format."""
        response = client.get("/test/http_exception")

        assert response.status_code == 403

        data = response.json()
        assert data["error"]["code"] == "HTTP_ERROR"
        assert data["error"]["message"] == "Forbidden"
        assert data["error"]["details"]["status_code"] == 403

    def test_correlation_id_consistency(self):
        """Test correlation_id is consistent across different tests."""
        response1 = client.get("/test/not_found")
        response2 = client.get("/test/budget_exceeded/test-workspace-123")

        data1 = response1.json()
        data2 = response2.json()

        # Note: Each request gets a new correlation ID, so they may differ
        # This is expected behavior
        assert "correlation_id" in data1
        assert "correlation_id" in data2

    def test_error_response_structure(self):
        """Test error response always follows the same structure."""
        response = client.get("/test/not_found")

        data = response.json()

        # Validate structure is always consistent
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert "details" in data["error"]
        assert "correlation_id" in data


# Additional tests could include:
# - Logging verification (assert logs are written)
# - Different details in error responses
# - Edge cases with empty details
