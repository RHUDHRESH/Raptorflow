"""
BCM Service: Supabase CRUD for Business Context Manifests.

Provides both sync (static reducer) and async (AI synthesizer) paths.
Integrates Upstash Redis cache for fast reads.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from backend.core.supabase_mgr import get_supabase_client
from backend.services.bcm_reducer import reduce_business_context
from backend.services import bcm_cache

logger = logging.getLogger(__name__)

TABLE = "business_context_manifests"


def _next_version(workspace_id: str) -> int:
    """Get the next version number for a workspace."""
    client = get_supabase_client()
    result = (
        client.table(TABLE)
        .select("version")
        .eq("workspace_id", workspace_id)
        .order("version", desc=True)
        .limit(1)
        .execute()
    )
    if result.data:
        return result.data[0]["version"] + 1
    return 1


def store_manifest(
    workspace_id: str,
    manifest: Dict[str, Any],
    source_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Store a BCM manifest in Supabase with write-through cache."""
    client = get_supabase_client()
    version = manifest.get("version", _next_version(workspace_id))

    row = {
        "workspace_id": workspace_id,
        "version": version,
        "manifest": manifest,
        "source_context": source_context,
        "checksum": manifest.get("checksum", ""),
        "token_estimate": manifest.get("meta", {}).get("token_estimate", 0),
    }

    result = client.table(TABLE).insert(row).execute()
    if result.data:
        logger.info("Stored BCM v%d for workspace %s", version, workspace_id)
        # Write-through: update cache with new manifest
        bcm_cache.set_manifest(workspace_id, manifest)
        return result.data[0]
    raise RuntimeError(f"Failed to store BCM manifest: {result}")


def get_latest(workspace_id: str) -> Optional[Dict[str, Any]]:
    """Get the latest BCM manifest row for a workspace.

    Always returns the full Supabase row (with source_context, created_at, etc.)
    so callers like rebuild/reflect can access source_context.
    Populates cache on read for fast manifest-only access.
    """
    client = get_supabase_client()
    result = (
        client.table(TABLE)
        .select("*")
        .eq("workspace_id", workspace_id)
        .order("version", desc=True)
        .limit(1)
        .execute()
    )
    if result.data:
        row = result.data[0]
        if row.get("manifest"):
            bcm_cache.set_manifest(workspace_id, row["manifest"])
        return row
    return None


def get_manifest_fast(workspace_id: str) -> Optional[Dict[str, Any]]:
    """Get just the BCM manifest dict (cache-first, no source_context).

    Use this for prompt compilation and Muse generation where only the
    manifest content is needed, not the full DB row.
    """
    cached = bcm_cache.get_manifest(workspace_id)
    if cached:
        return cached

    row = get_latest(workspace_id)
    return row["manifest"] if row else None


def get_by_version(workspace_id: str, version: int) -> Optional[Dict[str, Any]]:
    """Get a specific BCM version."""
    client = get_supabase_client()
    result = (
        client.table(TABLE)
        .select("*")
        .eq("workspace_id", workspace_id)
        .eq("version", version)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def list_versions(workspace_id: str) -> List[Dict[str, Any]]:
    """List all BCM versions for a workspace (summary only)."""
    client = get_supabase_client()
    result = (
        client.table(TABLE)
        .select("id, workspace_id, version, checksum, token_estimate, created_at")
        .eq("workspace_id", workspace_id)
        .order("version", desc=True)
        .execute()
    )
    return result.data or []


def rebuild(workspace_id: str) -> Optional[Dict[str, Any]]:
    """Rebuild BCM from the latest stored source_context (sync/static).

    Returns the new manifest row, or None if no source context exists.
    """
    latest = get_latest(workspace_id)
    if not latest or not latest.get("source_context"):
        logger.warning("No source_context found for workspace %s", workspace_id)
        return None

    source = latest["source_context"]
    new_version = latest["version"] + 1

    manifest = reduce_business_context(
        business_context=source,
        workspace_id=workspace_id,
        version=new_version,
        source="rebuild",
    )

    bcm_cache.invalidate(workspace_id)
    return store_manifest(workspace_id, manifest, source)


async def rebuild_async(workspace_id: str) -> Optional[Dict[str, Any]]:
    """Rebuild BCM with AI synthesis from the latest stored source_context.

    Returns the new manifest row, or None if no source context exists.
    """
    from backend.services.bcm_synthesizer import synthesize_business_context

    latest = get_latest(workspace_id)
    if not latest or not latest.get("source_context"):
        logger.warning("No source_context found for workspace %s", workspace_id)
        return None

    source = latest["source_context"]
    new_version = latest["version"] + 1

    manifest = await synthesize_business_context(
        business_context=source,
        workspace_id=workspace_id,
        version=new_version,
        source="rebuild",
    )

    bcm_cache.invalidate(workspace_id)
    return store_manifest(workspace_id, manifest, source)


def seed_from_business_context(
    workspace_id: str,
    business_context: Dict[str, Any],
) -> Dict[str, Any]:
    """Seed a BCM from a raw business_context.json (sync/static).

    Runs the reducer and stores both the manifest and source context.
    """
    version = _next_version(workspace_id)

    manifest = reduce_business_context(
        business_context=business_context,
        workspace_id=workspace_id,
        version=version,
        source="seed",
    )

    return store_manifest(workspace_id, manifest, business_context)


async def seed_from_business_context_async(
    workspace_id: str,
    business_context: Dict[str, Any],
) -> Dict[str, Any]:
    """Seed a BCM with AI synthesis from a raw business_context.json.

    Runs the synthesizer (static reducer + AI enrichment) and stores both.
    """
    from backend.services.bcm_synthesizer import synthesize_business_context

    version = _next_version(workspace_id)

    manifest = await synthesize_business_context(
        business_context=business_context,
        workspace_id=workspace_id,
        version=version,
        source="seed",
    )

    return store_manifest(workspace_id, manifest, business_context)


def clear_all(workspace_id: str) -> int:
    """Delete all BCM manifests for a workspace. Returns count deleted."""
    client = get_supabase_client()
    result = client.table(TABLE).delete().eq("workspace_id", workspace_id).execute()
    deleted_count = len(result.data) if result.data else 0
    logger.info("Cleared %d BCM manifests for workspace %s", deleted_count, workspace_id)
    bcm_cache.invalidate(workspace_id)
    return deleted_count
