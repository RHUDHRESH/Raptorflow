"""
Great Migration Script: SQLite to Supabase
==========================================

Performs the final cutover from fragmented SQLite files to the consolidated Supabase schema.
"""

import sqlite3
import json
import logging
import os
from datetime import datetime, UTC

from .core.supabase_mgr import get_supabase_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migration")


def migrate_synapse_state():
    """Migrates flow_state from synapse.db to campaign_arcs pulse."""
    db_path = "backend/synapse.db"
    if not os.path.exists(db_path):
        logger.warning(f"Synapse DB not found at {db_path}, skipping.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT id, state FROM flow_state")
    client = get_supabase_client()

    for row in cursor:
        flow_id, state_json = row
        state = json.loads(state_json)
        workspace_id = state.get("workspace_id", "system")

        logger.info(f"Migrating flow state {flow_id}...")
        client.table("campaign_arcs").upsert(
            {
                "id": flow_id,
                "workspace_id": workspace_id,
                "current_pulse": state,
                "updated_at": datetime.now(UTC).isoformat(),
            }
        ).execute()

    conn.close()
    logger.info("✅ Synapse state migration complete.")


def migrate_campaigns():
    """Migrates campaigns from campaigns.db to Supabase."""
    db_path = "backend/campaigns.db"
    if not os.path.exists(db_path):
        logger.warning(f"Campaigns DB not found at {db_path}, skipping.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT * FROM campaigns")
    client = get_supabase_client()

    # Column mapping depends on schema
    for row in cursor:
        logger.info(f"Migrating campaign {row[1]}...")
        # Simplified insert
        client.table("campaigns").upsert(
            {
                "id": row[0],
                "name": row[1],
                "workspace_id": row[3],
                "status": row[6],
                "created_at": row[7],
            }
        ).execute()

    conn.close()
    logger.info("✅ Campaigns migration complete.")


if __name__ == "__main__":
    migrate_synapse_state()
    migrate_campaigns()
