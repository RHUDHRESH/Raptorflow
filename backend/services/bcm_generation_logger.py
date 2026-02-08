"""
BCM Generation Logger: logs every Muse generation for learning and reflection.

Each log entry captures the prompt, output, BCM version, and optional feedback.
The reflector service later analyzes these logs to improve the BCM.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from backend.core.supabase_mgr import get_supabase_client

logger = logging.getLogger(__name__)

TABLE = "bcm_generation_log"


def log_generation(
    workspace_id: str,
    content_type: str,
    prompt_used: str,
    output: str,
    bcm_version: int,
    tokens_used: int = 0,
    cost_usd: float = 0.0,
) -> Optional[Dict[str, Any]]:
    """Log a generation event. Returns the stored row (with id for feedback)."""
    client = get_supabase_client()
    row = {
        "workspace_id": workspace_id,
        "content_type": content_type,
        "prompt_used": prompt_used[:5000],
        "output": output[:10000],
        "bcm_version": bcm_version,
        "tokens_used": tokens_used,
        "cost_usd": cost_usd,
    }
    try:
        result = client.table(TABLE).insert(row).execute()
        if result.data:
            return result.data[0]
    except Exception as exc:
        logger.warning("Failed to log generation: %s", exc)
    return None


def get_recent_generations(
    workspace_id: str,
    content_type: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Get recent generations, optionally filtered by content type."""
    client = get_supabase_client()
    query = (
        client.table(TABLE)
        .select("*")
        .eq("workspace_id", workspace_id)
        .order("created_at", desc=True)
        .limit(limit)
    )
    if content_type:
        query = query.eq("content_type", content_type)

    result = query.execute()
    return result.data or []


def get_rated_generations(
    workspace_id: str,
    min_score: Optional[int] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Get generations that have feedback scores."""
    client = get_supabase_client()
    query = (
        client.table(TABLE)
        .select("*")
        .eq("workspace_id", workspace_id)
        .filter("feedback_score", "not.is", "null")
        .order("feedback_score", desc=True)
        .limit(limit)
    )
    if min_score is not None:
        query = query.gte("feedback_score", min_score)

    result = query.execute()
    return result.data or []


def cleanup_old_generations(workspace_id: str) -> int:
    """Prune old unrated generations to prevent unbounded growth.

    Deletes unrated generations older than 60 days.
    Rated generations are kept indefinitely (they have learning value).

    Returns the number of deleted rows.
    """
    from datetime import datetime, timedelta, timezone

    client = get_supabase_client()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
    deleted = 0

    try:
        result = (
            client.table(TABLE)
            .delete()
            .eq("workspace_id", workspace_id)
            .filter("feedback_score", "is", "null")
            .lt("created_at", cutoff)
            .execute()
        )
        deleted = len(result.data) if result.data else 0
        if deleted:
            logger.info(
                "Cleaned up %d old unrated generations for workspace %s",
                deleted, workspace_id,
            )
    except Exception as exc:
        logger.warning("Generation log cleanup failed for workspace %s: %s", workspace_id, exc)

    return deleted
