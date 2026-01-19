"""
Redis key patterns and builders for Raptorflow.

Provides consistent key naming conventions across all Redis services.
"""

from typing import Optional

# Key prefixes
KEY_PREFIX = "raptorflow:"
SESSION_PREFIX = "session:"
CACHE_PREFIX = "cache:"
RATE_LIMIT_PREFIX = "rl:"
QUEUE_PREFIX = "queue:"
PUBSUB_PREFIX = "pubsub:"
LOCK_PREFIX = "lock:"
USAGE_PREFIX = "usage:"
WORKER_PREFIX = "worker:"
JOB_PREFIX = "job:"
ALERT_PREFIX = "alert:"


def build_session_key(session_id: str) -> str:
    """Build session key."""
    return f"{KEY_PREFIX}{SESSION_PREFIX}{session_id}"


def build_cache_key(workspace_id: str, key: str) -> str:
    """Build cache key with workspace isolation."""
    return f"{KEY_PREFIX}{CACHE_PREFIX}{workspace_id}:{key}"


def build_rate_limit_key(user_id: str, endpoint: str) -> str:
    """Build rate limit key."""
    return f"{KEY_PREFIX}{RATE_LIMIT_PREFIX}{user_id}:{endpoint}"


def build_queue_key(queue_name: str) -> str:
    """Build queue key."""
    return f"{KEY_PREFIX}{QUEUE_PREFIX}{queue_name}"


def build_queue_processing_key(queue_name: str) -> str:
    """Build queue processing key."""
    return f"{KEY_PREFIX}{QUEUE_PREFIX}{queue_name}:processing"


def build_pubsub_key(channel: str) -> str:
    """Build pubsub channel key."""
    return f"{KEY_PREFIX}{PUBSUB_PREFIX}{channel}"


def build_lock_key(resource: str) -> str:
    """Build distributed lock key."""
    return f"{KEY_PREFIX}{LOCK_PREFIX}{resource}"


def build_usage_key(workspace_id: str, period: str) -> str:
    """Build usage tracking key."""
    return f"{KEY_PREFIX}{USAGE_PREFIX}{workspace_id}:{period}"


def build_worker_key(worker_id: str) -> str:
    """Build worker info key."""
    return f"{KEY_PREFIX}{WORKER_PREFIX}{worker_id}"


def build_job_key(job_id: str) -> str:
    """Build job data key."""
    return f"{KEY_PREFIX}{JOB_PREFIX}{job_id}"


def build_alert_key(workspace_id: str, alert_id: str) -> str:
    """Build alert key."""
    return f"{KEY_PREFIX}{ALERT_PREFIX}{workspace_id}:{alert_id}"


def parse_key(key: str) -> Optional[dict]:
    """
    Parse a Redis key to extract components.

    Args:
        key: Redis key string

    Returns:
        Dictionary with parsed components or None if invalid
    """
    if not key.startswith(KEY_PREFIX):
        return None

    # Remove prefix
    key_without_prefix = key[len(KEY_PREFIX) :]

    # Split by first colon to get service
    parts = key_without_prefix.split(":", 1)
    if len(parts) < 2:
        return {"service": parts[0], "identifier": ""}

    service, identifier = parts

    result = {"service": service, "identifier": identifier}

    # Parse service-specific components
    if service == SESSION_PREFIX.rstrip(":"):
        result["session_id"] = identifier
    elif service == CACHE_PREFIX.rstrip(":"):
        workspace_parts = identifier.split(":", 1)
        result["workspace_id"] = workspace_parts[0]
        result["cache_key"] = workspace_parts[1] if len(workspace_parts) > 1 else ""
    elif service == RATE_LIMIT_PREFIX.rstrip(":"):
        user_parts = identifier.split(":", 1)
        result["user_id"] = user_parts[0]
        result["endpoint"] = user_parts[1] if len(user_parts) > 1 else ""
    elif service == QUEUE_PREFIX.rstrip(":"):
        result["queue_name"] = identifier
    elif service == USAGE_PREFIX.rstrip(":"):
        workspace_parts = identifier.split(":", 1)
        result["workspace_id"] = workspace_parts[0]
        result["period"] = workspace_parts[1] if len(workspace_parts) > 1 else ""
    elif service == WORKER_PREFIX.rstrip(":"):
        result["worker_id"] = identifier
    elif service == JOB_PREFIX.rstrip(":"):
        result["job_id"] = identifier
    elif service == ALERT_PREFIX.rstrip(":"):
        workspace_parts = identifier.split(":", 1)
        result["workspace_id"] = workspace_parts[0]
        result["alert_id"] = workspace_parts[1] if len(workspace_parts) > 1 else ""

    return result


def validate_key(key: str) -> bool:
    """
    Validate that a key follows Raptorflow conventions.

    Args:
        key: Redis key string

    Returns:
        True if valid, False otherwise
    """
    if not key or not isinstance(key, str):
        return False

    if not key.startswith(KEY_PREFIX):
        return False

    # Check for valid service prefix
    key_without_prefix = key[len(KEY_PREFIX) :]
    valid_services = [
        SESSION_PREFIX.rstrip(":"),
        CACHE_PREFIX.rstrip(":"),
        RATE_LIMIT_PREFIX.rstrip(":"),
        QUEUE_PREFIX.rstrip(":"),
        PUBSUB_PREFIX.rstrip(":"),
        LOCK_PREFIX.rstrip(":"),
        USAGE_PREFIX.rstrip(":"),
        WORKER_PREFIX.rstrip(":"),
        JOB_PREFIX.rstrip(":"),
        ALERT_PREFIX.rstrip(":"),
    ]

    for service in valid_services:
        if key_without_prefix.startswith(service):
            return True

    return False


# Key expiration constants
DEFAULT_TTL = 3600  # 1 hour
SESSION_TTL = 1800  # 30 minutes
CACHE_TTL = 3600  # 1 hour
RATE_LIMIT_TTL = 60  # 1 minute
JOB_TTL = 86400  # 24 hours
ALERT_TTL = 86400  # 24 hours


def get_ttl_for_service(service: str) -> int:
    """
    Get default TTL for a service.

    Args:
        service: Service name

    Returns:
        TTL in seconds
    """
    ttl_mapping = {
        SESSION_PREFIX.rstrip(":"): SESSION_TTL,
        CACHE_PREFIX.rstrip(":"): CACHE_TTL,
        RATE_LIMIT_PREFIX.rstrip(":"): RATE_LIMIT_TTL,
        QUEUE_PREFIX.rstrip(":"): JOB_TTL,
        ALERT_PREFIX.rstrip(":"): ALERT_TTL,
    }

    return ttl_mapping.get(service, DEFAULT_TTL)
