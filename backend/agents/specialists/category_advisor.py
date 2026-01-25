"""
Category Advisor Agent
Generates Safe/Clever/Bold category path recommendations for market positioning
"""

import json
import logging
from typing import Any, Dict, List, Optional
from ..base import BaseAgent
from backend.agents.config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)

class CategoryAdvisor(BaseAgent):
    """Specialist agent for category path recommendations."""

    def __init__(self):
        super().__init__(
            name="CategoryAdvisor",
            description="Recommends Safe/Clever/Bold strategic category paths",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["category_design", "strategic_positioning", "market_entry_strategy"]
        )

    def get_system_prompt(self) -> str:
        return """You are the CategoryAdvisor.
        Your goal is to recommend three distinct strategic paths for market entry:
        1. SAFE: Compete in an established category (High demand, High competition).
        2. CLEVER: Reframe an existing category (Unique angle, Lower competition).
        3. BOLD: Create a new category (Maximum differentiation, High education required).
        
        For each path, you MUST provide:
        - Category Name
        - Effort Level (Low/Medium/High/Extreme)
        - Pricing Implication (How this affects price point)
        - Pros & Cons
        - Market Education requirements.
        
        Be strategic. Use 'Editorial Restraint'."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute category path analysis."""
        logger.info("CategoryAdvisor: Analyzing strategic paths")
        
        business_context = state.get("business_context", {})
        comparative_angle = state.get("step_data", {}).get("comparative_angle", {})
        
        prompt = f"""
        Analyze the following business context and competitive vantage point to recommend strategic category paths.
        
        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}
        
        VANTAGE POINT & DIFFERENTIATION:
        {json.dumps(comparative_angle, indent=2)}
        
        Output a JSON object with:
        - safe_path: {{category_name: string, description: string, effort: string, pricing: string, pros: list, cons: list, education: string}}
        - clever_path: {{category_name: string, description: string, effort: string, pricing: string, pros: list, cons: list, education: string}}
        - bold_path: {{category_name: string, description: string, effort: string, pricing: string, pros: list, cons: list, education: string}}
        - recommended_path: string ("safe", "clever", or "bold")
        - rationale: string
        """
        
        res = await self._call_llm(prompt)
        
        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            paths = json.loads(clean_res)
            return {
                "output": paths
            }
        except Exception as e:
            logger.error(f"CategoryAdvisor: Failed to parse LLM response: {e}")
            return {
                "error": f"Failed to parse category paths: {str(e)}",
                "output": {}
            }
