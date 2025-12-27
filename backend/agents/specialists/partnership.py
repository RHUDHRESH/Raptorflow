import logging
from typing import Any, Dict

from agents.base import BaseCognitiveAgent
from models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.partnership")


class PartnershipAgent(BaseCognitiveAgent):
    """
    The Partnership & Affiliate Hunter.
    Specializes in leverage, audience overlap, and win-win incentive modeling.
    """

    def __init__(self):
        from core.prompts import AssetSpecializations

        super().__init__(
            name="PartnershipAgent",
            role="partnership",
            system_prompt=AssetSpecializations.PARTNERSHIP,
            model_tier="driver",
            auto_assign_tools=True,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        logger.info(f"PartnershipAgent ({self.name}) hunting for leverage...")
        return await super().__call__(state)
