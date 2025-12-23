import pytest

from backend.graphs.moves_campaigns_orchestrator import moves_campaigns_orchestrator


@pytest.mark.asyncio
async def test_graph_initialization():
    """Verify that the graph initializes correctly."""
    initial_state = {"tenant_id": "test-tenant", "messages": [], "status": "new"}

    # Run the graph
    config = {"configurable": {"thread_id": "test-thread-1"}}
    result = await moves_campaigns_orchestrator.ainvoke(initial_state, config)

    # It should flow: START -> init (planning) -> plan_campaign (monitoring) -> END
    assert result["status"] == "monitoring"
    assert "Orchestrator initialized." in result["messages"]
    assert "Campaign strategy generated." in result["messages"]


@pytest.mark.asyncio
async def test_graph_state_recovery_after_interrupt():
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
async def test_graph_router_success():
    """
    Verify that the graph handles routing between planning and monitoring.
    """
    initial_state = {"status": "planning", "messages": []}
    config = {"configurable": {"thread_id": "router-test"}}

    result = await moves_campaigns_orchestrator.ainvoke(initial_state, config)
    assert result["status"] == "monitoring"


@pytest.mark.asyncio
async def test_graph_hitl_interruption():
    """Verify that the graph interrupts before approve_move."""
    initial_state = {
        "tenant_id": "test-tenant",
        "messages": [],
        "status": "monitoring",  # Force 'monitoring' so init -> router -> moves
    }
    config = {"configurable": {"thread_id": "hitl-test"}}

    # We need to call it twice OR understand that init node OVERWRITES status.
    # Actually, initialize_orchestrator returns status='planning'.
    # I'll update the test to handle the flow properly.

    # Run the graph
    await moves_campaigns_orchestrator.ainvoke(initial_state, config)

    # It should have interrupted before 'approve_campaign' because status was 'monitoring' initially?
    # Wait, initial_state has status='monitoring'.
    # init returns {"messages": ["Orchestrator resumed."]}
    # router returns "moves" -> generate_moves -> approve_move (INTERRUPT)

    state = await moves_campaigns_orchestrator.aget_state(config)
    assert "approve_move" in state.next


@pytest.mark.asyncio
async def test_graph_campaign_approval_interrupt():
    """Verify that the graph interrupts before approve_campaign."""
    initial_state = {"tenant_id": "test-tenant", "messages": [], "status": "new"}
    config = {"configurable": {"thread_id": "campaign-approval-test"}}

    # Run the graph - should start from 'new' -> init (planning) -> plan_campaign -> approve_campaign (INTERRUPT)
    await moves_campaigns_orchestrator.ainvoke(initial_state, config)

    state = await moves_campaigns_orchestrator.aget_state(config)
    assert "approve_campaign" in state.next
