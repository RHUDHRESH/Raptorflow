import pytest
from unittest.mock import AsyncMock, patch
from backend.agents.specialists.soundbites_generator import SoundbitesGenerator

@pytest.mark.asyncio
async def test_soundbites_execution():
    """Test SoundbitesGenerator agent execution."""
    agent = SoundbitesGenerator()
    
    state = {
        "business_context": {
            "identity": {"company_name": "RaptorFlow"},
            "positioning": {"winner": "The Surgical Operator"}
        }
    }
    
    # Mock LLM call
    with patch.object(SoundbitesGenerator, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"library": [{"type": "PAM", "content": "Problem: Noise. Agitation: It kills speed. Mechanism: Surgical AI."}], "atomic_units": ["Pure Speed", "No Noise"], "improvement_loop": "Improved clarity by 20%."}'
        
        result = await agent.execute(state)
        
        assert "output" in result
        output = result["output"]
        assert "library" in output
        assert "atomic_units" in output
        assert "PAM" in output["library"][0]["type"]
