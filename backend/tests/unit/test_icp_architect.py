import pytest
from unittest.mock import AsyncMock, patch
from backend.agents.specialists.icp_architect import ICPArchitect

@pytest.mark.asyncio
async def test_icp_architect_execution():
    """Test ICPArchitect agent execution."""
    agent = ICPArchitect()
    
    state = {
        "business_context": {
            "identity": {"company_name": "RaptorFlow"},
            "positioning": {"winner": "The Surgical Operator"}
        },
        "step_data": {
            "market_intelligence": {"pain_points": []},
            "focus_sacrifice": {"focus_areas": ["Founders"]}
        }
    }
    
    # Mock LLM call
    with patch.object(ICPArchitect, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"profiles": [{"name": "The High-Growth Founder", "who_they_want_to_become": "The Unshakeable Visionary", "sophistication_level": 4, "behavioral_triggers": ["Competitive envy"]}], "primary_icp": "The High-Growth Founder"}'
        
        result = await agent.execute(state)
        
        assert "output" in result
        output = result["output"]
        assert "profiles" in output
        assert output["profiles"][0]["who_they_want_to_become"] == "The Unshakeable Visionary"
        assert output["profiles"][0]["sophistication_level"] == 4
