"""
BCM Event Recorder Service
Handles recording of discrete strategic and operational events to the ledger.
"""

import logging
from typing import Any, Dict, Optional

from core.supabase_mgr import get_supabase_client
from schemas.bcm_evolution import EventType

logger = logging.getLogger(__name__)


class BCMEventRecorder:
    """Service for recording BCM events to Supabase ledger"""

    def __init__(self, db_client=None):
        self.db = db_client or get_supabase_client()
        self.table_name = "bcm_events"

    async def record_event(
        self,
        workspace_id: str,
        event_type: EventType,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        ucid: Optional[str] = None,
    ) -> str:
        """
        Record a new event to the BCM ledger.

        Args:
            workspace_id: The UUID of the workspace
            event_type: Type of event from EventType enum
            payload: The actual event data
            metadata: Optional technical metadata
            ucid: Optional RaptorFlow UCID

        Returns:
            The ID of the recorded event
        """
        try:
            event_data = {
                "workspace_id": workspace_id,
                "event_type": event_type,
                "payload": payload,
                "metadata": metadata or {},
                "ucid": ucid,
            }

            result = self.db.table(self.table_name).insert(event_data).execute()

            if not result.data:
                raise Exception("Failed to record event: No data returned from DB")

            event_id = result.data[0]["id"]
            logger.info(
                f"Recorded {event_type} event for workspace {workspace_id}: {event_id}"
            )

            # Invalidate Hot Cache (Extreme Context Freshness)
            try:
                from services.upstash_client import get_upstash_client

                redis = get_upstash_client()

                # Invalidate all versions for this workspace to ensure total consistency
                # This handles both specific UCID and default baselines
                pattern = f"bcm:projected:{workspace_id}:*"
                await redis.clear_pattern(pattern)

                logger.debug(f"Invalidated BCM cache for workspace {workspace_id}")
            except Exception as cache_err:
                logger.warning(f"Failed to invalidate BCM cache: {cache_err}")

            return event_id

        except Exception as e:
            logger.error(f"Error recording BCM event: {str(e)}")
            raise
