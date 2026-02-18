"""
Policy profile resolution for the AI Hub.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable

from backend.ai.hub.contracts import ToolPolicy
from backend.services.exceptions import ValidationError


@dataclass(frozen=True)
class PolicyProfile:
    name: str
    description: str
    default_allowed_tools: frozenset[str]
    allow_mutating_external: bool = False


_PROFILES: Dict[str, PolicyProfile] = {
    "strict": PolicyProfile(
        name="strict",
        description="No implicit tools. Callers must explicitly allow tools.",
        default_allowed_tools=frozenset(),
        allow_mutating_external=False,
    ),
    "balanced": PolicyProfile(
        name="balanced",
        description="Safe defaults for deterministic, non-mutating tools.",
        default_allowed_tools=frozenset({"echo_context", "stable_hash"}),
        allow_mutating_external=False,
    ),
    "creative": PolicyProfile(
        name="creative",
        description="Same safety as balanced with broader generation latitude.",
        default_allowed_tools=frozenset({"echo_context", "stable_hash"}),
        allow_mutating_external=False,
    ),
}


def normalize_policy_profile(policy_profile: str | None) -> str:
    normalized = str(policy_profile or "balanced").strip().lower()
    if normalized not in _PROFILES:
        allowed = ", ".join(sorted(_PROFILES.keys()))
        raise ValidationError(
            f"Unknown policy_profile '{policy_profile}'. Allowed: {allowed}"
        )
    return normalized


def build_tool_policy(
    *,
    policy_profile: str,
    requested_tools: Iterable[str],
    explicit_allowed_tools: Iterable[str],
    allow_mutating_external: bool,
) -> ToolPolicy:
    profile_name = normalize_policy_profile(policy_profile)
    profile = _PROFILES[profile_name]

    requested = [str(tool).strip() for tool in requested_tools if str(tool).strip()]
    explicit = {
        str(tool).strip() for tool in explicit_allowed_tools if str(tool).strip()
    }

    if explicit:
        allowed_tools = explicit
    else:
        allowed_tools = {
            tool for tool in requested if tool in profile.default_allowed_tools
        }

    return ToolPolicy(
        allowed_tools=allowed_tools,
        allow_mutating_external=bool(
            allow_mutating_external or profile.allow_mutating_external
        ),
    )


def describe_policy_profiles() -> Dict[str, Dict[str, Any]]:
    return {
        name: {
            "description": profile.description,
            "default_allowed_tools": sorted(profile.default_allowed_tools),
            "allow_mutating_external": profile.allow_mutating_external,
        }
        for name, profile in sorted(_PROFILES.items())
    }

