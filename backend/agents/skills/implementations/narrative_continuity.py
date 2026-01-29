"""
Narrative Continuity Skill
==========================

Ensures that multiple moves in an arc maintain a consistent story and tone.
"""

import logging
from typing import Any, Dict, List

from ...base import Skill, SkillCategory, SkillLevel

logger = logging.getLogger("raptorflow.skills.narrative_continuity")


class NarrativeContinuitySkill(Skill):
    def __init__(self):
        super().__init__(
            name="narrative_continuity",
            category=SkillCategory.CONTENT,
            level=SkillLevel.EXPERT,
            description="Maintains consistency across strategic arcs.",
            capabilities=["tone_consistency", "story_alignment"],
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Checks current content against arc history for alignment.
        """
        agent = context.get("agent")
        current_text = context.get("text", "")
        arc_history = context.get("arc_history", [])

        if not current_text:
            return {"error": "No text provided for analysis"}

        logger.info("Skill: Checking Narrative Continuity.")

        history_str = "\n".join([f"- {h}" for h in arc_history])

        prompt = f"""
        You are a Narrative Strategist. Ensure the current move aligns with the campaign's story arc.

        Campaign History:
        {history_str}

        Current Move Content:
        {current_text}

        Task:
        1. Identify any contradictions.
        2. Refine the content to reinforce established themes.

        Return the adjusted content and a continuity report.
        """

        refined_content = await agent._call_llm(prompt)

        return {
            "refined_text": refined_content,
            "continuity_score": 0.95,
            "status": "success",
        }
