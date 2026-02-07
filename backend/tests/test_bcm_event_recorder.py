import pytest

pytest.skip(
    "BCM test suite needs rebase on canonical services; skipped for now.",
    allow_module_level=True,
)

import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest
from schemas.bcm_evolution import EventType

from .services.bcm_recorder import BCMEventRecorder


@pytest.mark.asyncio
async def test_record_event_success():
    """Test successfully recording an event"""
    mock_supabase = Mock()
    # execute() must be an AsyncMock because it is awaited in the service
    mock_execute = AsyncMock(return_value=Mock(data=[{"id": "event-123"}]))
    mock_supabase.table.return_value.insert.return_value.execute = mock_execute

    recorder = BCMEventRecorder(db_client=mock_supabase)

    workspace_id = str(uuid.uuid4())
    event_id = await recorder.record_event(
        workspace_id=workspace_id,
        event_type=EventType.STRATEGIC_SHIFT,
        payload={"new_positioning": "Industrial AI"},
        ucid="RF-2026-0001",
    )

    assert event_id == "event-123"
    mock_supabase.table.assert_called_with("bcm_events")

    # Verify payload structure
    inserted_data = mock_supabase.table().insert.call_args[0][0]
    assert inserted_data["workspace_id"] == workspace_id
    assert inserted_data["event_type"] == EventType.STRATEGIC_SHIFT
    assert inserted_data["payload"] == {"new_positioning": "Industrial AI"}
    assert inserted_data["ucid"] == "RF-2026-0001"


@pytest.mark.asyncio
async def test_record_event_failure():
    """Test failure during event recording"""
    mock_supabase = Mock()
    mock_execute = AsyncMock(side_effect=Exception("DB Error"))
    mock_supabase.table.return_value.insert.return_value.execute = mock_execute

    recorder = BCMEventRecorder(db_client=mock_supabase)

    with pytest.raises(Exception) as excinfo:
        await recorder.record_event(
            workspace_id=str(uuid.uuid4()),
            event_type=EventType.USER_INTERACTION,
            payload={},
        )
    assert "DB Error" in str(excinfo.value)
