"""
BCM Memory: CRUD for accumulated learning from user feedback and generation analysis.

Memories are workspace-scoped observations that the BCM uses to improve over time.
Types: correction, preference, pattern, insight.
Sources: user_feedback, generation_analysis, reflection.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from backend.core.supabase_mgr import get_supabase_client
from backend.services import bcm_cache

logger = logging.getLogger(__name__)

TABLE = "bcm_memories"


def add_memory(
    workspace_id: str,
    memory_type: str,
    content: Dict[str, Any],
    source: str,
    confidence: float = 0.5,
) -> Dict[str, Any]:
    """Store a new memory. Invalidates the memory summary cache."""
    client = get_supabase_client()
    row = {
        "workspace_id": workspace_id,
        "memory_type": memory_type,
        "content": content,
        "source": source,
        "confidence": confidence,
    }
    result = client.table(TABLE).insert(row).execute()
    if result.data:
        bcm_cache.invalidate(workspace_id)
        logger.info("Added %s memory for workspace %s", memory_type, workspace_id)
        return result.data[0]
    raise RuntimeError(f"Failed to store memory: {result}")


def get_relevant_memories(
    workspace_id: str,
    memory_type: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Get recent memories, optionally filtered by type."""
    client = get_supabase_client()
    query = (
        client.table(TABLE)
        .select("*")
        .eq("workspace_id", workspace_id)
        .order("created_at", desc=True)
        .limit(limit)
    )
    if memory_type:
        query = query.eq("memory_type", memory_type)

    result = query.execute()
    return result.data or []


def get_memory_summary(workspace_id: str) -> Dict[str, Any]:
    """Get a summary of all memories for a workspace (cached)."""
    cached = bcm_cache.get_memory_summary(workspace_id)
    if cached:
        return cached

    client = get_supabase_client()

    # Count by type
    all_memories = (
        client.table(TABLE)
        .select("memory_type, content, confidence")
        .eq("workspace_id", workspace_id)
        .order("confidence", desc=True)
        .limit(50)
        .execute()
    )
    rows = all_memories.data or []

    type_counts: Dict[str, int] = {}
    top_memories: List[Dict[str, Any]] = []
    for row in rows:
        mt = row.get("memory_type", "unknown")
        type_counts[mt] = type_counts.get(mt, 0) + 1
        if len(top_memories) < 10:
            top_memories.append(row)

    summary = {
        "total_count": len(rows),
        "type_counts": type_counts,
        "top_memories": top_memories,
    }

    bcm_cache.set_memory_summary(workspace_id, summary)
    return summary


def record_feedback(
    workspace_id: str,
    generation_id: str,
    score: int,
    edits: Optional[str] = None,
) -> Dict[str, Any]:
    """Record user feedback on a generation and create a memory from it."""
    client = get_supabase_client()

    # Security: Verify generation belongs to this workspace
    gen_check = (
        client.table("bcm_generation_log")
        .select("id")
        .eq("id", generation_id)
        .eq("workspace_id", workspace_id)
        .limit(1)
        .execute()
    )
    if not gen_check.data:
        raise ValueError(f"Generation {generation_id} not found or not owned by workspace")

    # Update the generation log
    update_data: Dict[str, Any] = {"feedback_score": score}
    if edits:
        update_data["user_edits"] = edits

    client.table("bcm_generation_log").update(update_data).eq(
        "id", generation_id
    ).execute()

    # Create a memory from the feedback
    memory_content: Dict[str, Any] = {
        "generation_id": generation_id,
        "score": score,
    }
    if edits:
        memory_content["user_edits"] = edits
        memory_type = "correction"
        memory_content["summary"] = f"User edited output (score: {score}/5)"
    elif score >= 4:
        memory_type = "preference"
        memory_content["summary"] = f"User liked this output (score: {score}/5)"
    else:
        memory_type = "correction"
        memory_content["summary"] = f"User disliked this output (score: {score}/5)"

    return add_memory(
        workspace_id=workspace_id,
        memory_type=memory_type,
        content=memory_content,
        source="user_feedback",
        confidence=score / 5.0,
    )


def delete_memory(workspace_id: str, memory_id: str) -> bool:
    """Delete a specific memory."""
    client = get_supabase_client()
    result = (
        client.table(TABLE)
        .delete()
        .eq("id", memory_id)
        .eq("workspace_id", workspace_id)
        .execute()
    )
    if result.data:
        bcm_cache.invalidate(workspace_id)
        return True
    return False


def cleanup_old_memories(workspace_id: str) -> int:
    """Prune stale memories to prevent unbounded growth.

    Deletes:
    - Low-confidence (<0.3) memories older than 30 days
    - All memories older than 90 days
    - Expired memories (expires_at < now)

    Returns the total number of deleted rows.
    """
    from datetime import datetime, timedelta, timezone

    client = get_supabase_client()
    now = datetime.now(timezone.utc)
    cutoff_30d = (now - timedelta(days=30)).isoformat()
    cutoff_90d = (now - timedelta(days=90)).isoformat()
    deleted = 0

    try:
        # 1. Expired memories
        r1 = (
            client.table(TABLE)
            .delete()
            .eq("workspace_id", workspace_id)
            .filter("expires_at", "not.is", "null")
            .lt("expires_at", now.isoformat())
            .execute()
        )
        deleted += len(r1.data) if r1.data else 0

        # 2. Low-confidence memories older than 30 days
        r2 = (
            client.table(TABLE)
            .delete()
            .eq("workspace_id", workspace_id)
            .lt("confidence", 0.3)
            .lt("created_at", cutoff_30d)
            .execute()
        )
        deleted += len(r2.data) if r2.data else 0

        # 3. All memories older than 90 days
        r3 = (
            client.table(TABLE)
            .delete()
            .eq("workspace_id", workspace_id)
            .lt("created_at", cutoff_90d)
            .execute()
        )
        deleted += len(r3.data) if r3.data else 0

        if deleted:
            bcm_cache.invalidate(workspace_id)
            logger.info("Cleaned up %d old memories for workspace %s", deleted, workspace_id)
    except Exception as exc:
        logger.warning("Memory cleanup failed for workspace %s: %s", workspace_id, exc)

    return deleted
