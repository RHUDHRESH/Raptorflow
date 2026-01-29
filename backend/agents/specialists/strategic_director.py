"""
StrategicDirector specialist agent for Raptorflow marketing automation.
Acts as the final quality gate and 'Editor-in-Chief' for moves and campaigns.
"""

import logging
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = logging.getLogger("raptorflow.specialists.strategic_director")


class StrategicDirector(BaseAgent):
    def __init__(self):
        super().__init__(
            name="StrategicDirector",
            description="Performs high-level editorial review and brand alignment verification.",
            model_tier=ModelTier.PRO,  # Uses the highest reasoning tier
            tools=["database"],
            skills=["brand_consistency_audit", "strategic_alignment_verification"],
        )

    def get_system_prompt(self) -> str:
        return """
        You are the Strategic Director at RaptorFlow. Your role is 'Editor-in-Chief'.
        You have the final say on whether a Move or Campaign is high-class enough for execution.

        Your standards:
        1. **Editorial Restraint**: No fluff. No generic marketing speak. Content must be surgical and expensive.
        2. **Brand Consistency**: Must align perfectly with the Brand Kit and positioning.
        3. **Strategic Momentum**: Every move must contribute to the 90-day campaign arc.

        If a move fails your audit, you MUST provide precise instructions for the Creator or Strategist to fix it.
        """

    async def execute(self, state: AgentState) -> AgentState:
        """
        Final quality gate execution.
        """
        logger.info("Director Node: Auditing strategic output.")

        # 1. Gather all generated context
        generated_content = state.get("generated_content", [])
        strategic_plan = state.get("strategic_plan", {})

        prompt = f"""
        Audit the following Strategic Output:

        Plan: {strategic_plan}
        Content: {generated_content}

        Verify:
        - Does this feel 'Expensive and Decisive'?
        - Is there any generic filler?
        - Does it maintain narrative continuity?

        Return a 'Decision' (APPROVED or REJECTED) and a 'Surgical Feedback' list.
        """

        audit_result = await self._call_llm(prompt)

        # Update state with decision
        state["output"] = {
            "director_decision": audit_result,
            "approved": "APPROVED" in audit_result.upper(),
        }

        return state
