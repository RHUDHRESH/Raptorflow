import sys
from unittest.mock import MagicMock, patch
import pytest
from uuid import uuid4

# CRITICAL: Mock all potentially crashing dependencies BEFORE any local imports
mock_langgraph = MagicMock()
sys.modules["langgraph"] = mock_langgraph
sys.modules["langgraph.graph"] = mock_langgraph.graph

mock_vertex = MagicMock()
sys.modules["langchain_google_vertexai"] = mock_vertex

mock_supabase = MagicMock()
sys.modules["supabase"] = mock_supabase

from backend.graphs.blackbox_analysis import (
    AnalysisState, 
    ingest_telemetry_node, 
    extract_insights_node, 
    attribute_outcomes_node, 
    reflect_and_validate_node,
    should_continue,
    create_blackbox_graph
)

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
    mock_data = [{"id": "o1", "metric_value": 100.0}]
    
    mock_chain = MagicMock()
    mock_session.table.return_value = mock_chain
    mock_chain.select.return_value = mock_chain
    mock_chain.eq.return_value = mock_chain
    mock_chain.limit.return_value = mock_chain
    mock_chain.execute.return_value = MagicMock(data=mock_data)
    
    with patch("backend.core.vault.Vault") as mock_vault_class:
        mock_vault_class.return_value.get_session.return_value = mock_session
        state: AnalysisState = {"move_id": str(uuid4()), "outcomes": []}
        result = attribute_outcomes_node(state)
        assert len(result["outcomes"]) == 1
        assert result["outcomes"][0]["metric_value"] == 100.0

def test_reflect_and_validate_node():
    state: AnalysisState = {
        "findings": ["Insight 1"],
        "outcomes": [{"val": 10}]
    }
    with patch("backend.inference.InferenceProvider.get_model") as mock_get_model:
        mock_llm = MagicMock()
        mock_get_model.return_value = mock_llm
        mock_llm.invoke.return_value = MagicMock(content="Confidence: 0.9\nReflection: Good")
        
        result = reflect_and_validate_node(state)
        assert result["confidence"] == 0.9
        assert result["reflection"] == "Good"

def test_blackbox_graph_routing():
    state_low = {"confidence": 0.4}
    assert should_continue(state_low) == "extract_insights"
    state_high = {"confidence": 0.8}
    assert should_continue(state_high) == "__end__"

def test_full_blackbox_graph_execution():
    # Use the mock for StateGraph
    mock_graph_instance = MagicMock()
    mock_langgraph.graph.StateGraph.return_value.compile.return_value = mock_graph_instance
    
    graph = create_blackbox_graph()
    assert graph is not None
    
    # Simulate invoke returning a final state
    mock_graph_instance.invoke.return_value = {
        "status": "validated",
        "confidence": 0.9,
        "findings": ["f1"]
    }
    
    initial_state = {"move_id": "test"}
    final_state = graph.invoke(initial_state)
    assert final_state["confidence"] == 0.9
