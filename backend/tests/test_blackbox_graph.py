import sys
from unittest.mock import MagicMock, patch
import pytest
from uuid import uuid4
from backend.graphs.blackbox_analysis import AnalysisState, ingest_telemetry_node, extract_insights_node, attribute_outcomes_node

def test_analysis_state_definition():
    assert "move_id" in AnalysisState.__annotations__
    assert "telemetry_data" in AnalysisState.__annotations__

def test_analysis_state_accumulation():
    state1: AnalysisState = {
        "move_id": "test",
        "telemetry_data": [{"id": 1}],
        "findings": ["initial"],
        "outcomes": [],
        "reflection": "",
        "confidence": 0.0,
        "status": "start"
    }
    state2: AnalysisState = {
        "telemetry_data": [{"id": 2}],
        "findings": ["new"],
        "reflection": "updated"
    }
    import operator
    combined_telemetry = operator.add(state1["telemetry_data"], state2["telemetry_data"])
    assert len(combined_telemetry) == 2

def test_ingest_telemetry_node():
    mock_session = MagicMock()
    mock_data = [{"id": "t1", "agent_id": "a1", "tokens": 10}]
    
    # Mock chain: session.table().select().eq().execute().data
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
        "findings": []
    }
    with patch("backend.inference.InferenceProvider.get_model") as mock_get_model:
        mock_llm = MagicMock()
        mock_get_model.return_value = mock_llm
        mock_llm.invoke.return_value = MagicMock(content="Insight 1")
        
        result = extract_insights_node(state)
        assert result["findings"] == ["Insight 1"]

def test_attribute_outcomes_node():
    mock_session = MagicMock()
    # Mocking chained calls: table().select().limit().execute()
    mock_query = MagicMock()
    mock_session.table.return_value = mock_query
    mock_query.select.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.execute.return_value = MagicMock(data=[
        {"id": "o1", "source": "conversion", "value": 100.0}
    ])

    
    with patch("backend.core.vault.Vault") as mock_vault_class:
        mock_vault_class.return_value.get_session.return_value = mock_session
        state: AnalysisState = {"move_id": str(uuid4()), "outcomes": []}
        result = attribute_outcomes_node(state)
        assert len(result["outcomes"]) == 1
        assert result["outcomes"][0]["metric_value"] == 100.0
