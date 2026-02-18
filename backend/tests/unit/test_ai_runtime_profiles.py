from __future__ import annotations

from backend.agents.runtime.profiles import (
    intensity_profile,
    normalize_execution_mode,
    normalize_intensity,
)


def test_normalize_execution_mode_defaults_to_council() -> None:
    assert normalize_execution_mode("single") == "single"
    assert normalize_execution_mode("swarm") == "swarm"
    assert normalize_execution_mode("unknown") == "council"


def test_normalize_intensity_defaults_to_medium() -> None:
    assert normalize_intensity("low") == "low"
    assert normalize_intensity("HIGH") == "high"
    assert normalize_intensity("custom") == "medium"


def test_intensity_profile_contains_required_shapes() -> None:
    profile = intensity_profile("high")
    assert profile["muse"]["reasoning_depth"] == "high"
    assert "default_engines" in profile["search"]
    assert "default_strategy" in profile["scraper"]
