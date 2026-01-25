"""
Constraint Engine Specialist Agent
Enforces strategic trade-offs and focus/sacrifice decisions.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from ..base import BaseAgent
from backend.agents.config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)

class ConstraintEngine(BaseAgent):
    """Specialist agent for focus & sacrifice constraint enforcement."""

    def __init__(self):
        super().__init__(
            name="ConstraintEngine",
            description="Enforces strategic focus by identifying necessary sacrifices",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["strategic_tradeoffs", "focus_optimization", "constraint_mapping"]
        )

    def get_system_prompt(self) -> str:
        return """You are the ConstraintEngine. 
        Your role is to enforce the most painful but necessary part of strategy: SACRIFICE.
        
        Key Responsibilities:
        1. Identify Focus Areas: Where should the company double down?
        2. Identify Forced Sacrifices: What segments, features, or markets must be abandoned to win elsewhere?
        3. 'Lightbulb' Explanations: Provide the non-obvious logic why a sacrifice is actually an advantage.
        4. David vs Goliath Logic: How to use limited resources to topple incumbents by being more focused.
        
        Be ruthless. True strategy is a series of 'No's. Use 'Editorial Restraint'."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute focus & sacrifice analysis."""
        logger.info("ConstraintEngine: Identifying strategic sacrifices")
        
        business_context = state.get("business_context", {})
        strategic_lock = state.get("step_data", {}).get("strategic_grid", {})
        
        prompt = f"""
        Analyze the business context and strategic position to enforce focus through sacrifice.
        Identify what must be given up to achieve the 'Surgical' position.
        
        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}
        
        STRATEGIC POSITION:
        {json.dumps(strategic_lock, indent=2)}
        
        Output a JSON object with:
        - focus_areas: list of strings
        - sacrifices: list of {{target: string, rationale: string, lightbulb: string}}
        - logic: string (Explain the David vs Goliath leverage)
        - risk_score: float (0.0-1.0, risk of NOT focusing)
        """
        
        res = await self._call_llm(prompt)
        
        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_res)
            return {
                "output": data
            }
        except Exception as e:
            logger.error(f"ConstraintEngine: Failed to parse LLM response: {e}")
            return {
                "error": f"Failed to parse constraints: {str(e)}",
                "output": {}
            }
