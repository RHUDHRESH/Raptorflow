"""
Rate limit configurations for Redis-based rate limiting.

This module is intentionally lightweight: it defines the default limits and a few
helpers for looking up per-endpoint/per-tier limits. The runtime implementation
is in `backend/redis/rate_limit.py`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class EndpointConfig:
    """Configuration for an endpoint's rate limiting."""

    path_pattern: str
    method: str
    base_limit: int
    window_seconds: int
    description: str = ""
    burst_allowance: int = 0


class RateLimitConfiguration:
    """Centralized rate limit configuration."""

    # Base rate limits per endpoint (requests, window_seconds, description)
    DEFAULT_LIMITS: Dict[str, Tuple[int, int, str]] = {
        "api": (100, 60, "General API requests"),
        "agents": (50, 60, "Agent execution requests"),
        "agent_execute": (20, 60, "Agent execution operations"),
        "muse_generate": (30, 60, "Muse content generation"),
        "upload": (10, 60, "File uploads"),
        "export": (5, 60, "Data exports"),
        "webhook": (1000, 60, "Webhook processing"),
        "auth": (100, 60, "Authentication requests"),
        "foundation": (20, 60, "Foundation data operations"),
        "icps": (20, 60, "ICP management"),
        "campaigns": (15, 60, "Campaign operations"),
        "moves": (30, 60, "Move operations"),
        "daily_wins": (5, 60, "Daily wins generation"),
        "analytics": (50, 60, "Analytics queries"),
        "billing": (20, 60, "Billing operations"),
        "health": (1000, 60, "Health checks"),
        "metrics": (100, 60, "Metrics endpoints"),
    }

    # User tier multipliers
    TIER_MULTIPLIERS: Dict[str, float] = {
        "free": 1.0,
        "starter": 2.0,
        "growth": 5.0,
        "pro": 10.0,
        "enterprise": 20.0,
        "unlimited": 100.0,
    }

    # Optional endpoint-specific configuration (used for richer metadata)
    ENDPOINT_CONFIGS: Dict[str, EndpointConfig] = {
        "health": EndpointConfig(
            path_pattern="/health",
            method="GET",
            base_limit=1000,
            window_seconds=60,
            description="Health check endpoint",
            burst_allowance=100,
        ),
        "metrics": EndpointConfig(
            path_pattern="/metrics",
            method="GET",
            base_limit=100,
            window_seconds=60,
            description="Metrics endpoint",
            burst_allowance=50,
        ),
        "agent_execute": EndpointConfig(
            path_pattern="/api/agents/execute",
            method="POST",
            base_limit=20,
            window_seconds=60,
            description="Agent execution",
            burst_allowance=5,
        ),
        "muse_generate": EndpointConfig(
            path_pattern="/api/muse/generate",
            method="POST",
            base_limit=30,
            window_seconds=60,
            description="Muse content generation",
            burst_allowance=10,
        ),
        "upload": EndpointConfig(
            path_pattern="/api/upload",
            method="POST",
            base_limit=10,
            window_seconds=60,
            description="File uploads",
            burst_allowance=2,
        ),
        "export": EndpointConfig(
            path_pattern="/api/export",
            method="POST",
            base_limit=5,
            window_seconds=60,
            description="Data exports",
            burst_allowance=1,
        ),
    }

    @classmethod
    def get_limit_for_endpoint(cls, endpoint: str, user_tier: str = "free") -> Tuple[int, int]:
        """
        Get (limit, window_seconds) for an endpoint and user tier.

        `endpoint` should be a stable identifier (e.g. "api", "agent_execute").
        """
        if endpoint in cls.ENDPOINT_CONFIGS:
            cfg = cls.ENDPOINT_CONFIGS[endpoint]
            multiplier = cls.TIER_MULTIPLIERS.get(user_tier, 1.0)
            return int(cfg.base_limit * multiplier), cfg.window_seconds

        base_limit, window_seconds, _desc = cls.DEFAULT_LIMITS.get(
            endpoint, cls.DEFAULT_LIMITS["api"]
        )
        multiplier = cls.TIER_MULTIPLIERS.get(user_tier, 1.0)
        return int(base_limit * multiplier), window_seconds

    @classmethod
    def get_endpoint_config(cls, endpoint: str) -> Optional[EndpointConfig]:
        """Get detailed endpoint configuration."""
        return cls.ENDPOINT_CONFIGS.get(endpoint)

    @classmethod
    def validate_tier(cls, user_tier: str) -> bool:
        """Validate user tier."""
        return user_tier in cls.TIER_MULTIPLIERS

