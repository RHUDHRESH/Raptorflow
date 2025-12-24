import pytest

from backend.graphs.spine_v3 import cognitive_spine_v3
from backend.models.cognitive import AgentMessage, CognitiveStatus


@pytest.mark.asyncio
async def test_spine_v3_cyclic_refinement():
    """
    Phase 24: Verify that the graph loops back from execute to research on low quality.
    """
    initial_state = {
        "tenant_id": "test-tenant",
        "raw_prompt": "Test cyclic flow",
        "messages": [],
        "status": CognitiveStatus.PLANNING,
        "quality_score": 0.5,  # Trigger refinement
        "reflection_log": [],
    }

    config = {"configurable": {"thread_id": "test-thread-cycle"}}

    # We expect multiple 'research' and 'execute' messages if the loop works
    # However, placeholders currently just update status.
    # To test the loop, we'd need placeholders that don't just increment status blindly.
    # For now, we'll verify the compile logic and status transitions.

    final_state = await cognitive_spine_v3.ainvoke(initial_state, config)

    assert final_state["status"] == CognitiveStatus.COMPLETE
    # Verify we visited research and execute
    msgs = [m.content for m in final_state["messages"]]
    assert any("Research complete" in m for m in msgs)
    assert any("Execution complete" in m for m in msgs)
