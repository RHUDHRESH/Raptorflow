"""
Strategic Grid Specialist Agent
Populates the 2x2 grid (Value vs Rarity) for core assets
"""

import logging
from typing import Any, Dict, List, Optional
from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)

class StrategicGridGenerator(BaseAgent):
    """Specialist agent for generating the strategic assets grid."""

    def __init__(self):
        super().__init__(
            name="StrategicGridGenerator",
            description="Maps business assets on a Value vs Rarity grid",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["strategic_analysis", "asset_valuation", "competitive_positioning"]
        )

    def get_system_prompt(self) -> str:
        return """You are the StrategicGridGenerator.
        Your goal is to evaluate core business assets (tech, team, brand, relationships) and map them on a 2x2 grid:
        - Value (How much does it help win?)
        - Rarity (How hard is it for competitors to copy?)"""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute strategic grid generation."""
        # 1. Get Assets
        # 2. Score Value & Rarity
        
        assets = [
            {
                "asset": "Proprietary AI Model",
                "value": 9,
                "rarity": 8,
                "quadrant": "Core Competency"
            },
            {
                "asset": "Customer Support",
                "value": 7,
                "rarity": 4,
                "quadrant": "Necessary Evil"
            }
        ]
        
        return {
            "output": {
                "grid_assets": assets,
                "moat_strength": 7.5
            }
        }
