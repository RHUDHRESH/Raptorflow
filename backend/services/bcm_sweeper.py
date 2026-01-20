"""
BCM Sweeper Service
Handles semantic compression of old events into summaries to keep the ledger economical.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from backend.agents.universal.agent import UniversalAgent
from backend.core.supabase_mgr import get_supabase_client
from backend.schemas.bcm_evolution import EventType

logger = logging.getLogger(__name__)

class BCMSweeper:
    """Service for compressing historical BCM events into strategic summaries"""
    
    def __init__(self, db_client=None):
        self.db = db_client or get_supabase_client()
        self.agent = UniversalAgent()

    async def compress_events(self, workspace_id: str, ucid: str, limit: int = 20) -> Dict[str, Any]:
        """
        Finds old user interactions and search queries and compresses them.
        """
        try:
            # 1. Fetch old interactions (prioritize USER_INTERACTION)
            result = await self.db.table("bcm_events") \
                .select("*") \
                .eq("workspace_id", workspace_id) \
                .eq("event_type", EventType.USER_INTERACTION) \
                .order("created_at") \
                .limit(limit) \
                .execute()
            
            events = result.data
            if len(events) < 2:
                return {"success": True, "message": "Not enough events to compress", "checkpoint_id": None}
            
            event_ids = [e["id"] for e in events]
            
            # 2. Universal Agent compression
            agent_input = {
                "events_to_compress": json.dumps(events)
            }
            
            response = await self.agent.run_step("bcm_compression", agent_input)
            
            if not response.get("success"):
                raise Exception(f"AI Compression failed: {response.get('error')}")
                
            compression_data = json.loads(response["output"])
            summary = compression_data.get("summary", f"Compressed {len(events)} interactions.")
            
            # 3. Create SYSTEM_CHECKPOINT event
            checkpoint_result = await self.db.table("bcm_events").insert({
                "workspace_id": workspace_id,
                "event_type": EventType.SYSTEM_CHECKPOINT,
                "payload": {
                    "summary": summary,
                    "compressed_event_ids": event_ids
                },
                "ucid": ucid
            }).execute()
            
            checkpoint_id = checkpoint_result.data[0]["id"]
            
            # 4. Delete old events
            await self.db.table("bcm_events") \
                .delete() \
                .in_("id", event_ids) \
                .execute()
                
            logger.info(f"BCM Sweep complete for {workspace_id}: {checkpoint_id}")
            return {
                "success": True,
                "checkpoint_id": checkpoint_id,
                "compressed_count": len(event_ids)
            }
            
        except Exception as e:
            logger.error(f"Error during BCM sweep: {e}")
            raise
