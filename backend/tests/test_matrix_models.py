import pytest
from pydantic import ValidationError

from backend.models.telemetry import AgentHealthStatus, SystemState, TelemetryEvent


def test_telemetry_event_valid():
    """Test that a valid TelemetryEvent can be created."""
    data = {
        "event_id": "evt_123",
        "timestamp": "2025-12-23T12:00:00Z",
        "event_type": "inference_start",
        "source": "agent_alpha",
        "payload": {"model": "gemini-2.0-flash", "prompt_len": 150},
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


def test_system_state_valid():
    """Test that a valid SystemState can be created."""
    data = {
        "active_agents": {
            "agent_1": {
                "status": "online",
                "last_heartbeat": "2025-12-23T12:00:00Z",
                "current_task": "researching",
            }
        },
        "system_status": "operational",
        "kill_switch_engaged": False,
    }
    state = SystemState(**data)
    assert state.active_agents["agent_1"].status == AgentHealthStatus.ONLINE
    assert state.kill_switch_engaged is False
