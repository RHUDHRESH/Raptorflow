"""
Integration between memory and database systems.
Vectorizes database records and invalidates memory on changes.
"""

import logging
from typing import Any, Dict, List, Optional

from memory.controller import MemoryController
from memory.vectorizers.foundation import FoundationVectorizer
from memory.vectorizers.icp import ICPVectorizer
from memory.vectorizers.move import MoveVectorizer

from supabase import Client

logger = logging.getLogger(__name__)


async def sync_database_to_memory(
    workspace_id: str, db: Client, memory_controller: MemoryController
) -> Dict[str, Any]:
    """
    Synchronize database records to memory system.

    Args:
        workspace_id: Workspace ID
        db: Database client
        memory_controller: Memory controller

    Returns:
        Sync results
    """
    try:
        logger.info(f"Starting database to memory sync for workspace: {workspace_id}")

        results = {
            "foundation": await _sync_foundation(workspace_id, db, memory_controller),
            "icps": await _sync_icps(workspace_id, db, memory_controller),
            "moves": await _sync_moves(workspace_id, db, memory_controller),
            "campaigns": await _sync_campaigns(workspace_id, db, memory_controller),
        }

        total_records = sum(
            result.get("records_processed", 0) for result in results.values()
        )
        logger.info(f"Database sync completed: {total_records} records processed")

        return results

    except Exception as e:
        logger.error(f"Error in database to memory sync: {e}")
        return {"error": str(e)}


async def _sync_foundation(
    workspace_id: str, db: Client, memory_controller: MemoryController
) -> Dict[str, Any]:
    """Sync foundation data to memory."""
    try:
        # Get foundation data
        result = (
            db.table("foundations")
            .select("*")
            .eq("workspace_id", workspace_id)
            .execute()
        )

        if not result.data:
            return {"records_processed": 0, "status": "no_data"}

        foundation_data = result.data[0]

        # Vectorize foundation
        vectorizer = FoundationVectorizer(memory_controller)
        await vectorizer.vectorize_foundation(workspace_id, foundation_data)

        return {
            "records_processed": 1,
            "status": "success",
            "foundation_id": foundation_data["id"],
        }

    except Exception as e:
        logger.error(f"Error syncing foundation: {e}")
        return {"records_processed": 0, "status": "error", "error": str(e)}


async def _sync_icps(
    workspace_id: str, db: Client, memory_controller: MemoryController
) -> Dict[str, Any]:
    """Sync ICP data to memory."""
    try:
        # Get ICP data
        result = (
            db.table("icp_profiles")
            .select("*")
            .eq("workspace_id", workspace_id)
            .execute()
        )

        if not result.data:
            return {"records_processed": 0, "status": "no_data"}

        vectorizer = ICPVectorizer(memory_controller)
        records_processed = 0

        for icp_data in result.data:
            await vectorizer.vectorize_icp(workspace_id, icp_data)
            records_processed += 1

        return {
            "records_processed": records_processed,
            "status": "success",
            "icp_count": len(result.data),
        }

    except Exception as e:
        logger.error(f"Error syncing ICPs: {e}")
        return {"records_processed": 0, "status": "error", "error": str(e)}


async def _sync_moves(
    workspace_id: str, db: Client, memory_controller: MemoryController
) -> Dict[str, Any]:
    """Sync move data to memory."""
    try:
        # Get move data
        result = (
            db.table("moves").select("*").eq("workspace_id", workspace_id).execute()
        )

        if not result.data:
            return {"records_processed": 0, "status": "no_data"}

        vectorizer = MoveVectorizer(memory_controller)
        records_processed = 0

        for move_data in result.data:
            await vectorizer.vectorize_move(workspace_id, move_data)
            records_processed += 1

        return {
            "records_processed": records_processed,
            "status": "success",
            "move_count": len(result.data),
        }

    except Exception as e:
        logger.error(f"Error syncing moves: {e}")
        return {"records_processed": 0, "status": "error", "error": str(e)}


async def _sync_campaigns(
    workspace_id: str, db: Client, memory_controller: MemoryController
) -> Dict[str, Any]:
    """Sync campaign data to memory."""
    try:
        # Get campaign data
        result = (
            db.table("campaigns").select("*").eq("workspace_id", workspace_id).execute()
        )

        if not result.data:
            return {"records_processed": 0, "status": "no_data"}

        records_processed = 0

        for campaign_data in result.data:
            # Store campaign as memory
            content = f"""
            Campaign: {campaign_data['name']}
            Description: {campaign_data.get('description', '')}
            Target ICPs: {campaign_data.get('target_icps', [])}
            Status: {campaign_data['status']}
            """

            await memory_controller.store(
                workspace_id=workspace_id,
                memory_type="campaign",
                content=content,
                metadata={
                    "campaign_id": campaign_data["id"],
                    "name": campaign_data["name"],
                    "status": campaign_data["status"],
                },
            )
            records_processed += 1

        return {
            "records_processed": records_processed,
            "status": "success",
            "campaign_count": len(result.data),
        }

    except Exception as e:
        logger.error(f"Error syncing campaigns: {e}")
        return {"records_processed": 0, "status": "error", "error": str(e)}


async def invalidate_on_change(
    table: str, record_id: str, workspace_id: str, memory_controller: MemoryController
) -> bool:
    """
    Invalidate relevant memory when database records change.

    Args:
        table: Table name that changed
        record_id: ID of changed record
        workspace_id: Workspace ID
        memory_controller: Memory controller

    Returns:
        Success status
    """
    try:
        logger.info(
            f"Invalidating memory for {table}:{record_id} in workspace {workspace_id}"
        )

        # Map tables to memory types
        table_to_memory_type = {
            "foundations": "foundation",
            "icp_profiles": "icp",
            "moves": "move",
            "campaigns": "campaign",
            "muse_assets": "content",
        }

        memory_type = table_to_memory_type.get(table)
        if not memory_type:
            logger.warning(f"No memory mapping for table: {table}")
            return True

        # Search for related memory
        memory_results = await memory_controller.search(
            workspace_id=workspace_id,
            query=record_id,
            memory_types=[memory_type],
            limit=50,
        )

        # Delete or update related memory
        invalidated_count = 0
        for memory_item in memory_results:
            if memory_item.metadata.get("record_id") == record_id:
                await memory_controller.delete(memory_item.id)
                invalidated_count += 1

        logger.info(
            f"Invalidated {invalidated_count} memory items for {table}:{record_id}"
        )

        return True

    except Exception as e:
        logger.error(f"Error invalidating memory: {e}")
        return False


class DatabaseMemorySync:
    """
    Handles ongoing synchronization between database and memory.
    """

    def __init__(self, db: Client, memory_controller: MemoryController):
        self.db = db
        self.memory_controller = memory_controller
        self.sync_queue = []

    async def queue_sync(self, workspace_id: str, table: str = None):
        """
        Queue workspace for synchronization.

        Args:
            workspace_id: Workspace ID to sync
            table: Specific table to sync (optional)
        """
        self.sync_queue.append(
            {"workspace_id": workspace_id, "table": table, "timestamp": time.time()}
        )

    async def process_sync_queue(self) -> Dict[str, Any]:
        """
        Process all queued synchronizations.

        Returns:
        Sync results
        """
        results = {}

        for sync_item in self.sync_queue:
            workspace_id = sync_item["workspace_id"]
            table = sync_item.get("table")

            if table:
                # Sync specific table
                if table == "foundations":
                    results[f"{workspace_id}_foundation"] = await _sync_foundation(
                        workspace_id, self.db, self.memory_controller
                    )
                elif table == "icp_profiles":
                    results[f"{workspace_id}_icps"] = await _sync_icps(
                        workspace_id, self.db, self.memory_controller
                    )
                elif table == "moves":
                    results[f"{workspace_id}_moves"] = await _sync_moves(
                        workspace_id, self.db, self.memory_controller
                    )
                elif table == "campaigns":
                    results[f"{workspace_id}_campaigns"] = await _sync_campaigns(
                        workspace_id, self.db, self.memory_controller
                    )
            else:
                # Sync all tables
                results[workspace_id] = await sync_database_to_memory(
                    workspace_id, self.db, self.memory_controller
                )

        # Clear queue
        self.sync_queue.clear()

        return results

    async def setup_database_triggers(self):
        """
        Set up database triggers for automatic memory invalidation.
        This would typically be done at the database level.
        """
        logger.info(
            "Database triggers would be set up here for automatic memory invalidation"
        )
        # In a real implementation, this would set up database triggers
        # that call the invalidate_on_change function
