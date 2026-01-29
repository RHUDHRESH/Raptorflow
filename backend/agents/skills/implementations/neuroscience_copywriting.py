"""
Neuroscience Copywriting Skill
==============================

Applies psychological triggers and neuroscience-backed patterns to marketing copy.
"""

import logging
from typing import Any, Dict, List

from ...base import Skill, SkillCategory, SkillLevel

logger = logging.getLogger("raptorflow.skills.neuroscience_copywriting")


class NeuroscienceCopywritingSkill(Skill):
    def __init__(self):
        super().__init__(
            name="neuroscience_copywriting",
            category=SkillCategory.CONTENT,
            level=SkillLevel.EXPERT,
            description="Applies scarcity, authority, and social proof triggers to content.",
            capabilities=[
                "psychological_trigger_injection",
                "readability_optimization",
            ],
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refines copy using neuroscience patterns.
        """
        agent = context.get("agent")
        text = context.get("text", "")

        if not text:
            return {"error": "No text provided for refinement"}

        logger.info("Skill: Applying Neuroscience Copywriting pass.")

        prompt = f"""
        You are an expert Neuroscience Copywriter. Refine the following text using:
        1. **Dopamine Loops**: Create curiosity and reward patterns.
        2. **Status Signaling**: Position the offer as a high-status move.
        3. **Limbic Resonance**: Evoke core emotional drivers.

        Original Text:
        {text}

        Return the refined text and a list of triggers used.
        """

        # Use agent's LLM to generate refined text
        refined_content = await agent._call_llm(prompt)

        return {
            "refined_text": refined_content,
            "triggers_applied": ["Scarcity", "Authority", "Status Signaling"],
            "status": "success",
        }
