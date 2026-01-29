"""
Reflection Module - Orchestrates the reflection loop

Coordinates quality scoring, self-critique, and improvement execution.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..config import CognitiveConfig

from correction_planner import CorrectionPlanner
from critic import SelfCritic
from executor import ImprovementExecutor
from ..models import Correction, Critique, QualityScore, ReflectionResult
from scorer import QualityScorer

logger = logging.getLogger(__name__)


class ReflectionModule:
    """Orchestrates the reflection and improvement loop."""

    def __init__(self, config: Optional[CognitiveConfig] = None):
        self.config = config or CognitiveConfig()
        self.scorer = QualityScorer()
        self.critic = SelfCritic()
        self.planner = CorrectionPlanner()
        self.executor = ImprovementExecutor()

        # Default quality criteria
        self.default_criteria = [
            "accuracy",
            "relevance",
            "coherence",
            "completeness",
            "actionability",
            "clarity",
        ]

    async def reflect(
        self,
        output: str,
        goal: str,
        context: Dict[str, Any],
        max_iterations: int = 3,
        criteria: Optional[List[str]] = None,
    ) -> ReflectionResult:
        """
        Perform reflection loop to improve output quality.

        Args:
            output: Initial content to improve
            goal: Original goal/request
            context: Additional context
            max_iterations: Maximum reflection iterations
            criteria: Quality criteria to assess

        Returns:
            ReflectionResult with improvement details
        """
        start_time = datetime.now()
        criteria = criteria or self.default_criteria

        try:
            # Initial quality assessment
            initial_score = await self.scorer.score(output, criteria)
            current_output = output
            corrections_applied = []

            logger.info(
                f"Starting reflection with initial score: {initial_score.overall}"
            )

            # Reflection loop
            for iteration in range(max_iterations):
                # Check if quality threshold met
                if initial_score.passed:
                    logger.info(f"Quality threshold met after {iteration} iterations")
                    break

                # Perform adversarial critique
                critique = await self.critic.critique(current_output, goal, context)

                # Plan corrections
                corrections = await self.planner.plan_corrections(critique)

                if not corrections:
                    logger.info("No corrections planned, ending reflection")
                    break

                # Apply corrections
                current_output = await self.executor.execute_corrections(
                    current_output, corrections
                )
                corrections_applied.extend(corrections)

                # Reassess quality
                new_score = await self.scorer.score(current_output, criteria)

                logger.info(
                    f"Iteration {iteration + 1}: Score {initial_score.overall} -> {new_score.overall}"
                )

                # Check for improvement
                if new_score.overall <= initial_score.overall:
                    logger.warning("No improvement detected, ending reflection")
                    break

                initial_score = new_score

            # Final assessment
            final_score = await self.scorer.score(current_output, criteria)
            processing_time = (datetime.now() - start_time).total_seconds()

            result = ReflectionResult(
                initial_score=initial_score,
                final_score=final_score,
                corrections_applied=corrections_applied,
                iterations=len(corrections_applied),
                approved=final_score.passed,
                processing_time=processing_time,
                timestamp=datetime.now(),
            )

            logger.info(
                f"Reflection completed: {final_score.overall} score, {result.approved}"
            )
            return result

        except Exception as e:
            logger.error(f"Reflection failed: {e}")
            # Return minimal result on failure
            return ReflectionResult(
                initial_score=QualityScore(
                    overall=50,
                    dimensions={"accuracy": 50, "relevance": 50},
                    issues=[],
                    passed=False,
                ),
                final_score=QualityScore(
                    overall=50,
                    dimensions={"accuracy": 50, "relevance": 50},
                    issues=[],
                    passed=False,
                ),
                corrections_applied=[],
                iterations=0,
                approved=False,
                processing_time=(datetime.now() - start_time).total_seconds(),
                timestamp=datetime.now(),
            )

    async def quick_assess(
        self, output: str, criteria: Optional[List[str]] = None
    ) -> QualityScore:
        """
        Quick quality assessment without full reflection loop.

        Args:
            output: Content to assess
            criteria: Quality criteria

        Returns:
            Quality score
        """
        criteria = criteria or self.default_criteria
        return await self.scorer.score(output, criteria)

    def set_quality_threshold(self, threshold: int):
        """Set quality threshold for approval."""
        self.config.quality_threshold = threshold
        self.scorer.quality_threshold = threshold
