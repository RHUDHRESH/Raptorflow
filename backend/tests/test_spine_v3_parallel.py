import pytest

from graphs.spine_v3 import cognitive_spine_v3
from models.cognitive import AgentMessage, CognitiveStatus


@pytest.mark.asyncio
async def test_spine_v3_parallel_research():
    """
    Phase 29: Verify parallel execution of research nodes.
    """
    initial_state = {
        "tenant_id": "parallel-test",
        "status": CognitiveStatus.RESEARCHING,
        "messages": [],
        "raw_prompt": "Parallel test",
    }

    config = {"configurable": {"thread_id": "test-parallel"}}

    # Run graph - it should hit market and competitor research then stop at finalize (or audit if we simulated enough)
    final_state = await cognitive_spine_v3.ainvoke(initial_state, config)

    msgs = [m.content for m in final_state["messages"]]
    # Check if both parallel results are in the final messages
    assert any("Market trends analyzed" in m for m in msgs)
    assert any("Competitor pricing extracted" in m for m in msgs)
    assert any("aggregation complete" in m.lower() for m in msgs)
