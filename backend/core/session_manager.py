"""
Simple session management system for Raptorflow agent conversations.
"""

import asyncio
import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """Session status types."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class SessionType(Enum):
    """Session types."""
    
    CHAT = "chat"
    WORKFLOW = "workflow"
    TASK = "task"
    SYSTEM = "system"


@dataclass
class SessionData:
    """Data stored in a session."""
    
    workspace_id: str
    agent_id: Optional[str] = None
    user_id: Optional[str] = None
    session_type: SessionType = SessionType.CHAT
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)


@dataclass
class Session:
    """Session object with metadata and management."""
    
    session_id: str
    session_data: SessionData
    status: SessionStatus
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "status": self.status.value,
            "session_type": self.session_data.session_type.value,
            "agent_id": self.session_data.agent_id,
            "workspace_id": self.session_data.workspace_id,
            "user_id": self.session_data.user_id,
            "context": self.session_data.context,
            "metadata": self.session_data.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_activity": self.session_data.last_activity.isoformat(),
        }


class SessionManager:
    """Simple but effective session manager for Raptorflow agents."""
    
    def __init__(
        self,
        session_ttl_minutes: int = 30,
        max_sessions_per_user: int = 10,
        cleanup_interval_seconds: int = 300,  # 5 minutes
        max_history_size: int = 10000
    ):
        self.session_ttl_minutes = session_ttl_minutes
        self.max_sessions_per_user = max_sessions_per_user
        self.cleanup_interval_seconds = cleanup_interval_seconds
        self.max_history_size = max_history_size
        
        # In-memory storage
        self.sessions: Dict[str, Session] = {}
        self.user_sessions: Dict[str, List[str]] = {}  # user_id -> [session_ids]
        
        # Background tasks
        self._background_tasks: set = set()
        self._running = False
        
        logger.info(f"Session manager initialized: TTL={session_ttl_minutes}min, max_sessions={max_sessions_per_user}")
    
    async def start(self):
        """Start the session manager background tasks."""
        if self._running:
            return
        
        self._running = True
        self._background_tasks.add(asyncio.create_task(self._cleanup_loop()))
        logger.info("Session manager started")
    
    async def stop(self):
        """Stop the session manager background tasks."""
        self._running = False
        
        for task in self._background_tasks:
            task.cancel()
        
        await asyncio.gather(*self._background_tasks, return_exceptions=True)
        self._background_tasks.clear()
        logger.info("Session manager stopped")
    
    def create_session(
        self,
        workspace_id: str,
        session_type: SessionType,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        initial_context: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Create a new session."""
        try:
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Check user session limit
            if user_id and user_id in self.user_sessions:
                user_sessions = self.user_sessions[user_id]
                if len(user_sessions) >= self.max_sessions_per_user:
                    # Remove oldest session
                    oldest_session_id = user_sessions[0]
                    if oldest_session_id in self.sessions:
                        del self.sessions[oldest_session_id]
                    del user_sessions[0]
                    logger.info(f"Removed oldest session {oldest_session_id} for user {user_id}")
            
            # Create session data
            session_data = SessionData(
                agent_id=agent_id,
                workspace_id=workspace_id,
                user_id=user_id,
                session_type=session_type,
                context=initial_context or {},
                metadata=metadata or {},
                created_at=datetime.now(),
                updated_at=datetime.now(),
                last_activity=datetime.now()
            )
            
            # Create session
            expires_at = datetime.now() + timedelta(minutes=self.session_ttl_minutes)
            session = Session(
                session_id=session_id,
                session_data=session_data,
                status=SessionStatus.ACTIVE,
                expires_at=expires_at,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Store session
            self.sessions[session_id] = session
            
            # Update user sessions
            if user_id:
                if user_id not in self.user_sessions:
                    self.user_sessions[user_id] = []
                self.user_sessions[user_id].append(session_id)
            
            logger.info(f"Created session {session_id} for user {user_id} in workspace {workspace_id}")
            
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise Exception(f"Session creation failed: {e}")
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        try:
            session = self.sessions.get(session_id)
            
            if not session:
                return None
            
            # Check if session is expired
            if datetime.now() > session.expires_at:
                session.status = SessionStatus.EXPIRED
                logger.warning(f"Session {session_id} has expired")
            
            # Update last activity
            session.session_data.last_activity = datetime.now()
            session.updated_at = datetime.now()
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    def update_session(
        self,
        session_id: str,
        context_update: Optional[Dict[str, Any]] = None,
        metadata_update: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update session context and metadata."""
        try:
            session = self.sessions.get(session_id)
            
            if not session:
                logger.warning(f"Session {session_id} not found")
                return False
            
            # Check if session is expired
            if datetime.now() > session.expires_at:
                session.status = SessionStatus.EXPIRED
                logger.warning(f"Cannot update expired session {session_id}")
                return False
            
            # Update session data
            if context_update:
                session.session_data.context.update(context_update)
            
            if metadata_update:
                session.session_data.metadata.update(metadata_update)
            
            session.session_data.last_activity = datetime.now()
            session.updated_at = datetime.now()
            
            logger.debug(f"Updated session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {e}")
            return False
    
    def terminate_session(self, session_id: str, reason: str = "User request") -> bool:
        """Terminate a session."""
        try:
            session = self.sessions.get(session_id)
            
            if not session:
                logger.warning(f"Session {session_id} not found")
                return False
            
            # Update status
            session.status = SessionStatus.TERMINATED
            session.session_data.metadata["termination_reason"] = reason
            session.session_data.last_activity = datetime.now()
            session.updated_at = datetime.now()
            
            logger.info(f"Terminated session {session_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to terminate session {session_id}: {e}")
            return False
    
    def get_user_sessions(self, user_id: str) -> List[str]:
        """Get all active sessions for a user."""
        try:
            return self.user_sessions.get(user_id, [])
            
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []
    
    def get_workspace_sessions(self, workspace_id: str) -> List[str]:
        """Get all active sessions in a workspace."""
        try:
            workspace_sessions = []
            
            for session_id, session in self.sessions.items():
                if (session.session_data.workspace_id == workspace_id and 
                    session.status == SessionStatus.ACTIVE):
                    workspace_sessions.append(session_id)
            
            return workspace_sessions
            
        except Exception as e:
            logger.error(f"Failed to get workspace sessions: {e}")
            return []
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session manager statistics."""
        try:
            total_sessions = len(self.sessions)
            active_sessions = len([
                s for s in self.sessions.values()
                if s.status == SessionStatus.ACTIVE
            ])
            expired_sessions = len([
                s for s in self.sessions.values()
                if s.status == SessionStatus.EXPIRED
            ])
            
            total_users = len(self.user_sessions)
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "expired_sessions": expired_sessions,
                "total_users": total_users,
                "max_sessions_per_user": self.max_sessions_per_user,
                "session_ttl_minutes": self.session_ttl_minutes,
                "cleanup_interval_seconds": self.cleanup_interval_seconds,
                "max_history_size": self.max_history_size,
            }
            
        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return {"error": str(e)}
    
    def get_session_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session context."""
        try:
            session = self.sessions.get(session_id)
            
            if not session:
                return None
            
            return session.session_data.context
            
        except Exception as e:
            logger.error(f"Failed to get session context: {e}")
            return None
    
    async def _cleanup_loop(self):
        """Background cleanup of expired sessions."""
        while self._running:
            try:
                await asyncio.sleep(self.cleanup_interval_seconds)
                
                # Find expired sessions
                expired_sessions = []
                current_time = datetime.now()
                
                for session_id, session in self.sessions.items():
                    if current_time > session.expires_at:
                        expired_sessions.append(session_id)
                
                # Remove expired sessions
                for session_id in expired_sessions:
                    session = self.sessions[session_id]
                    session.status = SessionStatus.EXPIRED
                    
                    # Remove from user sessions
                    if session.session_data.user_id:
                        user_sessions = self.user_sessions.get(session.session_data.user_id, [])
                        if session_id in user_sessions:
                            user_sessions.remove(session_id)
                    
                    del self.sessions[session_id]
                
                if expired_sessions:
                    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")
    
    def generate_session_hash(self, session_data: SessionData) -> str:
        """Generate a hash for session verification."""
        try:
            hash_data = {
                "session_id": session_data.agent_id,
                "workspace_id": session_data.workspace_id,
                "user_id": session_data.user_id,
                "session_type": session_data.session_type.value,
                "created_at": session_data.created_at.isoformat(),
            }
            
            return hashlib.sha256(json.dumps(hash_data, sort_keys=True)).hexdigest()
            
        except Exception as e:
            logger.error(f"Failed to generate session hash: {e}")
            return ""
    
    def validate_session(self, session: Session) -> bool:
        """Validate session integrity."""
        try:
            # Check if session is expired
            if datetime.now() > session.expires_at:
                return False
            
            # Check session hash integrity
            current_hash = self.generate_session_hash(session.session_data)
            stored_hash = session.session_data.metadata.get("session_hash")
            
            if stored_hash and current_hash != stored_hash:
                logger.error(f"Session {session.session_id} hash validation failed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate session {session.session_id}: {e}")
            return False


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager(
    session_ttl_minutes: int = 30,
    max_sessions_per_user: int = 10,
    cleanup_interval_seconds: int = 300,
    max_history_size: int = 10000
) -> SessionManager:
    """Get or create global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(
            session_ttl_minutes=session_ttl_minutes,
            max_sessions_per_user=max_sessions_per_user,
            cleanup_interval_seconds=cleanup_interval_seconds,
            max_history_size=max_history_size
        )
    return _session_manager


async def start_session_manager():
    """Start the global session manager."""
    session_manager = get_session_manager()
    await session_manager.start()


async def stop_session_manager():
    """Stop the global session manager."""
    session_manager = get_session_manager()
    if session_manager:
        await session_manager.stop()
