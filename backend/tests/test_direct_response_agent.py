from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.direct_response import DirectResponseAgent
from models.cognitive import AgentMessage, CognitiveIntelligenceState


@pytest.mark.asyncio
async def test_direct_response_agent_initialization():
    """Verify DirectResponseAgent initializes with correct persona and tools."""
    with patch("agents.base.InferenceProvider.get_model") as mock_get_model:
        mock_get_model.return_value = AsyncMock()

        agent = DirectResponseAgent()
        assert agent.name == "DirectResponseAgent"
        assert "Direct Response" in agent.system_prompt
        assert any(tool.name == "conversion_optimization" for tool in agent.tools)


@pytest.mark.asyncio
async def test_direct_response_agent_heuristics():
    """Verify DirectResponseAgent mentions Scientific Advertising principles."""
    mock_llm = MagicMock()
    mock_llm_with_tools = AsyncMock()
    mock_llm.bind_tools.return_value = mock_llm_with_tools

    mock_response = MagicMock()
    mock_response.content = (
        "According to Scientific Advertising, we should use specific claims."
    )
    mock_llm_with_tools.ainvoke.return_value = mock_response

    with (
        patch("agents.base.InferenceProvider.get_model") as mock_get_model,
        patch("agents.base.get_swarm_memory_coordinator") as mock_memory,
    ):
        mock_get_model.return_value = mock_llm
        mock_memory.return_value = AsyncMock()

        agent = DirectResponseAgent()
        state: CognitiveIntelligenceState = {
            "messages": [AgentMessage(role="human", content="Analyze my ad.")],
            "workspace_id": "test-ws",
        }

        await agent(state)
        # Check if the prompt includes the heuristics
        assert "Scientific Advertising" in agent.system_prompt
        assert "Claude Hopkins" in agent.system_prompt
