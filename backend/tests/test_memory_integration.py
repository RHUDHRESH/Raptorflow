import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.graphs.moves_campaigns_orchestrator import moves_campaigns_orchestrator

@pytest.fixture
def mock_memories():
    with patch("backend.graphs.moves_campaigns_orchestrator.SemanticMemory", new_callable=MagicMock) as mock_semantic, \
         patch("backend.graphs.moves_campaigns_orchestrator.LongTermMemory", new_callable=MagicMock) as mock_ltm:
        
        sem_instance = mock_semantic.return_value
        sem_instance.search = AsyncMock(return_value=[{"content": "mocked"}])
        
        ltm_instance = mock_ltm.return_value
        ltm_instance.log_decision = AsyncMock()
        
        yield sem_instance, ltm_instance

@pytest.mark.asyncio
async def test_memory_updater_integration(mock_memories):
    _, mock_ltm = mock_memories
    config = {"configurable": {"thread_id": "mem-update-test"}}
    
    # 1. Initialize and reach approve_campaign interrupt
    await moves_campaigns_orchestrator.ainvoke({
        "tenant_id": "test-tenant",
        "status": "new",
        "messages": []
    }, config)
    
    # 2. Resume (this should trigger memory_updater after approval logic)
    await moves_campaigns_orchestrator.ainvoke(None, config)
    
    # Verify log_decision was called
    mock_ltm.log_decision.assert_called()
