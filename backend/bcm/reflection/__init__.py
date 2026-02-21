"""
BCM Reflection Client - Self-improvement through feedback analysis.

Analyzes generation logs and feedback to identify patterns and improve
future content generation.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

GENERATION_TABLE = "bcm_generation_log"
REFLECTION_THRESHOLD = 20


class ReflectionClient:
    """
    Client for running reflection cycles.

    Reflection analyzes recent generations and feedback to:
    - Identify patterns in what works/doesn't work
    - Update guardrails and vocabulary
    - Create new memories from insights
    - Trigger BCM rebuilds with enriched data

    Example:
        client = ReflectionClient()

        # Check if reflection should run
        if client.should_reflect(workspace_id="ws_123"):
            result = await client.reflect(workspace_id="ws_123")
            print(f"Created {result['memories_created']} new memories")
    """

    def __init__(
        self,
        bcm_client: Optional[Any] = None,
        memory_client: Optional[Any] = None,
        db_client: Optional[Any] = None,
    ):
        self._bcm = bcm_client
        self._memory = memory_client
        self._db = db_client

    def _get_bcm(self):
        if self._bcm is None:
            from backend.bcm.core import get_bcm_client

            self._bcm = get_bcm_client()
        return self._bcm

    def _get_memory(self):
        if self._memory is None:
            from backend.bcm.memory import get_memory_client

            self._memory = get_memory_client()
        return self._memory

    def _get_db(self):
        if self._db is None:
            from backend.core.database.supabase import get_supabase_client

            self._db = get_supabase_client()
        return self._db

    def should_reflect(self, workspace_id: str) -> bool:
        """
        Check if a workspace has enough new generations to trigger reflection.

        Args:
            workspace_id: Workspace identifier

        Returns:
            True if reflection should run
        """
        bcm = self._get_bcm()
        db = self._get_db()

        bcm_row = bcm.get_latest(workspace_id)
        if not bcm_row:
            return False

        manifest = bcm_row.get("manifest", {})
        last_reflection = manifest.get("meta", {}).get("last_reflection_at")

        if not last_reflection:
            rated = self._get_rated_generations(workspace_id, limit=1)
            all_gens = self._get_recent_generations(
                workspace_id, limit=REFLECTION_THRESHOLD + 1
            )
            return len(all_gens) >= REFLECTION_THRESHOLD and len(rated) > 0

        recent = self._get_recent_generations(
            workspace_id,
            limit=REFLECTION_THRESHOLD + 1,
        )
        new_since = [g for g in recent if g.get("created_at", "") > last_reflection]
        return len(new_since) >= REFLECTION_THRESHOLD

    def _get_rated_generations(
        self,
        workspace_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get generations that have user feedback."""
        db = self._get_db()
        result = (
            db.table(GENERATION_TABLE)
            .select("*")
            .eq("workspace_id", workspace_id)
            .not_.is_("feedback_score", "null")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    def _get_recent_generations(
        self,
        workspace_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get recent generations for a workspace."""
        db = self._get_db()
        result = (
            db.table(GENERATION_TABLE)
            .select("*")
            .eq("workspace_id", workspace_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    async def reflect(self, workspace_id: str) -> Dict[str, Any]:
        """
        Run a reflection cycle for a workspace.

        Process:
        1. Fetch recent rated generations
        2. Fetch current BCM identity
        3. Send to AI for analysis
        4. Store insights as memories
        5. Update BCM with reflection timestamp

        Args:
            workspace_id: Workspace identifier

        Returns:
            Summary of what was learned
        """
        bcm = self._get_bcm()
        memory = self._get_memory()

        try:
            memory.cleanup_old_memories(workspace_id)
            self._cleanup_old_generations(workspace_id)
        except Exception as exc:
            logger.warning("Cleanup failed during reflection: %s", exc)

        rated = self._get_rated_generations(workspace_id, limit=20)
        if not rated:
            return {"status": "skipped", "reason": "No rated generations to reflect on"}

        bcm_row = bcm.get_latest(workspace_id)
        manifest = bcm_row["manifest"] if bcm_row else {}
        identity = manifest.get("identity", {})

        gen_summaries = []
        for g in rated:
            gen_summaries.append(
                {
                    "content_type": g.get("content_type", ""),
                    "output_preview": (g.get("output", ""))[:300],
                    "feedback_score": g.get("feedback_score"),
                    "user_edits": g.get("user_edits", ""),
                }
            )

        from backend.bcm.prompts import REFLECTION_PROMPT

        prompt = REFLECTION_PROMPT.format(
            generations_json=json.dumps(gen_summaries, indent=2),
            identity_json=json.dumps(identity, indent=2) if identity else "{}",
        )

        try:
            from backend.ai import get_client

            client = get_client()
            await client.initialize()

            result = await client.generate(
                prompt=prompt,
                workspace_id=workspace_id,
                user_id="bcm_reflector",
                max_tokens=2000,
                temperature=0.3,
            )

            if not result.success:
                return {"status": "error", "reason": result.error}

            parsed = self._parse_reflection_response(result.text)
            if not parsed:
                return {
                    "status": "error",
                    "reason": "Failed to parse reflection response",
                }

            insights = parsed.get("insights", [])
            memories_created = 0

            for insight in insights:
                try:
                    from backend.bcm.core.types import MemoryType, MemorySource

                    memory.add_memory(
                        workspace_id=workspace_id,
                        memory_type=MemoryType(insight.get("type", "insight")),
                        content={
                            "summary": insight.get("summary", ""),
                            "evidence": insight.get("evidence", ""),
                            "source_data": "reflection",
                        },
                        source=MemorySource.REFLECTION,
                        confidence=insight.get("confidence", 0.5),
                    )
                    memories_created += 1
                except Exception as exc:
                    logger.warning("Failed to store reflection insight: %s", exc)

            guardrail_updates = parsed.get("updated_guardrails", {})
            if any(
                guardrail_updates.get(k)
                for k in ("add_positive", "add_negative", "remove")
            ):
                try:
                    from backend.bcm.core.types import MemoryType, MemorySource

                    memory.add_memory(
                        workspace_id=workspace_id,
                        memory_type=MemoryType.PATTERN,
                        content={
                            "summary": "Guardrail updates from reflection",
                            "guardrail_updates": guardrail_updates,
                        },
                        source=MemorySource.REFLECTION,
                        confidence=0.7,
                    )
                    memories_created += 1
                except Exception as exc:
                    logger.warning("Failed to store guardrail update: %s", exc)

            voice_updates = parsed.get("voice_refinements", {})
            if any(
                voice_updates.get(k) for k in ("add_vocabulary", "add_anti_vocabulary")
            ):
                try:
                    from backend.bcm.core.types import MemoryType, MemorySource

                    memory.add_memory(
                        workspace_id=workspace_id,
                        memory_type=MemoryType.PREFERENCE,
                        content={
                            "summary": "Voice refinements from reflection",
                            "voice_updates": voice_updates,
                        },
                        source=MemorySource.REFLECTION,
                        confidence=0.6,
                    )
                    memories_created += 1
                except Exception as exc:
                    logger.warning("Failed to store voice update: %s", exc)

            try:
                source = bcm_row.get("source_context")
                if source:
                    new_version = manifest.get("version", 0) + 1
                    new_manifest = await bcm._synthesize(
                        business_context=source,
                        workspace_id=workspace_id,
                        version=new_version,
                        source="reflection",
                    )
                    new_manifest["meta"]["last_reflection_at"] = datetime.now(
                        timezone.utc
                    ).isoformat()
                    new_manifest["meta"]["memory_count"] = memory.get_summary(
                        workspace_id
                    ).get("total_count", 0)

                    new_manifest["checksum"] = ""
                    manifest_json = json.dumps(
                        new_manifest, sort_keys=True, separators=(",", ":")
                    )
                    new_manifest["checksum"] = hashlib.sha256(
                        manifest_json.encode()
                    ).hexdigest()[:16]
                    new_manifest["meta"]["token_estimate"] = len(manifest_json) // 4

                    from backend.services import bcm_cache

                    bcm_cache.invalidate(workspace_id)
                    bcm.store_manifest(workspace_id, new_manifest, source)
            except Exception as exc:
                logger.warning("Failed to rebuild BCM after reflection: %s", exc)

            logger.info(
                "Reflection complete for workspace %s: %d insights, %d memories created",
                workspace_id,
                len(insights),
                memories_created,
            )

            return {
                "status": "success",
                "insights_found": len(insights),
                "memories_created": memories_created,
                "guardrail_updates": bool(
                    any(
                        guardrail_updates.get(k)
                        for k in ("add_positive", "add_negative", "remove")
                    )
                ),
                "voice_updates": bool(
                    any(
                        voice_updates.get(k)
                        for k in ("add_vocabulary", "add_anti_vocabulary")
                    )
                ),
                "generations_analyzed": len(rated),
            }

        except Exception as exc:
            logger.error("Reflection failed: %s", exc, exc_info=True)
            return {"status": "error", "reason": str(exc)}

    def _parse_reflection_response(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from model response."""
        text = raw_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            start = 1
            end = len(lines) - 1
            for i in range(len(lines) - 1, 0, -1):
                if lines[i].strip() == "```":
                    end = i
                    break
            text = "\n".join(lines[start:end])

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            brace_start = text.find("{")
            brace_end = text.rfind("}")
            if brace_start != -1 and brace_end != -1:
                try:
                    return json.loads(text[brace_start : brace_end + 1])
                except json.JSONDecodeError:
                    pass
        return None

    def _cleanup_old_generations(self, workspace_id: str) -> int:
        """Clean up old generation logs."""
        db = self._get_db()
        from datetime import timedelta

        cutoff = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()

        result = (
            db.table(GENERATION_TABLE)
            .delete()
            .eq("workspace_id", workspace_id)
            .lt("created_at", cutoff)
            .execute()
        )
        deleted = len(result.data) if result.data else 0
        if deleted:
            logger.info(
                "Cleaned up %d old generation logs for workspace %s",
                deleted,
                workspace_id,
            )
        return deleted


_reflection_client: Optional[ReflectionClient] = None


def get_reflection_client() -> ReflectionClient:
    """Get the global reflection client instance."""
    global _reflection_client
    if _reflection_client is None:
        _reflection_client = ReflectionClient()
    return _reflection_client


__all__ = [
    "ReflectionClient",
    "get_reflection_client",
]
