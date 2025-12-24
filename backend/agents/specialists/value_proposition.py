import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.agents.base import BaseCognitiveAgent
from backend.models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.value_proposition")


class FeatureBenefitMap(BaseModel):
    """SOTA structured feature-benefit mapping."""

    feature: str
    pain_killer: str
    gain_creator: str


class ValuePropOutput(BaseModel):
    """SOTA structured value proposition result."""

    core_uvp: str = Field(description="The primary value proposition.")
    feature_map: List[FeatureBenefitMap]
    emotional_hook: str = Field(description="The core emotional reason to buy.")


class ValuePropositionAgent(BaseCognitiveAgent):
    """
    A07: The Value Proposition Designer.
    Persona: Master of Value Proposition Design.
    Instructions: StrategyPrompts.VALUE_PROP_MAPPER.
    """

    def __init__(self):
        from backend.core.prompts import StrategyPrompts

        super().__init__(
            name="ValuePropDesigner",
            role="strategist",
            system_prompt=StrategyPrompts.VALUE_PROP_MAPPER,
            model_tier="ultra",
            output_schema=ValuePropOutput,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Executes value proposition mapping."""
        logger.info("ValuePropositionAgent mapping UVPs...")
        return await super().__call__(state)
