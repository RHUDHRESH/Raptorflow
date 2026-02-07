from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from graphs.cognitive_spine import cognitive_spine
from models.cognitive import CognitiveStatus


@pytest.fixture
def mock_db():
    with patch(
        "backend.graphs.cognitive_spine.get_pool", new_callable=MagicMock
    ), patch("backend.graphs.cognitive_spine.SupabaseSaver", new_callable=MagicMock):
        yield


@pytest.mark.asyncio
async def test_cognitive_spine_initialization(mock_db):
    """
    Task 30: Verify that the cognitive spine initializes and routes correctly.
    """
    initial_state = {
        "tenant_id": "test-tenant",
        "raw_prompt": "Build a LinkedIn strategy",
        "messages": [],
        "status": CognitiveStatus.IDLE,
    }

    config = {"configurable": {"thread_id": "test-thread"}}

    # Run the graph
    result = await cognitive_spine.ainvoke(initial_state, config)

    # Verify transition (it should stop at the first interrupt: approve_assets)
    state = await cognitive_spine.aget_state(config)
    # status was set to AUDITING by creator_placeholder before reaching approve_assets
    assert state.values["status"] == CognitiveStatus.AUDITING
    assert "approve_assets" in state.next


@pytest.mark.asyncio
async def test_cognitive_spine_hitl_interrupt(mock_db):
    """
    Phase 28: Verify HITL interruption before asset approval.
    """
    initial_state = {
        "tenant_id": "test-tenant",
        "raw_prompt": "test",
        "status": CognitiveStatus.EXECUTING,  # Force flow towards approval
    }

    config = {"configurable": {"thread_id": "hitl-thread"}}

    # This should run until 'approve_assets'
    await cognitive_spine.ainvoke(initial_state, config)

    state = await cognitive_spine.aget_state(config)
    assert "approve_assets" in state.next
