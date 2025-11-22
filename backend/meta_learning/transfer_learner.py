"""
Transfer learning module for cross-workspace knowledge sharing.

This module enables knowledge transfer across workspaces by:
- Identifying similar workspaces based on attributes
- Extracting anonymized patterns from successful campaigns
- Suggesting cross-workspace insights with confidence scores
- Privacy-preserving pattern aggregation

Key Features:
- Workspace similarity detection
- Pattern anonymization and aggregation
- Confidence-scored recommendations
- Cold-start problem mitigation

Usage:
    transfer_learner = TransferLearner()
    insights = await transfer_learner.get_transfer_insights(
        target_workspace_id="ws_new",
        top_k=5
    )
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import numpy as np
from pydantic import BaseModel, Field
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler


class WorkspaceProfile(BaseModel):
    """
    Anonymized workspace profile for similarity matching.

    Attributes:
        workspace_id: Anonymized workspace identifier (hashed)
        industry: Industry vertical
        company_size: Company size category
        content_volume: Monthly content volume
        primary_channels: Main distribution channels
        avg_engagement: Average engagement rate
        feature_vector: Numerical feature representation
    """

    workspace_id: str  # Hashed ID for privacy
    industry: Optional[str] = None
    company_size: Optional[str] = None  # "startup", "smb", "enterprise"
    content_volume: Optional[int] = None  # Monthly content pieces
    primary_channels: List[str] = Field(default_factory=list)
    avg_engagement: Optional[float] = None
    feature_vector: List[float] = Field(default_factory=list)


class TransferInsight(BaseModel):
    """
    Cross-workspace insight with confidence and provenance.

    Attributes:
        insight_id: Unique identifier
        insight_type: Category of insight
        description: Human-readable insight
        source_workspaces: Number of workspaces supporting this insight
        confidence: Statistical confidence (0.0-1.0)
        effect_size: Expected impact magnitude
        applicable_scenarios: When to apply this insight
        metadata: Additional context
    """

    insight_id: str
    insight_type: str  # "strategy", "content", "timing", "channel"
    description: str
    source_workspaces: int  # Number of workspaces this is based on
    confidence: float = Field(ge=0.0, le=1.0)
    effect_size: float
    applicable_scenarios: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TransferLearner:
    """
    Enables privacy-preserving knowledge transfer across workspaces.

    This class helps new or underperforming workspaces benefit from
    patterns discovered in similar successful workspaces without
    exposing sensitive information.

    Methods:
        get_transfer_insights: Get insights from similar workspaces
        find_similar_workspaces: Find workspaces with similar profiles
        extract_transferable_patterns: Extract anonymized patterns
        compute_workspace_similarity: Calculate similarity scores
    """

    def __init__(
        self,
        min_source_workspaces: int = 3,
        min_confidence: float = 0.6,
        similarity_threshold: float = 0.7,
    ):
        """
        Initialize the transfer learner.

        Args:
            min_source_workspaces: Minimum workspaces needed to form an insight
            min_confidence: Minimum confidence for insights
            similarity_threshold: Minimum similarity to consider workspaces similar
        """
        self.min_source_workspaces = min_source_workspaces
        self.min_confidence = min_confidence
        self.similarity_threshold = similarity_threshold
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()

    async def get_transfer_insights(
        self,
        target_workspace_id: UUID,
        top_k: int = 5,
        insight_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get actionable insights from similar workspaces.

        This is the main entry point for transfer learning. It:
        1. Builds a profile for the target workspace
        2. Finds similar successful workspaces
        3. Extracts anonymized patterns from those workspaces
        4. Returns confidence-scored recommendations

        Args:
            target_workspace_id: Workspace requesting insights
            top_k: Number of top insights to return
            insight_types: Filter by insight types

        Returns:
            Dictionary containing:
                - insights: List of transfer insights
                - similar_workspaces: Count of similar workspaces found
                - coverage: How much data supports recommendations
                - metadata: Additional context
        """
        self.logger.info(
            f"Generating transfer insights for workspace {target_workspace_id}"
        )

        # Build target workspace profile
        target_profile = await self._build_workspace_profile(target_workspace_id)

        # Find similar workspaces
        similar_workspaces = await self.find_similar_workspaces(
            target_profile=target_profile,
            top_k=20,  # Consider top 20 similar workspaces
        )

        if len(similar_workspaces) < self.min_source_workspaces:
            self.logger.warning(
                f"Only found {len(similar_workspaces)} similar workspaces "
                f"(minimum: {self.min_source_workspaces})"
            )
            return {
                "insights": [],
                "similar_workspaces": len(similar_workspaces),
                "coverage": "low",
                "metadata": {
                    "reason": "insufficient_similar_workspaces",
                    "recommendation": "collect_more_data",
                },
            }

        # Extract transferable patterns
        all_insights = await self.extract_transferable_patterns(
            target_profile=target_profile,
            similar_workspaces=similar_workspaces,
        )

        # Filter by type if specified
        if insight_types:
            all_insights = [
                i for i in all_insights if i.insight_type in insight_types
            ]

        # Sort by confidence * effect_size and take top K
        all_insights.sort(
            key=lambda x: x.confidence * x.effect_size, reverse=True
        )
        top_insights = all_insights[:top_k]

        # Determine coverage
        coverage = "high" if len(similar_workspaces) >= 10 else "medium"
        if len(similar_workspaces) < 5:
            coverage = "low"

        return {
            "insights": [i.model_dump() for i in top_insights],
            "similar_workspaces": len(similar_workspaces),
            "coverage": coverage,
            "metadata": {
                "target_industry": target_profile.industry,
                "target_size": target_profile.company_size,
                "total_insights_found": len(all_insights),
            },
        }

    async def find_similar_workspaces(
        self,
        target_profile: WorkspaceProfile,
        top_k: int = 10,
    ) -> List[Tuple[WorkspaceProfile, float]]:
        """
        Find workspaces similar to the target workspace.

        Uses cosine similarity on feature vectors to identify
        workspaces with similar characteristics.

        Args:
            target_profile: Profile of target workspace
            top_k: Number of similar workspaces to return

        Returns:
            List of (workspace_profile, similarity_score) tuples
        """
        # Fetch all workspace profiles (would be from database in production)
        all_profiles = await self._fetch_all_workspace_profiles()

        # Remove target workspace
        all_profiles = [
            p for p in all_profiles
            if p.workspace_id != target_profile.workspace_id
        ]

        if not all_profiles:
            return []

        # Build feature matrix
        target_features = np.array(target_profile.feature_vector).reshape(1, -1)
        all_features = np.array([p.feature_vector for p in all_profiles])

        # Compute cosine similarity
        similarities = cosine_similarity(target_features, all_features)[0]

        # Filter by threshold and sort
        similar_indices = np.where(similarities >= self.similarity_threshold)[0]
        similar_profiles = [
            (all_profiles[i], float(similarities[i]))
            for i in similar_indices
        ]
        similar_profiles.sort(key=lambda x: x[1], reverse=True)

        return similar_profiles[:top_k]

    async def extract_transferable_patterns(
        self,
        target_profile: WorkspaceProfile,
        similar_workspaces: List[Tuple[WorkspaceProfile, float]],
    ) -> List[TransferInsight]:
        """
        Extract anonymized patterns from similar workspaces.

        Aggregates patterns across similar workspaces to create
        privacy-preserving insights that are applicable to the
        target workspace.

        Args:
            target_profile: Target workspace profile
            similar_workspaces: List of similar workspaces with similarity scores

        Returns:
            List of transfer insights
        """
        insights = []

        # Extract workspace IDs and similarity weights
        workspace_ids = [w[0].workspace_id for w in similar_workspaces]
        similarity_weights = np.array([w[1] for w in similar_workspaces])

        # Fetch performance data from similar workspaces
        workspace_data = await self._fetch_workspace_performance_data(
            workspace_ids
        )

        # Pattern 1: Optimal posting times
        timing_insight = await self._extract_timing_patterns(
            workspace_data, similarity_weights
        )
        if timing_insight:
            insights.append(timing_insight)

        # Pattern 2: Content strategy patterns
        content_insights = await self._extract_content_patterns(
            workspace_data, similarity_weights
        )
        insights.extend(content_insights)

        # Pattern 3: Channel mix optimization
        channel_insight = await self._extract_channel_patterns(
            workspace_data, similarity_weights
        )
        if channel_insight:
            insights.append(channel_insight)

        # Pattern 4: Campaign cadence
        cadence_insight = await self._extract_cadence_patterns(
            workspace_data, similarity_weights
        )
        if cadence_insight:
            insights.append(cadence_insight)

        # Filter by confidence threshold
        insights = [
            i for i in insights
            if i.confidence >= self.min_confidence
        ]

        return insights

    async def compute_workspace_similarity(
        self,
        workspace_a: UUID,
        workspace_b: UUID,
    ) -> float:
        """
        Compute similarity score between two workspaces.

        Args:
            workspace_a: First workspace ID
            workspace_b: Second workspace ID

        Returns:
            Similarity score (0.0-1.0)
        """
        profile_a = await self._build_workspace_profile(workspace_a)
        profile_b = await self._build_workspace_profile(workspace_b)

        features_a = np.array(profile_a.feature_vector).reshape(1, -1)
        features_b = np.array(profile_b.feature_vector).reshape(1, -1)

        similarity = cosine_similarity(features_a, features_b)[0][0]
        return float(similarity)

    async def _build_workspace_profile(
        self, workspace_id: UUID
    ) -> WorkspaceProfile:
        """
        Build an anonymized profile for a workspace.

        Args:
            workspace_id: Workspace to profile

        Returns:
            WorkspaceProfile with feature vector
        """
        # TODO: Fetch actual workspace data from database
        # For now, return simulated profile

        # Anonymize workspace ID with hash
        hashed_id = hashlib.sha256(str(workspace_id).encode()).hexdigest()[:16]

        # Simulate workspace attributes
        np.random.seed(hash(str(workspace_id)) % (2**32))

        industry = np.random.choice(
            ["saas", "ecommerce", "finance", "healthcare", "marketing"]
        )
        company_size = np.random.choice(["startup", "smb", "enterprise"])
        content_volume = int(np.random.normal(30, 10))
        primary_channels = list(
            np.random.choice(
                ["linkedin", "twitter", "email", "blog", "instagram"],
                size=2,
                replace=False,
            )
        )
        avg_engagement = float(np.random.beta(2, 5))

        # Build feature vector
        # Features: [content_volume_normalized, engagement_score,
        #           is_saas, is_ecommerce, is_startup, is_smb,
        #           uses_linkedin, uses_twitter, uses_email]
        feature_vector = [
            content_volume / 100.0,  # Normalize
            avg_engagement,
            1 if industry == "saas" else 0,
            1 if industry == "ecommerce" else 0,
            1 if company_size == "startup" else 0,
            1 if company_size == "smb" else 0,
            1 if "linkedin" in primary_channels else 0,
            1 if "twitter" in primary_channels else 0,
            1 if "email" in primary_channels else 0,
        ]

        return WorkspaceProfile(
            workspace_id=hashed_id,
            industry=industry,
            company_size=company_size,
            content_volume=content_volume,
            primary_channels=primary_channels,
            avg_engagement=avg_engagement,
            feature_vector=feature_vector,
        )

    async def _fetch_all_workspace_profiles(self) -> List[WorkspaceProfile]:
        """
        Fetch profiles for all workspaces.

        Returns:
            List of workspace profiles
        """
        # TODO: Replace with actual database query
        # Simulate 50 workspace profiles
        profiles = []
        for i in range(50):
            # Use deterministic seed for consistency
            profile = await self._build_workspace_profile(
                UUID(int=i, version=4)
            )
            profiles.append(profile)

        return profiles

    async def _fetch_workspace_performance_data(
        self, workspace_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Fetch performance data for specified workspaces.

        Args:
            workspace_ids: List of anonymized workspace IDs

        Returns:
            Aggregated performance data
        """
        # TODO: Replace with actual database query
        # Simulate aggregated data
        return {
            "optimal_posting_hours": [9, 10, 14, 17],  # Hours of day
            "best_content_length": {"blog": 1200, "social": 150, "email": 400},
            "top_performing_channels": ["linkedin", "email"],
            "optimal_cadence_days": 3,  # Days between posts
            "avg_engagement_by_channel": {
                "linkedin": 0.08,
                "twitter": 0.05,
                "email": 0.12,
            },
        }

    async def _extract_timing_patterns(
        self,
        workspace_data: Dict[str, Any],
        similarity_weights: np.ndarray,
    ) -> Optional[TransferInsight]:
        """
        Extract optimal posting time patterns.

        Args:
            workspace_data: Aggregated workspace data
            similarity_weights: Similarity scores for weighting

        Returns:
            Timing insight or None
        """
        optimal_hours = workspace_data.get("optimal_posting_hours", [])
        if not optimal_hours:
            return None

        # Weight by similarity (in real impl, would weight per workspace)
        avg_weight = float(np.mean(similarity_weights))

        return TransferInsight(
            insight_id="timing_optimal_hours",
            insight_type="timing",
            description=f"Post during {', '.join(map(str, optimal_hours))} hours for {1.3:.1f}x better engagement based on similar workspaces",
            source_workspaces=len(similarity_weights),
            confidence=min(0.9, avg_weight),
            effect_size=0.3,  # 30% improvement
            applicable_scenarios=["content_scheduling", "campaign_planning"],
            metadata={"optimal_hours": optimal_hours},
        )

    async def _extract_content_patterns(
        self,
        workspace_data: Dict[str, Any],
        similarity_weights: np.ndarray,
    ) -> List[TransferInsight]:
        """
        Extract content strategy patterns.

        Args:
            workspace_data: Aggregated workspace data
            similarity_weights: Similarity scores

        Returns:
            List of content insights
        """
        insights = []
        avg_weight = float(np.mean(similarity_weights))

        content_lengths = workspace_data.get("best_content_length", {})
        for content_type, length in content_lengths.items():
            insight = TransferInsight(
                insight_id=f"content_length_{content_type}",
                insight_type="content",
                description=f"Optimal {content_type} length is ~{length} words based on similar successful workspaces",
                source_workspaces=len(similarity_weights),
                confidence=min(0.85, avg_weight),
                effect_size=0.25,
                applicable_scenarios=[f"{content_type}_writing"],
                metadata={
                    "content_type": content_type,
                    "optimal_length": length,
                },
            )
            insights.append(insight)

        return insights

    async def _extract_channel_patterns(
        self,
        workspace_data: Dict[str, Any],
        similarity_weights: np.ndarray,
    ) -> Optional[TransferInsight]:
        """
        Extract channel optimization patterns.

        Args:
            workspace_data: Aggregated workspace data
            similarity_weights: Similarity scores

        Returns:
            Channel insight or None
        """
        top_channels = workspace_data.get("top_performing_channels", [])
        if not top_channels:
            return None

        avg_weight = float(np.mean(similarity_weights))
        engagement_data = workspace_data.get("avg_engagement_by_channel", {})

        return TransferInsight(
            insight_id="channel_optimization",
            insight_type="channel",
            description=f"Prioritize {', '.join(top_channels)} for maximum reach - these channels show highest engagement for similar businesses",
            source_workspaces=len(similarity_weights),
            confidence=min(0.88, avg_weight),
            effect_size=0.4,
            applicable_scenarios=["channel_selection", "campaign_planning"],
            metadata={
                "top_channels": top_channels,
                "engagement_rates": engagement_data,
            },
        )

    async def _extract_cadence_patterns(
        self,
        workspace_data: Dict[str, Any],
        similarity_weights: np.ndarray,
    ) -> Optional[TransferInsight]:
        """
        Extract posting cadence patterns.

        Args:
            workspace_data: Aggregated workspace data
            similarity_weights: Similarity scores

        Returns:
            Cadence insight or None
        """
        optimal_cadence = workspace_data.get("optimal_cadence_days")
        if not optimal_cadence:
            return None

        avg_weight = float(np.mean(similarity_weights))

        return TransferInsight(
            insight_id="posting_cadence",
            insight_type="strategy",
            description=f"Post every {optimal_cadence} days to maintain audience engagement without fatigue",
            source_workspaces=len(similarity_weights),
            confidence=min(0.82, avg_weight),
            effect_size=0.2,
            applicable_scenarios=["content_calendar", "campaign_planning"],
            metadata={"optimal_cadence_days": optimal_cadence},
        )
