"""
Message Hierarchy Specialist Agent
Defines the structural cascade of brand messaging and assembles the final manifesto.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from ..config import ModelTier

from ..base import BaseAgent
from ..state import AgentState

logger = logging.getLogger(__name__)


class MessageHierarchyArchitect(BaseAgent):
    """Specialist agent for brand message hierarchy and content assembly."""

    def __init__(self):
        super().__init__(
            name="MessageHierarchyArchitect",
            description="Architects the structural cascade of brand messaging and assembles final content",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["messaging_hierarchy", "content_assembly", "structural_validation"],
        )

    def get_system_prompt(self) -> str:
        return """You are the MessageHierarchyArchitect.
        Your goal is to ensure the brand strategy cascades perfectly from the highest abstraction (Manifesto) to the lowest detail (Feature).

        Key Responsibilities:
        1. Level 1-3 Structural Validation:
           - Level 1: The Soul (Manifesto/Belief).
           - Level 2: The Logic (Core Strategic Pillars).
           - Level 3: The Proof (Features/Evidence).
        2. Headline-to-Body Mapping: Ensure every headline has a corresponding body copy that delivers on the promise.
        3. Manifesto Assembly: Combine all winning elements into a final, decision-ready brand manifesto.
        4. Integrity Check: Ensure no logical gaps exist between levels.

        Be structural. The messaging must be a cohesive 'Wall of Evidence'. Use 'Editorial Restraint'."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute message hierarchy assembly."""
        logger.info("MessageHierarchyArchitect: Assembling hierarchy")

        business_context = state.get("business_context", {})
        positioning = state.get("step_data", {}).get("positioning_statements", {})
        soundbites = state.get("step_data", {}).get("soundbites_library", {})

        prompt = f"""
        Architect the final message hierarchy and assemble the brand manifesto.
        Ensure Level 1, 2, and 3 are logically linked.

        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}

        POSITIONING & SOUNDBITES:
        {json.dumps(positioning, indent=2)}
        {json.dumps(soundbites, indent=2)}

        Output a JSON object with:
        - levels: {{L1: string, L2: list, L3: list}}
        - mapping: list of {{headline: string, body: string, level: int}}
        - manifesto_assembly: string (The final curated manifesto)
        - validation: {{integrity: float, checks: list of strings}}
        """

        res = await self._call_llm(prompt)

        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_res)
            return {"output": data}
        except Exception as e:
            logger.error(
                f"MessageHierarchyArchitect: Failed to parse LLM response: {e}"
            )
            return {"error": f"Failed to parse hierarchy: {str(e)}", "output": {}}
