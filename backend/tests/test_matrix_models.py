import pytest
from pydantic import ValidationError
from backend.models.telemetry import TelemetryEvent


def test_telemetry_event_valid():
    """Test that a valid TelemetryEvent can be created."""
    data = {
        "event_id": "evt_123",
        "timestamp": "2025-12-23T12:00:00Z",
        "event_type": "inference_start",
        "source": "agent_alpha",
        "payload": {"model": "gemini-1.5-pro", "prompt_len": 150},
        "metadata": {"session_id": "sess_456"},
    }
    event = TelemetryEvent(**data)
    assert event.event_id == "evt_123"
    assert event.event_type == "inference_start"


def test_telemetry_event_invalid_type():
    """Test that TelemetryEvent raises error on invalid event_type."""
    data = {
        "event_id": "evt_123",
        "timestamp": "2025-12-23T12:00:00Z",
        "event_type": "INVALID_TYPE",
        "source": "agent_alpha",
        "payload": {},
    }
    with pytest.raises(ValidationError):
        TelemetryEvent(**data)
