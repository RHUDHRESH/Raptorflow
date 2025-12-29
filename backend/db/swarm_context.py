import json
import logging
from typing import Any, Dict, Optional

from db import get_db_connection

logger = logging.getLogger("raptorflow.db.swarm_context")


async def save_swarm_context(workspace_id: str, context: Dict[str, Any]):
    """
    Persists Swarm context variables to the database.
    """
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            query = """
                INSERT INTO swarm_context (workspace_id, context_data, updated_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (workspace_id)
                DO UPDATE SET context_data = %s, updated_at = CURRENT_TIMESTAMP
            """
            context_json = json.dumps(context)
            await cur.execute(query, (workspace_id, context_json, context_json))


async def load_swarm_context(workspace_id: str) -> Dict[str, Any]:
    """
    Retrieves Swarm context variables from the database.
    """
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            query = "SELECT context_data FROM swarm_context WHERE workspace_id = %s"
            await cur.execute(query, (workspace_id,))
            row = await cur.fetchone()
            if row:
                return json.loads(row[0])
            return {}
