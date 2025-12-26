import logging
from typing import Any, List, Optional

from memory.short_term import L1ShortTermMemory

logger = logging.getLogger("raptorflow.memory.peer_review")


class PeerReviewMemory:
    """
    Shared memory store for peer critiques across runs.
    Persists critique artifacts in L1 memory for reuse during self-correction.
    """

    def __init__(self, tenant_id: str, workspace_id: Optional[str] = None):
        self.tenant_id = tenant_id
        self.workspace_id = workspace_id or "global"
        self.l1 = L1ShortTermMemory()
        self.key = f"peer_review:{self.tenant_id}:{self.workspace_id}"

    async def append_critiques(
        self, critiques: List[dict], ttl: int = 86400
    ) -> bool:
        if not self.l1.client:
            logger.warning("Peer review memory unavailable; no L1 client.")
            return False
        existing = await self.l1.retrieve(self.key) or []
        updated = existing + critiques
        return await self.l1.store(self.key, updated, ttl=ttl)

    async def get_recent_critiques(self, limit: int = 5) -> List[dict]:
        if not self.l1.client:
            logger.warning("Peer review memory unavailable; no L1 client.")
            return []
        data = await self.l1.retrieve(self.key) or []
        return data[-limit:]

    async def store_snapshot(self, snapshot: Any, ttl: int = 86400) -> bool:
        if not self.l1.client:
            logger.warning("Peer review memory unavailable; no L1 client.")
            return False
        return await self.l1.store(self.key, snapshot, ttl=ttl)
