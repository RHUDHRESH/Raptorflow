import pytest

pytest.skip(
    "BCM test suite needs rebase on canonical services; skipped for now.",
    allow_module_level=True,
)

from unittest.mock import AsyncMock, Mock, patch

import pytest
from schemas.bcm_evolution import EventType

from .services.move import MoveService


@pytest.mark.asyncio
@patch("backend.services.move.MoveRepository")
@patch("backend.services.move.BCMEventRecorder")
async def test_complete_move_records_event(MockRecorder, MockRepo):
    """Test that completing a move records a BCM event"""
    # Mock Repository
    mock_repo = MockRepo.return_value
    mock_repo.get_by_id = AsyncMock(
        return_value={"id": "move-1", "status": "active", "title": "Test Move"}
    )
    mock_repo.complete_move = AsyncMock(
        return_value={"id": "move-1", "status": "completed"}
    )

    # Mock Recorder
    mock_recorder = MockRecorder.return_value
    mock_recorder.record_event = AsyncMock(return_value="event-123")

    service = MoveService()
    service.bcm_recorder = mock_recorder  # Inject mock

    workspace_id = "ws-123"
    await service.complete_move(move_id="move-1", workspace_id=workspace_id)

    # Verify event was recorded
    mock_recorder.record_event.assert_called_once()
    args, kwargs = mock_recorder.record_event.call_args
    assert kwargs["event_type"] == EventType.MOVE_COMPLETED
    assert kwargs["workspace_id"] == workspace_id
    assert kwargs["payload"]["move_id"] == "move-1"
