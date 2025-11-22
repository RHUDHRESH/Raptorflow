"""
Test configuration and fixtures for RaptorFlow backend tests.
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app
from backend.utils.cache import redis_cache
from backend.utils.queue import redis_queue


# ========== Pytest Configuration ==========

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ========== Mock Fixtures ==========

@pytest.fixture
def mock_supabase():
    """Mock Supabase client."""
    with patch('backend.services.supabase_client.supabase_client') as mock:
        # Configure mock methods
        mock.insert = AsyncMock(return_value={"id": str(uuid4())})
        mock.query = AsyncMock(return_value=[])
        mock.query_one = AsyncMock(return_value=None)
        mock.update = AsyncMock(return_value={"id": str(uuid4())})
        mock.delete = AsyncMock(return_value=True)
        mock.count = AsyncMock(return_value=0)
        yield mock


@pytest.fixture
def mock_vertex_ai():
    """Mock Vertex AI client."""
    with patch('backend.services.vertex_ai_client.vertex_ai_client') as mock:
        # Configure mock LLM responses
        mock.chat_completion = AsyncMock(return_value="Mocked LLM response")
        mock.generate = AsyncMock(return_value="Mocked generation")
        yield mock


@pytest.fixture
def mock_redis():
    """Mock Redis connections."""
    with patch('backend.utils.cache.redis_cache') as cache_mock, \
         patch('backend.utils.queue.redis_queue') as queue_mock:

        # Configure cache mock
        cache_mock.connect = AsyncMock()
        cache_mock.disconnect = AsyncMock()
        cache_mock.get = AsyncMock(return_value=None)
        cache_mock.set = AsyncMock(return_value=True)
        cache_mock.delete = AsyncMock(return_value=True)
        cache_mock.exists = AsyncMock(return_value=False)
        cache_mock.redis = MagicMock()
        cache_mock.redis.ping = AsyncMock()

        # Configure queue mock
        queue_mock.connect = AsyncMock()
        queue_mock.disconnect = AsyncMock()
        queue_mock.enqueue = AsyncMock(return_value="test-correlation-id")
        queue_mock.dequeue = AsyncMock(return_value=None)
        queue_mock.redis = MagicMock()
        queue_mock.redis.ping = AsyncMock()

        yield cache_mock, queue_mock


@pytest.fixture
def mock_auth():
    """Mock authentication."""
    test_user_id = str(uuid4())
    test_workspace_id = str(uuid4())

    async def mock_get_current_user():
        return {
            "user_id": test_user_id,
            "workspace_id": test_workspace_id,
            "email": "test@example.com",
            "role": "admin"
        }

    with patch('backend.main.get_current_user_and_workspace', new=mock_get_current_user):
        yield {
            "user_id": test_user_id,
            "workspace_id": test_workspace_id
        }


# ========== HTTP Client Fixtures ==========

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP client for testing API endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def authenticated_client(mock_auth) -> AsyncGenerator[AsyncClient, None]:
    """Authenticated HTTP client with valid JWT."""
    async with AsyncClient(
        app=app,
        base_url="http://test",
        headers={"Authorization": "Bearer mock-jwt-token"}
    ) as ac:
        yield ac


# ========== Test Data Fixtures ==========

@pytest.fixture
def sample_icp():
    """Sample ICP data."""
    return {
        "id": str(uuid4()),
        "name": "B2B SaaS Startups",
        "description": "Early-stage B2B SaaS companies",
        "demographics": {
            "company_size": "10-50 employees",
            "revenue": "$1M-$10M ARR",
            "industry": "Software"
        },
        "psychographics": {
            "pain_points": ["Customer acquisition", "Product-market fit"],
            "goals": ["Scale revenue", "Improve retention"],
            "values": ["Innovation", "Efficiency"]
        }
    }


@pytest.fixture
def sample_strategy():
    """Sample strategy data."""
    return {
        "id": str(uuid4()),
        "goal": "Increase inbound leads by 50%",
        "timeframe_days": 90,
        "adapt_stage": "plan",
        "insights": {
            "market_trends": ["AI adoption", "Remote work"],
            "opportunities": ["Content marketing", "LinkedIn ads"]
        },
        "campaign_ideas": [
            {
                "name": "Thought Leadership Campaign",
                "channels": ["linkedin", "blog"],
                "budget": 10000
            }
        ]
    }


@pytest.fixture
def sample_content():
    """Sample content data."""
    return {
        "id": str(uuid4()),
        "type": "blog",
        "title": "How to Scale Your SaaS Business",
        "body": "Lorem ipsum dolor sit amet...",
        "meta": {
            "word_count": 1500,
            "reading_time": "7 min"
        }
    }


@pytest.fixture
def sample_workflow_request():
    """Sample workflow execution request."""
    return {
        "goal": "full_campaign",
        "research_query": "B2B SaaS startups",
        "research_mode": "quick",
        "strategy_mode": "quick",
        "content_type": "blog",
        "content_params": {
            "topic": "SaaS scaling strategies",
            "tone": "professional"
        },
        "publish_platforms": ["linkedin"]
    }


# ========== Graph Testing Fixtures ==========

@pytest.fixture
def mock_graph_results():
    """Mock results from domain graphs."""
    return {
        "onboarding": {
            "session_id": str(uuid4()),
            "profile": {"entity_type": "b2b_saas"}
        },
        "research": {
            "icp_id": str(uuid4()),
            "icp": {
                "name": "B2B SaaS Startups",
                "pain_points": ["Scaling", "Retention"]
            }
        },
        "strategy": {
            "strategy_id": str(uuid4()),
            "campaign_ideas": [{"name": "Content Campaign"}]
        },
        "content": {
            "content_ids": [str(uuid4())],
            "content": "Sample blog post content"
        },
        "critic": {
            "recommendation": "approve",
            "overall_score": 90
        },
        "integration": {
            "assets": [{"type": "image", "url": "https://example.com/image.png"}]
        },
        "execution": {
            "published": ["linkedin"],
            "analytics": {"impressions": 1000}
        }
    }


# ========== Helper Functions ==========

@pytest.fixture
def make_correlation_id():
    """Factory for generating correlation IDs."""
    def _make():
        return f"test-{uuid4()}"
    return _make


@pytest.fixture
def assert_correlation_id():
    """Helper to assert correlation ID is present in response."""
    def _assert(response):
        assert "X-Correlation-ID" in response.headers
        assert response.headers["X-Correlation-ID"]
        return response.headers["X-Correlation-ID"]
    return _assert
