"""
Auth Service - Authentication operations.

Supports multiple auth modes:
- demo: Local demo mode (no real auth)
- supabase: Real Supabase authentication
- disabled: No auth (development only)
"""

from backend.services.auth.factory import get_auth_service, reset_auth_service
from backend.services.auth.demo import DemoAuthService, get_demo_auth_service
from backend.services.auth.supabase import (
    SupabaseAuthService,
    get_supabase_auth_service,
)
from backend.services.auth.disabled import (
    DisabledAuthService,
    get_disabled_auth_service,
)

auth_service = None

try:
    auth_service = get_auth_service()
except Exception as e:
    import logging

    logging.warning(f"Failed to initialize auth service: {e}")

__all__ = [
    "auth_service",
    "get_auth_service",
    "reset_auth_service",
    "DemoAuthService",
    "get_demo_auth_service",
    "SupabaseAuthService",
    "get_supabase_auth_service",
    "DisabledAuthService",
    "get_disabled_auth_service",
]
