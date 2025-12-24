import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.agents.base import BaseCognitiveAgent
from backend.models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.goal_aligner")


class InputMetric(BaseModel):
    """SOTA structured input metric."""

    name: str
    description: str
    target_value: str
    control_lever: str  # How we influence it


class GoalAlignmentOutput(BaseModel):
    """SOTA structured goal alignment result."""

    north_star_metric: str = Field(description="The single most important metric.")
    input_metrics: List[InputMetric]
    success_thresholds: Dict[str, str]
    alignment_rationale: str = Field(
        description="Why these metrics ensure the business goal is met."
    )


class GoalAlignerAgent(BaseCognitiveAgent):
    """
    A11: The Goal Aligner & Metric Specialist.
    Persona: Master of Marketing Metrics.
    Instructions: StrategyPrompts.GOAL_ALIGNER.
    """

    def __init__(self):
        from backend.core.prompts import StrategyPrompts

        super().__init__(
            name="GoalAligner",
            role="strategist",
            system_prompt=StrategyPrompts.GOAL_ALIGNER,
            model_tier="ultra",
            output_schema=GoalAlignmentOutput,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Executes goal alignment and metric decomposition."""
        logger.info("GoalAlignerAgent decomposing objectives...")
        return await super().__call__(state)
