"""
Advanced Analytics Service
Calculates ROI, cross-channel performance, and generates automated reports
Connected to REAL database (muse_assets)
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    from dependencies import get_db
    from services.vertex_ai_service import vertex_ai_service
except ImportError:
    vertex_ai_service = None

    def get_db():
        return None


logger = logging.getLogger(__name__)


class AdvancedAnalyticsService:
    """Service for complex content performance analysis using real DB state."""

    async def get_roi_report(
        self, workspace_id: str, timeframe_days: int = 30
    ) -> Dict[str, Any]:
        """Generate a comprehensive ROI report based on real muse_assets data."""
        logger.info(f"Generating real ROI report for workspace {workspace_id}")

        db = await get_db()
        if not db:
            return {}

        cutoff = datetime.now() - timedelta(days=timeframe_days)

        try:
            # Aggregate real metrics from muse_assets
            stats = await db.fetchrow(
                """
                SELECT
                    COUNT(*) as total_count,
                    SUM(view_count) as views,
                    SUM(share_count) as shares,
                    AVG(conversion_rate) as avg_conv,
                    SUM(cost_usd) as total_cost
                FROM muse_assets
                WHERE workspace_id = $1 AND created_at >= $2
                """,
                workspace_id,
                cutoff,
            )

            # Map by channel
            channel_stats = await db.fetch(
                """
                SELECT asset_type as channel, COUNT(*) as count, SUM(view_count) as views
                FROM muse_assets
                WHERE workspace_id = $1 AND created_at >= $2
                GROUP BY asset_type
                """,
                workspace_id,
                cutoff,
            )

            return {
                "timeframe": f"{timeframe_days}d",
                "total_assets": stats["total_count"],
                "total_views": stats["views"] or 0,
                "total_shares": stats["shares"] or 0,
                "avg_conversion": float(stats["avg_conv"] or 0),
                "total_investment": float(stats["total_cost"] or 0),
                "channel_breakdown": [dict(r) for r in channel_stats],
                "generated_at": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"ROI Report failed: {e}")
            return {"error": str(e)}

    async def get_automated_insights(self, workspace_id: str) -> List[str]:
        """Generate AI-driven strategic insights based on real performance data."""
        if not vertex_ai_service:
            return []

        report = await self.get_roi_report(workspace_id)

        prompt = f"""Analyze this content performance report and provide 3 surgical strategic insights.

REPORT:
{json.dumps(report, indent=2)}

Focus on:
1. What content types are winning.
2. Conversion efficiency.
3. One bold move to improve ROI."""

        try:
            ai_response = await vertex_ai_service.generate_text(
                prompt=prompt,
                workspace_id="analytics-insights",
                user_id="analytics-service",
                max_tokens=500,
            )

            if ai_response["status"] == "success":
                # Expecting a list of strings
                return [
                    line.strip("- ")
                    for line in ai_response["text"].strip().split("\n")
                    if line.strip()
                ]
            return ["Insufficient data for AI insights."]
        except Exception as e:
            logger.error(f"AI Insights failed: {e}")
            return ["Error generating insights."]


advanced_analytics_service = AdvancedAnalyticsService()
