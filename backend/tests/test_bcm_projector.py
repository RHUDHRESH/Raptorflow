import pytest
from unittest.mock import Mock, AsyncMock
from backend.services.bcm_projector import BCMProjector
from backend.schemas.bcm_evolution import EventType

@pytest.mark.asyncio
async def test_project_state_empty():
    """Test state projection with no events"""
    mock_supabase = Mock()
    mock_execute = AsyncMock(return_value=Mock(data=[]))
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute = mock_execute
    
    projector = BCMProjector(db_client=mock_supabase)
    state = await projector.get_latest_state(workspace_id="ws-123", ucid="RF-2026-0001")
    
    assert state.ucid == "RF-2026-0001"
    assert state.history.total_events == 0

@pytest.mark.asyncio
async def test_project_state_with_events():
    """Test state projection with strategic and move events"""
    events = [
        {
            "event_type": EventType.STRATEGIC_SHIFT,
            "payload": {"identity": {"name": "RaptorFlow Alpha"}}
        },
        {
            "event_type": EventType.MOVE_COMPLETED,
            "payload": {"move_id": "move-1", "title": "Launch Landing Page"}
        }
    ]
    
    mock_supabase = Mock()
    mock_execute = AsyncMock(return_value=Mock(data=events))
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute = mock_execute
    
    projector = BCMProjector(db_client=mock_supabase)
    state = await projector.get_latest_state(workspace_id="ws-123", ucid="RF-2026-0001")
    
    assert state.identity.name == "RaptorFlow Alpha"
    assert state.history.total_events == 2
    assert "Launch Landing Page" in state.history.significant_milestones
