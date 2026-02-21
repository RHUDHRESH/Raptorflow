"""
BCM event store and memory promotion helpers for the AI Hub.

This implementation is resilient: if Supabase is unavailable, it uses
in-memory fallback storage so runtime requests still complete.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.core.database.supabase import get_supabase_client

logger = logging.getLogger(__name__)

TABLE_EVENTS = "bcm_events"
TABLE_MEMORY_CANDIDATES = "bcm_memory_candidates"
TABLE_MEMORY_PROMOTED = "bcm_memory_promoted"


class BCMEventStore:
    def __init__(self) -> None:
        self._fallback_events: List[Dict[str, Any]] = []
        self._fallback_candidates: Dict[str, Dict[str, Any]] = {}
        self._fallback_promoted: Dict[str, Dict[str, Any]] = {}

    def _event_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def append_event(
        self,
        *,
        workspace_id: str,
        event_type: str,
        payload: Dict[str, Any],
        actor: str = "ai_hub",
        quality_score: Optional[float] = None,
        safety_verdict: Optional[str] = None,
        causation: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        row = {
            "event_id": str(uuid4()),
            "workspace_id": workspace_id,
            "event_type": event_type,
            "payload": payload,
            "actor": actor,
            "quality_score": quality_score,
            "safety_verdict": safety_verdict,
            "causation": causation or {},
            "created_at": self._event_now(),
        }

        try:
            client = get_supabase_client()
            result = client.table(TABLE_EVENTS).insert(row).execute()
            if result.data:
                return result.data[0]
        except Exception as exc:
            logger.warning("BCM event append fell back to in-memory storage: %s", exc)

        self._fallback_events.append(row)
        return row

    def list_recent_events(self, workspace_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        try:
            client = get_supabase_client()
            result = (
                client.table(TABLE_EVENTS)
                .select("*")
                .eq("workspace_id", workspace_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return result.data or []
        except Exception:
            rows = [e for e in self._fallback_events if e.get("workspace_id") == workspace_id]
            return list(reversed(rows[-limit:]))

    def create_memory_candidate(
        self,
        *,
        workspace_id: str,
        run_id: str,
        memory: Dict[str, Any],
        confidence: float,
        quality_gate: Dict[str, Any],
    ) -> Dict[str, Any]:
        row = {
            "candidate_id": str(uuid4()),
            "workspace_id": workspace_id,
            "run_id": run_id,
            "memory": memory,
            "confidence": confidence,
            "quality_gate": quality_gate,
            "status": "candidate",
            "created_at": self._event_now(),
        }

        try:
            client = get_supabase_client()
            result = client.table(TABLE_MEMORY_CANDIDATES).insert(row).execute()
            if result.data:
                stored = result.data[0]
                self._fallback_candidates[stored["candidate_id"]] = stored
                return stored
        except Exception as exc:
            logger.warning("Memory candidate persisted in fallback mode: %s", exc)

        self._fallback_candidates[row["candidate_id"]] = row
        return row

    def promote_candidate(
        self,
        *,
        workspace_id: str,
        candidate_id: str,
        promoted_reason: str,
        quality_score: float,
    ) -> Dict[str, Any]:
        candidate = self._fallback_candidates.get(candidate_id, {})
        promoted = {
            "memory_id": str(uuid4()),
            "workspace_id": workspace_id,
            "candidate_id": candidate_id,
            "memory": candidate.get("memory", {}),
            "quality_score": quality_score,
            "promoted_reason": promoted_reason,
            "created_at": self._event_now(),
        }

        try:
            client = get_supabase_client()
            result = client.table(TABLE_MEMORY_PROMOTED).insert(promoted).execute()
            if result.data:
                promoted = result.data[0]
            client.table(TABLE_MEMORY_CANDIDATES).update({"status": "promoted"}).eq(
                "candidate_id", candidate_id
            ).eq("workspace_id", workspace_id).execute()
        except Exception as exc:
            logger.warning("Memory promotion fallback mode: %s", exc)

        self._fallback_promoted[promoted["memory_id"]] = promoted
        if candidate:
            candidate["status"] = "promoted"
        return promoted

    def reject_candidate(
        self,
        *,
        workspace_id: str,
        candidate_id: str,
        reason: str,
    ) -> Dict[str, Any]:
        rejected = {
            "workspace_id": workspace_id,
            "candidate_id": candidate_id,
            "status": "rejected",
            "reason": reason,
            "updated_at": self._event_now(),
        }
        try:
            client = get_supabase_client()
            client.table(TABLE_MEMORY_CANDIDATES).update(
                {"status": "rejected", "rejection_reason": reason}
            ).eq("candidate_id", candidate_id).eq("workspace_id", workspace_id).execute()
        except Exception:
            pass

        candidate = self._fallback_candidates.get(candidate_id)
        if candidate:
            candidate["status"] = "rejected"
            candidate["rejection_reason"] = reason
        return rejected

