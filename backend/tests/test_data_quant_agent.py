from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.specialists.data_quant import DataQuantAgent
from models.cognitive import AgentMessage, CognitiveIntelligenceState


@pytest.mark.asyncio
async def test_data_quant_agent_initialization():
    """Verify DataQuantAgent initializes with correct persona and tools."""
    with patch("agents.base.InferenceProvider.get_model") as mock_get_model:
        mock_get_model.return_value = MagicMock()

        agent = DataQuantAgent()
        assert agent.name == "DataQuantAgent"
        assert "Data Quant" in agent.system_prompt
        assert any(tool.name == "bigquery_query_engine" for tool in agent.tools)
        assert any(tool.name == "bayesian_confidence_scorer" for tool in agent.tools)
        assert any(tool.name == "matrix_kpi_stream" for tool in agent.tools)


@pytest.mark.asyncio
async def test_data_quant_agent_execution():
    """Verify DataQuantAgent can be called."""
    mock_llm = MagicMock()
    mock_llm_with_tools = AsyncMock()
    mock_llm.bind_tools.return_value = mock_llm_with_tools

    mock_response = MagicMock()
    mock_response.content = "Confidence score is 0.98. Status: Validated Genius."
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

        agent = DataQuantAgent()
        state: CognitiveIntelligenceState = {
            "messages": [AgentMessage(role="human", content="Score this experiment.")],
            "workspace_id": "test-ws",
        }

        result = await agent(state)
        assert result["last_agent"] == "DataQuantAgent"
        assert "Genius" in result["messages"][0].content
