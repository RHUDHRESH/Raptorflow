"""
Performance Prediction Service - Predict content performance before publishing.

Provides:
- Content performance prediction using historical data
- Engagement forecasting
- Platform-specific predictions
- A/B test recommendations
- Optimal posting time suggestions
"""

import structlog
from typing import Dict, List, Any, Optional, Literal
from datetime import datetime, timedelta, timezone
import numpy as np
from backend.services.supabase_client import supabase_client

logger = structlog.get_logger(__name__)


class PerformancePredictionService:
    """
    Performance prediction service using historical data and ML models.

    Features:
    - Predict engagement metrics before publishing
    - Analyze historical performance patterns
    - Recommend optimal posting times
    - Platform-specific predictions
    - A/B test suggestions
    """

    def __init__(self):
        """Initialize performance prediction service."""
        self.min_historical_data = 10  # Minimum posts needed for predictions
        logger.info("Performance prediction service initialized")

    async def predict_performance(
        self,
        workspace_id: str,
        content_type: str,
        platform: str,
        content_features: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predict content performance metrics.

        Args:
            workspace_id: Workspace identifier
            content_type: Type of content (blog, email, social_post)
            platform: Target platform (linkedin, twitter, etc.)
            content_features: Content characteristics (length, tone, topics, etc.)
            correlation_id: Correlation ID for tracking

        Returns:
            Performance predictions with confidence scores
        """
        try:
            # Get historical performance data
            historical_data = await self._get_historical_performance(
                workspace_id,
                content_type,
                platform
            )

            if len(historical_data) < self.min_historical_data:
                logger.warning(
                    "Insufficient historical data for prediction",
                    workspace_id=workspace_id,
                    data_points=len(historical_data),
                    correlation_id=correlation_id
                )
                return {
                    "prediction_available": False,
                    "reason": "insufficient_data",
                    "min_required": self.min_historical_data,
                    "current_data_points": len(historical_data),
                    "message": f"Need at least {self.min_historical_data} historical posts for accurate predictions"
                }

            # Extract features and train simple model
            predictions = await self._generate_predictions(
                historical_data,
                content_features,
                platform
            )

            logger.info(
                "Performance prediction completed",
                workspace_id=workspace_id,
                platform=platform,
                predicted_engagement=predictions["predicted_engagement"],
                correlation_id=correlation_id
            )

            return {
                "prediction_available": True,
                "content_type": content_type,
                "platform": platform,
                **predictions,
                "predicted_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(
                f"Performance prediction failed: {e}",
                workspace_id=workspace_id,
                correlation_id=correlation_id
            )
            return {
                "prediction_available": False,
                "error": str(e)
            }

    async def predict_optimal_time(
        self,
        workspace_id: str,
        platform: str,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predict optimal posting times based on historical engagement.

        Args:
            workspace_id: Workspace identifier
            platform: Target platform
            correlation_id: Correlation ID for tracking

        Returns:
            Optimal posting time recommendations
        """
        try:
            # Get historical performance with timestamps
            historical_data = await self._get_historical_performance(
                workspace_id,
                platform=platform,
                include_timestamps=True
            )

            if len(historical_data) < self.min_historical_data:
                return {
                    "prediction_available": False,
                    "reason": "insufficient_data"
                }

            # Analyze engagement by time patterns
            time_analysis = self._analyze_time_patterns(historical_data)

            logger.info(
                "Optimal time prediction completed",
                workspace_id=workspace_id,
                platform=platform,
                best_day=time_analysis["best_day_of_week"],
                best_hour=time_analysis["best_hour"],
                correlation_id=correlation_id
            )

            return {
                "prediction_available": True,
                "platform": platform,
                **time_analysis,
                "predicted_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(
                f"Optimal time prediction failed: {e}",
                workspace_id=workspace_id,
                correlation_id=correlation_id
            )
            return {
                "prediction_available": False,
                "error": str(e)
            }

    async def suggest_ab_tests(
        self,
        workspace_id: str,
        content_variants: List[Dict[str, Any]],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Suggest A/B test configurations and predict outcomes.

        Args:
            workspace_id: Workspace identifier
            content_variants: List of content variants to test
            correlation_id: Correlation ID for tracking

        Returns:
            A/B test recommendations
        """
        try:
            if len(content_variants) < 2:
                return {
                    "error": "At least 2 variants required for A/B testing"
                }

            # Analyze each variant
            variant_predictions = []

            for i, variant in enumerate(content_variants):
                prediction = await self.predict_performance(
                    workspace_id=workspace_id,
                    content_type=variant.get("content_type", "social_post"),
                    platform=variant.get("platform", "linkedin"),
                    content_features=variant.get("features", {}),
                    correlation_id=correlation_id
                )

                variant_predictions.append({
                    "variant_id": i,
                    "variant_name": variant.get("name", f"Variant {i+1}"),
                    "prediction": prediction
                })

            # Determine recommended approach
            recommendation = self._generate_ab_recommendation(variant_predictions)

            logger.info(
                "A/B test suggestion completed",
                workspace_id=workspace_id,
                variants_count=len(content_variants),
                correlation_id=correlation_id
            )

            return {
                "variants": variant_predictions,
                "recommendation": recommendation,
                "suggested_split": self._suggest_traffic_split(variant_predictions),
                "estimated_duration_days": self._estimate_test_duration(workspace_id),
                "predicted_at": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error(
                f"A/B test suggestion failed: {e}",
                workspace_id=workspace_id,
                correlation_id=correlation_id
            )
            return {"error": str(e)}

    # ========== Helper Methods ==========

    async def _get_historical_performance(
        self,
        workspace_id: str,
        content_type: Optional[str] = None,
        platform: Optional[str] = None,
        include_timestamps: bool = False,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get historical performance data from database."""
        try:
            filters = {"workspace_id": workspace_id}

            if content_type:
                filters["content_type"] = content_type

            if platform:
                filters["platform"] = platform

            # Query published content with performance metrics
            data = await supabase_client.query(
                "content_performance",
                filters=filters,
                limit=limit,
                order_by="published_at.desc"
            )

            return data or []

        except Exception as e:
            logger.warning(f"Failed to get historical data: {e}")
            return []

    async def _generate_predictions(
        self,
        historical_data: List[Dict[str, Any]],
        content_features: Dict[str, Any],
        platform: str
    ) -> Dict[str, Any]:
        """Generate performance predictions using simple statistical model."""
        # Extract metrics from historical data
        engagement_rates = []
        impressions = []
        clicks = []

        for item in historical_data:
            metrics = item.get("metrics", {})
            engagement_rates.append(metrics.get("engagement_rate", 0))
            impressions.append(metrics.get("impressions", 0))
            clicks.append(metrics.get("clicks", 0))

        # Calculate statistics
        avg_engagement = np.mean(engagement_rates) if engagement_rates else 0
        std_engagement = np.std(engagement_rates) if len(engagement_rates) > 1 else 0
        avg_impressions = np.mean(impressions) if impressions else 0
        avg_clicks = np.mean(clicks) if clicks else 0

        # Adjust predictions based on content features
        feature_multiplier = 1.0

        # Content length impact
        if "word_count" in content_features:
            word_count = content_features["word_count"]
            if platform == "twitter" and word_count < 100:
                feature_multiplier *= 1.1  # Short tweets perform better
            elif platform == "linkedin" and 300 <= word_count <= 1000:
                feature_multiplier *= 1.15  # Medium posts perform better

        # Topic relevance (mock - in production use ML)
        if content_features.get("has_hashtags"):
            feature_multiplier *= 1.05

        if content_features.get("has_media"):
            feature_multiplier *= 1.2  # Media significantly boosts engagement

        # Generate predictions
        predicted_engagement = avg_engagement * feature_multiplier
        predicted_impressions = int(avg_impressions * feature_multiplier)
        predicted_clicks = int(avg_clicks * feature_multiplier)

        # Calculate confidence (higher with more data and lower variance)
        data_confidence = min(1.0, len(historical_data) / 50)
        variance_confidence = 1.0 - min(1.0, std_engagement / (avg_engagement + 0.01))
        overall_confidence = (data_confidence * 0.6 + variance_confidence * 0.4) * 100

        return {
            "predicted_engagement_rate": round(predicted_engagement, 2),
            "predicted_impressions": predicted_impressions,
            "predicted_clicks": predicted_clicks,
            "confidence_score": round(overall_confidence, 2),
            "historical_avg_engagement": round(avg_engagement, 2),
            "data_points_used": len(historical_data),
            "performance_range": {
                "min": round(max(0, predicted_engagement - std_engagement), 2),
                "max": round(predicted_engagement + std_engagement, 2)
            }
        }

    def _analyze_time_patterns(
        self,
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze engagement patterns by time."""
        # Group by day of week and hour
        day_performance = {i: [] for i in range(7)}  # 0=Monday, 6=Sunday
        hour_performance = {i: [] for i in range(24)}

        for item in historical_data:
            published_at = item.get("published_at")
            if not published_at:
                continue

            try:
                dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                day_of_week = dt.weekday()
                hour = dt.hour

                engagement = item.get("metrics", {}).get("engagement_rate", 0)
                day_performance[day_of_week].append(engagement)
                hour_performance[hour].append(engagement)

            except Exception:
                continue

        # Calculate average engagement for each day/hour
        day_avg = {day: np.mean(rates) if rates else 0 for day, rates in day_performance.items()}
        hour_avg = {hour: np.mean(rates) if rates else 0 for hour, rates in hour_performance.items()}

        best_day = max(day_avg.items(), key=lambda x: x[1])
        best_hour = max(hour_avg.items(), key=lambda x: x[1])

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        return {
            "best_day_of_week": day_names[best_day[0]],
            "best_day_engagement": round(best_day[1], 2),
            "best_hour": best_hour[0],
            "best_hour_engagement": round(best_hour[1], 2),
            "recommended_posting_time": f"{day_names[best_day[0]]} at {best_hour[0]:02d}:00",
            "day_breakdown": {day_names[day]: round(eng, 2) for day, eng in day_avg.items()},
            "hour_breakdown": {f"{h:02d}:00": round(eng, 2) for h, eng in hour_avg.items()}
        }

    def _generate_ab_recommendation(
        self,
        variant_predictions: List[Dict[str, Any]]
    ) -> str:
        """Generate A/B test recommendation."""
        # Find variant with highest predicted engagement
        best_variant = max(
            variant_predictions,
            key=lambda x: x["prediction"].get("predicted_engagement_rate", 0)
        )

        best_engagement = best_variant["prediction"].get("predicted_engagement_rate", 0)

        # Check if difference is significant
        other_variants = [v for v in variant_predictions if v["variant_id"] != best_variant["variant_id"]]

        if other_variants:
            avg_other_engagement = np.mean([
                v["prediction"].get("predicted_engagement_rate", 0)
                for v in other_variants
            ])

            if best_engagement > avg_other_engagement * 1.2:
                return f"Variant '{best_variant['variant_name']}' shows 20%+ higher predicted engagement. Consider 70/30 split favoring this variant."
            else:
                return "Predictions are close. Recommend 50/50 split for unbiased results."
        else:
            return "Run balanced test to gather data."

    def _suggest_traffic_split(
        self,
        variant_predictions: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Suggest traffic split percentages."""
        total_variants = len(variant_predictions)

        # Simple equal split for now
        # In production, could use Thompson Sampling or UCB for adaptive splits
        split = {
            v["variant_name"]: round(100 / total_variants, 1)
            for v in variant_predictions
        }

        return split

    def _estimate_test_duration(self, workspace_id: str) -> int:
        """Estimate A/B test duration in days."""
        # In production, calculate based on historical traffic
        # For now, return reasonable default
        return 7  # 1 week


# Global performance prediction instance
performance_predictor = PerformancePredictionService()
