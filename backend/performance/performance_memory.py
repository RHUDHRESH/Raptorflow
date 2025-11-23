"""
Performance Memory System for historical data and continuous learning.

This module provides a centralized interface for storing and retrieving
performance data, predictions, and actual results. It enables the ML models
to learn from past predictions and improve over time.

Features:
- Store historical performance metrics
- Track prediction accuracy
- Update ML model weights based on actual results
- Provide aggregated insights for benchmarking
- Manage A/B test results
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from uuid import UUID
import structlog
from backend.services.supabase_client import supabase_client

logger = structlog.get_logger()


class PerformanceMemory:
    """
    Memory system for performance predictions and actual results.

    This class manages the storage and retrieval of:
    - Content performance metrics (actual)
    - Performance predictions
    - A/B test results
    - Competitor benchmarks
    - Model accuracy metrics
    """

    def __init__(self):
        """Initialize the performance memory system."""
        self.db = supabase_client
        self.cache = {}  # In-memory cache for frequently accessed data

    async def store_prediction(
        self,
        content_id: str,
        prediction_type: str,
        predictions: Dict[str, Any],
        confidence: float,
        model_version: str = "1.0"
    ) -> Dict[str, Any]:
        """
        Store a performance prediction for later comparison with actual results.

        Args:
            content_id: Unique identifier for the content
            prediction_type: Type of prediction (engagement, conversion, viral)
            predictions: Dictionary of predicted metrics
            confidence: Confidence level (0.0-1.0)
            model_version: Version of the model used

        Returns:
            Stored prediction record
        """
        try:
            prediction_data = {
                "content_id": content_id,
                "prediction_type": prediction_type,
                "predictions": predictions,
                "confidence": confidence,
                "model_version": model_version,
                "created_at": datetime.utcnow().isoformat(),
                "actual_results": None,
                "accuracy_score": None
            }

            result = await self.db.insert("performance_predictions", prediction_data)
            logger.info(
                "Stored performance prediction",
                content_id=content_id,
                prediction_type=prediction_type
            )
            return result

        except Exception as e:
            logger.error("Failed to store prediction", error=str(e))
            raise

    async def store_actual_results(
        self,
        content_id: str,
        actual_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store actual performance results and calculate prediction accuracy.

        Args:
            content_id: Unique identifier for the content
            actual_metrics: Dictionary of actual performance metrics

        Returns:
            Updated prediction record with accuracy score
        """
        try:
            # Store actual results
            results_data = {
                "content_id": content_id,
                "metrics": actual_metrics,
                "recorded_at": datetime.utcnow().isoformat()
            }

            await self.db.insert("performance_results", results_data)

            # Update predictions with actual results and calculate accuracy
            predictions = await self.db.fetch_all(
                "performance_predictions",
                {"content_id": content_id}
            )

            for prediction in predictions:
                accuracy = self._calculate_accuracy(
                    prediction.get("predictions", {}),
                    actual_metrics
                )

                await self.db.update(
                    "performance_predictions",
                    {"content_id": content_id, "prediction_type": prediction["prediction_type"]},
                    {
                        "actual_results": actual_metrics,
                        "accuracy_score": accuracy,
                        "updated_at": datetime.utcnow().isoformat()
                    }
                )

            logger.info(
                "Stored actual results and updated predictions",
                content_id=content_id
            )
            return results_data

        except Exception as e:
            logger.error("Failed to store actual results", error=str(e))
            raise

    def _calculate_accuracy(
        self,
        predictions: Dict[str, Any],
        actuals: Dict[str, Any]
    ) -> float:
        """
        Calculate accuracy score between predictions and actual results.

        Uses Mean Absolute Percentage Error (MAPE) for numeric metrics.

        Args:
            predictions: Predicted metrics
            actuals: Actual metrics

        Returns:
            Accuracy score (0.0-1.0), where 1.0 is perfect accuracy
        """
        if not predictions or not actuals:
            return 0.0

        errors = []
        for key in predictions:
            if key in actuals and isinstance(predictions[key], (int, float)):
                actual_val = actuals[key]
                pred_val = predictions[key]

                if actual_val != 0:
                    error = abs((actual_val - pred_val) / actual_val)
                    errors.append(error)

        if not errors:
            return 0.0

        # Convert MAPE to accuracy score (lower error = higher accuracy)
        mape = sum(errors) / len(errors)
        accuracy = max(0.0, 1.0 - mape)
        return min(1.0, accuracy)

    async def get_historical_performance(
        self,
        workspace_id: str,
        content_type: Optional[str] = None,
        platform: Optional[str] = None,
        days_back: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Retrieve historical performance data for training ML models.

        Args:
            workspace_id: Workspace identifier
            content_type: Filter by content type (optional)
            platform: Filter by platform (optional)
            days_back: Number of days to look back

        Returns:
            List of historical performance records
        """
        try:
            # Build cache key
            cache_key = f"{workspace_id}_{content_type}_{platform}_{days_back}"

            # Check cache
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if cached_data["timestamp"] > datetime.utcnow() - timedelta(hours=1):
                    return cached_data["data"]

            # Query from database
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)

            # This is a simplified query - in production, you'd use more complex filtering
            results = await self.db.fetch_all("performance_results")

            # Filter results
            filtered_results = [
                r for r in results
                if datetime.fromisoformat(r.get("recorded_at", "")) > cutoff_date
            ]

            # Cache results
            self.cache[cache_key] = {
                "data": filtered_results,
                "timestamp": datetime.utcnow()
            }

            return filtered_results

        except Exception as e:
            logger.error("Failed to get historical performance", error=str(e))
            return []

    async def get_prediction_accuracy_trends(
        self,
        prediction_type: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze prediction accuracy trends over time.

        Args:
            prediction_type: Type of prediction to analyze
            days_back: Number of days to analyze

        Returns:
            Dictionary with accuracy trends and statistics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)

            predictions = await self.db.fetch_all(
                "performance_predictions",
                {"prediction_type": prediction_type}
            )

            # Filter by date and only include predictions with actual results
            recent_predictions = [
                p for p in predictions
                if p.get("actual_results") is not None
                and datetime.fromisoformat(p.get("created_at", "")) > cutoff_date
            ]

            if not recent_predictions:
                return {
                    "average_accuracy": 0.0,
                    "trend": "insufficient_data",
                    "sample_size": 0
                }

            accuracies = [p.get("accuracy_score", 0.0) for p in recent_predictions]
            avg_accuracy = sum(accuracies) / len(accuracies)

            # Calculate trend (simple: compare first half vs second half)
            mid_point = len(accuracies) // 2
            first_half_avg = sum(accuracies[:mid_point]) / mid_point if mid_point > 0 else 0
            second_half_avg = sum(accuracies[mid_point:]) / (len(accuracies) - mid_point)

            trend = "improving" if second_half_avg > first_half_avg else "declining"

            return {
                "average_accuracy": avg_accuracy,
                "trend": trend,
                "sample_size": len(recent_predictions),
                "first_period_accuracy": first_half_avg,
                "second_period_accuracy": second_half_avg
            }

        except Exception as e:
            logger.error("Failed to get accuracy trends", error=str(e))
            return {"average_accuracy": 0.0, "trend": "error", "sample_size": 0}

    async def store_ab_test_result(
        self,
        test_id: str,
        variant_id: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store A/B test results for a specific variant.

        Args:
            test_id: Unique test identifier
            variant_id: Variant identifier
            metrics: Performance metrics for the variant

        Returns:
            Stored test result record
        """
        try:
            result_data = {
                "test_id": test_id,
                "variant_id": variant_id,
                "metrics": metrics,
                "recorded_at": datetime.utcnow().isoformat()
            }

            result = await self.db.insert("ab_test_results", result_data)
            logger.info("Stored A/B test result", test_id=test_id, variant_id=variant_id)
            return result

        except Exception as e:
            logger.error("Failed to store A/B test result", error=str(e))
            raise

    async def get_ab_test_results(self, test_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all results for a specific A/B test.

        Args:
            test_id: Unique test identifier

        Returns:
            List of variant results
        """
        try:
            results = await self.db.fetch_all("ab_test_results", {"test_id": test_id})
            return results
        except Exception as e:
            logger.error("Failed to get A/B test results", error=str(e))
            return []

    async def get_performance_patterns(
        self,
        workspace_id: str,
        metric: str
    ) -> Dict[str, Any]:
        """
        Identify patterns in performance data (e.g., best posting times, top topics).

        Args:
            workspace_id: Workspace identifier
            metric: Metric to analyze (engagement_rate, conversion_rate, etc.)

        Returns:
            Dictionary with identified patterns and insights
        """
        try:
            # Get historical data
            historical_data = await self.get_historical_performance(
                workspace_id,
                days_back=180
            )

            if not historical_data:
                return {"patterns": [], "insights": "Insufficient data"}

            # Analyze patterns (simplified - would use more sophisticated analysis in production)
            patterns = {
                "top_performing_content": [],
                "optimal_posting_times": [],
                "trending_topics": [],
                "average_metrics": {},
                "insights": []
            }

            # Calculate average metrics
            metric_values = [
                d.get("metrics", {}).get(metric, 0)
                for d in historical_data
                if metric in d.get("metrics", {})
            ]

            if metric_values:
                patterns["average_metrics"][metric] = sum(metric_values) / len(metric_values)
                patterns["insights"].append(
                    f"Average {metric}: {patterns['average_metrics'][metric]:.2f}"
                )

            return patterns

        except Exception as e:
            logger.error("Failed to get performance patterns", error=str(e))
            return {"patterns": [], "insights": "Error analyzing patterns"}


# Global instance
performance_memory = PerformanceMemory()
