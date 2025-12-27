import logging
from typing import Any, Dict

from agents.base import BaseCognitiveAgent
from models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.direct_response")


class DirectResponseAgent(BaseCognitiveAgent):
    """
    The Direct Response Architect.
    Specializes in ROI, conversion, and scientific advertising.
    """

    def __init__(self):
        from core.prompts import AssetSpecializations

        super().__init__(
            name="DirectResponseAgent",
            role="direct_response",
            system_prompt=AssetSpecializations.DIRECT_RESPONSE,
            model_tier="driver",
            auto_assign_tools=True,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        logger.info(f"DirectResponseAgent ({self.name}) optimizing for conversion...")
        return await super().__call__(state)
