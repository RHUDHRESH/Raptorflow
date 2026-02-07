import logging
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from backend.agents.base import BaseCognitiveAgent
from backend.models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.messaging_matrix")


class MessagingPillar(BaseModel):
    """SOTA structured messaging pillar."""

    persona_name: str
    pillar_title: str
    primary_hook: str
    supporting_evidence: str


class MessagingMatrixOutput(BaseModel):
    """SOTA structured messaging matrix result."""

    matrix: List[MessagingPillar]
    overall_narrative: str = Field(
        description="The 'Red Thread' connecting all messaging."
    )


class MessagingMatrixAgent(BaseCognitiveAgent):
    """
    A08: The Messaging Architect.
    Persona: SOTA Messaging Architect.
    Instructions: StrategyPrompts.MESSAGING_MATRIX_GENERATOR.
    """

    def __init__(self):
        from backend.core.prompts import StrategyPrompts

        super().__init__(
            name="MessagingArchitect",
            role="strategist",
            system_prompt=StrategyPrompts.MESSAGING_MATRIX_GENERATOR,
            model_tier="ultra",
            output_schema=MessagingMatrixOutput,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Executes messaging matrix generation."""
        logger.info("MessagingMatrixAgent architecting pillars...")
        return await super().__call__(state)
