import sys
from unittest.mock import MagicMock, patch
import pytest

# Mock crashing dependencies
mock_vertex = MagicMock()
sys.modules["langchain_google_vertexai"] = mock_vertex

from backend.agents.blackbox_specialist import BlackboxSpecialist

def test_blackbox_specialist_base():
    # Concrete implementation for testing
    class ConcreteSpecialist(BlackboxSpecialist):
        def run(self, move_id, data):
            return {"result": "analyzed"}
            
    with patch("backend.inference.InferenceProvider.get_model") as mock_get_model:
        mock_get_model.return_value = MagicMock()
        
        specialist = ConcreteSpecialist(agent_id="test-specialist", model_tier="mundane")
        assert specialist.agent_id == "test-specialist"
        assert specialist.model is not None
        
        res = specialist.run("move-1", {})
        assert res["result"] == "analyzed"

def test_roi_analyst_agent():
    # This will fail until ROIAnalystAgent is implemented
    try:
        from backend.agents.roi_analyst import ROIAnalystAgent
        
        with patch("backend.inference.InferenceProvider.get_model") as mock_get_model:
            mock_llm = MagicMock()
            mock_get_model.return_value = mock_llm
            mock_llm.invoke.return_value = MagicMock(content="High ROI detected.")
            
            agent = ROIAnalystAgent()
            result = agent.run("move-123", {"spend": 100, "conversions": 5})
            
            assert "attribution" in result
            assert result["attribution"] == "High ROI detected."
            mock_llm.invoke.assert_called_once()
    except (ImportError, AttributeError):
        pytest.fail("ROIAnalystAgent not implemented")

def test_strategic_drift_agent():
    # This will fail until StrategicDriftAgent is implemented
    try:
        from backend.agents.drift_detector import StrategicDriftAgent
        
        with patch("backend.inference.InferenceProvider.get_model") as mock_get_model:
            mock_llm = MagicMock()
            mock_get_model.return_value = mock_llm
            mock_llm.invoke.return_value = MagicMock(content="Drift detected: Tone is too playful.")
            
            agent = StrategicDriftAgent()
            result = agent.run("move-123", {"trace": "playful tone", "brand_kit": "serious"})
            
            assert "drift_report" in result
            assert "Drift detected" in result["drift_report"]
            mock_llm.invoke.assert_called_once()
    except (ImportError, AttributeError):
        pytest.fail("StrategicDriftAgent not implemented")

def test_competitor_intelligence_agent():
    # This will fail until CompetitorIntelligenceAgent is implemented
    try:
        from backend.agents.competitor_intel import CompetitorIntelligenceAgent
        
        with patch("backend.inference.InferenceProvider.get_model") as mock_get_model:
            mock_llm = MagicMock()
            mock_get_model.return_value = mock_llm
            mock_llm.invoke.return_value = MagicMock(content="Competitor X lowered prices.")
            
            agent = CompetitorIntelligenceAgent()
            result = agent.run("move-123", {"telemetry_data": [{"action": "scrape", "res": "ok"}]})
            
            assert "competitor_insights" in result
            assert "Competitor X" in result["competitor_insights"]
            mock_llm.invoke.assert_called_once()
    except (ImportError, AttributeError):
        pytest.fail("CompetitorIntelligenceAgent not implemented")
