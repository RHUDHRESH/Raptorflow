"""
Comparative Angle Specialist Agent
Generates comparative angles and competitive positioning
"""

import logging
from typing import Any, Dict, List, Optional
from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)

class ComparativeAngleGenerator(BaseAgent):
    """Specialist agent for generating competitive alternatives and angles."""

    def __init__(self):
        super().__init__(
            name="ComparativeAngleGenerator",
            description="Generates strategic comparative angles against competitors",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["competitive_analysis", "strategic_positioning", "angle_generation"]
        )

    def get_system_prompt(self) -> str:
        return """You are the ComparativeAngleGenerator.
        Your goal is to define how the user's product compares to the alternatives found in research.
        Generate specific 'Comparative Angles' (e.g., 'The Affordable Alternative', 'The Enterprise Powerhouse')."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute comparative angle generation."""
        # 1. Get Market Insights
        # 2. Identify Competitors
        # 3. Generate Angles
        
        # Mock angles for now
        angles = [
            {
                "competitor": "Industry Giant X",
                "angle": "Precision vs. Mass",
                "narrative": "While Giant X focuses on broad features, we focus on high-precision AI for mid-market security."
            }
        ]
        
        return {
            "output": {
                "comparative_angles": angles,
                "differentiation_score": 82.0
            }
        }
