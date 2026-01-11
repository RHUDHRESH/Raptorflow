"""
Fact Checker - Validates factual accuracy

Checks claims against source material for accuracy.
"""

import asyncio
import logging
from typing import Dict, List, Optional

from ...llm import LLMClient, ModelConfig
from .models import FactCheckResult

logger = logging.getLogger(__name__)


class FactChecker:
    """Checks factual accuracy of content."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    async def check_facts(self, content: str, source_material: str) -> FactCheckResult:
        """
        Check factual accuracy against source material.

        Args:
            content: Content to fact-check
            source_material: Reference material for verification

        Returns:
            FactCheckResult with verification details
        """
        try:
            model_config = ModelConfig(
                model="gemini-1.5-pro", temperature=0.1, max_tokens=2000
            )

            prompt = self._build_fact_check_prompt(content, source_material)
            response = await self.llm.generate(prompt, model_config)

            return self._parse_fact_check_response(response.text)

        except Exception as e:
            logger.error(f"Fact checking failed: {e}")
            return FactCheckResult(
                verified_claims=[],
                unverified_claims=[f"Fact check failed: {str(e)}"],
                contradictions=[],
                confidence_score=0.0,
            )

    def _build_fact_check_prompt(self, content: str, source_material: str) -> str:
        """Build prompt for fact checking."""
        return f"""
Fact-check the following content against the provided source material.

Content to Check:
---
{content}
---

Source Material:
---
{source_material}
---

For each claim in the content, determine:
1. Is it verified by the source material?
2. Does it contradict the source material?
3. Is it not mentioned in the source material?

Respond in JSON format:
{{
    "verified_claims": [
        "<claim_that_is_supported_by_source>"
    ],
    "unverified_claims": [
        "<claim_not_found_in_source>"
    ],
    "contradictions": [
        "<claim_that_contradicts_source>"
    ],
    "confidence_score": <0.0_to_1.0_overall_confidence>
}}
"""

    def _parse_fact_check_response(self, response: str) -> FactCheckResult:
        """Parse LLM response into FactCheckResult."""
        try:
            import json

            start = response.find("{")
            end = response.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[start:end]
            data = json.loads(json_str)

            return FactCheckResult(
                verified_claims=data.get("verified_claims", []),
                unverified_claims=data.get("unverified_claims", []),
                contradictions=data.get("contradictions", []),
                confidence_score=data.get("confidence_score", 0.0),
            )

        except Exception as e:
            logger.error(f"Failed to parse fact check response: {e}")
            raise
