"""
Insight Agent - Analyzes metrics to generate actionable insights.
Identifies underperforming channels, suggests pivots, and detects anomalies.
Generates charts and trend analysis for campaign performance.
"""

import json
import structlog
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timezone, timedelta

from backend.services.vertex_ai_client import vertex_ai_client
from backend.services.supabase_client import supabase_client
from backend.models.campaign import MoveAnomaly
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class InsightAgent:
    """
    Analyzes performance data and generates strategic insights.
    Uses AI to identify patterns, anomalies, and opportunities.
    """
    
    def __init__(self):
        self.llm = vertex_ai_client
    
    async def analyze_performance(
        self,
        workspace_id: UUID,
        move_id: UUID,
        time_period_days: int = 30,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Analyzes campaign performance and generates insights.
        
        Args:
            workspace_id: User's workspace
            move_id: Campaign to analyze
            time_period_days: Lookback period
            
        Returns:
            Insights dict with recommendations
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Analyzing performance", move_id=move_id, correlation_id=correlation_id)
        
        # Fetch historical metrics
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=time_period_days)
        metrics_data = await supabase_client.fetch_all(
            "metrics_snapshot",
            {"workspace_id": str(workspace_id), "move_id": str(move_id)}
        )
        
        # Filter by date
        recent_metrics = [
            m for m in metrics_data 
            if datetime.fromisoformat(m["collected_at"]) >= cutoff_date
        ]
        
        if not recent_metrics:
            return {
                "status": "insufficient_data",
                "message": "Not enough data to generate insights"
            }
        
        # Use AI to analyze
        insights = await self._generate_insights(recent_metrics, correlation_id)
        
        # Detect anomalies
        anomalies = await self._detect_anomalies(move_id, recent_metrics, correlation_id)
        
        # Store anomalies
        for anomaly in anomalies:
            await supabase_client.insert("move_anomalies", anomaly.model_dump())
        
        return {
            "insights": insights,
            "anomalies": [a.model_dump() for a in anomalies],
            "analyzed_period_days": time_period_days,
            "data_points": len(recent_metrics)
        }
    
    async def _generate_insights(
        self,
        metrics_data: List[Dict],
        correlation_id: str
    ) -> List[Dict[str, str]]:
        """Uses AI to generate insights from metrics."""

        # Summarize metrics for LLM (last 20 snapshots)
        recent_metrics = metrics_data[-20:]
        metrics_summary = json.dumps(recent_metrics, indent=2)

        # Calculate trends
        trend_analysis = self._calculate_trends(metrics_data)

        prompt = f"""Analyze this marketing campaign performance data and generate 5-7 actionable insights.

**Metrics Data** (chronological, most recent last):
{metrics_summary}

**Trend Analysis**:
{json.dumps(trend_analysis, indent=2)}

**Analysis Tasks**:
1. Identify which platforms/channels are performing best and worst
2. Spot engagement trends (improving, declining, stagnant) with specific percentages
3. Analyze engagement rate changes over time
4. Identify content type performance patterns
5. Compare metrics to industry benchmarks (B2B SaaS: ~2-3% engagement rate, email: ~15-20% open rate)
6. Suggest specific, actionable improvements (not generic advice)
7. Highlight any concerning patterns or anomalies
8. Identify opportunities for optimization

**Output Requirements**:
- Return ONLY a JSON array, no additional text
- Each insight must include specific data points and percentages
- Recommendations must be concrete and actionable
- Focus on "why" and "what to do next"

Output as JSON array:
[
  {{
    "type": "opportunity|warning|trend|channel_performance|content_insight",
    "title": "Brief insight title with key metric",
    "description": "Detailed explanation with specific data points and percentages",
    "recommendation": "Specific action to take with expected impact",
    "priority": "high|medium|low",
    "affected_channels": ["channel1", "channel2"],
    "metrics_referenced": {{"metric_name": value}}
  }}
]
"""

        messages = [
            {"role": "system", "content": "You are a senior data analyst specializing in marketing analytics and campaign optimization. Provide clear, data-driven, actionable insights with specific numbers and percentages. Always return valid JSON only."},
            {"role": "user", "content": prompt}
        ]

        try:
            # Use reasoning model for deep analysis
            llm_response = await self.llm.chat_completion(
                messages,
                model_type="reasoning",
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            # Parse response
            result = json.loads(llm_response)

            # Handle different response formats
            if isinstance(result, dict):
                if "insights" in result:
                    insights = result["insights"]
                elif "analysis" in result:
                    insights = result["analysis"]
                else:
                    # Wrap single insight
                    insights = [result]
            else:
                insights = result

            # Ensure it's a list
            if not isinstance(insights, list):
                insights = [insights]

            logger.info(f"Generated {len(insights)} insights", correlation_id=correlation_id)
            return insights

        except Exception as e:
            logger.error(f"Failed to generate insights: {e}", correlation_id=correlation_id)
            return [{
                "type": "error",
                "title": "Analysis Failed",
                "description": str(e),
                "recommendation": "Retry analysis with valid metrics data",
                "priority": "high",
                "affected_channels": [],
                "metrics_referenced": {}
            }]

    def _calculate_trends(self, metrics_data: List[Dict]) -> Dict[str, Any]:
        """Calculate trend analysis from historical metrics."""

        if len(metrics_data) < 2:
            return {"status": "insufficient_data"}

        # Group by platform
        platform_trends = {}

        for snapshot in metrics_data:
            platform = snapshot.get("platform")
            metrics = snapshot.get("metrics", {})
            timestamp = snapshot.get("collected_at")

            if platform not in platform_trends:
                platform_trends[platform] = {
                    "data_points": [],
                    "first": None,
                    "last": None
                }

            platform_trends[platform]["data_points"].append({
                "timestamp": timestamp,
                "metrics": metrics
            })

        # Calculate trends for each platform
        trends = {}

        for platform, data in platform_trends.items():
            if len(data["data_points"]) < 2:
                continue

            first = data["data_points"][0]["metrics"]
            last = data["data_points"][-1]["metrics"]

            # Calculate percent changes
            impressions_change = self._percent_change(
                first.get("impressions", 0),
                last.get("impressions", 0)
            )

            engagement_change = self._percent_change(
                first.get("engagements", 0),
                last.get("engagements", 0)
            )

            engagement_rate_change = self._percent_change(
                first.get("engagement_rate", 0),
                last.get("engagement_rate", 0)
            )

            trends[platform] = {
                "impressions_trend": "up" if impressions_change > 5 else "down" if impressions_change < -5 else "stable",
                "impressions_change_percent": round(impressions_change, 2),
                "engagement_trend": "up" if engagement_change > 5 else "down" if engagement_change < -5 else "stable",
                "engagement_change_percent": round(engagement_change, 2),
                "engagement_rate_trend": "up" if engagement_rate_change > 5 else "down" if engagement_rate_change < -5 else "stable",
                "engagement_rate_change_percent": round(engagement_rate_change, 2),
                "data_points": len(data["data_points"])
            }

        return trends

    def _percent_change(self, old_value: float, new_value: float) -> float:
        """Calculate percentage change between two values."""
        if old_value == 0:
            return 100.0 if new_value > 0 else 0.0
        return ((new_value - old_value) / old_value) * 100
    
    async def _detect_anomalies(
        self,
        move_id: UUID,
        metrics_data: List[Dict],
        correlation_id: str
    ) -> List[MoveAnomaly]:
        """Detects anomalies in performance metrics."""
        
        anomalies = []
        
        # Simple rule-based detection (can be enhanced with ML)
        for i, metric in enumerate(metrics_data[-5:]):  # Check last 5 snapshots
            platform = metric.get("platform")
            metrics = metric.get("metrics", {})
            
            # Detect sudden drops
            if i > 0:
                prev_metrics = metrics_data[-(6-i)].get("metrics", {})
                
                # Check engagement drop
                current_engagement = metrics.get("engagement", 0)
                prev_engagement = prev_metrics.get("engagement", 0)
                
                if prev_engagement > 0 and current_engagement < prev_engagement * 0.5:
                    anomalies.append(MoveAnomaly(
                        move_id=move_id,
                        type="underperformance",
                        description=f"{platform} engagement dropped by {int((1 - current_engagement/prev_engagement) * 100)}%",
                        severity="high",
                        resolution_suggestion=f"Review recent {platform} content quality and posting times"
                    ))
        
        return anomalies
    
    async def generate_chart_data(
        self,
        workspace_id: UUID,
        move_id: UUID,
        time_period_days: int = 30,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Generates chart data for visualization of campaign performance.

        Args:
            workspace_id: User's workspace
            move_id: Campaign to analyze
            time_period_days: Lookback period
            correlation_id: Request correlation ID

        Returns:
            Chart data structures for various visualizations
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Generating chart data", move_id=move_id, correlation_id=correlation_id)

        # Fetch historical metrics
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=time_period_days)
        metrics_data = await supabase_client.fetch_all(
            "metrics_snapshot",
            {"workspace_id": str(workspace_id), "move_id": str(move_id)}
        )

        # Filter by date and sort
        recent_metrics = sorted(
            [m for m in metrics_data if datetime.fromisoformat(m["collected_at"]) >= cutoff_date],
            key=lambda x: x["collected_at"]
        )

        if not recent_metrics:
            return {"status": "no_data"}

        # Generate time series data
        time_series = self._generate_time_series(recent_metrics)

        # Generate platform comparison
        platform_comparison = self._generate_platform_comparison(recent_metrics)

        # Generate engagement funnel
        engagement_funnel = self._generate_engagement_funnel(recent_metrics)

        return {
            "time_series": time_series,
            "platform_comparison": platform_comparison,
            "engagement_funnel": engagement_funnel,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    def _generate_time_series(self, metrics_data: List[Dict]) -> Dict[str, Any]:
        """Generate time series data for line charts."""

        # Group by date
        daily_data = {}

        for snapshot in metrics_data:
            date = snapshot["collected_at"][:10]  # YYYY-MM-DD
            metrics = snapshot.get("metrics", {})

            if date not in daily_data:
                daily_data[date] = {
                    "impressions": 0,
                    "engagements": 0,
                    "clicks": 0,
                    "engagement_rate": 0
                }

            daily_data[date]["impressions"] += metrics.get("impressions", 0)
            daily_data[date]["engagements"] += metrics.get("engagements", 0)
            daily_data[date]["clicks"] += metrics.get("clicks", 0)

        # Calculate engagement rates
        for date, data in daily_data.items():
            if data["impressions"] > 0:
                data["engagement_rate"] = round(data["engagements"] / data["impressions"], 4)

        # Format for charting libraries (e.g., Chart.js)
        labels = sorted(daily_data.keys())
        datasets = {
            "impressions": [daily_data[date]["impressions"] for date in labels],
            "engagements": [daily_data[date]["engagements"] for date in labels],
            "clicks": [daily_data[date]["clicks"] for date in labels],
            "engagement_rate": [daily_data[date]["engagement_rate"] * 100 for date in labels]  # As percentage
        }

        return {
            "labels": labels,
            "datasets": datasets,
            "chart_type": "line"
        }

    def _generate_platform_comparison(self, metrics_data: List[Dict]) -> Dict[str, Any]:
        """Generate platform comparison data for bar charts."""

        platform_totals = {}

        for snapshot in metrics_data:
            platform = snapshot.get("platform")
            metrics = snapshot.get("metrics", {})

            if platform not in platform_totals:
                platform_totals[platform] = {
                    "impressions": 0,
                    "engagements": 0,
                    "clicks": 0,
                    "engagement_rate": 0
                }

            platform_totals[platform]["impressions"] += metrics.get("impressions", 0)
            platform_totals[platform]["engagements"] += metrics.get("engagements", 0)
            platform_totals[platform]["clicks"] += metrics.get("clicks", 0)

        # Calculate engagement rates
        for platform, data in platform_totals.items():
            if data["impressions"] > 0:
                data["engagement_rate"] = round(data["engagements"] / data["impressions"], 4)

        # Format for bar charts
        labels = list(platform_totals.keys())
        datasets = {
            "impressions": [platform_totals[p]["impressions"] for p in labels],
            "engagements": [platform_totals[p]["engagements"] for p in labels],
            "engagement_rate": [platform_totals[p]["engagement_rate"] * 100 for p in labels]
        }

        return {
            "labels": labels,
            "datasets": datasets,
            "chart_type": "bar"
        }

    def _generate_engagement_funnel(self, metrics_data: List[Dict]) -> Dict[str, Any]:
        """Generate engagement funnel data."""

        total_impressions = 0
        total_engagements = 0
        total_clicks = 0

        for snapshot in metrics_data:
            metrics = snapshot.get("metrics", {})
            total_impressions += metrics.get("impressions", 0)
            total_engagements += metrics.get("engagements", 0)
            total_clicks += metrics.get("clicks", 0)

        # Engagement funnel stages
        funnel_stages = [
            {"stage": "Impressions", "count": total_impressions, "percentage": 100.0},
            {
                "stage": "Engagements",
                "count": total_engagements,
                "percentage": round((total_engagements / total_impressions * 100) if total_impressions > 0 else 0, 2)
            },
            {
                "stage": "Clicks",
                "count": total_clicks,
                "percentage": round((total_clicks / total_impressions * 100) if total_impressions > 0 else 0, 2)
            }
        ]

        return {
            "stages": funnel_stages,
            "chart_type": "funnel"
        }

    async def analyze_content_type_performance(
        self,
        workspace_id: UUID,
        move_id: UUID,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Analyzes performance by content type to identify what works best.

        Args:
            workspace_id: User's workspace
            move_id: Campaign to analyze
            correlation_id: Request correlation ID

        Returns:
            Performance breakdown by content type with recommendations
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Analyzing content type performance", move_id=move_id, correlation_id=correlation_id)

        # Fetch published assets for this move
        assets = await supabase_client.fetch_all(
            "assets",
            {"workspace_id": str(workspace_id), "move_id": str(move_id), "status": "published"}
        )

        if not assets:
            return {
                "status": "no_published_content",
                "message": "No published content found for this campaign"
            }

        # Group by content type
        content_type_performance = {}

        for asset in assets:
            content_type = asset.get("type", "unknown")
            metadata = asset.get("metadata", {})
            metrics = metadata.get("performance_metrics", {})

            if content_type not in content_type_performance:
                content_type_performance[content_type] = {
                    "count": 0,
                    "total_impressions": 0,
                    "total_engagements": 0,
                    "total_clicks": 0,
                    "avg_engagement_rate": 0
                }

            stats = content_type_performance[content_type]
            stats["count"] += 1
            stats["total_impressions"] += metrics.get("impressions", 0)
            stats["total_engagements"] += metrics.get("engagements", 0)
            stats["total_clicks"] += metrics.get("clicks", 0)

        # Calculate averages and rankings
        for content_type, stats in content_type_performance.items():
            if stats["total_impressions"] > 0:
                stats["avg_engagement_rate"] = round(
                    stats["total_engagements"] / stats["total_impressions"], 4
                )
            stats["avg_impressions_per_piece"] = round(stats["total_impressions"] / stats["count"], 2)
            stats["avg_engagements_per_piece"] = round(stats["total_engagements"] / stats["count"], 2)

        # Rank by engagement rate
        ranked_types = sorted(
            content_type_performance.items(),
            key=lambda x: x[1]["avg_engagement_rate"],
            reverse=True
        )

        return {
            "content_type_performance": content_type_performance,
            "ranked_by_engagement": [
                {
                    "content_type": ct,
                    "engagement_rate": stats["avg_engagement_rate"],
                    "total_pieces": stats["count"]
                }
                for ct, stats in ranked_types
            ],
            "recommendations": self._generate_content_recommendations(ranked_types)
        }

    def _generate_content_recommendations(
        self,
        ranked_types: List[tuple]
    ) -> List[str]:
        """Generate recommendations based on content type performance."""

        recommendations = []

        if len(ranked_types) == 0:
            return ["Create and publish more content to gather performance data"]

        # Top performer
        top_type, top_stats = ranked_types[0]
        recommendations.append(
            f"Double down on {top_type} content - it has the highest engagement rate at {top_stats['avg_engagement_rate']*100:.2f}%"
        )

        # Bottom performer
        if len(ranked_types) > 1:
            bottom_type, bottom_stats = ranked_types[-1]
            if bottom_stats["avg_engagement_rate"] < 0.01:  # Less than 1%
                recommendations.append(
                    f"Consider pausing or reworking {bottom_type} content - engagement rate is only {bottom_stats['avg_engagement_rate']*100:.2f}%"
                )

        # Volume recommendations
        total_pieces = sum(stats["count"] for _, stats in ranked_types)
        if total_pieces < 10:
            recommendations.append(
                "Increase content volume to get more reliable performance insights (aim for 10+ pieces per type)"
            )

        return recommendations

    async def suggest_pivot(
        self,
        workspace_id: UUID,
        move_id: UUID,
        correlation_id: str = None
    ) -> Dict[str, Any]:
        """
        Suggests strategic pivots based on performance analysis.
        """
        correlation_id = correlation_id or get_correlation_id()
        logger.info("Suggesting pivot", move_id=move_id, correlation_id=correlation_id)
        
        # Get performance analysis
        performance = await self.analyze_performance(workspace_id, move_id, 14, correlation_id)
        
        # Get move details
        move_data = await supabase_client.fetch_one("moves", {"id": str(move_id)})
        
        prompt = f"""Based on this campaign's performance, suggest a strategic pivot.

**Campaign**: {move_data.get('name')}
**Current Performance**: {json.dumps(performance)}

**Pivot Options**:
1. Channel Shift (move budget from underperforming to high-performing channels)
2. Content Format Change (try different formats)
3. Audience Refinement (adjust targeting)
4. Timing Optimization (change posting schedule)
5. Messaging Adjustment (update value proposition)

Suggest the best pivot with rationale. Output as JSON:
{{
  "pivot_type": "channel_shift|format_change|audience|timing|messaging",
  "recommendation": "Specific action",
  "rationale": "Why this pivot",
  "expected_impact": "Predicted outcome",
  "effort": "low|medium|high"
}}
"""
        
        messages = [
            {"role": "system", "content": "You are a marketing strategist specializing in campaign optimization."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            llm_response = await self.llm.chat_completion(
                messages,
                model_type="reasoning",
                temperature=0.6,
                response_format={"type": "json_object"}
            )
            
            return json.loads(llm_response)
            
        except Exception as e:
            logger.error(f"Failed to suggest pivot: {e}", correlation_id=correlation_id)
            return {"error": str(e)}


insight_agent = InsightAgent()





