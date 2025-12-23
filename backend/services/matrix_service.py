from typing import Dict, Optional, Any
from datetime import datetime
from backend.models.telemetry import SystemState, AgentState, AgentHealthStatus


class MatrixService:
    """Industrial-grade service for the Matrix Command & Control center."""

    def __init__(self):
        self._state = SystemState()

    def get_system_overview(self) -> SystemState:
        """Retrieves the current global system state."""
        return self._state

    async def initialize_telemetry_stream(self) -> bool:
        """Initializes connection to telemetry providers (e.g., Upstash)."""
        # Implementation will come in Phase 005
        return True

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
