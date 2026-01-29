import pytest
from unittest.mock import Mock, AsyncMock, patch
from .services.telemetry import ReasoningTelemetry
from schemas.bcm_evolution import EventType


@pytest.mark.asyncio
@patch("backend.services.telemetry.get_supabase_client")
@patch("backend.services.telemetry.BCMEventRecorder")
async def test_log_reasoning_records_event(MockRecorder, MockSupabase):
    """Test that logging reasoning also records a BCM event"""
    mock_db = Mock()
    mock_execute = AsyncMock(return_value=Mock(data=[{"id": "log-1"}]))
    mock_db.table.return_value.insert.return_value.execute = mock_execute
    MockSupabase.return_value = mock_db

    mock_recorder = MockRecorder.return_value
    mock_recorder.record_event = AsyncMock(return_value="event-123")

    telemetry = ReasoningTelemetry()
    telemetry.bcm_recorder = mock_recorder

    workspace_id = "ws-123"
    await telemetry.log_reasoning(
        workspace_id=workspace_id,
        agent_name="TestAgent",
        task_id="task-1",
        trace={"thought": "thinking..."},
    )

    # Verify BCM event was recorded
    mock_recorder.record_event.assert_called_once()
    args, kwargs = mock_recorder.record_event.call_args
    assert kwargs["event_type"] == EventType.USER_INTERACTION
    assert kwargs["workspace_id"] == workspace_id
    assert kwargs["payload"]["agent_name"] == "TestAgent"
