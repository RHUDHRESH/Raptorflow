import logging
from typing import Any, Dict, List

from pydantic import BaseModel

from backend.agents.base import BaseCognitiveAgent
from backend.models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.content_repurposer")


class MicroAsset(BaseModel):
    """SOTA structured short-form asset."""

    platform: str
    content: str
    strategic_hook: str


class RepurposedOutput(BaseModel):
    """SOTA structured repurposing result."""

    source_summary: str
    micro_assets: List[MicroAsset]
    atomization_rationale: str


class ContentRepurposerAgent(BaseCognitiveAgent):
    """
    A16: The Content Atomizer.
    Persona: Master Content Atomizer.
    Instructions: MusePrompts.CONTENT_REPURPOSER.
    """

    def __init__(self):
        from backend.core.prompts import MusePrompts

        super().__init__(
            name="ContentRepurposer",
            role="creator",
            system_prompt=MusePrompts.CONTENT_REPURPOSER,
            model_tier="driver",
            output_schema=RepurposedOutput,
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Executes content atomization."""
        logger.info("ContentRepurposerAgent atomizing assets...")
        return await super().__call__(state)
