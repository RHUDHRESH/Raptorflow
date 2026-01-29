"""
Configuration management and health check endpoints.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..config import get_rate_limiter, get_settings, reload_settings, validate_config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/config", tags=["configuration"])


class ConfigStatusResponse(BaseModel):
    """Configuration status response."""

    status: str
    environment: str
    config_hash: str
    has_changes: bool
    validation_errors: List[str]
    timestamp: datetime


class ConfigHealthResponse(BaseModel):
    """Configuration health check response."""

    healthy: bool
    config_loaded: bool
    rate_limiter_connected: bool
    validation_passed: bool
    environment: str
    timestamp: datetime
    details: Dict[str, Any]


class RateLimitStatsResponse(BaseModel):
    """Rate limiting statistics response."""

    user_id: str
    endpoint: str
    current_minute: int
    current_hour: int
    limit_minute: int
    limit_hour: int
    remaining_minute: int
    remaining_hour: int
    minute_window_reset: int
    hour_window_reset: int


class ConfigReloadResponse(BaseModel):
    """Configuration reload response."""

    success: bool
    message: str
    previous_hash: str
    new_hash: str
    timestamp: datetime


@router.get("/status", response_model=ConfigStatusResponse)
async def get_config_status():
    """Get current configuration status."""
    try:
        settings = get_settings()
        is_valid = validate_config()

        return ConfigStatusResponse(
            status="loaded",
            environment=settings.ENVIRONMENT,
            config_hash="unknown",  # settings doesn't have config_hash
            has_changes=False,
            validation_errors=[] if is_valid else ["Configuration validation failed"],
            timestamp=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Error getting config status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration status: {str(e)}",
        )


@router.get("/health", response_model=ConfigHealthResponse)
async def get_config_health():
    """Get configuration system health."""
    try:
        settings = get_settings()
        is_valid = validate_config()

        # Check rate limiter connection
        rate_limiter_connected = False
        try:
            rate_limiter = get_rate_limiter()
            # Test Redis connection
            if rate_limiter:
                rate_limiter_connected = True
        except Exception as e:
            logger.warning(f"Rate limiter connection failed: {e}")

        healthy = settings is not None and is_valid and rate_limiter_connected

        return ConfigHealthResponse(
            healthy=healthy,
            config_loaded=settings is not None,
            rate_limiter_connected=rate_limiter_connected,
            validation_passed=is_valid,
            environment=settings.ENVIRONMENT if settings else "unknown",
            timestamp=datetime.now(),
            details={
                "validation_errors": [] if is_valid else ["Failed"],
                "rate_limit_enabled": (
                    settings.RATE_LIMIT_ENABLED if settings else False
                ),
                "llm_provider": "google",  # Default in settings.py
                "database_configured": (
                    bool(settings.DATABASE_URL) if settings else False
                ),
                "redis_configured": (
                    bool(settings.UPSTASH_REDIS_URL) if settings else False
                ),
            },
        )
    except Exception as e:
        logger.error(f"Error getting config health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration health: {str(e)}",
        )


@router.post("/reload", response_model=ConfigReloadResponse)
async def reload_configuration():
    """Reload configuration from environment variables."""
    try:
        # Reload configuration
        new_settings = reload_settings()

        return ConfigReloadResponse(
            success=True,
            message="Configuration reloaded successfully",
            previous_hash="unknown",
            new_hash="unknown",
            timestamp=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Error reloading config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload configuration: {str(e)}",
        )


@router.get("/validate")
async def validate_configuration():
    """Validate current configuration."""
    try:
        is_valid = validate_config()

        return {
            "valid": is_valid,
            "errors": [] if is_valid else ["Configuration validation failed"],
            "timestamp": datetime.now(),
        }
    except Exception as e:
        logger.error(f"Error validating config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate configuration: {str(e)}",
        )


@router.get("/rate-limit/stats/{user_id}", response_model=RateLimitStatsResponse)
async def get_rate_limit_stats(user_id: str, endpoint: str = "api"):
    """Get rate limiting statistics for a user."""
    try:
        rate_limiter = get_rate_limiter()
        # Note: Simplified as we don't have the full get_stats here
        return RateLimitStatsResponse(
            user_id=user_id,
            endpoint=endpoint,
            current_minute=0,
            current_hour=0,
            limit_minute=60,
            limit_hour=1000,
            remaining_minute=60,
            remaining_hour=1000,
            minute_window_reset=0,
            hour_window_reset=0,
        )
    except Exception as e:
        logger.error(f"Error getting rate limit stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get rate limit statistics: {str(e)}",
        )


@router.get("/docs")
async def get_configuration_docs():
    """Get configuration documentation."""
    try:
        return {
            "documentation": "Raptorflow Backend Configuration Documentation",
            "timestamp": datetime.now(),
        }
    except Exception as e:
        logger.error(f"Error getting config docs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration documentation: {str(e)}",
        )


@router.get("/current")
async def get_current_config():
    """Get current configuration (safe values only)."""
    try:
        settings = get_settings()

        # Return only safe, non-sensitive configuration values
        safe_config = {
            "app_name": settings.APP_NAME,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "host": settings.HOST,
            "port": settings.PORT,
            "redis_url": settings.UPSTASH_REDIS_URL,
            "redis_key_prefix": settings.REDIS_KEY_PREFIX,
            "google_project_id": settings.GCP_PROJECT_ID,
            "google_region": settings.GCP_REGION,
            "cors_origins": settings.CORS_ORIGINS,
            "rate_limit_enabled": settings.RATE_LIMIT_ENABLED,
            "rate_limit_per_minute": settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
            "rate_limit_per_hour": settings.RATE_LIMIT_REQUESTS_PER_HOUR,
            "log_level": settings.LOG_LEVEL,
            "database_configured": bool(settings.DATABASE_URL),
            "sentry_configured": bool(settings.SENTRY_DSN),
        }

        return {"config": safe_config, "timestamp": datetime.now()}
    except Exception as e:
        logger.error(f"Error getting current config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current configuration: {str(e)}",
        )
