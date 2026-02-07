from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from memory.short_term import L1ShortTermMemory
from models.cognitive import AgentSharedState


@pytest.mark.asyncio
async def test_agent_shared_state_persistence():
    """Verify that AgentSharedState can be saved and loaded from L1."""
    mock_l1 = AsyncMock()

    state = AgentSharedState(
        workspace_id="ws_123",
        context_pool={"competitor_pricing": "high", "trending_topics": ["SaaS", "AI"]},
    )

    # Mock store
    with patch("backend.memory.short_term.get_cache", return_value=mock_l1):
        l1 = L1ShortTermMemory()
        await l1.store(
            f"shared_state:{state.workspace_id}", state.model_dump(mode="json")
        )
        mock_l1.set.assert_called_once()

        # Mock retrieve
        # Pydantic v2 model_dump_json() returns a string
        mock_l1.get.return_value = state.model_dump_json()
        raw = await l1.retrieve(f"shared_state:{state.workspace_id}")
        loaded_state = AgentSharedState(**raw)

        assert loaded_state.workspace_id == "ws_123"
        assert loaded_state.context_pool["competitor_pricing"] == "high"
