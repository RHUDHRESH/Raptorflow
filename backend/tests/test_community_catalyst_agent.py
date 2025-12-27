from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.community_catalyst import CommunityCatalystAgent
from models.cognitive import AgentMessage, CognitiveIntelligenceState


@pytest.mark.asyncio
async def test_community_catalyst_agent_initialization():
    """Verify CommunityCatalystAgent initializes with correct persona and tools."""
    with patch("agents.base.InferenceProvider.get_model") as mock_get_model:
        mock_get_model.return_value = MagicMock()

        agent = CommunityCatalystAgent()
        assert agent.name == "CommunityCatalystAgent"
        assert "Community Catalyst" in agent.system_prompt
        assert any(tool.name == "sentiment_analysis" for tool in agent.tools)


@pytest.mark.asyncio
async def test_community_catalyst_agent_execution():
    """Verify CommunityCatalystAgent can be called."""
    mock_llm = MagicMock()
    mock_llm_with_tools = AsyncMock()
    mock_llm.bind_tools.return_value = mock_llm_with_tools

    mock_response = MagicMock()
    mock_response.content = (
        "User sentiment is positive. Recommended action: Public validation."
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

        agent = CommunityCatalystAgent()
        state: CognitiveIntelligenceState = {
            "messages": [
                AgentMessage(role="human", content="How is the community feeling?")
            ],
            "workspace_id": "test-ws",
        }

        result = await agent(state)
        assert result["last_agent"] == "CommunityCatalystAgent"
        assert "sentiment" in result["messages"][0].content.lower()
