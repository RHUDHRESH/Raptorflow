from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agents.base import BaseCognitiveAgent
from backend.models.cognitive import CognitiveIntelligenceState


class SkepticAgent(BaseCognitiveAgent):
    def __init__(self, llm):
        super().__init__(
            name="Skeptic", role="critic", system_prompt="Test", model_tier="driver"
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
        MagicMock(content="Longer polished content."),
    ]

    with patch("backend.agents.base.InferenceProvider") as mock_inference:
        mock_inference.get_model.return_value = mock_llm

        agent = SkepticAgent(mock_llm)
        state: CognitiveIntelligenceState = {"tenant_id": "test"}

        final_content = await agent.self_correct("Short content", state)

        assert final_content == "Longer polished content."
        assert mock_llm.ainvoke.call_count == 2


@pytest.mark.asyncio
async def test_agent_self_correction_with_peer_critiques():
    """
    Phase 37: Verify self-correction uses peer critiques when enabled.
    """
    mock_llm = AsyncMock()
    mock_llm.ainvoke.side_effect = [
        MagicMock(content="Needs more depth."),
        MagicMock(content="Expanded polished content."),
    ]

    with patch("backend.agents.base.InferenceProvider") as mock_inference, patch(
        "backend.agents.base.PeerReviewMemory"
    ) as mock_peer_memory:
        mock_inference.get_model.return_value = mock_llm
        mock_peer_instance = MagicMock()
        mock_peer_instance.get_recent_critiques = AsyncMock(
            return_value=[{"reviewer": "Peer A", "critique": "Add more evidence."}]
        )
        mock_peer_memory.return_value = mock_peer_instance

        agent = SkepticAgent(mock_llm)
        state: CognitiveIntelligenceState = {"tenant_id": "test", "workspace_id": "ws1"}

        final_content = await agent.self_correct(
            "Short content", state, use_peer_critiques=True
        )

        first_call = mock_llm.ainvoke.call_args_list[0][0][0][0].content
        assert "Peer A" in first_call
        assert final_content == "Expanded polished content."
