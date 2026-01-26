"""
Final Synthesis Specialist Agent
Declares 'Systems Online' and converts the final business context into a production BCM.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from backend.agents.config import ModelTier

from ..base import BaseAgent
from ..state import AgentState

logger = logging.getLogger(__name__)


class FinalSynthesis(BaseAgent):
    """Specialist agent for final onboarding synthesis and BCM transition."""

    def __init__(self):
        super().__init__(
            name="FinalSynthesis",
            description="Finalizes the onboarding system and transitions data to production",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["bcm_conversion", "systems_activation", "production_handover"],
        )

    def get_system_prompt(self) -> str:
        return """You are the FinalSynthesis agent.
        Your goal is the ultimate handover: converting the structured onboarding data into a 'Systems Online' state.

        Key Responsibilities:
        1. BCM Conversion: Map the final `business_context.json` into the formal Business Context Map (BCM) schema.
        2. Final Audit: Ensure no critical strategic gaps remain.
        3. Dashboard Handover: Prepare the payload for the Global Dashboard.
        4. Declaration: Formally declare 'Systems Online' once all 23 steps are synthesized.

        Be authoritative. This is the culmination of the founder's strategic journey. Use 'Editorial Restraint'."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute final synthesis and BCM handover."""
        logger.info("FinalSynthesis: Finalizing onboarding")

        business_context = state.get("business_context", {})
        all_step_data = state.get("step_data", {})

        prompt = f"""
        Perform the final synthesis of this onboarding session.
        Convert the following context into a production-ready BCM handover.

        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}

        EXTRACTED INSIGHTS (Step 1-22):
        {json.dumps(all_step_data, indent=2)}

        Output a JSON object with:
        - status: string ("Systems Online" or "Correction Required")
        - bcm_handover: {{nodes: list, edges: list}}
        - dashboard_redirect: string (The target URL)
        - final_audit: string (Final blessing)
        - ucid: string (The confirmed Customer ID)
        """

        res = await self._call_llm(prompt)

        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_res)
            return {"output": data}
        except Exception as e:
            logger.error(f"FinalSynthesis: Failed to parse LLM response: {e}")
            return {"error": f"Failed to parse final synthesis: {str(e)}", "output": {}}
