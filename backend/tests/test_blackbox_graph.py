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

from backend.graphs.blackbox_industrial import (
    AnalysisState, 
    ingest_telemetry_node, 
    extract_insights_node, 
    attribute_outcomes_node, 
    supervisor_node,
    reflect_and_validate_node,
    should_continue,
    create_blackbox_graph
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

def test_supervisor_agent_collaboration():
    state: AnalysisState = {
        "move_id": "move-123",
        "telemetry_data": [{"id": "t1"}],
        "findings": [],
        "outcomes": [{"val": 10}]
    }
    
    with patch("backend.agents.roi_analyst.ROIAnalystAgent.run") as mock_roi:
        with patch("backend.agents.drift_detector.StrategicDriftAgent.run") as mock_drift:
            with patch("backend.agents.competitor_intel.CompetitorIntelligenceAgent.run") as mock_intel:
                mock_roi.return_value = {"attribution": "ROI ok"}
                mock_drift.return_value = {"drift_report": "No drift"}
                mock_intel.return_value = {"competitor_insights": "No moves"}
                
                result = supervisor_node(state)
                assert "findings" in result
                assert "ROI ok" in result["findings"]
                assert "No drift" in result["findings"]
                assert result["status"] == "coordinated"

def test_critique_loop_logic():
    state: AnalysisState = {
        "findings": ["Weak finding"],
        "outcomes": []
    }
    
    with patch("backend.inference.InferenceProvider.get_model") as mock_get_model:
        mock_llm = MagicMock()
        mock_get_model.return_value = mock_llm
        
        # Simulate LLM providing a low-confidence critique
        mock_llm.invoke.return_value = MagicMock(
            content="Confidence: 0.3\nReflection: This analysis is insufficient. Findings are too vague."
        )
        
        result = reflect_and_validate_node(state)
        assert result["confidence"] == 0.3
        assert "insufficient" in result["reflection"]
        assert result["status"] == "validated"

def test_blackbox_graph_routing():
    state_low = {"confidence": 0.4}
    assert should_continue(state_low) == "retry"
    state_high = {"confidence": 0.8}
    assert should_continue(state_high) == "__end__"
