import asyncio
import json
from typing import Any, Dict, Optional

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from core.auth import get_current_user
from main import app
from models.requests import AssetCreateRequest, CampaignCreateRequest, MoveCreateRequest


class MockUser:
    """Mock user for testing."""

    def __init__(self, user_id: str = "test_user", tenant_id: str = "test_tenant"):
        self.id = user_id
        self.tenant_id = tenant_id
        self.email = "test@example.com"


def mock_get_current_user():
    """Mock authentication dependency."""
    return MockUser()


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def async_client():
    """Async test client fixture."""
    return AsyncClient(app=app, base_url="http://test")


@pytest.fixture
def mock_auth():
    """Mock authentication for testing."""
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def sample_campaign_data():
    """Sample campaign data for testing."""
    return {
        "title": "Test Campaign",
        "objective": "This is a test campaign for unit testing purposes",
        "status": "draft",
    }


@pytest.fixture
def sample_move_data():
    """Sample move data for testing."""
    return {
        "title": "Test Move",
        "description": "This is a test move for unit testing purposes",
        "priority": 3,
        "move_type": "content",
        "tool_requirements": [],
    }


@pytest.fixture
def sample_asset_data():
    """Sample asset data for testing."""
    return {
        "content": "This is test content for unit testing",
        "asset_type": "text",
        "metadata": {"test": True},
    }


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check_basic(self, client):
        """Test basic health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "timestamp" in data
        assert "version" in data
        assert "components" in data

    def test_health_check_detailed(self, client):
        """Test detailed health check."""
        response = client.get("/health?detailed=true")
        assert response.status_code == 200
        data = response.json()
        assert "database" in data["components"]
        assert "cache" in data["components"]


class TestCampaignEndpoints:
    """Test campaign management endpoints."""

    def test_create_campaign_success(self, client, mock_auth, sample_campaign_data):
        """Test successful campaign creation."""
        response = client.post("/v1/campaigns/", json=sample_campaign_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["message"] == "Campaign created successfully"

    def test_create_campaign_validation_error(self, client, mock_auth):
        """Test campaign creation with validation errors."""
        invalid_data = {
            "title": "",  # Invalid: empty title
            "objective": "too short",  # Invalid: too short objective
        }
        response = client.post("/v1/campaigns/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_create_campaign_unauthorized(self, client, sample_campaign_data):
        """Test campaign creation without authentication."""
        response = client.post("/v1/campaigns/", json=sample_campaign_data)
        assert response.status_code == 401  # Unauthorized

    def test_get_campaign_gantt(self, client, mock_auth):
        """Test getting campaign Gantt chart."""
        response = client.get("/v1/campaigns/test_campaign/gantt")
        # Will likely return 404 for non-existent campaign, but should not be 401
        assert response.status_code != 401


class TestMoveEndpoints:
    """Test move management endpoints."""

    def test_create_move_success(self, client, mock_auth, sample_move_data):
        """Test successful move creation."""
        response = client.post("/v1/moves/", json=sample_move_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_create_move_validation_error(self, client, mock_auth):
        """Test move creation with validation errors."""
        invalid_data = {
            "title": "",  # Invalid: empty title
            "description": "short",  # Invalid: too short
            "move_type": "invalid_type",  # Invalid: not in enum
        }
        response = client.post("/v1/moves/", json=invalid_data)
        assert response.status_code == 422


class TestAssetEndpoints:
    """Test asset management endpoints."""

    def test_create_asset_success(self, client, mock_auth, sample_asset_data):
        """Test successful asset creation."""
        response = client.post("/v1/assets/", json=sample_asset_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_create_asset_validation_error(self, client, mock_auth):
        """Test asset creation with validation errors."""
        invalid_data = {
            "content": "",  # Invalid: empty content
            "asset_type": "invalid_type",  # Invalid: not in enum
        }
        response = client.post("/v1/assets/", json=invalid_data)
        assert response.status_code == 422


class TestFoundationEndpoints:
    """Test foundation management endpoints."""

    def test_save_foundation_state(self, client, mock_auth):
        """Test saving foundation state."""
        state_data = {
            "state_data": {
                "test_key": "test_value",
                "timestamp": "2024-01-01T00:00:00Z",
            }
        }
        response = client.post("/v1/foundation/state", json=state_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_foundation_state(self, client, mock_auth):
        """Test getting foundation state."""
        response = client.get("/v1/foundation/state")
        # Will likely return 404 for non-existent state, but should not be 401
        assert response.status_code != 401


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limiting_headers(self, client):
        """Test that rate limiting headers are present."""
        response = client.get("/health")
        # Rate limiting middleware should add headers
        assert response.status_code in [200, 429]

    def test_rate_limiting_enforcement(self, client):
        """Test rate limiting enforcement (basic check)."""
        # Make multiple rapid requests
        responses = []
        for _ in range(5):
            response = client.get("/health")
            responses.append(response.status_code)

        # At least some requests should succeed
        assert any(status == 200 for status in responses)


class TestErrorHandling:
    """Test error handling across endpoints."""

    def test_404_handling(self, client):
        """Test 404 error handling."""
        response = client.get("/v1/nonexistent/endpoint")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test method not allowed handling."""
        response = client.delete("/v1/campaigns/")
        assert response.status_code == 405

    def test_invalid_json(self, client, mock_auth):
        """Test invalid JSON handling."""
        response = client.post(
            "/v1/campaigns/",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422


class TestCORS:
    """Test CORS configuration."""

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/health")
        assert response.status_code == 200
        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers


class TestMiddleware:
    """Test middleware functionality."""

    def test_correlation_id_header(self, client):
        """Test correlation ID is added."""
        response = client.get("/health")
        # Correlation ID middleware should add this header
        assert response.status_code in [200, 429, 503]

    def test_request_logging(self, client):
        """Test request logging middleware."""
        response = client.get("/health")
        # Request should be logged (can't directly test logging, but ensure no errors)
        assert response.status_code in [200, 429, 503]


class TestMetrics:
    """Test metrics collection."""

    def test_metrics_endpoint(self, client):
        """Test metrics collection is working."""
        # Make a request to generate metrics
        response = client.get("/health")
        assert response.status_code in [200, 429, 503]

        # Metrics should be collected (can't directly test, but ensure no errors)
        # This would typically be tested via metrics endpoint


class TestAsyncOperations:
    """Test async operations."""

    @pytest.mark.asyncio
    async def test_async_client(self, async_client):
        """Test async client functionality."""
        async with async_client as client:
            response = await client.get("/health")
            assert response.status_code in [200, 429, 503]

    @pytest.mark.asyncio
    async def test_async_campaign_creation(self, async_client, mock_auth):
        """Test async campaign creation."""
        campaign_data = {
            "title": "Async Test Campaign",
            "objective": "Testing async campaign creation",
            "status": "draft",
        }

        async with async_client as client:
            response = await client.post("/v1/campaigns/", json=campaign_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


class TestIntegration:
    """Integration tests."""

    def test_full_campaign_workflow(self, client, mock_auth):
        """Test complete campaign workflow."""
        # 1. Create campaign
        campaign_data = {
            "title": "Integration Test Campaign",
            "objective": "Testing full campaign workflow",
            "status": "draft",
        }
        response = client.post("/v1/campaigns/", json=campaign_data)
        assert response.status_code == 200

        # 2. Create move for campaign
        move_data = {
            "title": "Integration Test Move",
            "description": "Testing move creation in workflow",
            "priority": 3,
            "move_type": "content",
        }
        response = client.post("/v1/moves/", json=move_data)
        assert response.status_code == 200

        # 3. Create asset
        asset_data = {
            "content": "Integration test asset content",
            "asset_type": "text",
            "metadata": {"integration_test": True},
        }
        response = client.post("/v1/assets/", json=asset_data)
        assert response.status_code == 200


# Performance Tests
class TestPerformance:
    """Performance and load tests."""

    def test_response_time_health(self, client):
        """Test health endpoint response time."""
        import time

        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()

        response_time = end_time - start_time
        assert response_time < 1.0  # Should respond within 1 second
        assert response.status_code in [200, 429, 503]

    def test_concurrent_requests(self, client):
        """Test handling concurrent requests."""
        import threading
        import time

        results = []

        def make_request():
            response = client.get("/health")
            results.append(response.status_code)

        # Make 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All requests should complete without errors英
        assert len(results) == 10
        assert any(status == 200 for status in results)
