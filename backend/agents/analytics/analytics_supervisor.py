"""
Analytics Supervisor - Coordinates analytics workflow for moves/campaigns.
Validates move existence, collects metrics, generates insights, and produces reports.
"""

import structlog
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from backend.agents.analytics.metrics_collector_agent import metrics_collector_agent
from backend.agents.analytics.insight_agent import insight_agent
from backend.services.supabase_client import supabase_client
from backend.services.vertex_ai_client import vertex_ai_client
from backend.utils.correlation import get_correlation_id
from backend.utils.cache import redis_cache

logger = structlog.get_logger(__name__)


class AnalyticsSupervisor:
    """
    Tier-1 Supervisor for Analytics Domain.

    Orchestrates:
    - Metrics collection from all platforms
    - Insight generation and trend analysis
    - Anomaly detection
    - Content type performance analysis
    - Chart data generation for visualization
    - Strategic pivot suggestions

    Validates:
    - Move/campaign exists
    - Move has completed content and execution stages (has published assets)
    - Returns 404 if move not found or incomplete
    """

    def __init__(self):
        self.llm = vertex_ai_client
        self.metrics_collector = metrics_collector_agent
        self.insight_generator = insight_agent

    async def analyze_move(
        self,
        workspace_id: UUID,
        move_id: UUID,
        time_period_days: int = 30,
        include_charts: bool = True,
        include_content_analysis: bool = True,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Complete analytics workflow for a move/campaign.

        Args:
            workspace_id: User's workspace
            move_id: Campaign to analyze
            time_period_days: Lookback period for metrics
            include_charts: Whether to generate chart data
            include_content_analysis: Whether to analyze content type performance
            correlation_id: Request correlation ID

        Returns:
            Comprehensive analytics report with metrics, insights, and recommendations

        Raises:
            ValueError: If move not found or incomplete
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Starting analytics workflow",
            workspace_id=workspace_id,
            move_id=move_id,
            time_period_days=time_period_days,
            correlation_id=correlation_id
        )

        # Step 1: Validate move exists and is ready for analytics
        move = await self._validate_move(workspace_id, move_id, correlation_id)

        # Step 2: Collect metrics from all platforms
        logger.info("Collecting metrics", correlation_id=correlation_id)
        metrics = await self.metrics_collector.collect_metrics(
            workspace_id,
            move_id,
            platforms=move.get("channels"),
            time_range_days=time_period_days,
            correlation_id=correlation_id
        )

        # Step 3: Generate insights and detect anomalies
        logger.info("Generating insights", correlation_id=correlation_id)
        insights_result = await self.insight_generator.analyze_performance(
            workspace_id,
            move_id,
            time_period_days=time_period_days,
            correlation_id=correlation_id
        )

        # Step 4: Generate chart data (optional)
        charts = None
        if include_charts:
            logger.info("Generating chart data", correlation_id=correlation_id)
            charts = await self.insight_generator.generate_chart_data(
                workspace_id,
                move_id,
                time_period_days=time_period_days,
                correlation_id=correlation_id
            )

        # Step 5: Analyze content type performance (optional)
        content_analysis = None
        if include_content_analysis:
            logger.info("Analyzing content performance", correlation_id=correlation_id)
            content_analysis = await self.insight_generator.analyze_content_type_performance(
                workspace_id,
                move_id,
                correlation_id=correlation_id
            )

        # Step 6: Generate strategic recommendations
        logger.info("Generating strategic recommendations", correlation_id=correlation_id)
        recommendations = await self._generate_recommendations(
            move,
            metrics,
            insights_result,
            content_analysis,
            correlation_id
        )

        # Step 7: Compile final report
        report = {
            "move_id": str(move_id),
            "move_name": move.get("name"),
            "move_status": move.get("status"),
            "analysis_period_days": time_period_days,
            "analyzed_at": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "insights": insights_result.get("insights", []),
            "anomalies": insights_result.get("anomalies", []),
            "charts": charts,
            "content_analysis": content_analysis,
            "recommendations": recommendations,
            "summary": self._generate_executive_summary(
                metrics,
                insights_result,
                recommendations
            )
        }

        # Cache the report for quick access
        cache_key = f"analytics_report:{move_id}:{time_period_days}"
        await redis_cache.set(cache_key, report, ttl=300)  # 5 minute cache

        logger.info(
            "Analytics workflow completed",
            insights_count=len(insights_result.get("insights", [])),
            anomalies_count=len(insights_result.get("anomalies", [])),
            correlation_id=correlation_id
        )

        return report

    async def _validate_move(
        self,
        workspace_id: UUID,
        move_id: UUID,
        correlation_id: str
    ) -> Dict[str, Any]:
        """
        Validates that move exists and has completed content/execution stages.

        Args:
            workspace_id: User's workspace
            move_id: Campaign to validate
            correlation_id: Request correlation ID

        Returns:
            Move data if valid

        Raises:
            ValueError: If move not found or incomplete
        """
        logger.info("Validating move", move_id=move_id, correlation_id=correlation_id)

        # Check if move exists
        move = await supabase_client.fetch_one(
            "moves",
            {"id": str(move_id), "workspace_id": str(workspace_id)}
        )

        if not move:
            logger.error(
                "Move not found",
                move_id=move_id,
                workspace_id=workspace_id,
                correlation_id=correlation_id
            )
            raise ValueError(f"Move {move_id} not found or does not belong to workspace {workspace_id}")

        # Check if move has published content (completed content/execution stages)
        published_assets = await supabase_client.fetch_all(
            "assets",
            {"move_id": str(move_id), "status": "published"}
        )

        if not published_assets:
            logger.warning(
                "Move has no published content",
                move_id=move_id,
                move_status=move.get("status"),
                correlation_id=correlation_id
            )
            raise ValueError(
                f"Move {move_id} has no published content yet. "
                "Complete content creation and execution stages before running analytics."
            )

        logger.info(
            "Move validation successful",
            move_id=move_id,
            move_name=move.get("name"),
            published_assets_count=len(published_assets),
            correlation_id=correlation_id
        )

        return move

    async def _generate_recommendations(
        self,
        move: Dict[str, Any],
        metrics: Dict[str, Any],
        insights_result: Dict[str, Any],
        content_analysis: Optional[Dict[str, Any]],
        correlation_id: str
    ) -> List[str]:
        """
        Generates strategic recommendations using AI analysis.

        Args:
            move: Move data
            metrics: Collected metrics
            insights_result: Generated insights
            content_analysis: Content type performance analysis
            correlation_id: Request correlation ID

        Returns:
            List of actionable recommendations
        """
        # Compile insights from multiple sources
        all_insights = insights_result.get("insights", [])
        anomalies = insights_result.get("anomalies", [])

        # Extract key recommendations from insights
        recommendations = []

        for insight in all_insights:
            if insight.get("recommendation"):
                recommendations.append(insight["recommendation"])

        # Add content-based recommendations
        if content_analysis and content_analysis.get("recommendations"):
            recommendations.extend(content_analysis["recommendations"])

        # Generate AI-powered strategic recommendations
        try:
            aggregated_metrics = metrics.get("aggregated", {})

            prompt = f"""Based on this campaign performance data, provide 3-5 strategic recommendations for improvement.

**Campaign**: {move.get('name')}
**Goal**: {move.get('goal')}
**Channels**: {', '.join(move.get('channels', []))}
**Status**: {move.get('status')}

**Performance Summary**:
- Total Impressions: {aggregated_metrics.get('total_impressions', 0):,}
- Total Engagements: {aggregated_metrics.get('total_engagements', 0):,}
- Engagement Rate: {aggregated_metrics.get('engagement_rate', 0) * 100:.2f}%
- Total Clicks: {aggregated_metrics.get('total_clicks', 0):,}

**Key Insights**:
{json.dumps([i.get('title') for i in all_insights[:5]], indent=2)}

**Anomalies Detected**: {len(anomalies)}

Provide specific, actionable recommendations that:
1. Address underperforming areas
2. Capitalize on high-performing channels
3. Suggest content or strategy adjustments
4. Include expected impact

Return as JSON array of strings:
["Recommendation 1", "Recommendation 2", ...]
"""

            import json

            messages = [
                {
                    "role": "system",
                    "content": "You are a marketing strategist specializing in campaign optimization. Provide specific, actionable recommendations with expected impacts. Return ONLY a JSON array of strings."
                },
                {"role": "user", "content": prompt}
            ]

            llm_response = await self.llm.chat_completion(
                messages,
                model_type="reasoning",
                temperature=0.5,
                response_format={"type": "json_object"}
            )

            result = json.loads(llm_response)

            # Handle different response formats
            if isinstance(result, dict):
                if "recommendations" in result:
                    ai_recommendations = result["recommendations"]
                else:
                    # Take first list found
                    ai_recommendations = next(
                        (v for v in result.values() if isinstance(v, list)),
                        []
                    )
            else:
                ai_recommendations = result

            if ai_recommendations:
                recommendations.extend(ai_recommendations[:5])

        except Exception as e:
            logger.error(
                f"Failed to generate AI recommendations: {e}",
                correlation_id=correlation_id
            )

        # Deduplicate and limit
        unique_recommendations = list(dict.fromkeys(recommendations))[:10]

        return unique_recommendations

    def _generate_executive_summary(
        self,
        metrics: Dict[str, Any],
        insights_result: Dict[str, Any],
        recommendations: List[str]
    ) -> str:
        """Generates an executive summary of the analytics report."""

        aggregated = metrics.get("aggregated", {})
        insights = insights_result.get("insights", [])
        anomalies = insights_result.get("anomalies", [])

        # Count high-priority insights
        high_priority_insights = sum(1 for i in insights if i.get("priority") == "high")

        summary = f"""
Campaign Performance Summary:

📊 Metrics Overview:
- Impressions: {aggregated.get('total_impressions', 0):,}
- Engagements: {aggregated.get('total_engagements', 0):,}
- Engagement Rate: {aggregated.get('engagement_rate', 0) * 100:.2f}%
- Clicks: {aggregated.get('total_clicks', 0):,}

🔍 Key Findings:
- {len(insights)} insights generated
- {high_priority_insights} high-priority action items
- {len(anomalies)} anomalies detected

⚡ Top Recommendation:
{recommendations[0] if recommendations else "Continue monitoring performance"}

Platform Coverage: {len(metrics.get('platform_metrics', {}))} platforms analyzed
""".strip()

        return summary

    async def quick_pulse_check(
        self,
        workspace_id: UUID,
        move_id: UUID,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Quick health check for a move - lightweight analytics snapshot.

        Args:
            workspace_id: User's workspace
            move_id: Campaign to check
            correlation_id: Request correlation ID

        Returns:
            Quick snapshot of current performance
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info("Running quick pulse check", move_id=move_id, correlation_id=correlation_id)

        # Validate move exists (but don't require published content)
        move = await supabase_client.fetch_one(
            "moves",
            {"id": str(move_id), "workspace_id": str(workspace_id)}
        )

        if not move:
            raise ValueError(f"Move {move_id} not found")

        # Get latest metrics (24 hours)
        metrics = await self.metrics_collector.collect_metrics(
            workspace_id,
            move_id,
            time_range_days=1,
            correlation_id=correlation_id
        )

        aggregated = metrics.get("aggregated", {})

        # Simple health score (0-100)
        health_score = self._calculate_health_score(aggregated)

        return {
            "move_id": str(move_id),
            "move_name": move.get("name"),
            "health_score": health_score,
            "status": self._get_status_label(health_score),
            "last_24h_metrics": aggregated,
            "checked_at": datetime.utcnow().isoformat()
        }

    def _calculate_health_score(self, metrics: Dict[str, Any]) -> int:
        """Calculate a simple health score (0-100) based on metrics."""

        score = 50  # Base score

        engagement_rate = metrics.get("engagement_rate", 0)
        impressions = metrics.get("total_impressions", 0)

        # Adjust for engagement rate
        if engagement_rate >= 0.05:  # 5%+ is excellent
            score += 30
        elif engagement_rate >= 0.03:  # 3%+ is good
            score += 20
        elif engagement_rate >= 0.02:  # 2%+ is average
            score += 10
        elif engagement_rate < 0.01:  # <1% is poor
            score -= 20

        # Adjust for volume
        if impressions >= 10000:
            score += 20
        elif impressions >= 5000:
            score += 10
        elif impressions >= 1000:
            score += 5
        elif impressions < 100:
            score -= 10

        return max(0, min(100, score))

    def _get_status_label(self, health_score: int) -> str:
        """Convert health score to status label."""
        if health_score >= 80:
            return "excellent"
        elif health_score >= 60:
            return "good"
        elif health_score >= 40:
            return "fair"
        else:
            return "needs_attention"


# Global singleton instance
analytics_supervisor = AnalyticsSupervisor()
