import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.graphs.moves_campaigns_orchestrator import moves_campaigns_orchestrator

@pytest.fixture
def mock_strategic_agents():
    with patch("backend.graphs.moves_campaigns_orchestrator.SemanticMemory", new_callable=MagicMock) as mock_semantic, \
         patch("backend.graphs.moves_campaigns_orchestrator.LongTermMemory", new_callable=MagicMock) as mock_ltm, \
         patch("backend.graphs.moves_campaigns_orchestrator.KPIDefiner", new_callable=MagicMock) as mock_kpi, \
         patch("backend.graphs.moves_campaigns_orchestrator.InferenceProvider", new_callable=MagicMock) as mock_inf:
        
        sem_instance = mock_semantic.return_value
        sem_instance.search = AsyncMock(return_value=[{"content": "mocked"}])
        
        ltm_instance = mock_ltm.return_value
        ltm_instance.log_decision = AsyncMock()
        
        kpi_instance = mock_kpi.return_value
        kpi_instance.side_effect = AsyncMock(return_value={"kpi_targets": {"leads": 100}})
        
        # Mock get_model to return something simple
        mock_inf.get_model.return_value = MagicMock()
        
        yield sem_instance, ltm_instance, kpi_instance

@pytest.mark.asyncio
async def test_kpi_setter_node_integration(mock_strategic_agents):
    _, _, mock_kpi = mock_strategic_agents
    config = {"configurable": {"thread_id": "kpi-test"}}
    
    # Run the graph until the point where KPI setter should trigger
    # In our proposed flow: approve_campaign -> memory_updater -> kpi_setter
    
    # 1. Start and reach first interrupt
    await moves_campaigns_orchestrator.ainvoke({
        "tenant_id": "test-tenant",
        "status": "new",
        "messages": []
    }, config)
    
    # 2. Resume (this should trigger memory_updater and then kpi_setter)
    await moves_campaigns_orchestrator.ainvoke(None, config)
    
    # Verify kpi_setter was called
    # We might need to check the state to see if kpi_targets is populated
    state = await moves_campaigns_orchestrator.aget_state(config)
    assert "kpi_targets" in state.values
    assert state.values["kpi_targets"]["leads"] == 100
