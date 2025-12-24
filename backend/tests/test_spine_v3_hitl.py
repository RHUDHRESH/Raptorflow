import pytest

from backend.graphs.spine_v3 import cognitive_spine_v3
from backend.models.cognitive import AgentMessage, CognitiveStatus


@pytest.mark.asyncio
async def test_spine_v3_hitl_interruption():
    """
    Phase 28: Verify that the graph interrupts before the audit node.
    """
    thread_id = "hitl-test-thread"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "tenant_id": "test-tenant",
        "raw_prompt": "HITL test",
        "messages": [],
        "status": CognitiveStatus.PLANNING,
        "quality_score": 1.0,
        "reflection_log": [
            {"init": True},
            {"step": 2},
        ],  # Force audit status in execute
    }

    # 1. Run until interrupt
    await cognitive_spine_v3.ainvoke(initial_state, config)

    # 2. Check state - should be stopped at 'audit'
    state = await cognitive_spine_v3.aget_state(config)
    assert state.next[0] == "audit"
    assert state.values["status"] == CognitiveStatus.AUDITING

    # 3. Resume by providing None as input
    await cognitive_spine_v3.ainvoke(None, config)

    # 4. Verify completion
    final_state = await cognitive_spine_v3.aget_state(config)
    assert final_state.values["status"] == CognitiveStatus.COMPLETE
    assert any("Audit complete" in m.content for m in final_state.values["messages"])
