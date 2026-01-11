"""
Cognitive Test Configuration and Fixtures

Provides test fixtures and configuration for cognitive engine tests.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock

import pytest

from backend.cognitive.critic.adversarial import AdversarialCritic
from backend.cognitive.hitl.gate import ApprovalGate
from backend.cognitive.models import ExecutionPlan, PerceivedInput, ReflectionResult
from backend.cognitive.perception.module import PerceptionModule
from backend.cognitive.planning.module import PlanningModule
from backend.cognitive.reflection.module import ReflectionModule
from backend.llm import LLMClient


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing."""
    client = Mock(spec=LLMClient)

    # Mock generate method
    mock_response = Mock()
    mock_response.text = '{"test": "response"}'
    client.generate = AsyncMock(return_value=mock_response)

    return client


@pytest.fixture
def sample_perceived_input():
    """Sample perceived input for testing."""
    return PerceivedInput(
        raw_text="Create a marketing email for our new product",
        entities={"product": "new product"},
        intent="create",
        sentiment="neutral",
        urgency=2,
        context_signals={"topic": "marketing"},
    )


@pytest.fixture
def sample_execution_plan():
    """Sample execution plan for testing."""
    return ExecutionPlan(
        goal="Create marketing email",
        steps=[
            {
                "id": "1",
                "description": "Draft email content",
                "agent": "content_agent",
                "tools": ["text_editor"],
                "inputs": {"product": "new product"},
                "outputs": {"email_draft"},
                "dependencies": [],
                "estimated_tokens": 500,
                "estimated_cost": 0.01,
                "estimated_time": 30,
            }
        ],
        estimated_cost=0.01,
        estimated_time=30,
        risk_level=1,
        requires_approval=False,
    )


@pytest.fixture
def sample_reflection_result():
    """Sample reflection result for testing."""
    return ReflectionResult(
        initial_score={
            "overall": 65,
            "dimensions": {"accuracy": 70, "relevance": 60},
            "issues": [{"severity": "medium", "description": "Needs improvement"}],
            "passed": False,
        },
        final_score={
            "overall": 85,
            "dimensions": {"accuracy": 90, "relevance": 80},
            "issues": [],
            "passed": True,
        },
        corrections_applied=[
            {
                "target": "content",
                "action": "improve_clarity",
                "expected_improvement": "better readability",
            }
        ],
        iterations=2,
        approved=True,
        processing_time=5.2,
        timestamp=datetime.now(),
    )


@pytest.fixture
def perception_module(mock_llm_client):
    """Perception module fixture."""
    return PerceptionModule(llm_client=mock_llm_client)


@pytest.fixture
def planning_module(mock_llm_client):
    """Planning module fixture."""
    return PlanningModule(llm_client=mock_llm_client)


@pytest.fixture
def reflection_module(mock_llm_client):
    """Reflection module fixture."""
    return ReflectionModule()


@pytest.fixture
def approval_gate():
    """Approval gate fixture."""
    # Use mock Redis client for testing
    from backend.redis.client import RedisClient

    mock_redis = Mock(spec=RedisClient)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.lpush = AsyncMock(return_value=True)
    mock_redis.expire = AsyncMock(return_value=True)

    return ApprovalGate(redis_client=mock_redis)


@pytest.fixture
def adversarial_critic(mock_llm_client):
    """Adversarial critic fixture."""
    return AdversarialCritic(llm_client=mock_llm_client)


@pytest.fixture
def test_workspace_context():
    """Test workspace context."""
    return {
        "workspace_id": "test_workspace_123",
        "user_id": "test_user_456",
        "foundation": {
            "company_name": "Test Corp",
            "industry": "technology",
            "target_audience": "B2B",
        },
        "icps": [
            {
                "name": "Tech Manager",
                "role": "engineering_manager",
                "pain_points": ["team productivity", "tool adoption"],
            }
        ],
    }


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing."""
    from backend.redis.client import RedisClient

    mock_redis = Mock(spec=RedisClient)

    # Setup common Redis methods
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.delete = AsyncMock(return_value=True)
    mock_redis.exists = AsyncMock(return_value=False)
    mock_redis.expire = AsyncMock(return_value=True)
    mock_redis.ttl = AsyncMock(return_value=3600)
    mock_redis.incr = AsyncMock(return_value=1)
    mock_redis.decr = AsyncMock(return_value=0)
    mock_redis.lpush = AsyncMock(return_value=1)
    mock_redis.lrange = AsyncMock(return_value=[])
    mock_redis.ltrim = AsyncMock(return_value=True)
    mock_redis.lrem = AsyncMock(return_value=1)
    mock_redis.rpush = AsyncMock(return_value=1)
    mock_redis.publish = AsyncMock(return_value=1)

    return mock_redis


# Test data generators
def generate_test_text(length: int = 100) -> str:
    """Generate test text of specified length."""
    words = ["test", "data", "sample", "text", "content", "example"]
    result = []
    for i in range(length // 4 + 1):
        result.append(words[i % len(words)])
    return " ".join(result)


def generate_test_entities() -> Dict[str, Any]:
    """Generate test entities."""
    return {
        "person": ["John Doe", "Jane Smith"],
        "company": ["Test Corp", "Example Inc"],
        "product": ["Widget", "Gadget"],
        "location": ["New York", "San Francisco"],
        "date": ["2024-01-01", "2024-12-31"],
        "money": ["$100", "$500"],
        "percentage": ["25%", "50%"],
    }


# Async test helpers
@pytest.mark.asyncio
async def async_test_wrapper(test_func, *args, **kwargs):
    """Wrapper for async tests to handle cleanup."""
    try:
        await test_func(*args, **kwargs)
    except Exception as e:
        pytest.fail(f"Async test failed: {e}")


# Performance test markers
pytest.mark.performance = pytest.mark.skipif(
    not pytest.config.getoption("--run-performance"),
    reason="Performance tests disabled by default",
)

# Integration test markers
pytest.mark.integration = pytest.mark.skipif(
    not pytest.config.getoption("--run-integration"),
    reason="Integration tests disabled by default",
)
