"""
Configuration management and health check endpoints.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel

from config import (
    get_config, 
    get_rate_limiter, 
    reload_config, 
    validate_config,
    EssentialConfig
)

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
        config = get_config()
        validation_errors = validate_config()
        has_changes = config.has_config_changed()
        
        return ConfigStatusResponse(
            status="loaded",
            environment=config.environment,
            config_hash=config.config_hash or "unknown",
            has_changes=has_changes,
            validation_errors=validation_errors,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error getting config status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration status: {str(e)}"
        )


@router.get("/health", response_model=ConfigHealthResponse)
async def get_config_health():
    """Get configuration system health."""
    try:
        config = get_config()
        validation_errors = validate_config()
        
        # Check rate limiter connection
        rate_limiter_connected = False
        try:
            rate_limiter = get_rate_limiter()
            # Test Redis connection
            await rate_limiter._get_redis()
            rate_limiter_connected = True
        except Exception as e:
            logger.warning(f"Rate limiter connection failed: {e}")
        
        healthy = (
            config is not None and
            len(validation_errors) == 0 and
            rate_limiter_connected
        )
        
        return ConfigHealthResponse(
            healthy=healthy,
            config_loaded=config is not None,
            rate_limiter_connected=rate_limiter_connected,
            validation_passed=len(validation_errors) == 0,
            environment=config.environment if config else "unknown",
            timestamp=datetime.now(),
            details={
                "validation_errors": validation_errors,
                "rate_limit_enabled": config.rate_limit_enabled if config else False,
                "llm_provider": config.llm_provider if config else "unknown",
                "database_configured": bool(config.database_url) if config else False,
                "redis_configured": bool(config.redis_url) if config else False,
            }
        )
    except Exception as e:
        logger.error(f"Error getting config health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration health: {str(e)}"
        )


@router.post("/reload", response_model=ConfigReloadResponse)
async def reload_configuration():
    """Reload configuration from environment variables."""
    try:
        config = get_config()
        previous_hash = config.config_hash or "unknown"
        
        # Reload configuration
        new_config = await reload_config()
        new_hash = new_config.config_hash or "unknown"
        
        return ConfigReloadResponse(
            success=True,
            message="Configuration reloaded successfully",
            previous_hash=previous_hash,
            new_hash=new_hash,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error reloading config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload configuration: {str(e)}"
        )


@router.get("/validate")
async def validate_configuration():
    """Validate current configuration."""
    try:
        validation_errors = validate_config()
        
        return {
            "valid": len(validation_errors) == 0,
            "errors": validation_errors,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error validating config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate configuration: {str(e)}"
        )


@router.get("/rate-limit/stats/{user_id}", response_model=RateLimitStatsResponse)
async def get_rate_limit_stats(user_id: str, endpoint: str = "api"):
    """Get rate limiting statistics for a user."""
    try:
        rate_limiter = get_rate_limiter()
        stats = await rate_limiter.get_stats(user_id, endpoint)
        
        return RateLimitStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting rate limit stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get rate limit statistics: {str(e)}"
        )


@router.post("/rate-limit/reset/{user_id}")
async def reset_rate_limit(user_id: str, endpoint: str = "api"):
    """Reset rate limiting for a user."""
    try:
        rate_limiter = get_rate_limiter()
        success = await rate_limiter.reset_limit(user_id, endpoint)
        
        return {
            "success": success,
            "message": f"Rate limit reset for user {user_id} on endpoint {endpoint}",
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error resetting rate limit: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset rate limit: {str(e)}"
        )


@router.get("/docs")
async def get_configuration_docs():
    """Get configuration documentation."""
    try:
        from config import ENVIRONMENT_DOCS
        
        return {
            "documentation": ENVIRONMENT_DOCS,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error getting config docs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration documentation: {str(e)}"
        )


@router.get("/current")
async def get_current_config():
    """Get current configuration (safe values only)."""
    try:
        config = get_config()
        
        # Return only safe, non-sensitive configuration values
        safe_config = {
            "app_name": config.app_name,
            "environment": config.environment,
            "debug": config.debug,
            "host": config.host,
            "port": config.port,
            "redis_url": config.redis_url,
            "redis_key_prefix": config.redis_key_prefix,
            "llm_provider": config.llm_provider,
            "google_project_id": config.google_project_id,
            "google_region": config.google_region,
            "cors_origins": config.cors_origins,
            "agent_timeout_seconds": config.agent_timeout_seconds,
            "max_tokens_per_request": config.max_tokens_per_request,
            "rate_limit_enabled": config.rate_limit_enabled,
            "rate_limit_per_minute": config.rate_limit_per_minute,
            "rate_limit_per_hour": config.rate_limit_per_hour,
            "log_level": config.log_level,
            "config_hash": config.config_hash,
            "has_secrets": bool(config.secret_key and config.secret_key.get_secret_value() != "your-secret-key-change-in-production"),
            "has_google_api_key": bool(config.google_api_key),
            "database_configured": bool(config.database_url),
            "sentry_configured": bool(config.sentry_dsn),
        }
        
        return {
            "config": safe_config,
            "timestamp": datetime.now()
        }
    except Exception as e:
        logger.error(f"Error getting current config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current configuration: {str(e)}"
        )
