import logging
from typing import Any, Dict

from agents.base import BaseCognitiveAgent
from models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.brand_philosopher")


class BrandPhilosopherAgent(BaseCognitiveAgent):
    """
    The Brand Philosopher.
    Specializes in positioning, aesthetic, and brand narrative.
    """

    def __init__(self):
        from core.prompts import AssetSpecializations

        super().__init__(
            name="BrandPhilosopherAgent",
            role="brand_philosopher",
            system_prompt=AssetSpecializations.BRAND_PHILOSOPHER,
            model_tier="driver",
            auto_assign_tools=True,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        logger.info(
            f"BrandPhilosopherAgent ({self.name}) architecting brand narrative..."
        )
        return await super().__call__(state)
