import pytest
from unittest.mock import AsyncMock, patch
from backend.agents.specialists.buying_process_agent import BuyingProcessArchitect

@pytest.mark.asyncio
async def test_buying_process_execution():
    """Test BuyingProcessArchitect agent execution."""
    agent = BuyingProcessArchitect()
    
    state = {
        "business_context": {
            "identity": {"company_name": "RaptorFlow"}
        },
        "step_data": {
            "icp_profiles": {"profiles": [{"name": "The High-Growth Founder", "sophistication_level": 4}]}
        }
    }
    
    # Mock LLM call
    with patch.object(BuyingProcessArchitect, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"journey": [{"stage": "Unaware", "cognitive_shift": "From status quo to risk awareness", "chasm": false}], "chasm_logic": "Crossing from logic to belief."}'
        
        result = await agent.execute(state)
        
        assert "output" in result
        output = result["output"]
        assert "journey" in output
        assert "chasm_logic" in output
