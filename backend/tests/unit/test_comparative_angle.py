import pytest
from unittest.mock import AsyncMock, patch
from backend.agents.specialists.comparative_angle_agent import ComparativeAngleGenerator

@pytest.mark.asyncio
async def test_comparative_angle_execution():
    """Test ComparativeAngleGenerator agent execution."""
    agent = ComparativeAngleGenerator()
    
    state = {
        "business_context": {
            "identity": {"company_name": "RaptorFlow"},
            "competitors": ["Hubspot", "Salesforce"]
        },
        "step_data": {
            "market_intelligence": {
                "pain_points": [{"description": "Too complex", "category": "UX"}],
                "discovered_competitors": ["Hubspot", "Salesforce"]
            }
        }
    }
    
    # Mock LLM call
    with patch.object(ComparativeAngleGenerator, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"vantage_point": "Surgical Simplicity", "leverage": "AI-first UX", "competitor_mapping": [{"name": "Hubspot", "hook": "The All-in-One CRM", "gap": "Jack of all trades, master of none", "your_angle": "The specialized AI operator"}]}'
        
        result = await agent.execute(state)
        
        assert "output" in result
        output = result["output"]
        assert "vantage_point" in output
        assert "competitor_mapping" in output
        assert output["competitor_mapping"][0]["name"] == "Hubspot"
