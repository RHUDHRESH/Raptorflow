"""
Pytest configuration and fixtures for Raptorflow backend tests.
"""

import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from ..events.bus import EventBus
from ..infrastructure.storage import CloudStorage
from ..jobs.scheduler import JobScheduler
from ..redis_core.cache import CacheService
from ..redis_core.client import RedisClient
from ..redis_core.queue import QueueService
from ..redis_core.rate_limit import RateLimitService
from ..redis_core.session import SessionService
from ..redis_core.session_models import SessionData
from ..redis_core.usage import UsageTracker
from ..webhooks.handler import WebhookHandler
from fastapi import UploadFile
from io import BytesIO


@pytest.fixture
def sample_upload_file():
    """Create a sample UploadFile for testing."""
    def _create_file(filename="test.pdf", content=b"fake pdf content", content_type="application/pdf"):
        file_obj = BytesIO(content)
        return UploadFile(
            filename=filename,
            file=file_obj,
            headers={"content-type": content_type}
        )
    return _create_file


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def mock_redis() -> AsyncGenerator[AsyncMock, None]:
    """Mock Redis client for testing."""
    mock = AsyncMock()

    # Mock basic Redis operations
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = 1
    mock.exists.return_value = 0
    mock.expire.return_value = True
    mock.ttl.return_value = -1
    mock.incr.return_value = 1
    mock.decr.return_value = -1
    mock.keys.return_value = []

    yield mock


@pytest_asyncio.fixture
async def redis_client(mock_redis: AsyncMock) -> AsyncGenerator[RedisClient, None]:
    """Redis client fixture with mocked backend."""
    client = RedisClient()
    client._client = mock_redis
    yield client


@pytest.fixture
def test_session_data() -> SessionData:
    """Test session data fixture."""
    from datetime import datetime, timedelta

    return SessionData(
        session_id="test-session-123",
        user_id="test-user-456",
        workspace_id="test-workspace-789",
        current_agent="test-agent",
        messages=[{"role": "user", "content": "Hello"}],
        context={"key": "value"},
        created_at=datetime.utcnow(),
        last_active_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )


@pytest.fixture
def test_cache_data() -> dict:
    """Test cache data fixture."""
    return {
        "user_profile": {
            "name": "Test User",
            "email": "test@example.com",
            "preferences": {"theme": "dark"},
        },
        "workspace_settings": {
            "timezone": "UTC",
            "language": "en",
        },
    }


@pytest_asyncio.fixture
async def session_service(redis_client: RedisClient) -> SessionService:
    """Session service fixture."""
    return SessionService(redis_client)


@pytest_asyncio.fixture
async def cache_service(redis_client: RedisClient) -> CacheService:
    """Cache service fixture."""
    return CacheService(redis_client)


@pytest_asyncio.fixture
async def rate_limit_service(redis_client: RedisClient) -> RateLimitService:
    """Rate limit service fixture."""
    return RateLimitService(redis_client)


@pytest_asyncio.fixture
async def queue_service(redis_client: RedisClient) -> QueueService:
    """Queue service fixture."""
    return QueueService(redis_client)


@pytest_asyncio.fixture
async def usage_tracker(redis_client: RedisClient) -> UsageTracker:
    """Usage tracker fixture."""
    return UsageTracker(redis_client)


@pytest_asyncio.fixture
async def job_scheduler() -> AsyncGenerator[JobScheduler, None]:
    """Job scheduler fixture."""
    scheduler = JobScheduler()
    yield scheduler
    await scheduler.stop()


@pytest_asyncio.fixture
async def webhook_handler() -> WebhookHandler:
    """Webhook handler fixture."""
    return WebhookHandler()


@pytest_asyncio.fixture
async def cloud_storage() -> AsyncGenerator[CloudStorage, None]:
    """Cloud storage fixture with mocked client."""
    from unittest.mock import patch

    with patch("google.cloud.storage.Client") as mock_client:
        mock_storage = AsyncMock()
        mock_client.return_value = mock_storage

        storage = CloudStorage()
        storage._client = mock_storage
        yield storage


@pytest_asyncio.fixture
async def event_bus() -> AsyncGenerator[EventBus, None]:
    """Event bus fixture."""
    bus = EventBus()
    await bus.start()
    yield bus
    await bus.stop()


@pytest.fixture
def sample_webhook_event() -> dict:
    """Sample webhook event for testing."""
    return {
        "event_id": "webhook-123",
        "event_type": "user.created",
        "timestamp": "2024-01-01T00:00:00Z",
        "source": "supabase",
        "data": {
            "user_id": "user-456",
            "email": "test@example.com",
            "metadata": {"source": "signup"},
        },
    }


@pytest.fixture
def sample_job_data() -> dict:
    """Sample job data for testing."""
    return {
        "job_id": "job-123",
        "job_type": "memory_indexing",
        "workspace_id": "workspace-789",
        "user_id": "user-456",
        "payload": {"action": "reindex", "scope": "full"},
        "priority": 1,
    }


@pytest.fixture
def mock_bigquery_client() -> AsyncGenerator[MagicMock, None]:
    """Mock BigQuery client for testing."""
    from unittest.mock import patch

    with patch("google.cloud.bigquery.Client") as mock_client:
        mock_bq = MagicMock()
        mock_client.return_value = mock_bq

        # Mock query results
        mock_bq.query.return_value.result.return_value = [
            {"date": "2024-01-01", "count": 10, "cost": 5.0},
            {"date": "2024-01-02", "count": 15, "cost": 7.5},
        ]

        yield mock_bq


# Test configuration
@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings."""
    import os

    # Set test environment variables
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DEBUG"] = "true"
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["DATABASE_URL"] = "sqlite:///test.db"
    os.environ["UPSTASH_REDIS_URL"] = "redis://localhost:6379"
    os.environ["UPSTASH_REDIS_TOKEN"] = "test-token"
    os.environ["VERTEX_AI_PROJECT_ID"] = "test-project"
    os.environ["GCP_PROJECT_ID"] = "test-project"
    os.environ["WEBHOOK_SECRET"] = "test-webhook-secret"

    yield

    # Clean up environment variables
    test_vars = [
        "ENVIRONMENT",
        "DEBUG",
        "SECRET_KEY",
        "DATABASE_URL",
        "UPSTASH_REDIS_URL",
        "UPSTASH_REDIS_TOKEN",
        "VERTEX_AI_PROJECT_ID",
        "GCP_PROJECT_ID",
        "WEBHOOK_SECRET",
    ]

    for var in test_vars:
        os.environ.pop(var, None)


# Async test helpers
@pytest.fixture
def async_test():
    """Decorator for async test functions."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(func(*args, **kwargs))

        return wrapper

    return decorator


# Database fixtures
@pytest_asyncio.fixture
async def test_db():
    """Test database fixture."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    from ..db.base import Base

    Base.metadata.create_all(bind=engine)

    yield SessionLocal

    # Clean up
    Base.metadata.drop_all(bind=engine)


# Mock services
@pytest.fixture
def mock_notification_service():
    """Mock notification service."""
    service = AsyncMock()
    service.create_notification.return_value = {"id": "notif-123"}
    service.create_workspace_notification.return_value = {"id": "notif-456"}
    return service


@pytest.fixture
def mock_email_service():
    """Mock email service."""
    service = AsyncMock()
    service.is_enabled.return_value = True
    service.send_approval_request_email.return_value = True
    service.send_usage_warning_email.return_value = True
    return service


@pytest.fixture
def mock_memory_service():
    """Mock memory service."""
    service = AsyncMock()
    service.index_foundation_data.return_value = True
    return service


# Performance testing fixtures
@pytest.fixture
def performance_data():
    """Performance test data."""
    return {
        "small_dataset": list(range(100)),
        "medium_dataset": list(range(1000)),
        "large_dataset": list(range(10000)),
    }


# Error testing fixtures
@pytest.fixture
def error_scenarios():
    """Common error scenarios for testing."""
    return {
        "redis_connection_error": Exception("Redis connection failed"),
        "database_error": Exception("Database query failed"),
        "network_timeout": TimeoutError("Network timeout"),
        "authentication_error": Exception("Authentication failed"),
        "rate_limit_error": Exception("Rate limit exceeded"),
        "validation_error": ValueError("Invalid input"),
    }
