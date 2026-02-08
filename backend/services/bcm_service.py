"""
BCM Service: Supabase CRUD for Business Context Manifests.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from backend.core.supabase_mgr import get_supabase_client
from backend.services.bcm_reducer import reduce_business_context

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
    """Store a BCM manifest in Supabase. Returns the stored row."""
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
        return result.data[0]
    raise RuntimeError(f"Failed to store BCM manifest: {result}")


def get_latest(workspace_id: str) -> Optional[Dict[str, Any]]:
    """Get the latest BCM manifest for a workspace."""
    client = get_supabase_client()
    result = (
        client.table(TABLE)
        .select("*")
        .eq("workspace_id", workspace_id)
        .order("version", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


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
    """Rebuild BCM from the latest stored source_context.

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

    return store_manifest(workspace_id, manifest, source)


def seed_from_business_context(
    workspace_id: str,
    business_context: Dict[str, Any],
) -> Dict[str, Any]:
    """Seed a BCM from a raw business_context.json.

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
