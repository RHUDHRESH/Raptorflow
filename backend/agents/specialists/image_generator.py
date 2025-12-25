import logging
from typing import Any, Dict

from pydantic import BaseModel, Field

from backend.agents.base import BaseCognitiveAgent
from backend.core.prompts import CreativePrompts
from backend.models.cognitive import CognitiveIntelligenceState
from backend.tools.image_gen import DalleTool

logger = logging.getLogger("raptorflow.agents.image_generator")


class ImageOutput(BaseModel):
    """SOTA structured image result."""

    image_url: str
    revised_prompt: str
    rationale: str = Field(description="Why this image fits the brief.")


class ImageGenAgent(BaseCognitiveAgent):
    """
    A15: The Visual Asset Architect.
    Persona: Visual Strategist & Art Director.
    Instructions: CreativePrompts.VISUAL_ARCHITECT.
    """

    def __init__(self):
        super().__init__(
            name="ImageGenerator",
            role="creator",
            system_prompt=CreativePrompts.VISUAL_ARCHITECT,
            model_tier="driver",
            tools=[DalleTool()],
            output_schema=ImageOutput,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Executes image generation."""
        logger.info("ImageGenAgent architecting visuals...")
        # In a real SOTA flow, this agent would first generate a detailed prompt
        # using VISUAL_ARCHITECT instructions, then call the tool.
        # BaseCognitiveAgent currently calls the LLM with output_schema.
        return await super().__call__(state)
