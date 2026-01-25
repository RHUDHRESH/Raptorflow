"""
Buying Process Specialist Agent
Maps the buyer journey, cognitive shifts, and the problem-to-product chasm.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from backend.agents.config import ModelTier

from ..base import BaseAgent
from ..state import AgentState

logger = logging.getLogger(__name__)


class BuyingProcessArchitect(BaseAgent):
    """Specialist agent for architecting the educational and buying journey."""

    def __init__(self):
        super().__init__(
            name="BuyingProcessArchitect",
            description="Architects the buyer journey with cognitive shift mapping",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=[
                "buyer_journey_mapping",
                "cognitive_shift_analysis",
                "sales_cycle_design",
            ],
        )

    def get_system_prompt(self) -> str:
        return """You are the BuyingProcessArchitect.
        Your goal is to map the stages a customer must go through to become a 'True Believer' in the product.

        Key Responsibilities:
        1. Cognitive Shift Mapping: For every stage, identify the specific shift in the buyer's mind (e.g., 'From: CRM is a database -> To: CRM is an automated operator').
        2. The 'Chasm' Logic: Identify the gap between being 'Problem Aware' and 'Product Aware' and how to cross it.
        3. Educational Steps: What do they need to learn before they can buy?
        4. Trust Milestones: Specific data points or evidence needed to advance.

        Focus on psychological momentum. Use 'Editorial Restraint'."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute buyer journey mapping."""
        logger.info("BuyingProcessArchitect: Architecting the journey")

        business_context = state.get("business_context", {})
        icp_profiles = state.get("step_data", {}).get("icp_profiles", {})

        prompt = f"""
        Analyze the business context and ICP profiles to architect a 5-stage buyer journey.
        Focus on the cognitive shifts required to cross the chasm.

        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}

        ICP PROFILES:
        {json.dumps(icp_profiles, indent=2)}

        Output a JSON object with:
        - journey: list of {{
            stage: string,
            cognitive_shift: string,
            educational_requirements: list of strings,
            trust_milestones: list of strings,
            chasm: bool (is this the chasm stage?)
          }}
        - chasm_logic: string (How to cross from problem to product)
        - sales_cycle_complexity: string
        """

        res = await self._call_llm(prompt)

        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_res)
            return {"output": data}
        except Exception as e:
            logger.error(f"BuyingProcessArchitect: Failed to parse LLM response: {e}")
            return {"error": f"Failed to parse buyer journey: {str(e)}", "output": {}}
