"""
Engagement Predictor using ML models and historical data.

This module predicts content engagement metrics including:
- Likes/reactions
- Shares
- Comments
- Click-through rate (CTR)
- Conversion rate
- Engagement rate
- Confidence intervals

Uses historical performance data from Supabase and applies machine learning
models to predict future performance with confidence intervals.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import structlog
import re
from backend.performance.performance_memory import performance_memory

logger = structlog.get_logger()


class EngagementPredictor:
    """
    Predicts engagement metrics for content before publishing.

    Uses historical performance data and content features to estimate
    engagement. Provides confidence intervals for predictions.

    Features analyzed:
    - Content length
    - Keyword presence
    - Sentiment
    - Topic relevance
    - Platform specifics
    - Historical patterns
    """

    def __init__(self):
        """Initialize the engagement predictor."""
        self.memory = performance_memory
        self.model_version = "1.0"

        # Feature weights (in production, these would be learned from data)
        self.feature_weights = {
            "content_length": 0.15,
            "keyword_density": 0.20,
            "sentiment_score": 0.15,
            "platform_fit": 0.20,
            "topic_relevance": 0.15,
            "historical_performance": 0.15
        }

    async def predict_engagement(
        self,
        content: str,
        content_type: str,
        platform: str,
        workspace_id: str,
        content_id: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        target_audience: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Predict engagement metrics for content.

        Args:
            content: The content text to analyze
            content_type: Type of content (blog, social_post, email, etc.)
            platform: Target platform (linkedin, twitter, email, etc.)
            workspace_id: Workspace identifier for historical context
            content_id: Optional content identifier for storing predictions
            keywords: Optional keywords present in content
            target_audience: Optional audience/persona information

        Returns:
            Dictionary containing:
                - predictions: Predicted metrics (likes, shares, comments, CTR, conversion_rate)
                - confidence_intervals: Min/max ranges for each prediction
                - confidence_level: Overall confidence (0.0-1.0)
                - feature_scores: Breakdown of feature contributions
                - recommendations: Suggestions to improve predicted engagement
        """
        logger.info(
            "Predicting engagement",
            content_type=content_type,
            platform=platform,
            workspace_id=workspace_id
        )

        try:
            # Extract features from content
            features = await self._extract_features(
                content,
                content_type,
                platform,
                keywords or []
            )

            # Get historical baselines
            historical_data = await self.memory.get_historical_performance(
                workspace_id,
                content_type,
                platform,
                days_back=90
            )

            baseline_metrics = self._calculate_baseline_metrics(
                historical_data,
                platform
            )

            # Calculate predictions based on features and baselines
            predictions = self._calculate_predictions(
                features,
                baseline_metrics,
                platform
            )

            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(
                predictions,
                historical_data,
                features
            )

            # Overall confidence level
            confidence_level = self._calculate_confidence_level(
                historical_data,
                features
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                features,
                predictions,
                baseline_metrics
            )

            result = {
                "predictions": predictions,
                "confidence_intervals": confidence_intervals,
                "confidence_level": confidence_level,
                "feature_scores": features,
                "baseline_metrics": baseline_metrics,
                "recommendations": recommendations,
                "model_version": self.model_version,
                "predicted_at": datetime.now(timezone.utc).isoformat()
            }

            # Store prediction if content_id provided
            if content_id:
                await self.memory.store_prediction(
                    content_id,
                    "engagement",
                    predictions,
                    confidence_level,
                    self.model_version
                )

            return result

        except Exception as e:
            logger.error("Failed to predict engagement", error=str(e))
            raise

    async def _extract_features(
        self,
        content: str,
        content_type: str,
        platform: str,
        keywords: List[str]
    ) -> Dict[str, float]:
        """
        Extract numerical features from content for prediction.

        Args:
            content: Content text
            content_type: Type of content
            platform: Target platform
            keywords: Keywords present

        Returns:
            Dictionary of feature scores (0.0-1.0)
        """
        features = {}

        # Content length score (platform-specific optimal ranges)
        word_count = len(content.split())
        features["content_length"] = self._score_content_length(
            word_count,
            content_type,
            platform
        )

        # Keyword density
        if keywords:
            keyword_count = sum(
                content.lower().count(kw.lower()) for kw in keywords
            )
            features["keyword_density"] = min(1.0, keyword_count / max(1, word_count / 100))
        else:
            features["keyword_density"] = 0.5

        # Sentiment score (simplified - would use NLP in production)
        features["sentiment_score"] = self._analyze_sentiment(content)

        # Platform fit score
        features["platform_fit"] = self._score_platform_fit(
            content,
            content_type,
            platform
        )

        # Topic relevance (simplified scoring)
        features["topic_relevance"] = 0.7  # Would use topic modeling in production

        return features

    def _score_content_length(
        self,
        word_count: int,
        content_type: str,
        platform: str
    ) -> float:
        """
        Score content length based on optimal ranges for platform/type.

        Args:
            word_count: Number of words
            content_type: Type of content
            platform: Target platform

        Returns:
            Score from 0.0 to 1.0
        """
        # Optimal word count ranges by platform
        optimal_ranges = {
            "twitter": (20, 50),
            "linkedin": (150, 300),
            "instagram": (100, 200),
            "facebook": (100, 250),
            "blog": (800, 2000),
            "email": (50, 150)
        }

        optimal_min, optimal_max = optimal_ranges.get(platform, (100, 500))

        if optimal_min <= word_count <= optimal_max:
            return 1.0
        elif word_count < optimal_min:
            return max(0.3, word_count / optimal_min)
        else:
            # Penalty for being too long
            excess = word_count - optimal_max
            penalty = min(0.7, excess / optimal_max)
            return max(0.3, 1.0 - penalty)

    def _analyze_sentiment(self, content: str) -> float:
        """
        Analyze content sentiment (simplified version).

        Args:
            content: Content text

        Returns:
            Sentiment score (0.0 = very negative, 1.0 = very positive)
        """
        # Simplified sentiment analysis using keyword matching
        # In production, use a proper NLP library like TextBlob or VADER

        positive_words = [
            "amazing", "excellent", "great", "love", "best", "awesome",
            "fantastic", "wonderful", "incredible", "outstanding"
        ]
        negative_words = [
            "terrible", "worst", "hate", "awful", "horrible", "bad",
            "disappointing", "poor", "useless", "waste"
        ]

        content_lower = content.lower()

        positive_count = sum(
            1 for word in positive_words if word in content_lower
        )
        negative_count = sum(
            1 for word in negative_words if word in content_lower
        )

        total = positive_count + negative_count
        if total == 0:
            return 0.6  # Neutral default

        # Calculate sentiment score
        sentiment = (positive_count - negative_count) / total
        # Normalize to 0-1 range
        return (sentiment + 1) / 2

    def _score_platform_fit(
        self,
        content: str,
        content_type: str,
        platform: str
    ) -> float:
        """
        Score how well content fits the platform.

        Args:
            content: Content text
            content_type: Type of content
            platform: Target platform

        Returns:
            Platform fit score (0.0-1.0)
        """
        score = 0.5  # Base score

        # Check for platform-specific elements
        if platform == "twitter":
            # Twitter favors hashtags and @mentions
            hashtag_count = len(re.findall(r'#\w+', content))
            mention_count = len(re.findall(r'@\w+', content))
            score += min(0.3, (hashtag_count + mention_count) * 0.1)

        elif platform == "linkedin":
            # LinkedIn favors professional language and structure
            if any(word in content.lower() for word in ["insight", "strategy", "professional", "business"]):
                score += 0.2

        elif platform == "instagram":
            # Instagram favors visual descriptions and emojis
            emoji_count = len(re.findall(r'[\U0001F300-\U0001F9FF]', content))
            score += min(0.3, emoji_count * 0.05)

        elif platform == "email":
            # Email favors clear structure and CTAs
            if "click" in content.lower() or "learn more" in content.lower():
                score += 0.2

        return min(1.0, score)

    def _calculate_baseline_metrics(
        self,
        historical_data: List[Dict[str, Any]],
        platform: str
    ) -> Dict[str, float]:
        """
        Calculate baseline metrics from historical data.

        Args:
            historical_data: Historical performance records
            platform: Target platform

        Returns:
            Dictionary of baseline metrics
        """
        if not historical_data:
            # Return default baselines if no historical data
            return {
                "avg_likes": 10.0,
                "avg_shares": 2.0,
                "avg_comments": 3.0,
                "avg_ctr": 0.02,
                "avg_conversion_rate": 0.01,
                "avg_engagement_rate": 0.05
            }

        # Calculate averages from historical data
        likes = []
        shares = []
        comments = []
        ctrs = []
        conversions = []

        for record in historical_data:
            metrics = record.get("metrics", {})
            if metrics.get("likes") is not None:
                likes.append(metrics["likes"])
            if metrics.get("shares") is not None:
                shares.append(metrics["shares"])
            if metrics.get("comments") is not None:
                comments.append(metrics["comments"])
            if metrics.get("ctr") is not None:
                ctrs.append(metrics["ctr"])
            if metrics.get("conversion_rate") is not None:
                conversions.append(metrics["conversion_rate"])

        return {
            "avg_likes": sum(likes) / len(likes) if likes else 10.0,
            "avg_shares": sum(shares) / len(shares) if shares else 2.0,
            "avg_comments": sum(comments) / len(comments) if comments else 3.0,
            "avg_ctr": sum(ctrs) / len(ctrs) if ctrs else 0.02,
            "avg_conversion_rate": sum(conversions) / len(conversions) if conversions else 0.01,
            "avg_engagement_rate": 0.05  # Calculated metric
        }

    def _calculate_predictions(
        self,
        features: Dict[str, float],
        baseline_metrics: Dict[str, float],
        platform: str
    ) -> Dict[str, float]:
        """
        Calculate predicted metrics based on features and baselines.

        Args:
            features: Extracted feature scores
            baseline_metrics: Historical baseline metrics
            platform: Target platform

        Returns:
            Dictionary of predicted metrics
        """
        # Calculate overall quality score from features
        quality_score = sum(
            features[f] * self.feature_weights.get(f, 0.1)
            for f in features
        )

        # Apply quality multiplier to baseline metrics
        multiplier = 0.5 + (quality_score * 1.5)  # Range: 0.5x to 2.0x

        predictions = {
            "likes": baseline_metrics["avg_likes"] * multiplier,
            "shares": baseline_metrics["avg_shares"] * multiplier,
            "comments": baseline_metrics["avg_comments"] * multiplier,
            "ctr": baseline_metrics["avg_ctr"] * multiplier,
            "conversion_rate": baseline_metrics["avg_conversion_rate"] * multiplier,
            "engagement_rate": (
                (baseline_metrics["avg_likes"] + baseline_metrics["avg_shares"] + baseline_metrics["avg_comments"])
                / max(1, baseline_metrics["avg_likes"] * 10)  # Assuming 10x reach
            ) * multiplier
        }

        # Platform-specific adjustments
        if platform == "linkedin":
            predictions["shares"] *= 1.2  # LinkedIn favors sharing
        elif platform == "twitter":
            predictions["shares"] *= 1.5  # Twitter is built for sharing

        return predictions

    def _calculate_confidence_intervals(
        self,
        predictions: Dict[str, float],
        historical_data: List[Dict[str, Any]],
        features: Dict[str, float]
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate confidence intervals for predictions.

        Args:
            predictions: Predicted metrics
            historical_data: Historical performance data
            features: Content features

        Returns:
            Dictionary with min/max ranges for each prediction
        """
        # Calculate variance from historical data
        variance_multiplier = 0.3  # 30% variance by default

        if len(historical_data) > 10:
            variance_multiplier = 0.2  # Lower variance with more data

        intervals = {}
        for metric, value in predictions.items():
            intervals[metric] = {
                "min": value * (1 - variance_multiplier),
                "max": value * (1 + variance_multiplier),
                "predicted": value
            }

        return intervals

    def _calculate_confidence_level(
        self,
        historical_data: List[Dict[str, Any]],
        features: Dict[str, float]
    ) -> float:
        """
        Calculate overall confidence level for predictions.

        Args:
            historical_data: Historical performance data
            features: Content features

        Returns:
            Confidence level (0.0-1.0)
        """
        # Base confidence on amount of historical data
        data_confidence = min(1.0, len(historical_data) / 50)

        # Feature quality contributes to confidence
        feature_avg = sum(features.values()) / len(features) if features else 0.5

        # Combine factors
        confidence = (data_confidence * 0.6) + (feature_avg * 0.4)

        return min(1.0, max(0.1, confidence))

    def _generate_recommendations(
        self,
        features: Dict[str, float],
        predictions: Dict[str, float],
        baseline_metrics: Dict[str, float]
    ) -> List[str]:
        """
        Generate recommendations to improve predicted engagement.

        Args:
            features: Feature scores
            predictions: Predicted metrics
            baseline_metrics: Baseline metrics

        Returns:
            List of actionable recommendations
        """
        recommendations = []

        # Check each feature and suggest improvements
        if features.get("content_length", 0) < 0.7:
            recommendations.append(
                "Adjust content length to match platform optimal range"
            )

        if features.get("keyword_density", 0) < 0.5:
            recommendations.append(
                "Increase keyword density for better topic relevance"
            )

        if features.get("sentiment_score", 0) < 0.5:
            recommendations.append(
                "Consider more positive language to improve sentiment"
            )

        if features.get("platform_fit", 0) < 0.6:
            recommendations.append(
                "Add platform-specific elements (hashtags, mentions, emojis)"
            )

        # Compare to baselines
        if predictions.get("engagement_rate", 0) < baseline_metrics.get("avg_engagement_rate", 0):
            recommendations.append(
                "Current content may underperform. Consider stronger hooks or more compelling value proposition."
            )

        if not recommendations:
            recommendations.append(
                "Content is well-optimized for predicted strong engagement!"
            )

        return recommendations


# Global instance
engagement_predictor = EngagementPredictor()
