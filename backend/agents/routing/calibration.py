"""
Routing confidence calibration and validation.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .hlk import HLKRouter
from .intent import IntentRouter
from .semantic import SemanticRouter

logger = logging.getLogger(__name__)


@dataclass
class CalibrationData:
    """Calibration data for routing confidence."""

    expected_route: str
    actual_route: str
    semantic_confidence: float
    hlk_confidence: float
    intent_confidence: float
    correct: bool


class RoutingCalibrator:
    """Calibrates routing confidence thresholds based on empirical data."""

    def __init__(self):
        self.calibration_history: List[CalibrationData] = []
        self.optimized_thresholds = {
            "semantic_high": 0.75,  # Threshold for semantic-only routing
            "hlk_trust": 0.6,  # Threshold for trusting HLK over semantic
            "semantic_trust": 0.5,  # Threshold for trusting semantic over intent
            "intent_trust": 0.4,  # Base confidence for intent routing
        }

    def add_calibration_data(self, data: CalibrationData):
        """Add calibration data point."""
        self.calibration_history.append(data)

        # Re-optimize thresholds every 100 data points
        if len(self.calibration_history) % 100 == 0:
            self.optimize_thresholds()

    def optimize_thresholds(self):
        """Optimize thresholds based on calibration history."""
        if len(self.calibration_history) < 50:
            logger.warning("Insufficient calibration data for optimization")
            return

        # Calculate optimal thresholds using grid search
        best_thresholds = self._grid_search_optimization()

        if best_thresholds:
            self.optimized_thresholds = best_thresholds
            logger.info(f"Optimized thresholds: {best_thresholds}")

    def _grid_search_optimization(self) -> Dict[str, float]:
        """Grid search for optimal thresholds."""
        best_accuracy = 0.0
        best_thresholds = None

        # Define search space
        semantic_range = [0.6, 0.65, 0.7, 0.75, 0.8, 0.85]
        hlk_range = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75]
        semantic_trust_range = [0.4, 0.45, 0.5, 0.55, 0.6, 0.65]
        intent_trust_range = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55]

        # Grid search (sample to avoid combinatorial explosion)
        for s_high in semantic_range:
            for hlk in hlk_range:
                for s_trust in semantic_trust_range:
                    for i_trust in intent_trust_range:
                        thresholds = {
                            "semantic_high": s_high,
                            "hlk_trust": hlk,
                            "semantic_trust": s_trust,
                            "intent_trust": i_trust,
                        }

                        accuracy = self._evaluate_thresholds(thresholds)

                        if accuracy > best_accuracy:
                            best_accuracy = accuracy
                            best_thresholds = thresholds

        logger.info(f"Best accuracy: {best_accuracy:.3f}")
        return best_thresholds

    def _evaluate_thresholds(self, thresholds: Dict[str, float]) -> float:
        """Evaluate thresholds against calibration data."""
        correct = 0
        total = len(self.calibration_history)

        for data in self.calibration_history:
            predicted_route = self._predict_route(data, thresholds)
            if predicted_route == data.expected_route:
                correct += 1

        return correct / total if total > 0 else 0.0

    def _predict_route(
        self, data: CalibrationData, thresholds: Dict[str, float]
    ) -> str:
        """Predict route using given thresholds."""
        # Simulate routing decision logic
        if data.semantic_confidence >= thresholds["semantic_high"]:
            # Semantic-only routing
            route_map = {
                "onboarding": "OnboardingOrchestrator",
                "moves": "MoveStrategist",
                "muse": "ContentCreator",
                "blackbox": "BlackBoxStrategist",
                "research": "MarketResearchAgent",
                "analytics": "AnalyticsAgent",
                "general": "GeneralAgent",
            }
            return route_map.get(data.actual_route, "GeneralAgent")

        elif data.hlk_confidence >= thresholds["hlk_trust"]:
            return data.actual_route

        elif data.semantic_confidence >= thresholds["semantic_trust"]:
            return data.actual_route

        elif data.intent_confidence >= thresholds["intent_trust"]:
            return data.actual_route

        else:
            return "GeneralAgent"

    def get_optimized_thresholds(self) -> Dict[str, float]:
        """Get current optimized thresholds."""
        return self.optimized_thresholds.copy()

    def get_calibration_stats(self) -> Dict[str, any]:
        """Get calibration statistics."""
        if not self.calibration_history:
            return {"message": "No calibration data available"}

        total = len(self.calibration_history)
        correct = sum(1 for data in self.calibration_history if data.correct)
        accuracy = correct / total

        # Average confidences by router
        semantic_avg = (
            sum(data.semantic_confidence for data in self.calibration_history) / total
        )
        hlk_avg = sum(data.hlk_confidence for data in self.calibration_history) / total
        intent_avg = (
            sum(data.intent_confidence for data in self.calibration_history) / total
        )

        return {
            "total_samples": total,
            "accuracy": accuracy,
            "current_thresholds": self.optimized_thresholds,
            "average_confidences": {
                "semantic": semantic_avg,
                "hlk": hlk_avg,
                "intent": intent_avg,
            },
        }
