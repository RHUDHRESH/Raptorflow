from typing import Dict, Optional, Any, List
from datetime import datetime
from backend.models.telemetry import SystemState, AgentState, AgentHealthStatus, TelemetryEvent
from backend.services.cache import get_cache
from backend.db import get_pool, SupabaseSaver, get_db_connection
from backend.services.sanity_check import SystemSanityCheck
from backend.services.latency_monitor import LatencyMonitor
from backend.services.cost_governor import CostGovernor


class StateCheckpointManager:
    """
    SOTA State Checkpoint Manager.
    Handles LangGraph checkpoints and persistence across the ecosystem.
    """

    def __init__(self):
        self._pool = get_pool()
        self._saver = SupabaseSaver(self._pool)

    def get_saver(self) -> SupabaseSaver:
        """Returns the industrial-grade Supabase checkpointer."""
        return self._saver

    async def list_checkpoints(self, thread_id: str) -> List[Dict]:
        """Lists historical checkpoints for a specific thread."""
        # Wrap checkpointer logic or query DB directly
        async with self._pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT checkpoint_id, created_at FROM checkpoints WHERE thread_id = %s ORDER BY created_at DESC",
                    (thread_id,),
                )
                rows = await cur.fetchall()
                return [{"id": r[0], "timestamp": r[1]} for r in rows]


class MatrixService:
    """Industrial-grade service for the Matrix Command & Control center."""

    def __init__(self):
        self._state = SystemState()
        self._redis = get_cache()
        self._sanity = SystemSanityCheck()
        self._latency = LatencyMonitor()
        self._cost = CostGovernor()

    def get_system_overview(self) -> SystemState:
        """Retrieves the current global system state (Legacy)."""
        return self._state

    async def get_aggregated_overview(self, workspace_id: str) -> Dict[str, Any]:
        """
        Retrieves the complete aggregated health and cost dashboard.
        Combines deterministic checks with real-time telemetry.
        """
        health = await self._sanity.run_suite()
        cost = await self._cost.get_burn_report(workspace_id)
        
        return {
            "system_state": self._state.model_dump(),
            "health_report": health,
            "cost_report": cost,
            "timestamp": datetime.now().isoformat()
        }

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
        self, 
        agent_id: str, 
        task: Optional[str] = None, 
        status: AgentHealthStatus = AgentHealthStatus.ONLINE,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Captures a heartbeat from an active agent and updates global state."""
        agent_state = AgentState(
            status=status,
            last_heartbeat=datetime.now(),
            current_task=task,
            metadata=metadata or {}
        )
        self._state.active_agents[agent_id] = agent_state
        self._state.updated_at = datetime.now()
        
        # Periodic prune (simplified for now)
        self.prune_stale_agents()
        return True

    def prune_stale_agents(self, timeout_seconds: int = 300):
        """Marks agents as OFFLINE if they haven't sent a heartbeat within the timeout."""
        now = datetime.now()
        for agent_id, state in list(self._state.active_agents.items()):
            delta = (now - state.last_heartbeat).total_seconds()
            if delta > timeout_seconds:
                state.status = AgentHealthStatus.OFFLINE

    async def halt_system(self, reason: str = "Manual Trigger") -> bool:
        """
        Engages the global Kill-Switch to stop all agentic activity.
        Logs the action to the industrial audit trail.
        """
        self._state.kill_switch_engaged = True
        self._state.system_status = "halted"
        self._state.updated_at = datetime.now()
        
        # 2. Log to Audit Trail
        try:
            async with get_db_connection() as conn:
                async with conn.cursor() as cur:
                    query = """
                        INSERT INTO agent_decision_audit (
                            tenant_id, agent_id, decision_type, input_state, 
                            output_decision, rationale
                        ) VALUES (%s, %s, %s, %s, %s, %s);
                    """
                    import psycopg
                    await cur.execute(
                        query,
                        (
                            "system", # Global scope
                            "MatrixAdmin",
                            "kill_switch",
                            psycopg.types.json.Jsonb({"status": "active"}),
                            psycopg.types.json.Jsonb({"status": "halted"}),
                            reason
                        )
                    )
                    await conn.commit()
            return True
        except Exception as e:
            print(f"ERROR: Audit logging for kill-switch failed: {e}")
            # Still return True as the internal state was updated
            return True
