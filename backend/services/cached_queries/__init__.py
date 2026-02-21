"""
Cached Queries Service - Cached database queries.
"""

from backend.core.database.supabase import get_supabase_client
from backend.services.cached_queries.service import (
    get_foundation_data,
    get_workspace_by_id,
    get_workspace_campaigns,
    invalidate_cache,
    invalidate_workspace_cache,
)

__all__ = [
    "get_workspace_by_id",
    "get_workspace_campaigns",
    "get_foundation_data",
    "invalidate_cache",
    "invalidate_workspace_cache",
    "get_supabase_client",
]
