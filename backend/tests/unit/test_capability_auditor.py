import pytest
from unittest.mock import AsyncMock, patch
from backend.agents.specialists.capability_rating_agent import CapabilityRatingEngine

@pytest.mark.asyncio
async def test_capability_auditor_execution():
    """Test CapabilityAuditor (RatingEngine) agent execution."""
    agent = CapabilityRatingEngine()
    
    state = {
        "business_context": {
            "identity": {"company_name": "RaptorFlow"},
            "capabilities": [
                {"name": "Agent Swarm Orchestration", "claim": "First of its kind"}
            ]
        },
        "step_data": {
            "comparative_angle": {"vantage_point": "Surgical Simplicity"}
        }
    }
    
    # Mock LLM call
    with patch.object(CapabilityRatingEngine, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"ratings": [{"capability": "Agent Swarm", "tier": 4, "status": "Unique", "verification_query": "reddit AI agent swarm orchestration competitors"}], "gap_analysis": "No direct rival for swarm logic."}'
        
        # Mock tool call for verification
        with patch.object(CapabilityRatingEngine, "use_tool", new_callable=AsyncMock) as mock_tool:
            mock_tool.return_value = {"results": []} # No competitors found means claim holds
            
            result = await agent.execute(state)
            
            assert "output" in result
            output = result["output"]
            assert "ratings" in output
            assert output["ratings"][0]["tier"] == 4
