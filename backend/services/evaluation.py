import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("raptorflow.services.evaluation")


class OutputEvaluator:
    """
    Scores generated outputs based on outcome evidence and confidence.
    """

    def __init__(
        self, high_confidence_threshold: float = 0.8, l3_threshold: float = 0.92
    ):
        self.high_confidence_threshold = high_confidence_threshold
        self.l3_threshold = l3_threshold

    def evaluate_output(
        self,
        output: str,
        outcomes: Optional[List[Dict[str, Any]]] = None,
        confidence: Optional[float] = None,
    ) -> Dict[str, Any]:
        outcomes = outcomes or []
        base_confidence = confidence if confidence is not None else 0.5

        outcome_value = sum(float(o.get("value", 0) or 0.0) for o in outcomes)
        outcome_confidence = (
            sum(float(o.get("confidence", 1.0)) for o in outcomes) / len(outcomes)
            if outcomes
            else 0.0
        )

        evidence_score = min(
            1.0,
            0.35
            + (0.1 * min(len(outcomes), 5))
            + (0.35 * min(outcome_value / 1000.0, 1.0)),
        )

        content_score = min(1.0, max(0.1, len(output.strip()) / 240.0))
        score = min(
            1.0,
            (0.55 * base_confidence)
            + (0.25 * evidence_score)
            + (0.2 * content_score),
        )

        promote_to_l2 = score >= self.high_confidence_threshold
        promote_to_l3 = score >= self.l3_threshold

        outcome = {
            "score": round(score, 4),
            "confidence": round(base_confidence, 4),
            "outcome_value": round(outcome_value, 4),
            "outcome_confidence": round(outcome_confidence, 4),
            "evidence_score": round(evidence_score, 4),
            "content_score": round(content_score, 4),
            "promote_to_l2": promote_to_l2,
            "promote_to_l3": promote_to_l3,
            "promotion_targets": [
                tier
                for tier in ("L2", "L3")
                if (tier == "L2" and promote_to_l2)
                or (tier == "L3" and promote_to_l3)
            ],
        }

        logger.info(
            "Evaluation complete: score=%.4f confidence=%.4f promotions=%s",
            outcome["score"],
            outcome["confidence"],
            outcome["promotion_targets"],
        )

        return outcome
