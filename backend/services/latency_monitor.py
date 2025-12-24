import logging
from typing import List

from backend.memory.short_term import L1ShortTermMemory

logger = logging.getLogger("raptorflow.services.latency_monitor")


class LatencyMonitor:
    """
    SOTA Inference Latency Monitor.
    Tracks rolling window of inference latencies and triggers alerts on P95 spikes.
    Uses Osipov's guardrail pattern for system stability.
    """

    def __init__(self, threshold_ms: float = 2000.0, window_size: int = 50):
        self.threshold_ms = threshold_ms
        self.window_size = window_size
        self._memory = None

    @property
    def memory(self) -> L1ShortTermMemory:
        if self._memory is None:
            self._memory = L1ShortTermMemory()
        return self._memory

    def _calculate_p95(self, latencies: List[float]) -> float:
        """Calculates P95 using simple sorting (No numpy for stability)."""
        if not latencies:
            return 0.0
        sorted_lats = sorted(latencies)
        idx = int(0.95 * len(sorted_lats))
        return sorted_lats[min(idx, len(sorted_lats) - 1)]

    async def record_and_check(self, workspace_id: str, latency_ms: float) -> bool:
        """Records a new latency and checks if P95 exceeds threshold."""
        key = f"latencies:{workspace_id}"

        try:
            # 1. Retrieve existing latencies
            latencies = await self.memory.retrieve(key) or []

            # 2. Append new latency and maintain window size
            latencies.append(latency_ms)
            latencies = latencies[-self.window_size :]

            # 3. Store back to L1
            await self.memory.store(key, latencies, ttl=3600)  # 1h TTL

            # 4. Calculate P95 if we have enough data
            if len(latencies) >= 5:
                p95 = self._calculate_p95(latencies)
                if p95 > self.threshold_ms:
                    logger.warning(
                        f"LATENCY ALERT: P95 latency ({p95:.2f}ms) exceeds threshold ({self.threshold_ms}ms) "
                        f"for workspace {workspace_id}"
                    )
                    return True

            return False
        except Exception as e:
            logger.error(f"Latency monitoring failed: {e}")
            return False
