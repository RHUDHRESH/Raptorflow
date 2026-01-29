"""
Brand Checker - Ensures brand compliance

Validates content against brand voice and guardrails.
"""

import asyncio
import logging
from typing import Dict, List, Optional

from ...llm import LLMClient, ModelConfig
from ..models import BrandCheckResult, Issue, Severity

logger = logging.getLogger(__name__)


class BrandChecker:
    """Checks content for brand compliance."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    async def check_brand_compliance(
        self, content: str, brand_voice: str, guardrails: List[str]
    ) -> BrandCheckResult:
        """
        Check if content complies with brand guidelines.

        Args:
            content: Content to check
            brand_voice: Brand voice description
            guardrails: List of brand guardrails

        Returns:
            BrandCheckResult with compliance details
        """
        try:
            model_config = ModelConfig(
                model="gemini-1.5-flash-lite", temperature=0.1, max_tokens=1000
            )

            prompt = self._build_brand_check_prompt(content, brand_voice, guardrails)
            response = await self.llm.generate(prompt, model_config)

            return self._parse_brand_check_response(response.text)

        except Exception as e:
            logger.error(f"Brand check failed: {e}")
            return BrandCheckResult(
                compliant=False,
                violations=[Issue(Severity.HIGH, "brand_check_error", str(e))],
                suggestions=["Retry brand check after fixing error"],
            )

    def _build_brand_check_prompt(
        self, content: str, brand_voice: str, guardrails: List[str]
    ) -> str:
        """Build prompt for brand compliance check."""
        guardrails_text = "\n".join([f"- {rail}" for rail in guardrails])

        return f"""
Check if the following content complies with brand guidelines.

Brand Voice:
{brand_voice}

Brand Guardrails:
{guardrails_text}

Content to Check:
---
{content}
---

Respond in JSON format:
{{
    "compliant": <boolean>,
    "violations": [
        {{
            "severity": "low|medium|high|critical",
            "dimension": "brand_voice|guardrails|tone|terminology",
            "description": "<specific_violation>",
            "location": "<where_in_content>",
            "suggestion": "<how_to_fix>"
        }}
    ],
    "suggestions": [
        "<general_improvement_suggestion>"
    ]
}}
"""

    def _parse_brand_check_response(self, response: str) -> BrandCheckResult:
        """Parse LLM response into BrandCheckResult."""
        try:
            import json

            start = response.find("{")
            end = response.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[start:end]
            data = json.loads(json_str)

            violations = []
            for violation_data in data.get("violations", []):
                violations.append(
                    Issue(
                        severity=Severity(violation_data["severity"]),
                        dimension=violation_data["dimension"],
                        description=violation_data["description"],
                        location=violation_data.get("location"),
                        suggestion=violation_data.get("suggestion"),
                    )
                )

            return BrandCheckResult(
                compliant=data["compliant"],
                violations=violations,
                suggestions=data.get("suggestions", []),
            )

        except Exception as e:
            logger.error(f"Failed to parse brand check response: {e}")
            raise
