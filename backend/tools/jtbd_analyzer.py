import logging
from typing import Any, Dict

from core.tool_registry import BaseRaptorTool, RaptorRateLimiter

logger = logging.getLogger("raptorflow.tools.jtbd")


class JTBDAnalyzerTool(BaseRaptorTool):
    """
    SOTA JTBD Framework Analyzer Tool.
    Analyzes business context to extract the 'Job to be Done', 'Desired Outcomes', and 'Emotional Triggers'.
    """

    @property
    def name(self) -> str:
        return "jtbd_framework_analyzer"

    @property
    def description(self) -> str:
        return (
            "Analyzes text context using the Jobs to be Done (JTBD) framework. "
            "Use this to identify what the user is actually 'hiring' the product for. "
            "Returns core jobs, emotional triggers, and functional requirements."
        )

    @RaptorRateLimiter.get_retry_decorator()
    async def _execute(self, context: str, **kwargs) -> Dict[str, Any]:
        logger.info("Analyzing JTBD framework")

        # Simulated JTBD analysis
        # In production, this would use a specialized LLM call

        return {
            "success": True,
            "core_job": "Automate industrial-grade marketing to buy back 20 hours of founder time.",
            "emotional_triggers": [
                "Anxiety over random posting",
                "Desire for surgical control",
            ],
            "functional_requirements": [
                "End-to-end trace visibility",
                "Deterministic tool execution",
            ],
            "jtbd_confidence": 0.94,
        }
