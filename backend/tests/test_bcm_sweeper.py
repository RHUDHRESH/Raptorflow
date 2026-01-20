import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from backend.services.bcm_sweeper import BCMSweeper
from backend.schemas.bcm_evolution import EventType

@pytest.mark.asyncio
@patch("backend.services.bcm_sweeper.UniversalAgent")
async def test_semantic_compression_loop(MockAgent):
    """Test that the sweeper compresses events into a checkpoint"""
    mock_db = Mock()
    # Mock finding old events
    mock_events = [
        {"id": "1", "event_type": "USER_INTERACTION", "payload": {"query": "test1"}},
        {"id": "2", "event_type": "USER_INTERACTION", "payload": {"query": "test2"}},
    ]
    # Mock chain: table().select().eq().eq().order().limit().execute()
    mock_execute_select = AsyncMock(return_value=Mock(data=mock_events))
    mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.limit.return_value.execute = mock_execute_select
    
    # Mock Agent compression
    mock_agent = MockAgent.return_value
    mock_agent.run_step = AsyncMock(return_value={
        "success": True,
        "output": '{"summary": "User searched for tests", "compressed_event_ids": ["1", "2"]}'
    })
    
    # Mock recording the checkpoint: table().insert().execute()
    mock_execute_insert = AsyncMock(return_value=Mock(data=[{"id": "checkpoint-1"}]))
    mock_db.table.return_value.insert.return_value.execute = mock_execute_insert
    
    # Mock deleting old events: table().delete().in_().execute()
    mock_execute_delete = AsyncMock()
    mock_db.table.return_value.delete.return_value.in_.return_value.execute = mock_execute_delete
    
    sweeper = BCMSweeper(db_client=mock_db)
    sweeper.sweep_threshold = 1 # Force sweep for test
    sweeper.agent = mock_agent
    
    result = await sweeper.compress_events(workspace_id="ws-123", ucid="RF-2026-0001")
    
    assert result["success"] is True
    assert result["checkpoint_id"] == "checkpoint-1"
    mock_agent.run_step.assert_called_once()
    # Verify deletion was called for compressed IDs
    mock_db.table.return_value.delete.assert_called()
