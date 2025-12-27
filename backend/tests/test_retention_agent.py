from unittest.mock import MagicMock, patch

import pytest

from agents.specialists.retention import RetentionAgent
from tools.churn_prediction import ChurnPredictionTool


@pytest.mark.asyncio
async def test_retention_agent_initialization():
    """Verify RetentionAgent initializes with correct persona and tools."""
    assert RetentionAgent is not None, "RetentionAgent not implemented yet"
    with patch("agents.base.InferenceProvider.get_model") as mock_get_model:
        mock_get_model.return_value = MagicMock()

        agent = RetentionAgent()
        assert agent.name == "RetentionAgent"
        assert "Retention & LTV Specialist" in agent.system_prompt
        assert any(tool.name == "churn_prediction_heuristics" for tool in agent.tools)


@pytest.mark.asyncio
async def test_churn_prediction_tool():
    """Verify ChurnPredictionTool returns churn data."""
    assert ChurnPredictionTool is not None, "ChurnPredictionTool not implemented yet"
    tool = ChurnPredictionTool()
    result = await tool._execute(workspace_id="test-ws")

    assert result["success"] is True
    assert "high_risk_segments" in result
    assert "churn_probability" in result
