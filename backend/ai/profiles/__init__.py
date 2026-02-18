"""
AI Profiles - Intensity and reasoning depth profiles for AI generation.

Profiles control resource allocation, temperature, and ensemble behavior
for different use cases and cost tiers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type, TypeVar

from backend.ai.types import IntensityLevel, ReasoningDepth, ExecutionMode


@dataclass
class ReasoningProfile:
    """
    Controls depth of reasoning and output complexity.

    Higher depths allow more tokens and higher temperature variance.
    """

    max_tokens_cap: int
    temperature_min: float
    temperature_max: float
    memory_limit: int

    def clamp_temperature(self, temperature: float) -> float:
        """Clamp temperature to allowed range."""
        return max(self.temperature_min, min(temperature, self.temperature_max))


REASONING_PROFILES: Dict[ReasoningDepth, ReasoningProfile] = {
    ReasoningDepth.LOW: ReasoningProfile(
        max_tokens_cap=500,
        temperature_min=0.2,
        temperature_max=0.5,
        memory_limit=3,
    ),
    ReasoningDepth.MEDIUM: ReasoningProfile(
        max_tokens_cap=1000,
        temperature_min=0.3,
        temperature_max=0.8,
        memory_limit=6,
    ),
    ReasoningDepth.HIGH: ReasoningProfile(
        max_tokens_cap=1800,
        temperature_min=0.4,
        temperature_max=0.9,
        memory_limit=10,
    ),
}


@dataclass
class IntensityProfile:
    """
    Controls resource intensity for generation.

    Higher intensity = more tokens, more parallelism, higher cost.
    """

    reasoning_depth: ReasoningDepth
    token_multiplier: float
    temperature_delta: float
    ensemble_cap: int


INTENSITY_PROFILES: Dict[IntensityLevel, IntensityProfile] = {
    IntensityLevel.LOW: IntensityProfile(
        reasoning_depth=ReasoningDepth.LOW,
        token_multiplier=0.75,
        temperature_delta=-0.1,
        ensemble_cap=1,
    ),
    IntensityLevel.MEDIUM: IntensityProfile(
        reasoning_depth=ReasoningDepth.MEDIUM,
        token_multiplier=1.0,
        temperature_delta=0.0,
        ensemble_cap=2,
    ),
    IntensityLevel.HIGH: IntensityProfile(
        reasoning_depth=ReasoningDepth.HIGH,
        token_multiplier=1.25,
        temperature_delta=0.08,
        ensemble_cap=3,
    ),
}


@dataclass
class AIProfile:
    """
    Complete AI generation profile combining intensity and reasoning settings.

    Resolved from user input or defaults, this profile drives the actual
    generation parameters.
    """

    intensity: IntensityLevel
    reasoning_depth: ReasoningDepth
    execution_mode: ExecutionMode
    max_tokens: int
    temperature: float
    memory_limit: int
    ensemble_size: int
    reasoning_profile: ReasoningProfile
    intensity_profile: IntensityProfile

    @classmethod
    def resolve(
        cls,
        requested_max_tokens: int = 800,
        requested_temperature: float = 0.7,
        intensity: Optional[IntensityLevel] = None,
        reasoning_depth: Optional[ReasoningDepth] = None,
        execution_mode: Optional[ExecutionMode] = None,
        default_intensity: IntensityLevel = IntensityLevel.MEDIUM,
        default_execution_mode: ExecutionMode = ExecutionMode.SINGLE,
    ) -> AIProfile:
        """
        Resolve a complete profile from user input.

        Args:
            requested_max_tokens: User-requested max tokens
            requested_temperature: User-requested temperature
            intensity: Intensity level (defaults to MEDIUM)
            reasoning_depth: Reasoning depth (defaults to intensity's depth)
            execution_mode: Execution mode (defaults to SINGLE)
            default_intensity: Default intensity if not specified
            default_execution_mode: Default execution mode if not specified

        Returns:
            Fully resolved AIProfile ready for generation
        """
        intensity = intensity or default_intensity
        execution_mode = execution_mode or default_execution_mode

        intensity_profile = INTENSITY_PROFILES.get(
            intensity, INTENSITY_PROFILES[IntensityLevel.MEDIUM]
        )

        reasoning_depth = reasoning_depth or intensity_profile.reasoning_depth
        reasoning_profile = REASONING_PROFILES.get(
            reasoning_depth, REASONING_PROFILES[ReasoningDepth.MEDIUM]
        )

        token_multiplier = intensity_profile.token_multiplier
        effective_max_tokens = min(
            int(requested_max_tokens * token_multiplier),
            reasoning_profile.max_tokens_cap,
        )

        adjusted_temp = requested_temperature + intensity_profile.temperature_delta
        effective_temperature = reasoning_profile.clamp_temperature(adjusted_temp)

        ensemble_cap = intensity_profile.ensemble_cap
        if execution_mode == ExecutionMode.SINGLE:
            ensemble_size = 1
        elif execution_mode == ExecutionMode.COUNCIL:
            ensemble_size = min(2, ensemble_cap)
        else:
            ensemble_size = min(3, ensemble_cap)

        return cls(
            intensity=intensity,
            reasoning_depth=reasoning_depth,
            execution_mode=execution_mode,
            max_tokens=effective_max_tokens,
            temperature=effective_temperature,
            memory_limit=reasoning_profile.memory_limit,
            ensemble_size=ensemble_size,
            reasoning_profile=reasoning_profile,
            intensity_profile=intensity_profile,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intensity": self.intensity.value,
            "reasoning_depth": self.reasoning_depth.value,
            "execution_mode": self.execution_mode.value,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "memory_limit": self.memory_limit,
            "ensemble_size": self.ensemble_size,
        }


class ProfileRegistry:
    """
    Registry for custom profiles.

    Allows registration of custom intensity and reasoning profiles
    beyond the defaults.
    """

    _instance: Optional[ProfileRegistry] = None

    def __new__(cls) -> ProfileRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._intensity_profiles = dict(INTENSITY_PROFILES)
            cls._instance._reasoning_profiles = dict(REASONING_PROFILES)
        return cls._instance

    def register_intensity(
        self,
        level: IntensityLevel,
        profile: IntensityProfile,
    ) -> None:
        self._intensity_profiles[level] = profile

    def register_reasoning(
        self,
        depth: ReasoningDepth,
        profile: ReasoningProfile,
    ) -> None:
        self._reasoning_profiles[depth] = profile

    def get_intensity(self, level: IntensityLevel) -> IntensityProfile:
        return self._intensity_profiles.get(
            level, INTENSITY_PROFILES[IntensityLevel.MEDIUM]
        )

    def get_reasoning(self, depth: ReasoningDepth) -> ReasoningProfile:
        return self._reasoning_profiles.get(
            depth, REASONING_PROFILES[ReasoningDepth.MEDIUM]
        )


__all__ = [
    "AIProfile",
    "ProfileRegistry",
    "IntensityProfile",
    "ReasoningProfile",
    "INTENSITY_PROFILES",
    "REASONING_PROFILES",
]
