import logging
from typing import Any, Dict

from pydantic import BaseModel

from backend.agents.base import BaseCognitiveAgent
from backend.models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.copywriter")


class CopyOutput(BaseModel):
    """SOTA structured copy result."""

    headline: str
    body: str
    cta: str
    tone_alignment: str


class CopywriterAgent(BaseCognitiveAgent):
    """
    A14: The Asset Copywriter.
    Persona: High-Conversion Copywriter.
    Instructions: Dynamic based on asset type.
    """

    def __init__(self, asset_type: str = "social"):
        from backend.core.prompts import AssetSpecializations

        prompts_map = {
            "social": AssetSpecializations.LINKEDIN_THOUGHT_LEADER,
            "email": AssetSpecializations.EMAIL_COLD,
            "ad": AssetSpecializations.AD_COPYWRITER,
        }

        system_prompt = prompts_map.get(
            asset_type, AssetSpecializations.LINKEDIN_THOUGHT_LEADER
        )

        super().__init__(
            name=f"Copywriter_{asset_type}",
            role="creator",
            system_prompt=system_prompt,
            model_tier="driver",
            output_schema=CopyOutput,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Executes copywriting."""
        logger.info(f"CopywriterAgent ({self.name}) architecting content...")
        return await super().__call__(state)
