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
