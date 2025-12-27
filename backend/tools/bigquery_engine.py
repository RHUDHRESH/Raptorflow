import logging
from typing import Any, Dict

from core.analytics import Analytics
from core.tool_registry import BaseRaptorTool, RaptorRateLimiter

logger = logging.getLogger("raptorflow.tools.bigquery")


class BigQueryQueryEngineTool(BaseRaptorTool):
    """
    SOTA BigQuery Query Engine Tool.
    Executes surgical SQL queries against the BigQuery Gold Zone for longitudinal analysis.
    """

    def __init__(self):
        self._analytics = Analytics()

    @property
    def name(self) -> str:
        return "bigquery_query_engine"

    @property
    def description(self) -> str:
        return (
            "Executes SQL queries against the BigQuery analytics warehouse. "
            "Use this for longitudinal performance analysis, trend detection, "
            "and complex data-driven pattern recognition across campaigns. "
            "Input is a standard SQL query string."
        )

    @RaptorRateLimiter.get_retry_decorator()
    async def _execute(self, sql: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Executing BigQuery SQL: {sql}")

        try:
            results = self._analytics.query_gold_zone(sql)
            # Convert row iterator to list of dicts
            rows = [dict(row) for row in results]

            return {
                "success": True,
                "row_count": len(rows),
                "data": rows,
                "sql_executed": sql,
            }
        except Exception as e:
            logger.error(f"BigQuery execution failed: {e}")
            return {"success": False, "error": str(e), "sql_executed": sql}
