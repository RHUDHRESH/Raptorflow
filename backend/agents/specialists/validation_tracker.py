"""
Validation Tracker Specialist Agent
Audits launch readiness and tracks non-content strategic tasks.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)


class ValidationTracker(BaseAgent):
    """Specialist agent for reality checks and launch readiness auditing."""

    def __init__(self):
        super().__init__(
            name="ValidationTracker",
            description="Audits strategic readiness and tracks validation protocols",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["readiness_audit", "task_tracking", "reality_check_synthesis"],
        )

    def get_system_prompt(self) -> str:
        return """You are the ValidationTracker.
        Your goal is to perform a final 'Reality Check' before the brand goes live.

        Key Responsibilities:
        1. Launch Readiness Auditor: Assign an AI score (0-100) based on data completeness and consistency.
        2. Non-Content Task Tracking: Identify specific actions needed (e.g., 'Verify CISO email list', 'Test pricing link').
        3. Skip/Commit Logic: Identify which strategic gaps can be skipped vs. which must be committed to.
        4. Consistency Audit: Do the ICP, Offer, and Messaging actually align?

        Be an objective auditor. High standards only. Use 'Editorial Restraint'."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute readiness audit and task generation."""
        logger.info("ValidationTracker: Performing reality check")

        business_context = state.get("business_context", {})
        step_data = state.get("step_data", {})

        prompt = f"""
        Audit the entire onboarding state for launch readiness.
        Identify remaining gaps and non-content tasks.

        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}

        STEP DATA (Insights extracted so far):
        {json.dumps(step_data, indent=2)}

        Output a JSON object with:
        - readiness_score: int (0-100)
        - audit_report: string (Executive summary of state)
        - tasks: list of {{name: string, reason: string, priority: string}}
        - skip_commit_logic: string (What to ignore vs what to fix)
        - alignment_check: {{icp_offer: bool, offer_messaging: bool, messaging_icp: bool}}
        """

        res = await self._call_llm(prompt)

        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_res)
            return {"output": data}
        except Exception as e:
            logger.error(f"ValidationTracker: Failed to parse LLM response: {e}")
            return {"error": f"Failed to parse readiness audit: {str(e)}", "output": {}}
