"""
Session management service using Redis.

Handles user sessions with workspace isolation, context persistence,
and approval system integration.
"""

import hashlib
import hmac
import os
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .client import get_redis
from .session_models import SessionData


class SessionService:
    """Redis-based session management service."""

    KEY_PREFIX = "session:"
    DEFAULT_TTL = 1800  # 30 minutes

    def __init__(self):
        self.redis = get_redis()
        self.session_ttl = self.DEFAULT_TTL
        self.secret_key = os.getenv("WORKSPACE_KEY_SECRET", secrets.token_hex(32))

    def _generate_secure_session_id(self) -> str:
        """Generate cryptographically secure session ID."""
        try:
            import uuid7

            return str(uuid7.uuid7())
        except ImportError:
            # Fallback to UUID4 with additional entropy
            base_uuid = str(uuid.uuid4())
            entropy = secrets.token_hex(8)
            return f"{base_uuid}-{entropy}"

    def _sign_workspace_id(self, workspace_id: str) -> str:
        """Create HMAC signature for workspace_id."""
        return hmac.new(
            self.secret_key.encode(), workspace_id.encode(), hashlib.sha256
        ).hexdigest()

    def _verify_workspace_id(self, workspace_id: str, signature: str) -> bool:
        """Verify workspace_id signature."""
        expected = self._sign_workspace_id(workspace_id)
        return hmac.compare_digest(expected, signature)

    def _get_key(self, session_id: str) -> str:
        """Get Redis key for session."""
        return f"{self.KEY_PREFIX}{session_id}"

    async def create_session(
        self,
        user_id: str,
        workspace_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> str:
        """Create a new session with enhanced security."""
        session_id = self._generate_secure_session_id()
        workspace_signature = self._sign_workspace_id(workspace_id)

        session_data = SessionData(
            session_id=session_id,
            user_id=user_id,
            workspace_id=workspace_id,
            expires_at=datetime.now() + timedelta(seconds=self.session_ttl),
            settings=metadata or {},
        )

        # Add session binding for security
        if ip_address and user_agent:
            binding_data = f"{session_id}:{ip_address}:{user_agent}"
            session_binding = hashlib.sha256(binding_data.encode()).hexdigest()
            session_data.settings["session_binding"] = session_binding
            session_data.settings["bound_ip"] = ip_address
            session_data.settings["bound_user_agent"] = user_agent

        # Store with workspace signature for validation
        key = self._get_key(session_id)
        session_dict = session_data.to_dict()
        session_dict["workspace_signature"] = workspace_signature

        await self.redis.set_json(key, session_dict, ex=self.session_ttl)

        return session_id

    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session data with security validation."""
        key = self._get_key(session_id)
        data = await self.redis.get_json(key)

        if not data:
            return None

        # Validate workspace signature
        if "workspace_signature" in data and "workspace_id" in data:
            if not self._verify_workspace_id(
                data["workspace_id"], data["workspace_signature"]
            ):
                return None  # Signature validation failed

        session = SessionData.from_dict(data)

        # Check if expired
        if session.is_expired():
            await self.delete_session(session_id)
            return None

        return session

    async def save_session(self, session: SessionData):
        """Save session data."""
        key = self._get_key(session.session_id)

        # Update last active time
        session.last_active_at = datetime.now()

        # Calculate TTL from expiry
        if session.expires_at:
            ttl_seconds = max(
                0, int((session.expires_at - datetime.now()).total_seconds())
            )
        else:
            ttl_seconds = self.session_ttl

        await self.redis.set_json(key, session.to_dict(), ex=ttl_seconds)

    async def update_session(
        self, session_id: str, updates: Dict[str, Any]
    ) -> Optional[SessionData]:
        """Update session fields."""
        session = await self.get_session(session_id)
        if not session:
            return None

        # Update allowed fields
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)

        await self.save_session(session)
        return session

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[SessionData]:
        """Add a message to the session."""
        session = await self.get_session(session_id)
        if not session:
            return None

        session.add_message(role, content, metadata)
        await self.save_session(session)
        return session

    async def set_current_agent(
        self, session_id: str, agent_name: str
    ) -> Optional[SessionData]:
        """Set the currently active agent."""
        session = await self.get_session(session_id)
        if not session:
            return None

        session.set_current_agent(agent_name)
        await self.save_session(session)
        return session

    async def update_context(
        self, session_id: str, context_updates: Dict[str, Any]
    ) -> Optional[SessionData]:
        """Update session context."""
        session = await self.get_session(session_id)
        if not session:
            return None

        for key, value in context_updates.items():
            session.update_context(key, value)

        await self.save_session(session)
        return session

    async def add_pending_approval(
        self, session_id: str, approval_data: Dict[str, Any]
    ) -> Optional[SessionData]:
        """Add a pending approval request."""
        session = await self.get_session(session_id)
        if not session:
            return None

        session.add_pending_approval(approval_data)
        await self.save_session(session)
        return session

    async def remove_pending_approval(
        self, session_id: str, approval_id: str
    ) -> Optional[SessionData]:
        """Remove a pending approval request."""
        session = await self.get_session(session_id)
        if not session:
            return None

        session.remove_pending_approval(approval_id)
        await self.save_session(session)
        return session

    async def set_last_output(
        self, session_id: str, output: Dict[str, Any]
    ) -> Optional[SessionData]:
        """Set the last output from agent."""
        session = await self.get_session(session_id)
        if not session:
            return None

        session.last_output = output
        session.last_active_at = datetime.now()
        await self.save_session(session)
        return session

    async def extend_session(
        self, session_id: str, seconds: int = 1800
    ) -> Optional[SessionData]:
        """Extend session expiry."""
        session = await self.get_session(session_id)
        if not session:
            return None

        session.extend_expiry(seconds)
        await self.save_session(session)
        return session

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        key = self._get_key(session_id)
        result = await self.redis.delete(key)
        return result > 0

    async def get_user_sessions(
        self, user_id: str, workspace_id: Optional[str] = None
    ) -> List[SessionData]:
        """Get all sessions for a user."""
        # This is inefficient - in production, maintain a user->sessions index
        # For now, we'll implement a simple pattern search
        pattern = f"{self.KEY_PREFIX}*"
        sessions = []

        # Note: Upstash Redis doesn't support SCAN, so this is a limitation
        # In production, maintain a separate index: user_sessions:{user_id}
        return sessions

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        # In production, this would use SCAN to find expired sessions
        # For now, rely on Redis TTL to automatically clean up
        return 0

    async def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session summary for debugging."""
        session = await self.get_session(session_id)
        if not session:
            return None

        return session.get_summary()

    async def validate_session_access(
        self,
        session_id: str,
        user_id: str,
        workspace_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """Enhanced session validation with multiple security checks."""
        session = await self.get_session(session_id)
        if not session:
            return False

        # Basic validation
        if session.user_id != user_id or session.workspace_id != workspace_id:
            return False

        # Session binding validation (if available)
        if "session_binding" in session.settings:
            if ip_address and user_agent:
                binding_data = f"{session_id}:{ip_address}:{user_agent}"
                expected_binding = hashlib.sha256(binding_data.encode()).hexdigest()
                if not hmac.compare_digest(
                    expected_binding, session.settings["session_binding"]
                ):
                    return False
            else:
                # Missing IP or User-Agent - reject for security
                return False

        return True

    async def get_active_sessions_count(self, workspace_id: str) -> int:
        """Get count of active sessions for workspace."""
        # In production, maintain a workspace_sessions:{workspace_id} counter
        # For now, return 0 as placeholder
        return 0
