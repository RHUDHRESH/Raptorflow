import logging
import time
from typing import Any, Dict, List, Optional

from backend.inference import InferenceProvider
from backend.models.cognitive import ModelTier

logger = logging.getLogger("raptorflow.services.shadow_inference")


class ShadowInferenceService:
    """
    SOTA Shadow Inference Service.
    Runs 'Shadow' models in parallel with Production models to compare performance.
    Following Osipov's MLOps guardrail patterns.
    """

    def __init__(
        self,
        prod_tier: ModelTier = ModelTier.DRIVER,
        shadow_tier: ModelTier = ModelTier.SMART,
    ):
        self.prod_tier = prod_tier
        self.shadow_tier = shadow_tier

    async def run_comparison(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Runs inference on both Production and Shadow models.
        Returns both results and comparison metadata.
        """
        start_time = time.time()

        # 1. Production Run
        prod_llm = InferenceProvider.get_model(model_tier=self.prod_tier.value)
        prod_res = await prod_llm.ainvoke(prompt, **kwargs)
        prod_latency = time.time() - start_time

        # 2. Shadow Run (vNext)
        shadow_start = time.time()
        shadow_llm = InferenceProvider.get_model(model_tier=self.shadow_tier.value)
        shadow_res = await shadow_llm.ainvoke(prompt, **kwargs)
        shadow_latency = time.time() - shadow_start

        comparison = {
            "prompt": prompt,
            "production": {
                "tier": self.prod_tier.value,
                "content": prod_res.content,
                "latency": prod_latency,
            },
            "shadow": {
                "tier": self.shadow_tier.value,
                "content": shadow_res.content,
                "latency": shadow_latency,
            },
            "latency_delta": shadow_latency - prod_latency,
        }

        logger.info(
            f"Shadow Inference Complete. Latency Delta: {comparison['latency_delta']:.4f}s"
        )
        return comparison

    def log_comparison(self, comparison: Dict[str, Any]):
        """Logs comparison results for analytical review."""
        # In a real build, this would stream to BigQuery/Supabase
        logger.info(
            f"Comparison Logged: {comparison['production']['tier']} vs {comparison['shadow']['tier']}"
        )
