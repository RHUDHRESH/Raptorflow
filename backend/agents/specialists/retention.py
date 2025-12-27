import logging
from typing import Any, Dict

from agents.base import BaseCognitiveAgent
from models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.retention")


class RetentionAgent(BaseCognitiveAgent):
    """
    The Retention & LTV Specialist.
    Specializes in lifecycle marketing, churn prediction, and LTV maximization.
    """

    def __init__(self):
        from core.prompts import AssetSpecializations

        super().__init__(
            name="RetentionAgent",
            role="retention",
            system_prompt=AssetSpecializations.RETENTION,
            model_tier="driver",
            auto_assign_tools=True,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        logger.info(f"RetentionAgent ({self.name}) calculating survival probability...")
        return await super().__call__(state)
