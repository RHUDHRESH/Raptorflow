import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock
from backend.services.matrix_service import MatrixService
from backend.models.telemetry import TelemetryEvent, SystemState, AgentHealthStatus, AgentState

@pytest.fixture
def matrix_service(monkeypatch):
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True
    mock_redis.xadd.return_value = "msg_123"
    
    # Mock get_cache to return our mock_redis
    monkeypatch.setattr("backend.services.matrix_service.get_cache", lambda: mock_redis)
    
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
async def test_initialize_telemetry_stream_failure(matrix_service, monkeypatch):
    """Test handling of telemetry stream initialization failure."""
    # Mocking failure if we had an internal provider
    async def mock_fail():
        return False
    
    # For now, MatrixService always returns True, so we'll need to update it 
    # to actually attempt a connection in Phase 005. 
    # This test will define that it CAN fail.
    pass 

@pytest.mark.asyncio
async def test_emit_telemetry_event(matrix_service):
    """Test emitting a telemetry event."""
    event = TelemetryEvent(
        event_id="evt_999",
        event_type="agent_start",
        source="matrix_supervisor",
        payload={"action": "monitoring"}
    )
    success = await matrix_service.emit_event(event)
    assert success is True

@pytest.mark.asyncio
async def test_emit_event_failure(matrix_service, monkeypatch):
    """Test emitting a telemetry event when redis fails."""
    # Re-mock redis to fail
    mock_redis = AsyncMock()
    mock_redis.xadd.side_effect = Exception("Redis error")
    monkeypatch.setattr(matrix_service, "_redis", mock_redis)
    
    event = TelemetryEvent(
        event_id="evt_err",
        event_type="error",
        source="tester"
    )
    success = await matrix_service.emit_event(event)
    assert success is False

@pytest.mark.asyncio
async def test_initialize_telemetry_stream_failure_actual(matrix_service, monkeypatch):
    """Test initializing the telemetry stream when redis fails."""
    mock_redis = AsyncMock()
    mock_redis.ping.side_effect = Exception("Connection error")
    monkeypatch.setattr(matrix_service, "_redis", mock_redis)
    
    success = await matrix_service.initialize_telemetry_stream()
    assert success is False

@pytest.mark.asyncio
async def test_capture_agent_heartbeat(matrix_service):
    """Test capturing an agent heartbeat."""
    success = await matrix_service.capture_agent_heartbeat("agent_alpha", "working")
    assert success is True
    overview = matrix_service.get_system_overview()
    assert "agent_alpha" in overview.active_agents
    assert overview.active_agents["agent_alpha"].current_task == "working"

@pytest.mark.asyncio
async def test_capture_agent_heartbeat_status_busy(matrix_service):
    """Test capturing a heartbeat with BUSY status."""
    success = await matrix_service.capture_agent_heartbeat(
        "agent_beta", 
        task="processing", 
        status=AgentHealthStatus.BUSY
    )
    assert success is True
    overview = matrix_service.get_system_overview()
    assert overview.active_agents["agent_beta"].status == AgentHealthStatus.BUSY

@pytest.mark.asyncio
async def test_capture_agent_heartbeat_metadata(matrix_service):
    """Test capturing a heartbeat with metadata."""
    metadata = {"token_usage": 150, "model": "gpt-4"}
    success = await matrix_service.capture_agent_heartbeat(
        "agent_gamma", 
        metadata=metadata
    )
    assert success is True
    overview = matrix_service.get_system_overview()
    assert overview.active_agents["agent_gamma"].metadata["token_usage"] == 150

@pytest.mark.asyncio
async def test_prune_stale_agents(matrix_service):
    """Test pruning stale agents."""
    from datetime import timedelta
    # Add a stale agent manually
    stale_state = AgentState(
        status=AgentHealthStatus.ONLINE,
        last_heartbeat=datetime.now() - timedelta(seconds=600),
        current_task="old task"
    )
    matrix_service._state.active_agents["stale_agent"] = stale_state
    
    # Prune
    matrix_service.prune_stale_agents(timeout_seconds=300)
    
    overview = matrix_service.get_system_overview()
    assert overview.active_agents["stale_agent"].status == AgentHealthStatus.OFFLINE

@pytest.mark.asyncio
async def test_halt_system(matrix_service):
    """Test engaging the global kill-switch."""
    success = await matrix_service.halt_system()
    assert success is True
    overview = matrix_service.get_system_overview()
    assert overview.kill_switch_engaged is True
    assert overview.system_status == "halted"
