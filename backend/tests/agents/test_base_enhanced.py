"""
Unit tests for BaseAgentEnhanced and memory integration.

Tests verify that:
1. BaseAgentEnhanced calls search() before executing
2. BaseAgentEnhanced enriches context with memories and preferences
3. BaseAgentEnhanced calls remember() after execution
4. BaseAgentEnhanced stores feedback via learn_from_feedback()
5. Performance metrics are tracked correctly
6. Error handling works correctly
"""

import pytest
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from backend.agents.base_enhanced import BaseAgentEnhanced
from backend.memory.manager import MemoryManager, MemoryEntry


class TestAgent(BaseAgentEnhanced):
    """
    Concrete test implementation of BaseAgentEnhanced.

    This agent simply echoes the input with some modifications,
    allowing us to test the memory integration without complex logic.
    """

    def __init__(self, memory: MemoryManager):
        super().__init__(name="TestAgent", memory=memory)
        self.core_execute_called = False
        self.received_context = None

    async def _execute_core(self, enriched_context: Dict[str, Any]) -> Dict[str, Any]:
        """Simple echo implementation for testing."""
        self.core_execute_called = True
        self.received_context = enriched_context

        # Echo the input with a simple transformation
        message = enriched_context.get("message", "")
        return {
            "echo": message.upper(),
            "original": message,
            "confidence": 0.95
        }

    def _get_task_type(self) -> str:
        return "test_task"

    def _create_input_summary(self, payload: Dict[str, Any]) -> str:
        return f"Test task: {payload.get('message', 'no message')}"

    def _create_output_summary(self, result: Dict[str, Any]) -> str:
        return f"Echoed: {result.get('echo', 'no echo')}"


@pytest.fixture
def mock_memory():
    """Create a mock MemoryManager for testing."""
    memory = MagicMock(spec=MemoryManager)
    memory.workspace_id = "test_workspace"
    memory.user_id = "test_user"

    # Mock search to return empty list by default
    memory.search = AsyncMock(return_value=[])

    # Mock remember to return a memory ID
    memory.remember = AsyncMock(return_value="mem_test_123")

    # Mock get_user_preferences to return empty prefs
    memory.get_user_preferences = AsyncMock(return_value={
        "total_feedback_count": 0,
        "average_rating": 0.0,
        "common_corrections": {},
        "preferences": {}
    })

    # Mock add_feedback
    memory.add_feedback = AsyncMock(return_value=True)

    # Mock get_performance_history
    memory.get_performance_history = AsyncMock(return_value=[])

    return memory


@pytest.fixture
def test_agent(mock_memory):
    """Create a TestAgent instance with mock memory."""
    return TestAgent(memory=mock_memory)


class TestBaseAgentEnhancedMemoryIntegration:
    """Test suite for memory integration in BaseAgentEnhanced."""

    @pytest.mark.asyncio
    async def test_calls_memory_search_before_executing(self, test_agent, mock_memory):
        """Test that agent searches memory before executing core logic."""
        payload = {"message": "hello world"}

        result = await test_agent.execute(payload)

        # Verify memory.search() was called
        assert mock_memory.search.called
        assert mock_memory.search.call_count == 1

        # Verify search parameters
        call_args = mock_memory.search.call_args
        assert call_args.kwargs["agent_name"] == "TestAgent"
        assert call_args.kwargs["task_type"] == "test_task"
        assert call_args.kwargs["limit"] == 5

        # Verify execution succeeded
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_enriches_context_with_memories(self, test_agent, mock_memory):
        """Test that agent enriches context with recalled memories."""
        # Create mock memories
        mock_memories = [
            MemoryEntry(
                agent_name="TestAgent",
                task_type="test_task",
                input_summary="Previous test: hello",
                output_summary="Echoed: HELLO",
                result={"echo": "HELLO"},
                performance_metrics={"execution_time_ms": 100}
            ),
            MemoryEntry(
                agent_name="TestAgent",
                task_type="test_task",
                input_summary="Previous test: world",
                output_summary="Echoed: WORLD",
                result={"echo": "WORLD"},
                performance_metrics={"execution_time_ms": 120}
            )
        ]

        mock_memory.search.return_value = mock_memories

        payload = {"message": "hello world"}
        result = await test_agent.execute(payload)

        # Verify context was enriched
        assert test_agent.core_execute_called
        enriched_context = test_agent.received_context

        assert "recalled_memories" in enriched_context
        assert len(enriched_context["recalled_memories"]) == 2

        assert "memory_summaries" in enriched_context
        assert len(enriched_context["memory_summaries"]) == 2

        assert "user_preferences" in enriched_context
        assert "original_payload" in enriched_context
        assert enriched_context["original_payload"] == payload

    @pytest.mark.asyncio
    async def test_enriches_context_with_user_preferences(self, test_agent, mock_memory):
        """Test that agent enriches context with user preferences."""
        mock_prefs = {
            "total_feedback_count": 10,
            "average_rating": 4.2,
            "common_corrections": {"tone": "professional"},
            "preferences": {"style": "concise"}
        }

        mock_memory.get_user_preferences.return_value = mock_prefs

        payload = {"message": "test"}
        result = await test_agent.execute(payload)

        enriched_context = test_agent.received_context

        assert enriched_context["user_preferences"] == mock_prefs
        assert enriched_context["average_user_rating"] == 4.2
        assert enriched_context["total_feedback_count"] == 10

    @pytest.mark.asyncio
    async def test_calls_memory_remember_after_execution(self, test_agent, mock_memory):
        """Test that agent stores result in memory after execution."""
        payload = {"message": "hello"}

        result = await test_agent.execute(payload)

        # Verify memory.remember() was called
        assert mock_memory.remember.called
        assert mock_memory.remember.call_count == 1

        # Verify remember parameters
        call_args = mock_memory.remember.call_args
        assert call_args.kwargs["agent_name"] == "TestAgent"
        assert call_args.kwargs["task_type"] == "test_task"
        assert "Test task: hello" in call_args.kwargs["input_summary"]
        assert "Echoed: HELLO" in call_args.kwargs["output_summary"]
        assert call_args.kwargs["result"]["echo"] == "HELLO"

        # Verify performance metrics were included
        perf_metrics = call_args.kwargs["performance_metrics"]
        assert "execution_time_ms" in perf_metrics
        assert perf_metrics["execution_time_ms"] > 0
        assert perf_metrics["recalled_memory_count"] == 0

    @pytest.mark.asyncio
    async def test_returns_memory_id_in_metadata(self, test_agent, mock_memory):
        """Test that agent returns memory_id in result metadata."""
        payload = {"message": "test"}

        result = await test_agent.execute(payload)

        assert "metadata" in result
        assert "memory_id" in result["metadata"]
        assert result["metadata"]["memory_id"] == "mem_test_123"

    @pytest.mark.asyncio
    async def test_tracks_performance_metrics(self, test_agent, mock_memory):
        """Test that agent tracks performance metrics correctly."""
        payload = {"message": "test"}

        result = await test_agent.execute(payload)

        assert "metadata" in result
        assert "execution_time_ms" in result["metadata"]
        assert result["metadata"]["execution_time_ms"] > 0

        # Verify metrics were passed to memory.remember()
        call_args = mock_memory.remember.call_args
        perf_metrics = call_args.kwargs["performance_metrics"]

        assert "execution_time_ms" in perf_metrics
        assert "recalled_memory_count" in perf_metrics
        assert "confidence_score" in perf_metrics
        assert perf_metrics["confidence_score"] == 0.95  # From test agent result


class TestBaseAgentEnhancedFeedbackLearning:
    """Test suite for feedback learning in BaseAgentEnhanced."""

    @pytest.mark.asyncio
    async def test_learn_from_feedback_stores_feedback(self, test_agent, mock_memory):
        """Test that learn_from_feedback stores feedback in memory."""
        feedback = {
            "rating": 4,
            "comments": "Good result",
            "helpful": True
        }

        result = await test_agent.learn_from_feedback("mem_123", feedback)

        # Verify add_feedback was called
        assert mock_memory.add_feedback.called
        call_args = mock_memory.add_feedback.call_args
        assert call_args.args[0] == "mem_123"
        assert call_args.args[1] == feedback

        # Verify result
        assert result["status"] == "success"
        assert result["feedback_stored"] is True

    @pytest.mark.asyncio
    async def test_learn_from_feedback_detects_corrections(self, test_agent, mock_memory):
        """Test that learn_from_feedback detects corrections in feedback."""
        feedback = {
            "rating": 3,
            "corrections": {
                "echo": "CORRECTED_VALUE",
                "tone": "professional"
            }
        }

        result = await test_agent.learn_from_feedback("mem_123", feedback)

        assert result["has_corrections"] is True
        assert "echo" in result["corrected_fields"]
        assert "tone" in result["corrected_fields"]

    @pytest.mark.asyncio
    async def test_learn_from_feedback_flags_low_ratings(self, test_agent, mock_memory):
        """Test that learn_from_feedback flags low ratings."""
        feedback = {
            "rating": 2,
            "comments": "Not helpful"
        }

        result = await test_agent.learn_from_feedback("mem_123", feedback)

        assert result["needs_improvement"] is True

    @pytest.mark.asyncio
    async def test_learn_from_feedback_handles_missing_memory(self, test_agent, mock_memory):
        """Test that learn_from_feedback handles missing memory gracefully."""
        mock_memory.add_feedback.return_value = False

        feedback = {"rating": 4}

        result = await test_agent.learn_from_feedback("nonexistent_mem", feedback)

        assert result["status"] == "error"
        assert "not found" in result["message"]

    @pytest.mark.asyncio
    async def test_get_improvement_suggestions_with_no_history(self, test_agent, mock_memory):
        """Test improvement suggestions with no historical data."""
        mock_memory.get_performance_history.return_value = []

        suggestions = await test_agent.get_improvement_suggestions(limit=10)

        assert suggestions["status"] == "insufficient_data"

    @pytest.mark.asyncio
    async def test_get_improvement_suggestions_with_history(self, test_agent, mock_memory):
        """Test improvement suggestions with historical performance data."""
        mock_history = [
            {
                "timestamp": "2025-01-01T10:00:00",
                "task_type": "test_task",
                "metrics": {"execution_time_ms": 1200},
                "user_feedback": {"rating": 4, "comments": "Good"}
            },
            {
                "timestamp": "2025-01-01T11:00:00",
                "task_type": "test_task",
                "metrics": {"execution_time_ms": 1500},
                "user_feedback": {"rating": 3, "comments": "Slow"}
            },
            {
                "timestamp": "2025-01-01T12:00:00",
                "task_type": "test_task",
                "metrics": {"execution_time_ms": 1100},
                "user_feedback": {"rating": 5, "comments": "Excellent"}
            }
        ]

        mock_memory.get_performance_history.return_value = mock_history

        suggestions = await test_agent.get_improvement_suggestions(limit=10)

        assert suggestions["status"] == "success"
        assert suggestions["total_executions"] == 3
        assert suggestions["feedback_count"] == 3
        assert suggestions["average_rating"] == 4.0  # (4 + 3 + 5) / 3
        assert suggestions["average_execution_time_ms"] > 0
        assert len(suggestions["common_issues"]) <= 5

    @pytest.mark.asyncio
    async def test_get_improvement_suggestions_flags_low_rating(self, test_agent, mock_memory):
        """Test that low average rating generates improvement suggestion."""
        mock_history = [
            {
                "timestamp": "2025-01-01T10:00:00",
                "task_type": "test_task",
                "metrics": {"execution_time_ms": 1000},
                "user_feedback": {"rating": 2}
            },
            {
                "timestamp": "2025-01-01T11:00:00",
                "task_type": "test_task",
                "metrics": {"execution_time_ms": 1000},
                "user_feedback": {"rating": 3}
            }
        ]

        mock_memory.get_performance_history.return_value = mock_history

        suggestions = await test_agent.get_improvement_suggestions()

        assert suggestions["average_rating"] == 2.5
        assert any("satisfaction" in s.lower() for s in suggestions["suggestions"])


class TestBaseAgentEnhancedErrorHandling:
    """Test suite for error handling in BaseAgentEnhanced."""

    @pytest.mark.asyncio
    async def test_stores_error_in_memory_on_failure(self, mock_memory):
        """Test that errors are stored in memory for learning."""

        class FailingAgent(BaseAgentEnhanced):
            async def _execute_core(self, enriched_context):
                raise ValueError("Test error")

            def _get_task_type(self):
                return "test_task"

            def _create_input_summary(self, payload):
                return "Test input"

            def _create_output_summary(self, result):
                return "Test output"

        agent = FailingAgent(name="FailingAgent", memory=mock_memory)

        with pytest.raises(ValueError, match="Test error"):
            await agent.execute({"message": "test"})

        # Verify error was stored in memory
        assert mock_memory.remember.called
        call_args = mock_memory.remember.call_args

        assert call_args.kwargs["task_type"] == "test_task_error"
        assert "error" in call_args.kwargs["result"]
        assert "Test error" in call_args.kwargs["result"]["error"]
        assert call_args.kwargs["performance_metrics"]["success"] is False

    @pytest.mark.asyncio
    async def test_error_storage_failure_is_silent(self, mock_memory):
        """Test that failure to store error doesn't crash the agent."""

        class FailingAgent(BaseAgentEnhanced):
            async def _execute_core(self, enriched_context):
                raise ValueError("Core error")

            def _get_task_type(self):
                return "test_task"

            def _create_input_summary(self, payload):
                return "Test"

            def _create_output_summary(self, result):
                return "Test"

        # Make memory.remember fail
        mock_memory.remember.side_effect = Exception("Memory storage failed")

        agent = FailingAgent(name="FailingAgent", memory=mock_memory)

        # Original error should still be raised, memory storage failure is logged
        with pytest.raises(ValueError, match="Core error"):
            await agent.execute({"message": "test"})


class TestBaseAgentEnhancedWithRealMemory:
    """Integration tests using real MemoryManager (in-memory storage)."""

    @pytest.mark.asyncio
    async def test_full_memory_lifecycle(self):
        """Test complete memory lifecycle: store -> recall -> feedback."""
        memory = MemoryManager(workspace_id="test_ws", user_id="test_user")
        agent = TestAgent(memory=memory)

        # First execution (no memories to recall)
        payload1 = {"message": "first message"}
        result1 = await agent.execute(payload1)

        assert result1["status"] == "success"
        assert result1["metadata"]["recalled_memory_count"] == 0
        memory_id1 = result1["metadata"]["memory_id"]

        # Add feedback to first execution
        feedback1 = {"rating": 5, "comments": "Excellent", "helpful": True}
        feedback_result = await agent.learn_from_feedback(memory_id1, feedback1)
        assert feedback_result["status"] == "success"

        # Second execution (should recall first execution)
        payload2 = {"message": "second message"}
        result2 = await agent.execute(payload2)

        assert result2["status"] == "success"
        # Should recall at least one memory (the first execution)
        assert result2["metadata"]["recalled_memory_count"] >= 1

        # Verify enriched context contained recalled memories
        assert agent.received_context is not None
        assert len(agent.received_context["recalled_memories"]) >= 1

        # Verify user preferences include feedback
        prefs = await memory.get_user_preferences()
        assert prefs["total_feedback_count"] == 1
        assert prefs["average_rating"] == 5.0

    @pytest.mark.asyncio
    async def test_cross_execution_learning(self):
        """Test that agent learns from multiple executions."""
        memory = MemoryManager(workspace_id="test_ws", user_id="test_user")
        agent = TestAgent(memory=memory)

        # Execute multiple times
        for i in range(5):
            payload = {"message": f"message {i}"}
            result = await agent.execute(payload)

            # Add feedback
            feedback = {"rating": 4 + (i % 2), "helpful": True}  # Alternating 4 and 5
            await agent.learn_from_feedback(result["metadata"]["memory_id"], feedback)

        # Get improvement suggestions
        suggestions = await agent.get_improvement_suggestions(limit=10)

        assert suggestions["status"] == "success"
        assert suggestions["total_executions"] == 5
        assert suggestions["feedback_count"] == 5
        assert 4.0 <= suggestions["average_rating"] <= 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
