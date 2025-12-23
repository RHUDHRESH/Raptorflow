import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from backend.agents.specialists.value_proposition import ValuePropositionAgent, ValuePropOutput, FeatureBenefitMap
from backend.models.cognitive import AgentMessage

@pytest.mark.asyncio
async def test_value_proposition_logic():
    """
    Phase 46: Verify that the ValuePropositionAgent maps UVPs correctly.
    """
    expected_vp = ValuePropOutput(
        core_uvp="Precision strategy for founders.",
        feature_map=[FeatureBenefitMap(feature="AI Graph", pain_killer="Stops chaos", gain_creator="Clarity")],
        emotional_hook="Control your destiny."
    )
    
    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = expected_vp
    
    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm
        
        agent = ValuePropositionAgent()
        state = {
            "tenant_id": "test-tenant",
            "messages": [],
            "raw_prompt": "Map our value prop."
        }
        
        result = await agent(state)
        
        assert result["last_agent"] == "ValuePropDesigner"
        assert "Precision strategy" in result["messages"][0].content
