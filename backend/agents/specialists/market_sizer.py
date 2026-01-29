"""
Market Sizer Specialist Agent
Calculates TAM, SAM, and SOM based on real-world market data.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)


class MarketSizer(BaseAgent):
    """Specialist agent for market sizing and TAM/SAM/SOM calculations."""

    def __init__(self):
        super().__init__(
            name="MarketSizer",
            description="Calculates market size (TAM/SAM/SOM) using industry benchmarks",
            model_tier=ModelTier.FLASH,
            tools=["database", "web_search"],
            skills=["market_sizing", "financial_modeling", "industry_research"],
        )

    def get_system_prompt(self) -> str:
        return """You are the MarketSizer.
        Your goal is to calculate the market potential for the user's business with financial precision.

        Definitions:
        - TAM (Total Addressable Market): The total market demand if 100% of the world were customers.
        - SAM (Serviceable Addressable Market): The portion of the TAM that can be reached by the product.
        - SOM (Serviceable Obtainable Market): The portion of the SAM that can realistically be captured.

        Key Responsibilities:
        1. TAM/SAM/SOM Calculation: Provide specific dollar amounts based on industry research.
        2. Market Reality Check: Is the market growing or shrinking?
        3. Competitor Share Estimate: How much of the SOM is already held by rivals?

        Be realistic. Investors hate inflated TAMs. Use 'Editorial Restraint'."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute market sizing analysis."""
        logger.info("MarketSizer: Calculating market potential")

        business_context = state.get("business_context", {})
        icp_profiles = state.get("step_data", {}).get("icp_profiles", {})

        prompt = f"""
        Calculate the TAM, SAM, and SOM for the following business.
        Use industry benchmarks and research data.

        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}

        ICP PROFILES:
        {json.dumps(icp_profiles, indent=2)}

        Output a JSON object with:
        - tam: number (Total USD)
        - sam: number (Total USD)
        - som: number (Total USD)
        - reality_check: string (Analysis of market health)
        - unit_economics_hint: string (e.g. CAC/LTV estimate)
        """

        res = await self._call_llm(prompt)

        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_res)
            return {"output": data}
        except Exception as e:
            logger.error(f"MarketSizer: Failed to parse LLM response: {e}")
            return {"error": f"Failed to parse market size: {str(e)}", "output": {}}
