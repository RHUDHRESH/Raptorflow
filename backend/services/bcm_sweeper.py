import json
import logging
from typing import Any, Dict, List, Optional

from memory.models import MemoryType
from memory.vector_store import VectorMemory
from schemas.bcm_evolution import EventType

from .agents.universal.agent import UniversalAgent
from .core.supabase_mgr import get_supabase_client

logger = logging.getLogger(__name__)


class BCMSweeper:
    """Service for compressing and vectorizing historical BCM events for extreme memory efficiency."""

    def __init__(self, db_client=None, vector_store=None):
        self.db = db_client or get_supabase_client()
        self.agent = UniversalAgent()
        self.vector_store = vector_store or VectorMemory(supabase_client=self.db)
        self.sweep_threshold = 10  # Only sweep if > 10 interactions (Economy)

    async def compress_events(
        self, workspace_id: str, ucid: str, limit: int = 50
    ) -> Dict[str, Any]:
        """
        Condenses events into summaries and injects them into Strategic Long-Term Memory (pgvector).
        """
        try:
            # 1. Fetch old interactions
            result = (
                await self.db.table("bcm_events")
                .select("*")
                .eq("workspace_id", workspace_id)
                .eq("event_type", EventType.USER_INTERACTION)
                .order("created_at")
                .limit(limit)
                .execute()
            )

            events = result.data

            # ECONOMY: Only sweep if we have enough events to justify AI cost
            if not events or len(events) < self.sweep_threshold:
                return {
                    "success": True,
                    "message": "Below sweep threshold",
                    "checkpoint_id": None,
                }

            event_ids = [e["id"] for e in events]

            # 2. Universal Agent compression
            agent_input = {"events_to_compress": json.dumps(events)}

            response = await self.agent.run_step("bcm_compression", agent_input)

            if not response.get("success"):
                raise Exception(f"AI Compression failed: {response.get('error')}")

            compression_data = json.loads(response["output"])
            summary = compression_data.get("summary", "")
            key_learnings = compression_data.get("key_takeaways", [])

            # 3. STRATEGIC MEMORY: Vectorize the summary for future semantic search
            try:
                vector_content = (
                    f"LEARNINGS: {' '.join(key_learnings)} \nSUMMARY: {summary}"
                )
                await self.vector_store.store(
                    workspace_id=workspace_id,
                    memory_type=MemoryType.BCM,
                    content=vector_content,
                    metadata={
                        "ucid": ucid,
                        "event_ids": event_ids,
                        "type": "strategic_checkpoint",
                    },
                )
                logger.info(
                    f"BCM Sweeper: Vectorized strategic memory for {workspace_id}"
                )
            except Exception as v_err:
                logger.warning(
                    f"BCM Sweeper: Vectorization failed (non-critical): {v_err}"
                )

            # 4. Create SYSTEM_CHECKPOINT event (Ledger)
            checkpoint_result = (
                await self.db.table("bcm_events")
                .insert(
                    {
                        "workspace_id": workspace_id,
                        "event_type": EventType.SYSTEM_CHECKPOINT,
                        "payload": {
                            "summary": summary,
                            "key_learnings": key_learnings,
                            "compressed_event_ids": event_ids,
                            "compressed_count": len(event_ids),
                        },
                        "ucid": ucid,
                    }
                )
                .execute()
            )

            checkpoint_id = checkpoint_result.data[0]["id"]

            # 5. Delete old events (Economy: keep DB lean)
            await self.db.table("bcm_events").delete().in_("id", event_ids).execute()

            logger.info(f"BCM Sweep complete for {workspace_id}: {checkpoint_id}")
            return {
                "success": True,
                "checkpoint_id": checkpoint_id,
                "compressed_count": len(event_ids),
            }

        except Exception as e:
            logger.error(f"Error during BCM sweep for {workspace_id}: {e}")
            raise  # Re-raise to ensure tests and callers know it failed

    async def sweep_all_workspaces(self):
        """
        Background task to clean up old events for all workspaces.
        """
        logger.info("Starting global BCM Semantic Sweep...")
        try:
            # 1. ECONOMY: Efficiently find workspaces that have pending interactions
            result = (
                await self.db.table("bcm_events")
                .select("workspace_id")
                .eq("event_type", EventType.USER_INTERACTION)
                .execute()
            )

            # Using set for unique IDs if distinct isn't directly available via simple select
            workspaces = list(set([r["workspace_id"] for r in result.data]))

            stats = {"total": len(workspaces), "successful": 0, "failed": 0}

            for ws_id in workspaces:
                try:
                    # Try to compress
                    sweep_res = await self.compress_events(
                        workspace_id=ws_id, ucid="SYSTEM-AUTO-SWEEP"
                    )
                    if sweep_res["success"]:
                        stats["successful"] += 1
                    else:
                        stats["failed"] += 1
                except Exception as sweep_err:
                    logger.error(f"Sweep failed for workspace {ws_id}: {sweep_err}")
                    stats["failed"] += 1

            logger.info(f"Global BCM Sweep finished. Stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Global BCM Sweep failed: {e}")
            return {"error": str(e)}
