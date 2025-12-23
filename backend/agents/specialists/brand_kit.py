import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.agents.base import BaseCognitiveAgent
from backend.core.prompts import StrategyPrompts
from backend.models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.brand_kit")

class BrandKitOutput(BaseModel):
    """SOTA structured Brand Kit."""
    brand_values: List[str] = Field(description="Exactly 3 core values.")
    visual_palette: Dict[str, str] = Field(description="Primary, secondary, and accent colors.")
    voice_adjectives: List[str] = Field(description="3 adjectives defining the tone.")
    taglines: List[str] = Field(description="Key marketing one-liners found or created.")

class BrandKitAgent(BaseCognitiveAgent):
    """
    A04: The Brand Kit Architect.
    Persona: Industrial Brand Architect.
    Instructions: StrategyPrompts.BRAND_KIT_EXTRACTOR.
    """
    def __init__(self):
        super().__init__(
            name="BrandKitArchitect",
            role="strategist",
            system_prompt=StrategyPrompts.BRAND_KIT_EXTRACTOR,
            model_tier="ultra",
            output_schema=BrandKitOutput
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Executes brand kit extraction."""
        logger.info("BrandKitAgent extracting assets...")
        return await super().__call__(state)
