"""
BCM Manifest Service

Builds BCM manifests from onboarding sessions and business_contexts,
then persists them into the bcm_manifests table with versioning.
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..integration.bcm_reducer import BCMReducer
from ..core.supabase_mgr import get_supabase_admin

logger = logging.getLogger(__name__)


class BCMManifestService:
    """Service for BCM manifest generation and retrieval."""

    def __init__(self, db_client=None):
        self.db = db_client or get_supabase_admin()
        self.reducer = BCMReducer()

    async def generate_manifest(
        self, workspace_id: str, force: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a BCM manifest from onboarding + business_contexts and persist it.

        Args:
            workspace_id: Workspace identifier
            force: Whether to force regeneration
        """
        latest_record = await self.get_latest_manifest_record(workspace_id)
        if latest_record and not force:
            generated_at = latest_record.get("generated_at")
            if generated_at:
                parsed = datetime.fromisoformat(generated_at)
                if datetime.utcnow() - parsed < timedelta(hours=1):
                    return {
                        "success": False,
                        "reason": "Recent BCM exists, use force=true to override",
                    }

        session_record = await self._get_latest_onboarding_session(workspace_id)
        if not session_record:
            raise ValueError("No onboarding session found for workspace")

        steps_data = await self._get_onboarding_steps(session_record["id"])
        session_data = session_record.get("session_data") or {}
        raw_steps = self._normalize_step_data(steps_data, session_data)

        metadata = session_record.get("metadata") or {}
        metadata.update(
            {
                "workspace_id": workspace_id,
                "user_id": session_record.get("user_id"),
                "session_id": session_record.get("session_id"),
            }
        )

        raw_step_data = {"metadata": metadata, **raw_steps}

        business_context = await self._get_business_context(workspace_id)

        if business_context:
            raw_step_data["business_context"] = business_context

        bcm_manifest = await self.reducer.reduce(raw_step_data)
        manifest_payload = bcm_manifest.dict()

        if business_context:
            manifest_payload["business_context"] = business_context

        checksum = self._compute_checksum(manifest_payload)
        version = await self._next_version(workspace_id)

        await self._store_manifest(
            workspace_id=workspace_id,
            session_id=session_record.get("id"),
            version=version,
            checksum=checksum,
            manifest=manifest_payload,
            generated_at=manifest_payload.get("generated_at"),
        )

        return {
            "success": True,
            "manifest": manifest_payload,
            "version": version,
            "checksum": checksum,
            "generated_at": manifest_payload.get("generated_at"),
        }

    async def get_latest_manifest_record(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Fetch the latest manifest record for a workspace."""
        result = (
            self.db.table("bcm_manifests")
            .select("*")
            .eq("workspace_id", workspace_id)
            .order("version", desc=True)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
        return None

    async def get_manifest(
        self, workspace_id: str, version: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a manifest JSON for a workspace and optional version."""
        query = self.db.table("bcm_manifests").select("*").eq(
            "workspace_id", workspace_id
        )
        if version is not None:
            query = query.eq("version", version)
        else:
            query = query.order("version", desc=True).limit(1)
        result = query.execute()
        if result.data:
            return result.data[0]
        return None

    async def get_version_history(
        self, workspace_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Return version history for a workspace."""
        result = (
            self.db.table("bcm_manifests")
            .select("id, workspace_id, version, checksum, generated_at, created_at")
            .eq("workspace_id", workspace_id)
            .order("version", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    async def _get_latest_onboarding_session(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        result = (
            self.db.table("onboarding_sessions")
            .select("id, session_id, user_id, workspace_id, session_data, metadata, updated_at")
            .eq("workspace_id", workspace_id)
            .order("updated_at", desc=True)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
        return None

    async def _get_onboarding_steps(self, session_id: str) -> List[Dict[str, Any]]:
        result = (
            self.db.table("onboarding_steps")
            .select("step_number, step_name, status, step_data")
            .eq("session_id", session_id)
            .order("step_number", desc=False)
            .execute()
        )
        return result.data or []

    async def _get_business_context(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        result = (
            self.db.table("business_contexts")
            .select("*")
            .eq("workspace_id", workspace_id)
            .order("updated_at", desc=True)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
        return None

    def _normalize_step_data(
        self, steps: List[Dict[str, Any]], session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        if steps:
            normalized: Dict[str, Any] = {}
            for step in steps:
                normalized[f"step_{step['step_number']}"] = {
                    "data": step.get("step_data") or {},
                    "status": step.get("status"),
                    "name": step.get("step_name"),
                }
            return normalized

        session_steps = session_data.get("steps") or session_data.get("step_data") or {}
        normalized = {}
        for key, value in session_steps.items():
            step_key = f"step_{key}" if not str(key).startswith("step_") else str(key)
            if isinstance(value, dict) and "data" in value:
                normalized[step_key] = value
            else:
                normalized[step_key] = {"data": value}
        return normalized

    async def _next_version(self, workspace_id: str) -> int:
        latest = await self.get_latest_manifest_record(workspace_id)
        if not latest:
            return 1
        return int(latest.get("version", 0)) + 1

    async def _store_manifest(
        self,
        workspace_id: str,
        session_id: Optional[str],
        version: int,
        checksum: str,
        manifest: Dict[str, Any],
        generated_at: Optional[str],
    ) -> None:
        record = {
            "workspace_id": workspace_id,
            "session_id": session_id,
            "version": version,
            "checksum": checksum,
            "manifest_json": manifest,
            "generated_at": generated_at or datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        result = self.db.table("bcm_manifests").insert(record).execute()
        if not result.data:
            raise RuntimeError("Failed to persist BCM manifest")

    def _compute_checksum(self, manifest: Dict[str, Any]) -> str:
        serialized = json.dumps(manifest, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()
