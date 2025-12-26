import logging
from typing import Any, Dict

from pydantic import BaseModel, Field

from agents.base import BaseCognitiveAgent
from core.prompts import CreativePrompts
from models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.layout_architect")


class LayoutOutput(BaseModel):
    """SOTA structured layout result."""

    code_snippet: str = Field(description="HTML or SVG code.")
    styling_framework: str = Field(description="Tailwind, inline CSS, or pure SVG.")
    accessibility_score: float = Field(description="0 to 1 confidence score.")


class LayoutArchitectAgent(BaseCognitiveAgent):
    """
    A17: The Layout & UI Architect.
    Persona: SOTA Layout & UI Architect.
    Instructions: CreativePrompts.LAYOUT_ARCHITECT.
    """

    def __init__(self):
        super().__init__(
            name="LayoutArchitect",
            role="creator",
            system_prompt=CreativePrompts.LAYOUT_ARCHITECT,
            model_tier="driver",
            output_schema=LayoutOutput,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Executes layout generation."""
        logger.info("LayoutArchitectAgent architecting layouts...")
        return await super().__call__(state)
