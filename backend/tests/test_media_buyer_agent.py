from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.media_buyer import MediaBuyerAgent
from models.cognitive import AgentMessage, CognitiveIntelligenceState


@pytest.mark.asyncio
async def test_media_buyer_agent_initialization():
    """Verify MediaBuyerAgent initializes with correct persona and tools."""
    with patch("agents.base.InferenceProvider.get_model") as mock_get_model:
        mock_get_model.return_value = MagicMock()

        agent = MediaBuyerAgent()
        assert agent.name == "MediaBuyerAgent"
        assert "Media Buyer" in agent.system_prompt
        assert any(tool.name == "budget_pacing_simulator" for tool in agent.tools)


@pytest.mark.asyncio
async def test_media_buyer_agent_execution():
    """Verify MediaBuyerAgent can be called."""
    mock_llm = MagicMock()
    mock_llm_with_tools = AsyncMock()
    mock_llm.bind_tools.return_value = mock_llm_with_tools

    mock_response = MagicMock()
    mock_response.content = (
        "Ad spend optimized. Pacing is on track for $10k monthly budget."
    )
    mock_response.response_metadata = {
        "token_usage": {"prompt_token_count": 10, "candidates_token_count": 5}
    }
    mock_llm_with_tools.ainvoke.return_value = mock_response

    with (
        patch("agents.base.InferenceProvider.get_model") as mock_get_model,
        patch("agents.base.get_swarm_memory_coordinator") as mock_memory,
    ):
        mock_get_model.return_value = mock_llm
        mock_memory.return_value = AsyncMock()

        agent = MediaBuyerAgent()
        state: CognitiveIntelligenceState = {
            "messages": [
                AgentMessage(role="human", content="Optimize my $10k budget.")
            ],
            "workspace_id": "test-ws",
        }

        result = await agent(state)
        assert result["last_agent"] == "MediaBuyerAgent"
        assert "budget" in result["messages"][0].content.lower()
