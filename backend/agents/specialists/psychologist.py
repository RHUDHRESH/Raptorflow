import logging
from typing import Any, Dict

from agents.base import BaseCognitiveAgent
from models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.psychologist")


class PsychologistAgent(BaseCognitiveAgent):
    """
    The Behavioral Psychologist.
    Specializes in consumer triggers, JTBD, and influence principles.
    """

    def __init__(self):
        from core.prompts import AssetSpecializations

        super().__init__(
            name="PsychologistAgent",
            role="psychologist",
            system_prompt=AssetSpecializations.PSYCHOLOGIST,
            model_tier="driver",
            auto_assign_tools=True,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        logger.info(f"PsychologistAgent ({self.name}) mapping consumer triggers...")
        return await super().__call__(state)
