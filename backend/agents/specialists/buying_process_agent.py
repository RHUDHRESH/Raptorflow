"""
Buying Process Specialist Agent
Maps the sales cycle, buyer journey, and decision-making milestones
"""

import logging
from typing import Any, Dict, List, Optional
from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)

class BuyingProcessArchitect(BaseAgent):
    """Specialist agent for architecting the buying process."""

    def __init__(self):
        super().__init__(
            name="BuyingProcessArchitect",
            description="Maps the B2B buying journey and sales cycle",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["buyer_journey_mapping", "sales_process_design", "milestone_definition"]
        )

    def get_system_prompt(self) -> str:
        return """You are the BuyingProcessArchitect.
        Your goal is to define the specific steps a customer takes from awareness to purchase.
        Identify key decision-makers at each stage and the 'Trust Milestones' needed to advance."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute buying process mapping."""
        # 1. Get ICP Data
        # 2. Map Stages
        # 3. Define Milestones
        
        stages = [
            {
                "stage": "Awareness",
                "buyer_action": "Recognizes zero-day vulnerability gap",
                "trust_milestone": "Educational whitepaper download"
            },
            {
                "stage": "Consideration",
                "buyer_action": "Evaluates AI vs Legacy firewalls",
                "trust_milestone": "Technical proof-of-concept (POC)"
            },
            {
                "stage": "Decision",
                "buyer_action": "CISO approval and budget sign-off",
                "trust_milestone": "Security audit completion"
            }
        ]
        
        return {
            "output": {
                "buying_stages": stages,
                "sales_cycle_complexity": "High"
            }
        }
