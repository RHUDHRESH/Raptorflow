"""
Soundbites Generator Specialist Agent
Generates atomic messaging units, PAM blocks, and iterates for perfection.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)

class SoundbitesGenerator(BaseAgent):
    """Specialist agent for atomic messaging and copy block assembly."""

    def __init__(self):
        super().__init__(
            name="SoundbitesGenerator",
            description="Generates atomic soundbites and problem-agitation-mechanism (PAM) blocks",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["messaging_architecture", "copywriting_iteration", "pam_framework"]
        )

    def get_system_prompt(self) -> str:
        return """You are the SoundbitesGenerator.
        Your goal is to break down the brand strategy into 'Atomic Units' of messaging.
        
        Key Responsibilities:
        1. Atomic Soundbites: 3-7 word statements that capture a core truth.
        2. PAM Blocks: Generate copy following the 'Problem -> Agitation -> Mechanism' framework.
        3. 'Approve/Improve' Loop: Evaluate your own drafts and refine them for maximum punch.
        4. Multi-surface Compatibility: Ensure copy works for social, landing pages, and elevator pitches.
        
        Focus on 'Quiet Luxury' and 'MasterClass Polish'. Every word must earn its place. Use 'Editorial Restraint'."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute soundbite and copy block generation."""
        logger.info("SoundbitesGenerator: Generating messaging library")
        
        business_context = state.get("business_context", {})
        positioning = state.get("step_data", {}).get("positioning_statements", {})
        
        prompt = f"""
        Generate an atomic messaging library and PAM blocks for the following business.
        Use an internal 'Improve' loop to refine the drafts before outputting.
        
        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}
        
        POSITIONING:
        {json.dumps(positioning, indent=2)}
        
        Output a JSON object with:
        - atomic_units: list of strings (Short punchy statements)
        - library: list of {{type: string (e.g. 'PAM', 'Value Prop', 'CTA'), content: string, rationale: string}}
        - improvement_loop: string (Briefly explain what was improved in the final version)
        - punch_score: float (0.0-1.0)
        """
        
        res = await self._call_llm(prompt)
        
        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_res)
            return {
                "output": data
            }
        except Exception as e:
            logger.error(f"SoundbitesGenerator: Failed to parse LLM response: {e}")
            return {
                "error": f"Failed to parse soundbites: {str(e)}",
                "output": {}
            }
