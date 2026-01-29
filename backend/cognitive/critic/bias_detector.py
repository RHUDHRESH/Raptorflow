"""
Bias Detector - Identifies and analyzes content bias

Detects various types of bias including gender, racial, political,
and other forms of bias in content.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from ...llm import LLMClient, ModelConfig
from ..models import BiasReport, BiasType, Severity

logger = logging.getLogger(__name__)


class BiasDetector:
    """Detects and analyzes bias in content."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()
        self.bias_patterns = self._load_bias_patterns()

    async def detect_bias(self, content: str) -> BiasReport:
        """
        Detect bias in content.

        Args:
            content: Content to analyze

        Returns:
            BiasReport with detected biases and analysis
        """
        try:
            detected_biases = []

            # Multiple bias detection methods
            bias_methods = [
                self._detect_gender_bias,
                self._detect_racial_bias,
                self._detect_political_bias,
                self._detect_age_bias,
                self._detect_cultural_bias,
                self._detect_economic_bias,
            ]

            for bias_method in bias_methods:
                try:
                    method_biases = await bias_method(content)
                    detected_biases.extend(method_biases)
                except Exception as e:
                    logger.warning(
                        f"Bias detection method {bias_method.__name__} failed: {e}"
                    )

            # Calculate overall bias score and severity
            overall_score = self._calculate_bias_score(detected_biases)
            severity = self._determine_bias_severity(overall_score)

            # Generate suggestions
            suggestions = self._generate_bias_suggestions(detected_biases)

            # Extract locations
            locations = list(
                set(
                    [
                        bias.get("location", "")
                        for bias in detected_biases
                        if bias.get("location")
                    ]
                )
            )

            return BiasReport(
                detected_biases=detected_biases,
                severity=severity,
                locations=locations,
                suggestions=suggestions,
                overall_bias_score=overall_score,
            )

        except Exception as e:
            logger.error(f"Bias detection failed: {e}")
            return BiasReport(
                detected_biases=[
                    {
                        "type": "system_error",
                        "description": f"Bias detection failed: {str(e)}",
                        "severity": "high",
                    }
                ],
                severity=Severity.HIGH,
                locations=[],
                suggestions=["Fix bias detection system"],
                overall_bias_score=0.0,
            )

    async def _detect_gender_bias(self, content: str) -> List[Dict[str, Any]]:
        """Detect gender bias in content."""
        try:
            model_config = ModelConfig(
                model="gemini-1.5-flash-lite", temperature=0.2, max_tokens=1000
            )

            prompt = f"""
Analyze this content for gender bias:

Content:
---
{content}
---

Look for:
- Gender stereotypes
- Unequal representation
- Gendered language assumptions
- Traditional role reinforcement
- Exclusionary language
- Gender-based value judgments

Respond in JSON:
{{
    "gender_biases": [
        {{
            "type": "gender",
            "description": "<specific_bias_description>",
            "severity": "<low|medium|high|critical>",
            "location": "<where_in_content>",
            "example": "<biased_text_example>",
            "suggestion": "<how_to_fix>"
        }}
    ]
}}
"""

            response = await self.llm.generate(prompt, model_config)
            data = json.loads(response.text)

            return data.get("gender_biases", [])

        except Exception as e:
            logger.error(f"Gender bias detection failed: {e}")
            return []

    async def _detect_racial_bias(self, content: str) -> List[Dict[str, Any]]:
        """Detect racial bias in content."""
        try:
            model_config = ModelConfig(
                model="gemini-1.5-flash-lite", temperature=0.2, max_tokens=1000
            )

            prompt = f"""
Analyze this content for racial bias:

Content:
---
{content}
---

Look for:
- Racial stereotypes
- Cultural assumptions
- Racial generalizations
- Exclusionary language
- Microaggressions
- Unequal representation

Respond in JSON:
{{
    "racial_biases": [
        {{
            "type": "racial",
            "description": "<specific_bias_description>",
            "severity": "<low|medium|high|critical>",
            "location": "<where_in_content>",
            "example": "<biased_text_example>",
            "suggestion": "<how_to_fix>"
        }}
    ]
}}
"""

            response = await self.llm.generate(prompt, model_config)
            data = json.loads(response.text)

            return data.get("racial_biases", [])

        except Exception as e:
            logger.error(f"Racial bias detection failed: {e}")
            return []

    async def _detect_political_bias(self, content: str) -> List[Dict[str, Any]]:
        """Detect political bias in content."""
        try:
            model_config = ModelConfig(
                model="gemini-1.5-flash-lite", temperature=0.2, max_tokens=1000
            )

            prompt = f"""
Analyze this content for political bias:

Content:
---
{content}
---

Look for:
- Political leaning bias
- Partisan language
- One-sided arguments
- Political stereotypes
- Exclusion of viewpoints
- Loaded political terms

Respond in JSON:
{{
    "political_biases": [
        {{
            "type": "political",
            "description": "<specific_bias_description>",
            "severity": "<low|medium|high|critical>",
            "location": "<where_in_content>",
            "example": "<biased_text_example>",
            "suggestion": "<how_to_fix>"
        }}
    ]
}}
"""

            response = await self.llm.generate(prompt, model_config)
            data = json.loads(response.text)

            return data.get("political_biases", [])

        except Exception as e:
            logger.error(f"Political bias detection failed: {e}")
            return []

    async def _detect_age_bias(self, content: str) -> List[Dict[str, Any]]:
        """Detect age bias in content."""
        try:
            model_config = ModelConfig(
                model="gemini-1.5-flash-lite", temperature=0.2, max_tokens=800
            )

            prompt = f"""
Analyze this content for age bias:

Content:
---
{content}
---

Look for:
- Age stereotypes
- Generational assumptions
- Age discrimination
- Exclusion of age groups
- Age-based value judgments
- Inappropriate age references

Respond in JSON:
{{
    "age_biases": [
        {{
            "type": "age",
            "description": "<specific_bias_description>",
            "severity": "<low|medium|high|critical>",
            "location": "<where_in_content>",
            "example": "<biased_text_example>",
            "suggestion": "<how_to_fix>"
        }}
    ]
}}
"""

            response = await self.llm.generate(prompt, model_config)
            data = json.loads(response.text)

            return data.get("age_biases", [])

        except Exception as e:
            logger.error(f"Age bias detection failed: {e}")
            return []

    async def _detect_cultural_bias(self, content: str) -> List[Dict[str, Any]]:
        """Detect cultural bias in content."""
        try:
            model_config = ModelConfig(
                model="gemini-1.5-flash-lite", temperature=0.2, max_tokens=800
            )

            prompt = f"""
Analyze this content for cultural bias:

Content:
---
{content}
---

Look for:
- Cultural assumptions
- Western-centric perspectives
- Cultural stereotypes
- Exclusion of cultural contexts
- Cultural insensitivity
- Ethnocentric language

Respond in JSON:
{{
    "cultural_biases": [
        {{
            "type": "cultural",
            "description": "<specific_bias_description>",
            "severity": "<low|medium|high|critical>",
            "location": "<where_in_content>",
            "example": "<biased_text_example>",
            "suggestion": "<how_to_fix>"
        }}
    ]
}}
"""

            response = await self.llm.generate(prompt, model_config)
            data = json.loads(response.text)

            return data.get("cultural_biases", [])

        except Exception as e:
            logger.error(f"Cultural bias detection failed: {e}")
            return []

    async def _detect_economic_bias(self, content: str) -> List[Dict[str, Any]]:
        """Detect economic bias in content."""
        try:
            model_config = ModelConfig(
                model="gemini-1.5-flash-lite", temperature=0.2, max_tokens=800
            )

            prompt = f"""
Analyze this content for economic bias:

Content:
---
{content}
---

Look for:
- Class assumptions
- Economic stereotypes
- Wealth bias
- Exclusion of economic realities
- Privilege blindness
- Economic value judgments

Respond in JSON:
{{
    "economic_biases": [
        {{
            "type": "economic",
            "description": "<specific_bias_description>",
            "severity": "<low|medium|high|critical>",
            "location": "<where_in_content>",
            "example": "<biased_text_example>",
            "suggestion": "<how_to_fix>"
        }}
    ]
}}
"""

            response = await self.llm.generate(prompt, model_config)
            data = json.loads(response.text)

            return data.get("economic_biases", [])

        except Exception as e:
            logger.error(f"Economic bias detection failed: {e}")
            return []

    def _calculate_bias_score(self, detected_biases: List[Dict[str, Any]]) -> float:
        """Calculate overall bias score."""
        if not detected_biases:
            return 0.0

        severity_weights = {"low": 0.1, "medium": 0.3, "high": 0.6, "critical": 1.0}

        total_score = 0.0
        for bias in detected_biases:
            severity = bias.get("severity", "low")
            weight = severity_weights.get(severity, 0.1)
            total_score += weight

        # Normalize to 0-1 scale
        max_possible = len(detected_biases) * 1.0
        return min(total_score / max_possible, 1.0) if max_possible > 0 else 0.0

    def _determine_bias_severity(self, bias_score: float) -> Severity:
        """Determine overall bias severity from score."""
        if bias_score >= 0.8:
            return Severity.CRITICAL
        elif bias_score >= 0.6:
            return Severity.HIGH
        elif bias_score >= 0.3:
            return Severity.MEDIUM
        else:
            return Severity.LOW

    def _generate_bias_suggestions(
        self, detected_biases: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate suggestions to address detected biases."""
        suggestions = set()

        for bias in detected_biases:
            suggestion = bias.get("suggestion")
            if suggestion:
                suggestions.add(suggestion)

        # Add general suggestions based on bias types
        bias_types = set([bias.get("type") for bias in detected_biases])

        if "gender" in bias_types:
            suggestions.add("Use gender-neutral language and avoid stereotypes")

        if "racial" in bias_types:
            suggestions.add("Ensure inclusive language and avoid racial assumptions")

        if "political" in bias_types:
            suggestions.add("Present balanced viewpoints and avoid partisan language")

        if "age" in bias_types:
            suggestions.add("Avoid age stereotypes and include all age groups")

        if "cultural" in bias_types:
            suggestions.add("Consider diverse cultural perspectives")

        if "economic" in bias_types:
            suggestions.add(
                "Be mindful of economic diversity and avoid class assumptions"
            )

        return list(suggestions)

    def _load_bias_patterns(self) -> Dict[str, List[str]]:
        """Load pattern-based bias detection rules."""
        return {
            "gender": [
                r"\b(men|women|guys|ladies|he|she|him|her)\b",
                r"\b(masculine|feminine|male|female)\b",
            ],
            "racial": [
                # Add racial bias patterns if needed
            ],
            "age": [
                r"\b(young|old|elderly|teenager|kid|senior)\b",
            ],
        }
