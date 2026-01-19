"""
Conflict Resolver executable skill.
"""

import logging
import json
from typing import Any, Dict, List

from ..base import Skill, SkillCategory, SkillLevel

logger = logging.getLogger(__name__)

class ConflictResolverSkill(Skill):
    """Skill for identifying and resolving conflicts between concurrent moves."""

    def __init__(self):
        super().__init__(
            name="conflict_resolver",
            category=SkillCategory.STRATEGY,
            level=SkillLevel.EXPERT,
            description="Identify and resolve overlaps or contradictions in marketing moves.",
            capabilities=[
                "Offer overlap detection",
                "Message contradiction identification",
                "Audience fatigue analysis"
            ]
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute conflict resolution.
        """
        agent = context.get("agent")
        moves = context.get("moves", [])
        
        if not agent:
            raise ValueError("Agent is required for conflict resolution")

        system_prompt = "You are a Strategic Conflict Resolver. Analyze concurrent moves for the same workspace."
        prompt = f"Analyze these concurrent moves for the same workspace:\n{json.dumps(moves)}"
        
        try:
            result = await agent._call_llm(prompt, system_prompt=system_prompt)
            return {"conflicts_report": result}
        except Exception as e:
            logger.error(f"Conflict resolution failed: {e}")
            return {"error": str(e), "conflicts": []}

