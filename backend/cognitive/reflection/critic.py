"""
Self Critic - Adversarial self-review for quality improvement

Performs adversarial critique to find flaws and areas for improvement.
"""

import asyncio
import logging
from typing import Dict, List, Optional

from ...llm import LLMClient, ModelConfig
from ..models import Critique, Issue, Severity

logger = logging.getLogger(__name__)


class SelfCritic:
    """Performs adversarial self-critique using LLM."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    async def critique(self, output: str, goal: str, context: Dict) -> Critique:
        """
        Perform adversarial critique of output.

        Args:
            output: Content to critique
            goal: Original goal/request
            context: Additional context for critique

        Returns:
            Critique with identified issues and recommendations
        """
        try:
            # Use PRO model for thorough critique
            model_config = ModelConfig(
                model="gemini-1.5-pro",
                temperature=0.3,  # Higher temperature for creative critique
                max_tokens=2000,
            )

            prompt = self._build_critique_prompt(output, goal, context)
            response = await self.llm.generate(prompt, model_config)

            return self._parse_critique_response(response.text)

        except Exception as e:
            logger.error(f"Self-critique failed: {e}")
            # Return minimal critique on failure
            return Critique(
                issues=[Issue(Severity.HIGH, "critique_error", str(e))],
                severity_counts={Severity.HIGH: 1},
                recommendations=["Retry critique after fixing error"],
                overall_assessment="Critique failed due to error",
            )

    def _build_critique_prompt(self, output: str, goal: str, context: Dict) -> str:
        """Build prompt for adversarial critique."""
        context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])

        return f"""
You are an adversarial critic. Your job is to find flaws, weaknesses, and areas for improvement in the following content.

Be thorough, critical, and specific. Look for:
- Factual errors or inaccuracies
- Logical fallacies or weak reasoning
- Missing important information
- Poor structure or clarity
- Brand voice inconsistencies
- Actionability issues
- Potential user confusion

Original Goal:
{goal}

Context:
{context_str}

Content to Critique:
---
{output}
---

Respond in JSON format:
{{
    "issues": [
        {{
            "severity": "low|medium|high|critical",
            "dimension": "<category_of_issue>",
            "description": "<specific_issue_description>",
            "location": "<where_in_content_if_applicable>",
            "suggestion": "<how_to_fix_this_issue>"
        }}
    ],
    "severity_counts": {{
        "low": <count>,
        "medium": <count>,
        "high": <count>,
        "critical": <count>
    }},
    "recommendations": [
        "<specific_recommendation_for_improvement>",
        "<another_recommendation>"
    ],
    "overall_assessment": "<summary_of_content_quality_and_main_concerns>"
}}
"""

    def _parse_critique_response(self, response: str) -> Critique:
        """Parse LLM response into Critique."""
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
                        location=issue_data.get("location"),
                        suggestion=issue_data.get("suggestion"),
                    )
                )

            # Parse severity counts
            severity_counts = {}
            for severity, count in data.get("severity_counts", {}).items():
                severity_counts[Severity(severity)] = count

            return Critique(
                issues=issues,
                severity_counts=severity_counts,
                recommendations=data.get("recommendations", []),
                overall_assessment=data.get("overall_assessment", ""),
            )

        except Exception as e:
            logger.error(f"Failed to parse critique response: {e}")
            raise
