"""
BCM Memory Client - Manages learned preferences and insights.

Memories are workspace-scoped observations that improve content generation over time.
Types: correction, preference, pattern, insight.
Sources: user_feedback, generation_analysis, reflection.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from backend.bcm.core.types import Memory, MemoryType, MemorySource

logger = logging.getLogger(__name__)

TABLE = "bcm_memories"


class MemoryClient:
    """
    Client for managing BCM memories.

    Memories accumulate learnings from:
    - User feedback on generated content
    - Generation analysis patterns
    - Reflection cycles

    Example:
        client = MemoryClient()

        # Record user feedback
        memory = client.record_feedback(
            workspace_id="ws_123",
            generation_id="gen_456",
            score=4,
            edits="Made it more concise",
        )

        # Get relevant memories for generation
        memories = client.get_relevant(workspace_id="ws_123", limit=10)
    """

    def __init__(
        self, db_client: Optional[Any] = None, cache_client: Optional[Any] = None
    ):
        self._db = db_client
        self._cache = cache_client

    def _get_db(self):
        if self._db is None:
            from backend.core.database.supabase import get_supabase_client

            self._db = get_supabase_client()
        return self._db

    def _get_cache(self):
        if self._cache is None:
            from backend.services import bcm_cache

            self._cache = bcm_cache
        return self._cache

    def add_memory(
        self,
        workspace_id: str,
        memory_type: MemoryType,
        content: Dict[str, Any],
        source: MemorySource,
        confidence: float = 0.5,
    ) -> Memory:
        """
        Store a new memory.

        Args:
            workspace_id: Workspace identifier
            memory_type: Type of memory (correction, preference, pattern, insight)
            content: Memory content dictionary
            source: Where this memory came from
            confidence: Confidence level (0.0-1.0)

        Returns:
            Created Memory object
        """
        db = self._get_db()
        cache = self._get_cache()

        row = {
            "workspace_id": workspace_id,
            "memory_type": memory_type.value
            if isinstance(memory_type, MemoryType)
            else memory_type,
            "content": content,
            "source": source.value if isinstance(source, MemorySource) else source,
            "confidence": confidence,
        }

        result = db.table(TABLE).insert(row).execute()
        if result.data:
            cache.invalidate(workspace_id)
            logger.info("Added %s memory for workspace %s", memory_type, workspace_id)
            return Memory.from_dict(result.data[0])
        raise RuntimeError(f"Failed to store memory: {result}")

    def get_relevant(
        self,
        workspace_id: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10,
    ) -> List[Memory]:
        """
        Get recent memories, optionally filtered by type.

        Args:
            workspace_id: Workspace identifier
            memory_type: Optional filter by memory type
            limit: Maximum number of memories to return

        Returns:
            List of Memory objects
        """
        db = self._get_db()
        query = (
            db.table(TABLE)
            .select("*")
            .eq("workspace_id", workspace_id)
            .order("created_at", desc=True)
            .limit(limit)
        )

        if memory_type:
            type_value = (
                memory_type.value
                if isinstance(memory_type, MemoryType)
                else memory_type
            )
            query = query.eq("memory_type", type_value)

        result = query.execute()
        return [Memory.from_dict(row) for row in (result.data or [])]

    def get_summary(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get a summary of all memories for a workspace.

        Args:
            workspace_id: Workspace identifier

        Returns:
            Dictionary with total_count, type_counts, and top_memories
        """
        cache = self._get_cache()
        cached = cache.get_memory_summary(workspace_id)
        if cached:
            return cached

        db = self._get_db()

        all_memories = (
            db.table(TABLE)
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

        cache.set_memory_summary(workspace_id, summary)
        return summary

    def record_feedback(
        self,
        workspace_id: str,
        generation_id: str,
        score: int,
        edits: Optional[str] = None,
    ) -> Memory:
        """
        Record user feedback on a generation and create a memory.

        Args:
            workspace_id: Workspace identifier
            generation_id: Generation log ID
            score: User score (1-5)
            edits: Optional user edits to the output

        Returns:
            Created Memory object
        """
        db = self._get_db()

        gen_check = (
            db.table("bcm_generation_log")
            .select("id")
            .eq("id", generation_id)
            .eq("workspace_id", workspace_id)
            .limit(1)
            .execute()
        )
        if not gen_check.data:
            raise ValueError(
                f"Generation {generation_id} not found or not owned by workspace"
            )

        update_data: Dict[str, Any] = {"feedback_score": score}
        if edits:
            update_data["user_edits"] = edits

        db.table("bcm_generation_log").update(update_data).eq(
            "id", generation_id
        ).execute()

        memory_content: Dict[str, Any] = {
            "generation_id": generation_id,
            "score": score,
        }
        if edits:
            memory_content["user_edits"] = edits
            memory_type = MemoryType.CORRECTION
            memory_content["summary"] = f"User edited output (score: {score}/5)"
        elif score >= 4:
            memory_type = MemoryType.PREFERENCE
            memory_content["summary"] = f"User liked this output (score: {score}/5)"
        else:
            memory_type = MemoryType.CORRECTION
            memory_content["summary"] = f"User disliked this output (score: {score}/5)"

        return self.add_memory(
            workspace_id=workspace_id,
            memory_type=memory_type,
            content=memory_content,
            source=MemorySource.USER_FEEDBACK,
            confidence=score / 5.0,
        )

    def delete(self, workspace_id: str, memory_id: str) -> bool:
        """Delete a specific memory."""
        db = self._get_db()
        cache = self._get_cache()
        result = (
            db.table(TABLE)
            .delete()
            .eq("id", memory_id)
            .eq("workspace_id", workspace_id)
            .execute()
        )
        if result.data:
            cache.invalidate(workspace_id)
            return True
        return False

    def cleanup_old_memories(self, workspace_id: str) -> int:
        """
        Prune stale memories to prevent unbounded growth.

        Deletes:
        - Low-confidence (<0.3) memories older than 30 days
        - All memories older than 90 days
        - Expired memories (expires_at < now)

        Returns:
            Total number of deleted rows
        """
        db = self._get_db()
        cache = self._get_cache()
        now = datetime.now(timezone.utc)
        cutoff_30d = (now - timedelta(days=30)).isoformat()
        cutoff_90d = (now - timedelta(days=90)).isoformat()
        deleted = 0

        try:
            r1 = (
                db.table(TABLE)
                .delete()
                .eq("workspace_id", workspace_id)
                .filter("expires_at", "not.is", "null")
                .lt("expires_at", now.isoformat())
                .execute()
            )
            deleted += len(r1.data) if r1.data else 0

            r2 = (
                db.table(TABLE)
                .delete()
                .eq("workspace_id", workspace_id)
                .lt("confidence", 0.3)
                .lt("created_at", cutoff_30d)
                .execute()
            )
            deleted += len(r2.data) if r2.data else 0

            r3 = (
                db.table(TABLE)
                .delete()
                .eq("workspace_id", workspace_id)
                .lt("created_at", cutoff_90d)
                .execute()
            )
            deleted += len(r3.data) if r3.data else 0

            if deleted:
                cache.invalidate(workspace_id)
                logger.info(
                    "Cleaned up %d old memories for workspace %s", deleted, workspace_id
                )
        except Exception as exc:
            logger.warning(
                "Memory cleanup failed for workspace %s: %s", workspace_id, exc
            )

        return deleted


_memory_client: Optional[MemoryClient] = None


def get_memory_client() -> MemoryClient:
    """Get the global memory client instance."""
    global _memory_client
    if _memory_client is None:
        _memory_client = MemoryClient()
    return _memory_client


__all__ = [
    "MemoryClient",
    "Memory",
    "MemoryType",
    "MemorySource",
    "get_memory_client",
]
