import pytest
from unittest.mock import AsyncMock, patch
from backend.agents.specialists.neuroscience_copywriter import NeuroscienceCopywriter

@pytest.mark.asyncio
async def test_neuroscience_copywriter_execution():
    """Test NeuroscienceCopywriter agent execution."""
    agent = NeuroscienceCopywriter()
    
    state = {
        "business_context": {
            "identity": {"company_name": "RaptorFlow"},
            "positioning": {"winner": "The Surgical Operator"}
        }
    }
    
    # Mock LLM call
    with patch.object(NeuroscienceCopywriter, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"manifesto": "The era of complex marketing is over...", "limbic_score": 0.92, "compliance": {"limbic": true, "pattern": true, "simplicity": true, "social_proof": true, "scarcity": true, "contrast": true}, "headlines": ["Surgical AI", "End Complexity"]}'
        
        result = await agent.execute(state)
        
        assert "output" in result
        output = result["output"]
        assert "manifesto" in output
        assert output["limbic_score"] > 0.8
        assert output["compliance"]["limbic"] is True
