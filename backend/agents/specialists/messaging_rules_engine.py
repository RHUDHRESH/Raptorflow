"""
Messaging Rules Engine Specialist Agent
Generates and enforces messaging guardrails, forbidden words, and anti-patterns.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)


class MessagingRulesEngine(BaseAgent):
    """Specialist agent for brand messaging guardrails and rule enforcement."""

    def __init__(self):
        super().__init__(
            name="MessagingRulesEngine",
            description="Generates brand messaging guardrails and detects forbidden patterns",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["brand_governance", "anti_pattern_detection", "voice_consistency"],
        )

    def get_system_prompt(self) -> str:
        return """You are the MessagingRulesEngine.
        Your goal is to define the 'Do's and Don'ts' of the brand voice to ensure absolute consistency.

        Key Responsibilities:
        1. Messaging Guardrails: Define the core pillars of the brand voice (e.g., 'Surgical', 'Poetic', 'Restrained').
        2. Forbidden Words: Identify specific words or phrases that must NEVER be used (e.g., Jargon like 'Synergy', 'Paradigm').
        3. Anti-Pattern Alerts: Identify common industry messaging tropes that this brand must avoid.
        4. Real-time Detection Logic: Prepare the patterns for automated enforcement.

        Be strict. The brand's integrity depends on these rules. Use 'Editorial Restraint'."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute messaging rules generation."""
        logger.info("MessagingRulesEngine: Establishing guardrails")

        business_context = state.get("business_context", {})
        strategic_lock = state.get("step_data", {}).get("strategic_grid", {})

        prompt = f"""
        Analyze the business context and strategic position to generate strict messaging guardrails.

        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}

        STRATEGIC POSITION:
        {json.dumps(strategic_lock, indent=2)}

        Output a JSON object with:
        - rules: list of {{type: string, rule: string, do: string, dont: string}}
        - forbidden_words: list of strings
        - anti_patterns: list of strings
        - rationale: string
        """

        res = await self._call_llm(prompt)

        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_res)
            return {"output": data}
        except Exception as e:
            logger.error(f"MessagingRulesEngine: Failed to parse LLM response: {e}")
            return {"error": f"Failed to parse messaging rules: {str(e)}", "output": {}}
