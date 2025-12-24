import pytest

from backend.agents.supervisor import HumanInTheLoopNode


@pytest.mark.asyncio
async def test_hitl_interrupt_logic():
    """Test that the HITL node correctly requests approval."""
    node = HumanInTheLoopNode()

    state = {"instructions": "Approve system-wide kill-switch", "messages": []}

    result = await node(state)
    assert result["approval_required"] is True
    assert "Approve" in result["approval_prompt"]
    assert result["status"] == "AWAITING_HUMAN"


@pytest.mark.asyncio
async def test_hitl_process_approval():
    """Test processing a human approval response."""
    node = HumanInTheLoopNode()

    # Simulate state with human response
    state = {"human_response": "YES", "instructions": "Approve system-wide kill-switch"}

    result = await node(state)
    assert result["approved"] is True
    assert result["status"] == "APPROVED"
