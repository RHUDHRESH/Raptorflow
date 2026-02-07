import logging
from datetime import datetime
from typing import Any, Dict

from db import get_db_connection

logger = logging.getLogger("raptorflow.services.cost_governor")


class CostGovernor:
    """
    SOTA Cost Governor Service.
    Calculates real-time financial burn for agentic workloads.
    Enables automatic budget enforcement and ROI tracking.
    """

    def __init__(self, daily_budget: float = 50.00):
        self.daily_budget = daily_budget

    async def calculate_daily_burn(self, workspace_id: str) -> float:
        """Calculates total dollar burn for the current day in a workspace."""
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    SELECT SUM(cost_estimate)
                    FROM agent_decision_audit
                    WHERE tenant_id = %s AND created_at >= CURRENT_DATE;
                """
                await cur.execute(query, (workspace_id,))
                result = await cur.fetchone()
                return float(result[0] or 0.0)

    async def is_over_budget(self, workspace_id: str) -> bool:
        """Checks if the workspace has exceeded its daily budget."""
        try:
            burn = await self.calculate_daily_burn(workspace_id)
            if burn > self.daily_budget:
                logger.warning(
                    f"BUDGET EXCEEDED: ${burn:.2f} burn for workspace {workspace_id} (Budget: ${self.daily_budget:.2f})"
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Cost governor check failed: {e}")
            return False

    async def get_burn_report(self, workspace_id: str) -> Dict[str, Any]:
        """Generates a detailed burn report."""
        burn = await self.calculate_daily_burn(workspace_id)
        return {
            "daily_burn": burn,
            "budget": self.daily_budget,
            "usage_percentage": (
                (burn / self.daily_budget) * 100 if self.daily_budget > 0 else 0
            ),
            "status": "danger" if burn > self.daily_budget else "normal",
            "timestamp": datetime.now().isoformat(),
        }
