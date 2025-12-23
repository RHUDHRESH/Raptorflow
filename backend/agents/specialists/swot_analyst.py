import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.agents.base import BaseCognitiveAgent
from backend.models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.swot_analyst")

class SWOTOutput(BaseModel):
    """SOTA structured SWOT analysis result."""
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    strategic_summary: str = Field(description="The high-leverage strategic takeaway.")

class SWOTAnalystAgent(BaseCognitiveAgent):
    """
    A09: The Strategic SWOT Analyst.
    Persona: Master Strategic Consultant.
    Instructions: StrategyPrompts.SWOT_ANALYZER.
    """
    def __init__(self):
        from backend.core.prompts import StrategyPrompts
        super().__init__(
            name="SWOTAnalyst",
            role="strategist",
            system_prompt=StrategyPrompts.SWOT_ANALYZER,
            model_tier="ultra",
            output_schema=SWOTOutput
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Executes SWOT analysis."""
        logger.info("SWOTAnalystAgent analyzing strategic position...")
        return await super().__call__(state)
