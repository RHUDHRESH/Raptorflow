"""
Pytest fixtures for memory tests.

This module provides common fixtures and utilities for testing
the memory system components.
"""

import asyncio
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.memory.graph_models import (
    EntityType,
    GraphEntity,
    GraphRelationship,
    RelationType,
)
from backend.memory.models import MemoryChunk, MemoryType


@pytest.fixture
def test_workspace_id() -> str:
    """Test workspace ID."""
    return "test-workspace-123"


@pytest.fixture
def test_user_id() -> str:
    """Test user ID."""
    return "test-user-456"


@pytest.fixture
def sample_foundation() -> Dict[str, Any]:
    """Sample foundation data for testing."""
    return {
        "id": "foundation-123",
        "company_info": {
            "name": "Test Company",
            "description": "A test company for memory system testing",
            "industry": "Technology",
            "size": "Medium",
            "location": "San Francisco",
        },
        "mission": "To revolutionize memory systems",
        "vision": "A world with perfect memory recall",
        "values": ["Innovation", "Quality", "Integrity"],
        "usps": [
            "Advanced vector embeddings",
            "Intelligent graph relationships",
            "Real-time episodic memory",
        ],
        "features": ["Vector search", "Knowledge graph", "Conversation tracking"],
        "target_market": "Enterprise customers",
        "competitive_advantage": "Proprietary AI algorithms",
    }


@pytest.fixture
def sample_icp() -> Dict[str, Any]:
    """Sample ICP data for testing."""
    return {
        "id": "icp-123",
        "basic_info": {
            "name": "Tech Innovators",
            "description": "Early adopters of technology",
            "industry": "Technology",
            "size": "Small to Medium",
        },
        "demographics": {
            "age_range": "25-45",
            "education": "Bachelor's degree or higher",
            "income": "$75k+",
        },
        "psychographics": {
            "personality": "Innovative, risk-takers",
            "values": ["Efficiency", "Growth", "Innovation"],
        },
        "behaviors": [
            "Early technology adopters",
            "Active on social media",
            "Read tech blogs",
        ],
        "pain_points": [
            "Data management challenges",
            "Inefficient workflows",
            "Limited memory capacity",
        ],
        "goals": ["Improve productivity", "Scale operations", "Innovate faster"],
        "channels": ["LinkedIn", "Tech conferences", "Online forums"],
    }


@pytest.fixture
def sample_move() -> Dict[str, Any]:
    """Sample move data for testing."""
    return {
        "id": "move-123",
        "title": "Launch Memory System",
        "description": "Deploy comprehensive memory system",
        "goals": [
            "Complete implementation",
            "Achieve 99% uptime",
            "User adoption >80%",
        ],
        "strategy": "Phased rollout with continuous feedback",
        "execution_plan": [
            "Phase 1: Core functionality",
            "Phase 2: Advanced features",
            "Phase 3: Optimization",
        ],
        "success_metrics": [
            "System performance",
            "User satisfaction",
            "Business impact",
        ],
        "risks": ["Technical complexity", "User resistance", "Resource constraints"],
    }


@pytest.fixture
def sample_research() -> Dict[str, Any]:
    """Sample research data for testing."""
    return {
        "id": "research-123",
        "title": "Memory System Effectiveness Study",
        "summary": "Analysis of memory system performance",
        "key_findings": [
            "95% accuracy in semantic search",
            "2x faster information retrieval",
            "High user satisfaction",
        ],
        "insights": [
            "Vector embeddings significantly improve recall",
            "Graph relationships enhance context understanding",
            "Episodic memory aids decision making",
        ],
        "conclusions": [
            "Memory system meets performance goals",
            "Ready for production deployment",
            "Continued optimization recommended",
        ],
        "recommendations": [
            "Scale to more users",
            "Add advanced analytics",
            "Improve user interface",
        ],
        "methodology": "A/B testing with control group",
        "sources": ["Internal data", "User feedback", "Industry benchmarks"],
    }


@pytest.fixture
def sample_conversation() -> List[Dict[str, Any]]:
    """Sample conversation messages for testing."""
    return [
        {
            "role": "user",
            "content": "How does the memory system work?",
            "timestamp": "2024-01-01T10:00:00Z",
        },
        {
            "role": "assistant",
            "content": "The memory system uses vector embeddings, knowledge graphs, and episodic memory to store and retrieve information efficiently.",
            "timestamp": "2024-01-01T10:00:05Z",
        },
        {
            "role": "user",
            "content": "Can you show me an example of how to search for information?",
            "timestamp": "2024-01-01T10:00:10Z",
        },
        {
            "role": "assistant",
            "content": "Certainly! You can search using natural language queries like 'find information about our company mission' and the system will return relevant results.",
            "timestamp": "2024-01-01T10:00:15Z",
        },
    ]


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    client = MagicMock()
    client.table.return_value = client
    client.insert.return_value = client
    client.select.return_value = client
    client.update.return_value = client
    client.delete.return_value = client
    client.eq.return_value = client
    client.order.return_value = client
    client.limit.return_value = client
    client.execute.return_value = {"data": [], "error": None}
    return client


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing."""
    client = AsyncMock()
    client.get.return_value = None
    client.set.return_value = True
    client.delete.return_value = True
    client.exists.return_value = False
    client.hget.return_value = None
    client.hset.return_value = True
    client.hdel.return_value = True
    return client


@pytest.fixture
def sample_memory_chunk(test_workspace_id: str) -> MemoryChunk:
    """Sample memory chunk for testing."""
    return MemoryChunk(
        id="chunk-123",
        workspace_id=test_workspace_id,
        memory_type=MemoryType.FOUNDATION,
        content="Test company mission is to revolutionize memory systems",
        metadata={"section": "mission", "priority": 1.0},
        score=0.95,
    )


@pytest.fixture
def sample_graph_entity(test_workspace_id: str) -> GraphEntity:
    """Sample graph entity for testing."""
    return GraphEntity(
        id="entity-123",
        workspace_id=test_workspace_id,
        entity_type=EntityType.COMPANY,
        name="Test Company",
        properties={"industry": "Technology", "size": "Medium"},
    )


@pytest.fixture
def sample_graph_relationship(test_workspace_id: str) -> GraphRelationship:
    """Sample graph relationship for testing."""
    return GraphRelationship(
        id="rel-123",
        workspace_id=test_workspace_id,
        source_id="entity-123",
        target_id="entity-456",
        relation_type=RelationType.HAS_FEATURE,
        properties={"type": "core_feature"},
        weight=1.0,
    )


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_embedding_model():
    """Mock embedding model for testing."""
    model = AsyncMock()
    model.encode.return_value = [[0.1, 0.2, 0.3] * 128]  # 384-dimensional vector
    model.encode_single.return_value = [0.1, 0.2, 0.3] * 128
    return model


@pytest.fixture
def mock_memory_controller():
    """Mock memory controller for testing."""
    controller = AsyncMock()
    controller.store.return_value = MemoryChunk()
    controller.search.return_value = []
    controller.retrieve.return_value = None
    controller.update.return_value = MemoryChunk()
    controller.delete.return_value = True
    controller.get_stats.return_value = {
        "total_chunks": 0,
        "chunks_by_type": {},
        "storage_bytes": 0,
        "avg_age_days": 0.0,
    }
    return controller


@pytest.fixture
def mock_graph_memory():
    """Mock graph memory for testing."""
    memory = AsyncMock()
    memory.add_entity.return_value = "entity-123"
    memory.add_relationship.return_value = "rel-123"
    memory.get_entity.return_value = GraphEntity()
    memory.get_relationship.return_value = GraphRelationship()
    memory.find_entities.return_value = []
    memory.get_relationships.return_value = []
    memory.get_subgraph.return_value = MagicMock(entities=[], relationships=[])
    memory.delete_entity.return_value = True
    memory.delete_relationship.return_value = True
    return memory


@pytest.fixture
def mock_episodic_memory():
    """Mock episodic memory for testing."""
    memory = AsyncMock()
    memory.create_episode.return_value = "episode-123"
    memory.add_turn.return_value = "turn-123"
    memory.get_episode.return_value = MagicMock()
    memory.get_turn.return_value = MagicMock()
    memory.list_episodes.return_value = []
    memory.search_episodes.return_value = []
    memory.end_episode.return_value = True
    memory.delete_episode.return_value = True
    return memory


@pytest.fixture
def mock_working_memory():
    """Mock working memory for testing."""
    memory = AsyncMock()
    memory.create_session.return_value = "session-123"
    memory.get_session.return_value = MagicMock()
    memory.update_session.return_value = True
    memory.delete_session.return_value = True
    memory.list_sessions.return_value = []
    memory.add_to_context_window.return_value = True
    memory.get_context_window.return_value = []
    memory.write_to_scratch_pad.return_value = True
    memory.get_scratch_pad.return_value = {}
    return memory


# Helper functions for tests
def create_test_memory_chunk(
    workspace_id: str,
    memory_type: MemoryType,
    content: str,
    metadata: Dict[str, Any] = None,
) -> MemoryChunk:
    """Create a test memory chunk."""
    return MemoryChunk(
        workspace_id=workspace_id,
        memory_type=memory_type,
        content=content,
        metadata=metadata or {},
    )


def create_test_graph_entity(
    workspace_id: str,
    entity_type: EntityType,
    name: str,
    properties: Dict[str, Any] = None,
) -> GraphEntity:
    """Create a test graph entity."""
    return GraphEntity(
        workspace_id=workspace_id,
        entity_type=entity_type,
        name=name,
        properties=properties or {},
    )


def create_test_graph_relationship(
    workspace_id: str,
    source_id: str,
    target_id: str,
    relation_type: RelationType,
    properties: Dict[str, Any] = None,
) -> GraphRelationship:
    """Create a test graph relationship."""
    return GraphRelationship(
        workspace_id=workspace_id,
        source_id=source_id,
        target_id=target_id,
        relation_type=relation_type,
        properties=properties or {},
    )


# Async test helpers
async def async_create_test_chunks(count: int, workspace_id: str) -> List[MemoryChunk]:
    """Create multiple test memory chunks asynchronously."""
    chunks = []
    for i in range(count):
        chunk = create_test_memory_chunk(
            workspace_id=workspace_id,
            memory_type=MemoryType.FOUNDATION,
            content=f"Test content {i}",
            metadata={"index": i},
        )
        chunks.append(chunk)
    return chunks


async def async_wait_for_condition(
    condition_func, timeout: float = 5.0, interval: float = 0.1
) -> bool:
    """Wait for a condition to become true."""
    import time

    start_time = time.time()

    while time.time() - start_time < timeout:
        if await condition_func():
            return True
        await asyncio.sleep(interval)

    return False
