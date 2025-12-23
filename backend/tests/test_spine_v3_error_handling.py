import pytest
from backend.graphs.spine_v3 import cognitive_spine_v3
from backend.models.cognitive import CognitiveStatus, AgentMessage

@pytest.mark.asyncio
async def test_spine_v3_error_recovery():
    """
    Phase 27: Verify that the graph recovers from execution errors by reverting to research.
    """
    initial_state = {
        "tenant_id": "test-tenant",
        "status": CognitiveStatus.EXECUTING,
        "error": "Tool timeout",
        "messages": [],
        "raw_prompt": "Recover from error"
    }
    
    config = {"configurable": {"thread_id": "test-thread-error"}}
    
    final_state = await cognitive_spine_v3.ainvoke(initial_state, config)
    print(f"DEBUG MESSAGES: {[m.content for m in final_state['messages']]}")
    
    assert final_state["status"] == CognitiveStatus.COMPLETE
    msgs = [m.content for m in final_state["messages"]]
    assert any("RECOVERY" in m for m in msgs)
    assert any("Reverting to research" in m for m in msgs)