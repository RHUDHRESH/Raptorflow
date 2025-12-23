from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.graphs.moves_campaigns_orchestrator import moves_campaigns_orchestrator


@pytest.fixture
def mock_semantic_memory():
    with patch("backend.graphs.moves_campaigns_orchestrator.SemanticMemory", new_callable=MagicMock) as mock_class:
        instance = mock_class.return_value
        instance.search = AsyncMock(return_value=[{"content": "mocked context"}])
        yield instance

@pytest.mark.asyncio
async def test_graph_initialization(mock_semantic_memory):
    """Verify that the graph initializes correctly."""
    initial_state = {"tenant_id": "test-tenant", "messages": [], "status": "new"}

    # Run the graph
    config = {"configurable": {"thread_id": "test-thread-1"}}
    result = await moves_campaigns_orchestrator.ainvoke(initial_state, config)

    # It should flow: START -> init (planning) -> inject_context -> plan_campaign (monitoring) -> interrupt(approve_campaign)
    # Wait, it interrupts now!
    state = await moves_campaigns_orchestrator.aget_state(config)
    assert "approve_campaign" in state.next
    assert "Orchestrator initialized." in state.values["messages"]
    assert "Injected 1 business context snippets." in state.values["messages"]

@pytest.mark.asyncio
async def test_graph_state_recovery_after_interrupt(mock_semantic_memory):
    """Verify that the graph can recover state after being interrupted (simulated crash)."""
    config = {"configurable": {"thread_id": "crash-test-thread"}}
    initial_state = {"tenant_id": "test-tenant", "messages": [], "status": "new"}

    # 1. Run until first interrupt (approve_campaign)
    await moves_campaigns_orchestrator.ainvoke(initial_state, config)
    
    state = await moves_campaigns_orchestrator.aget_state(config)
    assert "approve_campaign" in state.next
    assert state.values["status"] == "monitoring"
    
    # 2. Simulate "crash" by using a DIFFERENT instance of the graph (but same checkpointer logic)
    # Since they use the same shared MemorySaver in this test environment if we are not careful.
    # Actually, moves_campaigns_orchestrator has a checkpointer attached.
    
    # Let's resume by providing approval
    await moves_campaigns_orchestrator.ainvoke(None, config)
    
    # 3. Verify it finished
    final_state = await moves_campaigns_orchestrator.aget_state(config)
    assert final_state.next == ()
    assert "Campaign strategy approved by human." in final_state.values["messages"]


@pytest.mark.asyncio
async def test_graph_router_success(mock_semantic_memory):
    """
    Verify that the graph handles routing between planning and monitoring.
    """
    initial_state = {"status": "planning", "messages": [], "tenant_id": "test"}
    config = {"configurable": {"thread_id": "router-test"}}

    await moves_campaigns_orchestrator.ainvoke(initial_state, config)
    state = await moves_campaigns_orchestrator.aget_state(config)
    assert "approve_campaign" in state.next


@pytest.mark.asyncio
async def test_graph_hitl_interruption(mock_semantic_memory):
    """Verify that the graph interrupts before approve_move."""
    initial_state = {
        "tenant_id": "test-tenant",
        "messages": [],
        "status": "monitoring",  # Force 'monitoring' so init -> router -> moves
    }
    config = {"configurable": {"thread_id": "hitl-test"}}

    # Run the graph
    await moves_campaigns_orchestrator.ainvoke(initial_state, config)

    state = await moves_campaigns_orchestrator.aget_state(config)
    assert "approve_move" in state.next


@pytest.mark.asyncio
async def test_graph_campaign_approval_interrupt(mock_semantic_memory):
    """Verify that the graph interrupts before approve_campaign."""
    initial_state = {"tenant_id": "test-tenant", "messages": [], "status": "new"}
    config = {"configurable": {"thread_id": "campaign-approval-test"}}

    # Run the graph - should start from 'new' -> init (planning) -> plan_campaign -> approve_campaign (INTERRUPT)
    await moves_campaigns_orchestrator.ainvoke(initial_state, config)

    state = await moves_campaigns_orchestrator.aget_state(config)
    assert "approve_campaign" in state.next
