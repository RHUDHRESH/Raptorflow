from typing import Dict, Optional

import psycopg

from db import get_db_connection


class LongTermMemory:
    """
    SOTA Long-Term Memory Manager.
    Handles historical outcome storage and agent decision auditing using Postgres.
    """

    async def log_decision(
        self,
        tenant_id: str,
        agent_id: str,
        decision_type: str,
        input_state: Optional[Dict] = None,
        output_decision: Optional[Dict] = None,
        rationale: Optional[str] = None,
        cost_estimate: float = 0.0,
    ):
        """Logs an agent decision to the audit trail."""
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    INSERT INTO agent_decision_audit (
                        tenant_id, agent_id, decision_type, input_state,
                        output_decision, rationale, cost_estimate
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
                await cur.execute(
                    query,
                    (
                        tenant_id,
                        agent_id,
                        decision_type,
                        psycopg.types.json.Jsonb(input_state or {}),
                        psycopg.types.json.Jsonb(output_decision or {}),
                        rationale,
                        cost_estimate,
                    ),
                )
                await conn.commit()

    async def get_decisions(self, tenant_id: str, limit: int = 10) -> list[dict]:
        """Retrieves recent decisions for a tenant."""
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    SELECT agent_id, decision_type, rationale, created_at
                    FROM agent_decision_audit
                    WHERE tenant_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s;
                """
                await cur.execute(query, (tenant_id, limit))
                results = await cur.fetchall()
                return [
                    {
                        "agent_id": r[0],
                        "decision_type": r[1],
                        "rationale": r[2],
                        "created_at": r[3],
                    }
                    for r in results
                ]
