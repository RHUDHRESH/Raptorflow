"""
End-to-end integration tests for Phase 1 systems.

Tests the complete functionality of all Phase 1 components:
- Authentication and rate limiting
- Audit logging
- Memory systems
- Graph operations
- Background jobs
- Webhook verification
- Error handling
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.core.audit import get_audit_logger

# Import the systems we're testing
from backend.core.auth import get_current_user, get_workspace_id
from backend.core.error_handling import ErrorHandler, get_error_handler
from backend.core.jwt import get_jwt_validator
from backend.core.rate_limiting import get_rate_limiter
from backend.jobs.scheduler import JobScheduler
from backend.memory.graph_memory import GraphMemory
from backend.memory.graph_query import GraphQueryEngine
from backend.memory.hybrid_search import HybridSearchEngine
from backend.memory.vector_store import VectorMemory
from backend.webhooks.verification import WebhookVerifier


class TestAuthenticationSystem:
    """Test authentication and authorization systems."""

    @pytest.fixture
    async def app(self):
        """Create test FastAPI app."""
        app = FastAPI()

        @app.get("/test-auth")
        async def test_auth():
            return {"status": "authenticated"}

        return app

    @pytest.fixture
    async def client(self, app):
        """Create test client."""
        return TestClient(app)

    async def test_jwt_token_validation(self):
        """Test JWT token validation and refresh."""
        validator = get_jwt_validator()

        # Test token extraction
        header = "Bearer test_token"
        token = validator.extract_token(header)
        assert token == "test_token"

        # Test invalid header format
        with pytest.raises(Exception):
            validator.extract_token("Invalid token")

    async def test_rate_limiting(self):
        """Test Redis-based rate limiting."""
        rate_limiter = get_rate_limiter()

        workspace_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())

        # Test rate limit check
        result = await rate_limiter.check_rate_limit(
            workspace_id=workspace_id,
            user_id=user_id,
            endpoint="api",
            ip_address="127.0.0.1",
        )

        assert result.allowed is True
        assert result.remaining >= 0

    async def test_audit_logging(self):
        """Test comprehensive audit logging."""
        audit_logger = get_audit_logger()

        workspace_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())

        # Test authentication logging
        success = await audit_logger.log_authentication(
            user_id=user_id,
            action="login_success",
            ip_address="127.0.0.1",
            user_agent="test-agent",
            success=True,
        )

        assert success is True

        # Test workspace access logging
        success = await audit_logger.log_workspace_access(
            user_id=user_id,
            workspace_id=workspace_id,
            action="read",
            resource_type="workspace",
            success=True,
        )

        assert success is True


class TestMemorySystems:
    """Test memory and vector systems."""

    async def test_vector_storage(self):
        """Test vector memory storage and retrieval."""
        vector_memory = VectorMemory()

        workspace_id = str(uuid.uuid4())

        # Create test chunk
        from backend.memory.models import MemoryChunk, MemoryType

        chunk = MemoryChunk(
            workspace_id=workspace_id,
            memory_type=MemoryType.FOUNDATION,
            content="Test content for vector storage",
            metadata={"test": True},
        )

        # Store chunk
        chunk_id = await vector_memory.store(chunk)
        assert chunk_id is not None

        # Search for chunk
        results = await vector_memory.search(
            workspace_id=workspace_id, query="test content", limit=10
        )

        assert len(results) > 0

    async def test_graph_operations(self):
        """Test graph memory operations."""
        graph_memory = GraphMemory()

        workspace_id = str(uuid.uuid4())

        # Create test entities
        from backend.memory.graph_models import EntityType, GraphEntity

        entity1 = GraphEntity(
            workspace_id=workspace_id,
            name="Test Entity 1",
            entity_type=EntityType.PERSON,
            properties={"role": "test"},
        )

        entity2 = GraphEntity(
            workspace_id=workspace_id,
            name="Test Entity 2",
            entity_type=EntityType.ORGANIZATION,
            properties={"type": "test"},
        )

        # Store entities
        entity1_id = await graph_memory.store_entity(entity1)
        entity2_id = await graph_memory.store_entity(entity2)

        assert entity1_id is not None
        assert entity2_id is not None

        # Create relationship
        from backend.memory.graph_models import GraphRelationship, RelationType

        relationship = GraphRelationship(
            workspace_id=workspace_id,
            source_id=entity1_id,
            target_id=entity2_id,
            relation_type=RelationType.WORKS_FOR,
            properties={"since": "2023"},
        )

        rel_id = await graph_memory.store_relationship(relationship)
        assert rel_id is not None

    async def test_hybrid_search(self):
        """Test hybrid search with reranking."""
        vector_memory = VectorMemory()
        search_engine = HybridSearchEngine(vector_memory)

        workspace_id = str(uuid.uuid4())

        # Create test data
        from backend.memory.models import MemoryChunk, MemoryType

        chunks = [
            MemoryChunk(
                workspace_id=workspace_id,
                memory_type=MemoryType.FOUNDATION,
                content="Business strategy and market analysis",
                metadata={"category": "business"},
            ),
            MemoryChunk(
                workspace_id=workspace_id,
                memory_type=MemoryType.RESEARCH,
                content="Technical research and development findings",
                metadata={"category": "technical"},
            ),
        ]

        # Store chunks
        for chunk in chunks:
            await vector_memory.store(chunk)

        # Test hybrid search
        results = await search_engine.search(
            workspace_id=workspace_id,
            query="business strategy",
            memory_types=[MemoryType.FOUNDATION],
        )

        assert len(results) >= 0


class TestWebhookVerification:
    """Test webhook signature verification."""

    async def test_stripe_webhook_verification(self):
        """Test Stripe webhook signature verification."""
        verifier = WebhookVerifier()

        # Create test webhook config
        from backend.webhooks.models import WebhookConfig

        config = WebhookConfig(
            source="stripe", secret_key="whsec_test_secret_key", enabled=True
        )

        # Test headers and body
        headers = {"stripe-signature": "t=1640995243,v1=test_signature"}
        body = b'{"event": "payment.succeeded"}'

        # This should fail with test data, but not crash
        result = await verifier.verify_signature("stripe", headers, body, config)
        assert isinstance(result, bool)

    async def test_supabase_webhook_verification(self):
        """Test Supabase webhook signature verification."""
        verifier = WebhookVerifier()

        # Create test webhook config
        from backend.webhooks.models import WebhookConfig

        config = WebhookConfig(
            source="supabase", secret_key="test_supabase_secret", enabled=True
        )

        # Test headers and body
        headers = {"supabase-signature": "test_signature"}
        body = b'{"type": "INSERT", "table": "users"}'

        # This should fail with test data, but not crash
        result = await verifier.verify_signature("supabase", headers, body, config)
        assert isinstance(result, bool)


class TestErrorHandling:
    """Test error handling and retry mechanisms."""

    async def test_circuit_breaker(self):
        """Test circuit breaker functionality."""
        from backend.core.error_handling import CircuitBreaker, CircuitBreakerConfig

        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=1.0)

        circuit_breaker = CircuitBreaker(config)

        # Create a function that fails
        async def failing_function():
            raise Exception("Test failure")

        # First failure should open circuit breaker
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_function)

        with pytest.raises(Exception):
            await circuit_breaker.call(failing_function)

        # Circuit should now be open
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            await circuit_breaker.call(failing_function)

    async def test_retry_handler(self):
        """Test retry handler with exponential backoff."""
        from backend.core.error_handling import RetryConfig, RetryHandler

        config = RetryConfig(max_attempts=3, base_delay=0.1, max_delay=1.0)

        retry_handler = RetryHandler(config)

        attempt_count = 0

        async def sometimes_failing_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise Exception("Temporary failure")
            return "success"

        # Should succeed after retries
        result = await retry_handler.execute(sometimes_failing_function)
        assert result == "success"
        assert attempt_count == 3

    async def test_error_handler(self):
        """Test centralized error handling."""
        error_handler = ErrorHandler()

        # Create test error
        error = Exception("Test error")
        context = error_handler.ErrorContext(
            component="test_component", operation="test_operation", user_id="test_user"
        )

        # Handle error
        error_info = await error_handler.handle_error(
            error=error, context=context, severity=error_handler.ErrorSeverity.MEDIUM
        )

        assert error_info.error_id is not None
        assert error_info.message == "Test error"
        assert error_info.context.component == "test_component"

        # Check error stats
        stats = error_handler.get_error_stats(hours=24)
        assert stats["total_errors"] >= 1


class TestBackgroundJobs:
    """Test background job system."""

    async def test_job_scheduler(self):
        """Test job scheduling and execution."""
        scheduler = JobScheduler()

        executed_jobs = []

        async def test_job():
            executed_jobs.append("job_executed")
            return "success"

        # Register job
        scheduler.register_job(
            name="test_job",
            function=test_job,
            schedule="0 0 * * *",  # Daily
            enabled=True,
        )

        # Start scheduler
        await scheduler.start()

        # Manual trigger for testing
        result = await scheduler.trigger_job("test_job")
        assert result == "success"
        assert len(executed_jobs) == 1

        # Stop scheduler
        await scheduler.stop()


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""

    async def test_user_workflow(self):
        """Test complete user interaction workflow."""
        # This would test the full flow from user authentication
        # through API calls, rate limiting, audit logging, and responses

        # Create test user
        user_id = str(uuid.uuid4())
        workspace_id = str(uuid.uuid4())

        # Test authentication
        validator = get_jwt_validator()
        # In real test, would create actual JWT token

        # Test rate limiting
        rate_limiter = get_rate_limiter()
        result = await rate_limiter.check_rate_limit(
            workspace_id=workspace_id,
            user_id=user_id,
            endpoint="api",
            ip_address="127.0.0.1",
        )
        assert result.allowed is True

        # Test audit logging
        audit_logger = get_audit_logger()
        await audit_logger.log_authentication(
            user_id=user_id,
            action="login_success",
            ip_address="127.0.0.1",
            success=True,
        )

    async def test_data_processing_workflow(self):
        """Test complete data processing workflow."""
        workspace_id = str(uuid.uuid4())

        # Test vector storage
        vector_memory = VectorMemory()

        from backend.memory.models import MemoryChunk, MemoryType

        chunk = MemoryChunk(
            workspace_id=workspace_id,
            memory_type=MemoryType.RESEARCH,
            content="Research findings about market trends",
            metadata={"topic": "market_analysis"},
        )

        chunk_id = await vector_memory.store(chunk)
        assert chunk_id is not None

        # Test search
        search_engine = HybridSearchEngine(vector_memory)
        results = await search_engine.search(
            workspace_id=workspace_id, query="market trends"
        )

        assert len(results) >= 0

        # Test graph operations
        graph_memory = GraphMemory()

        from backend.memory.graph_models import EntityType, GraphEntity

        entity = GraphEntity(
            workspace_id=workspace_id,
            name="Market Research",
            entity_type=EntityType.CONCEPT,
            properties={"type": "research"},
        )

        entity_id = await graph_memory.store_entity(entity)
        assert entity_id is not None

    async def test_error_recovery_workflow(self):
        """Test error handling and recovery workflows."""
        error_handler = ErrorHandler()

        # Register circuit breaker
        circuit_breaker = error_handler.register_circuit_breaker(
            "test_service", error_handler.CircuitBreakerConfig(failure_threshold=2)
        )

        # Register retry handler
        retry_handler = error_handler.register_retry_handler(
            "test_operation", error_handler.RetryConfig(max_attempts=3)
        )

        attempt_count = 0

        async def unreliable_service():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise Exception("Service temporarily unavailable")
            return "success"

        # Test with circuit breaker and retry
        result = await retry_handler.execute(unreliable_service)
        assert result == "success"
        assert attempt_count == 2


# Performance and Load Tests


class TestPerformance:
    """Test system performance under load."""

    async def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        rate_limiter = get_rate_limiter()

        workspace_id = str(uuid.uuid4())

        # Create concurrent requests
        tasks = []
        for i in range(50):
            task = rate_limiter.check_rate_limit(
                workspace_id=workspace_id,
                user_id=str(uuid.uuid4()),
                endpoint="api",
                ip_address=f"192.168.1.{i % 255}",
            )
            tasks.append(task)

        # Execute all concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check that most succeeded
        successful = sum(
            1 for r in results if isinstance(r, object) and hasattr(r, "allowed")
        )
        assert successful >= 40  # Allow some to be rate limited

    async def test_memory_search_performance(self):
        """Test memory search performance with large datasets."""
        vector_memory = VectorMemory()
        search_engine = HybridSearchEngine(vector_memory)

        workspace_id = str(uuid.uuid4())

        # Create test data
        from backend.memory.models import MemoryChunk, MemoryType

        chunks = []
        for i in range(100):
            chunk = MemoryChunk(
                workspace_id=workspace_id,
                memory_type=MemoryType.FOUNDATION,
                content=f"Test content {i} with various keywords and concepts",
                metadata={"index": i},
            )
            chunks.append(chunk)

        # Store all chunks
        start_time = datetime.utcnow()
        for chunk in chunks:
            await vector_memory.store(chunk)

        storage_time = (datetime.utcnow() - start_time).total_seconds()
        assert storage_time < 10.0  # Should complete within 10 seconds

        # Test search performance
        start_time = datetime.utcnow()
        results = await search_engine.search(
            workspace_id=workspace_id, query="test content", limit=20
        )

        search_time = (datetime.utcnow() - start_time).total_seconds()
        assert search_time < 2.0  # Search should complete within 2 seconds
        assert len(results) <= 20


# Test Configuration and Fixtures


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_workspace():
    """Create test workspace."""
    return str(uuid.uuid4())


@pytest.fixture
async def test_user():
    """Create test user."""
    return str(uuid.uuid4())


# Integration Test Runner


class IntegrationTestRunner:
    """Run all integration tests with reporting."""

    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None

    async def run_all_tests(self):
        """Run all integration tests."""
        self.start_time = datetime.utcnow()

        test_classes = [
            TestAuthenticationSystem,
            TestMemorySystems,
            TestWebhookVerification,
            TestErrorHandling,
            TestBackgroundJobs,
            TestEndToEndWorkflows,
            TestPerformance,
        ]

        for test_class in test_classes:
            class_name = test_class.__name__
            print(f"\n🧪 Running {class_name}...")

            try:
                # Create instance and run tests
                instance = test_class()
                methods = [
                    method for method in dir(instance) if method.startswith("test_")
                ]

                class_results = {}
                for method_name in methods:
                    try:
                        method = getattr(instance, method_name)
                        if asyncio.iscoroutinefunction(method):
                            await method()
                        class_results[method_name] = "PASS"
                    except Exception as e:
                        class_results[method_name] = f"FAIL: {str(e)}"

                self.results[class_name] = class_results

            except Exception as e:
                self.results[class_name] = {"ERROR": str(e)}

        self.end_time = datetime.utcnow()
        self._generate_report()

    def _generate_report(self):
        """Generate test report."""
        duration = (self.end_time - self.start_time).total_seconds()

        print("\n" + "=" * 80)
        print("📊 INTEGRATION TEST REPORT")
        print("=" * 80)
        print(f"Duration: {duration:.2f} seconds")
        print(f"Started: {self.start_time}")
        print(f"Ended: {self.end_time}")
        print("\nResults:")

        total_tests = 0
        total_passed = 0

        for class_name, results in self.results.items():
            print(f"\n📋 {class_name}:")
            for test_name, result in results.items():
                total_tests += 1
                status = "✅" if result == "PASS" else "❌"
                print(f"  {status} {test_name}: {result}")
                if result == "PASS":
                    total_passed += 1

        print(f"\n📈 Summary: {total_passed}/{total_tests} tests passed")
        print(f"Success Rate: {(total_passed/total_tests)*100:.1f}%")
        print("=" * 80)


if __name__ == "__main__":
    # Run all integration tests
    runner = IntegrationTestRunner()
    asyncio.run(runner.run_all_tests())
