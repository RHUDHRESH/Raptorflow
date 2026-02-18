"""
Shared AI runtime profiles across orchestration modules.

Defines:
- execution topology modes (single/council/swarm)
- intensity profiles (low/medium/high)
"""

from __future__ import annotations

from typing import Any, Dict, Literal, cast


ExecutionMode = Literal["single", "council", "swarm"]
IntensityLevel = Literal["low", "medium", "high"]


EXECUTION_MODES = {"single", "council", "swarm"}
INTENSITY_LEVELS = {"low", "medium", "high"}


INTENSITY_PROFILES: Dict[str, Dict[str, Any]] = {
    "low": {
        "muse": {
            "reasoning_depth": "low",
            "token_multiplier": 0.75,
            "temperature_delta": -0.1,
            "ensemble_cap": 1,
        },
        "search": {
            "default_engines": ["duckduckgo"],
            "max_results": 10,
            "summary_results": 4,
        },
        "scraper": {
            "default_strategy": "conservative",
            "timeout_seconds": 45,
        },
    },
    "medium": {
        "muse": {
            "reasoning_depth": "medium",
            "token_multiplier": 1.0,
            "temperature_delta": 0.0,
            "ensemble_cap": 2,
        },
        "search": {
            "default_engines": ["duckduckgo", "brave"],
            "max_results": 20,
            "summary_results": 6,
        },
        "scraper": {
            "default_strategy": "balanced",
            "timeout_seconds": 30,
        },
    },
    "high": {
        "muse": {
            "reasoning_depth": "high",
            "token_multiplier": 1.25,
            "temperature_delta": 0.08,
            "ensemble_cap": 3,
        },
        "search": {
            "default_engines": ["duckduckgo", "brave", "searx"],
            "max_results": 40,
            "summary_results": 8,
        },
        "scraper": {
            "default_strategy": "optimized",
            "timeout_seconds": 25,
        },
    },
}


def normalize_execution_mode(value: str | None) -> ExecutionMode:
    raw = (value or "").strip().lower()
    if raw in EXECUTION_MODES:
        return cast(ExecutionMode, raw)
    return "council"


def normalize_intensity(value: str | None) -> IntensityLevel:
    raw = (value or "").strip().lower()
    if raw in INTENSITY_LEVELS:
        return cast(IntensityLevel, raw)
    return "medium"


def intensity_profile(level: str | None) -> Dict[str, Any]:
    normalized = normalize_intensity(level)
    return INTENSITY_PROFILES[normalized]
