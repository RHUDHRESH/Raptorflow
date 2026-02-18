"""
Cached database queries for expensive operations
Uses Redis caching decorator for performance
"""

from typing import List, Optional, Dict, Any, Callable
from backend.infrastructure.cache.decorator import cached, invalidate_cache


def _workspace_cache_key(workspace_id: str, **_kwargs: Any) -> str:
    return workspace_id


def _campaign_cache_key(
    workspace_id: str, status: Optional[str] = None, **_kwargs: Any
) -> str:
    return f"{workspace_id}:{status or 'all'}"


def _get_supabase_client():
    import backend.services.cached_queries as cached_queries_module

    getter = getattr(cached_queries_module, "get_supabase_client", None)
    if getter is not None:
        return getter()
    from backend.infrastructure.database.supabase import get_supabase_client

    return get_supabase_client()


def _set_supabase_client_getter(getter: Callable):
    global _supabase_client_getter
    _supabase_client_getter = getter


@cached(ttl=300, prefix="workspace", key_func=_workspace_cache_key)
async def get_workspace_by_id(workspace_id: str) -> Optional[Dict[str, Any]]:
    """
    Get workspace by ID with 5-minute cache.

    Args:
        workspace_id: Workspace UUID

    Returns:
        Workspace data or None
    """
    supabase = _get_supabase_client()
    result = supabase.table("workspaces").select("*").eq("id", workspace_id).execute()

    if result.data:
        return result.data[0]
    return None


@cached(ttl=600, prefix="campaigns", key_func=_campaign_cache_key)
async def get_workspace_campaigns(
    workspace_id: str, status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get campaigns for workspace with 10-minute cache.

    Args:
        workspace_id: Workspace UUID
        status: Optional status filter

    Returns:
        List of campaigns
    """
    supabase = _get_supabase_client()
    query = supabase.table("campaigns").select("*").eq("workspace_id", workspace_id)

    if status:
        query = query.eq("status", status)

    result = query.execute()
    return result.data or []


@cached(ttl=300, prefix="foundation", key_func=_workspace_cache_key)
async def get_foundation_data(workspace_id: str) -> Optional[Dict[str, Any]]:
    """
    Get foundation data with 5-minute cache.

    Args:
        workspace_id: Workspace UUID

    Returns:
        Foundation data or None
    """
    supabase = _get_supabase_client()

    # Get all foundation components
    brand_kits = (
        supabase.table("foundation_brand_kits")
        .select("*")
        .eq("workspace_id", workspace_id)
        .execute()
    )
    positioning = (
        supabase.table("foundation_positioning")
        .select("*")
        .eq("workspace_id", workspace_id)
        .execute()
    )
    voice_tones = (
        supabase.table("foundation_voice_tones")
        .select("*")
        .eq("workspace_id", workspace_id)
        .execute()
    )
    state = (
        supabase.table("foundation_state")
        .select("*")
        .eq("workspace_id", workspace_id)
        .execute()
    )

    return {
        "brand_kits": brand_kits.data or [],
        "positioning": positioning.data or [],
        "voice_tones": voice_tones.data or [],
        "state": state.data[0] if state.data else None,
    }


@cached(ttl=900, prefix="icp", key_func=_workspace_cache_key)
async def get_workspace_icps(workspace_id: str) -> List[Dict[str, Any]]:
    """
    Get ICP profiles for workspace with 15-minute cache.

    Args:
        workspace_id: Workspace UUID

    Returns:
        List of ICP profiles with related data
    """
    supabase = _get_supabase_client()

    # Get ICP profiles
    profiles = (
        supabase.table("icp_profiles")
        .select("*")
        .eq("workspace_id", workspace_id)
        .execute()
    )

    if not profiles.data:
        return []

    # Enrich with related data
    enriched_profiles = []
    for profile in profiles.data:
        profile_id = profile["id"]

        # Get related data
        firmographics = (
            supabase.table("icp_firmographics")
            .select("*")
            .eq("profile_id", profile_id)
            .execute()
        )
        pain_map = (
            supabase.table("icp_pain_map")
            .select("*")
            .eq("profile_id", profile_id)
            .execute()
        )
        psycholinguistics = (
            supabase.table("icp_psycholinguistics")
            .select("*")
            .eq("profile_id", profile_id)
            .execute()
        )

        enriched_profiles.append(
            {
                **profile,
                "firmographics": firmographics.data[0] if firmographics.data else None,
                "pain_map": pain_map.data or [],
                "psycholinguistics": psycholinguistics.data[0]
                if psycholinguistics.data
                else None,
            }
        )

    return enriched_profiles


async def invalidate_workspace_cache(workspace_id: str) -> None:
    """
    Invalidate all cache entries for a workspace.

    Args:
        workspace_id: Workspace UUID
    """
    await invalidate_cache("workspace", workspace_id)
    await invalidate_cache("campaigns", workspace_id)
    await invalidate_cache("foundation", workspace_id)
    await invalidate_cache("icp", workspace_id)


async def invalidate_campaign_cache(workspace_id: str) -> None:
    """
    Invalidate campaign cache for a workspace.

    Args:
        workspace_id: Workspace UUID
    """
    await invalidate_cache("campaigns", workspace_id)
