import pytest

from backend.core.pivoting import PivotEngine


def test_pivot_logic_detection():
    """
    Phase 59: Verify that the PivotEngine recommends shifts on low quality.
    """
    # 1. Low quality triggers high urgency pivot
    recs = PivotEngine.evaluate_pivot(0.4, [])
    assert len(recs) == 1
    assert recs[0].urgency == "high"
    assert "research" in recs[0].proposed_pivot.lower()

    # 2. Positive quality, no pivot
    recs_good = PivotEngine.evaluate_pivot(0.9, [])
    assert len(recs_good) == 0
