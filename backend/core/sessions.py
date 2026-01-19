"""
Enhanced Redis-based session management for Raptorflow.
Provides secure, scalable session management with performance optimization.
"""

import asyncio
import json
import logging
import secrets
import time
import uuid
import zlib
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from enum import Enum
import redis.asyncio as redis
import jwt
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """Session status types."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"


class SessionType(Enum):
    """Session types for different use cases."""
    CHAT = "chat"
    WORKFLOW = "workflow"
    TASK = "task"
    SYSTEM = "system"
    API = "api"


@dataclass
class SessionContext:
    """Rich session context for conversation continuity."""
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    agent_state: Dict[str, Any] = field(default_factory=dict)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    workspace_context: Dict[str, Any] = field(default_factory=dict)
    temporary_data: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        
        # Keep only last 100 messages to prevent bloat
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]


@dataclass
class SessionMetadata:
    """Session metadata for analytics and management."""
    user_agent: str = ""
    ip_address: str = ""
    device_type: str = ""
    location: Dict[str, str] = field(default_factory=dict)
    subscription_tier: str = "free"
    feature_flags: List[str] = field(default_factory=list)
    security_flags: List[str] = field(default_factory=list)
    performance_profile: str = "standard"


@dataclass
class EnhancedSession:
    """Enhanced session with comprehensive data."""
    session_id: str
    user_id: str
    workspace_id: str
    session_type: SessionType
    status: SessionStatus
    context: SessionContext
    metadata: SessionMetadata
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    last_activity: datetime
    access_count: int = 0
    security_token: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "session_type": self.session_type.value,
            "status": self.status.value,
            "context": asdict(self.context),
            "metadata": asdict(self.metadata),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "access_count": self.access_count,
            "security_token": self.security_token
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EnhancedSession':
        """Create from dictionary."""
        context = SessionContext(**data.get("context", {}))
        metadata = SessionMetadata(**data.get("metadata", {}))
        
        return cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            workspace_id=data["workspace_id"],
            session_type=SessionType(data["session_type"]),
            status=SessionStatus(data["status"]),
            context=context,
            metadata=metadata,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            last_activity=datetime.fromisoformat(data["last_activity"]),
            access_count=data.get("access_count", 0),
            security_token=data.get("security_token", "")
        )


class SessionSecurityManager:
    """Handles session security including JWT tokens and encryption."""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
    def generate_security_token(self, session_id: str, user_id: str) -> str:
        """Generate JWT security token for session."""
        payload = {
            "session_id": session_id,
            "user_id": user_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_security_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT security token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Security token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid security token")
            return None
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()


class RedisSessionManager:
    """Enhanced Redis-based session manager with performance optimization."""
    
    def __init__(
        self,
        redis_url: str,
        secret_key: str,
        session_ttl_minutes: int = 30,
        max_sessions_per_user: int = 50,
        cleanup_interval_seconds: int = 300,
        compression_threshold: int = 1024
    ):
        self.redis_url = redis_url
        self.session_ttl = timedelta(minutes=session_ttl_minutes)
        self.max_sessions_per_user = max_sessions_per_user
        self.cleanup_interval = cleanup_interval_seconds
        self.compression_threshold = compression_threshold
        
        # Initialize Redis connection
        self.redis_client: Optional[redis.Redis] = None
        
        # Security manager
        self.security_manager = SessionSecurityManager(secret_key)
        
        # Session prefixes
        self.session_prefix = "session:"
        self.user_sessions_prefix = "user_sessions:"
        self.analytics_prefix = "analytics:"
        
        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Performance metrics
        self.metrics = {
            "sessions_created": 0,
            "sessions_validated": 0,
            "sessions_expired": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "compression_ratio": 0.0
        }
        
        logger.info(f"Redis session manager initialized: TTL={session_ttl_minutes}min")
    
    async def initialize(self):
        """Initialize Redis connection and start background tasks."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            await self.start_background_tasks()
            logger.info("Redis session manager connected successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis session manager: {e}")
            raise
    
    async def start_background_tasks(self):
        """Start background cleanup and analytics tasks."""
        if self._running:
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Background tasks started")
    
    async def stop(self):
        """Stop background tasks and close connections."""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("Redis session manager stopped")
    
    async def create_session(
        self,
        user_id: str,
        workspace_id: str,
        session_type: SessionType = SessionType.CHAT,
        initial_context: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Create a new enhanced session."""
        try:
            # Generate secure session ID
            session_id = str(uuid.uuid4())
            
            # Check user session limit
            await self._enforce_user_session_limit(user_id)
            
            # Create session objects
            context = SessionContext()
            if initial_context:
                for key, value in initial_context.items():
                    if hasattr(context, key):
                        setattr(context, key, value)
            
            session_metadata = SessionMetadata()
            if metadata:
                for key, value in metadata.items():
                    if hasattr(session_metadata, key):
                        setattr(session_metadata, key, value)
            
            # Create session
            now = datetime.utcnow()
            session = EnhancedSession(
                session_id=session_id,
                user_id=user_id,
                workspace_id=workspace_id,
                session_type=session_type,
                status=SessionStatus.ACTIVE,
                context=context,
                metadata=session_metadata,
                created_at=now,
                updated_at=now,
                expires_at=now + self.session_ttl,
                last_activity=now
            )
            
            # Generate security token
            session.security_token = self.security_manager.generate_security_token(
                session_id, user_id
            )
            
            # Store in Redis with compression
            await self._store_session(session)
            
            # Add to user sessions index
            await self._add_to_user_sessions(user_id, session_id)
            
            # Update metrics
            self.metrics["sessions_created"] += 1
            
            logger.info(f"Created session {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    async def validate_session(self, session_id: str, security_token: str = None) -> Optional[EnhancedSession]:
        """Validate and retrieve session."""
        try:
            # Try to get from cache
            session = await self._get_session(session_id)
            if not session:
                self.metrics["cache_misses"] += 1
                return None
            
            self.metrics["cache_hits"] += 1
            
            # Check expiration
            if datetime.utcnow() > session.expires_at:
                await self.invalidate_session(session_id, "expired")
                self.metrics["sessions_expired"] += 1
                return None
            
            # Verify security token if provided
            if security_token:
                token_payload = self.security_manager.verify_security_token(security_token)
                if not token_payload or token_payload.get("session_id") != session_id:
                    logger.warning(f"Invalid security token for session {session_id}")
                    return None
            
            # Update activity and access count
            session.last_activity = datetime.utcnow()
            session.access_count += 1
            await self._store_session(session)
            
            self.metrics["sessions_validated"] += 1
            return session
            
        except Exception as e:
            logger.error(f"Failed to validate session {session_id}: {e}")
            return None
    
    async def update_session_context(
        self,
        session_id: str,
        context_update: Dict[str, Any],
        merge_strategy: str = "update"
    ) -> bool:
        """Update session context."""
        try:
            session = await self._get_session(session_id)
            if not session:
                return False
            
            # Apply context updates based on strategy
            if merge_strategy == "update":
                for key, value in context_update.items():
                    if hasattr(session.context, key):
                        current_value = getattr(session.context, key)
                        if isinstance(current_value, dict) and isinstance(value, dict):
                            current_value.update(value)
                        else:
                            setattr(session.context, key, value)
            elif merge_strategy == "replace":
                for key, value in context_update.items():
                    if hasattr(session.context, key):
                        setattr(session.context, key, value)
            
            session.updated_at = datetime.utcnow()
            await self._store_session(session)
            return True
            
        except Exception as e:
            logger.error(f"Failed to update session context: {e}")
            return False
    
    async def invalidate_session(self, session_id: str, reason: str = "user_request") -> bool:
        """Invalidate/remove a session."""
        try:
            session = await self._get_session(session_id)
            if not session:
                return False
            
            # Mark as terminated
            session.status = SessionStatus.TERMINATED
            session.updated_at = datetime.utcnow()
            
            # Store final state
            await self._store_session(session)
            
            # Remove from user sessions index
            await self._remove_from_user_sessions(session.user_id, session_id)
            
            # Log analytics
            await self._log_session_event(session_id, "terminated", {"reason": reason})
            
            logger.info(f"Invalidated session {session_id}: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to invalidate session {session_id}: {e}")
            return False
    
    async def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[str]:
        """Get all session IDs for a user."""
        try:
            key = f"{self.user_sessions_prefix}{user_id}"
            session_ids = await self.redis_client.smembers(key)
            
            if not active_only:
                return list(session_ids)
            
            # Filter for active sessions only
            active_sessions = []
            for session_id in session_ids:
                session = await self._get_session(session_id)
                if session and session.status == SessionStatus.ACTIVE:
                    active_sessions.append(session_id)
            
            return active_sessions
            
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []
    
    async def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get analytics data for a session."""
        try:
            session = await self._get_session(session_id)
            if not session:
                return {}
            
            # Calculate session duration
            duration = datetime.utcnow() - session.created_at
            
            # Get conversation metrics
            conversation_count = len(session.context.conversation_history)
            
            return {
                "session_id": session_id,
                "user_id": session.user_id,
                "workspace_id": session.workspace_id,
                "session_type": session.session_type.value,
                "duration_seconds": duration.total_seconds(),
                "access_count": session.access_count,
                "conversation_count": conversation_count,
                "status": session.status.value,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get session analytics: {e}")
            return {}
    
    async def _store_session(self, session: EnhancedSession):
        """Store session in Redis with compression."""
        try:
            key = f"{self.session_prefix}{session.session_id}"
            data = json.dumps(session.to_dict())
            
            # Compress if large
            if len(data) > self.compression_threshold:
                compressed = zlib.compress(data.encode())
                await self.redis_client.setex(
                    key, 
                    int(self.session_ttl.total_seconds()), 
                    compressed
                )
                # Mark as compressed
                await self.redis_client.set(f"{key}:compressed", "1")
            else:
                await self.redis_client.setex(
                    key,
                    int(self.session_ttl.total_seconds()),
                    data
                )
            
        except Exception as e:
            logger.error(f"Failed to store session: {e}")
            raise
    
    async def _get_session(self, session_id: str) -> Optional[EnhancedSession]:
        """Get session from Redis with decompression."""
        try:
            key = f"{self.session_prefix}{session_id}"
            
            # Check if compressed
            is_compressed = await self.redis_client.exists(f"{key}:compressed")
            
            if is_compressed:
                compressed_data = await self.redis_client.get(key)
                if not compressed_data:
                    return None
                data = zlib.decompress(compressed_data).decode()
            else:
                data = await self.redis_client.get(key)
                if not data:
                    return None
                data = data.decode()
            
            session_dict = json.loads(data)
            return EnhancedSession.from_dict(session_dict)
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    async def _add_to_user_sessions(self, user_id: str, session_id: str):
        """Add session to user sessions index."""
        key = f"{self.user_sessions_prefix}{user_id}"
        await self.redis_client.sadd(key, session_id)
        await self.redis_client.expire(key, int(self.session_ttl.total_seconds() * 2))
    
    async def _remove_from_user_sessions(self, user_id: str, session_id: str):
        """Remove session from user sessions index."""
        key = f"{self.user_sessions_prefix}{user_id}"
        await self.redis_client.srem(key, session_id)
    
    async def _enforce_user_session_limit(self, user_id: str):
        """Enforce maximum sessions per user."""
        user_sessions = await self.get_user_sessions(user_id)
        
        if len(user_sessions) >= self.max_sessions_per_user:
            # Remove oldest sessions
            sessions_to_remove = len(user_sessions) - self.max_sessions_per_user + 1
            
            for session_id in user_sessions[:sessions_to_remove]:
                await self.invalidate_session(session_id, "session_limit_exceeded")
    
    async def _log_session_event(self, session_id: str, event_type: str, data: Dict[str, Any]):
        """Log session analytics event."""
        try:
            key = f"{self.analytics_prefix}{session_id}:{event_type}:{int(time.time())}"
            await self.redis_client.setex(key, 86400, json.dumps(data))  # 24h TTL
        except Exception as e:
            logger.error(f"Failed to log session event: {e}")
    
    async def _cleanup_loop(self):
        """Background cleanup loop for expired sessions."""
        while self._running:
            try:
                await self._cleanup_expired_sessions()
                await asyncio.sleep(self.cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        try:
            # This is a simplified cleanup - in production, you'd want to scan
            # sessions more efficiently using Redis patterns or indexes
            pattern = f"{self.session_prefix}*"
            cursor = 0
            
            while True:
                cursor, keys = await self.redis_client.scan(cursor, match=pattern, count=100)
                
                for key in keys:
                    session_id = key.decode().replace(self.session_prefix, "")
                    session = await self._get_session(session_id)
                    
                    if session and datetime.utcnow() > session.expires_at:
                        await self.invalidate_session(session_id, "expired_cleanup")
                
                if cursor == 0:
                    break
                    
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get session manager metrics."""
        return self.metrics.copy()


# Global session manager instance
_session_manager: Optional[RedisSessionManager] = None


async def get_session_manager() -> RedisSessionManager:
    """Get global session manager instance."""
    global _session_manager
    
    if _session_manager is None:
        from backend.agents.config import get_config
        config = get_config()
        
        redis_url = config.REDIS_URL or "redis://localhost:6379"
        secret_key = getattr(config, 'SESSION_SECRET_KEY', 'your-secret-key-here')
        
        _session_manager = RedisSessionManager(
            redis_url=redis_url,
            secret_key=secret_key
        )
        await _session_manager.initialize()
    
    return _session_manager
