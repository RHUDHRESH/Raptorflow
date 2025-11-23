"""
Performance pattern analyzer for RaptorFlow.

This module analyzes historical content and campaign performance to identify
winning and losing patterns using machine learning and statistical analysis.

Key Features:
- Pattern extraction from historical data
- Statistical significance testing
- ML-based pattern recognition (clustering, classification)
- Confidence scoring and sample size tracking
- Task-specific pattern recommendations

Usage:
    analyzer = PerformanceAnalyzer()
    patterns = await analyzer.analyze_patterns(
        workspace_id="ws_123",
        content_type="social",
        min_samples=30
    )
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

import numpy as np
from pydantic import BaseModel, Field
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler


class PerformancePattern(BaseModel):
    """
    Represents a discovered performance pattern.

    Attributes:
        pattern_id: Unique identifier for the pattern
        pattern_type: Type of pattern (winning|losing|neutral)
        description: Human-readable description of the pattern
        features: Key features that define this pattern
        confidence: Statistical confidence (0.0-1.0)
        sample_size: Number of data points supporting this pattern
        effect_size: Magnitude of impact (Cohen's d or similar)
        applicable_tasks: Task types where this pattern applies
        metadata: Additional pattern metadata
    """

    pattern_id: str
    pattern_type: str  # "winning", "losing", "neutral"
    description: str
    features: Dict[str, Any]
    confidence: float = Field(ge=0.0, le=1.0)
    sample_size: int
    effect_size: float
    applicable_tasks: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PerformanceAnalyzer:
    """
    Analyzes historical performance data to discover actionable patterns.

    This class uses machine learning and statistical methods to:
    1. Extract features from historical content/campaign data
    2. Identify clusters of high/low performing content
    3. Determine statistically significant patterns
    4. Generate actionable recommendations

    Methods:
        analyze_patterns: Main entry point for pattern analysis
        identify_winning_patterns: Extract high-performing patterns
        identify_losing_patterns: Extract low-performing patterns
        get_pattern_recommendations: Get task-specific recommendations
    """

    def __init__(
        self,
        min_confidence: float = 0.7,
        min_sample_size: int = 20,
        min_effect_size: float = 0.3,
    ):
        """
        Initialize the performance analyzer.

        Args:
            min_confidence: Minimum confidence threshold for patterns (0.0-1.0)
            min_sample_size: Minimum samples required to identify a pattern
            min_effect_size: Minimum effect size (Cohen's d) to consider significant
        """
        self.min_confidence = min_confidence
        self.min_sample_size = min_sample_size
        self.min_effect_size = min_effect_size
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()

    async def analyze_patterns(
        self,
        workspace_id: UUID,
        content_type: Optional[str] = None,
        lookback_days: int = 90,
        min_samples: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Analyze performance patterns from historical data.

        Args:
            workspace_id: Workspace to analyze
            content_type: Filter by content type (blog, email, social, etc.)
            lookback_days: Number of days to look back for historical data
            min_samples: Override default minimum sample size

        Returns:
            Dictionary containing:
                - winning_patterns: List of high-performing patterns
                - losing_patterns: List of low-performing patterns
                - insights: High-level insights and recommendations
                - statistics: Analysis statistics
        """
        self.logger.info(
            f"Analyzing patterns for workspace {workspace_id}, "
            f"content_type={content_type}, lookback={lookback_days}d"
        )

        # Fetch historical data
        historical_data = await self._fetch_historical_data(
            workspace_id=workspace_id,
            content_type=content_type,
            lookback_days=lookback_days,
        )

        if len(historical_data) < (min_samples or self.min_sample_size):
            self.logger.warning(
                f"Insufficient data: {len(historical_data)} samples "
                f"(minimum: {min_samples or self.min_sample_size})"
            )
            return {
                "winning_patterns": [],
                "losing_patterns": [],
                "insights": ["Insufficient data for pattern analysis"],
                "statistics": {"sample_count": len(historical_data)},
            }

        # Extract features and labels
        features, labels, metadata = self._extract_features(historical_data)

        # Identify patterns
        winning_patterns = await self._identify_winning_patterns(
            features, labels, metadata
        )
        losing_patterns = await self._identify_losing_patterns(
            features, labels, metadata
        )

        # Generate insights
        insights = self._generate_insights(winning_patterns, losing_patterns)

        return {
            "winning_patterns": [p.model_dump() for p in winning_patterns],
            "losing_patterns": [p.model_dump() for p in losing_patterns],
            "insights": insights,
            "statistics": {
                "sample_count": len(historical_data),
                "winning_pattern_count": len(winning_patterns),
                "losing_pattern_count": len(losing_patterns),
                "lookback_days": lookback_days,
            },
        }

    async def _identify_winning_patterns(
        self,
        features: np.ndarray,
        labels: np.ndarray,
        metadata: List[Dict[str, Any]],
    ) -> List[PerformancePattern]:
        """
        Identify high-performing patterns using clustering and classification.

        Args:
            features: Feature matrix (n_samples, n_features)
            labels: Performance labels (engagement scores, conversion rates, etc.)
            metadata: Metadata for each sample

        Returns:
            List of winning performance patterns
        """
        patterns = []

        # Normalize features
        features_scaled = self.scaler.fit_transform(features)

        # Cluster analysis to find groups of similar content
        n_clusters = min(5, len(features) // 10)  # Adaptive cluster count
        if n_clusters >= 2:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(features_scaled)

            # Analyze each cluster
            for cluster_id in range(n_clusters):
                cluster_mask = clusters == cluster_id
                cluster_labels = labels[cluster_mask]

                if len(cluster_labels) < self.min_sample_size:
                    continue

                # Calculate cluster statistics
                cluster_mean = np.mean(cluster_labels)
                overall_mean = np.mean(labels)
                cluster_std = np.std(cluster_labels)

                # Cohen's d effect size
                pooled_std = np.std(labels)
                effect_size = (
                    (cluster_mean - overall_mean) / pooled_std
                    if pooled_std > 0
                    else 0
                )

                # T-test for statistical significance
                t_stat, p_value = stats.ttest_ind(
                    cluster_labels, labels[~cluster_mask]
                )
                confidence = 1 - p_value

                # Only keep winning patterns (above average with strong effect)
                if (
                    cluster_mean > overall_mean
                    and effect_size >= self.min_effect_size
                    and confidence >= self.min_confidence
                ):
                    # Extract feature importances for this cluster
                    cluster_features = self._extract_cluster_features(
                        features[cluster_mask], metadata, cluster_mask
                    )

                    pattern = PerformancePattern(
                        pattern_id=f"winning_cluster_{cluster_id}",
                        pattern_type="winning",
                        description=self._describe_pattern(
                            cluster_features, cluster_mean, overall_mean
                        ),
                        features=cluster_features,
                        confidence=min(confidence, 0.99),
                        sample_size=int(np.sum(cluster_mask)),
                        effect_size=float(effect_size),
                        applicable_tasks=self._infer_applicable_tasks(
                            cluster_features
                        ),
                        metadata={
                            "cluster_id": cluster_id,
                            "mean_performance": float(cluster_mean),
                            "std_performance": float(cluster_std),
                            "p_value": float(p_value),
                        },
                    )
                    patterns.append(pattern)

        # Feature importance analysis using Random Forest
        if len(features) >= self.min_sample_size * 2:
            patterns.extend(
                await self._analyze_feature_importance(features, labels, metadata)
            )

        return patterns

    async def _identify_losing_patterns(
        self,
        features: np.ndarray,
        labels: np.ndarray,
        metadata: List[Dict[str, Any]],
    ) -> List[PerformancePattern]:
        """
        Identify low-performing patterns to avoid.

        Args:
            features: Feature matrix
            labels: Performance labels
            metadata: Sample metadata

        Returns:
            List of losing performance patterns
        """
        patterns = []

        # Normalize features
        features_scaled = self.scaler.fit_transform(features)

        # Cluster analysis
        n_clusters = min(5, len(features) // 10)
        if n_clusters >= 2:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(features_scaled)

            for cluster_id in range(n_clusters):
                cluster_mask = clusters == cluster_id
                cluster_labels = labels[cluster_mask]

                if len(cluster_labels) < self.min_sample_size:
                    continue

                cluster_mean = np.mean(cluster_labels)
                overall_mean = np.mean(labels)
                pooled_std = np.std(labels)
                effect_size = (
                    (overall_mean - cluster_mean) / pooled_std
                    if pooled_std > 0
                    else 0
                )

                # T-test
                t_stat, p_value = stats.ttest_ind(
                    cluster_labels, labels[~cluster_mask]
                )
                confidence = 1 - p_value

                # Only keep losing patterns (below average with strong negative effect)
                if (
                    cluster_mean < overall_mean
                    and effect_size >= self.min_effect_size
                    and confidence >= self.min_confidence
                ):
                    cluster_features = self._extract_cluster_features(
                        features[cluster_mask], metadata, cluster_mask
                    )

                    pattern = PerformancePattern(
                        pattern_id=f"losing_cluster_{cluster_id}",
                        pattern_type="losing",
                        description=self._describe_pattern(
                            cluster_features, cluster_mean, overall_mean, losing=True
                        ),
                        features=cluster_features,
                        confidence=min(confidence, 0.99),
                        sample_size=int(np.sum(cluster_mask)),
                        effect_size=float(effect_size),
                        applicable_tasks=self._infer_applicable_tasks(
                            cluster_features
                        ),
                        metadata={
                            "cluster_id": cluster_id,
                            "mean_performance": float(cluster_mean),
                            "std_performance": float(np.std(cluster_labels)),
                            "p_value": float(p_value),
                        },
                    )
                    patterns.append(pattern)

        return patterns

    async def _analyze_feature_importance(
        self,
        features: np.ndarray,
        labels: np.ndarray,
        metadata: List[Dict[str, Any]],
    ) -> List[PerformancePattern]:
        """
        Use Random Forest to identify important features for high performance.

        Args:
            features: Feature matrix
            labels: Performance labels
            metadata: Sample metadata

        Returns:
            List of feature-based patterns
        """
        patterns = []

        # Binarize labels: top 25% = high performing
        threshold = np.percentile(labels, 75)
        binary_labels = (labels >= threshold).astype(int)

        # Train Random Forest classifier
        clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
        clf.fit(features, binary_labels)

        # Get feature importances
        importances = clf.feature_importances_
        feature_names = [f"feature_{i}" for i in range(features.shape[1])]

        # Find top important features
        top_indices = np.argsort(importances)[-5:]  # Top 5 features
        top_features = {
            feature_names[i]: float(importances[i]) for i in top_indices
        }

        # Create a pattern based on feature importance
        if len(top_features) > 0:
            pattern = PerformancePattern(
                pattern_id="rf_feature_importance",
                pattern_type="winning",
                description=f"Content with strong {', '.join(list(top_features.keys())[:3])} performs {np.percentile(labels, 75) / np.mean(labels):.1f}x better",
                features=top_features,
                confidence=float(clf.score(features, binary_labels)),
                sample_size=len(labels),
                effect_size=float(
                    (np.mean(labels[binary_labels == 1]) - np.mean(labels))
                    / np.std(labels)
                ),
                applicable_tasks=["content_generation", "campaign_planning"],
                metadata={"model_type": "random_forest", "n_estimators": 100},
            )
            patterns.append(pattern)

        return patterns

    async def _fetch_historical_data(
        self,
        workspace_id: UUID,
        content_type: Optional[str],
        lookback_days: int,
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical performance data from database.

        In production, this would query the analytics database.
        For now, returns simulated data for demonstration.

        Args:
            workspace_id: Workspace ID to query
            content_type: Content type filter
            lookback_days: Number of days to look back

        Returns:
            List of historical content records with performance metrics
        """
        # TODO: Replace with actual database query
        # Example query:
        # SELECT * FROM content_analytics
        # WHERE workspace_id = ? AND created_at >= NOW() - INTERVAL ? DAY
        # ORDER BY created_at DESC

        # Simulated data for demonstration
        np.random.seed(42)
        n_samples = max(50, lookback_days)

        data = []
        for i in range(n_samples):
            data.append(
                {
                    "content_id": f"content_{i}",
                    "content_type": content_type or np.random.choice(
                        ["blog", "email", "social"]
                    ),
                    "engagement_score": float(np.random.gamma(2, 2)),
                    "conversion_rate": float(np.random.beta(2, 5)),
                    "word_count": int(np.random.normal(500, 200)),
                    "has_emoji": bool(np.random.random() > 0.5),
                    "has_cta": bool(np.random.random() > 0.3),
                    "sentiment_score": float(np.random.normal(0.6, 0.2)),
                    "created_at": datetime.now(timezone.utc)
                    - timedelta(days=np.random.randint(0, lookback_days)),
                }
            )

        return data

    def _extract_features(
        self, historical_data: List[Dict[str, Any]]
    ) -> tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
        """
        Extract feature matrix and labels from historical data.

        Args:
            historical_data: List of content records with metrics

        Returns:
            Tuple of (features, labels, metadata)
        """
        features_list = []
        labels_list = []
        metadata_list = []

        for record in historical_data:
            # Extract features
            feature_vector = [
                record.get("word_count", 0),
                1 if record.get("has_emoji") else 0,
                1 if record.get("has_cta") else 0,
                record.get("sentiment_score", 0.5),
            ]
            features_list.append(feature_vector)

            # Label is engagement score (or could be conversion rate)
            label = record.get("engagement_score", 0.0)
            labels_list.append(label)

            # Keep metadata for interpretation
            metadata_list.append(
                {
                    "content_id": record.get("content_id"),
                    "content_type": record.get("content_type"),
                    "created_at": record.get("created_at"),
                }
            )

        return (
            np.array(features_list),
            np.array(labels_list),
            metadata_list,
        )

    def _extract_cluster_features(
        self,
        cluster_features: np.ndarray,
        metadata: List[Dict[str, Any]],
        cluster_mask: np.ndarray,
    ) -> Dict[str, Any]:
        """
        Extract human-readable features from a cluster.

        Args:
            cluster_features: Feature matrix for cluster samples
            metadata: Metadata for all samples
            cluster_mask: Boolean mask for cluster membership

        Returns:
            Dictionary of interpretable features
        """
        cluster_metadata = [m for i, m in enumerate(metadata) if cluster_mask[i]]

        # Compute feature statistics
        mean_features = np.mean(cluster_features, axis=0)

        # Extract content types in cluster
        content_types = [m.get("content_type") for m in cluster_metadata]
        most_common_type = max(set(content_types), key=content_types.count)

        return {
            "avg_word_count": float(mean_features[0]),
            "emoji_usage": float(mean_features[1]),
            "cta_inclusion": float(mean_features[2]),
            "avg_sentiment": float(mean_features[3]),
            "dominant_content_type": most_common_type,
            "sample_count": len(cluster_metadata),
        }

    def _describe_pattern(
        self,
        features: Dict[str, Any],
        cluster_mean: float,
        overall_mean: float,
        losing: bool = False,
    ) -> str:
        """
        Generate human-readable pattern description.

        Args:
            features: Extracted feature dictionary
            cluster_mean: Mean performance of pattern
            overall_mean: Overall mean performance
            losing: Whether this is a losing pattern

        Returns:
            Human-readable description
        """
        performance_diff = (
            (cluster_mean / overall_mean - 1) * 100
            if overall_mean > 0
            else 0
        )

        if losing:
            desc = f"Content performs {abs(performance_diff):.1f}% worse when: "
        else:
            desc = f"Content performs {performance_diff:.1f}% better when: "

        descriptors = []

        if features.get("emoji_usage", 0) > 0.7:
            descriptors.append("includes emojis")
        if features.get("cta_inclusion", 0) > 0.7:
            descriptors.append("has clear CTA")
        if features.get("avg_word_count", 0) > 600:
            descriptors.append("is long-form (>600 words)")
        elif features.get("avg_word_count", 0) < 300:
            descriptors.append("is short-form (<300 words)")
        if features.get("avg_sentiment", 0.5) > 0.7:
            descriptors.append("has positive sentiment")

        desc += ", ".join(descriptors) if descriptors else "using this approach"
        return desc

    def _infer_applicable_tasks(self, features: Dict[str, Any]) -> List[str]:
        """
        Infer which tasks this pattern applies to.

        Args:
            features: Pattern features

        Returns:
            List of applicable task types
        """
        tasks = []

        content_type = features.get("dominant_content_type", "")
        if content_type == "blog":
            tasks.append("blog_writing")
        elif content_type == "email":
            tasks.append("email_campaign")
        elif content_type == "social":
            tasks.append("social_media_post")

        # Generic tasks
        tasks.extend(["content_generation", "campaign_planning"])

        return tasks

    def _generate_insights(
        self,
        winning_patterns: List[PerformancePattern],
        losing_patterns: List[PerformancePattern],
    ) -> List[str]:
        """
        Generate high-level insights from patterns.

        Args:
            winning_patterns: List of winning patterns
            losing_patterns: List of losing patterns

        Returns:
            List of actionable insights
        """
        insights = []

        if winning_patterns:
            insights.append(
                f"Identified {len(winning_patterns)} high-performing patterns "
                f"with average {np.mean([p.effect_size for p in winning_patterns]):.2f} effect size"
            )

            # Top winning pattern
            top_pattern = max(winning_patterns, key=lambda p: p.effect_size)
            insights.append(
                f"Top strategy: {top_pattern.description} "
                f"(confidence: {top_pattern.confidence:.1%})"
            )

        if losing_patterns:
            insights.append(
                f"Identified {len(losing_patterns)} patterns to avoid "
                f"with average {np.mean([p.effect_size for p in losing_patterns]):.2f} negative impact"
            )

            # Top pattern to avoid
            top_avoid = max(losing_patterns, key=lambda p: p.effect_size)
            insights.append(f"Avoid: {top_avoid.description}")

        if not winning_patterns and not losing_patterns:
            insights.append(
                "No statistically significant patterns found. "
                "Consider collecting more data or adjusting thresholds."
            )

        return insights

    async def get_pattern_recommendations(
        self,
        workspace_id: UUID,
        task_type: str,
        top_k: int = 3,
    ) -> List[PerformancePattern]:
        """
        Get top pattern recommendations for a specific task.

        Args:
            workspace_id: Workspace to analyze
            task_type: Type of task (e.g., "blog_writing", "email_campaign")
            top_k: Number of top patterns to return

        Returns:
            List of top recommended patterns sorted by effect size
        """
        # Analyze patterns
        analysis = await self.analyze_patterns(workspace_id=workspace_id)

        # Filter patterns applicable to this task
        applicable_patterns = [
            PerformancePattern(**p)
            for p in analysis["winning_patterns"]
            if task_type in p.get("applicable_tasks", [])
        ]

        # Sort by effect size and return top K
        applicable_patterns.sort(key=lambda p: p.effect_size, reverse=True)
        return applicable_patterns[:top_k]
