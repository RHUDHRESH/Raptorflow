import logging
from typing import Any, Dict, List

from pydantic import BaseModel

logger = logging.getLogger("raptorflow.core.pivoting")


class PivotRecommendation(BaseModel):
    """SOTA structured pivot recommendation."""

    detected_failure: str
    proposed_pivot: str
    urgency: str  # low, medium, high
    strategic_rationale: str


class PivotEngine:
    """
    Industrial Pivot Logic Agent helper.
    Detects when a campaign arc needs a surgical shift based on performance.
    """

    @staticmethod
    def evaluate_pivot(
        quality_score: float, outcomes: List[Dict[str, Any]]
    ) -> List[PivotRecommendation]:
        """Surgically evaluates if a pivot is required."""
        recommendations = []

        # SOTA Heuristic: If quality is low, pivot
        if quality_score < 0.6:
            recommendations.append(
                PivotRecommendation(
                    detected_failure="Low tactical quality score.",
                    proposed_pivot="Execute deep-dive research on competitor messaging.",
                    urgency="high",
                    strategic_rationale="Foundation is shaky, execution will fail without better data.",
                )
            )

        # Outcomes check (simulated)
        if any("fail" in str(o).lower() for o in outcomes):
            recommendations.append(
                PivotRecommendation(
                    detected_failure="Negative outcome detected in execution.",
                    proposed_pivot="Simplify monthly milestones to increase focus.",
                    urgency="medium",
                    strategic_rationale="Resource burn is high with low conversion.",
                )
            )

        logger.info(
            f"Pivot evaluation complete. Recommendations: {len(recommendations)}"
        )
        return recommendations
