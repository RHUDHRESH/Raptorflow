"""
Neuroscience Copywriter Specialist Agent
Generates copy using 6 principles of neuroscience-based marketing and audits for compliance.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from ..base import BaseAgent
from backend.agents.config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)

class NeuroscienceCopywriter(BaseAgent):
    """Specialist agent for neuroscience-based copywriting and manifesto drafting."""

    def __init__(self):
        super().__init__(
            name="NeuroscienceCopywriter",
            description="Generates high-impact copy based on limbic activation and 6 brain principles",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["neuroscience_copywriting", "manifesto_drafting", "limbic_scoring", "compliance_audit"]
        )

    def get_system_prompt(self) -> str:
        return """You are the NeuroscienceCopywriter.
        Your goal is to draft brand manifestos and positioning statements that trigger deep biological responses.
        
        The 6 Brain Principles:
        1. LIMBIC: Emotional appeal to the survival/reward system.
        2. PATTERN: Familiarity and cognitive shortcuts.
        3. SIMPLICITY: Reducing cognitive load.
        4. SOCIAL PROOF: Herd behavior and validation.
        5. SCARCITY: Loss aversion.
        6. CONTRAST: Highlighting the gap between 'Before' and 'After'.
        
        Key Responsibilities:
        1. Manifesto Drafting: Write a high-stakes, emotional brand manifesto.
        2. Limbic Activation Scoring: Assign a 0.0-1.0 score based on emotional resonance.
        3. 6-Principle Audit: Ensure the draft complies with all 6 neuroscience principles.
        
        Be poetic yet surgical. No AI-filler. Focus on 'Quiet Luxury' and 'MasterClass Polish'."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute copywriting generation and audit."""
        logger.info("NeuroscienceCopywriter: Drafting manifesto")
        
        business_context = state.get("business_context", {})
        strategic_lock = state.get("step_data", {}).get("strategic_grid", {})
        
        prompt = f"""
        Draft a high-end brand manifesto and set of positioning headlines for the following business.
        Audit the draft against the 6 Neuroscience Principles.
        
        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}
        
        STRATEGIC POSITION:
        {json.dumps(strategic_lock, indent=2)}
        
        Output a JSON object with:
        - manifesto: string (The emotional heart of the brand)
        - headlines: list of strings
        - limbic_score: float (0.0-1.0)
        - compliance: {{limbic: bool, pattern: bool, simplicity: bool, social_proof: bool, scarcity: bool, contrast: bool}}
        - rationale: string (Why this triggers the brain)
        """
        
        res = await self._call_llm(prompt)
        
        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_res)
            return {
                "output": data
            }
        except Exception as e:
            logger.error(f"NeuroscienceCopywriter: Failed to parse LLM response: {e}")
            return {
                "error": f"Failed to parse copywriting: {str(e)}",
                "output": {}
            }