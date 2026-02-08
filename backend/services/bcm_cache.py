"""
BCM Cache: Upstash Redis hot cache for BCM manifests and compiled prompts.

Provides fast (~2ms) reads for BCM data that would otherwise require
a Supabase round-trip (~200ms). Write-through on store, invalidate on rebuild.

Falls back gracefully if Redis is unavailable — all methods return None on miss
and silently skip writes on error.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Key prefixes and TTLs
_PREFIX = "bcm:"
MANIFEST_TTL = 3600       # 1 hour
PROMPT_KIT_TTL = 1800     # 30 min
MEMORY_SUMMARY_TTL = 300  # 5 min

def _get_client():
    """Get the shared Upstash Redis client from redis_mgr."""
    try:
        from backend.core.redis_mgr import get_redis_client
        return get_redis_client()
    except Exception as exc:
        logger.warning("BCM cache disabled: %s", exc)
        return None


def _key(workspace_id: str, suffix: str) -> str:
    return f"{_PREFIX}{workspace_id}:{suffix}"


# ── Manifest cache ───────────────────────────────────────────────────────────

def get_manifest(workspace_id: str) -> Optional[Dict[str, Any]]:
    """Get cached BCM manifest. Returns None on miss or error."""
    client = _get_client()
    if not client:
        return None
    try:
        data = client.get(_key(workspace_id, "manifest"))
        if data:
            return json.loads(data) if isinstance(data, str) else data
    except Exception as exc:
        logger.debug("Cache miss (manifest): %s", exc)
    return None


def set_manifest(workspace_id: str, manifest: Dict[str, Any]) -> None:
    """Cache a BCM manifest with TTL."""
    client = _get_client()
    if not client:
        return
    try:
        client.set(
            _key(workspace_id, "manifest"),
            json.dumps(manifest, separators=(",", ":")),
            ex=MANIFEST_TTL,
        )
    except Exception as exc:
        logger.debug("Cache write failed (manifest): %s", exc)


# ── Compiled prompt cache ────────────────────────────────────────────────────

def get_compiled_prompt(workspace_id: str, content_type: str) -> Optional[str]:
    """Get a cached compiled system prompt for a content type."""
    client = _get_client()
    if not client:
        return None
    try:
        data = client.get(_key(workspace_id, f"prompt:{content_type}"))
        if data:
            return data if isinstance(data, str) else str(data)
    except Exception as exc:
        logger.debug("Cache miss (prompt:%s): %s", content_type, exc)
    return None


def set_compiled_prompt(
    workspace_id: str, content_type: str, prompt: str
) -> None:
    """Cache a compiled system prompt."""
    client = _get_client()
    if not client:
        return
    try:
        client.set(
            _key(workspace_id, f"prompt:{content_type}"),
            prompt,
            ex=PROMPT_KIT_TTL,
        )
    except Exception as exc:
        logger.debug("Cache write failed (prompt:%s): %s", content_type, exc)


# ── Memory summary cache ────────────────────────────────────────────────────

def get_memory_summary(workspace_id: str) -> Optional[Dict[str, Any]]:
    """Get cached memory summary."""
    client = _get_client()
    if not client:
        return None
    try:
        data = client.get(_key(workspace_id, "memory_summary"))
        if data:
            return json.loads(data) if isinstance(data, str) else data
    except Exception as exc:
        logger.debug("Cache miss (memory_summary): %s", exc)
    return None


def set_memory_summary(
    workspace_id: str, summary: Dict[str, Any]
) -> None:
    """Cache a memory summary."""
    client = _get_client()
    if not client:
        return
    try:
        client.set(
            _key(workspace_id, "memory_summary"),
            json.dumps(summary, separators=(",", ":")),
            ex=MEMORY_SUMMARY_TTL,
        )
    except Exception as exc:
        logger.debug("Cache write failed (memory_summary): %s", exc)


# ── Invalidation ─────────────────────────────────────────────────────────────

def invalidate(workspace_id: str) -> None:
    """Invalidate all cached data for a workspace. Called on BCM update/rebuild."""
    client = _get_client()
    if not client:
        return
    try:
        # Delete manifest
        client.delete(_key(workspace_id, "manifest"))
        # Delete known prompt types
        for ct in ("general", "email", "blog", "social", "ad_copy"):
            client.delete(_key(workspace_id, f"prompt:{ct}"))
        # Delete memory summary
        client.delete(_key(workspace_id, "memory_summary"))
        logger.info("Cache invalidated for workspace %s", workspace_id)
    except Exception as exc:
        logger.debug("Cache invalidation failed: %s", exc)
