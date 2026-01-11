"""
Improvement Executor - Applies corrections to content

Executes planned corrections to improve content quality.
"""

import asyncio
import logging
from typing import Dict, List, Optional

from ...llm import LLMClient, ModelConfig
from .models import Correction, QualityScore

logger = logging.getLogger(__name__)


class ImprovementExecutor:
    """Executes corrections to improve content."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()

    async def execute_corrections(
        self, output: str, corrections: List[Correction]
    ) -> str:
        """
        Apply corrections to improve content.

        Args:
            output: Original content
            corrections: List of corrections to apply

        Returns:
            Improved content
        """
        try:
            if not corrections:
                return output

            # Use PRO model for high-quality improvements
            model_config = ModelConfig(
                model="gemini-1.5-pro", temperature=0.3, max_tokens=3000
            )

            prompt = self._build_execution_prompt(output, corrections)
            response = await self.llm.generate(prompt, model_config)

            return self._extract_improved_content(response.text)

        except Exception as e:
            logger.error(f"Correction execution failed: {e}")
            return output  # Return original on failure

    def _build_execution_prompt(
        self, output: str, corrections: List[Correction]
    ) -> str:
        """Build prompt for applying corrections."""
        corrections_text = "\n".join(
            [
                f"{i+1}. Target: {c.target}\n   Action: {c.action}\n   Expected: {c.expected_improvement}"
                for i, c in enumerate(corrections)
            ]
        )

        return f"""
Apply the following corrections to improve the content:

Corrections to Apply:
{corrections_text}

Original Content:
---
{output}
---

Apply the corrections systematically. Focus on:
1. Fixing critical issues first
2. Maintaining the original intent and voice
3. Ensuring the result is coherent and well-structured
4. Preserving any correct parts of the original

Return only the improved content without explanations or metadata.
"""

    def _extract_improved_content(self, response: str) -> str:
        """Extract improved content from LLM response."""
        # Remove any markdown formatting or explanations
        lines = response.strip().split("\n")

        # Skip common preamble lines
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith(
                ("Here is", "Improved content:", "The improved", "After applying")
            ):
                start_idx = i
                break

        # Get the actual content
        content_lines = lines[start_idx:]

        # Remove any trailing explanations
        end_idx = len(content_lines)
        for i in range(len(content_lines) - 1, -1, -1):
            line = content_lines[i].strip()
            if line and not line.startswith(
                ("Note:", "Explanation:", "Summary:", "The improvements")
            ):
                end_idx = i + 1
                break

        improved_content = "\n".join(content_lines[:end_idx])

        # Clean up any markdown markers
        improved_content = improved_content.strip()
        if improved_content.startswith("```"):
            improved_content = improved_content.split("\n", 1)[1]
        if improved_content.endswith("```"):
            improved_content = improved_content.rsplit("\n", 1)[0]

        return improved_content.strip()
