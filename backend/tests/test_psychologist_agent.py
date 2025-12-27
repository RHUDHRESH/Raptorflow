from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.psychologist import PsychologistAgent
from models.cognitive import AgentMessage, CognitiveIntelligenceState


@pytest.mark.asyncio
async def test_psychologist_agent_initialization():
    """Verify PsychologistAgent initializes with correct persona and tools."""
    with patch("agents.base.InferenceProvider.get_model") as mock_get_model:
        mock_get_model.return_value = MagicMock()

        agent = PsychologistAgent()
        assert agent.name == "PsychologistAgent"
        assert "Psychologist" in agent.system_prompt
        assert any(tool.name == "jtbd_framework_analyzer" for tool in agent.tools)
        assert any(tool.name == "cohorts_intelligence" for tool in agent.tools)


@pytest.mark.asyncio
async def test_psychologist_agent_execution():
    """Verify PsychologistAgent can be called."""
    mock_llm = MagicMock()
    mock_llm_with_tools = AsyncMock()
    mock_llm.bind_tools.return_value = mock_llm_with_tools

    mock_response = MagicMock()
    mock_response.content = "The core JTBD is automating industrial marketing."
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

        agent = PsychologistAgent()
        state: CognitiveIntelligenceState = {
            "messages": [
                AgentMessage(role="human", content="Analyze the target segment.")
            ],
            "workspace_id": "test-ws",
        }

        result = await agent(state)
        assert result["last_agent"] == "PsychologistAgent"
        assert "JTBD" in result["messages"][0].content
