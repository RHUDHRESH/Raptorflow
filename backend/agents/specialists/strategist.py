import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.agents.base import BaseCognitiveAgent
from backend.core.prompts import StrategyPrompts
from backend.models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.strategist")


class PositioningOutput(BaseModel):
    """SOTA structured positioning result."""

    contrarian_truth: str = Field(
        description="The non-obvious truth about the category."
    )
    job_to_be_done: str = Field(
        description="The specific functional/emotional job the user is hiring the product for."
    )
    category_of_one: str = Field(
        description="The new category name where the product has no competition."
    )
    uvp_statement: str = Field(
        description="The 100% surgical Unique Value Proposition."
    )


class StrategistAgent(BaseCognitiveAgent):
    """
    A01: The Master Strategist.
    Persona: Master of Strategic Positioning.
    Instructions: StrategyPrompts.POSITIONING_REFINER.
    """

    def __init__(self):
        super().__init__(
            name="Strategist",
            role="strategist",
            system_prompt=StrategyPrompts.POSITIONING_REFINER,
            model_tier="ultra",  # Strategists need the highest reasoning
            output_schema=PositioningOutput,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Industrial strategy execution."""
        logger.info("StrategistAgent refining positioning...")
        return await super().__call__(state)
