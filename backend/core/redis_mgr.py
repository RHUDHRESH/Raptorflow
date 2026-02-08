"""Upstash Redis manager.

Provides a single, canonical way to access the Upstash Redis client.
Falls back gracefully if credentials are not configured.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

_redis_client = None
_init_attempted = False


def get_redis_client():
    """Get the Upstash Redis client. Returns None if unavailable."""
    global _redis_client, _init_attempted

    if _init_attempted:
        return _redis_client
    _init_attempted = True

    try:
        from backend.config.settings import get_settings

        settings = get_settings()
        url = settings.UPSTASH_REDIS_REST_URL
        token = settings.UPSTASH_REDIS_REST_TOKEN

        if not url or not token:
            logger.info("Redis disabled: no Upstash credentials configured")
            return None

        from upstash_redis import Redis

        _redis_client = Redis(url=url, token=token)
        # Quick connectivity check
        _redis_client.ping()
        logger.info("Redis initialized (Upstash REST)")
        return _redis_client
    except ImportError:
        logger.warning("Redis disabled: upstash-redis package not installed")
        return None
    except Exception as exc:
        logger.warning("Redis disabled: %s", exc)
        return None


def reset_redis_client() -> None:
    """Reset cached client (useful for tests)."""
    global _redis_client, _init_attempted
    _redis_client = None
    _init_attempted = False
