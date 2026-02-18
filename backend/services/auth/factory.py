"""Auth Service Factory - Returns appropriate auth service based on AUTH_MODE."""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)

_auth_service: Optional[Any] = None

# Trusted proxy IPs for rate limiting (configure for your setup)
TRUSTED_PROXY_IPS = os.getenv("TRUSTED_PROXY_IPS", "127.0.0.1,::1").split(",")


def _is_production() -> bool:
    """Check if running in production environment."""
    env = os.getenv("ENVIRONMENT", "").lower()
    return env in ("prod", "production", "staging")


def _validate_auth_mode() -> tuple[str, bool]:
    """Validate AUTH_MODE setting.

    Returns:
        Tuple of (auth_mode, is_valid)
    """
    auth_mode = os.getenv("AUTH_MODE", "").strip().lower()

    if not auth_mode:
        return "", False

    valid_modes = ("demo", "supabase", "disabled")
    if auth_mode not in valid_modes:
        return auth_mode, False

    return auth_mode, True


def get_auth_service() -> Any:
    """Get the configured auth service based on AUTH_MODE setting.

    Returns:
        DemoAuthService if AUTH_MODE=demo (DEV ONLY)
        SupabaseAuthService if AUTH_MODE=supabase

    Raises:
        ValueError: If AUTH_MODE is invalid or demo mode used in production
    """
    global _auth_service

    if _auth_service is not None:
        return _auth_service

    # Validate AUTH_MODE
    auth_mode, is_valid = _validate_auth_mode()

    if not auth_mode:
        raise ValueError(
            "AUTH_MODE environment variable is required. "
            "Set AUTH_MODE=demo, supabase, or disabled"
        )

    if not is_valid:
        raise ValueError(
            f"Invalid AUTH_MODE: {auth_mode}. Use: demo, supabase, or disabled"
        )

    # Block demo mode in production
    if auth_mode == "demo":
        if _is_production():
            raise ValueError(
                "Demo mode (AUTH_MODE=demo) is not allowed in production. "
                "Use AUTH_MODE=supabase or AUTH_MODE=disabled"
            )
        logger.warning("DEMO MODE - FOR DEVELOPMENT ONLY - NOT SECURE")

    if auth_mode == "demo":
        from backend.services.auth.demo import get_demo_auth_service

        _auth_service = get_demo_auth_service()
        logger.info("Auth service: DEMO mode (DEV ONLY)")
    elif auth_mode == "supabase":
        from backend.services.auth.supabase import get_supabase_auth_service

        _auth_service = get_supabase_auth_service()
        logger.info("Auth service: SUPABASE mode")
    elif auth_mode == "disabled":
        from backend.services.auth.disabled import get_disabled_auth_service

        _auth_service = get_disabled_auth_service()
        logger.warning("Auth service: DISABLED (no auth required)")

    return _auth_service


def reset_auth_service() -> None:
    """Reset the auth service (useful for testing)."""
    global _auth_service
    _auth_service = None


__all__ = [
    "get_auth_service",
    "reset_auth_service",
    "TRUSTED_PROXY_IPS",
]
