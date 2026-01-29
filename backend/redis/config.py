"""
Redis configuration for Raptorflow.

Centralizes all Redis-related configuration settings.
import os
from typing import Optional
class RedisConfig:
    """Redis configuration settings."""
    # Connection settings
    UPSTASH_REDIS_URL = os.getenv("UPSTASH_REDIS_URL", "redis://localhost:6379")
    UPSTASH_REDIS_TOKEN = os.getenv("UPSTASH_REDIS_TOKEN", "")
    # Key settings
    KEY_PREFIX = "raptorflow:"
    DEFAULT_TTL = 3600  # 1 hour in seconds
    MAX_CONNECTIONS = 10
    # Session settings
    SESSION_TTL = 1800  # 30 minutes
    MAX_SESSIONS_PER_USER = 5
    # Cache settings
    CACHE_TTL = 3600  # 1 hour
    MAX_CACHE_SIZE = 1024 * 1024  # 1MB per entry
    CACHE_CLEANUP_INTERVAL = 3600  # 1 hour
    # Rate limiting settings
    RATE_LIMIT_TTL = 60  # 1 minute
    DEFAULT_RATE_LIMITS = {
        "api": (100, 60),  # 100 requests per minute
        "agents": (50, 60),  # 50 agent calls per minute
        "upload": (10, 60),  # 10 uploads per minute
        "export": (5, 60),  # 5 exports per minute
    }
    # Queue settings
    QUEUE_TTL = 86400  # 24 hours
    MAX_QUEUE_SIZE = 10000
    JOB_RETRY_DELAY = 60  # 1 minute
    MAX_JOB_RETRIES = 3
    # Worker settings
    WORKER_HEARTBEAT_INTERVAL = 30  # 30 seconds
    WORKER_TIMEOUT = 300  # 5 minutes
    MAX_WORKERS_PER_QUEUE = 10
    # Usage tracking settings
    USAGE_TTL = 86400 * 90  # 90 days
    USAGE_ALERT_THRESHOLDS = {
        "daily": 10.0,  # $10 per day
        "monthly": 100.0,  # $100 per month
    # PubSub settings
    PUBSUB_TTL = 3600  # 1 hour
    MAX_SUBSCRIBERS_PER_CHANNEL = 100
    # Lock settings
    LOCK_TTL = 300  # 5 minutes
    LOCK_RETRY_DELAY = 1  # 1 second
    MAX_LOCK_RETRIES = 10
    # Monitoring settings
    METRICS_TTL = 3600  # 1 hour
    HEALTH_CHECK_INTERVAL = 60  # 1 minute
    # Security settings
    ENCRYPTION_KEY = os.getenv("REDIS_ENCRYPTION_KEY", "")
    ENABLE_ENCRYPTION = os.getenv("REDIS_ENABLE_ENCRYPTION", "false").lower() == "true"
    # Performance settings
    CONNECTION_POOL_SIZE = 10
    SOCKET_TIMEOUT = 30
    SOCKET_CONNECT_TIMEOUT = 10
    MAX_RETRIES_PER_COMMAND = 3
    RETRY_DELAY = 1  # 1 second
    # Development settings
    DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
    MOCK_REDIS = os.getenv("MOCK_REDIS", "false").lower() == "true"
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode."""
        return (
            os.getenv("ENVIRONMENT", "").lower() == "production" and not cls.MOCK_REDIS
        )
    def get_connection_string(cls) -> str:
        """Get Redis connection string."""
        if cls.MOCK_REDIS:
            raise ValueError("Mock Redis cannot be used in production")
        return cls.UPSTASH_REDIS_URL or ""
    def get_auth_token(cls) -> Optional[str]:
        """Get Redis authentication token."""
        return cls.UPSTASH_REDIS_TOKEN or None
    def validate_config(cls) -> list[str]:
        """
        Validate configuration and return list of issues.
        Returns:
            List of configuration issues
        issues = []
        # Production validation
        if cls.is_production():
            if not cls.UPSTASH_REDIS_URL:
                issues.append("UPSTASH_REDIS_URL not set in production")
            if not cls.UPSTASH_REDIS_TOKEN:
                issues.append("UPSTASH_REDIS_TOKEN not set in production")
            if cls.MOCK_REDIS:
                issues.append("MOCK_REDIS cannot be enabled in production")
        else:
            # Development validation
            if not cls.UPSTASH_REDIS_URL and not cls.MOCK_REDIS:
                issues.append("UPSTASH_REDIS_URL not set and MOCK_REDIS is disabled")
        if cls.MAX_CONNECTIONS < 1:
            issues.append("MAX_CONNECTIONS must be at least 1")
        if cls.DEFAULT_TTL < 1:
            issues.append("DEFAULT_TTL must be at least 1 second")
        if cls.SESSION_TTL < 60:
            issues.append("SESSION_TTL should be at least 60 seconds")
        return issues
    def get_rate_limit(cls, endpoint: str, user_tier: str = "free") -> tuple[int, int]:
        Get rate limit for endpoint and user tier.
        Args:
            endpoint: API endpoint
            user_tier: User subscription tier
            Tuple of (limit, window_seconds)
        # Base limits from default configuration
        base_limit, base_window = cls.DEFAULT_RATE_LIMITS.get(endpoint, (10, 60))
        # Adjust based on user tier
        tier_multipliers = {"free": 1.0, "starter": 2.0, "pro": 5.0, "enterprise": 10.0}
        multiplier = tier_multipliers.get(user_tier, 1.0)
        adjusted_limit = int(base_limit * multiplier)
        return adjusted_limit, base_window
    def get_cache_ttl(cls, cache_type: str = "default") -> int:
        Get TTL for different cache types.
            cache_type: Type of cached data
            TTL in seconds
        ttl_mapping = {
            "default": cls.CACHE_TTL,
            "session": cls.SESSION_TTL,
            "user": cls.CACHE_TTL * 2,
            "workspace": cls.CACHE_TTL * 4,
            "system": cls.CACHE_TTL * 8,
        }
        return ttl_mapping.get(cache_type, cls.DEFAULT_TTL)
    def should_encrypt(cls, key_pattern: str) -> bool:
        Determine if data should be encrypted based on key pattern.
            key_pattern: Redis key pattern
            True if encryption should be used
        if not cls.ENABLE_ENCRYPTION:
            return False
        # Encrypt sensitive data patterns
        sensitive_patterns = [
            "session:",
            "user:",
            "auth:",
            "token:",
            "credential:",
        ]
        return any(pattern in key_pattern.lower() for pattern in sensitive_patterns)
# Global configuration instance
config = RedisConfig()
def get_config() -> RedisConfig:
    """Get global Redis configuration instance."""
    return config
def validate_redis_config() -> bool:
    """
    Validate Redis configuration.
    Returns:
        True if configuration is valid
    issues = config.validate_config()
    if issues:
        print("Redis configuration issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    return True
