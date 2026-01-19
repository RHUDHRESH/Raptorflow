import pytest
from unittest.mock import AsyncMock, patch
from backend.agents.specialists.message_hierarchy_agent import MessageHierarchyArchitect

@pytest.mark.asyncio
async def test_message_hierarchy_execution():
    """Test MessageHierarchyArchitect agent execution."""
    agent = MessageHierarchyArchitect()
    
    state = {
        "business_context": {
            "identity": {"company_name": "RaptorFlow"},
            "positioning": {"manifesto": "The era of complex marketing is over..."}
        },
        "step_data": {
            "soundbites_library": {"atomic_units": ["Pure Speed"]}
        }
    }
    
    # Mock LLM call
    with patch.object(MessageHierarchyArchitect, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"levels": {"L1": "Manifesto", "L2": "Pillars", "L3": "Features"}, "mapping": [{"headline": "Speed", "body": "We are fast."}], "manifesto_assembly": "Full assembly...", "validation": {"integrity": 0.98, "checks": ["Hierarchy logic holds"]}}'
        
        result = await agent.execute(state)
        
        assert "output" in result
        output = result["output"]
        assert "levels" in output
        assert "mapping" in output
        assert output["validation"]["integrity"] > 0.9
