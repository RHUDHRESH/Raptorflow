"""
ICP Architect Specialist Agent
Creates deep Ideal Customer Profiles using psychographics and market sophistication models.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)


class ICPArchitect(BaseAgent):
    """Specialist agent for deep ICP profiling and psychographic mapping."""

    def __init__(self):
        super().__init__(
            name="ICPArchitect",
            description="Architects deep Ideal Customer Profiles with market sophistication analysis",
            model_tier=ModelTier.FLASH,
            tools=["database", "web_search"],
            skills=[
                "icp_architecture",
                "psychographic_mapping",
                "market_sophistication_analysis",
            ],
        )

    def get_system_prompt(self) -> str:
        return """You are the ICPArchitect.
        Your goal is to define the Ideal Customer Profile (ICP) with surgical depth.

        Key Responsibilities:
        1. 'Who They Want To Become': Map the customer's transformation journey (Identity Shift).
        2. Market Sophistication (Level 1-5):
           - Level 1: First to market (Feature focus).
           - Level 2: Competition exists (Mechanism focus).
           - Level 3: Market is skeptical (Deep mechanism focus).
           - Level 4: Market is saturated (Identity/Lifestyle focus).
           - Level 5: Market is dead (Emotion/Belief focus).
        3. Behavioral Triggers: Identify the specific events that cause them to seek a solution.
        4. Tiered Profiles: Primary, Secondary, and Tertiary ICPs.

        Be precise. Rejects generic personas. Use 'Editorial Restraint'."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute deep ICP profiling."""
        logger.info("ICPArchitect: Building deep customer profiles")

        business_context = state.get("business_context", {})
        market_intelligence = state.get("step_data", {}).get("market_intelligence", {})
        focus_sacrifice = state.get("step_data", {}).get("focus_sacrifice", {})

        prompt = f"""
        Analyze the business context, market intelligence, and strategic focus to architect deep ICP profiles.
        Focus on psychographics and market sophistication.

        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}

        MARKET INTELLIGENCE:
        {json.dumps(market_intelligence, indent=2)}

        STRATEGIC FOCUS:
        {json.dumps(focus_sacrifice, indent=2)}

        Output a JSON object with:
        - profiles: list of {{
            name: string,
            tagline: string,
            who_they_want_to_become: string (Identity Shift),
            sophistication_level: int (1-5),
            behavioral_triggers: list of strings,
            pain_points: list of strings,
            fears: list of strings,
            aspirations: list of strings
          }}
        - primary_icp: string (name of the primary profile)
        - strategy_summary: string
        """

        res = await self._call_llm(prompt)

        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_res)
            return {"output": data}
        except Exception as e:
            logger.error(f"ICPArchitect: Failed to parse LLM response: {e}")
            return {"error": f"Failed to parse ICP profiles: {str(e)}", "output": {}}
