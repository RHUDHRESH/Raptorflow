from unittest.mock import AsyncMock, Mock, patch

import pytest
from schemas.bcm_evolution import EventType

from .services.bcm_service import BCMService


@pytest.mark.asyncio
@patch("backend.services.bcm_service.BCMProjector")
@patch("backend.services.bcm_service.UniversalAgent")
@patch("backend.services.bcm_service.BCMEventRecorder")
async def test_refine_context_loop(MockRecorder, MockAgent, MockProjector):
    """Test the full BCM refinement loop"""
    # Mock database client for the recorder
    mock_db = Mock()
    mock_execute = AsyncMock(return_value=Mock(data=[]))
    mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute = (
        mock_execute
    )

    # Mock Projector
    mock_projector = MockProjector.return_value
    mock_projector.get_latest_state = AsyncMock(
        return_value=Mock(model_dump_json=lambda: "{}")
    )

    # Mock Agent
    mock_agent = MockAgent.return_value
    mock_agent.run_step = AsyncMock(
        return_value={
            "success": True,
            "output": '{"evolved_insights": ["Tested new niche"], "evolution_index": 2.5}',
        }
    )

    # Mock Recorder
    mock_recorder = MockRecorder.return_value
    mock_recorder.db = mock_db  # Ensure it has the mocked db
    mock_recorder.record_event = AsyncMock(return_value="event-refine-1")

    service = BCMService()
    service.projector = mock_projector
    service.agent = mock_agent
    service.recorder = mock_recorder

    await service.refine_context(workspace_id="ws-123", ucid="RF-2026-0001")

    # Verify sequence
    mock_projector.get_latest_state.assert_called_once()
    mock_agent.run_step.assert_called_once()
    mock_recorder.record_event.assert_called_once()

    args, kwargs = mock_recorder.record_event.call_args
    assert kwargs["event_type"] == EventType.AI_REFINEMENT
    assert "Tested new niche" in kwargs["payload"]["evolved_insights"]
