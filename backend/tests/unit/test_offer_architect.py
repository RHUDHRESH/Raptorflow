import pytest
from unittest.mock import AsyncMock, patch
from backend.agents.specialists.offer_architect import OfferArchitect

@pytest.mark.asyncio
async def test_offer_architect_execution():
    """Test OfferArchitect agent execution with realistic state."""
    agent = OfferArchitect()
    
    state = {
        "business_context": {
            "identity": {
                "company_name": "TestCorp",
                "product_name": "TestProduct"
            },
            "offer": {
                "current_price": "$100/mo",
                "guarantee": "30-day money back"
            }
        },
        "step_data": {
            "truth_sheet": {
                "verified_facts": [
                    {"category": "offer", "value": "B2B SaaS"}
                ]
            }
        }
    }
    
    # Mock LLM call
    with patch.object(OfferArchitect, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"revenue_model": "SaaS Subscription", "pricing_logic": "Value-based", "risk_reversal": {"score": 0.8, "feedback": "Strong guarantee"}, "outcome_mapping": []}'
        
        result = await agent.execute(state)
        
        assert "output" in result
        output = result["output"]
        assert output["revenue_model"] == "SaaS Subscription"
        assert "risk_reversal" in output
        assert output["risk_reversal"]["score"] == 0.8

@pytest.mark.asyncio
async def test_financial_calculations():
    """Test financial model calculations (Recurring vs One-time)."""
    agent = OfferArchitect()
    
    # This might be a helper method or part of the execute logic
    # For now, let's assume it's part of the intelligence
    # We want to ensure it handles different models correctly
    
    res_recurring = agent.calculate_ltv("subscription", 100, 12)
    assert res_recurring == 1200
    
    res_one_time = agent.calculate_ltv("one_time", 500)
    assert res_one_time == 500
