from unittest.mock import AsyncMock, MagicMock

import pytest

from core.serving import ModelServer
from models.telemetry import TelemetryEvent, TelemetryEventType


@pytest.fixture
def mock_matrix():
    mock = MagicMock()
    mock.emit_event = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def model_server(mock_matrix):
    return ModelServer(matrix_service=mock_matrix)


@pytest.mark.asyncio
async def test_log_inference_metadata(model_server, mock_matrix):
    """Test that model server logs inference metadata."""
    metadata = {
        "model": "gemini-2.5-flash",
        "tokens_in": 100,
        "tokens_out": 200,
        "latency_ms": 150.5,
    }
    await model_server.log_inference("agent_1", metadata)

    assert mock_matrix.emit_event.called
    args, _ = mock_matrix.emit_event.call_args
    event = args[0]
    assert event.event_type == TelemetryEventType.INFERENCE_END
    assert event.source == "agent_1"
    assert event.payload["model"] == "gemini-2.5-flash"
