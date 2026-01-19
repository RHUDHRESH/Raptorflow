"""
Perceptual Map Generator Agent
Creates AI-powered positioning maps with strategic options and competitor placement.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)

class PerceptualMapGenerator(BaseAgent):
    """Specialist agent for quadrant analysis and strategic positioning options."""

    def __init__(self):
        super().__init__(
            name="PerceptualMapGenerator",
            description="Generates strategic perceptual maps and positioning options",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["strategic_mapping", "competitive_positioning", "quadrant_analysis"]
        )

    def get_system_prompt(self) -> str:
        return """You are the PerceptualMapGenerator.
        Your goal is to map the competitive landscape onto a 2D plane (X and Y axes) and identify the 'Only You' quadrant.
        
        Key Responsibilities:
        1. Select Optimal Axes: Choose two dimensions that maximize differentiation (e.g., Speed vs. Coverage, Precision vs. Ease).
        2. Place Competitors: Use research data to coordinate competitors on a 0.0 to 1.0 scale.
        3. Identify 'Only You' Quadrant: The area where you have zero direct competition based on Tier 4 capabilities.
        4. Propose 3 Positioning Options: Different ways to own the high ground.
        
        Be precise. The coordinates must reflect the true market reality. Use 'Editorial Restraint'."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute perceptual mapping analysis."""
        logger.info("PerceptualMapGenerator: Creating strategic map")
        
        business_context = state.get("business_context", {})
        market_intelligence = state.get("step_data", {}).get("market_intelligence", {})
        capability_rating = state.get("step_data", {}).get("capability_rating", {})
        
        prompt = f"""
        Analyze the business context, market intelligence, and capability ratings to generate a perceptual map.
        
        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}
        
        MARKET INTELLIGENCE:
        {json.dumps(market_intelligence, indent=2)}
        
        CAPABILITY RATINGS:
        {json.dumps(capability_rating, indent=2)}
        
        Output a JSON object with:
        - primary_axis: {{name: string, low_label: string, high_label: string}}
        - secondary_axis: {{name: string, low_label: string, high_label: string}}
        - competitors: list of {{name: string, x: float, y: float, description: string}}
        - positioning_options: list of {{name: string, description: string, coordinates: [float, float], rationale: string}}
        - only_you_quadrant: string (Which area is empty and why you own it)
        """
        
        res = await self._call_llm(prompt)
        
        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            map_data = json.loads(clean_res)
            return {
                "output": map_data
            }
        except Exception as e:
            logger.error(f"PerceptualMapGenerator: Failed to parse LLM response: {e}")
            return {
                "error": f"Failed to parse perceptual map: {str(e)}",
                "output": {}
            }
        
