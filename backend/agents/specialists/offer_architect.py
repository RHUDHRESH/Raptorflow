"""
Offer Architect Specialist Agent
Defines revenue models, pricing logic, and outcome mapping.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from ..config import ModelTier

from ..base import BaseAgent
from ..state import AgentState

logger = logging.getLogger(__name__)


class OfferArchitect(BaseAgent):
    """Specialist agent for offer architecture and pricing models."""

    def __init__(self):
        super().__init__(
            name="OfferArchitect",
            description="Architects revenue models and validates offer strength",
            model_tier=ModelTier.FLASH,
            tools=["database", "web_search"],
            skills=[
                "revenue_modeling",
                "pricing_strategy",
                "risk_reversal_optimization",
            ],
        )

    def get_system_prompt(self) -> str:
        return """You are the OfferArchitect.
        Your role is to transform a business's core capabilities into a high-leverage offer.

        Key Responsibilities:
        1. Define the Revenue Model (Subscription, One-time, Performance-based, etc.)
        2. Establish Pricing Logic based on Value and Outcome.
        3. Audit the 'Risk Reversal' (Guarantees) for maximum conversion strength.
        4. Map Outcomes to specific Deliverables in the Business Context Map (BCM).

        Be surgical. Use 'Editorial Restraint'. Focus on conversion-ready offer structures."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute offer architecture analysis."""
        logger.info("OfferArchitect: Analyzing offer structure")

        business_context = state.get("business_context", {})
        step_data = state.get("step_data", {})

        # Prepare prompt for LLM
        prompt = f"""
        Analyze the following business context and verified facts to architect a high-converting offer.

        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}

        VERIFIED FACTS:
        {json.dumps(step_data.get("truth_sheet", {}), indent=2)}

        Output a JSON object with:
        - revenue_model: string
        - pricing_logic: string
        - risk_reversal: {{score: float (0-1), feedback: string}}
        - outcome_mapping: list of {{outcome: string, deliverable: string}}
        """

        res = await self._call_llm(prompt)

        try:
            # Clean LLM output
            clean_res = res.strip().replace("```json", "").replace("```", "")
            analysis = json.loads(clean_res)
            return {"output": analysis}
        except Exception as e:
            logger.error(f"OfferArchitect: Failed to parse LLM response: {e}")
            return {"error": f"Failed to parse analysis: {str(e)}", "output": {}}

    def calculate_ltv(self, model_type: str, price: float, months: int = 12) -> float:
        """Calculate Life Time Value (LTV) for a model."""
        if model_type.lower() in ["subscription", "recurring", "saas"]:
            return price * months
        return price
