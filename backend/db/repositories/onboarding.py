"""
Onboarding Repository for session and evidence management
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from backend.core.supabase_mgr import get_supabase_client

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

    async def get_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        result = (
            self._get_supabase_client()
            .table(self.table_name)
            .select("*")
            .eq("id", session_id)
            .maybe_single()
            .execute()
        )
        return result.data if result.data else None

    async def store_evidence_classification(
        self, session_id: str, classification: Dict[str, Any]
    ) -> bool:
        """Store evidence classification result"""
        return await self._store_step_data(
            session_id, "evidence_classification", classification
        )

    async def store_extracted_facts(
        self, session_id: str, facts: List[Dict[str, Any]]
    ) -> bool:
        """Store extracted facts"""
        return await self._store_step_data(
            session_id, "extracted_facts", {"facts": facts}
        )

    async def store_contradictions(
        self, session_id: str, contradictions: List[Dict[str, Any]]
    ) -> bool:
        """Store detected contradictions"""
        return await self._store_step_data(
            session_id, "contradictions", {"contradictions": contradictions}
        )

    async def store_reddit_research(
        self, session_id: str, research: Dict[str, Any]
    ) -> bool:
        """Store Reddit research results"""
        return await self._store_step_data(session_id, "reddit_research", research)

    async def store_perceptual_map(
        self, session_id: str, map_data: Dict[str, Any]
    ) -> bool:
        """Store perceptual map"""
        return await self._store_step_data(session_id, "perceptual_map", map_data)

    async def store_copy_variants(
        self, session_id: str, variants: List[Dict[str, Any]]
    ) -> bool:
        """Store neuroscience copy variants"""
        return await self._store_step_data(
            session_id, "copy_variants", {"variants": variants}
        )

    async def store_channel_strategy(
        self, session_id: str, strategy: Dict[str, Any]
    ) -> bool:
        """Store channel strategy"""
        return await self._store_step_data(session_id, "channel_strategy", strategy)

    async def store_category_paths(
        self, session_id: str, paths: Dict[str, Any]
    ) -> bool:
        """Store category paths analysis"""
        return await self._store_step_data(session_id, "category_paths", paths)

    async def store_market_size(
        self, session_id: str, market_size: Dict[str, Any]
    ) -> bool:
        """Store TAM/SAM/SOM market size data"""
        return await self._store_step_data(session_id, "market_size", market_size)

    async def store_competitor_analysis(
        self, session_id: str, analysis: Dict[str, Any]
    ) -> bool:
        """Store competitor analysis results"""
        return await self._store_step_data(session_id, "competitor_analysis", analysis)

    async def store_focus_sacrifice(
        self, session_id: str, data: Dict[str, Any]
    ) -> bool:
        """Store focus/sacrifice analysis"""
        return await self._store_step_data(session_id, "focus_sacrifice", data)

    async def store_truth_sheet(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Store truth sheet entries"""
        return await self._store_step_data(session_id, "truth_sheet", data)

    async def store_proof_points(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Store proof point validations"""
        return await self._store_step_data(session_id, "proof_points", data)

    async def store_messaging_rules(
        self, session_id: str, data: Dict[str, Any]
    ) -> bool:
        """Store messaging rules"""
        return await self._store_step_data(session_id, "messaging_rules", data)

    async def store_soundbites(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Store soundbites library"""
        return await self._store_step_data(session_id, "soundbites", data)

    async def store_icp_deep(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Store comprehensive ICP profiles"""
        return await self._store_step_data(session_id, "icp_deep", data)

    async def store_positioning(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Store positioning statements"""
        return await self._store_step_data(session_id, "positioning", data)

    async def store_launch_readiness(
        self, session_id: str, data: Dict[str, Any]
    ) -> bool:
        """Store launch readiness checklist"""
        return await self._store_step_data(session_id, "launch_readiness", data)

    async def store_channel_strategy(
        self, session_id: str, data: Dict[str, Any]
    ) -> bool:
        """Store channel strategy"""
        return await self._store_step_data(session_id, "channel_strategy", data)

    async def _store_step_data(self, session_id: str, key: str, data: Any) -> bool:
        """Helper to store data in step_data JSONB"""
        result = (
            self._get_supabase_client()
            .table(self.table_name)
            .select("step_data")
            .eq("id", session_id)
            .single()
            .execute()
        )
        if not result.data:
            return False

        current_data = result.data.get("step_data") or {}
        current_data[key] = {
            "data": data,
            "updated_at": datetime.utcnow().isoformat(),
        }

        res = (
            self._get_supabase_client()
            .table(self.table_name)
            .update({"step_data": current_data})
            .eq("id", session_id)
            .execute()
        )
        return res.data is not None

    async def get_session_progress(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive session progress"""
        result = (
            self._get_supabase_client()
            .table(self.table_name)
            .select("*")
            .eq("id", session_id)
            .single()
            .execute()
        )
        if not result.data:
            return {"error": "Session not found"}

        session = result.data
        step_data = session.get("step_data", {})
        completed_steps = session.get("completed_steps", [])

        return {
            "session_id": session_id,
            "current_step": session.get("current_step", 1),
            "completed_steps": completed_steps,
            "total_steps": 23,
            "progress_percentage": (len(completed_steps) / 23) * 100,
            "status": session.get("status", "in_progress"),
            "has_evidence": "evidence_classification" in step_data,
            "has_facts": "extracted_facts" in step_data,
            "has_contradictions": "contradictions" in step_data,
            "has_research": "reddit_research" in step_data,
            "has_positioning": "perceptual_map" in step_data,
        }

    async def advance_step(self, session_id: str) -> bool:
        """Advance to next step"""
        result = (
            self._get_supabase_client()
            .table(self.table_name)
            .select("current_step, completed_steps")
            .eq("id", session_id)
            .single()
            .execute()
        )
        if not result.data:
            return False

        current = result.data.get("current_step", 1)
        completed = result.data.get("completed_steps", [])

        if current not in completed:
            completed.append(current)

        res = (
            self._get_supabase_client()
            .table(self.table_name)
            .update({"current_step": current + 1, "completed_steps": completed})
            .eq("id", session_id)
            .execute()
        )
        return res.data is not None
