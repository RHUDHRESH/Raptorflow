"""Supabase manager.

Provides a single, canonical way to create and access Supabase clients.
"""

import logging
import os
from typing import Optional

from supabase import Client, create_client

logger = logging.getLogger(__name__)

_supabase_client: Optional[Client] = None
_supabase_admin: Optional[Client] = None


def _get_supabase_url() -> str:
    return (
        os.getenv("SUPABASE_URL")
        or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        or os.getenv("DATABASE_URL")
        or ""
    )


def _get_supabase_anon_key() -> str:
    return os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY") or ""


def _get_supabase_service_role_key() -> str:
    return (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_SERVICE_KEY")
        or os.getenv("SERVICE_ROLE_KEY")
        or ""
    )


def get_supabase_client() -> Client:
    """Get a Supabase client suitable for server-side calls.

    Prefers service-role key if available, otherwise falls back to anon key.
    """

    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    url = _get_supabase_url()
    key = _get_supabase_service_role_key() or _get_supabase_anon_key()

    if not url or not key:
        raise ValueError(
            "Supabase credentials not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or NEXT_PUBLIC_SUPABASE_ANON_KEY)."
        )

    _supabase_client = create_client(url, key)
    return _supabase_client


def get_supabase_admin() -> Client:
    """Get an admin Supabase client (service role)."""

    global _supabase_admin

    if _supabase_admin is not None:
        return _supabase_admin

    url = _get_supabase_url()
    key = _get_supabase_service_role_key()

    if not url or not key:
        raise ValueError(
            "Supabase admin credentials not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
        )

    _supabase_admin = create_client(url, key)
    return _supabase_admin


def reset_supabase_clients() -> None:
    """Reset cached clients (useful for tests)."""

    global _supabase_client, _supabase_admin
    _supabase_client = None
    _supabase_admin = None
