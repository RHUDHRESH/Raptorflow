from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.pr_specialist import PRSpecialistAgent
from models.cognitive import AgentMessage, CognitiveIntelligenceState


@pytest.mark.asyncio
async def test_pr_specialist_agent_initialization():
    """Verify PRSpecialistAgent initializes with correct persona and tools."""
    with patch("agents.base.InferenceProvider.get_model") as mock_get_model:
        mock_get_model.return_value = MagicMock()

        agent = PRSpecialistAgent()
        assert agent.name == "PRSpecialistAgent"
        assert "PR & Media" in agent.system_prompt
        assert any(tool.name == "journalist_pitch_architect" for tool in agent.tools)


@pytest.mark.asyncio
async def test_pr_specialist_agent_execution():
    """Verify PRSpecialistAgent can be called."""
    mock_llm = MagicMock()
    mock_llm_with_tools = AsyncMock()
    mock_llm.bind_tools.return_value = mock_llm_with_tools

    mock_response = MagicMock()
    mock_response.content = "Here is a surgical pitch for TechCrunch."
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

        agent = PRSpecialistAgent()
        state: CognitiveIntelligenceState = {
            "messages": [
                AgentMessage(
                    role="human", content="Pitch my new feature to TechCrunch."
                )
            ],
            "workspace_id": "test-ws",
        }

        result = await agent(state)
        assert result["last_agent"] == "PRSpecialistAgent"
        assert "pitch" in result["messages"][0].content.lower()
