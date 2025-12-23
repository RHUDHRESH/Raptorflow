import logging
from typing import Any, Dict, List
from backend.core.toolbelt import BaseRaptorTool
from backend.services.blackbox_service import BlackboxService
from backend.core.vault import Vault

logger = logging.getLogger("raptorflow.tools.blackbox")

class FetchHistoricalPerformanceTool(BaseRaptorTool):
    """
    Tool to retrieve historical performance metrics (token costs, latencies) for specific moves.
    """

    def __init__(self):
        self.service = BlackboxService(Vault())

    @property
    def name(self) -> str:
        return "fetch_historical_performance"

    @property
    def description(self) -> str:
        return (
            "Retrieves historical performance data including token costs and latency "
            "for one or more move IDs. Useful for cost analysis and optimization."
        )

    async def _execute(self, move_ids: List[str]) -> Dict[str, Any]:
        """
        Aggregates performance data for the requested moves.
        """
        results = {}
        for mid in move_ids:
            cost = self.service.calculate_move_cost(mid)
            telemetry = self.service.get_telemetry_by_move(mid)
            
            # Simple aggregation
            avg_latency = 0
            if telemetry:
                avg_latency = sum(t.get("latency", 0) for t in telemetry) / len(telemetry)
                
            results[mid] = {
                "total_tokens": cost,
                "avg_latency": avg_latency,
                "trace_count": len(telemetry)
            }
            
        return results
