import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from backend.agents.specialists.creative_director import CreativeDirectorAgent, CreativeOutput, CreativeAsset
from backend.models.cognitive import CognitiveStatus

@pytest.mark.asyncio
async def test_creative_director_persona_execution():
    """
    Phase 36: Verify creative director persona uses correct instructions and returns structured data.
    """
    mock_runnable = AsyncMock()
    mock_runnable.ainvoke.return_value = CreativeOutput(
        assets=[CreativeAsset(type=\"social\", content=\"SOTA Copy\", visual_direction=\"Minimal\")],
        brand_kit_alignment=0.95,
        rationale=\"Aligned with tokens.\"
    )
    
    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_runnable
        mock_inference.get_model.return_value = mock_llm
        
        agent = CreativeDirectorAgent()
        # Verify system prompt
        assert "World-Class Creative Director" in agent.system_prompt
        
        state = {
            "tenant_id": "test-tenant",
            "messages": [],
            "raw_prompt": "Create a LinkedIn post for RaptorFlow."
        }
        
        result = await agent(state)
        
        assert result["last_agent"] == "CreativeDirector"
        assert "SOTA Copy" in result["messages"][0].content
