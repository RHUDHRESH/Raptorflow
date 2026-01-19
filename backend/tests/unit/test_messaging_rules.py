import pytest
from unittest.mock import AsyncMock, patch
from backend.agents.specialists.messaging_rules_engine import MessagingRulesEngine

@pytest.mark.asyncio
async def test_messaging_rules_execution():
    """Test MessagingRulesEngine agent execution."""
    agent = MessagingRulesEngine()
    
    state = {
        "business_context": {
            "identity": {"company_name": "RaptorFlow"},
            "positioning": {"winner": "The Surgical Operator"}
        }
    }
    
    # Mock LLM call
    with patch.object(MessagingRulesEngine, "_call_llm", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"rules": [{"type": "voice", "rule": "Quiet Luxury", "do": "Elegant brevity", "dont": "Screaming sales copy"}], "forbidden_words": ["synergy", "paradigm shift"], "anti_patterns": ["Excessive emojis"]}'
        
        result = await agent.execute(state)
        
        assert "output" in result
        output = result["output"]
        assert "rules" in output
        assert "forbidden_words" in output
        assert "synergy" in output["forbidden_words"]
