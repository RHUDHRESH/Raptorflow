import logging
from typing import Any, Dict, Optional

from core.tool_registry import BaseRaptorTool, RaptorRateLimiter

logger = logging.getLogger("raptorflow.tools.style_guide")


class StyleGuideEnforcerTool(BaseRaptorTool):
    """
    SOTA Style Guide Enforcer Tool.
    Audits content for brand voice, 'Quiet Luxury' alignment, and narrative consistency.
    """

    @property
    def name(self) -> str:
        return "style_guide_enforcer"

    @property
    def description(self) -> str:
        return (
            "Audits content against the brand's style guide and 'Quiet Luxury' principles. "
            "Use this to ensure all messaging is calm, expensive, and decisive. "
            "Returns an alignment score and specific editorial corrections."
        )

    @RaptorRateLimiter.get_retry_decorator()
    async def _execute(
        self, content: str, brand_kit: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Dict[str, Any]:
        logger.info("Enforcing style guide alignment")

        # Simulated style guide enforcement
        violations = []
        if "!" in content:
            violations.append(
                "Excessive use of exclamation marks. Use periods for a calmer, more expensive tone."
            )

        hype_words = ["amazing", "revolutionary", "game-changing", "disrupt"]
        found_hype = [w for w in hype_words if w in content.lower()]
        if found_hype:
            violations.append(
                f"Found hype words: {found_hype}. Replace with surgical, data-backed claims."
            )

        score = 100 - (len(violations) * 15)

        return {
            "success": True,
            "alignment_score": max(0, score),
            "violations": violations,
            "editorial_decree": (
                "Simplify the prose. Remove adjectives. Let the results speak."
                if violations
                else "Perfectly restrained."
            ),
        }
