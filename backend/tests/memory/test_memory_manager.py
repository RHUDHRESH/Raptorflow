"""
Unit tests for MemoryManager.

Tests verify that:
1. MemoryManager stores and retrieves memories correctly
2. Search filters work as expected
3. User preferences are extracted from feedback
4. Performance history tracking works
5. Feedback can be added to existing memories
"""

import pytest
from datetime import datetime
from typing import Any, Dict

from backend.memory.manager import MemoryManager, MemoryEntry


class TestMemoryEntry:
    """Test suite for MemoryEntry class."""

    def test_memory_entry_creation(self):
        """Test creating a MemoryEntry."""
        entry = MemoryEntry(
            agent_name="TestAgent",
            task_type="test_task",
            input_summary="Test input",
            output_summary="Test output",
            result={"status": "success"},
            metadata={"key": "value"},
            performance_metrics={"latency": 100}
        )

        assert entry.agent_name == "TestAgent"
        assert entry.task_type == "test_task"
        assert entry.input_summary == "Test input"
        assert entry.output_summary == "Test output"
        assert entry.result == {"status": "success"}
        assert entry.metadata == {"key": "value"}
        assert entry.performance_metrics == {"latency": 100}
        assert entry.memory_id is not None
        assert entry.timestamp is not None

    def test_memory_entry_to_dict(self):
        """Test converting MemoryEntry to dictionary."""
        entry = MemoryEntry(
            agent_name="TestAgent",
            task_type="test_task",
            input_summary="Test input",
            output_summary="Test output",
            result={"status": "success"}
        )

        entry_dict = entry.to_dict()

        assert entry_dict["agent_name"] == "TestAgent"
        assert entry_dict["task_type"] == "test_task"
        assert "memory_id" in entry_dict
        assert "timestamp" in entry_dict
        assert isinstance(entry_dict["timestamp"], str)  # Should be ISO format

    def test_memory_entry_from_dict(self):
        """Test creating MemoryEntry from dictionary."""
        data = {
            "memory_id": "mem_123",
            "agent_name": "TestAgent",
            "task_type": "test_task",
            "input_summary": "Test input",
            "output_summary": "Test output",
            "result": {"status": "success"},
            "metadata": {"key": "value"},
            "performance_metrics": {"latency": 100},
            "user_feedback": {"rating": 5},
            "timestamp": "2025-01-01T12:00:00",
            "correlation_id": "corr_123"
        }

        entry = MemoryEntry.from_dict(data)

        assert entry.memory_id == "mem_123"
        assert entry.agent_name == "TestAgent"
        assert entry.task_type == "test_task"
        assert entry.user_feedback == {"rating": 5}
        assert entry.correlation_id == "corr_123"
        assert isinstance(entry.timestamp, datetime)


class TestMemoryManager:
    """Test suite for MemoryManager class."""

    @pytest.fixture
    def memory_manager(self):
        """Create a MemoryManager instance for testing."""
        return MemoryManager(workspace_id="test_ws", user_id="test_user")

    @pytest.mark.asyncio
    async def test_remember_stores_memory(self, memory_manager):
        """Test that remember() stores a memory entry."""
        memory_id = await memory_manager.remember(
            agent_name="TestAgent",
            task_type="test_task",
            input_summary="Test input",
            output_summary="Test output",
            result={"status": "success"},
            performance_metrics={"latency": 100},
            metadata={"custom_key": "custom_value"}
        )

        assert memory_id is not None
        assert isinstance(memory_id, str)

        # Verify memory was stored
        assert len(memory_manager._memory_store) == 1
        stored_memory = memory_manager._memory_store[0]
        assert stored_memory.memory_id == memory_id
        assert stored_memory.agent_name == "TestAgent"

    @pytest.mark.asyncio
    async def test_search_returns_memories(self, memory_manager):
        """Test that search() returns stored memories."""
        # Store some memories
        await memory_manager.remember(
            agent_name="TestAgent",
            task_type="test_task",
            input_summary="Build ICP for SaaS company",
            output_summary="Created executive persona",
            result={"icp_name": "SaaS Executive"}
        )

        await memory_manager.remember(
            agent_name="TestAgent",
            task_type="test_task",
            input_summary="Build ICP for ecommerce company",
            output_summary="Created retail persona",
            result={"icp_name": "Retail Manager"}
        )

        # Search for memories
        memories = await memory_manager.search(
            query="Build ICP for SaaS",
            agent_name="TestAgent",
            limit=5
        )

        assert len(memories) == 2  # Should return all memories (no semantic search in MVP)

    @pytest.mark.asyncio
    async def test_search_filters_by_agent_name(self, memory_manager):
        """Test that search() filters by agent name."""
        # Store memories from different agents
        await memory_manager.remember(
            agent_name="Agent1",
            task_type="task1",
            input_summary="Input 1",
            output_summary="Output 1",
            result={"status": "success"}
        )

        await memory_manager.remember(
            agent_name="Agent2",
            task_type="task1",
            input_summary="Input 2",
            output_summary="Output 2",
            result={"status": "success"}
        )

        # Search for Agent1 memories only
        memories = await memory_manager.search(
            query="task",
            agent_name="Agent1",
            limit=10
        )

        assert len(memories) == 1
        assert memories[0].agent_name == "Agent1"

    @pytest.mark.asyncio
    async def test_search_filters_by_task_type(self, memory_manager):
        """Test that search() filters by task type."""
        # Store memories with different task types
        await memory_manager.remember(
            agent_name="TestAgent",
            task_type="icp_building",
            input_summary="Build ICP",
            output_summary="Created ICP",
            result={"status": "success"}
        )

        await memory_manager.remember(
            agent_name="TestAgent",
            task_type="content_generation",
            input_summary="Generate blog",
            output_summary="Created blog",
            result={"status": "success"}
        )

        # Search for only icp_building tasks
        memories = await memory_manager.search(
            query="task",
            agent_name="TestAgent",
            task_type="icp_building",
            limit=10
        )

        assert len(memories) == 1
        assert memories[0].task_type == "icp_building"

    @pytest.mark.asyncio
    async def test_search_respects_limit(self, memory_manager):
        """Test that search() respects the limit parameter."""
        # Store 10 memories
        for i in range(10):
            await memory_manager.remember(
                agent_name="TestAgent",
                task_type="test_task",
                input_summary=f"Input {i}",
                output_summary=f"Output {i}",
                result={"index": i}
            )

        # Search with limit=3
        memories = await memory_manager.search(
            query="task",
            agent_name="TestAgent",
            limit=3
        )

        assert len(memories) == 3

    @pytest.mark.asyncio
    async def test_search_returns_most_recent_first(self, memory_manager):
        """Test that search() returns most recent memories first."""
        # Store memories with different timestamps
        id1 = await memory_manager.remember(
            agent_name="TestAgent",
            task_type="test_task",
            input_summary="First",
            output_summary="First output",
            result={"order": 1}
        )

        id2 = await memory_manager.remember(
            agent_name="TestAgent",
            task_type="test_task",
            input_summary="Second",
            output_summary="Second output",
            result={"order": 2}
        )

        id3 = await memory_manager.remember(
            agent_name="TestAgent",
            task_type="test_task",
            input_summary="Third",
            output_summary="Third output",
            result={"order": 3}
        )

        # Search
        memories = await memory_manager.search(
            query="task",
            agent_name="TestAgent",
            limit=10
        )

        # Most recent should be first
        assert memories[0].result["order"] == 3
        assert memories[1].result["order"] == 2
        assert memories[2].result["order"] == 1

    @pytest.mark.asyncio
    async def test_add_feedback_to_memory(self, memory_manager):
        """Test adding feedback to an existing memory."""
        # Store a memory
        memory_id = await memory_manager.remember(
            agent_name="TestAgent",
            task_type="test_task",
            input_summary="Test",
            output_summary="Test output",
            result={"status": "success"}
        )

        # Add feedback
        feedback = {
            "rating": 4,
            "comments": "Good result",
            "helpful": True
        }

        success = await memory_manager.add_feedback(memory_id, feedback)

        assert success is True

        # Verify feedback was added
        stored_memory = memory_manager._memory_store[0]
        assert stored_memory.user_feedback == feedback

    @pytest.mark.asyncio
    async def test_add_feedback_to_nonexistent_memory(self, memory_manager):
        """Test adding feedback to a nonexistent memory."""
        success = await memory_manager.add_feedback(
            "nonexistent_id",
            {"rating": 5}
        )

        assert success is False

    @pytest.mark.asyncio
    async def test_get_performance_history(self, memory_manager):
        """Test retrieving performance history."""
        # Store memories with performance metrics
        for i in range(5):
            await memory_manager.remember(
                agent_name="TestAgent",
                task_type="test_task",
                input_summary=f"Input {i}",
                output_summary=f"Output {i}",
                result={"status": "success"},
                performance_metrics={
                    "latency_ms": 100 + i * 10,
                    "quality_score": 0.8 + i * 0.02
                }
            )

        # Get performance history
        history = await memory_manager.get_performance_history(
            agent_name="TestAgent",
            task_type="test_task",
            limit=10
        )

        assert len(history) == 5

        # Verify structure
        for entry in history:
            assert "timestamp" in entry
            assert "task_type" in entry
            assert "metrics" in entry
            assert "latency_ms" in entry["metrics"]

    @pytest.mark.asyncio
    async def test_get_performance_history_with_feedback(self, memory_manager):
        """Test that performance history includes user feedback."""
        # Store memory
        memory_id = await memory_manager.remember(
            agent_name="TestAgent",
            task_type="test_task",
            input_summary="Test",
            output_summary="Test output",
            result={"status": "success"},
            performance_metrics={"latency_ms": 100}
        )

        # Add feedback
        await memory_manager.add_feedback(memory_id, {"rating": 5, "helpful": True})

        # Get history
        history = await memory_manager.get_performance_history(
            agent_name="TestAgent",
            limit=10
        )

        assert len(history) == 1
        assert history[0]["user_feedback"]["rating"] == 5

    @pytest.mark.asyncio
    async def test_get_user_preferences_no_feedback(self, memory_manager):
        """Test getting user preferences with no feedback."""
        prefs = await memory_manager.get_user_preferences()

        assert prefs["total_feedback_count"] == 0
        assert prefs["average_rating"] == 0.0

    @pytest.mark.asyncio
    async def test_get_user_preferences_with_feedback(self, memory_manager):
        """Test extracting user preferences from feedback."""
        # Store memories with feedback
        for i in range(3):
            memory_id = await memory_manager.remember(
                agent_name="TestAgent",
                task_type="test_task",
                input_summary=f"Test {i}",
                output_summary=f"Output {i}",
                result={"status": "success"}
            )

            await memory_manager.add_feedback(
                memory_id,
                {"rating": 4 + (i % 2), "helpful": True}  # Alternating 4 and 5
            )

        # Get preferences
        prefs = await memory_manager.get_user_preferences()

        assert prefs["total_feedback_count"] == 3
        assert 4.0 <= prefs["average_rating"] <= 5.0

    @pytest.mark.asyncio
    async def test_clear_workspace_memory(self, memory_manager):
        """Test clearing all memories for a workspace."""
        # Store some memories
        for i in range(5):
            await memory_manager.remember(
                agent_name="TestAgent",
                task_type="test_task",
                input_summary=f"Test {i}",
                output_summary=f"Output {i}",
                result={"status": "success"}
            )

        assert len(memory_manager._memory_store) == 5

        # Clear memory
        deleted_count = memory_manager.clear_workspace_memory()

        assert deleted_count == 5
        assert len(memory_manager._memory_store) == 0

    @pytest.mark.asyncio
    async def test_metadata_includes_workspace_and_user(self, memory_manager):
        """Test that stored memories include workspace and user IDs."""
        memory_id = await memory_manager.remember(
            agent_name="TestAgent",
            task_type="test_task",
            input_summary="Test",
            output_summary="Test output",
            result={"status": "success"},
            metadata={"custom_key": "value"}
        )

        stored_memory = memory_manager._memory_store[0]

        assert stored_memory.metadata["workspace_id"] == "test_ws"
        assert stored_memory.metadata["user_id"] == "test_user"
        assert stored_memory.metadata["custom_key"] == "value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
