import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.agents.base import BaseCognitiveAgent
from backend.models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.muse_briefer")


class CreativeBriefOutput(BaseModel):
    """SOTA structured creative brief result."""

    one_big_idea: str = Field(description="The core creative concept.")
    emotional_resonance_points: List[str] = Field(
        description="What will make the user feel."
    )

    visual_metaphors: List[str] = Field(description="Concepts for visual storytelling.")
    creative_constraints: List[str] = Field(description="Mandatories from Brand Kit.")


class MuseBriefingAgent(BaseCognitiveAgent):
    """
    A13: The Creative Briefing Specialist.
    Persona: Master Creative Strategist.
    Instructions: MusePrompts.CREATIVE_BRIEFER.
    """

    def __init__(self):
        from backend.core.prompts import MusePrompts

        super().__init__(
            name="MuseBriefer",
            role="strategist",
            system_prompt=MusePrompts.CREATIVE_BRIEFER,
            model_tier="ultra",  # Briefing needs high synthesis
            output_schema=CreativeBriefOutput,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Executes creative briefing."""
        logger.info("MuseBriefingAgent architecting creative context...")
        return await super().__call__(state)
