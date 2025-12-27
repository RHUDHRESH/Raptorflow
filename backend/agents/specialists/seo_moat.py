import logging
from typing import Any, Dict

from agents.base import BaseCognitiveAgent
from models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.seo_moat")


class SEOMoatAgent(BaseCognitiveAgent):
    """
    The SEO & Content Moat Builder.
    Specializes in topical authority, keyword clustering, and organic durability.
    """

    def __init__(self):
        from core.prompts import AssetSpecializations

        super().__init__(
            name="SEOMoatAgent",
            role="seo_moat",
            system_prompt=AssetSpecializations.SEO_MOAT,
            model_tier="driver",
            auto_assign_tools=True,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        logger.info(f"SEOMoatAgent ({self.name}) architecting content moat...")
        return await super().__call__(state)
