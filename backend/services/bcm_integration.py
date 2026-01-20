"""
BCM Evolution Integration Utility
=================================

A high-level interface for other services to interact with the BCM Evolution system.
Provides one-liner methods for common operations like ledgering events.
"""

import logging
from typing import Any, Dict, List, Optional
from backend.services.bcm_recorder import BCMEventRecorder
from backend.services.bcm_projector import BCMProjector
from backend.schemas.bcm_evolution import EventType
from backend.core.supabase_mgr import get_supabase_client

logger = logging.getLogger(__name__)

class BCMIntegration:
    """Gateway for all services to access BCM Evolution features."""

    def __init__(self, db_client=None):
        self.db = db_client or get_supabase_client()
        self.recorder = BCMEventRecorder(db_client=self.db)
        self.projector = BCMProjector(db_client=self.db)

    async def record_strategic_shift(self, workspace_id: str, ucid: str, reason: str, updates: Dict[str, Any]):
        """Record a major strategic baseline or shift."""
        try:
            return await self.recorder.record_event(
                workspace_id=workspace_id,
                event_type=EventType.STRATEGIC_SHIFT,
                payload={
                    "reason": reason,
                    "updates": updates
                },
                ucid=ucid
            )
        except Exception as e:
            logger.error(f"BCM Integration failed to record strategic shift: {e}")
            return None

    async def record_interaction(self, workspace_id: str, agent_name: str, interaction_type: str, payload: Dict[str, Any]):
        """Record a user-agent interaction."""
        try:
            return await self.recorder.record_event(
                workspace_id=workspace_id,
                event_type=EventType.USER_INTERACTION,
                payload={
                    "agent_name": agent_name,
                    "interaction_type": interaction_type,
                    **payload
                }
            )
        except Exception as e:
            logger.error(f"BCM Integration failed to record interaction: {e}")
            return None

    async def get_latest_context(self, workspace_id: str, ucid: str):
        """Get the current evolved strategic context."""
        try:
            return await self.projector.get_latest_state(workspace_id, ucid)
        except Exception as e:
            logger.error(f"BCM Integration failed to project context: {e}")
            return None

# Global instance for easy access
bcm_evolution = BCMIntegration()
