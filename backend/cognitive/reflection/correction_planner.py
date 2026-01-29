"""
Correction Planner - Plans corrections based on critique

Analyzes critique and creates prioritized correction plan.
"""

import asyncio
import logging
from typing import Dict, List, Optional

from ...llm import LLMClient, ModelConfig
from ..models import Correction, Critique, Severity

logger = logging.getLogger(__name__)


class CorrectionPlanner:
    """Plans corrections based on critique analysis."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    async def plan_corrections(self, critique: Critique) -> List[Correction]:
        """
        Plan corrections based on critique.

        Args:
            critique: Critique with identified issues

        Returns:
            List of prioritized corrections
        """
        try:
            # Use FLASH_LITE for quick correction planning
            model_config = ModelConfig(
                model="gemini-1.5-flash-lite", temperature=0.2, max_tokens=1500
            )

            prompt = self._build_correction_prompt(critique)
            response = await self.llm.generate(prompt, model_config)

            return self._parse_correction_response(response.text)

        except Exception as e:
            logger.error(f"Correction planning failed: {e}")
            return [
                Correction(
                    target="error_recovery",
                    action="retry_critique",
                    expected_improvement="Fix planning error and retry",
                )
            ]

    def _build_correction_prompt(self, critique: Critique) -> str:
        """Build prompt for correction planning."""
        issues_text = "\n".join(
            [
                f"- {issue.severity}: {issue.description} (Suggestion: {issue.suggestion})"
                for issue in critique.issues
            ]
        )

        return f"""
Based on the following critique, plan specific corrections to improve the content.

Critique Issues:
{issues_text}

Recommendations:
{chr(10).join(f"- {rec}" for rec in critique.recommendations)}

Plan corrections in order of priority (critical first, then high, medium, low).
For each correction, specify:
1. What needs to be corrected (target)
2. How to correct it (action)
3. What improvement is expected

Respond in JSON format:
{{
    "corrections": [
        {{
            "target": "<specific_element_to_correct>",
            "action": "<specific_action_to_take>",
            "expected_improvement": "<what_this_should_achieve>"
        }}
    ]
}}
"""

    def _parse_correction_response(self, response: str) -> List[Correction]:
        """Parse LLM response into corrections list."""
        try:
            import json

            # Extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[start:end]
            data = json.loads(json_str)

            corrections = []
            for correction_data in data.get("corrections", []):
                corrections.append(
                    Correction(
                        target=correction_data["target"],
                        action=correction_data["action"],
                        expected_improvement=correction_data["expected_improvement"],
                    )
                )

            return corrections

        except Exception as e:
            logger.error(f"Failed to parse correction response: {e}")
            raise
