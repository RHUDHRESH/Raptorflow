import pytest
from unittest.mock import MagicMock
from backend.services.matrix_service import MatrixService
from backend.models.telemetry import TelemetryEvent, SystemState

@pytest.fixture
def matrix_service():
    return MatrixService()

def test_get_system_overview(matrix_service):
    """Test retrieving system overview state."""
    overview = matrix_service.get_system_overview()
    assert isinstance(overview, SystemState)
    assert overview.system_status == "operational"

@pytest.mark.asyncio
async def test_initialize_telemetry_stream(matrix_service):
    """Test initializing the telemetry stream."""
    # This will likely involve Upstash/Redis, so we'll mock or test interface
    success = await matrix_service.initialize_telemetry_stream()
    assert success is True

@pytest.mark.asyncio
async def test_capture_agent_heartbeat(matrix_service):
    """Test capturing an agent heartbeat."""
    success = await matrix_service.capture_agent_heartbeat("agent_alpha", "working")
    assert success is True
    overview = matrix_service.get_system_overview()
    assert "agent_alpha" in overview.active_agents
    assert overview.active_agents["agent_alpha"].current_task == "working"

@pytest.mark.asyncio
async def test_halt_system(matrix_service):
    """Test engaging the global kill-switch."""
    success = await matrix_service.halt_system()
    assert success is True
    overview = matrix_service.get_system_overview()
    assert overview.kill_switch_engaged is True
    assert overview.system_status == "halted"
