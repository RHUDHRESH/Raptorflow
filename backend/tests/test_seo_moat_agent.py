from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.seo_moat import SEOMoatAgent
from models.cognitive import AgentMessage, CognitiveIntelligenceState


@pytest.mark.asyncio
async def test_seo_moat_agent_initialization():
    """Verify SEOMoatAgent initializes with correct persona and tools."""
    with patch("agents.base.InferenceProvider.get_model") as mock_get_model:
        mock_get_model.return_value = MagicMock()

        agent = SEOMoatAgent()
        assert agent.name == "SEOMoatAgent"
        assert "SEO & Content Moat" in agent.system_prompt
        assert any(tool.name == "semantic_cluster_generator" for tool in agent.tools)
        assert any(tool.name == "radar_keywords" for tool in agent.tools)


@pytest.mark.asyncio
async def test_seo_moat_agent_execution():
    """Verify SEOMoatAgent can be called."""
    mock_llm = MagicMock()
    mock_llm_with_tools = AsyncMock()
    mock_llm.bind_tools.return_value = mock_llm_with_tools

    mock_response = MagicMock()
    mock_response.content = "Semantic cluster generated for 'Marketing OS'."
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

        agent = SEOMoatAgent()
        state: CognitiveIntelligenceState = {
            "messages": [
                AgentMessage(role="human", content="Build a moat for Marketing OS.")
            ],
            "workspace_id": "test-ws",
        }

        result = await agent(state)
        assert result["last_agent"] == "SEOMoatAgent"
        assert (
            "moat" in result["messages"][0].content.lower()
            or "cluster" in result["messages"][0].content.lower()
        )
