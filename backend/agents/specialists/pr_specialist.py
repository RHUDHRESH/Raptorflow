import logging
from typing import Any, Dict

from agents.base import BaseCognitiveAgent
from models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.pr_specialist")


class PRSpecialistAgent(BaseCognitiveAgent):
    """
    The PR & Media Specialist.
    Specializes in outreach, journalist pitches, and media event discovery.
    """

    def __init__(self):
        from core.prompts import AssetSpecializations

        super().__init__(
            name="PRSpecialistAgent",
            role="pr_specialist",
            system_prompt=AssetSpecializations.PR_SPECIALIST,
            model_tier="driver",
            auto_assign_tools=True,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        logger.info(f"PRSpecialistAgent ({self.name}) architecting outreach...")
        return await super().__call__(state)
