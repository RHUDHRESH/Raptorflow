from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agents.memory_reflection import MemoryReflectionAgent


@pytest.mark.asyncio
async def test_memory_reflection_summarize_daily():
    """Verify that the reflection agent can summarize a list of traces."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()

    # Create a real-ish object for the return value
    class MockResult:
        def __init__(self, summary, learnings, confidence):
            self.summary = summary
            self.learnings = learnings
            self.confidence = confidence

        def model_dump(self):
            return {
                "summary": self.summary,
                "learnings": self.learnings,
                "confidence": self.confidence,
            }

    mock_chain.ainvoke.return_value = MockResult(
        summary="Busy day with 5 successful campaign generations.",
        learnings=["Users prefer shorter action items."],
        confidence=0.9,
    )
    mock_llm.with_structured_output.return_value = mock_chain

    with patch(
        "backend.agents.memory_reflection.InferenceProvider"
    ) as mock_inference, patch(
        "backend.agents.memory_reflection.SwarmLearning"
    ) as mock_swarm_learning:
        mock_inference.get_model.return_value = mock_llm
        mock_swarm_learning.return_value.record_learning = AsyncMock()

        agent = MemoryReflectionAgent()
        traces = [
            {"thought": "Generated move 1", "status": "success"},
            {"thought": "Generated move 2", "status": "success"},
        ]

        result = await agent.reflect_on_traces(workspace_id="ws_1", traces=traces)

        assert "Busy day" in result["summary"]
        assert len(result["learnings"]) > 0
        mock_chain.ainvoke.assert_called_once()
