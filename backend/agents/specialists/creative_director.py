import logging
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from backend.agents.base import BaseCognitiveAgent
from backend.core.prompts import CreativePrompts
from backend.models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.creative_director")


class CreativeAsset(BaseModel):
    """SOTA structured creative asset."""

    type: str = Field(description="email | social | ad | landing_page")
    content: str = Field(description="The surgical marketing copy.")
    visual_direction: str = Field(description="Art direction for the image/layout.")


class CreativeOutput(BaseModel):
    """SOTA structured creative result."""

    assets: List[CreativeAsset]
    brand_kit_alignment: float = Field(description="0 to 1 confidence score.")
    rationale: str = Field(description="Why this direction works.")


class CreativeDirectorAgent(BaseCognitiveAgent):
    """
    A03: The Master Creative Director.
    Persona: World-Class Creative Director.
    Instructions: CreativePrompts.ASSET_FACTORY.
    """

    def __init__(self):
        super().__init__(
            name="CreativeDirector",
            role="creator",
            system_prompt=CreativePrompts.ASSET_FACTORY,
            model_tier="driver",  # Creative work needs standard driver power
            output_schema=CreativeOutput,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Industrial creative execution."""
        logger.info("CreativeDirectorAgent architecting assets...")
        return await super().__call__(state)
