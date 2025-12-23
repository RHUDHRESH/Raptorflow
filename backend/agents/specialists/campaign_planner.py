import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.agents.base import BaseCognitiveAgent
from backend.models.cognitive import CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.agents.campaign_planner")

class StrategicMilestone(BaseModel):
    """SOTA structured milestone."""
    title: str
    description: str
    target_kpi: str

class MonthlyArc(BaseModel):
    """SOTA structured monthly theme and milestones."""
    month_number: int
    theme: str
    milestones: List[StrategicMilestone]

class CampaignArcOutput(BaseModel):
    """SOTA structured 90-day campaign arc."""
    campaign_title: str
    overall_objective: str
    monthly_arcs: List[MonthlyArc]
    success_metrics: List[str]

class CampaignPlannerAgent(BaseCognitiveAgent):
    """
    A10: The Strategic Campaign Planner.
    Persona: SOTA Fractional CMO.
    Instructions: StrategyPrompts.CAMPAIGN_ARC_PLANNER.
    """
    def __init__(self):
        from backend.core.prompts import StrategyPrompts
        super().__init__(
            name="CampaignPlanner",
            role="strategist",
            system_prompt=StrategyPrompts.CAMPAIGN_ARC_PLANNER,
            model_tier="ultra",
            output_schema=CampaignArcOutput
        )

    async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
        """Executes 90-day campaign planning."""
        logger.info("CampaignPlannerAgent architecting 90-day arc...")
        return await super().__call__(state)

