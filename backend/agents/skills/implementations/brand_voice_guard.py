"""
Brand Voice Guard Skill
=======================

Ensures all generated content adheres to the 'Expensive, Calm, and Decisive' brand persona.
"""

import logging
from typing import Dict, Any, List
from backend.agents.skills.base import Skill, SkillCategory, SkillLevel

logger = logging.getLogger("raptorflow.skills.brand_voice_guard")

class BrandVoiceGuardSkill(Skill):
    def __init__(self):
        super().__init__(
            name="brand_voice_guard",
            category=SkillCategory.CONTENT,
            level=SkillLevel.MASTER,
            description="Final pass to ensure editorial restraint and expensive tone.",
            capabilities=["tone_correction", "fluff_removal"]
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs a 'Restraint' pass on the text.
        """
        agent = context.get("agent")
        text = context.get("text", "")
        
        if not text:
            return {"error": "No text provided for guardrail pass"}
            
        logger.info("Skill: Running Brand Voice Guardrail.")
        
        prompt = f"""
        You are an Elite Editorial Director. Refine the following text to match our persona:
        
        Persona: 'Expensive, Calm, Decisive, Surgical'.
        Rules:
        - Remove ALL exclamation marks.
        - Remove generic adjectives (amazing, incredible, etc.).
        - Use short, powerful sentences.
        - Focus on results and clarity.
        
        Original Text:
        {text}
        
        Return the 'Purified Text'.
        """
        
        purified_text = await agent._call_llm(prompt)
        
        return {
            "purified_text": purified_text,
            "status": "success"
        }
