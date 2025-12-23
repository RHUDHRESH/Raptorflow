from unittest.mock import MagicMock, patch, AsyncMock
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
        state: AnalysisState = {"move_id": str(uuid4()), "telemetry_data": [], "findings": [], "outcomes": [], "status": []}
        result = ingest_telemetry_node(state)
        assert len(result["telemetry_data"]) == 1
        assert result["telemetry_data"][0]["id"] == "t1"
        assert "ingested" in result["status"]

def test_extract_insights_node():
    state: AnalysisState = {
        "move_id": "test",
        "telemetry_data": [{"id": "t1"}],
        "findings": [],
        "status": []
    }
    with patch("langchain_google_vertexai.chat_models.ChatVertexAI.ainvoke", new_callable=AsyncMock) as mock_ainvoke:
        mock_ainvoke.return_value = MagicMock(content="Insight 1")
        
        result = asyncio.run(extract_insights_node(state))
        assert result["findings"] == ["Insight 1"]
        assert "analyzed" in result["status"]

def test_attribute_outcomes_node():
    mock_service = MagicMock()
    mock_service.get_outcomes_for_move.return_value = [{"id": "o1", "value": 100.0}]
    
    with patch("backend.graphs.blackbox_analysis.get_blackbox_service", return_value=mock_service):
        state: AnalysisState = {"move_id": str(uuid4()), "outcomes": [], "status": []}
        result = attribute_outcomes_node(state)
        assert len(result["outcomes"]) == 1
        assert result["outcomes"][0]["value"] == 100.0
        assert "attributed" in result["status"]

def test_reflect_and_validate_node():
    state: AnalysisState = {
        "findings": ["Insight 1"],
        "outcomes": [{"val": 10}],
        "status": []
    }
    with patch("langchain_google_vertexai.chat_models.ChatVertexAI.ainvoke", new_callable=AsyncMock) as mock_ainvoke:
        mock_ainvoke.return_value = MagicMock(content="Confidence: 0.9\nReflection: Good.")
        
        result = asyncio.run(reflect_and_validate_node(state))
        assert result["confidence"] == 0.9
        assert result["reflection"] == "Good."
        assert "validated" in result["status"]

def test_blackbox_graph_execution():
    mock_service = MagicMock()
    mock_service.get_telemetry_by_move.return_value = [{"id": "t1"}]
    mock_service.get_outcomes_for_move.return_value = [{"id": "o1", "value": 50}]
    
    with patch("backend.graphs.blackbox_analysis.get_blackbox_service", return_value=mock_service):
        with patch("langchain_google_vertexai.chat_models.ChatVertexAI.ainvoke", new_callable=AsyncMock) as mock_ainvoke:
            # 1. extract response
            res1 = MagicMock(content="Finding 1")
            # 2. ROI response
            res2 = MagicMock(content="ROI: 200%")
            # 3. Drift response
            res3 = MagicMock(content="No drift.")
            # 4. Competitor response
            res4 = MagicMock(content="No competitor moves.")
            # 5. reflect response
            res5 = MagicMock(content="Confidence: 0.8\nReflection: Good.")
            # 6. critique response
            res6 = MagicMock(content="Score: 0.9\nReflection: Excellent.")
            
            mock_ainvoke.side_effect = [res1, res2, res3, res4, res5, res6]
            
            graph = create_blackbox_graph()
            result = asyncio.run(graph.ainvoke({
                "move_id": str(uuid4()), 
                "telemetry_data": [], 
                "findings": [], 
                "outcomes": [],
                "reflection": "",
                "confidence": 0.0,
                "status": []
            }))
            
            assert "validated" in result["status"]
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
    from unittest.mock import AsyncMock

    agent = ROIAnalystAgent()
    assert agent.agent_id == "roi_analyst"

    with patch("langchain_google_vertexai.chat_models.ChatVertexAI.ainvoke", new_callable=AsyncMock) as mock_ainvoke:
        mock_ainvoke.return_value = MagicMock(content="Attribution complete: 200% ROI")
        state = {"move_id": "m1", "outcomes": [{"value": 100}], "status": []}
        result = asyncio.run(agent.run(state))
        assert "attribution_report" in result
        assert "ROI" in result["attribution_report"]
        mock_ainvoke.assert_called_once()

def test_strategic_drift_agent():
    from backend.agents.blackbox_specialist import StrategicDriftAgent
    from unittest.mock import AsyncMock

    agent = StrategicDriftAgent()
    assert agent.agent_id == "strategic_drift"

    with patch("langchain_google_vertexai.chat_models.ChatVertexAI.ainvoke", new_callable=AsyncMock) as mock_ainvoke:
        mock_ainvoke.return_value = MagicMock(content="Drift Detected: Brand tone is too aggressive.")
        state = {"move_id": "m1", "findings": ["Finding 1"], "status": []}
        result = asyncio.run(agent.run(state))
        assert "drift_analysis" in result
        assert "Brand tone" in result["drift_analysis"]
        mock_ainvoke.assert_called_once()
        
def test_competitor_intelligence_agent():
    from backend.agents.blackbox_specialist import CompetitorIntelligenceAgent
    from unittest.mock import AsyncMock

    agent = CompetitorIntelligenceAgent()
    assert agent.agent_id == "competitor_intelligence"

    with patch("langchain_google_vertexai.chat_models.ChatVertexAI.ainvoke", new_callable=AsyncMock) as mock_ainvoke:
        mock_ainvoke.return_value = MagicMock(content="Competitor X just launched a similar feature.")
        state = {"move_id": "m1", "telemetry_data": [{"trace": {"action": "scrape"}}], "status": []}
        result = asyncio.run(agent.run(state))
        assert "competitor_insights" in result
        assert "Competitor X" in result["competitor_insights"]
        mock_ainvoke.assert_called_once()

def test_blackbox_critique_agent():
    from backend.agents.blackbox_specialist import BlackboxCritiqueAgent
    from unittest.mock import AsyncMock

    agent = BlackboxCritiqueAgent()
    assert agent.agent_id == "blackbox_critique"

    with patch("langchain_google_vertexai.chat_models.ChatVertexAI.ainvoke", new_callable=AsyncMock) as mock_ainvoke:
        mock_ainvoke.return_value = MagicMock(content="Score: 0.9\nReflection: Solid analysis.")
        state = {"findings": ["Insight 1"], "attribution_report": "ROI: 100%", "status": []}
        result = asyncio.run(agent.run(state))
        assert "critique" in result
        assert result["confidence_score"] == 0.9
        mock_ainvoke.assert_called_once()

def test_agent_specialization_accuracy():
    """Verify that each agent focuses on its assigned domain."""
    from backend.agents.blackbox_specialist import ROIAnalystAgent, StrategicDriftAgent, CompetitorIntelligenceAgent
    from unittest.mock import AsyncMock
    
    # 1. Test ROI Analyst focus
    roi_agent = ROIAnalystAgent()
    with patch("langchain_google_vertexai.chat_models.ChatVertexAI.ainvoke", new_callable=AsyncMock) as mock_inv:
        mock_inv.return_value = MagicMock(content="ROI Analysis")
        res = asyncio.run(roi_agent.run({"outcomes": []}))
        assert "attribution_report" in res
        
    # 2. Test Strategic Drift focus
    drift_agent = StrategicDriftAgent()
    with patch("langchain_google_vertexai.chat_models.ChatVertexAI.ainvoke", new_callable=AsyncMock) as mock_inv:
        mock_inv.return_value = MagicMock(content="Drift Analysis")
        res = asyncio.run(drift_agent.run({"findings": []}))
        assert "drift_analysis" in res
        
    # 3. Test Competitor Intel focus
    comp_agent = CompetitorIntelligenceAgent()
    with patch("langchain_google_vertexai.chat_models.ChatVertexAI.ainvoke", new_callable=AsyncMock) as mock_inv:
        mock_inv.return_value = MagicMock(content="Competitor Analysis")
        res = asyncio.run(comp_agent.run({"telemetry_data": []}))
        assert "competitor_insights" in res
