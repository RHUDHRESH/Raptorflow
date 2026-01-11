"""
Rate limit configurations for Redis-based rate limiting.

Defines endpoint-specific limits, user tiers, and rate limiting policies.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class RateLimitConfig:
    """Configuration for a single rate limit."""

    limit: int
    window_seconds: int
    description: str
    tier_multipliers: Dict[str, float]


@dataclass
class EndpointConfig:
    """Configuration for an endpoint's rate limiting."""

    path_pattern: str
    method: str
    base_limit: int
    window_seconds: int
    description: str
    tier_multipliers: Dict[str, float]
    burst_allowance: int = 0
    custom_headers: Dict[str, str] = None


class RateLimitConfiguration:
    """Centralized rate limit configuration."""

    # Base rate limits per endpoint (requests, window_seconds)
    DEFAULT_LIMITS = {
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
    TIER_MULTIPLIERS = {
        "free": 1.0,
        "starter": 2.0,
        "growth": 5.0,
        "pro": 10.0,
        "enterprise": 20.0,
        "unlimited": 100.0,
    }

    # Special endpoint configurations
    ENDPOINT_CONFIGS = {
        # High-frequency endpoints
        "health": EndpointConfig(
            path_pattern="/health",
            method="GET",
            base_limit=1000,
            window_seconds=60,
            description="Health check endpoint",
            tier_multipliers=TIER_MULTIPLIERS,
            burst_allowance=100,
        ),
        "metrics": EndpointConfig(
            path_pattern="/metrics",
            method="GET",
            base_limit=100,
            window_seconds=60,
            description="Metrics collection",
            tier_multipliers=TIER_MULTIPLIERS,
            burst_allowance=50,
        ),
        # Agent operations
        "agent_execute": EndpointConfig(
            path_pattern="/api/v1/agents/execute",
            method="POST",
            base_limit=20,
            window_seconds=60,
            description="Agent execution",
            tier_multipliers=TIER_MULTIPLIERS,
            custom_headers={"X-RateLimit-Agent": "true", "X-RateLimit-Cost": "tokens"},
        ),
        # Content generation
        "muse_generate": EndpointConfig(
            path_pattern="/api/v1/muse/generate",
            method="POST",
            base_limit=30,
            window_seconds=60,
            description="Muse content generation",
            tier_multipliers=TIER_MULTIPLIERS,
            custom_headers={
                "X-RateLimit-Content": "generation",
                "X-RateLimit-Cost": "tokens",
            },
        ),
        # File operations
        "upload": EndpointConfig(
            path_pattern="/api/v1/upload",
            method="POST",
            base_limit=10,
            window_seconds=60,
            description="File uploads",
            tier_multipliers=TIER_MULTIPLIERS,
            custom_headers={"X-RateLimit-File": "upload", "X-RateLimit-Size": "10MB"},
        ),
        # Export operations
        "export": EndpointConfig(
            path_pattern="/api/v1/export",
            method="POST",
            base_limit=5,
            window_seconds=60,
            description="Data exports",
            tier_multipliers=TIER_MULTIPLIERS,
            custom_headers={"X-RateLimit-Export": "data", "X-RateLimit-Size": "50MB"},
        ),
    }

    # Global rate limit policies
    GLOBAL_POLICIES = {
        "max_requests_per_hour": {
            "free": 1000,
            "starter": 5000,
            "growth": 20000,
            "pro": 50000,
            "enterprise": 100000,
            "unlimited": 1000000,
        },
        "max_tokens_per_hour": {
            "free": 10000,
            "starter": 50000,
            "growth": 200000,
            "progress": 500000,
            "enterprise": 1000000,
            "unlimited": 10000000,
        },
        "max_cost_per_hour": {
            "free": 1.0,  # $1 per hour
            "starter": 5.0,  # $5 per hour
            "growth": 20.0,  # $20 per hour
            "pro": 50.0,  # $50 per hour
            "enterprise": 100.0,  # $100 per hour
            "unlimited": 1000.0,  # $1000 per hour
        },
    }

    # Rate limit bypass rules
    BYPASS_RULES = {
        "admin_users": {"bypass_all": True, "multiplier": 100.0},
        "internal_services": {
            "bypass_endpoints": ["health", "metrics"],
            "multiplier": 10.0,
        },
        "webhook_sources": {"bypass_endpoints": ["webhook"], "multiplier": 5.0},
    }

    # Rate limit escalation policies
    ESCALATION_POLICIES = {
        "violation_threshold": 5,  # Number of violations before escalation
        "escalation_actions": [
            "log_warning",
            "reduce_multiplier",
            "temporary_block",
            "permanent_block",
        ],
        "block_durations": {
            "temporary": 300,  # 5 minutes
            "permanent": 86400,  # 24 hours
        },
    }

    @classmethod
    def get_limit_for_endpoint(
        cls, endpoint: str, user_tier: str = "free"
    ) -> Tuple[int, int]:
        """
        Get rate limit for endpoint and user tier.

        Args:
            endpoint: Endpoint identifier
            user_tier: User subscription tier

        Returns:
            Tuple of (limit, window_seconds)
        """
        # Check for special endpoint config
        if endpoint in cls.ENDPOINT_CONFIGS:
            config = cls.ENDPOINT_CONFIGS[endpoint]
            multiplier = config.tier_multipliers.get(
                user_tier, cls.TIER_MULTIPLIERS.get(user_tier, 1.0)
            )
            return int(config.base_limit * multiplier), config.window_seconds

        # Use default limits
        base_limit, window = cls.DEFAULT_LIMITS.get(endpoint, cls.DEFAULT_LIMITS["api"])
        multiplier = cls.TIER_MULTIPLIERS.get(user_tier, 1.0)
        return int(base_limit * multiplier), window

    @classmethod
    def get_endpoint_config(cls, endpoint: str) -> Optional[EndpointConfig]:
        """Get detailed endpoint configuration."""
        return cls.ENDPOINT_CONFIGS.get(endpoint)

    @classmethod
    def get_tier_multiplier(cls, user_tier: str) -> float:
        """Get tier multiplier for user."""
        return cls.TIER_MULTIPLIERS.get(user_tier, 1.0)

    @classmethod
    def should_bypass_limit(
        cls, endpoint: str, user_id: str, user_tier: str, user_role: str = None
    ) -> Tuple[bool, float]:
        """
        Check if rate limit should be bypassed for user.

        Returns:
            Tuple of (should_bypass, multiplier)
        """
        # Check admin bypass
        if user_role == "admin":
            return True, cls.BYPASS_RULES["admin_users"]["multiplier"]

        # Check internal service bypass
        if user_role == "service":
            config = cls.BYPASS_RULES["internal_services"]
            if endpoint in config["bypass_endpoints"]:
                return True, config["multiplier"]

        # Check webhook source bypass
        if user_role == "webhook":
            config = cls.BYPASS_RULES["webhook_sources"]
            if endpoint in config["bypass_endpoints"]:
                return True, config["multiplier"]

        return False, 1.0

    @classmethod
    def get_global_limits(cls, user_tier: str) -> Dict[str, int]:
        """Get global limits for user tier."""
        return {
            key: limits.get(user_tier, cls.GLOBAL_POLICIES[key]["free"])
            for key, limits in cls.GLOBAL_POLICIES.items()
        }

    @classmethod
    def validate_tier(cls, user_tier: str) -> bool:
        """Validate user tier."""
        return user_tier in cls.TIER_MULTIPLIERS

    @classmethod
    def get_all_endpoint_configs(cls) -> Dict[str, EndpointConfig]:
        """Get all endpoint configurations."""
        return cls.ENDPOINT_CONFIGS.copy()

    @classmethod
    def add_custom_endpoint(cls, config: EndpointConfig):
        """Add custom endpoint configuration."""
        cls.ENDPOINT_CONFIGS[config.path_pattern] = config

    @classmethod
    def update_endpoint_limit(cls, endpoint: str, limit: int, window_seconds: int):
        """Update endpoint limit."""
        if endpoint in cls.ENDPOINT_CONFIGS:
            cls.ENDPOINT_CONFIGS[endpoint].base_limit = limit
            cls.ENDPOINT_CONFIGS[endpoint].window_seconds = window_seconds
        else:
            # Create new config
            cls.ENDPOINT_CONFIGS[endpoint] = EndpointConfig(
                path_pattern=endpoint,
                method="*",
                base_limit=limit,
                window_seconds=window_seconds,
                description=f"Custom limit for {endpoint}",
                tier_multipliers=cls.TIER_MULTIPLIERS.copy(),
            )

    @classmethod
    def get_rate_limit_headers(cls, result) -> Dict[str, str]:
        """Generate standard rate limit headers."""
        headers = {
            "X-RateLimit-Limit": str(result.limit),
            "X-RateLimit-Remaining": str(result.remaining),
            "X-RateLimit-Reset": str(int(result.reset_at.timestamp())),
            "X-RateLimit-Window": str(result.window_seconds),
        }

        if result.retry_after:
            headers["Retry-After"] = str(result.retry_after)

        return headers


# Utility functions for rate limit configuration
def get_rate_limit_for_path(path: str, method: str = "GET") -> Optional[str]:
    """Get rate limit key for HTTP path and method."""
    # Normalize path
    normalized_path = path.rstrip("/")

    # Direct match
    if normalized_path in RateLimitConfiguration.DEFAULT_LIMITS:
        return normalized_path

    # Pattern matching
    for endpoint_config in RateLimitConfiguration.ENDPOINT_CONFIGS.values():
        if normalized_path.startswith(endpoint_config.path_pattern) and (
            method == endpoint_config.method or endpoint_config.method == "*"
        ):
            return endpoint_config.path_pattern

    # Default to API
    return "api"


def is_rate_limited_endpoint(path: str) -> bool:
    """Check if endpoint should be rate limited."""
    # Skip health and metrics endpoints from rate limiting
    skip_patterns = ["/health", "/metrics", "/status"]
    return not any(path.startswith(pattern) for pattern in skip_patterns)


def get_rate_limit_priority(endpoint: str) -> int:
    """Get priority for rate limit checking (lower = higher priority)."""
    priority_map = {
        "health": 1000,
        "metrics": 999,
        "agent_execute": 100,
        "muse_generate": 90,
        "upload": 80,
        "export": 70,
        "webhook": 60,
        "api": 50,
        "agents": 40,
        "foundation": 30,
        "icps": 20,
        "campaigns": 10,
    }

    return priority_map.get(endpoint, 0)
