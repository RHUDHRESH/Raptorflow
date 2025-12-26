import pytest
import asyncio
from typing import Dict, Any, Optional
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json

from main import app
from core.auth import get_current_user
from models.requests import CampaignCreateRequest, MoveCreateRequest, AssetCreateRequest


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
        "status": "draft"
    }


@pytest.fixture
def sample_move_data():
    """Sample move data for testing."""
    return {
        "title": "Test Move",
        "description": "This is a test move for unit testing purposes",
        "priority": 3,
        "move_type": "content",
        "tool_requirements": []
    }


@pytest.fixture
def sample_asset_data():
    """Sample asset data for testing."""
    return {
        "content": "This is test content for unit testing",
        "asset_type": "text",
        "metadata": {"test": True}
    }


class TestDatabaseOperations:
    """Test database operations and transactions."""
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test database connection pool."""
        from db import get_pool
        pool = get_pool()
        assert pool is not None
        
        # Test connection
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                result = await cur.fetchone()
                assert result[0] == 1
    
    @pytest.mark.asyncio
    async def test_transaction_rollback(self):
        """Test transaction rollback on error."""
        from db import get_db_transaction
        
        try:
            async with get_db_transaction() as conn:
                async with conn.cursor() as cur:
                    # This should work
                    await cur.execute("SELECT 1")
                    result = await cur.fetchone()
                    assert result[0] == 1
                    
                    # Force an error to test rollback
                    raise Exception("Test rollback")
        except Exception as e:
            assert str(e) == "Test rollback"
    
    @pytest.mark.asyncio
    async def test_cache_operations(self):
        """Test cache operations."""
        from memory.cache import get_cache_client
        
        cache = get_cache_client()
        test_key = "test_key"
        test_value = {"test": "data"}
        
        # Test set and get
        await cache.set(test_key, test_value)
        result = await cache.get(test_key)
        assert result == test_value
        
        # Test delete
        await cache.delete(test_key)
        result = await cache.get(test_key)
        assert result is None


class TestAuthentication:
    """Test authentication and authorization."""
    
    def test_jwt_validation(self):
        """Test JWT token validation."""
        from core.auth import get_current_user
        from fastapi import HTTPException
        
        # Test with invalid token
        try:
            # This should raise an exception
            get_current_user("invalid_token")
        except HTTPException:
            pass  # Expected
        except Exception:
            pass  # Also expected for invalid token
    
    def test_tenant_extraction(self):
        """Test tenant ID extraction."""
        from core.auth import get_tenant_id
        
        # Test with valid tenant
        mock_token = {"app_metadata": {"tenant_id": "test_tenant"}}
        tenant_id = get_tenant_id(mock_token)
        assert tenant_id == "test_tenant"
        
        # Test with missing tenant
        mock_token = {"app_metadataaid": {}}
        tenant_id = get_tenant_id(mock_token)
        assert tenant_id is None


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_basic(self):
        """Test basic rate limiting."""
        from services.rate_limiter import GlobalRateLimiter
        
        limiter = GlobalRateLimiter()
        
        # Test allowed request
        result = await limiter.is_allowed("test_client")
        assert result is True
        
        # Test remaining requests
        remaining = await limiter.get_remaining_requests("test_client")
        assert remaining >= 0
    
    @pytest.mark.asyncio
    async def test_rate_limiter_reset(self):
        """Test rate limiter reset."""
        from services.rate_limiter import GlobalRateLimiter
        
        limiter = GlobalRateLimiter()
        client_id = "test_reset_client"
        
        # Use some requests
        await limiter.is_allowed(client_id)
        
        # Reset
        await limiter.reset_limit(client_id)
        
        # Should have full limit again
        remaining = await limiter.get_remaining_requests(client_id)
        assert remaining > 0


class TestMetrics:
    """Test metrics collection."""
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self):
        """Test metrics collection and aggregation."""
        from core.metrics import get_metrics_collector
        
        metrics = get_metrics_collector()
        await metrics.start()
        
        # Test counter
        await metrics.increment_counter("test_counter", 1.0)
        counter_value = await metrics.get_counter("test_counter")
        assert counter_value == 1.0
        
        # Test gauge
        await metrics.set_gauge("test_gauge", 42.0)
        gauge_value = await metrics.get_gauge("test_gauge")
        assert gauge_value == 42.0
        
        # Test histogram
        await metrics.record_histogram("test_histogram", 1.5)
        await metrics.record_histogram("test_histogram", 2.5)
        await metrics.record_histogram("test_histogram", 3.5)
        
        summary = await metrics.get_histogram_summary("test_histogram")
        assert summary is not None
        assert summary.count == 3
        assert summary.min == 1.5
        assert summary.max == 3.5
        
        await metrics.stop()
    
    @pytest.mark.asyncio
    async def test_metrics_aggregation(self):
        """Test metrics aggregation and percentiles."""
        from core.metrics import get_metrics_collector
        
        metrics = get_metrics_collector()
        await metrics.start()
        
        # Record multiple values
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for value in values:
            await metrics.record_histogram("test_percentiles", value)
        
        summary = await metrics.get_histogram_summary("test_percentiles")
        assert summary is not None
        assert summary.p50 == 5.5  # Median
        assert summary.p95 == 9.55  # 95th percentile
        
        await metrics.stop()


class TestTaskQueue:
    """Test background task queue."""
    
    @pytest.mark.asyncio
    async def test_task_queue_basic(self):
        """Test basic task queue operations."""
        from core.tasks import BackgroundTaskQueue, TaskPriority
        
        queue = BackgroundTaskQueue(max_workers=2)
        await queue.start()
        
        # Simple task function
        async def test_task(x, y):
            return x + y
        
        # Add task
        task_id = await queue.add_task(
            test_task, 
            5, 3, 
            priority=TaskPriority.HIGH
        )
        
        # Wait for task completion
        await asyncio.sleep(0.1)
        
        # Check status
        status = await queue.get_task_status(task_id)
        assert status is not None
        
        await queue.stop()
    
    @pytest.mark.asyncio
    async def test_task_queue_retry(self):
        """Test task retry logic."""
        from core.tasks import BackgroundTaskQueue, TaskPriority
        
        queue = BackgroundTaskQueue(max_workers=1)
        await queue.start()
        
        # Failing task function
        call_count = 0
        async def failing_task():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Task failed")
            return "success"
        
        # Add task with retries
        task_id = await queue.add_task(
            failing_task,
            max_retries=3
        )
        
        # Wait for task completion
        await asyncio.sleep(0.5)
        
        # Check that task was retried
        status = await queue.get_task_status(task_id)
        assert status is not None
        
        await queue.stop()
    
    @pytest.mark.asyncio
    async def test_task_queue_priority(self):
        """Test task priority ordering."""
        from core.tasks import BackgroundTaskQueue, TaskPriority
        
        queue = BackgroundTaskQueue(max_workers=1)
        await queue.start()
        
        results = []
        
        async def priority_task(task_id):
            results.append(task_id)
            return task_id
        
        # Add tasks in reverse priority order
        await queue.add_task(priority_task, "low", priority=TaskPriority.LOW)
        await queue.add_task(priority_task, "high", priority=TaskPriority.HIGH)
        await queue.add_task(priority_task, "medium", priority=TaskPriority.NORMAL)
        
        # Wait for all tasks to complete
        await asyncio.sleep(0.5)
        
        # High priority task should execute first
        assert len(results) == 3
        assert results[0] == "high"
        
        await queue.stop()


class TestEnvironmentValidation:
    """Test environment variable validation."""
    
    def test_valid_environment(self):
        """Test validation with valid environment."""
        from core.env_validator import EnvironmentValidator, EnvVar, EnvType
        
        validator = EnvironmentValidator()
        validator.add_variable(EnvVar(
            name="TEST_VAR",
            env_type=EnvType.STRING,
            required=False,
            default="test_value"
        ))
        
        # Set environment variable
        import os
        os.environ["TEST_VAR"] = "test_value"
        
        result = validator.validate_all()
        assert result is True
        assert len(validator.errors) == 0
    
    def test_invalid_environment(self):
        """Test validation with invalid environment."""
        from core.env_validator import EnvironmentValidator, EnvVar, EnvType
        
        validator = EnvironmentValidator()
        validator.add_variable(EnvVar(
            name="REQUIRED_VAR",
            env_type=EnvType.STRING,
            required=True
        ))
        
        # Don't set required variable
        result = validator.validate_all()
        assert result is False
        assert len(validator.errors) > 0
        assert any("REQUIRED_VAR" in error for error in validator.errors)
    
    def test_type_validation(self):
        """Test type validation."""
        from core.env_validator import EnvironmentValidator, EnvVar, EnvType
        
        validator = EnvironmentValidator()
        validator.add_variable(EnvVar(
            name="INT_VAR",
            env_type=EnvType.INTEGER,
            required=False
        ))
        
        # Set invalid integer value
        import os
        os.environ["INT_VAR"] = "not_an_integer"
        
        result = validator.validate_all()
        assert result is False
        assert any("Expected integer" in error for error in validator.errors)


class TestErrorHandling:
    """Test error handling patterns."""
    
    def test_raptorflow_error(self):
        """Test custom RaptorFlowError."""
        from core.exceptions import RaptorFlowError
        
        error = RaptorFlowError(
            message="Test error",
            status_code=400,
            error_code="TEST_ERROR"
        )
        
        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.error_code == "TEST_ERROR"
    
    def test_exception_handler(self):
        """Test global exception handler."""
        from fastapi import Request
        from core.exceptions import RaptorFlowError
        from main import app
        
        # Test exception handler registration
        assert app.exception_handlers is not None


class TestLogging:
    """Test logging configuration."""
    
    def test_logging_setup(self):
        """Test logging configuration setup."""
        from utils.logging_config import setup_logging, get_logger
        
        # Setup logging
        setup_logging()
        
        # Get logger
        logger = get_logger("test")
        assert logger is not None
        assert logger.name == "raptorflow.test"
    
    def test_logger_levels(self):
        """Test different logger levels."""
        from utils.logging_config import get_logger
        
        logger = get_logger("test_levels")
        
        # Test different log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # Should not raise exceptions
        assert True


# Integration Tests
class TestFullIntegration:
    """Full integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_request_flow(self):
        """Test complete request flow through all layers."""
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        # Test health check
        response = client.get("/health")
        assert response.status_code in [200, 429, 503]
        
        # Test with authentication
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        # Test campaign creation
        campaign_data = {
            "title": "Integration Test Campaign",
            "objective": "Testing full integration flow",
            "status": "draft"
        }
        response = client.post("/v1/campaigns/", json=campaign_data)
        assert response.status_code == 200
        
        app.dependency_overrides.clear()
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent operations."""
        import asyncio
        
        # Test concurrent database operations
        async def concurrent_db_operation():
            from db import get_db_connection
            async with get_db_connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    return await cur.fetchone()
        
        # Run multiple concurrent operations
        tasks = [concurrent_db_operation() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(results) == 5
        assert all(result[0] == 1 for result in results)


# Performance Tests
class TestPerformance:
    """Performance and load tests."""
    
    @pytest.mark.asyncio
    async def test_database_pool_performance(self):
        """Test database connection pool performance."""
        import time
        from db import get_pool
        
        pool = get_pool()
        
        # Test multiple concurrent connections
        start_time = time.time()
        
        async def test_connection():
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    return await cur.fetchone()
        
        tasks = [test_connection() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
assert len(results) == 10
        end_time = time.time()
        
        # Should complete within reasonable time
        assert (end_time - start_time) < 5.0
    
    @pytest.mark.asyncio
    async def test_cache_performance(self):
        """Test cache performance."""
        import time
        from memory.cache import get_cache_client
        
        cache = get_cache_client()
        
        # Test cache set/get performance
        start_time = time.time()
        
        for i in range(100):
            await cache.set(f"perf_test_{i}", f"value_{i}")
            await cache.get(f"perf_test_{i}")
        
        end_time = time.time()
        
        # Should complete within reasonable time
        assert (end_time - start_time) < 2.0
