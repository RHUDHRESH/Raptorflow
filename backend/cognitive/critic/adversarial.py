"""
Adversarial Critic - Devil's advocate quality assessment

Performs thorough adversarial critique to find flaws, weaknesses,
and areas for improvement using devil's advocate methodology.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ...llm import LLMClient, ModelConfig
from .models import AdversarialCritique, Vulnerability

logger = logging.getLogger(__name__)


@dataclass
class AdversarialCritique:
    """Result of adversarial critique."""

    vulnerabilities: List[Vulnerability]
    severity_counts: Dict[str, int]
    recommendations: List[str]
    overall_assessment: str
    confidence_score: float


@dataclass
class Vulnerability:
    """Identified vulnerability or weakness."""

    category: str
    severity: str
    description: str
    location: Optional[str]
    impact: str
    mitigation: str


class AdversarialCritic:
    """Performs adversarial critique using devil's advocate approach."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    async def critique(self, output: str, goal: str) -> AdversarialCritique:
        """
        Perform adversarial critique of output.

        Args:
            output: Content to critique
            goal: Original goal/request

        Returns:
            AdversarialCritique with identified vulnerabilities
        """
        try:
            # Use PRO model for thorough adversarial analysis
            model_config = ModelConfig(
                model="gemini-1.5-pro",
                temperature=0.4,  # Higher temperature for creative critique
                max_tokens=3000,
            )

            prompt = self._build_adversarial_prompt(output, goal)
            response = await self.llm.generate(prompt, model_config)

            return self._parse_adversarial_response(response.text)

        except Exception as e:
            logger.error(f"Adversarial critique failed: {e}")
            return AdversarialCritique(
                vulnerabilities=[
                    Vulnerability(
                        category="system_error",
                        severity="high",
                        description=f"Critique failed: {str(e)}",
                        location=None,
                        impact="Unable to assess quality",
                        mitigation="Retry critique after fixing error",
                    )
                ],
                severity_counts={"high": 1},
                recommendations=["Fix critique system error"],
                overall_assessment="Critique system failure",
                confidence_score=0.0,
            )

    def _build_adversarial_prompt(self, output: str, goal: str) -> str:
        """Build prompt for adversarial critique."""
        return f"""
You are an adversarial critic. Your job is to find every possible flaw, weakness, and vulnerability in the following content. Be ruthless, thorough, and creative.

Adopt a devil's advocate mindset. Question assumptions, challenge claims, look for hidden problems, and imagine how this content could fail or be attacked.

Original Goal:
{goal}

Content to Critique:
---
{output}
---

Look for these types of vulnerabilities:
1. **Factual Issues**: Inaccuracies, outdated information, questionable claims
2. **Logical Flaws**: Weak reasoning, fallacies, contradictions, gaps
3. **Quality Problems**: Poor clarity, confusing language, bad structure
4. **User Experience**: Confusing instructions, missing steps, unclear outcomes
5. **Security Risks**: Sensitive information, dangerous advice, privacy issues
6. **Brand Damage**: Inappropriate tone, off-brand messaging, reputation risks
7. **Legal Issues**: Copyright problems, compliance violations, liability risks
8. **Technical Errors**: Incorrect procedures, bad advice, unsafe recommendations
9. **Accessibility**: Exclusionary language, inaccessible content
10. **Competitive Weakness**: How competitors could attack or outperform this

For each vulnerability found, provide:
- Category (from list above)
- Severity (low/medium/high/critical)
- Specific description
- Location (if applicable)
- Potential impact
- Mitigation strategy

Respond in JSON format:
{{
    "vulnerabilities": [
        {{
            "category": "<category>",
            "severity": "<severity>",
            "description": "<specific_issue>",
            "location": "<where_in_content>",
            "impact": "<potential_consequences>",
            "mitigation": "<how_to_fix>"
        }}
    ],
    "severity_counts": {{
        "low": <count>,
        "medium": <count>,
        "high": <count>,
        "critical": <count>
    }},
    "recommendations": [
        "<strategic_recommendation>",
        "<another_recommendation>"
    ],
    "overall_assessment": "<summary_of_content_quality_and_main_concerns>",
    "confidence_score": <0.0_to_1.0_how_confident_in_this_critique>
}}
"""

    def _parse_adversarial_response(self, response: str) -> AdversarialCritique:
        """Parse LLM response into AdversarialCritique."""
        try:
            # Extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[start:end]
            data = json.loads(json_str)

            # Parse vulnerabilities
            vulnerabilities = []
            for vuln_data in data.get("vulnerabilities", []):
                vulnerabilities.append(
                    Vulnerability(
                        category=vuln_data["category"],
                        severity=vuln_data["severity"],
                        description=vuln_data["description"],
                        location=vuln_data.get("location"),
                        impact=vuln_data["impact"],
                        mitigation=vuln_data["mitigation"],
                    )
                )

            return AdversarialCritique(
                vulnerabilities=vulnerabilities,
                severity_counts=data.get("severity_counts", {}),
                recommendations=data.get("recommendations", []),
                overall_assessment=data.get("overall_assessment", ""),
                confidence_score=data.get("confidence_score", 0.8),
            )

        except Exception as e:
            logger.error(f"Failed to parse adversarial response: {e}")
            raise

    async def get_attack_vectors(
        self, output: str, context: Dict[str, Any]
    ) -> List[str]:
        """
        Identify potential attack vectors against the content.

        Args:
            output: Content to analyze
            context: Additional context

        Returns:
            List of potential attack vectors
        """
        try:
            model_config = ModelConfig(
                model="gemini-1.5-pro", temperature=0.5, max_tokens=1500
            )

            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])

            prompt = f"""
Analyze the following content for potential attack vectors. How could competitors, critics, or malicious actors attack this content?

Context:
{context_str}

Content:
---
{output}
---

Identify specific attack vectors that could be used against this content:
1. Fact-checking attacks
2. Logic and reasoning attacks
3. Quality and professionalism attacks
4. Bias and discrimination attacks
5. Security and privacy attacks
6. Legal and compliance attacks
7. Competitive superiority attacks

Respond with a list of specific attack vectors:
{{
    "attack_vectors": [
        "<specific_attack_vector_description>",
        "<another_attack_vector>"
    ]
}}
"""

            response = await self.llm.generate(prompt, model_config)
            data = json.loads(response.text)

            return data.get("attack_vectors", [])

        except Exception as e:
            logger.error(f"Failed to identify attack vectors: {e}")
            return []

    async def stress_test_content(
        self, output: str, stress_scenarios: List[str]
    ) -> Dict[str, Any]:
        """
        Stress test content against various scenarios.

        Args:
            output: Content to test
            stress_scenarios: List of stress scenarios

        Returns:
            Stress test results
        """
        try:
            results = {}

            for scenario in stress_scenarios:
                model_config = ModelConfig(
                    model="gemini-1.5-flash-lite", temperature=0.3, max_tokens=800
                )

                prompt = f"""
Test how this content performs under stress scenario: {scenario}

Content:
---
{output}
---

Evaluate performance on:
- Robustness (does it break?)
- Clarity under pressure
- Accuracy under stress
- User experience impact
- Potential failures

Respond in JSON:
{{
    "scenario": "{scenario}",
    "performance_score": <0.0_to_1.0>,
    "weaknesses_found": ["<weakness>", "<another>"],
    "failure_points": ["<potential_failure>"],
    "recommendations": ["<improvement>"]
}}
"""

                response = await self.llm.generate(prompt, model_config)
                results[scenario] = json.loads(response.text)

            return results

        except Exception as e:
            logger.error(f"Failed to stress test content: {e}")
            return {}
