import logging
from typing import Any, Dict

from agents.base import BaseCognitiveAgent
from models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.viral_alchemist")


class ViralAlchemistAgent(BaseCognitiveAgent):
    """
    The Viral Alchemist.
    Specializes in hooks, social momentum, and trend surfing.
    """

    def __init__(self):
        from core.prompts import AssetSpecializations

        super().__init__(
            name="ViralAlchemistAgent",
            role="viral_alchemist",
            system_prompt=AssetSpecializations.VIRAL_ALCHEMIST,
            model_tier="driver",
            auto_assign_tools=True,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        logger.info(f"ViralAlchemistAgent ({self.name}) architecting viral hooks...")
        return await super().__call__(state)
