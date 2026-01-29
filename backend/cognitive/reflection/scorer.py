"""
Quality Scorer - Evaluates output quality across multiple dimensions

Uses LLM to assess content quality based on predefined criteria.
"""

import asyncio
import logging
from typing import Dict, List, Optional

from ...llm import LLMClient, ModelConfig
from ..models import PerceivedInput
from ..models import Issue, QualityScore, Severity

logger = logging.getLogger(__name__)


class QualityScorer:
    """Evaluates output quality using LLM analysis."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()
        self.quality_threshold = 70

    async def score(self, output: str, criteria: List[str]) -> QualityScore:
        """
        Score output quality across multiple dimensions.

        Args:
            output: Content to evaluate
            criteria: List of quality criteria to assess

        Returns:
            QualityScore with detailed assessment
        """
        try:
            # Use FLASH_LITE for quick quality assessment
            model_config = ModelConfig(
                model="gemini-1.5-flash-lite",
                temperature=0.1,  # Low temperature for consistent scoring
                max_tokens=1000,
            )

            prompt = self._build_scoring_prompt(output, criteria)
            response = await self.llm.generate(prompt, model_config)

            return self._parse_score_response(response.text)

        except Exception as e:
            logger.error(f"Quality scoring failed: {e}")
            # Return minimal score on failure
            return QualityScore(
                overall=50,
                dimensions={"accuracy": 50, "relevance": 50, "coherence": 50},
                issues=[Issue(Severity.HIGH, "scoring_error", str(e))],
                passed=False,
            )

    def _build_scoring_prompt(self, output: str, criteria: List[str]) -> str:
        """Build prompt for quality scoring."""
        return f"""
Evaluate the following content quality across these dimensions: {', '.join(criteria)}

Rate each dimension 0-100 where:
- 90-100: Excellent
- 70-89: Good
- 50-69: Fair
- 0-49: Poor

Content to evaluate:
---
{output}
---

Respond in JSON format:
{{
    "dimensions": {{
        "accuracy": <score>,
        "relevance": <score>,
        "coherence": <score>,
        "completeness": <score>,
        "actionability": <score>,
        "clarity": <score>
    }},
    "overall": <weighted_average>,
    "issues": [
        {{
            "severity": "low|medium|high|critical",
            "dimension": "<dimension_name>",
            "description": "<issue_description>",
            "suggestion": "<how_to_fix>"
        }}
    ],
    "passed": <boolean_if_meets_threshold_70>
}}
"""

    def _parse_score_response(self, response: str) -> QualityScore:
        """Parse LLM response into QualityScore."""
        try:
            import json

            # Extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[start:end]
            data = json.loads(json_str)

            # Parse issues
            issues = []
            for issue_data in data.get("issues", []):
                issues.append(
                    Issue(
                        severity=Severity(issue_data["severity"]),
                        dimension=issue_data["dimension"],
                        description=issue_data["description"],
                        suggestion=issue_data.get("suggestion"),
                    )
                )

            return QualityScore(
                overall=data["overall"],
                dimensions=data["dimensions"],
                issues=issues,
                passed=data["passed"],
            )

        except Exception as e:
            logger.error(f"Failed to parse score response: {e}")
            raise
