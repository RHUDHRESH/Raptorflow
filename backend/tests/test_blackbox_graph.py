from unittest.mock import MagicMock, patch
from uuid import uuid4
import pytest
import asyncio
from backend.graphs.blackbox_analysis import AnalysisState, ingest_telemetry_node, extract_insights_node, attribute_outcomes_node, reflect_and_validate_node, create_blackbox_graph

def test_analysis_state_definition():
    # TypedDict verification
    assert "move_id" in AnalysisState.__annotations__
    assert "telemetry_data" in AnalysisState.__annotations__

def test_ingest_telemetry_node():
    mock_service = MagicMock()
    mock_service.get_telemetry_by_move.return_value = [{"id": "t1"}]
    
    with patch("backend.graphs.blackbox_analysis.get_blackbox_service", return_value=mock_service):
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
    mock_service = MagicMock()
    mock_service.get_outcomes_for_move.return_value = [{"id": "o1", "value": 100.0}]
    
    with patch("backend.graphs.blackbox_analysis.get_blackbox_service", return_value=mock_service):
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
    mock_service = MagicMock()
    mock_service.get_telemetry_by_move.return_value = [{"id": "t1"}]
    mock_service.get_outcomes_for_move.return_value = [{"id": "o1", "value": 50}]
    
    with patch("backend.graphs.blackbox_analysis.get_blackbox_service", return_value=mock_service):
        with patch("backend.inference.InferenceProvider.get_model") as mock_get_model:
            mock_llm = MagicMock()
            mock_get_model.return_value = mock_llm
            
            # 1. extract response
            res1 = MagicMock(content="Finding 1")
            # 2. reflect response (Confidence high enough to complete)
            res2 = MagicMock(content="Confidence: 0.8\nReflection: Good.")
            
            mock_llm.invoke.side_effect = [res1, res2]
            
            graph = create_blackbox_graph()
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

def test_blackbox_specialist_base():
    from backend.agents.blackbox_specialist import BlackboxSpecialist
    
    class MockSpecialist(BlackboxSpecialist):
        async def run(self, state: dict) -> dict:
            return {"result": "ok"}
            
    specialist = MockSpecialist(agent_id="test-spec")
    assert specialist.agent_id == "test-spec"
    assert specialist.llm is not None

def test_roi_analyst_agent():

    from backend.agents.blackbox_specialist import ROIAnalystAgent

    

    agent = ROIAnalystAgent()

    assert agent.agent_id == "roi_analyst"

    

    # Mock LLM ainvoke using patch.object to avoid Pydantic validation

    from unittest.mock import AsyncMock

    with patch.object(agent.llm, "ainvoke", new_callable=AsyncMock) as mock_ainvoke:

        mock_ainvoke.return_value = MagicMock(content="Attribution complete: 200% ROI")

        

        state = {"move_id": "m1", "outcomes": [{"value": 100}]}

        result = asyncio.run(agent.run(state))

        

        assert "attribution_report" in result

        assert "ROI" in result["attribution_report"]


