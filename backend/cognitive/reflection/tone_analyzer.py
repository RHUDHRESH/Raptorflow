"""
Tone Analyzer - Analyzes and matches content tone

Evaluates content tone against target tone requirements.
"""

import asyncio
import logging
from typing import Dict, List, Optional

from ...llm import LLMClient, ModelConfig
from .models import ToneAnalysisResult

logger = logging.getLogger(__name__)


class ToneAnalyzer:
    """Analyzes content tone and matches against target."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    async def analyze_tone(self, content: str, target_tone: str) -> ToneAnalysisResult:
        """
        Analyze content tone against target.

        Args:
            content: Content to analyze
            target_tone: Desired tone description

        Returns:
            ToneAnalysisResult with tone matching details
        """
        try:
            model_config = ModelConfig(
                model="gemini-1.5-flash-lite", temperature=0.1, max_tokens=1000
            )

            prompt = self._build_tone_analysis_prompt(content, target_tone)
            response = await self.llm.generate(prompt, model_config)

            return self._parse_tone_analysis_response(response.text)

        except Exception as e:
            logger.error(f"Tone analysis failed: {e}")
            return ToneAnalysisResult(
                detected_tone="unknown",
                matches_target=False,
                adjustments_needed=["Retry tone analysis after fixing error"],
            )

    def _build_tone_analysis_prompt(self, content: str, target_tone: str) -> str:
        """Build prompt for tone analysis."""
        return f"""
Analyze the tone of the following content and compare it to the target tone.

Target Tone:
{target_tone}

Content to Analyze:
---
{content}
---

Common tones: professional, casual, formal, friendly, authoritative, conversational,
empathetic, technical, creative, persuasive, neutral, urgent, reassuring

Respond in JSON format:
{{
    "detected_tone": "<primary_tone_detected>",
    "matches_target": <boolean>,
    "adjustments_needed": [
        "<specific_adjustment_to_match_target_tone>"
    ]
}}
"""

    def _parse_tone_analysis_response(self, response: str) -> ToneAnalysisResult:
        """Parse LLM response into ToneAnalysisResult."""
        try:
            import json

            start = response.find("{")
            end = response.rfind("}") + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[start:end]
            data = json.loads(json_str)

            return ToneAnalysisResult(
                detected_tone=data.get("detected_tone", "unknown"),
                matches_target=data.get("matches_target", False),
                adjustments_needed=data.get("adjustments_needed", []),
            )

        except Exception as e:
            logger.error(f"Failed to parse tone analysis response: {e}")
            raise
