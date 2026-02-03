"""DB-local Supabase manager.

This module exists to satisfy legacy imports like `from db.core.supabase_mgr import ...`.
It forwards to the canonical implementation in `core.supabase_mgr`.
"""

from core.supabase_mgr import get_supabase_admin, get_supabase_client

from supabase import Client

__all__ = ["Client", "get_supabase_client", "get_supabase_admin"]
