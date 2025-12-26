"""
Mock Dependencies for Memory System Testing

Provides mock implementations of external dependencies to avoid import issues during testing.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("raptorflow.memory.mocks")


class MockInferenceProvider:
    """Mock implementation of InferenceProvider for testing."""

    @classmethod
    def get_model(cls, model_tier: str = "fast", temperature: float = 0.0, **kwargs):
        """Mock model getter."""
        return MockModel(model_tier, temperature)

    @classmethod
    def get_embeddings(cls):
        """Mock embeddings getter."""
        return MockEmbeddings()


class MockModel:
    """Mock LLM model for testing."""

    def __init__(self, model_tier: str, temperature: float):
        self.model_tier = model_tier
        self.temperature = temperature

    def with_structured_output(self, output_schema):
        """Mock structured output wrapper."""
        return self

    async def ainvoke(self, prompt: str) -> "MockResponse":
        """Mock async invoke."""
        return MockResponse(f"Mock response for: {prompt[:50]}...")

    def invoke(self, prompt: str) -> "MockResponse":
        """Mock invoke."""
        return MockResponse(f"Mock response for: {prompt[:50]}...")


class MockResponse:
    """Mock LLM response."""

    def __init__(self, content: str):
        self.content = content
        self.response_metadata = {
            "token_usage": {"prompt_token_count": 10, "candidates_token_count": 5}
        }


class MockEmbeddings:
    """Mock embeddings provider."""

    async def aembed_query(self, text: str) -> List[float]:
        """Mock async embedding generation."""
        # Generate deterministic mock embeddings based on text hash
        hash_val = hash(text) % 1000
        return [hash_val / 1000.0] * 1536  # Mock 1536-dimensional embedding

    def embed_query(self, text: str) -> List[float]:
        """Mock embedding generation."""
        return asyncio.run(self.aembed_query(text))


class MockMemoryManager:
    """Mock memory manager for testing."""

    def __init__(self):
        self.l1 = MockL1Memory()
        self.l2 = MockL2Memory()
        self.l3 = MockL3Memory()


class MockL1Memory:
    """Mock L1 short-term memory."""

    def __init__(self):
        self.storage: Dict[str, Any] = {}

    async def store(self, key: str, value: Any, ttl: Optional[int] = None):
        """Mock store."""
        self.storage[key] = value

    async def retrieve(self, key: str) -> Optional[Any]:
        """Mock retrieve."""
        return self.storage.get(key)


class MockL2Memory:
    """Mock L2 episodic memory."""

    def __init__(self):
        self.episodes: List[Dict] = []

    async def recall_similar(
        self,
        workspace_id: str,
        query_embedding: List[float],
        limit: int = 10,
        filters: Optional[Dict] = None,
    ) -> List[Dict]:
        """Mock recall similar episodes."""
        # Return mock episodes
        return [
            {
                "id": f"episode_{i}",
                "content": f"Mock episode content {i}",
                "metadata": {"type": "episodic"},
                "similarity": 0.8 - (i * 0.1),
            }
            for i in range(min(limit, 5))
        ]

    async def store_episode(
        self,
        workspace_id: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict] = None,
    ):
        """Mock store episode."""
        self.episodes.append(
            {
                "id": f"episode_{len(self.episodes)}",
                "content": content,
                "embedding": embedding,
                "metadata": metadata or {},
            }
        )


class MockL3Memory:
    """Mock L3 semantic memory."""

    def __init__(self):
        self.foundations: List[Dict] = []

    async def search_foundation(
        self, workspace_id: str, query: str, limit: int = 10
    ) -> List[Dict]:
        """Mock search foundation."""
        return [
            {
                "id": f"foundation_{i}",
                "content": f"Mock foundation content {i}",
                "metadata": {"type": "foundation"},
                "similarity": 0.9 - (i * 0.1),
            }
            for i in range(min(limit, 3))
        ]

    async def remember_foundation(
        self,
        workspace_id: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict] = None,
    ):
        """Mock remember foundation."""
        self.foundations.append(
            {
                "id": f"foundation_{len(self.foundations)}",
                "content": content,
                "embedding": embedding,
                "metadata": metadata or {},
            }
        )


class MockSwarmLearning:
    """Mock swarm learning system."""

    def __init__(self):
        self.knowledge: Dict[str, List[Dict]] = {"L1": [], "L2": [], "L3": []}

    async def retrieve_swarm_knowledge(
        self, workspace_id: str, query: str, limit: int = 20
    ) -> Dict[str, List[Dict]]:
        """Mock retrieve swarm knowledge."""
        return {
            "L1": [
                {"content": f"Mock L1 knowledge {i}", "metadata": {}} for i in range(3)
            ],
            "L2": [
                {"content": f"Mock L2 knowledge {i}", "metadata": {}} for i in range(2)
            ],
            "L3": [
                {"content": f"Mock L3 knowledge {i}", "metadata": {}} for i in range(1)
            ],
        }

    async def record_learning(
        self,
        workspace_id: str,
        learning: str,
        confidence: float,
        metadata: Optional[Dict] = None,
    ):
        """Mock record learning."""
        for tier in self.knowledge:
            self.knowledge[tier].append(
                {
                    "content": learning,
                    "confidence": confidence,
                    "metadata": metadata or {},
                }
            )


class MockCapabilityProfile:
    """Mock capability profile."""

    def __init__(self):
        self.allowed_tools = ["all"]
        self.agent_capabilities = {}

    def allows_tool(self, tool_name: str) -> bool:
        """Mock tool permission check."""
        return True


class MockSettings:
    """Mock settings object."""

    def __init__(self):
        self.VERTEX_AI_API_KEY = "mock_api_key"
        self.INFERENCE_SIMPLE = "mock_simple"


# Mock registry for dependency injection
_mocks = {
    "InferenceProvider": MockInferenceProvider,
    "MemoryManager": MockMemoryManager,
    "SwarmLearning": MockSwarmLearning,
    "CapabilityProfile": MockCapabilityProfile,
    "get_settings": lambda: MockSettings(),
}


def register_mock(name: str, mock_class):
    """Register a mock class."""
    _mocks[name] = mock_class


def get_mock(name: str):
    """Get a mock class."""
    return _mocks.get(name)


def setup_mocks():
    """Setup all mocks for testing."""
    # This would be called in test setup
    import sys

    # Mock the backend modules
    sys.modules["backend.inference"] = type(
        "MockModule", (), {"InferenceProvider": MockInferenceProvider}
    )()

    sys.modules["backend.memory.manager"] = type(
        "MockModule", (), {"MemoryManager": MockMemoryManager}
    )()

    sys.modules["backend.memory.swarm_learning"] = type(
        "MockModule", (), {"SwarmLearning": MockSwarmLearning}
    )()

    sys.modules["backend.models.capabilities"] = type(
        "MockModule", (), {"CapabilityProfile": MockCapabilityProfile}
    )()

    sys.modules["backend.core.config"] = type(
        "MockModule", (), {"get_settings": lambda: MockSettings()}
    )()

    logger.info("All mocks setup complete")


def cleanup_mocks():
    """Cleanup mocks after testing."""
    import sys

    modules_to_remove = [
        "backend.inference",
        "backend.memory.manager",
        "backend.memory.swarm_learning",
        "backend.models.capabilities",
        "backend.core.config",
    ]

    for module in modules_to_remove:
        if module in sys.modules:
            del sys.modules[module]

    logger.info("All mocks cleaned up")


# Test context manager for mocks
class MockContext:
    """Context manager for setting up and cleaning up mocks."""

    def __enter__(self):
        setup_mocks()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        cleanup_mocks()
        return False


# Helper functions for testing
def create_test_fragment(
    agent_id: str = "test_agent",
    agent_type: str = "test",
    content: str = "Test content",
    importance_score: float = 0.5,
) -> "MemoryFragment":
    """Create a test memory fragment."""
    from memory.consolidated import MemoryFragment

    return MemoryFragment(
        agent_id=agent_id,
        agent_type=agent_type,
        content=content,
        importance_score=importance_score,
    )


def create_test_state(
    workspace_id: str = "test_workspace", messages: Optional[List] = None, **kwargs
) -> Dict[str, Any]:
    """Create a test cognitive state."""
    from models.cognitive import AgentMessage

    return {
        "workspace_id": workspace_id,
        "messages": messages or [],
        "last_agent": "test_agent",
        "raw_prompt": "Test prompt",
        **kwargs,
    }


async def run_with_mocks(test_func, *args, **kwargs):
    """Run a test function with mocks setup."""
    with MockContext():
        return await test_func(*args, **kwargs)
