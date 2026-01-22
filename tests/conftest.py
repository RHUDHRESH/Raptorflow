"""
Test configuration and fixtures
"""

import asyncio
from typing import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest

# Import test fixtures from submodules
from .db.conftest import (
    assert_valid_asset_type,
    assert_valid_email,
    assert_valid_platform,
    assert_valid_status,
    assert_valid_subscription_tier,
    assert_valid_uuid,
    event_loop,
    generate_test_foundation_data,
    generate_test_icp_data,
    generate_test_user_data,
    generate_test_workspace_data,
    mock_auth_context,
    mock_supabase_client,
    mock_user,
    mock_workspace,
    sample_agent_execution,
    sample_blackbox_strategy,
    sample_campaign,
    sample_daily_win,
    sample_foundation,
    sample_icp,
    sample_move,
    sample_muse_asset,
    test_database,
)

# Make all fixtures available
__all__ = [
    # Database fixtures
    "mock_supabase_client",
    "mock_user",
    "mock_workspace",
    "mock_auth_context",
    "sample_foundation",
    "sample_icp",
    "sample_move",
    "sample_campaign",
    "sample_muse_asset",
    "sample_blackbox_strategy",
    "sample_daily_win",
    "sample_agent_execution",
    "test_database",
    "event_loop",
    # Utility functions
    "assert_valid_uuid",
    "assert_valid_email",
    "assert_valid_subscription_tier",
    "assert_valid_asset_type",
    "assert_valid_platform",
    "assert_valid_status",
    "generate_test_user_data",
    "generate_test_workspace_data",
    "generate_test_foundation_data",
    "generate_test_icp_data",
]


# Test configuration
def pytest_configure(config):
    """Configure pytest settings"""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')",
        "integration: marks tests as integration tests",
        "unit: marks tests as unit tests",
    )
    config.addinivalue_line(
        "filterwarnings",
        "ignore::DeprecationWarning",
        "ignore::PendingDeprecationWarning",
    )


# Async test configuration
@pytest.fixture(scope="session")
def event_loop_policy():
    """Create event loop policy for async tests"""
    policy = asyncio.DefaultEventLoopPolicy()
    return policy


# Test database setup
@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Setup test database before tests"""
    # This would set up a test database
    # For now, we'll use mocks
    yield

    # Cleanup would happen here


# Global test utilities
@pytest.fixture
def mock_redis():
    """Mock Redis client for testing"""
    redis_client = AsyncMock()
    redis_client.ping.return_value = True
    redis_client.get.return_value = None
    redis_client.set.return_value = True
    redis_client.delete.return_value = 1
    return redis_client


@pytest.fixture
def mock_email_service():
    """Mock email service for testing"""
    email_service = AsyncMock()
    email_service.send_email.return_value = {"message_id": "test-id"}
    return email_service


@pytest.fixture
def mock_payment_service():
    """Mock payment service for testing"""
    payment_service = AsyncMock()
    payment_service.create_payment.return_value = {"payment_id": "test-id"}
    payment_service.process_payment.return_value = {"status": "success"}
    return payment_service


# Test data generators
@pytest.fixture
def generate_test_move_data():
    """Generate test move data"""
    return {
        "name": "Test Move",
        "category": "ignite",
        "goal": "Test goal",
        "strategy": {"approach": "test"},
        "execution_plan": [{"step": "Plan", "duration": 1}],
        "duration_days": 30,
        "success_metrics": [{"metric": "coverage", "target": 90}],
    }


@pytest.fixture
def generate_test_campaign_data():
    """Generate test campaign data"""
    return {
        "name": "Test Campaign",
        "description": "Test description",
        "target_icps": [],
        "phases": [{"phase": "Planning", "duration": 7}],
        "budget_usd": 1000.0,
        "success_metrics": [{"metric": "leads", "target": 100}],
    }


@pytest.fixture
def generate_test_asset_data():
    """Generate test asset data"""
    return {
        "title": "Test Asset",
        "content": "Test content",
        "asset_type": "email",
        "metadata": {"word_count": 100},
        "quality_score": 75,
    }


@pytest.fixture
def generate_test_strategy_data():
    """Generate test strategy data"""
    return {
        "name": "Test Strategy",
        "focus_area": "acquisition",
        "risk_level": 5,
        "risk_reasons": ["Test reason"],
        "phases": [{"phase": "Research", "duration_days": 7}],
        "expected_upside": "Test upside",
    }


@pytest.fixture
def generate_test_win_data():
    """Generate test daily win data"""
    return {
        "topic": "Test Topic",
        "angle": "Test angle",
        "hook": "Test hook",
        "platform": "twitter",
        "estimated_minutes": 15,
        "relevance_score": 80,
    }


# Mock service fixtures
@pytest.fixture
def mock_ai_service():
    """Mock AI service for testing"""
    ai_service = AsyncMock()
    ai_service.generate_content.return_value = {
        "content": "Generated content",
        "quality_score": 85,
        "tokens_used": 1000,
        "cost_usd": 0.01,
    }
    return ai_service


@pytest.fixture
def mock_notification_service():
    """Mock notification service for testing"""
    notification_service = AsyncMock()
    notification_service.send_notification.return_value = {"notification_id": "test-id"}
    return notification_service


@pytest.fixture
def mock_analytics_service():
    """Mock analytics service for testing"""
    analytics_service = AsyncMock()
    analytics_service.track_event.return_value = True
    analytics_service.get_metrics.return_value = {
        "page_views": 100,
        "unique_visitors": 50,
        "conversion_rate": 0.05,
    }
    return analytics_service


# Environment configuration
@pytest.fixture
def test_environment():
    """Test environment configuration"""
    import os

    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///test.db"
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"

    yield

    # Cleanup
    os.environ.pop("TESTING", None)
    os.environ.pop("DATABASE_URL", None)
    os.environ.pop("REDIS_URL", None)


# Test logging configuration
@pytest.fixture
def test_logger():
    """Test logger configuration"""
    import logging

    # Configure test logger
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger = logging.getLogger("test")
    return logger


# Performance testing utilities
@pytest.fixture
def performance_monitor():
    """Performance monitoring utility"""
    import time

    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.duration = None

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.end_time = time.time()
            self.duration = self.end_time - self.start_time

        def get_duration(self):
            return self.duration

    return PerformanceMonitor()


# Test data cleanup utilities
@pytest.fixture
def test_data_cleaner():
    """Test data cleanup utility"""
    cleaned_items = []

    class TestDataCleaner:
        def add_item(self, item_id):
            cleaned_items.append(item_id)

        def cleanup(self):
            cleaned_items.clear()

        def get_cleaned_items(self):
            return cleaned_items.copy()

    return TestDataCleaner()


# Security testing utilities
@pytest.fixture
def security_tester():
    """Security testing utility"""

    class SecurityTester:
        def test_sql_injection(self, input_string):
            """Test for SQL injection vulnerabilities"""
            sql_patterns = [
                "SELECT",
                "INSERT",
                "UPDATE",
                "DELETE",
                "DROP",
                "UNION",
                "OR 1=1",
                "--",
                "/*",
                "*/",
                "xp_cmdshell",
                "exec(",
                "eval(",
            ]

            return any(
                pattern.lower() in input_string.lower() for pattern in sql_patterns
            )

        def test_xss(self, input_string):
            """Test for XSS vulnerabilities"""
            xss_patterns = [
                "<script>",
                "</script>",
                "javascript:",
                "onerror=",
                "onload=",
                "onclick=",
                "<img",
                "<iframe",
                "<object>",
                "<embed",
            ]

            return any(
                pattern.lower() in input_string.lower() for pattern in xss_patterns
            )

        def test_path_traversal(self, input_string):
            """Test for path traversal vulnerabilities"""
            traversal_patterns = [
                "../",
                "..\\",
                "/etc/passwd",
                "/etc/shadow",
                "C:\\Windows\\System32",
                "C:\\Windows\\",
            ]

            return any(pattern in input_string for pattern in traversal_patterns)

    return SecurityTester()


# Rate limiting test utilities
@pytest.fixture
def rate_limiter():
    """Rate limiting test utility"""

    class RateLimiter:
        def __init__(self, limit=100, window=60):
            self.limit = limit
            self.window = window
            self.requests = []

        def is_allowed(self, user_id):
            """Check if request is allowed"""
            now = time.time()

            # Remove old requests outside window
            self.requests = [
                req_time for req_time in self.requests if now - req_time < self.window
            ]

            # Count requests for this user
            user_requests = len([req for req in self.requests if req_time < now])

            return user_requests < self.limit

        def record_request(self, user_id):
            """Record a request"""
            self.requests.append(time.time())

    return RateLimiter()


# Mock HTTP client for testing
@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing"""
    client = AsyncMock()

    # Mock response
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"data": "test"}
    response.text.return_value = "test response"

    client.get.return_value = response
    client.post.return_value = response
    client.put.return_value = response
    client.delete.return_value = response

    return client


# File system test utilities
@pytest.fixture
def file_system_tester():
    """File system test utility"""
    import os
    import tempfile

    class FileSystemTester:
        def __init__(self):
            self.temp_dir = tempfile.mkdtemp()

        def create_test_file(self, filename, content="test"):
            """Create a test file"""
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, "w") as f:
                f.write(content)
            return filepath

        def read_test_file(self, filename):
            """Read a test file"""
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, "r") as f:
                return f.read()

        def delete_test_file(self, filename):
            """Delete a test file"""
            filepath = os.path.join(self.temp_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)

        def cleanup(self):
            """Clean up test directory"""
            import shutil

            shutil.rmtree(self.temp_dir)

    return FileSystemTester()


# Time-based test utilities
@pytest.fixture
def time_traveler():
    """Time travel utility for testing"""
    import time
    from unittest.mock import patch

    class TimeTraveler:
        def __init__(self):
            self.patches = []

        def travel_to(self, target_time):
            """Travel to a specific time"""
            patcher = patch("time.time", return_value=target_time)
            self.patches.append(patcher)
            patcher.start()

        def travel_back(self):
            """Travel back to original time"""
            if self.patches:
                self.patches.pop().stop()

        def cleanup(self):
            """Clean up all patches"""
            while self.patches:
                self.patches.pop().stop()

    return TimeTraveler()
