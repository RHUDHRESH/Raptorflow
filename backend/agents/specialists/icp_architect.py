import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.agents.base import BaseCognitiveAgent
from backend.core.prompts import StrategyPrompts
from backend.models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.icp_architect")

class ICPPersona(BaseModel):
    """SOTA structured ICP persona."""
    name: str = Field(description="Persona name.")
    demographics: Dict[str, Any] = Field(description="Age, Location, Job Title, Industry.")
    psychographics: Dict[str, Any] = Field(description="Values, Interests, Lifestyle, Status Games.")
    pain_points: List[str] = Field(description="Core frustrations.")
    buying_triggers: List[str] = Field(description="Events that force a decision.")

class ICPOutput(BaseModel):
    """SOTA structured ICP result."""
    personas: List[ICPPersona]
    summary: str = Field(description="Executive summary of the target cohorts.")

class ICPArchitectAgent(BaseCognitiveAgent):
    """
    A05: The ICP Architect.
    Persona: Cognitive Psychologist & Market Researcher.
    Instructions: StrategyPrompts.ICP_PROFILER.
    """
    def __init__(self):
        super().__init__(
            name="ICPArchitect",
            role="researcher",
            system_prompt=StrategyPrompts.ICP_PROFILER,
            model_tier="reasoning",
            output_schema=ICPOutput
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Executes ICP profiling."""
        logger.info("ICPArchitectAgent profiling cohorts...")
        return await super().__call__(state)