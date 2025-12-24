import pytest

from backend.graphs.spine_v3 import cognitive_spine_v3
from backend.models.cognitive import CognitiveStatus


@pytest.mark.asyncio
async def test_spine_v3_basic_flow():
    """
    Phase 22: Verify basic START -> init -> finalize -> END flow.
    """
    initial_state = {
        "tenant_id": "test-tenant",
        "raw_prompt": "Create a marketing campaign for a new SaaS tool.",
        "messages": [],
        "status": CognitiveStatus.IDLE,
    }

    config = {"configurable": {"thread_id": "test-thread-1"}}

    final_state = await cognitive_spine_v3.ainvoke(initial_state, config)

    assert final_state["status"] == CognitiveStatus.COMPLETE
    # Messages: Init, Plan complete, Finalizing complete
    assert len(final_state["messages"]) >= 3
    assert any("Planning complete" in m.content for m in final_state["messages"])
