import logging
import time
from typing import Any, Dict, Optional
from uuid import uuid4

from db import get_db_connection
from models.telemetry import TelemetryEvent, TelemetryEventType

logger = logging.getLogger("raptorflow.services.telemetry_collector")


class TelemetryCollectorService:
    """
    Durable telemetry collector for agent and tool performance events.
    Stores events in a Postgres-backed telemetry_events table.
    """

    async def store_event(self, event: TelemetryEvent) -> bool:
        query = """
            INSERT INTO telemetry_events (
                event_id,
                timestamp,
                event_type,
                source,
                payload,
                metadata
            )
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        import psycopg

        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        query,
                        (
                            event.event_id,
                            event.timestamp,
                            str(event.event_type),
                            event.source,
                            psycopg.types.json.Jsonb(event.payload),
                            psycopg.types.json.Jsonb(event.metadata),
                        ),
                    )
                    await conn.commit()
                    return True
                except Exception as exc:
                    logger.error(f"Failed to persist telemetry event: {exc}")
                    return False

    async def record_agent_event(
        self,
        event_type: TelemetryEventType,
        agent_name: str,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        event = TelemetryEvent(
            event_id=str(uuid4()),
            event_type=event_type,
            source=agent_name,
            payload=payload,
            metadata=metadata or {},
        )
        return await self.store_event(event)

    async def record_tool_event(
        self,
        event_type: TelemetryEventType,
        tool_name: str,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        event = TelemetryEvent(
            event_id=str(uuid4()),
            event_type=event_type,
            source=tool_name,
            payload=payload,
            metadata=metadata or {},
        )
        return await self.store_event(event)

    async def summarize_for_learning(
        self,
        workspace_id: Optional[str] = None,
        lookback_hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Returns summarized performance signals for the learning layer.
        """
        agent_query = """
            SELECT
                source,
                COUNT(*) AS total_runs,
                AVG((payload->>'duration_ms')::float) AS avg_duration_ms,
                AVG(
                    CASE WHEN (payload->>'success')::boolean THEN 1 ELSE 0 END
                ) AS success_rate,
                AVG(
                    COALESCE((payload->>'total_tokens')::float, 0)
                ) AS avg_total_tokens
            FROM telemetry_events
            WHERE event_type = %s
              AND timestamp >= NOW() - (%s || ' hours')::interval
              AND (%s IS NULL OR metadata->>'workspace_id' = %s)
            GROUP BY source
            ORDER BY total_runs DESC;
        """
        tool_query = """
            SELECT
                source,
                COUNT(*) AS total_runs,
                AVG((payload->>'duration_ms')::float) AS avg_duration_ms,
                AVG(
                    CASE WHEN (payload->>'success')::boolean THEN 1 ELSE 0 END
                ) AS success_rate
            FROM telemetry_events
            WHERE event_type = %s
              AND timestamp >= NOW() - (%s || ' hours')::interval
              AND (%s IS NULL OR metadata->>'workspace_id' = %s)
            GROUP BY source
            ORDER BY total_runs DESC;
        """
        report: Dict[str, Any] = {
            "window_hours": lookback_hours,
            "agents": [],
            "tools": [],
        }
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(
                        agent_query,
                        (
                            TelemetryEventType.AGENT_END.value,
                            lookback_hours,
                            workspace_id,
                            workspace_id,
                        ),
                    )
                    agent_rows = await cur.fetchall()
                    report["agents"] = [
                        {
                            "agent_name": row[0],
                            "total_runs": row[1],
                            "avg_duration_ms": row[2],
                            "success_rate": row[3],
                            "avg_total_tokens": row[4],
                        }
                        for row in agent_rows
                    ]

                    await cur.execute(
                        tool_query,
                        (
                            TelemetryEventType.TOOL_END.value,
                            lookback_hours,
                            workspace_id,
                            workspace_id,
                        ),
                    )
                    tool_rows = await cur.fetchall()
                    report["tools"] = [
                        {
                            "tool_name": row[0],
                            "total_runs": row[1],
                            "avg_duration_ms": row[2],
                            "success_rate": row[3],
                        }
                        for row in tool_rows
                    ]
                except Exception as exc:
                    logger.error(f"Failed to summarize telemetry: {exc}")

        return report

    @staticmethod
    def capture_duration_ms(start_time: float) -> float:
        return (time.perf_counter() - start_time) * 1000


_telemetry_collector: Optional[TelemetryCollectorService] = None


def get_telemetry_collector() -> TelemetryCollectorService:
    global _telemetry_collector
    if _telemetry_collector is None:
        _telemetry_collector = TelemetryCollectorService()
    return _telemetry_collector
