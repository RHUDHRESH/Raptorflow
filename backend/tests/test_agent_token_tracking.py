from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agents.base import BaseCognitiveAgent
from backend.models.cognitive import AgentMessage, CognitiveIntelligenceState


class TrackerAgent(BaseCognitiveAgent):
    def __init__(self, llm):
        super().__init__(
            name="Tracker", role="strategist", system_prompt="Test", model_tier="driver"
        )
        self.llm = llm
        self.llm_with_tools = llm


@pytest.mark.asyncio
async def test_agent_token_tracking():
    """
    Phase 38: Verify that token usage is captured from metadata.
    """
    mock_llm = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = "Response"
    mock_response.response_metadata = {
        "token_usage": {"prompt_token_count": 50, "candidates_token_count": 20}
    }
    mock_llm.ainvoke.return_value = mock_response

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_inference.get_model.return_value = mock_llm

        agent = TrackerAgent(mock_llm)
        state: CognitiveIntelligenceState = {"messages": []}

        result = await agent(state)

        assert result["token_usage"]["Tracker_input"] == 50
        assert result["token_usage"]["Tracker_output"] == 20
