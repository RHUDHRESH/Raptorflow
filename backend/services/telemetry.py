"""
Reasoning Telemetry Service: Persists AI reasoning traces for audit and API visibility.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .core.supabase_mgr import get_supabase_client
from .services.bcm_integration import bcm_evolution

logger = logging.getLogger(__name__)


class ReasoningTelemetry:
    """Service for capturing and persisting agent reasoning traces."""

    def __init__(self):
        self.supabase = get_supabase_client()

    async def log_reasoning(
        self, workspace_id: str, agent_name: str, task_id: str, trace: Dict[str, Any]
    ) -> bool:
        """
        Persists a reasoning trace to the database and BCM Ledger.
        """
        try:
            data = {
                "workspace_id": workspace_id,
                "agent_name": agent_name,
                "task_id": task_id,
                "trace": trace,
                "created_at": datetime.utcnow().isoformat(),
            }

            # Using Supabase JSONB for persistence
            await self.supabase.table("agent_reasoning_logs").insert(data).execute()

            # Record in BCM Ledger via unified integration
            await bcm_evolution.record_interaction(
                workspace_id=workspace_id,
                agent_name=agent_name,
                interaction_type="AI_REASONING",
                payload={"task_id": task_id, "reasoning_length": len(str(trace))},
            )

            return True
        except Exception as e:
            logger.error(f"Failed to log reasoning: {e}")
            return False

    async def get_trace(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a reasoning trace for a specific task.
        """
        try:
            res = (
                await self.supabase.table("agent_reasoning_logs")
                .select("reasoning_trace")
                .eq("task_id", task_id)
                .single()
                .execute()
            )
            return res.data.get("reasoning_trace") if res.data else None
        except Exception as e:
            logger.error(f"Failed to retrieve trace: {e}")
            return None
