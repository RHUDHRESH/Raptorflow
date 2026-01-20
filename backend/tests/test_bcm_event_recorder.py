import pytest
import uuid
from unittest.mock import AsyncMock, patch
from backend.services.bcm_recorder import BCMEventRecorder
from backend.schemas.bcm_evolution import EventType

@pytest.mark.asyncio
async def test_record_event_success():
    """Test successfully recording an event"""
    mock_supabase = AsyncMock()
    mock_supabase.table.return_value.insert.return_value.execute.return_value = AsyncMock(data=[{"id": "event-123"}])
    
    recorder = BCMEventRecorder(db_client=mock_supabase)
    
    workspace_id = str(uuid.uuid4())
    event_id = await recorder.record_event(
        workspace_id=workspace_id,
        event_type=EventType.STRATEGIC_SHIFT,
        payload={"new_positioning": "Industrial AI"},
        ucid="RF-2026-0001"
    )
    
    assert event_id == "event-123"
    mock_supabase.table.assert_called_with("bcm_events")
    mock_supabase.table().insert.assert_called_once()
    
    # Verify payload structure
    args, kwargs = mock_supabase.table().insert.call_args
    inserted_data = args[0]
    assert inserted_data["workspace_id"] == workspace_id
    assert inserted_data["event_type"] == EventType.STRATEGIC_SHIFT
    assert inserted_data["payload"] == {"new_positioning": "Industrial AI"}
    assert inserted_data["ucid"] == "RF-2026-0001"

@pytest.mark.asyncio
async def test_record_event_failure():
    """Test failure during event recording"""
    mock_supabase = AsyncMock()
    mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("DB Error")
    
    recorder = BCMEventRecorder(db_client=mock_supabase)
    
    with pytest.raises(Exception) as excinfo:
        await recorder.record_event(
            workspace_id=str(uuid.uuid4()),
            event_type=EventType.USER_INTERACTION,
            payload={}
        )
    assert "DB Error" in str(excinfo.value)
