import logging
from typing import Any, Dict

from agents.base import BaseCognitiveAgent
from models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.community_catalyst")


class CommunityCatalystAgent(BaseCognitiveAgent):
    """
    The Community Catalyst.
    Specializes in retention, engagement, and social capital.
    """

    def __init__(self):
        from core.prompts import AssetSpecializations

        super().__init__(
            name="CommunityCatalystAgent",
            role="community_catalyst",
            system_prompt=AssetSpecializations.COMMUNITY_CATALYST,
            model_tier="driver",
            auto_assign_tools=True,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        logger.info(
            f"CommunityCatalystAgent ({self.name}) architecting community moves..."
        )
        return await super().__call__(state)
