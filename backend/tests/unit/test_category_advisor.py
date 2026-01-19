import pytest
from unittest.mock import AsyncMock, patch
from backend.agents.specialists.category_advisor import CategoryAdvisor

@pytest.mark.asyncio
async def test_category_advisor_execution():
    """Test CategoryAdvisor agent execution."""
    agent = CategoryAdvisor()
    
    state = {
        "business_context": {
            "identity": {
                "company_name": "RaptorFlow",
                "product_description": "AI agent swarm for automated marketing."
            }
        },
        "step_data": {
            "comparative_angle": {
                "vantage_point": "Surgical Simplicity"
            }
        }
    }
    
    # Mock LLM call
    with patch.object(CategoryAdvisor, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"safe_path": {"category_name": "Marketing Automation", "pros": ["Demand"], "cons": ["Crowded"]}, "clever_path": {"category_name": "Autonomous Growth Engine", "pros": ["Modern"], "cons": ["Education"]}, "bold_path": {"category_name": "Founder OS", "pros": ["Owner"], "cons": ["Extreme effort"]}, "recommended_path": "clever"}'
        
        result = await agent.execute(state)
        
        assert "output" in result
        output = result["output"]
        assert "safe_path" in output
        assert "clever_path" in output
        assert "bold_path" in output
        assert output["recommended_path"] == "clever"
