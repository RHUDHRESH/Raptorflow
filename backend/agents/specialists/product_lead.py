import logging
from typing import Any, Dict

from agents.base import BaseCognitiveAgent
from models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.product_lead")


class ProductLeadAgent(BaseCognitiveAgent):
    """
    The Product Marketing Lead.
    Specializes in GTM strategy, value architecture, and benefit-to-feature mapping.
    """

    def __init__(self):
        from core.prompts import AssetSpecializations

        super().__init__(
            name="ProductLeadAgent",
            role="product_lead",
            system_prompt=AssetSpecializations.PRODUCT_LEAD,
            model_tier="driver",
            auto_assign_tools=True,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        logger.info(f"ProductLeadAgent ({self.name}) architecting value...")
        return await super().__call__(state)
