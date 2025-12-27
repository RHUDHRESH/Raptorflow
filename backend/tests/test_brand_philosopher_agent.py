from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.brand_philosopher import BrandPhilosopherAgent
from models.cognitive import AgentMessage, CognitiveIntelligenceState


@pytest.mark.asyncio
async def test_brand_philosopher_agent_initialization():
    """Verify BrandPhilosopherAgent initializes with correct persona and tools."""
    with patch("agents.base.InferenceProvider.get_model") as mock_get_model:
        mock_get_model.return_value = MagicMock()

        agent = BrandPhilosopherAgent()
        assert agent.name == "BrandPhilosopherAgent"
        assert "Brand Philosopher" in agent.system_prompt
        assert any(tool.name == "style_guide_enforcer" for tool in agent.tools)


@pytest.mark.asyncio
async def test_brand_philosopher_agent_execution():
    """Verify BrandPhilosopherAgent can be called."""
    mock_llm = MagicMock()
    mock_llm_with_tools = AsyncMock()
    mock_llm.bind_tools.return_value = mock_llm_with_tools

    mock_response = MagicMock()
    mock_response.content = "Your brand narrative is now expensive and restrained."
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

        agent = BrandPhilosopherAgent()
        state: CognitiveIntelligenceState = {
            "messages": [AgentMessage(role="human", content="Review my brand voice.")],
            "workspace_id": "test-ws",
        }

        result = await agent(state)
        assert result["last_agent"] == "BrandPhilosopherAgent"
        assert "expensive" in result["messages"][0].content.lower()
