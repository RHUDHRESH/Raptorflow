"""
Session management for RaptorFlow
Handles user sessions with Redis backend
"""

import json
import logging
import secrets
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from backend.core.models import User
from backend.core.supabase_mgr import get_supabase_client
from backend.redis_core.client import get_redis

logger = logging.getLogger(__name__)


@dataclass
class Session:
    """Session data structure"""

    session_id: str
    user_id: str
    workspace_id: str
    created_at: datetime
    expires_at: datetime
    data: Dict[str, Any]


class SessionManager:
    """Redis-backed session manager"""

    def __init__(self):
        self.redis = get_redis()
        self.supabase = get_supabase_client()
        self.session_ttl = 1800  # 30 minutes
        self.session_prefix = "session:"

    async def create_session(self, user_id: str, workspace_id: str) -> str:
        """
        Create a new session for user

        Args:
            user_id: User ID
            workspace_id: Workspace ID

        Returns:
            Session ID
        """
        session_id = secrets.token_urlsafe(32)
        created_at = datetime.utcnow()
        expires_at = created_at + timedelta(seconds=self.session_ttl)

        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "workspace_id": workspace_id,
            "created_at": created_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "data": {},
        }

        try:
            # Store in Redis with TTL
            key = f"{self.session_prefix}{session_id}"
            await self.redis.set_json(key, session_data, ex=self.session_ttl)

            return session_id

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None

    async def validate_session(self, session_id: str) -> Optional[Session]:
        """
        Validate session and return session data

        Args:
            session_id: Session ID to validate

        Returns:
            Session object if valid, None otherwise
        """
        try:
            key = f"{self.session_prefix}{session_id}"
            session_data = await self.redis.get_json(key)

            if not session_data:
                return None

            # Refresh TTL on access
            await self.redis.expire(key, self.session_ttl)

            return Session(
                session_id=session_data["session_id"],
                user_id=session_data["user_id"],
                workspace_id=session_data["workspace_id"],
                created_at=datetime.fromisoformat(session_data["created_at"]),
                expires_at=datetime.utcnow() + timedelta(seconds=self.session_ttl),
                data=session_data.get("data", {}),
            )

        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return None

    async def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate/remove a session

        Args:
            session_id: Session ID to invalidate

        Returns:
            True if session was invalidated, False otherwise
        """
        try:
            key = f"{self.session_prefix}{session_id}"
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error invalidating session: {e}")
            return False

    async def update_session_data(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update session data

        Args:
            session_id: Session ID
            data: Data to update

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            key = f"{self.session_prefix}{session_id}"
            session_data = await self.redis.get_json(key)

            if not session_data:
                return False

            session_data["data"] = data
            await self.redis.set_json(key, session_data, ex=self.session_ttl)
            return True
        except Exception as e:
            logger.error(f"Error updating session data: {e}")
            return False

    async def get_session_user(self, session_id: str) -> Optional[User]:
        """
        Get user from session

        Args:
            session_id: Session ID

        Returns:
            User object if session is valid, None otherwise
        """
        session = await self.validate_session(session_id)
        if not session:
            return None

        try:
            # Fetch user from database
            result = (
                self.supabase.table("users")
                .select("*")
                .eq("id", session.user_id)
                .single()
                .execute()
            )

            if not result.data:
                return None

            user_data = result.data
            return User(
                id=user_data["id"],
                email=user_data["email"],
                full_name=user_data.get("full_name"),
                avatar_url=user_data.get("avatar_url"),
                subscription_tier=user_data.get("subscription_tier", "free"),
                budget_limit_monthly=float(user_data.get("budget_limit_monthly", 1.0)),
                onboarding_completed_at=user_data.get("onboarding_completed_at"),
                preferences=user_data.get("preferences", {}),
                created_at=user_data.get("created_at"),
                updated_at=user_data.get("updated_at"),
            )

        except Exception as e:
            logger.error(f"Error getting session user: {e}")
            return None


# Global session manager instance
_session_manager = SessionManager()


def get_session_manager() -> SessionManager:
    """Get global session manager instance"""
    return _session_manager
