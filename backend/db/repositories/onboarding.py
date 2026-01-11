"""
Onboarding Repository for session and evidence management
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..core.supabase import get_supabase_client
from .base import BaseModel, Repository


@dataclass
class OnboardingSession(BaseModel):
    current_step: int = 1
    completed_steps: List[int] = field(default_factory=list)
    step_data: Dict[str, Any] = field(default_factory=dict)
    evidence_items: List[Dict[str, Any]] = field(default_factory=list)
    extracted_facts: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "in_progress"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class OnboardingRepository(Repository[OnboardingSession]):
    """Repository for onboarding sessions and evidence vault"""

    def __init__(self):
        super().__init__("onboarding_sessions")
        self.vault_table = "evidence_vault"

    def _map_to_model(self, data: Dict[str, Any]) -> OnboardingSession:
        return OnboardingSession(
            id=data.get("id"),
            workspace_id=data.get("workspace_id", ""),
            created_at=data.get("started_at"),  # Map started_at to created_at logic
            updated_at=None,
            current_step=data.get("current_step", 1),
            completed_steps=data.get("completed_steps", []),
            step_data=data.get("step_data", {}),
            evidence_items=data.get("evidence_items", []),
            extracted_facts=data.get("extracted_facts", []),
            status=data.get("status", "in_progress"),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
        )

    async def create_session(self, workspace_id: str) -> Optional[OnboardingSession]:
        """Create new onboarding session through Supabase (which generates ID)"""
        # Ensure we don't have duplicates for workspace if unique constraint exists
        # Schema: workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE UNIQUE
        # So we should check or upsert.

        # Check existing
        existing = await self.get_by_workspace(workspace_id)
        if existing:
            return existing

        data = {
            "workspace_id": workspace_id,
            "current_step": 1,
            "status": "in_progress",
            "step_data": {},
        }
        # Repo.create usually sets ID, but here we let DB default gen_random_uuid
        # Base implementation uses self.table().insert().
        result = (
            self._get_supabase_client()
            .table(self.table_name)
            .insert(data)
            .single()
            .execute()
        )
        if result.data:
            return self._map_to_model(result.data)
        return None

    async def get_by_workspace(self, workspace_id: str) -> Optional[OnboardingSession]:
        """Get session by workspace ID"""
        result = (
            self._get_supabase_client()
            .table(self.table_name)
            .select("*")
            .eq("workspace_id", workspace_id)
            .maybe_single()
            .execute()
        )
        if result.data:
            return self._map_to_model(result.data)
        return None

    async def update_step(
        self, session_id: str, step: int, data: Dict[str, Any]
    ) -> Optional[OnboardingSession]:
        """Update step data and current step"""
        # First get current data to merge? JSONB patch works differently.
        # We can fetch first.
        # But step_data is one JSONB blob. We might want to merge `data` into `step_data[step]`.

        # NOTE: Logic from original route: session["steps"][str(step_id)] = { data, version... }
        # Schema has `step_data JSONB`.
        # We should probably store as { "1": {...}, "2": {...} }

        # Fetch current
        result = (
            self._get_supabase_client()
            .table(self.table_name)
            .select("*")
            .eq("id", session_id)
            .single()
            .execute()
        )
        if not result.data:
            return None

        current_data = result.data.get("step_data") or {}
        current_data[str(step)] = {
            "data": data,
            "updated_at": datetime.utcnow().isoformat(),
        }

        update_payload = {
            "current_step": step,  # Advance pointer? Or just update. Assuming context.
            "step_data": current_data,
        }

        res = (
            self._get_supabase_client()
            .table(self.table_name)
            .update(update_payload)
            .eq("id", session_id)
            .single()
            .execute()
        )
        return self._map_to_model(res.data) if res.data else None

    async def add_evidence(
        self, session_id: str, workspace_id: str, evidence_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add item to evidence vault"""
        # Insert into evidence_vault
        vault_entry = {
            "workspace_id": workspace_id,
            "session_id": session_id,
            "source_type": evidence_data.get("type", "file"),  # mapping required
            "source_name": evidence_data.get("filename")
            or evidence_data.get("url")
            or "unknown",
            "file_path": evidence_data.get("filename"),  # or storage path
            "url": evidence_data.get("url"),
            "content": evidence_data.get("extracted_text")
            or evidence_data.get("content"),
            "processing_status": (
                "processed"
                if evidence_data.get("ocr_processed") or evidence_data.get("scraped")
                else "failed"
            ),
            "processed_at": datetime.utcnow().isoformat(),
        }

        res = (
            self._get_supabase_client()
            .table(self.vault_table)
            .insert(vault_entry)
            .single()
            .execute()
        )
        return res.data if res.data else None

    async def get_vault_items(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all evidence items for a session"""
        res = (
            self._get_supabase_client()
            .table(self.vault_table)
            .select("*")
            .eq("session_id", session_id)
            .execute()
        )
        return res.data or []

    async def delete_vault_item(self, item_id: str) -> bool:
        """Delete vault item"""
        res = (
            self._get_supabase_client()
            .table(self.vault_table)
            .delete()
            .eq("id", item_id)
            .execute()
        )
        return True  # logic check needed? Supabase returns count usually.
