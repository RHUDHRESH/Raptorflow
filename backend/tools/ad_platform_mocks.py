import logging
import random
from typing import Any, Dict

from core.tool_registry import BaseRaptorTool, RaptorRateLimiter

logger = logging.getLogger("raptorflow.tools.ad_mocks")


class AdPlatformMockTool(BaseRaptorTool):
    """
    SOTA Ad Platform Mock Tool.
    Simulates cross-platform (Meta, Google, LinkedIn) ad performance for strategy testing.
    """

    @property
    def name(self) -> str:
        return "ad_platform_mocks"

    @property
    def description(self) -> str:
        return (
            "Simulates ad performance across major platforms (Meta, Google, LinkedIn). "
            "Use this to test media buying strategies and predict outcomes without live spend. "
            "Returns simulated CTR, CPC, and conversion data based on industry benchmarks."
        )

    @RaptorRateLimiter.get_retry_decorator()
    async def _execute(
        self, platform: str, niche: str = "saas", **kwargs
    ) -> Dict[str, Any]:
        logger.info(f"Simulating {platform} performance for niche: {niche}")

        # SOTA Benchmarks (Industrial averages)
        benchmarks = {
            "meta": {"ctr": 0.012, "cpc": 1.85, "conv": 0.035},
            "google": {"ctr": 0.045, "cpc": 3.40, "conv": 0.042},
            "linkedin": {"ctr": 0.008, "cpc": 8.50, "conv": 0.061},
        }

        base = benchmarks.get(platform.lower(), benchmarks["meta"])

        # Add slight variance for realism
        variance = 1 + (random.random() - 0.5) * 0.2

        return {
            "success": True,
            "platform": platform,
            "niche": niche,
            "simulated_metrics": {
                "ctr": round(base["ctr"] * variance, 4),
                "cpc": round(base["cpc"] / variance, 2),
                "conversion_rate": round(base["conv"] * variance, 4),
            },
            "confidence": 0.85,
        }
