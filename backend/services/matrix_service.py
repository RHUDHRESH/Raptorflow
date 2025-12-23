from typing import Dict, Optional, Any
from datetime import datetime
from backend.models.telemetry import SystemState, AgentState, AgentHealthStatus, TelemetryEvent
from backend.services.cache import get_cache


class MatrixService:
    """Industrial-grade service for the Matrix Command & Control center."""

    def __init__(self):
        self._state = SystemState()
        self._redis = get_cache()

    def get_system_overview(self) -> SystemState:
        """Retrieves the current global system state."""
        return self._state

    async def initialize_telemetry_stream(self) -> bool:
        """Initializes connection to telemetry providers (e.g., Upstash)."""
        try:
            # Simple ping to verify connection
            await self._redis.ping()
            return True
        except Exception as e:
            print(f"ERROR: Failed to initialize telemetry stream: {e}")
            return False

    async def emit_event(self, event: TelemetryEvent) -> bool:
        """Emits a telemetry event to the live stream."""
        try:
            # Push to a Redis stream or list for real-time dashboard
            await self._redis.xadd("matrix_telemetry", {"event": event.model_dump_json()})
            return True
        except Exception as e:
            print(f"ERROR: Failed to emit telemetry event: {e}")
            return False

    async def capture_agent_heartbeat(
        self, agent_id: str, task: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Captures a heartbeat from an active agent and updates global state."""
        agent_state = AgentState(
            status=AgentHealthStatus.ONLINE,
            last_heartbeat=datetime.now(),
            current_task=task,
            metadata=metadata or {}
        )
        self._state.active_agents[agent_id] = agent_state
        self._state.updated_at = datetime.now()
        return True

    async def halt_system(self) -> bool:
        """Engages the global Kill-Switch to stop all agentic activity."""
        self._state.kill_switch_engaged = True
        self._state.system_status = "halted"
        self._state.updated_at = datetime.now()
        return True
