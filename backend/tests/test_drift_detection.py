import pytest

from services.drift_detection import DriftDetectionService


def test_drift_detection_no_drift():
    """Verify that similar distributions do not trigger drift."""
    service = DriftDetectionService()
    baseline = [1.0, 1.1, 1.2, 1.0, 0.9]
    current = [1.0, 1.1, 1.2, 1.0, 0.9]

    p_value = service.calculate_p_value(baseline, current)
    assert p_value > 0.05


def test_drift_detection_significant_drift():
    """Verify that significantly different distributions trigger drift."""
    service = DriftDetectionService()
    baseline = [1.0, 1.1, 1.2, 1.0, 0.9]
    current = [5.0, 5.5, 4.8, 6.0, 5.2]

    p_value = service.calculate_p_value(baseline, current)
    assert p_value < 0.05


def test_detect_drift_multi_metrics():
    """Verify multi-metric drift detection logic."""
    service = DriftDetectionService()
    baseline = {"latency": [100, 110, 105], "tokens": [500, 550, 520]}
    current = {"latency": [100, 110, 105], "tokens": [2000, 2500, 2200]}

    results = service.detect_drift(baseline, current)
    assert results["is_drifting"] is True
    assert results["metrics"]["latency"]["is_drifting"] is False
    assert results["metrics"]["tokens"]["is_drifting"] is True
