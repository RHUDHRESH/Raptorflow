import logging
from typing import Dict, Any, Optional
from backend.services.matrix_service import MatrixService

logger = logging.getLogger("raptorflow.services.circuit_breaker")

class KillSwitchCircuitBreaker:
    """
    SOTA Kill-Switch Circuit Breaker.
    Automatically engages the global system halt when critical metrics (Drift, Budget, Latency)
    violate safety thresholds. Implements Osipov's fail-safe engineering patterns.
    """

    def __init__(self, drift_threshold: float = 0.1):
        self.drift_threshold = drift_threshold
        self.matrix = MatrixService()

    async def check_and_trip(
        self, 
        workspace_id: str, 
        drift_score: Optional[float] = None,
        is_over_budget: bool = False,
        reason: str = "Unspecified failure"
    ) -> bool:
        """Checks metrics and trips the global kill-switch if necessary."""
        trip_needed = False
        trip_reason = reason

        # 1. Check Drift (Osipov pattern: >10% is critical)
        if drift_score is not None and drift_score > self.drift_threshold:
            trip_needed = True
            trip_reason = f"Critical Drift Detected: {drift_score:.2f} > {self.drift_threshold}"
            
        # 2. Check Budget
        if is_over_budget:
            trip_needed = True
            trip_reason = "Critical Budget Overflow Detected"

        if trip_needed:
            logger.critical(f"CIRCUIT BREAKER TRIPPED for {workspace_id}: {trip_reason}")
            success = await self.matrix.halt_system()
            return success
            
        return False
