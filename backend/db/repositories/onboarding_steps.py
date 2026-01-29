from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from core.supabase_mgr import get_supabase_admin
from .base import Repository


class OnboardingStepsRepository(Repository[Dict[str, Any]]):
    """Repository for onboarding_steps table."""

    def __init__(self) -> None:
        super().__init__("onboarding_steps")

    def _get_supabase_client(self):
        return get_supabase_admin()

    def upsert_step(
        self,
        session_id: str,
        step_number: int,
        step_name: str,
        phase_number: int,
        status: str,
        step_data: Dict[str, Any],
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        is_required: bool = True,
    ) -> Dict[str, Any]:
        def _normalize_datetime(value: Optional[datetime]) -> Optional[str]:
            if isinstance(value, datetime):
                return value.isoformat()
            return value

        payload = {
            "session_id": session_id,
            "step_number": step_number,
            "step_name": step_name,
            "phase_number": phase_number,
            "status": status,
            "step_data": step_data,
            "started_at": _normalize_datetime(started_at),
            "completed_at": _normalize_datetime(completed_at),
            "is_required": is_required,
            "updated_at": datetime.utcnow().isoformat(),
        }
        result = (
            self._get_supabase_client()
            .table(self.table_name)
            .upsert(payload, on_conflict="session_id,step_number")
            .single()
            .execute()
        )
        return result.data or {}

    def get_step(self, session_id: str, step_number: int) -> Optional[Dict[str, Any]]:
        result = (
            self._get_supabase_client()
            .table(self.table_name)
            .select("*")
            .eq("session_id", session_id)
            .eq("step_number", step_number)
            .maybe_single()
            .execute()
        )
        return result.data or None

    def count_completed_steps(self, session_id: str) -> int:
        result = (
            self._get_supabase_client()
            .table(self.table_name)
            .select("id", count="exact")
            .eq("session_id", session_id)
            .eq("status", "complete")
            .execute()
        )
        return result.count or 0
