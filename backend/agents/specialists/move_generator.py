import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.agents.base import BaseCognitiveAgent
from backend.models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.move_generator")


class ActionItem(BaseModel):
    """SOTA structured action item."""

    task: str
    owner: str = Field(description="Agent role or Human.")
    tool_requirements: List[str]


class WeeklyMove(BaseModel):
    """SOTA structured weekly move."""

    week_number: int
    title: str
    description: str
    action_items: List[ActionItem]
    desired_outcome: str


class MovePacketOutput(BaseModel):
    """SOTA structured move generation result."""

    month_theme: str
    moves: List[WeeklyMove]
    strategic_rationale: str = Field(
        description="Why these moves drive the 90-day arc."
    )


class MoveGeneratorAgent(BaseCognitiveAgent):
    """
    A12: The High-Velocity Move Generator.
    Persona: Master of Marketing Execution.
    Instructions: MovePrompts.GENERATOR_SYSTEM.
    """

    def __init__(self):
        from backend.core.prompts import MovePrompts

        super().__init__(
            name="MoveGenerator",
            role="operator",
            system_prompt=MovePrompts.GENERATOR_SYSTEM,
            model_tier="driver",
            output_schema=MovePacketOutput,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Executes weekly move generation."""
        logger.info("MoveGeneratorAgent decomposing arc into moves...")
        return await super().__call__(state)
