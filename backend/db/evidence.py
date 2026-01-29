"""
Evidence Repository - Placeholder to fix import errors
"""

from typing import Any, Dict, List, Optional
from .core.supabase_mgr import get_supabase_client


class EvidenceRepository:
    def __init__(self):
        self.table_name = "evidence_vault"
        self.supabase = get_supabase_client()

    async def list_by_session(
        self, workspace_id: str, session_id: str
    ) -> List[Dict[str, Any]]:
        return []

    async def get_by_id(
        self, evidence_id: str, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        return None

    async def add_evidence(
        self,
        workspace_id: str,
        session_id: str,
        source_type: str,
        source_name: str,
        content: str,
    ) -> Dict[str, Any]:
        return {}

    async def mark_processed(
        self, evidence_id: str, key_topics: List[str]
    ) -> Dict[str, Any]:
        return {}

    async def get_file_record(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        return None

    async def update_file_record(self, file_record: Dict[str, Any]) -> bool:
        return True
