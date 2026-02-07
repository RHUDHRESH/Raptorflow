from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.base import BaseCognitiveAgent
from models.cognitive import AgentMessage, CognitiveIntelligenceState


class StreamAgent(BaseCognitiveAgent):
    def __init__(self, llm):
        super().__init__(
            name="Streamer",
            role="strategist",
            system_prompt="Test",
            model_tier="driver",
        )
        self.llm = llm
        self.llm_with_tools = llm


@pytest.mark.asyncio
async def test_agent_streaming():
    """
    Phase 39: Verify agent can yield stream chunks.
    """
    mock_llm = MagicMock()

    async def mock_astream(messages):
        yield MagicMock(content="Chunk 1")
        yield MagicMock(content="Chunk 2")

    mock_llm.astream = mock_astream

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_inference.get_model.return_value = mock_llm

        agent = StreamAgent(mock_llm)
        state: CognitiveIntelligenceState = {"messages": []}

        chunks = []
        async for chunk in agent.astream(state):
            chunks.append(chunk.content)

        assert chunks == ["Chunk 1", "Chunk 2"]
