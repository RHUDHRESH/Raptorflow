from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4
import pytest
import asyncio
from backend.graphs.blackbox_industrial import (
    AnalysisState,
    ingest_telemetry_node,
    extract_insights_node,
    attribute_outcomes_node,
    supervisor_node,
    reflect_and_validate_node,
    should_continue,
    create_blackbox_graph,
)


def test_analysis_state_definition():
    assert "move_id" in AnalysisState.__annotations__
    assert "telemetry_data" in AnalysisState.__annotations__


def test_ingest_telemetry_node():
    mock_session = MagicMock()
    mock_data = [{"id": "t1", "agent_id": "a1", "tokens": 10}]

    mock_table = MagicMock()
    mock_session.table.return_value = mock_table
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=mock_data)

    with patch("backend.core.vault.Vault") as mock_vault_class:
        mock_vault_class.return_value.get_session.return_value = mock_session
        state: AnalysisState = {"move_id": str(uuid4()), "telemetry_data": []}
        result = ingest_telemetry_node(state)
        assert len(result["telemetry_data"]) == 1
        assert result["telemetry_data"][0]["id"] == "t1"


def test_extract_insights_node():
    state: AnalysisState = {
        "move_id": "test",
        "telemetry_data": [{"id": "t1"}],
        "findings": [],
    }
    with patch(
        "langchain_google_vertexai.chat_models.ChatVertexAI.ainvoke",
        new_callable=AsyncMock,
    ) as mock_ainvoke:
        mock_ainvoke.return_value = MagicMock(content="Insight 1")

        result = asyncio.run(extract_insights_node(state))
        assert result["findings"] == ["Insight 1"]


def test_attribute_outcomes_node():
    mock_session = MagicMock()
    mock_data = [{"id": "o1", "value": 100.0}]

    mock_table = MagicMock()
    mock_session.table.return_value = mock_table
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=mock_data)

    with patch("backend.core.vault.Vault") as mock_vault_class:
        mock_vault_class.return_value.get_session.return_value = mock_session
        state: AnalysisState = {"move_id": str(uuid4()), "outcomes": []}
        result = attribute_outcomes_node(state)
        assert len(result["outcomes"]) == 1
        assert result["outcomes"][0]["value"] == 100.0


def test_reflect_and_validate_node():
    state: AnalysisState = {"findings": ["Insight 1"], "outcomes": [{"val": 10}]}
    with patch(
        "langchain_google_vertexai.chat_models.ChatVertexAI.ainvoke",
        new_callable=AsyncMock,
    ) as mock_ainvoke:
        mock_ainvoke.return_value = MagicMock(
            content="Confidence: 0.9\nReflection: Good"
        )

        result = asyncio.run(reflect_and_validate_node(state))
        assert result["confidence"] == 0.9
        assert result["reflection"] == "Good"


def test_blackbox_graph_routing():
    state_low = {"confidence": 0.4}
    assert should_continue(state_low) == "retry"
    state_high = {"confidence": 0.8}
    assert should_continue(state_high) == "__end__"


def test_learning_agent():
    from backend.agents.blackbox_specialist import LearningAgent

    agent = LearningAgent()
    assert agent.agent_id == "learning_agent"

    with patch(
        "langchain_google_vertexai.chat_models.ChatVertexAI.ainvoke",
        new_callable=AsyncMock,
    ) as mock_ainvoke:
        mock_ainvoke.return_value = MagicMock(content="Pivot: Switch to video content.")
        state = {
            "findings": ["Text ads have low CTR"],
            "reflection": "Users want more visual engagement.",
            "status": [],
        }
        result = asyncio.run(agent.run(state))
        assert "pivots" in result
        assert "video content" in result["pivots"]
        mock_ainvoke.assert_called_once()
