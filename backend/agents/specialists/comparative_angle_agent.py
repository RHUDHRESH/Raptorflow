"""
Comparative Angle Specialist Agent
Generates comparative angles and competitive positioning
"""

import json
import logging
from typing import Any, Dict, List, Optional

from ..config import ModelTier

from ..base import BaseAgent
from ..state import AgentState

logger = logging.getLogger(__name__)


class ComparativeAngleGenerator(BaseAgent):
    """Specialist agent for generating competitive alternatives and angles."""

    def __init__(self):
        super().__init__(
            name="ComparativeAngleGenerator",
            description="Generates strategic comparative angles against competitors",
            model_tier=ModelTier.FLASH,
            tools=["database", "web_search"],
            skills=[
                "competitive_analysis",
                "strategic_positioning",
                "angle_generation",
            ],
        )

    def get_system_prompt(self) -> str:
        return """You are the ComparativeAngleGenerator.
        Your goal is to define how the user's product compares to the alternatives found in research.

        Key Responsibilities:
        1. Identify the 'Vantage Point': The unique high ground you hold.
        2. Identify 'Your Leverage': What unfair advantage do you have?
        3. Build 'Rival Hook vs Your Gap' Mapping: Map competitor's main marketing hook to the gap/weakness it creates, and how you fill it.
        4. Detect Competitor Weaknesses: Based on customer verbatims and market data.

        Be surgical. Use 'Editorial Restraint'. Focus on positioning that creates a 'Must-Have' realization for the ICP."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute comparative angle generation."""
        logger.info("ComparativeAngleGenerator: Mapping competitive landscape")

        business_context = state.get("business_context", {})
        market_intelligence = state.get("step_data", {}).get("market_intelligence", {})

        prompt = f"""
        Analyze the business context and market intelligence to define a superior competitive position.

        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}

        MARKET INTELLIGENCE (Reddit/Titan results):
        {json.dumps(market_intelligence, indent=2)}

        Output a JSON object with:
        - vantage_point: string (The strategic high ground)
        - leverage: string (Your unfair advantage)
        - competitor_mapping: list of {{
            name: string,
            hook: string (Their main claim),
            gap: string (The weakness/downside of their claim),
            your_angle: string (How you win)
          }}
        - differentiation_score: float (0-100)
        """

        res = await self._call_llm(prompt)

        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            angles = json.loads(clean_res)
            return {"output": angles}
        except Exception as e:
            logger.error(
                f"ComparativeAngleGenerator: Failed to parse LLM response: {e}"
            )
            return {
                "error": f"Failed to parse comparative angles: {str(e)}",
                "output": {},
            }
