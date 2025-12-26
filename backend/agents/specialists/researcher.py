import logging
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from agents.base import BaseCognitiveAgent
from models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.researcher")


class MarketTrendSignal(BaseModel):
    """SOTA structured trend signal."""

    name: str = Field(description="Name of the emerging trend.")
    strength: float = Field(description="0 to 1 signal strength.")
    signal_evidence: str = Field(
        description="The core evidence or 'why' behind the trend."
    )


class ResearchOutput(BaseModel):
    """SOTA structured research result."""

    trends: List[MarketTrendSignal]
    market_gaps: List[str] = Field(description="Identified white-space in the market.")
    competitor_blind_spots: List[str] = Field(
        description="What competitors are ignoring."
    )


class ResearcherAgent(BaseCognitiveAgent):
    """
    A02: The Master Researcher.
    Persona: Master Trend Forecaster.
    Instructions: ResearchPrompts.TREND_EXTRACTOR.
    """

    def __init__(self):
        from core.prompts import ResearchPrompts
        from tools.registry import UnifiedToolRegistry

        registry = UnifiedToolRegistry.default()
        profiles = registry.get_capability_profiles(["tavily_search"])
        super().__init__(
            name="Researcher",
            role="researcher",
            system_prompt=ResearchPrompts.TREND_EXTRACTOR,
            model_tier="reasoning",  # Researchers need high reasoning
            tools=registry.resolve_tools_from_profiles(profiles),
            output_schema=ResearchOutput,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Industrial research execution."""
        logger.info("ResearcherAgent extracting trends...")
        return await super().__call__(state)
