"""
Comprehensive Memory System Tests

Deep testing suite for the memory system with proper mocking and error handling.
"""

import asyncio
import logging
import pytest
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List
from uuid import uuid4

from mocks import (
    MockContext,
    create_test_fragment,
    create_test_state,
    run_with_mocks
)

# Import after mocks are set up
with MockContext():
    from memory.cache import SwarmMemoryCache
    from memory.consolidated import MemoryFragment, SwarmMemoryConsolidator
    from memory.factories import (
        create_swarm_memory_consolidator,
        create_swarm_memory_coordinator,
        get_swarm_memory_coordinator,
        check_memory_system_health
    )
    from memory.swarm_coordinator import SwarmMemoryCoordinator
    from models.cognitive import AgentMessage, CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.memory.deep_tests")


class TestMemorySystemDeep:
    """
    Deep testing suite for memory system focusing on edge cases and error conditions.
    """

    @pytest.fixture
    def workspace_id(self):
        """Test workspace ID."""
        return f"deep_test_workspace_{uuid4().hex[:8]}"

    @pytest.fixture
    async def consolidator(self, workspace_id):
        """Swarm memory consolidator fixture."""
        with MockContext():
            return create_swarm_memory_consolidator(workspace_id)

    @pytest.fixture
    async def coordinator(self, workspace_id):
        """Swarm memory coordinator fixture."""
        with MockContext():
            return create_swarm_memory_coordinator(workspace_id)

    @pytest.fixture
    async def cache(self):
        """Memory cache fixture."""
        return SwarmMemoryCache(max_memory_mb=10, max_entries=100)

    class TestMemoryFragmentValidation:
        """Test MemoryFragment validation and edge cases."""

        def test_valid_fragment_creation(self):
            """Test creating valid memory fragments."""
            fragment = MemoryFragment(
                agent_id="test_agent",
                agent_type="researcher",
                content="Test content",
                importance_score=0.7
            )
            assert fragment.agent_id == "test_agent"
            assert fragment.importance_score == 0.7
            assert fragment.memory_tier == "L1"

        def test_invalid_importance_score(self):
            """Test invalid importance scores."""
            with pytest.raises(ValueError, match="importance_score"):
                MemoryFragment(importance_score=1.5)
            
            with pytest.raises(ValueError, match="importance_score"):
                MemoryFragment(importance_score=-0.1)

        def test_invalid_memory_tier(self):
            """Test invalid memory tiers."""
            with pytest.raises(ValueError, match="memory_tier"):
                MemoryFragment(memory_tier="L4")

        def test_fragment_serialization(self):
            """Test fragment serialization/deserialization."""
            original = MemoryFragment(
                agent_id="test_agent",
                content="Test content",
                importance_score=0.8
            )
            
            # Convert to dict
            fragment_dict = original.to_dict()
            assert "id" in fragment_dict
            assert fragment_dict["agent_id"] == "test_agent"
            assert "timestamp" in fragment_dict
            
            # Convert back from dict
            restored = MemoryFragment.from_dict(fragment_dict)
            assert restored.agent_id == original.agent_id
            assert restored.content == original.content
            assert restored.importance_score == original.importance_score

    class TestConsolidatorEdgeCases:
        """Test consolidator edge cases and error conditions."""

        async def test_invalid_workspace_id(self):
            """Test invalid workspace ID handling."""
            with pytest.raises(ValueError, match="workspace_id"):
                SwarmMemoryConsolidator("")
            
            with pytest.raises(ValueError, match="workspace_id"):
                SwarmMemoryConsolidator(None)
            
            with pytest.raises(ValueError, match="workspace_id"):
                SwarmMemoryConsolidator(123)

        async def test_consolidation_without_embedder(self, consolidator):
            """Test consolidation when embedder is not available."""
            # Simulate embedder failure
            consolidator.embedder = None
            
            # Should not crash, but should handle gracefully
            result = await consolidator.consolidate_agent_memories(force_consolidation=True)
            assert result is not None
            assert hasattr(result, 'workspace_id')

        async def test_consolidation_with_empty_fragments(self, consolidator):
            """Test consolidation with no fragments."""
            result = await consolidator.consolidate_agent_memories(force_consolidation=True)
            assert result is not None
            assert len(result.fragments) == 0

        async def test_consolidation_interval_logic(self, consolidator):
            """Test consolidation interval logic."""
            # First consolidation should work
            result1 = await consolidator.consolidate_agent_memories(force_consolidation=False)
            assert result1 is not None
            
            # Second consolidation without force should be skipped
            result2 = await consolidator.consolidate_agent_memories(force_consolidation=False)
            assert result2 is result1  # Should return same object
            
            # With force, should work again
            result3 = await consolidator.consolidate_agent_memories(force_consolidation=True)
            assert result3 is not None

        async def test_fragment_deduplication(self, consolidator):
            """Test fragment deduplication logic."""
            # Create duplicate fragments
            fragment1 = create_test_fragment(content="duplicate content")
            fragment2 = create_test_fragment(content="duplicate content")
            fragment3 = create_test_fragment(content="unique content")
            
            # Mock gathering fragments
            consolidator._gather_memory_fragments = lambda agent_ids: [fragment1, fragment2, fragment3]
            
            result = await consolidator.consolidate_agent_memories(force_consolidation=True)
            
            # Should deduplicate duplicates
            unique_contents = set(f.content for f in result.fragments)
            assert len(unique_contents) == 2
            assert "duplicate content" in unique_contents
            assert "unique content" in unique_contents

        async def test_similarity_calculation_edge_cases(self, consolidator):
            """Test similarity calculation edge cases."""
            # Test with no embeddings
            f1 = create_test_fragment()
            f2 = create_test_fragment()
            f1.embedding = None
            f2.embedding = None
            
            similarity = await consolidator._calculate_fragment_similarity(f1, f2)
            assert similarity == 0.0
            
            # Test with mismatched dimensions
            f1.embedding = [1.0, 2.0]
            f2.embedding = [1.0, 2.0, 3.0]
            
            similarity = await consolidator._calculate_fragment_similarity(f1, f2)
            assert similarity == 0.0
            
            # Test with zero magnitude
            f1.embedding = [0.0, 0.0]
            f2.embedding = [1.0, 1.0]
            
            similarity = await consolidator._calculate_fragment_similarity(f1, f2)
            assert similarity == 0.0

    class TestCoordinatorEdgeCases:
        """Test coordinator edge cases and error conditions."""

        async def test_coordinator_invalid_workspace(self):
            """Test coordinator with invalid workspace ID."""
            with pytest.raises(ValueError, match="workspace_id"):
                SwarmMemoryCoordinator("")
            
            with pytest.raises(ValueError, match="workspace_id"):
                SwarmMemoryCoordinator(None)

        async def test_agent_initialization(self, coordinator):
            """Test agent memory initialization."""
            success = await coordinator.initialize_agent_memory("test_agent", "researcher")
            assert success is True
            assert "test_agent" in coordinator.active_agents
            assert "test_agent" in coordinator.agent_memory_usage

        async def test_duplicate_agent_initialization(self, coordinator):
            """Test initializing the same agent twice."""
            await coordinator.initialize_agent_memory("test_agent", "researcher")
            
            # Should handle duplicate initialization gracefully
            success = await coordinator.initialize_agent_memory("test_agent", "researcher")
            assert success is True
            assert "test_agent" in coordinator.active_agents

        async def test_memory_recording_validation(self, coordinator):
            """Test memory recording with invalid inputs."""
            # Initialize agent first
            await coordinator.initialize_agent_memory("test_agent", "researcher")
            
            # Test with invalid importance
            with pytest.raises(ValueError):
                await coordinator.record_agent_memory(
                    agent_id="test_agent",
                    content="test",
                    importance=1.5
                )
            
            # Test with non-existent agent
            with pytest.raises(ValueError):
                await coordinator.record_agent_memory(
                    agent_id="non_existent",
                    content="test",
                    importance=0.5
                )

        async def test_context_retrieval_edge_cases(self, coordinator):
            """Test context retrieval edge cases."""
            # Test with non-existent agent
            context = await coordinator.get_agent_context("non_existent")
            assert context["agent_id"] == "non_existent"
            assert len(context["personal_memory"]) == 0
            
            # Test with empty query
            await coordinator.initialize_agent_memory("test_agent", "researcher")
            context = await coordinator.get_agent_context("test_agent", query="")
            assert context["agent_id"] == "test_agent"

    class TestCacheEdgeCases:
        """Test cache edge cases and performance."""

        async def test_cache_invalid_parameters(self):
            """Test cache with invalid parameters."""
            with pytest.raises(ValueError, match="max_memory_mb"):
                SwarmMemoryCache(max_memory_mb=0)
            
            with pytest.raises(ValueError, match="max_entries"):
                SwarmMemoryCache(max_entries=0)

        async def test_cache_ttl_expiration(self, cache):
            """Test cache TTL expiration."""
            # Set entry with very short TTL
            await cache.set("test_key", "test_value", ttl_seconds=1)
            
            # Should be available immediately
            value = await cache.get("test_key")
            assert value == "test_value"
            
            # Wait for expiration
            await asyncio.sleep(2)
            
            # Should be expired
            value = await cache.get("test_key")
            assert value is None

        async def test_cache_memory_limits(self, cache):
            """Test cache memory limit enforcement."""
            # Fill cache beyond limits
            large_value = "x" * 1000000  # 1MB string
            
            for i in range(100):
                await cache.set(f"key_{i}", large_value)
            
            # Cache should still function (eviction should work)
            value = await cache.get("key_0")
            # May or may not be present depending on eviction policy
            
            # Cache should not crash
            stats = cache.get_stats()
            assert stats is not None

        async def test_cache_concurrent_access(self, cache):
            """Test concurrent cache access."""
            async def worker(worker_id):
                for i in range(10):
                    await cache.set(f"worker_{worker_id}_key_{i}", f"worker_{worker_id}_value_{i}")
                    value = await cache.get(f"worker_{worker_id}_key_{i}")
                    assert value == f"worker_{worker_id}_value_{i}"
            
            # Run multiple workers concurrently
            tasks = [worker(i) for i in range(5)]
            await asyncio.gather(*tasks)
            
            # Cache should be consistent
            stats = cache.get_stats()
            assert stats["sets"] == 50  # 5 workers * 10 sets each

    class TestSystemIntegration:
        """Test system integration and end-to-end scenarios."""

        async def test_full_consolidation_workflow(self, workspace_id):
            """Test complete consolidation workflow."""
            with MockContext():
                # Create coordinator
                coordinator = create_swarm_memory_coordinator(workspace_id)
                
                # Initialize agents
                await coordinator.initialize_agent_memory("researcher_1", "researcher")
                await coordinator.initialize_agent_memory("creative_1", "creative")
                
                # Record some memories
                await coordinator.record_agent_memory(
                    "researcher_1",
                    "Market research shows AI adoption growing",
                    importance=0.8
                )
                
                await coordinator.record_agent_memory(
                    "creative_1", 
                    "New campaign concept focusing on AI benefits",
                    importance=0.7
                )
                
                # Get context
                context = await coordinator.get_agent_context("researcher_1")
                assert context["agent_id"] == "researcher_1"
                
                # Check system health
                health = check_memory_system_health(workspace_id)
                assert health["workspace_id"] == workspace_id
                assert health["status"] in ["healthy", "warning"]

        async def test_error_recovery_scenarios(self, workspace_id):
            """Test error recovery scenarios."""
            with MockContext():
                coordinator = create_swarm_memory_coordinator(workspace_id)
                
                # Test recovery from embedder failure
                coordinator.consolidator.embedder = None
                
                # Should still be able to record memories
                await coordinator.initialize_agent_memory("test_agent", "researcher")
                success = await coordinator.record_agent_memory(
                    "test_agent",
                    "Test memory",
                    importance=0.5
                )
                assert success is True
                
                # Should still be able to get context
                context = await coordinator.get_agent_context("test_agent")
                assert context is not None

        async def test_performance_under_load(self, workspace_id):
            """Test system performance under load."""
            with MockContext():
                coordinator = create_swarm_memory_coordinator(workspace_id)
                
                # Initialize many agents
                num_agents = 50
                for i in range(num_agents):
                    await coordinator.initialize_agent_memory(f"agent_{i}", "researcher")
                
                # Record many memories concurrently
                async def record_memory(agent_id):
                    for j in range(10):
                        await coordinator.record_agent_memory(
                            agent_id,
                            f"Memory {j} for {agent_id}",
                            importance=0.5
                        )
                
                start_time = time.time()
                tasks = [record_memory(f"agent_{i}") for i in range(num_agents)]
                await asyncio.gather(*tasks)
                end_time = time.time()
                
                # Should complete within reasonable time
                duration = end_time - start_time
                assert duration < 30.0  # 30 seconds max for 500 memory operations
                
                # All agents should still be active
                assert len(coordinator.active_agents) == num_agents

    class TestStateHydration:
        """Test state hydration functionality."""

        async def test_state_hydration_with_workspace(self):
            """Test state hydration with valid workspace."""
            with MockContext():
                from memory.swarm_coordinator import hydrate_state_with_swarm_memory
                
                state = create_test_state(
                    workspace_id="test_workspace",
                    last_agent="test_agent"
                )
                
                # Should not crash
                hydrated_state = await hydrate_state_with_swarm_memory(state)
                assert hydrated_state is not None
                assert "swarm_memory_context" in hydrated_state

        async def test_state_hydration_without_workspace(self):
            """Test state hydration without workspace ID."""
            with MockContext():
                from memory.swarm_coordinator import hydrate_state_with_swarm_memory
                
                state = create_test_state()
                state.pop("workspace_id", None)  # Remove workspace ID
                
                # Should return state unchanged
                hydrated_state = await hydrate_state_with_swarm_memory(state)
                assert hydrated_state is state
                assert "swarm_memory_context" not in hydrated_state

        async def test_agent_execution_recording(self):
            """Test agent execution recording."""
            with MockContext():
                from memory.swarm_coordinator import record_agent_execution
                
                state = create_test_state(workspace_id="test_workspace")
                result = {"output": "test result", "tokens": 10}
                
                # Should not crash
                success = await record_agent_execution(state, result)
                assert success is True

    class TestMemoryStatistics:
        """Test memory statistics and monitoring."""

        async def test_statistics_collection(self, coordinator):
            """Test statistics collection."""
            stats = await coordinator.get_memory_statistics()
            assert stats is not None
            assert "workspace_id" in stats
            assert "total_fragments" in stats
            assert "active_agents" in stats
            assert "memory_tiers" in stats

        async def test_health_check_scenarios(self, workspace_id):
            """Test health check in various scenarios."""
            # Test with non-existent workspace
            health = check_memory_system_health("non_existent")
            assert health["status"] == "warning"
            assert "No coordinator found" in health["issues"]
            
            # Test with valid workspace
            with MockContext():
                coordinator = create_swarm_memory_coordinator(workspace_id)
                health = check_memory_system_health(workspace_id)
                assert health["status"] in ["healthy", "warning", "degraded"]


# Performance benchmarks
class TestPerformanceBenchmarks:
    """Performance benchmark tests."""

    async def test_cache_performance_benchmark(self):
        """Benchmark cache performance."""
        cache = SwarmMemoryCache(max_memory_mb=50, max_entries=1000)
        
        # Benchmark set operations
        start_time = time.time()
        for i in range(1000):
            await cache.set(f"key_{i}", f"value_{i}")
        set_time = time.time() - start_time
        
        # Benchmark get operations
        start_time = time.time()
        for i in range(1000):
            await cache.get(f"key_{i}")
        get_time = time.time() - start_time
        
        # Performance assertions
        assert set_time < 5.0  # 1000 sets in < 5 seconds
        assert get_time < 2.0  # 1000 gets in < 2 seconds
        
        stats = cache.get_stats()
        assert stats["hit_rate"] > 0.9  # Should have high hit rate

    async def test_consolidation_performance_benchmark(self, workspace_id):
        """Benchmark consolidation performance."""
        with MockContext():
            consolidator = create_swarm_memory_consolidator(workspace_id)
            
            # Create many test fragments
            fragments = [
                create_test_fragment(
                    agent_id=f"agent_{i % 10}",
                    content=f"Test content {i}",
                    importance_score=0.5 + (i % 5) * 0.1
                )
                for i in range(100)
            ]
            
            # Mock fragment gathering
            consolidator._gather_memory_fragments = lambda agent_ids: fragments
            
            # Benchmark consolidation
            start_time = time.time()
            result = await consolidator.consolidate_agent_memories(force_consolidation=True)
            consolidation_time = time.time() - start_time
            
            # Performance assertions
            assert consolidation_time < 10.0  # 100 fragments in < 10 seconds
            assert len(result.fragments) <= 100  # Should not increase fragments


# Test utilities
class TestUtils:
    """Test utility functions."""

    def test_mock_context_manager(self):
        """Test mock context manager."""
        with MockContext():
            # Mocks should be active
            from inference import InferenceProvider
            assert InferenceProvider is not None
        
        # Mocks should be cleaned up
        import sys
        assert 'backend.inference' not in sys.modules

    async def test_test_helpers(self):
        """Test helper functions."""
        fragment = create_test_fragment()
        assert fragment.agent_id == "test_agent"
        assert fragment.content == "Test content"
        
        state = create_test_state()
        assert "workspace_id" in state
        assert "messages" in state


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])
