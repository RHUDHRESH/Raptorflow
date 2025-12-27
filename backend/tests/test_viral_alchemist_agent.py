from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.viral_alchemist import ViralAlchemistAgent
from models.cognitive import AgentMessage, CognitiveIntelligenceState


@pytest.mark.asyncio
async def test_viral_alchemist_agent_initialization():
    """Verify ViralAlchemistAgent initializes with correct persona and tools."""
    with patch("agents.base.InferenceProvider.get_model") as mock_get_model:
        mock_get_model.return_value = MagicMock()

        agent = ViralAlchemistAgent()
        assert agent.name == "ViralAlchemistAgent"
        assert "Viral Alchemist" in agent.system_prompt
        assert any(tool.name == "radar_trend_analyzer" for tool in agent.tools)


@pytest.mark.asyncio
async def test_viral_alchemist_agent_execution():
    """Verify ViralAlchemistAgent can be called."""
    mock_llm = MagicMock()
    mock_llm_with_tools = AsyncMock()
    mock_llm.bind_tools.return_value = mock_llm_with_tools

    mock_response = MagicMock()
    mock_response.content = "Here is a viral hook for you."
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

        agent = ViralAlchemistAgent()
        state: CognitiveIntelligenceState = {
            "messages": [AgentMessage(role="human", content="Give me a hook.")],
            "workspace_id": "test-ws",
        }

        result = await agent(state)
        assert result["last_agent"] == "ViralAlchemistAgent"
        assert "viral hook" in result["messages"][0].content.lower()
