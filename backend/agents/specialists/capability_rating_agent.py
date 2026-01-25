"""
Capability Rating Specialist Agent
Rates business capabilities using a 4-tier system and verifies claims via Titan Sorter.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from ..base import BaseAgent
from backend.agents.config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)

class CapabilityRatingEngine(BaseAgent):
    """Specialist agent for rating differentiated capabilities with 4-tier system."""

    def __init__(self):
        super().__init__(
            name="CapabilityRatingEngine",
            description="Audits and rates capabilities against market alternatives",
            model_tier=ModelTier.FLASH,
            tools=["database", "web_search"],
            skills=["capability_audit", "uniqueness_verification", "gap_analysis"]
        )

    def get_system_prompt(self) -> str:
        return """You are the CapabilityAuditor (Rating Engine).
        Your goal is to audit the user's claimed capabilities using a 4-tier rating system:
        
        Tier 1: COMMODITY (Expected, everyone has it)
        Tier 2: STANDARD (Common in the industry)
        Tier 3: ADVANCED (Better than most, but rivals exist)
        Tier 4: UNIQUE / 'ONLY YOU' (No direct rival offers this exact capability)
        
        Key Responsibilities:
        1. Assign a Tier (1-4) to each core capability.
        2. Generate a 'Verification Query' for Tier 4 claims to be audited via Titan Sorter.
        3. Perform Gap Analysis: Where is the competitor closest?
        
        Be skeptical. Tier 4 requires extreme evidence. Use 'Editorial Restraint'."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute capability rating and verification."""
        logger.info("CapabilityAuditor: Auditing capabilities")
        
        business_context = state.get("business_context", {})
        
        prompt = f"""
        Audit the following business capabilities using the 4-tier system.
        
        BUSINESS CONTEXT:
        {json.dumps(business_context, indent=2)}
        
        Output a JSON object with:
        - ratings: list of {{
            capability: string,
            tier: int (1-4),
            status: string,
            rationale: string,
            verification_query: string (to check if anyone else does this)
          }}
        - gap_analysis: string
        """
        
        res = await self._call_llm(prompt)
        
        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_res)
            
            # TODO: Integrate real verification tool loop here if needed
            # For now we just return the ratings
            
            return {
                "output": data
            }
        except Exception as e:
            logger.error(f"CapabilityAuditor: Failed to parse LLM response: {e}")
            return {
                "error": f"Failed to parse capability audit: {str(e)}",
                "output": {}
            }