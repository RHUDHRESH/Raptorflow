"""
Working memory system for agent context management.
"""

import asyncio
import json
import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from backend.agents.exceptions import DatabaseError, ValidationError, WorkspaceError
from .redis_client import get_redis_client

logger = logging.getLogger(__name__)


@dataclass
class MemoryItem:
    """Single memory item with metadata."""

    key: str
    value: Any
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemorySession:
    """Memory session for tracking agent interactions."""

    session_id: str
    workspace_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    items: Dict[str, MemoryItem] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    agent_history: List[Dict[str, Any]] = field(default_factory=list)
    expires_at: Optional[datetime] = None


class WorkingMemory:
    """Working memory system for agent context management."""

    def __init__(self):
        self.redis_client = None
        self.default_ttl = 3600  # 1 hour
        self.session_ttl = 86400  # 24 hours
        self.max_session_items = 1000
        self.max_agent_history = 50

        # In-memory cache for frequently accessed sessions
        self._session_cache: Dict[str, MemorySession] = {}
        self._cache_max_size = 100
        self._cache_access_times: Dict[str, datetime] = {}

    async def initialize(self):
        """Initialize working memory system."""
        try:
            self.redis_client = await get_redis_client()
            logger.info("Working memory initialized")
        except Exception as e:
            logger.error(f"Failed to initialize working memory: {e}")
            raise DatabaseError(f"Working memory initialization failed: {str(e)}")

    async def create_session(
        self,
        session_id: str,
        workspace_id: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None,
    ) -> MemorySession:
        """Create a new memory session."""
        try:
            # Validate inputs
            if not session_id or not workspace_id or not user_id:
                raise ValidationError(
                    "Session ID, workspace ID, and user ID are required"
                )

            # Create session
            session = MemorySession(
                session_id=session_id,
                workspace_id=workspace_id,
                user_id=user_id,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                context=context or {},
                expires_at=datetime.now() + timedelta(seconds=ttl or self.session_ttl),
            )

            # Store in Redis
            await self._store_session(session)

            # Add to cache
            self._add_to_cache(session)

            logger.info(
                f"Created memory session {session_id} for workspace {workspace_id}"
            )
            return session

        except Exception as e:
            logger.error(f"Failed to create memory session: {e}")
            raise DatabaseError(f"Memory session creation failed: {str(e)}")

    async def get_session(
        self, session_id: str, workspace_id: str, user_id: str
    ) -> Optional[MemorySession]:
        """Get a memory session."""
        try:
            # Check cache first
            cache_key = f"{workspace_id}:{user_id}:{session_id}"
            if cache_key in self._session_cache:
                session = self._session_cache[cache_key]
                self._cache_access_times[cache_key] = datetime.now()
                return session

            # Load from Redis
            session_data = await self.redis_client.get(
                f"session:{session_id}", workspace_id=workspace_id
            )

            if not session_data:
                return None

            # Deserialize session
            session = self._deserialize_session(session_data)

            # Validate session
            if session.workspace_id != workspace_id or session.user_id != user_id:
                logger.warning(f"Session {session_id} workspace/user mismatch")
                return None

            # Check if expired
            if session.expires_at and datetime.now() > session.expires_at:
                await self.delete_session(session_id, workspace_id, user_id)
                return None

            # Add to cache
            self._add_to_cache(session)

            return session

        except Exception as e:
            logger.error(f"Failed to get memory session: {e}")
            raise DatabaseError(f"Memory session retrieval failed: {str(e)}")

    async def update_session(self, session: MemorySession) -> bool:
        """Update a memory session."""
        try:
            # Update timestamps
            session.last_activity = datetime.now()

            # Limit items
            if len(session.items) > self.max_session_items:
                # Remove oldest items
                sorted_items = sorted(
                    session.items.items(),
                    key=lambda x: x[1].last_accessed or x[1].created_at,
                )
                items_to_remove = len(session.items) - self.max_session_items

                for i, (key, _) in enumerate(sorted_items[:items_to_remove]):
                    del session.items[key]

            # Limit agent history
            if len(session.agent_history) > self.max_agent_history:
                session.agent_history = session.agent_history[-self.max_agent_history :]

            # Store in Redis
            await self._store_session(session)

            # Update cache
            cache_key = f"{session.workspace_id}:{session.user_id}:{session.session_id}"
            if cache_key in self._session_cache:
                self._session_cache[cache_key] = session
                self._cache_access_times[cache_key] = datetime.now()

            return True

        except Exception as e:
            logger.error(f"Failed to update memory session: {e}")
            raise DatabaseError(f"Memory session update failed: {str(e)}")

    async def delete_session(
        self, session_id: str, workspace_id: str, user_id: str
    ) -> bool:
        """Delete a memory session."""
        try:
            # Delete from Redis
            deleted = await self.redis_client.delete(
                f"session:{session_id}", workspace_id=workspace_id
            )

            # Remove from cache
            cache_key = f"{workspace_id}:{user_id}:{session_id}"
            if cache_key in self._session_cache:
                del self._session_cache[cache_key]
                del self._cache_access_times[cache_key]

            logger.info(f"Deleted memory session {session_id}")
            return deleted

        except Exception as e:
            logger.error(f"Failed to delete memory session: {e}")
            raise DatabaseError(f"Memory session deletion failed: {str(e)}")

    async def set_item(
        self,
        session_id: str,
        workspace_id: str,
        user_id: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Set a memory item in a session."""
        try:
            # Get session
            session = await self.get_session(session_id, workspace_id, user_id)
            if not session:
                raise ValidationError(f"Session {session_id} not found")

            # Create memory item
            now = datetime.now()
            memory_item = MemoryItem(
                key=key,
                value=value,
                created_at=now,
                updated_at=now,
                expires_at=now + timedelta(seconds=ttl) if ttl else None,
                tags=tags or [],
                metadata=metadata or {},
            )

            # Add to session
            session.items[key] = memory_item

            # Update session
            await self.update_session(session)

            return True

        except Exception as e:
            logger.error(f"Failed to set memory item: {e}")
            raise DatabaseError(f"Memory item set failed: {str(e)}")

    async def get_item(
        self, session_id: str, workspace_id: str, user_id: str, key: str
    ) -> Optional[Any]:
        """Get a memory item from a session."""
        try:
            # Get session
            session = await self.get_session(session_id, workspace_id, user_id)
            if not session:
                return None

            # Get item
            item = session.items.get(key)
            if not item:
                return None

            # Check if expired
            if item.expires_at and datetime.now() > item.expires_at:
                await self.delete_item(session_id, workspace_id, user_id, key)
                return None

            # Update access stats
            item.access_count += 1
            item.last_accessed = datetime.now()

            # Update session
            await self.update_session(session)

            return item.value

        except Exception as e:
            logger.error(f"Failed to get memory item: {e}")
            raise DatabaseError(f"Memory item retrieval failed: {str(e)}")

    async def delete_item(
        self, session_id: str, workspace_id: str, user_id: str, key: str
    ) -> bool:
        """Delete a memory item from a session."""
        try:
            # Get session
            session = await self.get_session(session_id, workspace_id, user_id)
            if not session:
                return False

            # Delete item
            deleted = key in session.items
            if deleted:
                del session.items[key]
                await self.update_session(session)

            return deleted

        except Exception as e:
            logger.error(f"Failed to delete memory item: {e}")
            raise DatabaseError(f"Memory item deletion failed: {str(e)}")

    async def set_context(
        self, session_id: str, workspace_id: str, user_id: str, context: Dict[str, Any]
    ) -> bool:
        """Set context for a session."""
        try:
            # Get session
            session = await self.get_session(session_id, workspace_id, user_id)
            if not session:
                raise ValidationError(f"Session {session_id} not found")

            # Update context
            session.context.update(context)

            # Update session
            await self.update_session(session)

            return True

        except Exception as e:
            logger.error(f"Failed to set session context: {e}")
            raise DatabaseError(f"Session context set failed: {str(e)}")

    async def get_context(
        self, session_id: str, workspace_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Get context for a session."""
        try:
            # Get session
            session = await self.get_session(session_id, workspace_id, user_id)
            if not session:
                return {}

            return session.context.copy()

        except Exception as e:
            logger.error(f"Failed to get session context: {e}")
            raise DatabaseError(f"Session context retrieval failed: {str(e)}")

    async def add_agent_history(
        self,
        session_id: str,
        workspace_id: str,
        user_id: str,
        agent_name: str,
        action: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Add agent action to session history."""
        try:
            # Get session
            session = await self.get_session(session_id, workspace_id, user_id)
            if not session:
                raise ValidationError(f"Session {session_id} not found")

            # Add to history
            history_item = {
                "timestamp": datetime.now().isoformat(),
                "agent_name": agent_name,
                "action": action,
                "data": data or {},
            }

            session.agent_history.append(history_item)

            # Update session
            await self.update_session(session)

            return True

        except Exception as e:
            logger.error(f"Failed to add agent history: {e}")
            raise DatabaseError(f"Agent history addition failed: {str(e)}")

    async def get_agent_history(
        self, session_id: str, workspace_id: str, user_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get agent history for a session."""
        try:
            # Get session
            session = await self.get_session(session_id, workspace_id, user_id)
            if not session:
                return []

            # Return recent history
            return session.agent_history[-limit:]

        except Exception as e:
            logger.error(f"Failed to get agent history: {e}")
            raise DatabaseError(f"Agent history retrieval failed: {str(e)}")

    async def cleanup_expired_sessions(self, workspace_id: str) -> int:
        """Clean up expired sessions for a workspace."""
        try:
            # Get all session keys for workspace
            session_keys = await self.redis_client.keys(
                "session:*", workspace_id=workspace_id
            )

            cleaned_count = 0
            for session_key in session_keys:
                session_id = session_key.replace("session:", "")

                # Get session
                session = await self.get_session(session_id, workspace_id, "")
                if (
                    session
                    and session.expires_at
                    and datetime.now() > session.expires_at
                ):
                    await self.delete_session(session_id, workspace_id, "")
                    cleaned_count += 1

            logger.info(
                f"Cleaned up {cleaned_count} expired sessions for workspace {workspace_id}"
            )
            return cleaned_count

        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            raise DatabaseError(f"Session cleanup failed: {str(e)}")

    async def get_workspace_stats(self, workspace_id: str) -> Dict[str, Any]:
        """Get memory statistics for a workspace."""
        try:
            # Get all session keys for workspace
            session_keys = await self.redis_client.keys(
                "session:*", workspace_id=workspace_id
            )

            stats = {
                "total_sessions": len(session_keys),
                "active_sessions": 0,
                "total_items": 0,
                "total_agent_history": 0,
                "oldest_session": None,
                "newest_session": None,
            }

            if session_keys:
                session_data = []
                oldest_time = None
                newest_time = None

                for session_key in session_keys:
                    session_id = session_key.replace("session:", "")
                    session = await self.get_session(session_id, workspace_id, "")

                    if session:
                        session_data.append(session)

                        # Check if expired
                        if (
                            not session.expires_at
                            or datetime.now() <= session.expires_at
                        ):
                            stats["active_sessions"] += 1

                        stats["total_items"] += len(session.items)
                        stats["total_agent_history"] += len(session.agent_history)

                        # Track oldest/newest
                        if oldest_time is None or session.created_at < oldest_time:
                            oldest_time = session.created_at
                        if newest_time is None or session.created_at > newest_time:
                            newest_time = session.created_at

                stats["oldest_session"] = (
                    oldest_time.isoformat() if oldest_time else None
                )
                stats["newest_session"] = (
                    newest_time.isoformat() if newest_time else None
                )

            return stats

        except Exception as e:
            logger.error(f"Failed to get workspace stats: {e}")
            raise DatabaseError(f"Workspace stats retrieval failed: {str(e)}")

    def _store_session(self, session: MemorySession):
        """Store session in Redis."""
        session_data = self._serialize_session(session)
        return asyncio.create_task(
            self.redis_client.set(
                f"session:{session.session_id}",
                session_data,
                ttl=(
                    int((session.expires_at - datetime.now()).total_seconds())
                    if session.expires_at
                    else None
                ),
                workspace_id=session.workspace_id,
            )
        )

    def _serialize_session(self, session: MemorySession) -> Dict[str, Any]:
        """Serialize session to dictionary."""
        return {
            "session_id": session.session_id,
            "workspace_id": session.workspace_id,
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "expires_at": (
                session.expires_at.isoformat() if session.expires_at else None
            ),
            "items": {
                key: {
                    "key": item.key,
                    "value": item.value,
                    "created_at": item.created_at.isoformat(),
                    "updated_at": item.updated_at.isoformat(),
                    "expires_at": (
                        item.expires_at.isoformat() if item.expires_at else None
                    ),
                    "access_count": item.access_count,
                    "last_accessed": (
                        item.last_accessed.isoformat() if item.last_accessed else None
                    ),
                    "tags": item.tags,
                    "metadata": item.metadata,
                }
                for key, item in session.items.items()
            },
            "context": session.context,
            "agent_history": session.agent_history,
        }

    def _deserialize_session(self, data: Dict[str, Any]) -> MemorySession:
        """Deserialize session from dictionary."""
        items = {}
        for key, item_data in data.get("items", {}).items():
            items[key] = MemoryItem(
                key=item_data["key"],
                value=item_data["value"],
                created_at=datetime.fromisoformat(item_data["created_at"]),
                updated_at=datetime.fromisoformat(item_data["updated_at"]),
                expires_at=(
                    datetime.fromisoformat(item_data["expires_at"])
                    if item_data.get("expires_at")
                    else None
                ),
                access_count=item_data.get("access_count", 0),
                last_accessed=(
                    datetime.fromisoformat(item_data["last_accessed"])
                    if item_data.get("last_accessed")
                    else None
                ),
                tags=item_data.get("tags", []),
                metadata=item_data.get("metadata", {}),
            )

        return MemorySession(
            session_id=data["session_id"],
            workspace_id=data["workspace_id"],
            user_id=data["user_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            expires_at=(
                datetime.fromisoformat(data["expires_at"])
                if data.get("expires_at")
                else None
            ),
            items=items,
            context=data.get("context", {}),
            agent_history=data.get("agent_history", []),
        )

    def _add_to_cache(self, session: MemorySession):
        """Add session to cache with LRU eviction."""
        cache_key = f"{session.workspace_id}:{session.user_id}:{session.session_id}"

        # Remove oldest if cache is full
        if len(self._session_cache) >= self._cache_max_size:
            oldest_key = min(self._cache_access_times.items(), key=lambda x: x[1])[0]

            if oldest_key in self._session_cache:
                del self._session_cache[oldest_key]
            if oldest_key in self._cache_access_times:
                del self._cache_access_times[oldest_key]

        # Add to cache
        self._session_cache[cache_key] = session
        self._cache_access_times[cache_key] = datetime.now()


# Global working memory instance
_working_memory: Optional[WorkingMemory] = None


async def get_working_memory() -> WorkingMemory:
    """Get or create working memory instance."""
    global _working_memory

    if _working_memory is None:
        _working_memory = WorkingMemory()
        await _working_memory.initialize()

    return _working_memory
