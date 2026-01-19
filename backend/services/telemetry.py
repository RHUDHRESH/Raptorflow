"""
Reasoning Telemetry Service: Persists AI reasoning traces for audit and API visibility.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from backend.core.supabase_mgr import get_supabase_client

logger = logging.getLogger(__name__)

class ReasoningTelemetry:
    """Service for managing reasoning traces and logs."""

    def __init__(self):
        self.supabase = get_supabase_client()

    async def log_reasoning(self, workspace_id: str, agent_name: str, task_id: str, trace: Dict[str, Any]) -> bool:
        """
        Persists a reasoning trace to the database.
        """
        try:
            data = {
                "workspace_id": workspace_id,
                "agent_name": agent_name,
                "task_id": task_id,
                "reasoning_trace": trace,
                "timestamp": datetime.now().isoformat()
            }
            
            # Using Supabase JSONB for persistence
            await self.supabase.table("agent_reasoning_logs").insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to log reasoning: {e}")
            return False

    async def get_trace(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a reasoning trace for a specific task.
        """
        try:
            res = await self.supabase.table("agent_reasoning_logs").select("reasoning_trace").eq("task_id", task_id).single().execute()
            return res.data.get("reasoning_trace") if res.data else None
        except Exception as e:
            logger.error(f"Failed to retrieve trace: {e}")
            return None