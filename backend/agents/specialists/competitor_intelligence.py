import logging
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from agents.base import BaseCognitiveAgent
from models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.competitor_intelligence")


class CompetitorProfile(BaseModel):
    """SOTA structured competitor profile."""

    brand_name: str
    landing_page_hooks: List[str]
    pricing_model: str
    messaging_weakness: str


class CompetitorMapOutput(BaseModel):
    """SOTA structured competitor map result."""

    competitors: List[CompetitorProfile]
    market_positioning_gap: str = Field(
        description="The 'Blue Ocean' opportunity identified."
    )


class CompetitorIntelligenceAgent(BaseCognitiveAgent):
    """
    A06: The Competitor Intelligence Specialist.
    Persona: Master of Competitive Intelligence.
    Instructions: ResearchPrompts.COMPETITOR_MAPPER.
    """

    def __init__(self):
        from core.prompts import ResearchPrompts

        super().__init__(
            name="CompetitorIntelligence",
            role="researcher",
            system_prompt=ResearchPrompts.COMPETITOR_MAPPER,
            model_tier="reasoning",
            output_schema=CompetitorMapOutput,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Executes competitor intelligence mapping."""
        logger.info("CompetitorIntelligenceAgent mapping market...")
        return await super().__call__(state)
