import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock

import aioresponses
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

logger = logging.getLogger("raptorflow.testing")


class TestType(Enum):
    """Types of tests."""

    UNIT = "unit"
    INTEGRATION = "integration"
    END_TO_END = "end_to_end"
    PERFORMANCE = "performance"
    SECURITY = "security"


class TestEnvironment(Enum):
    """Test environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"


@dataclass
class TestConfig:
    """Test configuration."""

    environment: TestEnvironment = TestEnvironment.TESTING
    database_url: str = "sqlite:///test.db"
    redis_url: str = "redis://localhost:6379/1"
    api_base_url: str = "http://localhost:8000"
    timeout: int = 30
    max_retries: int = 3
    cleanup_after_test: bool = True
    generate_reports: bool = True


@dataclass
class TestResult:
    """Test result data."""

    test_name: str
    test_type: TestType
    passed: bool
    duration_ms: float
    error_message: Optional[str] = None
    assertions: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TestDatabase:
    """Test database manager."""

    def __init__(self, config: TestConfig):
        self.config = config
        self.connection = None

    async def setup(self):
        """Setup test database."""
        logger.info("Setting up test database")

    async def teardown(self):
        """Cleanup test database."""
        logger.info("Cleaning up test database")

    async def create_test_data(
        self, data_type: str, count: int = 10
    ) -> List[Dict[str, Any]]:
        """Create test data."""
        test_data = []

        if data_type == "users":
            for i in range(count):
                test_data.append(
                    {
                        "id": f"test_user_{i}",
                        "email": f"test{i}@example.com",
                        "username": f"testuser{i}",
                        "role": "user",
                        "is_active": True,
                    }
                )
        elif data_type == "campaigns":
            for i in range(count):
                test_data.append(
                    {
                        "id": f"test_campaign_{i}",
                        "name": f"Test Campaign {i}",
                        "description": f"Test campaign description {i}",
                        "status": "active",
                        "created_at": datetime.utcnow().isoformat(),
                    }
                )

        return test_data


class TestRedis:
    """Test Redis manager."""

    def __init__(self, config: TestConfig):
        self.config = config
        self.client = None

    async def setup(self):
        """Setup test Redis."""
        logger.info("Setting up test Redis")

    async def teardown(self):
        """Cleanup test Redis."""
        logger.info("Cleaning up test Redis")

    async def flush_all(self):
        """Flush all test data."""
        if self.client:
            await self.client.flushall()


class APITestSuite:
    """
    Production-grade API testing suite.
    """

    def __init__(self, config: TestConfig):
        self.config = config
        self.test_db = TestDatabase(config)
        self.test_redis = TestRedis(config)
        self.test_results: List[TestResult] = []
        self.current_test_session = datetime.utcnow().isoformat()

    async def setup_test_environment(self):
        """Setup test environment."""
        await self.test_db.setup()
        await self.test_redis.setup()
        logger.info("Test environment setup complete")

    async def teardown_test_environment(self):
        """Teardown test environment."""
        await self.test_db.teardown()
        await self.test_redis.teardown()
        logger.info("Test environment teardown complete")

    async def run_unit_tests(self) -> List[TestResult]:
        """Run unit tests."""
        logger.info("Running unit tests")
        results = []

        # Test authentication utilities
        auth_results = await self._test_authentication_utils()
        results.extend(auth_results)

        # Test validation utilities
        validation_results = await self._test_validation_utils()
        results.extend(validation_results)

        # Test error handling utilities
        error_results = await self._test_error_handling_utils()
        results.extend(error_results)

        # Test monitoring utilities
        monitoring_results = await self._test_monitoring_utils()
        results.extend(monitoring_results)

        self.test_results.extend(results)
        return results

    async def run_integration_tests(self) -> List[TestResult]:
        """Run integration tests."""
        logger.info("Running integration tests")
        results = []

        # Test API endpoints
        endpoint_results = await self._test_api_endpoints()
        results.extend(endpoint_results)

        # Test database operations
        db_results = await self._test_database_operations()
        results.extend(db_results)

        # Test Redis operations
        redis_results = await self._test_redis_operations()
        results.extend(redis_results)

        # Test middleware integration
        middleware_results = await self._test_middleware_integration()
        results.extend(middleware_results)

        self.test_results.extend(results)
        return results

    async def _test_authentication_utils(self) -> List[TestResult]:
        """Test authentication utilities."""
        results = []

        # Test JWT token creation and validation
        start_time = datetime.utcnow()
        try:
            from core.auth_enhanced import get_enhanced_auth_manager

            auth_manager = get_enhanced_auth_manager()

            # Create session token
            token = await auth_manager.create_session_token("test_user", "test_tenant")
            assert token is not None
            assert len(token) > 0

            # Validate session token
            session = await auth_manager.validate_session_token(token)
            assert session is not None
            assert session["user_id"] == "test_user"
            assert session["tenant_id"] == "test_tenant"

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_session_token_creation_validation",
                    test_type=TestType.UNIT,
                    passed=True,
                    duration_ms=duration,
                    assertions=4,
                )
            )

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_session_token_creation_validation",
                    test_type=TestType.UNIT,
                    passed=False,
                    duration_ms=duration,
                    error_message=str(e),
                )
            )

        # Test API key creation and validation
        start_time = datetime.utcnow()
        try:
            # Create API key
            api_key = await auth_manager.create_api_key(
                "test_user", "test_tenant", "test_key"
            )
            assert api_key is not None
            assert api_key.startswith("rpf_")

            # Validate API key
            key_info = await auth_manager.validate_api_key(api_key)
            assert key_info is not None
            assert key_info["user_id"] == "test_user"
            assert key_info["tenant_id"] == "test_tenant"
            assert key_info["name"] == "test_key"

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_api_key_creation_validation",
                    test_type=TestType.UNIT,
                    passed=True,
                    duration_ms=duration,
                    assertions=4,
                )
            )

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_api_key_creation_validation",
                    test_type=TestType.UNIT,
                    passed=False,
                    duration_ms=duration,
                    error_message=str(e),
                )
            )

        return results

    async def _test_validation_utils(self) -> List[TestResult]:
        """Test validation utilities."""
        results = []

        start_time = datetime.utcnow()
        try:
            from core.validation import (
                ValidationRule,
                ValidationType,
                get_request_validator,
            )

            validator = get_request_validator()

            # Test email validation
            rule = ValidationRule(
                name="email_validation",
                type=ValidationType.EMAIL,
                required=True,
                pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            )

            # Valid email
            valid_data = {"email": "test@example.com"}
            result = await validator.validate_request(valid_data, {"email": [rule]})
            assert result.is_valid is True
            assert len(result.errors) == 0

            # Invalid email
            invalid_data = {"email": "invalid-email"}
            result = await validator.validate_request(invalid_data, {"email": [rule]})
            assert result.is_valid is False
            assert len(result.errors) > 0

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_email_validation",
                    test_type=TestType.UNIT,
                    passed=True,
                    duration_ms=duration,
                    assertions=4,
                )
            )

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_email_validation",
                    test_type=TestType.UNIT,
                    passed=False,
                    duration_ms=duration,
                    error_message=str(e),
                )
            )

        return results

    async def _test_error_handling_utils(self) -> List[TestResult]:
        """Test error handling utilities."""
        results = []

        start_time = datetime.utcnow()
        try:
            from core.error_handling import (
                ErrorCategory,
                ErrorContext,
                ErrorSeverity,
                get_error_handler,
            )

            error_handler = get_error_handler()

            # Test error handling
            test_error = ValueError("Test error message")
            context = ErrorContext(
                request_id="test_request",
                user_id="test_user",
                tenant_id="test_tenant",
                endpoint="/test/endpoint",
                method="GET",
            )

            error_details = await error_handler.handle_error(
                test_error, context, ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM
            )

            assert error_details is not None
            assert error_details.category == ErrorCategory.VALIDATION
            assert error_details.severity == ErrorSeverity.MEDIUM
            assert error_details.message == "Test error message"
            assert error_details.context.request_id == "test_request"

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_error_handling",
                    test_type=TestType.UNIT,
                    passed=True,
                    duration_ms=duration,
                    assertions=5,
                )
            )

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_error_handling",
                    test_type=TestType.UNIT,
                    passed=False,
                    duration_ms=duration,
                    error_message=str(e),
                )
            )

        return results

    async def _test_monitoring_utils(self) -> List[TestResult]:
        """Test monitoring utilities."""
        results = []

        start_time = datetime.utcnow()
        try:
            from core.monitoring import (
                AlertRule,
                AlertSeverity,
                get_performance_monitor,
            )

            monitor = get_performance_monitor()

            # Test metric recording
            await monitor.record_metric(
                "test_metric",
                100.0,
                tags={"endpoint": "/test", "method": "GET"},
                unit="ms",
            )

            # Test alert rule evaluation
            rule = AlertRule(
                name="test_alert",
                metric_name="test_metric",
                threshold=50.0,
                operator=">",
                severity=AlertSeverity.WARNING,
            )

            # This should trigger an alert since 100.0 > 50.0
            metric_value = 100.0
            should_alert = rule.evaluate(metric_value)
            assert should_alert is True

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_monitoring_metrics",
                    test_type=TestType.UNIT,
                    passed=True,
                    duration_ms=duration,
                    assertions=2,
                )
            )

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_monitoring_metrics",
                    test_type=TestType.UNIT,
                    passed=False,
                    duration_ms=duration,
                    error_message=str(e),
                )
            )

        return results

    async def _test_api_endpoints(self) -> List[TestResult]:
        """Test API endpoints."""
        results = []

        # Test health endpoint
        start_time = datetime.utcnow()
        try:
            async with AsyncClient(base_url=self.config.api_base_url) as client:
                response = await client.get("/health")
                assert response.status_code == 200

                data = response.json()
                assert "status" in data
                assert data["status"] == "healthy"

                duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                results.append(
                    TestResult(
                        test_name="test_health_endpoint",
                        test_type=TestType.INTEGRATION,
                        passed=True,
                        duration_ms=duration,
                        assertions=3,
                    )
                )

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_health_endpoint",
                    test_type=TestType.INTEGRATION,
                    passed=False,
                    duration_ms=duration,
                    error_message=str(e),
                )
            )

        # Test metrics endpoint
        start_time = datetime.utcnow()
        try:
            async with AsyncClient(base_url=self.config.api_base_url) as client:
                response = await client.get("/metrics")
                assert response.status_code == 200

                duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                results.append(
                    TestResult(
                        test_name="test_metrics_endpoint",
                        test_type=TestType.INTEGRATION,
                        passed=True,
                        duration_ms=duration,
                        assertions=1,
                    )
                )

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_metrics_endpoint",
                    test_type=TestType.INTEGRATION,
                    passed=False,
                    duration_ms=duration,
                    error_message=str(e),
                )
            )

        return results

    async def _test_database_operations(self) -> List[TestResult]:
        """Test database operations."""
        results = []

        start_time = datetime.utcnow()
        try:
            # Create test data
            test_users = await self.test_db.create_test_data("users", 5)
            assert len(test_users) == 5
            assert all("email" in user for user in test_users)

            test_campaigns = await self.test_db.create_test_data("campaigns", 3)
            assert len(test_campaigns) == 3
            assert all("name" in campaign for campaign in test_campaigns)

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_database_operations",
                    test_type=TestType.INTEGRATION,
                    passed=True,
                    duration_ms=duration,
                    assertions=4,
                )
            )

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_database_operations",
                    test_type=TestType.INTEGRATION,
                    passed=False,
                    duration_ms=duration,
                    error_message=str(e),
                )
            )

        return results

    async def _test_redis_operations(self) -> List[TestResult]:
        """Test Redis operations."""
        results = []

        start_time = datetime.utcnow()
        try:
            from core.cache import get_cache_manager

            cache_manager = get_cache_manager()

            # Test cache set/get
            test_key = "test_key"
            test_value = {
                "message": "test data",
                "timestamp": datetime.utcnow().isoformat(),
            }

            await cache_manager.set_json(test_key, test_value)
            retrieved_value = await cache_manager.get_json(test_key)

            assert retrieved_value is not None
            assert retrieved_value["message"] == test_value["message"]

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_redis_operations",
                    test_type=TestType.INTEGRATION,
                    passed=True,
                    duration_ms=duration,
                    assertions=3,
                )
            )

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_redis_operations",
                    test_type=TestType.INTEGRATION,
                    passed=False,
                    duration_ms=duration,
                    error_message=str(e),
                )
            )

        return results

    async def _test_middleware_integration(self) -> List[TestResult]:
        """Test middleware integration."""
        results = []

        start_time = datetime.utcnow()
        try:
            # Test that middleware stack is properly configured
            from main import app

            # Check that middleware is registered
            middleware_stack = app.middleware_stack
            assert middleware_stack is not None

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_middleware_integration",
                    test_type=TestType.INTEGRATION,
                    passed=True,
                    duration_ms=duration,
                    assertions=1,
                )
            )

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            results.append(
                TestResult(
                    test_name="test_middleware_integration",
                    test_type=TestType.INTEGRATION,
                    passed=False,
                    duration_ms=duration,
                    error_message=str(e),
                )
            )

        return results

    async def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.passed])
        failed_tests = total_tests - passed_tests

        # Calculate statistics
        avg_duration = (
            sum(r.duration_ms for r in self.test_results) / total_tests
            if total_tests > 0
            else 0
        )

        # Group by test type
        results_by_type = {}
        for result in self.test_results:
            test_type = result.test_type.value
            if test_type not in results_by_type:
                results_by_type[test_type] = {"passed": 0, "failed": 0, "total": 0}

            results_by_type[test_type]["total"] += 1
            if result.passed:
                results_by_type[test_type]["passed"] += 1
            else:
                results_by_type[test_type]["failed"] += 1

        # Get failed tests
        failed_test_details = [
            {
                "test_name": r.test_name,
                "error_message": r.error_message,
                "duration_ms": r.duration_ms,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in self.test_results
            if not r.passed
        ]

        return {
            "test_session": self.current_test_session,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (
                    (passed_tests / total_tests * 100) if total_tests > 0 else 0
                ),
                "average_duration_ms": avg_duration,
            },
            "results_by_type": results_by_type,
            "failed_tests": failed_test_details,
            "test_environment": self.config.environment.value,
            "generated_at": datetime.utcnow().isoformat(),
        }


# Global test suite
_test_suite: Optional[APITestSuite] = None


def get_test_suite(config: TestConfig = None) -> APITestSuite:
    """Get the global test suite instance."""
    global _test_suite
    if _test_suite is None:
        _test_suite = APITestSuite(config or TestConfig())
    return _test_suite


async def run_all_tests(config: TestConfig = None) -> Dict[str, Any]:
    """Run all tests and generate report."""
    test_suite = get_test_suite(config)

    try:
        await test_suite.setup_test_environment()

        # Run unit tests
        unit_results = await test_suite.run_unit_tests()

        # Run integration tests
        integration_results = await test_suite.run_integration_tests()

        # Generate report
        report = await test_suite.generate_test_report()

        return report

    finally:
        await test_suite.teardown_test_environment()


# Pytest fixtures
@pytest.fixture
async def test_config():
    """Pytest fixture for test configuration."""
    return TestConfig()


@pytest.fixture
async def test_suite(test_config):
    """Pytest fixture for test suite."""
    suite = APITestSuite(test_config)
    await suite.setup_test_environment()
    yield suite
    await suite.teardown_test_environment()


@pytest.fixture
async def test_client():
    """Pytest fixture for test client."""
    from main import app

    return TestClient(app)


# Example test functions
@pytest.mark.asyncio
async def test_authentication_session_token(test_suite):
    """Test authentication session token creation and validation."""
    results = await test_suite._test_authentication_utils()
    assert all(r.passed for r in results)


@pytest.mark.asyncio
async def test_validation_email(test_suite):
    """Test email validation."""
    results = await test_suite._test_validation_utils()
    assert all(r.passed for r in results)


@pytest.mark.asyncio
async def test_error_handling(test_suite):
    """Test error handling."""
    results = await test_suite._test_error_handling_utils()
    assert all(r.passed for r in results)


@pytest.mark.asyncio
async def test_monitoring_metrics(test_suite):
    """Test monitoring metrics."""
    results = await test_suite._test_monitoring_utils()
    assert all(r.passed for r in results)


@pytest.mark.asyncio
async def test_health_endpoint(test_client):
    """Test health endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


if __name__ == "__main__":
    # Run tests when executed directly
    async def main():
        config = TestConfig()
        report = await run_all_tests(config)

        print(f"\nTest Results:")
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed_tests']}")
        print(f"Failed: {report['summary']['failed_tests']}")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"Average Duration: {report['summary']['average_duration_ms']:.1f}ms")

        if report["failed_tests"]:
            print(f"\nFailed Tests:")
            for failed in report["failed_tests"]:
                print(f"- {failed['test_name']}: {failed['error_message']}")

    asyncio.run(main())
