import logging
from typing import Any, Dict

from agents.base import BaseCognitiveAgent
from models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.media_buyer")


class MediaBuyerAgent(BaseCognitiveAgent):
    """
    The Media Buyer Strategist.
    Specializes in paid acquisition, unit economics, and budget optimization.
    """

    def __init__(self):
        from core.prompts import AssetSpecializations

        super().__init__(
            name="MediaBuyerAgent",
            role="media_buyer",
            system_prompt=AssetSpecializations.MEDIA_BUYER,
            model_tier="driver",
            auto_assign_tools=True,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        logger.info(f"MediaBuyerAgent ({self.name}) optimizing ad spend...")
        return await super().__call__(state)
