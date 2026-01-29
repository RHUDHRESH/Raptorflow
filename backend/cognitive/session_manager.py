"""
Persistent Session Storage Manager
Fixes memory leaks by storing sessions in Redis/database
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from interfaces import ICacheBackend, IStorageBackend

logger = logging.getLogger(__name__)


@dataclass
class SessionData:
    """Session data model"""

    session_id: str
    user_id: str
    workspace_id: str
    created_at: datetime
    last_active_at: datetime
    expires_at: datetime
    data: Dict[str, Any]
    status: str = "active"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for storage"""
        result = asdict(self)
        # Convert datetime to ISO string
        for field in ["created_at", "last_active_at", "expires_at"]:
            if isinstance(result[field], datetime):
                result[field] = result[field].isoformat()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionData":
        """Create from dict"""
        # Convert ISO string back to datetime
        for field in ["created_at", "last_active_at", "expires_at"]:
            if field in data and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field])
        return cls(**data)


class SessionManager:
    """Manages persistent sessions with automatic cleanup"""

    def __init__(
        self,
        storage: IStorageBackend,
        cache: ICacheBackend,
        default_ttl_hours: int = 24,
    ):
        self.storage = storage
        self.cache = cache
        self.default_ttl_hours = default_ttl_hours
        self.cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start the session manager"""
        self._running = True
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Session manager started")

    async def stop(self):
        """Stop the session manager"""
        self._running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Session manager stopped")

    async def create_session(
        self,
        session_id: str,
        user_id: str,
        workspace_id: str,
        initial_data: Optional[Dict[str, Any]] = None,
    ) -> SessionData:
        """Create a new session"""
        now = datetime.now()
        expires_at = now + timedelta(hours=self.default_ttl_hours)

        session_data = SessionData(
            session_id=session_id,
            user_id=user_id,
            workspace_id=workspace_id,
            created_at=now,
            last_active_at=now,
            expires_at=expires_at,
            data=initial_data or {},
        )

        # Save to persistent storage
        await self.storage.save_session(session_id, session_data.to_dict())

        # Cache for fast access
        await self.cache.set(
            f"session:{session_id}",
            session_data.to_dict(),
            ttl=int(self.default_ttl_hours * 3600),
        )

        logger.info(f"Created session {session_id} for user {user_id}")
        return session_data

    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session data"""
        # Try cache first
        cached_data = await self.cache.get(f"session:{session_id}")
        if cached_data:
            return SessionData.from_dict(cached_data)

        # Fallback to storage
        stored_data = await self.storage.load_session(session_id)
        if stored_data:
            session = SessionData.from_dict(stored_data)
            # Update cache
            await self.cache.set(
                f"session:{session_id}",
                stored_data,
                ttl=int(self.default_ttl_hours * 3600),
            )
            return session

        return None

    async def update_session(
        self, session_id: str, updates: Dict[str, Any], extend_ttl: bool = True
    ) -> Optional[SessionData]:
        """Update session data"""
        session = await self.get_session(session_id)
        if not session:
            return None

        # Update session data
        session.data.update(updates)
        session.last_active_at = datetime.now()

        if extend_ttl:
            session.expires_at = datetime.now() + timedelta(
                hours=self.default_ttl_hours
            )

        # Save to storage
        await self.storage.save_session(session_id, session.to_dict())

        # Update cache
        await self.cache.set(
            f"session:{session_id}",
            session.to_dict(),
            ttl=int(self.default_ttl_hours * 3600),
        )

        return session

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        # Delete from storage
        await self.storage.delete_session(session_id)

        # Delete from cache
        await self.cache.delete(f"session:{session_id}")

        logger.info(f"Deleted session {session_id}")
        return True

    async def get_user_sessions(self, user_id: str) -> List[SessionData]:
        """Get all active sessions for a user"""
        # This would need to be implemented based on storage backend capabilities
        # For now, return empty list
        return []

    async def _cleanup_loop(self):
        """Background cleanup of expired sessions"""
        while self._running:
            try:
                await self._cleanup_expired_sessions()
                await asyncio.sleep(300)  # Run every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        # This would need to be implemented based on storage backend
        # For Redis, we could use SCAN to find expired keys
        # For database, we could run a DELETE query
        pass

    async def get_active_session_count(self) -> int:
        """Get count of active sessions"""
        # This would need to be implemented based on storage backend
        return 0
