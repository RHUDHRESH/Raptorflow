import logging
from typing import Any, Dict

from agents.base import BaseCognitiveAgent

logger = logging.getLogger("raptorflow.agents.email_architect")


class EmailSequenceArchitectAgent(BaseCognitiveAgent):
    """
    The Email Sequence Architect.
    Specializes in multi-step drip logic and narrative continuity.
    """

    def __init__(self):
        architect_prompt = """
        # ROLE: World-Class Email Marketing Strategist
        # TASK: Architect multi-step email sequences with surgical precision.

        # HEURISTICS:
        1. NARRATIVE ARC: Every email must bridge the gap between current pain and future success.
        2. DELAYS: Use strategic delays (e.g., 1 day, 3 days) based on psychological fatigue limits.
        3. CTAs: Vary CTA intensity - Soft CTAs early, Hard CTAs late.
        4. SEGMENTATION: Suggest segments based on user engagement.

        # OUTPUT: Return a JSON object with:
        - sequence_title: name of the sequence
        - steps: list of objects {'day': int, 'subject': string, 'goal': string, 'logic': string}
        - total_duration: total days
        - reasoning: strategic justification
        """

        super().__init__(
            name="EmailSequenceArchitectAgent",
            role="email_architect",
            system_prompt=architect_prompt,
            model_tier="driver",
            auto_assign_tools=False,
        )

    async def architect_sequence(self, goal: str, target_icp: str) -> Dict[str, Any]:
        """
        Architects a surgical email sequence.
        """
        logger.info(
            f"EmailSequenceArchitectAgent architecting for {target_icp} with goal: {goal}"
        )

        prompt = (
            f"Architect a 5-email sequence for {target_icp} with the goal of: {goal}"
        )

        response = await self.llm.ainvoke(prompt)
        content = response.content

        import json

        try:
            start_idx = content.find("{")
            end_idx = content.rfind("}")
            if start_idx != -1 and end_idx != -1:
                return json.loads(content[start_idx : end_idx + 1])
        except Exception as e:
            logger.error(f"Failed to parse Email Architect output: {e}")

        return {"sequence_title": "Custom Sequence", "steps": []}
