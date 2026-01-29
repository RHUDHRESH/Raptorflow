"""
Brand Audit Specialist Agent
Performs adversarial audit of brand claims against evidence via real AI inference
"""

import json
import logging
from typing import Any, Dict, List, Optional

from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)


class BrandAuditEngine(BaseAgent):
    """Adversarial agent that audits brand claims against evidence using real inference."""

    def __init__(self):
        super().__init__(
            name="BrandAuditEngine",
            description="Audits brand consistency and claims via real AI inference",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["brand_audit", "claim_verification", "adversarial_logic"],
        )

    def get_system_prompt(self) -> str:
        return """You are the BrandAuditEngine. Your job is to look for 'Brand Gaps'.
        Compare what the company claims (Truth Sheet) vs what the evidence actually shows.
        Identify inconsistencies in tone, value props, or market positioning.
        Be skeptical. Be surgical. If a claim is not backed by evidence, flag it."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute brand audit using real AI inference."""
        truth_sheet = state.get("step_data", {}).get("truth_sheet", {})
        extracted_facts = (
            state.get("step_data", {}).get("auto_extraction", {}).get("facts", [])
        )

        prompt = f"""Perform a surgical brand audit.

CLAIMS (Truth Sheet):
{json.dumps(truth_sheet, indent=2)}

EVIDENCE (Extracted Facts):
{json.dumps(extracted_facts, indent=2)}

Identify any 'Brand Gaps' where a claim is not supported by the evidence or is contradicted.
Return a JSON object:
{{
  "brand_gaps": [
    {{ "claim": "...", "evidence_gap": "...", "severity": "high/medium/low" }}
  ],
  "score": 0-100,
  "status": "ready/caution/danger",
  "summary": "Brief analysis"
}}"""

        res = await self._call_llm(prompt)
        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            audit_data = json.loads(clean_res)
            return {"output": audit_data}
        except:
            return {"output": {"error": "Failed to parse AI audit"}, "status": "error"}
