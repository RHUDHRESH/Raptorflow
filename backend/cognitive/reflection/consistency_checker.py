"""
Consistency Checker - Ensures content consistency

Checks for consistency with prior content and internal logic.
"""

import asyncio
import logging
from typing import Dict, List, Optional

from ...llm import LLMClient, ModelConfig
from ..models import ConsistencyResult, Issue, Severity

logger = logging.getLogger(__name__)


class ConsistencyChecker:
    """Checks content for consistency issues."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    async def check_consistency(
        self, content: str, prior_content: List[str]
    ) -> ConsistencyResult:
        """
        Check consistency with prior content.

        Args:
            content: Current content to check
            prior_content: List of prior content pieces

        Returns:
            ConsistencyResult with consistency analysis
        """
        try:
            model_config = ModelConfig(
                model="gemini-1.5-flash-lite", temperature=0.1, max_tokens=1500
            )

            prompt = self._build_consistency_prompt(content, prior_content)
            response = await self.llm.generate(prompt, model_config)

            return self._parse_consistency_response(response.text)

        except Exception as e:
            logger.error(f"Consistency check failed: {e}")
            return ConsistencyResult(
                consistent=False,
                inconsistencies=[Issue(Severity.HIGH, "consistency_error", str(e))],
                recommended_changes=["Retry consistency check after fixing error"],
            )

    def _build_consistency_prompt(self, content: str, prior_content: List[str]) -> str:
        """Build prompt for consistency checking."""
        prior_text = "\n\n---\n\n".join(prior_content)

        return f"""
Check if the following content is consistent with prior content.

Current Content:
---
{content}
---

Prior Content:
---
{prior_text}
---

Look for:
- Contradictory statements
- Changing terminology or definitions
- Inconsistent tone or voice
- Conflicting data or facts
- Timeline inconsistencies

Respond in JSON format:
{{
    "consistent": <boolean>,
    "inconsistencies": [
        {{
            "severity": "low|medium|high|critical",
            "dimension": "terminology|facts|tone|timeline|logic",
            "description": "<specific_inconsistency>",
            "location": "<where_in_current_content>",
            "suggestion": "<how_to_fix>"
        }}
    ],
    "recommended_changes": [
        "<specific_change_to_improve_consistency>"
    ]
}}
"""

    def _parse_consistency_response(self, response: str) -> ConsistencyResult:
        """Parse LLM response into ConsistencyResult."""
        try:
            import json

            start = response.find("{")
            end = response.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[start:end]
            data = json.loads(json_str)

            inconsistencies = []
            for inconsistency_data in data.get("inconsistencies", []):
                inconsistencies.append(
                    Issue(
                        severity=Severity(inconsistency_data["severity"]),
                        dimension=inconsistency_data["dimension"],
                        description=inconsistency_data["description"],
                        location=inconsistency_data.get("location"),
                        suggestion=inconsistency_data.get("suggestion"),
                    )
                )

            return ConsistencyResult(
                consistent=data["consistent"],
                inconsistencies=inconsistencies,
                recommended_changes=data.get("recommended_changes", []),
            )

        except Exception as e:
            logger.error(f"Failed to parse consistency response: {e}")
            raise
