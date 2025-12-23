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


class FetchBrandKitAlignmentTool(BaseRaptorTool):
    """
    Tool to retrieve Brand Kit and active Positioning for alignment analysis.
    """

    def __init__(self):
        from backend.services.foundation_service import FoundationService
        self.service = FoundationService(Vault())

    @property
    def name(self) -> str:
        return "fetch_brand_kit_alignment"

    @property
    def description(self) -> str:
        return (
            "Retrieves the active brand kit and positioning data for a tenant. "
            "Essential for detecting strategic drift and ensuring brand consistency."
        )

    async def _execute(self, brand_kit_id: str) -> Dict[str, Any]:
        """
        Retrieves brand kit and related positioning data.
        """
        from uuid import UUID
        bkid = UUID(brand_kit_id)
        
        brand_kit = await self.service.get_brand_kit(bkid)
        positioning = await self.service.get_active_positioning(bkid)
        
        return {
            "brand_kit": brand_kit.model_dump() if brand_kit else None,
            "positioning": positioning.model_dump() if positioning else None
        }
