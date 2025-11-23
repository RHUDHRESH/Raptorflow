"""
Comprehensive tests for correlation ID utilities.
"""

import pytest
from contextvars import copy_context
from backend.utils.correlation import (
    set_correlation_id,
    get_correlation_id,
    correlation_id_middleware
)
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient


class TestCorrelationId:
    """Test correlation ID context management."""

    def test_set_and_get_correlation_id(self):
        """Test setting and retrieving correlation ID."""
        test_id = "test-correlation-id-12345"

        set_correlation_id(test_id)
        result = get_correlation_id()

        assert result == test_id

    def test_get_correlation_id_default(self):
        """Test getting correlation ID when not set."""
        # Run in fresh context
        ctx = copy_context()

        def get_id():
            return get_correlation_id()

        result = ctx.run(get_id)

        # Should return "unknown" when not set
        assert result == "unknown"

    def test_correlation_id_isolation(self):
        """Test that correlation IDs are isolated between contexts."""
        id1 = "correlation-1"
        id2 = "correlation-2"

        # Set in first context
        ctx1 = copy_context()

        def set_id1():
            set_correlation_id(id1)
            return get_correlation_id()

        result1 = ctx1.run(set_id1)
        assert result1 == id1

        # Set in second context
        ctx2 = copy_context()

        def set_id2():
            set_correlation_id(id2)
            return get_correlation_id()

        result2 = ctx2.run(set_id2)
        assert result2 == id2

        # Verify isolation
        assert result1 != result2


@pytest.mark.asyncio
class TestCorrelationIdMiddleware:
    """Test correlation ID middleware functionality."""

    async def test_middleware_with_existing_header(self):
        """Test middleware when X-Correlation-ID header is present."""
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            return {"correlation_id": get_correlation_id()}

        # Add middleware
        app.middleware("http")(correlation_id_middleware)

        client = TestClient(app)

        # Send request with correlation ID header
        response = client.get("/test", headers={"X-Correlation-ID": "existing-id-123"})

        assert response.status_code == 200
        data = response.json()
        assert data["correlation_id"] == "existing-id-123"

    async def test_middleware_without_header(self):
        """Test middleware generates ID when header is missing."""
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            return {"correlation_id": get_correlation_id()}

        # Add middleware
        app.middleware("http")(correlation_id_middleware)

        client = TestClient(app)

        # Send request without correlation ID header
        response = client.get("/test")

        assert response.status_code == 200
        data = response.json()
        # Should have generated a UUID
        assert data["correlation_id"] != "unknown"
        assert len(data["correlation_id"]) == 36  # UUID length

    async def test_middleware_adds_response_header(self):
        """Test that middleware adds correlation ID to response headers."""
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        # Add middleware
        app.middleware("http")(correlation_id_middleware)

        client = TestClient(app)

        # Send request
        response = client.get("/test", headers={"X-Correlation-ID": "test-id-456"})

        assert response.status_code == 200
        # Check response header
        assert "X-Correlation-ID" in response.headers
        assert response.headers["X-Correlation-ID"] == "test-id-456"

    async def test_middleware_preserves_correlation_across_calls(self):
        """Test that correlation ID is preserved throughout request lifecycle."""
        app = FastAPI()

        correlation_ids = []

        @app.get("/test")
        async def test_endpoint():
            # Capture correlation ID at different points
            id1 = get_correlation_id()
            correlation_ids.append(id1)

            # Simulate some async work
            import asyncio
            await asyncio.sleep(0.01)

            id2 = get_correlation_id()
            correlation_ids.append(id2)

            return {"ids": correlation_ids}

        # Add middleware
        app.middleware("http")(correlation_id_middleware)

        client = TestClient(app)

        # Send request
        response = client.get("/test", headers={"X-Correlation-ID": "persistent-id"})

        assert response.status_code == 200
        data = response.json()

        # All captured IDs should be the same
        assert all(cid == "persistent-id" for cid in data["ids"])
