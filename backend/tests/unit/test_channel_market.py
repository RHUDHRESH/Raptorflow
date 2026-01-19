import pytest
from unittest.mock import AsyncMock, patch
from backend.agents.specialists.channel_recommender import ChannelRecommender
from backend.agents.specialists.market_sizer import MarketSizer

@pytest.mark.asyncio
async def test_channel_recommender_execution():
    """Test ChannelRecommender agent execution."""
    agent = ChannelRecommender()
    
    state = {
        "business_context": {"identity": {"company_name": "RaptorFlow"}},
        "step_data": {
            "icp_profiles": {"profiles": [{"name": "The Founder", "preferred_channels": ["Twitter"]}]}
        }
    }
    
    # Mock LLM call
    with patch.object(ChannelRecommender, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"recommendations": [{"channel": "Twitter", "priority": "High", "rationale": "High ICP density"}], "mix": {"organic": 0.7, "paid": 0.3}}'
        
        result = await agent.execute(state)
        
        assert "output" in result
        output = result["output"]
        assert output["recommendations"][0]["channel"] == "Twitter"

@pytest.mark.asyncio
async def test_market_sizer_execution():
    """Test MarketSizer agent execution."""
    agent = MarketSizer()
    
    state = {
        "business_context": {"identity": {"industry": "Marketing Tech"}},
        "step_data": {"icp_profiles": {"profiles": [{"name": "Founders"}]}}
    }
    
    # Mock LLM call
    with patch.object(MarketSizer, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"tam": 5000000000, "sam": 100000000, "som": 10000000, "reality_check": "Market is large but growing."}'
        
        result = await agent.execute(state)
        
        assert "output" in result
        output = result["output"]
        assert output["tam"] == 5000000000
        assert output["som"] == 10000000
