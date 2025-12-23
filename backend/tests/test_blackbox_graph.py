from unittest.mock import MagicMock, patch
from uuid import uuid4
import pytest
from backend.graphs.blackbox_analysis import AnalysisState, ingest_telemetry_node, extract_insights_node, attribute_outcomes_node, reflect_and_validate_node, build_blackbox_graph

def test_analysis_state_definition():
    # TypedDict verification
    assert "move_id" in AnalysisState.__annotations__
    assert "telemetry_data" in AnalysisState.__annotations__

def test_ingest_telemetry_node():
    mock_session = MagicMock()
    mock_data = [{"id": "t1", "agent_id": "a1", "tokens": 10}]

    # Mocking the chained calls: session.table().select().eq().execute()
    mock_query = MagicMock()
    mock_session.table.return_value = mock_query
    mock_query.select.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.execute.return_value = MagicMock(data=mock_data)

    with patch("backend.core.vault.Vault") as mock_vault_class:
        mock_vault_instance = mock_vault_class.return_value
        mock_vault_instance.get_session.return_value = mock_session
        move_id = str(uuid4())
        state: AnalysisState = {"move_id": move_id, "telemetry_data": []}

        result = ingest_telemetry_node(state)

        assert "telemetry_data" in result
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
    # Mocking chained calls: table().select().eq().limit().execute()
    mock_query = MagicMock()
    mock_session.table.return_value = mock_query
    mock_query.select.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.execute.return_value = MagicMock(data=[
        {"id": "o1", "source": "conversion", "value": 100.0}
    ])

    with patch("backend.core.vault.Vault") as mock_vault_class:
        mock_vault_class.return_value.get_session.return_value = mock_session
        state: AnalysisState = {"move_id": str(uuid4()), "outcomes": []}
        result = attribute_outcomes_node(state)
        assert len(result["outcomes"]) == 1
        assert result["outcomes"][0]["value"] == 100.0
        assert result["status"] == "attributed"

def test_reflect_and_validate_node():
    state: AnalysisState = {
        "findings": ["Insight 1"],
        "outcomes": [{"val": 10}]
    }
    with patch("backend.inference.InferenceProvider.get_model") as mock_get_model:
        mock_llm = MagicMock()
        mock_get_model.return_value = mock_llm
        mock_llm.invoke.return_value = MagicMock(content="Confidence: 0.9\nReflection: Good.")
        
        result = reflect_and_validate_node(state)
        assert result["confidence"] == 0.9
        assert result["reflection"] == "Good."
        assert result["status"] == "validated"

def test_blackbox_graph_execution():
    mock_session = MagicMock()
    # Mock ingest
    mock_query_ingest = MagicMock()
    mock_query_ingest.select.return_value = mock_query_ingest
    mock_query_ingest.eq.return_value = mock_query_ingest
    mock_query_ingest.execute.return_value = MagicMock(data=[{"id": "t1"}])
    
    # Mock attribute
    mock_query_attr = MagicMock()
    mock_query_attr.select.return_value = mock_query_attr
    mock_query_attr.eq.return_value = mock_query_attr
    mock_query_attr.limit.return_value = mock_query_attr
    mock_query_attr.execute.return_value = MagicMock(data=[{"id": "o1", "value": 50}])
    
    # Simple table selection side effect
    def table_mock(name):
        if name == "blackbox_telemetry_industrial":
            return mock_query_ingest
        return mock_query_attr
        
    mock_session.table.side_effect = table_mock
    
    with patch("backend.core.vault.Vault") as mock_vault_class:
        mock_vault_class.return_value.get_session.return_value = mock_session
        
        with patch("backend.inference.InferenceProvider.get_model") as mock_get_model:
            mock_llm = MagicMock()
            mock_get_model.return_value = mock_llm
            
            # 1. extract response
            res1 = MagicMock(content="Finding 1")
            # 2. reflect response (Confidence high enough to complete)
            res2 = MagicMock(content="Confidence: 0.8\nReflection: Good.")
            
            mock_llm.invoke.side_effect = [res1, res2]
            
            graph = build_blackbox_graph()
            result = graph.invoke({
                "move_id": str(uuid4()), 
                "telemetry_data": [], 
                "findings": [], 
                "outcomes": [],
                "reflection": "",
                "confidence": 0.0,
                "status": ""
            })
            
            assert result["status"] == "validated"
            assert result["confidence"] == 0.8
            assert "Finding 1" in result["findings"]