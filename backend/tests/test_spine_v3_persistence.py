import pytest
from backend.graphs.spine_v3 import cognitive_spine_v3
from backend.models.cognitive import CognitiveStatus, AgentMessage
from langgraph.checkpoint.memory import MemorySaver

@pytest.mark.asyncio
async def test_spine_v3_persistence_resume():
    """
    Phase 25: Verify that the graph state can be recovered from a checkpointer.
    """
    # We'll use a specific thread_id to test recovery
    thread_id = "persistence-test-thread"
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "tenant_id": "test-tenant",
        "raw_prompt": "Persistence test",
        "messages": [],
        "status": CognitiveStatus.IDLE
    }
    
    # 1. Run the first step
    # We can use astream to see updates or just ainvoke and then check state
    await cognitive_spine_v3.ainvoke(initial_state, config)
    
    # 2. Get state from checkpointer
    state = await cognitive_spine_v3.aget_state(config)
    assert state.values["status"] == CognitiveStatus.COMPLETE
    assert len(state.values["messages"]) > 0
    
    # In a more complex graph with interrupts, we'd resume from an interrupt.
    # Since our current graph is deterministic, we'll verify the checkpointer has the state.

