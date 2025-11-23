"""
Meta-Learning Service - Learn from past performance and optimize strategies.

Provides:
- Strategy effectiveness analysis
- Campaign performance learning
- Pattern recognition in successful content
- Automated optimization recommendations
- Continuous improvement tracking
"""

import structlog
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from backend.services.supabase_client import supabase_client

logger = structlog.get_logger(__name__)


class MetaLearningService:
    """
    Meta-learning service that learns from historical performance to improve future outcomes.

    Features:
    - Analyze what works and what doesn't
    - Identify successful patterns
    - Generate optimization recommendations
    - Track improvement over time
    - Learn from A/B test results
    """

    def __init__(self):
        """Initialize meta-learning service."""
        self.min_learning_samples = 20
        logger.info("Meta-learning service initialized")

    async def learn_from_performance(
        self,
        workspace_id: str,
        time_period_days: int = 90,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Learn from historical performance data.

        Args:
            workspace_id: Workspace identifier
            time_period_days: Look back period in days
            correlation_id: Correlation ID for tracking

        Returns:
            Learning insights and recommendations
        """
        try:
            # Get historical performance data
            historical_data = await self._get_performance_data(
                workspace_id,
                time_period_days
            )

            if len(historical_data) < self.min_learning_samples:
                logger.warning(
                    "Insufficient data for meta-learning",
                    workspace_id=workspace_id,
                    samples=len(historical_data),
                    correlation_id=correlation_id
                )
                return {
                    "learning_available": False,
                    "reason": "insufficient_data",
                    "samples_found": len(historical_data),
                    "samples_needed": self.min_learning_samples
                }

            # Analyze patterns
            content_patterns = await self._analyze_content_patterns(historical_data)
            timing_patterns = await self._analyze_timing_patterns(historical_data)
            platform_insights = await self._analyze_platform_performance(historical_data)
            improvement_trends = await self._analyze_improvement_trends(historical_data)

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                content_patterns,
                timing_patterns,
                platform_insights
            )

            result = {
                "learning_available": True,
                "workspace_id": workspace_id,
                "analysis_period_days": time_period_days,
                "samples_analyzed": len(historical_data),
                "content_patterns": content_patterns,
                "timing_patterns": timing_patterns,
                "platform_insights": platform_insights,
                "improvement_trends": improvement_trends,
                "recommendations": recommendations,
                "learned_at": datetime.utcnow().isoformat()
            }

            logger.info(
                "Meta-learning completed",
                workspace_id=workspace_id,
                samples_analyzed=len(historical_data),
                recommendations_count=len(recommendations),
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            logger.error(
                f"Meta-learning failed: {e}",
                workspace_id=workspace_id,
                correlation_id=correlation_id
            )
            return {
                "learning_available": False,
                "error": str(e)
            }

    async def track_strategy_effectiveness(
        self,
        workspace_id: str,
        strategy_id: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track and analyze effectiveness of a specific strategy.

        Args:
            workspace_id: Workspace identifier
            strategy_id: Strategy identifier
            correlation_id: Correlation ID for tracking

        Returns:
            Strategy effectiveness analysis
        """
        try:
            # Get content published under this strategy
            strategy_content = await supabase_client.query(
                "content_performance",
                filters={
                    "workspace_id": workspace_id,
                    "strategy_id": strategy_id
                }
            )

            if not strategy_content:
                return {
                    "tracking_available": False,
                    "reason": "no_published_content"
                }

            # Calculate aggregate metrics
            total_posts = len(strategy_content)
            engagement_rates = [
                item.get("metrics", {}).get("engagement_rate", 0)
                for item in strategy_content
            ]
            avg_engagement = np.mean(engagement_rates) if engagement_rates else 0
            std_engagement = np.std(engagement_rates) if len(engagement_rates) > 1 else 0

            # Determine effectiveness
            if avg_engagement > 5.0:
                effectiveness = "high"
            elif avg_engagement > 2.0:
                effectiveness = "medium"
            else:
                effectiveness = "low"

            result = {
                "tracking_available": True,
                "strategy_id": strategy_id,
                "total_posts": total_posts,
                "avg_engagement_rate": round(avg_engagement, 2),
                "engagement_std": round(std_engagement, 2),
                "effectiveness": effectiveness,
                "consistency_score": round(self._calculate_consistency(engagement_rates), 2),
                "tracked_at": datetime.utcnow().isoformat()
            }

            logger.info(
                "Strategy effectiveness tracked",
                strategy_id=strategy_id,
                effectiveness=effectiveness,
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            logger.error(
                f"Strategy tracking failed: {e}",
                strategy_id=strategy_id,
                correlation_id=correlation_id
            )
            return {
                "tracking_available": False,
                "error": str(e)
            }

    async def learn_from_ab_test(
        self,
        workspace_id: str,
        test_id: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Learn from A/B test results.

        Args:
            workspace_id: Workspace identifier
            test_id: A/B test identifier
            correlation_id: Correlation ID for tracking

        Returns:
            Learnings from A/B test
        """
        try:
            # Get A/B test results
            test_results = await supabase_client.query_one(
                "ab_tests",
                filters={
                    "workspace_id": workspace_id,
                    "test_id": test_id
                }
            )

            if not test_results:
                return {
                    "learning_available": False,
                    "reason": "test_not_found"
                }

            variants = test_results.get("variants", [])
            winner = test_results.get("winner")

            # Extract learnings
            learnings = []

            if winner:
                winner_data = next((v for v in variants if v["id"] == winner), None)

                if winner_data:
                    # Analyze what made the winner successful
                    winner_features = winner_data.get("features", {})

                    for feature, value in winner_features.items():
                        learnings.append({
                            "feature": feature,
                            "winning_value": value,
                            "confidence": "high" if test_results.get("statistical_significance", 0) > 0.95 else "medium",
                            "recommendation": f"Use {feature}={value} in future content"
                        })

            result = {
                "learning_available": True,
                "test_id": test_id,
                "winner": winner,
                "learnings": learnings,
                "statistical_significance": test_results.get("statistical_significance", 0),
                "learned_at": datetime.utcnow().isoformat()
            }

            logger.info(
                "A/B test learning completed",
                test_id=test_id,
                learnings_count=len(learnings),
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            logger.error(
                f"A/B test learning failed: {e}",
                test_id=test_id,
                correlation_id=correlation_id
            )
            return {
                "learning_available": False,
                "error": str(e)
            }

    # ========== Helper Methods ==========

    async def _get_performance_data(
        self,
        workspace_id: str,
        time_period_days: int
    ) -> List[Dict[str, Any]]:
        """Get performance data for learning."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=time_period_days)

            data = await supabase_client.query(
                "content_performance",
                filters={"workspace_id": workspace_id},
                limit=500
            )

            # Filter by date
            filtered_data = [
                item for item in (data or [])
                if item.get("published_at") and
                datetime.fromisoformat(item["published_at"].replace('Z', '+00:00')) >= cutoff_date
            ]

            return filtered_data

        except Exception as e:
            logger.warning(f"Failed to get performance data: {e}")
            return []

    async def _analyze_content_patterns(
        self,
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze what content patterns lead to success."""
        # Group by content type
        content_types = {}

        for item in historical_data:
            content_type = item.get("content_type", "unknown")
            engagement = item.get("metrics", {}).get("engagement_rate", 0)

            if content_type not in content_types:
                content_types[content_type] = []

            content_types[content_type].append(engagement)

        # Calculate average engagement by type
        type_performance = {
            ctype: {
                "avg_engagement": round(np.mean(rates), 2),
                "count": len(rates)
            }
            for ctype, rates in content_types.items()
        }

        # Find best performing type
        best_type = max(type_performance.items(), key=lambda x: x[1]["avg_engagement"])

        return {
            "by_content_type": type_performance,
            "best_performing_type": best_type[0],
            "best_type_engagement": best_type[1]["avg_engagement"]
        }

    async def _analyze_timing_patterns(
        self,
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze timing patterns."""
        day_performance = {i: [] for i in range(7)}

        for item in historical_data:
            published_at = item.get("published_at")
            if not published_at:
                continue

            try:
                dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                day_of_week = dt.weekday()
                engagement = item.get("metrics", {}).get("engagement_rate", 0)
                day_performance[day_of_week].append(engagement)
            except Exception:
                continue

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_avg = {
            day_names[day]: round(np.mean(rates), 2) if rates else 0
            for day, rates in day_performance.items()
        }

        best_day = max(day_avg.items(), key=lambda x: x[1])

        return {
            "by_day_of_week": day_avg,
            "best_day": best_day[0],
            "best_day_engagement": best_day[1]
        }

    async def _analyze_platform_performance(
        self,
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze platform-specific performance."""
        platform_performance = {}

        for item in historical_data:
            platform = item.get("platform", "unknown")
            engagement = item.get("metrics", {}).get("engagement_rate", 0)

            if platform not in platform_performance:
                platform_performance[platform] = []

            platform_performance[platform].append(engagement)

        platform_avg = {
            platform: {
                "avg_engagement": round(np.mean(rates), 2),
                "count": len(rates)
            }
            for platform, rates in platform_performance.items()
        }

        best_platform = max(platform_avg.items(), key=lambda x: x[1]["avg_engagement"])

        return {
            "by_platform": platform_avg,
            "best_platform": best_platform[0],
            "best_platform_engagement": best_platform[1]["avg_engagement"]
        }

    async def _analyze_improvement_trends(
        self,
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze if performance is improving over time."""
        # Sort by date
        sorted_data = sorted(
            historical_data,
            key=lambda x: x.get("published_at", "")
        )

        # Split into first half and second half
        mid_point = len(sorted_data) // 2
        first_half = sorted_data[:mid_point]
        second_half = sorted_data[mid_point:]

        first_half_engagement = np.mean([
            item.get("metrics", {}).get("engagement_rate", 0)
            for item in first_half
        ]) if first_half else 0

        second_half_engagement = np.mean([
            item.get("metrics", {}).get("engagement_rate", 0)
            for item in second_half
        ]) if second_half else 0

        improvement = second_half_engagement - first_half_engagement
        improvement_pct = (improvement / first_half_engagement * 100) if first_half_engagement > 0 else 0

        if improvement_pct > 10:
            trend = "improving"
        elif improvement_pct < -10:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "first_period_avg": round(first_half_engagement, 2),
            "second_period_avg": round(second_half_engagement, 2),
            "improvement_percentage": round(improvement_pct, 2),
            "trend": trend
        }

    async def _generate_recommendations(
        self,
        content_patterns: Dict[str, Any],
        timing_patterns: Dict[str, Any],
        platform_insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on learnings."""
        recommendations = []

        # Content type recommendation
        best_content_type = content_patterns.get("best_performing_type")
        if best_content_type:
            recommendations.append({
                "category": "content_type",
                "priority": "high",
                "recommendation": f"Focus on {best_content_type} content",
                "reason": f"Shows {content_patterns['best_type_engagement']}% avg engagement",
                "confidence": "high"
            })

        # Timing recommendation
        best_day = timing_patterns.get("best_day")
        if best_day:
            recommendations.append({
                "category": "timing",
                "priority": "medium",
                "recommendation": f"Post on {best_day}",
                "reason": f"Highest engagement on {best_day}",
                "confidence": "medium"
            })

        # Platform recommendation
        best_platform = platform_insights.get("best_platform")
        if best_platform:
            recommendations.append({
                "category": "platform",
                "priority": "high",
                "recommendation": f"Prioritize {best_platform}",
                "reason": f"{best_platform} shows best engagement",
                "confidence": "high"
            })

        return recommendations

    def _calculate_consistency(self, values: List[float]) -> float:
        """Calculate consistency score (0-100) based on variance."""
        if not values or len(values) < 2:
            return 0.0

        mean_val = np.mean(values)
        std_val = np.std(values)

        # Coefficient of variation
        cv = std_val / mean_val if mean_val > 0 else 1.0

        # Convert to consistency score (lower CV = higher consistency)
        consistency = max(0, min(100, (1 - cv) * 100))

        return consistency


# Global meta-learning instance
meta_learner = MetaLearningService()
