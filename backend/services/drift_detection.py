import logging
import math
from typing import Any, Dict, List, Optional

logger = logging.getLogger("raptorflow.services.drift_detection")


class DriftDetectionService:
    """
    SOTA Drift Detection Service (Native implementation).
    Implements a simplified Kolmogorov-Smirnov-like test to detect data drift without external math libraries.
    Following Osipov's MLOps patterns for industrial guardrails.
    """

    @staticmethod
    def calculate_p_value(baseline: List[float], current: List[float]) -> float:
        """
        Simplified KS-test logic using native Python.
        Calculates the maximum distance between cumulative distribution functions.
        """
        if not baseline or not current:
            return 1.0

        # 1. Sort both samples
        s1 = sorted(baseline)
        s2 = sorted(current)
        n1 = len(s1)
        n2 = len(s2)

        # 2. Compute the maximum distance (D-statistic)
        all_data = sorted(set(s1 + s2))
        d_max = 0.0

        idx1 = 0
        idx2 = 0

        for x in all_data:
            # Find proportion of s1 <= x
            while idx1 < n1 and s1[idx1] <= x:
                idx1 += 1
            cdf1 = idx1 / n1

            # Find proportion of s2 <= x
            while idx2 < n2 and s2[idx2] <= x:
                idx2 += 1
            cdf2 = idx2 / n2

            distance = abs(cdf1 - cdf2)
            if distance > d_max:
                d_max = distance

        # 3. Heuristic p-value for SOTA speed
        # Threshold: Adjusted for small sample sensitivity
        critical_value = 0.5 * math.sqrt((n1 + n2) / (n1 * n2))

        if d_max > critical_value:
            return 0.01  # Drift detected
        return 0.5  # No drift detected

    def detect_drift(
        self,
        baseline_metrics: Dict[str, List[float]],
        current_metrics: Dict[str, List[float]],
        threshold: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Detects drift across multiple metric categories.
        """
        results = {}
        overall_drift = False

        for metric_name, baseline_data in baseline_metrics.items():
            if metric_name in current_metrics:
                current_data = current_metrics[metric_name]
                p_value = self.calculate_p_value(baseline_data, current_data)

                is_drifting = p_value < threshold
                results[metric_name] = {"p_value": p_value, "is_drifting": is_drifting}
                if is_drifting:
                    overall_drift = True
                    logger.warning(
                        f"DRIFT DETECTED in metric '{metric_name}': p-value {p_value:.4f}"
                    )

        return {"is_drifting": overall_drift, "metrics": results}
