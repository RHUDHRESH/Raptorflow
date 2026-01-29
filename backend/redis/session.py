"""
Session management service using Redis.

Provides secure user session management with workspace isolation,
automatic cleanup, and security features.
"""

import json
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .client import get_redis
from .critical_fixes import SessionValidator


class SessionService:
    """Redis-based session management service."""

    KEY_PREFIX = "session:"
    USER_SESSIONS_PREFIX = "user_sessions:"
    WORKSPACE_SESSIONS_PREFIX = "workspace_sessions:"

    def __init__(self):
        self.redis = get_redis()
        self.validator = SessionValidator()
        self.session_timeout = 3600  # 1 hour
        self.max_sessions_per_user = 10

    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for session."""
        return f"{self.KEY_PREFIX}{session_id}"

    def _get_user_sessions_key(self, user_id: str) -> str:
        """Get Redis key for user's sessions."""
        return f"{self.USER_SESSIONS_PREFIX}{user_id}"

    def _get_workspace_sessions_key(self, workspace_id: str) -> str:
        """Get Redis key for workspace's sessions."""
        return f"{self.WORKSPACE_SESSIONS_PREFIX}{workspace_id}"

    async def create_session(
        self,
        user_id: str,
        workspace_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        custom_timeout: Optional[int] = None,
    ) -> str:
        """Create a new session."""
        # Generate secure session ID
        session_id = secrets.token_urlsafe(32)

        # Check session limit for user
        await self._enforce_session_limit(user_id)

        # Create session data
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "workspace_id": workspace_id,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "metadata": metadata or {},
            "ip_address": None,  # Will be set on first access
            "user_agent": None,  # Will be set on first access
        }

        # Validate session data
        validated_data = self.validator.validate_session(session_data)

        # Store session
        session_key = self._get_session_key(session_id)
        timeout = custom_timeout or self.session_timeout

        await self.redis.set_json(session_key, validated_data, ex=timeout)

        # Add to user sessions index
        user_sessions_key = self._get_user_sessions_key(user_id)
        await self.redis.async_client.zadd(
            user_sessions_key, {session_id: datetime.now().timestamp()}
        )
        await self.redis.async_client.expire(user_sessions_key, timeout)

        # Add to workspace sessions index
        workspace_sessions_key = self._get_workspace_sessions_key(workspace_id)
        await self.redis.async_client.zadd(
            workspace_sessions_key, {session_id: datetime.now().timestamp()}
        )
        await self.redis.async_client.expire(workspace_sessions_key, timeout)

        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        session_key = self._get_session_key(session_id)
        session_data = await self.redis.get_json(session_key)

        if not session_data:
            return None

        # Validate session
        try:
            validated_data = self.validator.validate_session(session_data)

            # Update last accessed time
            validated_data["last_accessed"] = datetime.now().isoformat()
            await self.redis.set_json(session_key, validated_data)

            return validated_data
        except ValueError:
            # Invalid session, delete it
            await self.delete_session(session_id)
            return None

    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data."""
        session_data = await self.get_session(session_id)
        if not session_data:
            return False

        # Apply updates
        session_data.update(updates)
        session_data["last_accessed"] = datetime.now().isoformat()

        # Validate and save
        try:
            validated_data = self.validator.validate_session(session_data)
            session_key = self._get_session_key(session_id)
            await self.redis.set_json(session_key, validated_data)
            return True
        except ValueError:
            return False

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        session_data = await self.get_session(session_id)
        if not session_data:
            return False

        # Remove session
        session_key = self._get_session_key(session_id)
        await self.redis.delete(session_key)

        # Remove from user sessions index
        user_sessions_key = self._get_user_sessions_key(session_data["user_id"])
        await self.redis.async_client.zrem(user_sessions_key, session_id)

        # Remove from workspace sessions index
        workspace_sessions_key = self._get_workspace_sessions_key(
            session_data["workspace_id"]
        )
        await self.redis.async_client.zrem(workspace_sessions_key, session_id)

        return True

    async def delete_user_sessions(self, user_id: str) -> int:
        """Delete all sessions for a user."""
        user_sessions_key = self._get_user_sessions_key(user_id)

        # Get all session IDs
        session_ids = await self.redis.async_client.zrange(user_sessions_key, 0, -1)

        # Delete each session
        deleted_count = 0
        for session_id in session_ids:
            if await self.delete_session(session_id):
                deleted_count += 1

        return deleted_count

    async def delete_workspace_sessions(self, workspace_id: str) -> int:
        """Delete all sessions for a workspace."""
        workspace_sessions_key = self._get_workspace_sessions_key(workspace_id)

        # Get all session IDs
        session_ids = await self.redis.async_client.zrange(
            workspace_sessions_key, 0, -1
        )

        # Delete each session
        deleted_count = 0
        for session_id in session_ids:
            if await self.delete_session(session_id):
                deleted_count += 1

        return deleted_count

    async def get_user_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a user."""
        user_sessions_key = self._get_user_sessions_key(user_id)

        # Get session IDs sorted by last access
        session_ids = await self.redis.async_client.zrange(
            user_sessions_key, 0, -1, withscores=True
        )

        sessions = []
        for session_id, _ in session_ids:
            session_data = await self.get_session(session_id)
            if session_data:
                sessions.append(session_data)

        return sessions

    async def get_workspace_sessions(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a workspace."""
        workspace_sessions_key = self._get_workspace_sessions_key(workspace_id)

        # Get session IDs sorted by last access
        session_ids = await self.redis.async_client.zrange(
            workspace_sessions_key, 0, -1, withscores=True
        )

        sessions = []
        for session_id, _ in session_ids:
            session_data = await self.get_session(session_id)
            if session_data:
                sessions.append(session_data)

        return sessions

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        # This would typically be run as a background job
        # For now, sessions expire automatically via Redis TTL
        return 0

    async def _enforce_session_limit(self, user_id: str):
        """Enforce maximum sessions per user."""
        user_sessions = await self.get_user_sessions(user_id)

        if len(user_sessions) >= self.max_sessions_per_user:
            # Remove oldest session
            oldest_session = min(user_sessions, key=lambda x: x["last_accessed"])
            await self.delete_session(oldest_session["session_id"])

    async def extend_session(
        self, session_id: str, additional_time: int = 3600
    ) -> bool:
        """Extend session timeout."""
        session_data = await self.get_session(session_id)
        if not session_data:
            return False

        session_key = self._get_session_key(session_id)
        current_ttl = await self.redis.ttl(session_key)

        if current_ttl > 0:
            new_ttl = current_ttl + additional_time
            await self.redis.async_client.expire(session_key, new_ttl)
            return True

        return False

    async def is_session_valid(self, session_id: str) -> bool:
        """Check if session is valid."""
        return await self.get_session(session_id) is not None

    async def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        # This would require maintaining additional stats keys
        # For now, return placeholder data
        return {
            "total_sessions": 0,
            "active_sessions": 0,
            "sessions_per_workspace": {},
            "sessions_per_user": {},
        }
