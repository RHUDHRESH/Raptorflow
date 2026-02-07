import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List
from uuid import uuid4

import pytest

from memory.cache import (
    CachedSwarmCoordinator,
    SwarmMemoryCache,
    create_cached_coordinator,
)
from memory.consolidated import (
    ConsolidatedMemory,
    MemoryFragment,
    SwarmMemoryConsolidator,
)
from memory.factories import (
    create_swarm_memory_consolidator,
    create_swarm_memory_coordinator,
    get_swarm_memory_coordinator,
)
from memory.swarm_coordinator import (
    SwarmMemoryCoordinator,
    hydrate_state_with_swarm_memory,
    record_agent_execution,
)
from models.cognitive import AgentMessage, CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.memory.tests")


class TestSwarmMemorySystem:
    """
    Comprehensive test suite for the swarm memory system.
    Tests consolidation, caching, and performance.
    """

    @pytest.fixture
    async def workspace_id(self):
        """Test workspace ID."""
        return f"test_workspace_{uuid4().hex[:8]}"

    @pytest.fixture
    async def consolidator(self, workspace_id):
        """Swarm memory consolidator fixture."""
        return create_swarm_memory_consolidator(workspace_id)

    @pytest.fixture
    async def coordinator(self, workspace_id):
        """Swarm memory coordinator fixture."""
        return create_swarm_memory_coordinator(workspace_id)

    @pytest.fixture
    async def cached_coordinator(self, workspace_id):
        """Cached coordinator fixture."""
        return create_cached_coordinator(workspace_id, cache_size_mb=10)

    @pytest.fixture
    async def sample_fragments(self):
        """Sample memory fragments for testing."""
        return [
            MemoryFragment(
                agent_id="researcher_1",
                agent_type="researcher",
                content="Market analysis shows growing trend in AI adoption",
                importance_score=0.8,
                workspace_id="test_workspace",
            ),
            MemoryFragment(
                agent_id="strategist_1",
                agent_type="strategist",
                content="Strategy pivot recommended based on competitive landscape",
                importance_score=0.9,
                workspace_id="test_workspace",
            ),
            MemoryFragment(
                agent_id="creative_1",
                agent_type="creative",
                content="New creative concept developed for Q1 campaign",
                importance_score=0.7,
                workspace_id="test_workspace",
            ),
        ]

    async def test_memory_fragment_creation(self):
        """Test memory fragment creation and properties."""
        fragment = MemoryFragment(
            agent_id="test_agent",
            agent_type="researcher",
            content="Test memory content",
            importance_score=0.8,
            workspace_id="test_workspace",
        )

        assert fragment.agent_id == "test_agent"
        assert fragment.agent_type == "researcher"
        assert fragment.importance_score == 0.8
        assert fragment.memory_tier == "L1"
        assert fragment.access_count == 0
        assert isinstance(fragment.id, str)

    async def test_consolidator_initialization(self, workspace_id):
        """Test consolidator initialization."""
        consolidator = create_swarm_memory_consolidator(workspace_id)

        assert consolidator.workspace_id == workspace_id
        assert consolidator.consolidated_memory.workspace_id == workspace_id
        assert len(consolidator.consolidated_memory.fragments) == 0
        assert consolidator._fragment_cache == {}
        assert consolidator._search_cache == {}

    async def test_agent_memory_recording(self, coordinator, sample_fragments):
        """Test recording agent memories."""
        # Initialize agent
        success = await coordinator.initialize_agent_memory(
            "researcher_1", "researcher"
        )
        assert success is True
        assert "researcher_1" in coordinator.active_agents

        # Record memories
        for fragment in sample_fragments:
            success = await coordinator.record_agent_memory(
                agent_id=fragment.agent_id,
                content=fragment.content,
                metadata={"test": True},
                importance=fragment.importance_score,
            )
            assert success is True

        # Check agent usage tracking
        usage = coordinator.agent_memory_usage["researcher_1"]
        assert usage["fragments"] >= 1

    async def test_memory_consolidation(self, consolidator, sample_fragments):
        """Test memory consolidation process."""
        # Add fragments to consolidator (simulating gathered fragments)
        consolidator.consolidated_memory.fragments.extend(sample_fragments)

        # Perform consolidation
        result = await consolidator.consolidate_agent_memories(force_consolidation=True)

        assert isinstance(result, ConsolidatedMemory)
        assert len(result.fragments) >= len(sample_fragments)
        assert (
            result.last_consolidation
            > consolidator.consolidated_memory.last_consolidation - timedelta(seconds=1)
        )

    async def test_memory_search(self, coordinator, sample_fragments):
        """Test memory search functionality."""
        # Record sample memories
        for fragment in sample_fragments:
            await coordinator.record_agent_memory(
                agent_id=fragment.agent_id,
                content=fragment.content,
                importance=fragment.importance_score,
            )

        # Test search
        results = await coordinator.search_swarm_memory(
            query="market analysis", limit=5
        )

        assert isinstance(results, list)
        # Results may be empty since embeddings aren't fully mocked in this test

    async def test_agent_context_retrieval(self, coordinator, sample_fragments):
        """Test agent context retrieval."""
        # Initialize agent and record memories
        await coordinator.initialize_agent_memory("researcher_1", "researcher")

        for fragment in sample_fragments:
            if fragment.agent_id == "researcher_1":
                await coordinator.record_agent_memory(
                    agent_id=fragment.agent_id,
                    content=fragment.content,
                    importance=fragment.importance_score,
                )

        # Get agent context
        context = await coordinator.get_agent_context(
            agent_id="researcher_1", query="market analysis"
        )

        assert context["agent_id"] == "researcher_1"
        assert "personal_memory" in context
        assert "relevant_swarm_memory" in context
        assert "cross_agent_insights" in context

    async def test_cache_performance(self):
        """Test cache performance and tier management."""
        cache = SwarmMemoryCache(max_memory_mb=1, max_entries=100)

        # Test set/get operations
        await cache.set("key1", "value1", ttl=60)
        value = await cache.get("key1")
        assert value == "value1"

        # Test cache miss
        value = await cache.get("nonexistent")
        assert value is None

        # Test cache statistics
        stats = await cache.get_cache_stats()
        assert stats["total_entries"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1

        await cache.cleanup()

    async def test_cached_coordinator(self, cached_coordinator):
        """Test cached coordinator functionality."""
        # Initialize agent
        await cached_coordinator.coordinator.initialize_agent_memory(
            "test_agent", "researcher"
        )

        # Record memory
        success = await cached_coordinator.record_agent_memory(
            agent_id="test_agent", content="Test memory content", importance=0.8
        )
        assert success is True

        # Search (should cache result)
        results1 = await cached_coordinator.search_swarm_memory(
            query="test content", use_cache=True
        )

        # Search again (should hit cache)
        results2 = await cached_coordinator.search_swarm_memory(
            query="test content", use_cache=True
        )

        assert results1 == results2

        # Check cache stats
        stats = await cached_coordinator.cache.get_cache_stats()
        assert stats["hits"] >= 1

    async def test_state_hydration(self):
        """Test state hydration with swarm memory."""
        state = CognitiveIntelligenceState(
            tenant_id="test_tenant",
            workspace_id="test_workspace",
            raw_prompt="Analyze market trends",
            messages=[],
        )

        # Hydrate state
        hydrated_state = await hydrate_state_with_swarm_memory(state)

        assert "swarm_memory_context" in hydrated_state
        assert hydrated_state["workspace_id"] == "test_workspace"

    async def test_performance_benchmarks(self, coordinator):
        """Test performance benchmarks for memory operations."""
        # Initialize test agents
        agents = ["agent_1", "agent_2", "agent_3"]
        for i, agent_id in enumerate(agents):
            await coordinator.initialize_agent_memory(agent_id, f"agent_type_{i}")

        # Benchmark memory recording
        start_time = time.time()
        for i in range(100):
            await coordinator.record_agent_memory(
                agent_id=agents[i % len(agents)],
                content=f"Test memory {i}",
                importance=0.5 + (i % 3) * 0.1,
            )
        record_time = time.time() - start_time

        # Benchmark search
        start_time = time.time()
        for i in range(50):
            await coordinator.search_swarm_memory(
                query=f"test memory {i % 10}", limit=5
            )
        search_time = time.time() - start_time

        # Performance assertions (adjust thresholds based on environment)
        assert record_time < 5.0  # Should record 100 memories in < 5 seconds
        assert search_time < 3.0  # Should perform 50 searches in < 3 seconds

        logger.info(
            f"Performance: Record={record_time:.2f}s, Search={search_time:.2f}s"
        )

    async def test_consolidation_workflow(self, workspace_id):
        """Test end-to-end consolidation workflow."""
        # Setup
        coordinator = get_swarm_memory_coordinator(workspace_id)

        # Initialize agents
        agents = [
            ("researcher_1", "researcher"),
            ("strategist_1", "strategist"),
            ("creative_1", "creative"),
        ]

        for agent_id, agent_type in agents:
            await coordinator.initialize_agent_memory(agent_id, agent_type)

        # Record diverse memories
        memories = [
            ("researcher_1", "Market research shows 25% growth in AI tools", 0.8),
            ("strategist_1", "Strategic pivot to AI-first approach recommended", 0.9),
            ("creative_1", "New campaign concept: AI-powered creativity", 0.7),
            ("researcher_1", "Competitor analysis reveals gap in market", 0.8),
            ("strategist_1", "Q1 strategy aligned with research findings", 0.7),
        ]

        for agent_id, content, importance in memories:
            await coordinator.record_agent_memory(
                agent_id=agent_id,
                content=content,
                importance=importance,
                metadata={"timestamp": datetime.now().isoformat()},
            )

        # Perform consolidation
        consolidation_result = await coordinator.consolidate_swarm_memories(force=True)

        assert consolidation_result["fragments_consolidated"] >= len(memories)
        assert consolidation_result["agents_involved"] == len(agents)
        assert "duration_seconds" in consolidation_result

        # Test consolidated search
        results = await coordinator.search_swarm_memory(
            query="AI strategy market", limit=10
        )

        assert isinstance(results, list)

        # Get memory statistics
        stats = await coordinator.get_swarm_memory_metrics()

        assert stats["workspace_id"] == workspace_id
        assert stats["active_agents"] == len(agents)
        assert stats["total_consolidations"] >= 1

        logger.info(f"Consolidation workflow completed: {consolidation_result}")

    async def test_cache_memory_management(self):
        """Test cache memory management and eviction."""
        cache = SwarmMemoryCache(max_memory_mb=1, max_entries=10)

        # Fill cache beyond capacity
        large_values = []
        for i in range(15):
            # Create values that will exceed cache capacity
            large_value = "x" * 1000  # 1KB per value
            large_values.append(large_value)
            await cache.set(f"key_{i}", large_value, ttl=300)

        # Check that cache evicted old entries
        stats = await cache.get_cache_stats()
        assert stats["total_entries"] <= cache.max_entries
        assert stats["memory_usage_bytes"] <= cache.max_memory_bytes
        assert stats["evictions"] > 0

        # Test LRU behavior
        await cache.set("important_key", "important_value", ttl=300)

        # Access important key frequently
        for _ in range(10):
            value = await cache.get("important_key")
            assert value == "important_value"

        # Fill cache again
        for i in range(15):
            await cache.set(f"new_key_{i}", f"value_{i}", ttl=300)

        # Important key should still be in cache due to frequent access
        value = await cache.get("important_key")
        assert value == "important_value"

        await cache.cleanup()

    async def test_error_handling(self, coordinator):
        """Test error handling in memory operations."""
        # Test invalid agent initialization
        success = await coordinator.initialize_agent_memory("", "")
        assert success is True  # Should still succeed but log warning

        # Test memory recording with invalid data
        success = await coordinator.record_agent_memory(
            agent_id="nonexistent_agent", content=None, importance=0.5
        )
        # Should handle gracefully
        assert isinstance(success, bool)

        # Test search with empty query
        results = await coordinator.search_swarm_memory(query="", limit=5)
        assert isinstance(results, list)

        # Test context for nonexistent agent
        context = await coordinator.get_agent_context(agent_id="nonexistent_agent")
        assert context["agent_id"] == "nonexistent_agent"
        assert "error" not in context  # Should handle gracefully


# Performance test utilities
async def run_performance_tests():
    """Run performance tests for the memory system."""
    workspace_id = f"perf_test_{uuid4().hex[:8]}"
    coordinator = get_swarm_memory_coordinator(workspace_id)

    print("Starting performance tests...")

    # Test 1: Memory recording performance
    print("Test 1: Memory recording performance...")
    start_time = time.time()

    # Initialize agents
    for i in range(10):
        await coordinator.initialize_agent_memory(f"agent_{i}", "test_agent")

    # Record memories
    for i in range(1000):
        await coordinator.record_agent_memory(
            agent_id=f"agent_{i % 10}",
            content=f"Performance test memory {i}",
            importance=0.5 + (i % 5) * 0.1,
        )

    record_time = time.time() - start_time
    print(f"  Recorded 1000 memories in {record_time:.2f} seconds")
    print(f"  Average: {1000/record_time:.2f} memories/second")

    # Test 2: Search performance
    print("Test 2: Search performance...")
    start_time = time.time()

    for i in range(100):
        await coordinator.search_swarm_memory(
            query=f"performance test {i % 10}", limit=10
        )

    search_time = time.time() - start_time
    print(f"  Performed 100 searches in {search_time:.2f} seconds")
    print(f"  Average: {100/search_time:.2f} searches/second")

    # Test 3: Consolidation performance
    print("Test 3: Consolidation performance...")
    start_time = time.time()

    consolidation_result = await coordinator.consolidate_swarm_memories(force=True)

    consolidation_time = time.time() - start_time
    print(f"  Consolidation completed in {consolidation_time:.2f} seconds")
    print(f"  Processed {consolidation_result['fragments_consolidated']} fragments")

    # Test 4: Cache performance
    print("Test 4: Cache performance...")
    cached_coordinator = create_cached_coordinator(coordinator, cache_size_mb=20)

    start_time = time.time()

    # First pass (cache misses)
    for i in range(50):
        await cached_coordinator.search_swarm_memory(
            query=f"cached search {i % 5}", use_cache=True
        )

    first_pass_time = time.time() - start_time

    # Second pass (cache hits)
    start_time = time.time()
    for i in range(50):
        await cached_coordinator.search_swarm_memory(
            query=f"cached search {i % 5}", use_cache=True
        )

    second_pass_time = time.time() - start_time

    print(f"  First pass (cache misses): {first_pass_time:.2f} seconds")
    print(f"  Second pass (cache hits): {second_pass_time:.2f} seconds")
    print(f"  Cache speedup: {first_pass_time/second_pass_time:.2f}x")

    # Final statistics
    stats = await coordinator.get_swarm_memory_metrics()
    cache_stats = await cached_coordinator.cache.get_cache_stats()

    print("\nFinal Statistics:")
    print(f"  Total fragments: {stats['total_fragments']}")
    print(f"  Active agents: {stats['active_agents']}")
    print(f"  Cache hit rate: {cache_stats['hit_rate']:.2%}")
    print(f"  Memory usage: {cache_stats['memory_usage_mb']:.2f} MB")

    print("\nPerformance tests completed!")


if __name__ == "__main__":
    # Run performance tests
    asyncio.run(run_performance_tests())
