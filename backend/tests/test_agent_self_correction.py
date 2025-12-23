import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from backend.agents.base import BaseCognitiveAgent
from backend.models.cognitive import CognitiveIntelligenceState

class SkepticAgent(BaseCognitiveAgent):
    def __init__(self, llm):
        super().__init__(
            name="Skeptic",
            role="critic",
            system_prompt="Test",
            model_tier="driver"
        )
        self.llm = llm

@pytest.mark.asyncio
async def test_agent_self_correction_flow():
    """
    Phase 37: Verify self-correction loop (Critique -> Refine).
    """
    mock_llm = AsyncMock()
    # 1st call: Critique, 2nd call: Refine
    mock_llm.ainvoke.side_effect = [
        MagicMock(content="Too short."),
        MagicMock(content="Longer polished content.")
    ]
    
    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_inference.get_model.return_value = mock_llm
        
        agent = SkepticAgent(mock_llm)
        state: CognitiveIntelligenceState = {"tenant_id": "test"}
        
        final_content = await agent.self_correct("Short content", state)
        
        assert final_content == "Longer polished content."
        assert mock_llm.ainvoke.call_count == 2
