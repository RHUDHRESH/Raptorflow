"""
RaptorFlow Session Service
Phase 1.3.1: Persistent Session Storage

Handles session management, data persistence, multi-device synchronization,
session recovery, and data versioning for the onboarding system.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

import redis.asyncio as redis
from supabase import create_client, Client

from fastapi import HTTPException
from pydantic import BaseModel

from .config import get_settings
from .core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class SessionStatus(str, Enum):
    """Session status types."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    ERROR = "error"
    PAUSED = "paused"


class StepStatus(str, Enum):
    """Step completion status."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class OnboardingSession:
    """Onboarding session data."""

    id: str
    workspace_id: str
    user_id: str
    current_step: int
    total_steps: int
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict] = None
    version: int = 1


@dataclass
class StepData:
    """Data for a specific onboarding step."""

    session_id: str
    step_id: int
    status: StepStatus
    data: Dict
    updated_at: datetime
    version: int = 1
    validation_errors: Optional[List[str]] = None
    processing_time: Optional[float] = None


@dataclass
class SessionSnapshot:
    """Session snapshot for versioning."""

    session_id: str
    version: int
    snapshot_data: Dict
    created_at: datetime
    created_by: str
    description: Optional[str] = None


class RedisSessionManager:
    """Redis-based session caching and management."""

    def __init__(self):
        self.redis_client = None
        self.session_ttl = 86400  # 24 hours
        self.step_ttl = 3600  # 1 hour

    async def _get_client(self):
        """Get Redis client."""
        if self.redis_client is None:
            self.redis_client = redis.from_url(
                settings.REDIS_URL, encoding="utf-8", decode_responses=True
            )
        return self.redis_client

    async def cache_session(self, session: OnboardingSession):
        """Cache session in Redis."""
        client = await self._get_client()

        session_key = f"session:{session.id}"
        session_data = json.dumps(asdict(session), default=str)

        await client.setex(session_key, self.session_ttl, session_data)

        # Index by workspace and user
        await client.sadd(f"sessions:workspace:{session.workspace_id}", session.id)
        await client.sadd(f"sessions:user:{session.user_id}", session.id)

        logger.info(f"Cached session {session.id} in Redis")

    async def cache_step_data(self, step_data: StepData):
        """Cache step data in Redis."""
        client = await self._get_client()

        step_key = f"session:{step_data.session_id}:step:{step_data.step_id}"
        step_data_dict = asdict(step_data)

        await client.setex(
            step_key, self.step_ttl, json.dumps(step_data_dict, default=str)
        )

        logger.info(
            f"Cached step {step_data.step_id} for session {step_data.session_id}"
        )

    async def get_cached_session(self, session_id: str) -> Optional[OnboardingSession]:
        """Get session from Redis cache."""
        try:
            client = await self._get_client()
            session_key = f"session:{session_id}"

            session_data = await client.get(session_key)
            if not session_data:
                return None

            session_dict = json.loads(session_data)

            # Convert datetime strings back to datetime objects
            session_dict["created_at"] = datetime.fromisoformat(
                session_dict["created_at"]
            )
            session_dict["updated_at"] = datetime.fromisoformat(
                session_dict["updated_at"]
            )
            if session_dict.get("completed_at"):
                session_dict["completed_at"] = datetime.fromisoformat(
                    session_dict["completed_at"]
                )

            return OnboardingSession(**session_dict)

        except Exception as e:
            logger.error(f"Failed to get cached session {session_id}: {e}")
            return None

    async def get_cached_step_data(
        self, session_id: str, step_id: int
    ) -> Optional[StepData]:
        """Get step data from Redis cache."""
        try:
            client = await self._get_client()
            step_key = f"session:{session_id}:step:{step_id}"

            step_data = await client.get(step_key)
            if not step_data:
                return None

            step_dict = json.loads(step_data)
            step_dict["updated_at"] = datetime.fromisoformat(step_dict["updated_at"])

            return StepData(**step_dict)

        except Exception as e:
            logger.error(f"Failed to get cached step data {session_id}:{step_id}: {e}")
            return None

    async def invalidate_session_cache(self, session_id: str):
        """Invalidate session cache."""
        client = await self._get_client()

        # Delete session data
        session_key = f"session:{session_id}"
        await client.delete(session_key)

        # Delete all step data
        step_pattern = f"session:{session_id}:step:*"
        step_keys = await client.keys(step_pattern)
        if step_keys:
            await client.delete(*step_keys)

        logger.info(f"Invalidated cache for session {session_id}")


class SupabaseSessionManager:
    """Supabase-based persistent session storage."""

    def __init__(self):
        self.db_client = None

    async def _get_client(self):
        """Get Supabase client."""
        if self.db_client is None:
            self.db_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        return self.db_client

    async def create_session(
        self, workspace_id: str, user_id: str, total_steps: int = 25
    ) -> OnboardingSession:
        """Create a new onboarding session."""
        client = await self._get_client()

        session = OnboardingSession(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            user_id=user_id,
            current_step=1,
            total_steps=total_steps,
            status=SessionStatus.IN_PROGRESS,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            metadata={
                "client_info": self._get_client_info(),
                "ip_address": None,  # Would be set from request
                "user_agent": None,  # Would be set from request
            },
        )

        try:
            # Insert into database
            result = (
                client.table("onboarding_sessions").insert(asdict(session)).execute()
            )

            if result.data:
                logger.info(f"Created session {session.id} in database")
                return session
            else:
                raise Exception("Failed to create session in database")

        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise HTTPException(status_code=500, detail="Failed to create session")

    async def update_session(self, session: OnboardingSession) -> OnboardingSession:
        """Update session in database."""
        client = await self._get_client()

        session.updated_at = datetime.utcnow()
        session.version += 1

        try:
            result = (
                client.table("onboarding_sessions")
                .update(asdict(session))
                .eq("id", session.id)
                .execute()
            )

            if result.data:
                logger.info(f"Updated session {session.id} in database")
                return session
            else:
                raise Exception("Failed to update session in database")

        except Exception as e:
            logger.error(f"Failed to update session {session.id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to update session")

    async def get_session(self, session_id: str) -> Optional[OnboardingSession]:
        """Get session from database."""
        try:
            client = await self._get_client()
            result = (
                client.table("onboarding_sessions")
                .select("*")
                .eq("id", session_id)
                .execute()
            )

            if result.data:
                session_dict = result.data[0]

                # Convert string timestamps to datetime
                session_dict["created_at"] = datetime.fromisoformat(
                    session_dict["created_at"].replace("Z", "+00:00")
                )
                session_dict["updated_at"] = datetime.fromisoformat(
                    session_dict["updated_at"].replace("Z", "+00:00")
                )
                if session_dict.get("completed_at"):
                    session_dict["completed_at"] = datetime.fromisoformat(
                        session_dict["completed_at"].replace("Z", "+00:00")
                    )

                return OnboardingSession(**session_dict)
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    async def update_step_data(
        self,
        session_id: str,
        step_id: int,
        data: Dict,
        status: StepStatus = StepStatus.COMPLETED,
    ) -> StepData:
        """Update step data in database."""
        client = await self._get_client()

        step_data = StepData(
            session_id=session_id,
            step_id=step_id,
            status=status,
            data=data,
            updated_at=datetime.utcnow(),
            version=1,
        )

        try:
            # Upsert step data
            result = (
                client.table("onboarding_step_data").upsert(asdict(step_data)).execute()
            )

            if result.data:
                logger.info(f"Updated step {step_id} for session {session_id}")
                return step_data
            else:
                raise Exception("Failed to update step data in database")

        except Exception as e:
            logger.error(f"Failed to update step data {session_id}:{step_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to update step data")

    async def get_step_data(self, session_id: str, step_id: int) -> Optional[StepData]:
        """Get step data from database."""
        try:
            client = await self._get_client()
            result = (
                client.table("onboarding_step_data")
                .select("*")
                .eq("session_id", session_id)
                .eq("step_id", step_id)
                .execute()
            )

            if result.data:
                step_dict = result.data[0]
                step_dict["updated_at"] = datetime.fromisoformat(
                    step_dict["updated_at"].replace("Z", "+00:00")
                )
                return StepData(**step_dict)
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to get step data {session_id}:{step_id}: {e}")
            return None

    async def create_snapshot(
        self, session_id: str, description: Optional[str] = None
    ) -> SessionSnapshot:
        """Create a session snapshot."""
        client = await self._get_client()

        # Get current session data
        session = await self.get_session(session_id)
        if not session:
            raise Exception("Session not found")

        # Get all step data
        all_steps_result = (
            client.table("onboarding_step_data")
            .select("*")
            .eq("session_id", session_id)
            .execute()
        )
        all_steps = all_steps_result.data if all_steps_result.data else []

        snapshot = SessionSnapshot(
            session_id=session_id,
            version=session.version + 1,
            snapshot_data={"session": asdict(session), "steps": all_steps},
            created_at=datetime.utcnow(),
            created_by=session.user_id,
            description=description,
        )

        try:
            result = (
                client.table("session_snapshots").insert(asdict(snapshot)).execute()
            )

            if result.data:
                logger.info(
                    f"Created snapshot {snapshot.version} for session {session_id}"
                )
                return snapshot
            else:
                raise Exception("Failed to create snapshot")

        except Exception as e:
            logger.error(f"Failed to create snapshot for session {session_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to create snapshot")

    async def get_snapshots(self, session_id: str) -> List[SessionSnapshot]:
        """Get all snapshots for a session."""
        try:
            client = await self._get_client()
            result = (
                client.table("session_snapshots")
                .select("*")
                .eq("session_id", session_id)
                .order("created_at", desc=True)
                .execute()
            )

            snapshots = []
            for snapshot_dict in result.data if result.data else []:
                snapshot_dict["created_at"] = datetime.fromisoformat(
                    snapshot_dict["created_at"].replace("Z", "+00:00")
                )
                snapshots.append(SessionSnapshot(**snapshot_dict))

            return snapshots

        except Exception as e:
            logger.error(f"Failed to get snapshots for session {session_id}: {e}")
            return []

    def _get_client_info(self) -> Dict:
        """Get client information for session metadata."""
        return {
            "platform": "web",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
        }


class SessionService:
    """Main session service combining caching and persistent storage."""

    def __init__(self):
        self.redis_manager = RedisSessionManager()
        self.supabase_manager = SupabaseSessionManager()

    async def create_session(
        self, workspace_id: str, user_id: str
    ) -> OnboardingSession:
        """
        Create a new onboarding session.

        Args:
            workspace_id: Workspace ID
            user_id: User ID

        Returns:
            Created session
        """
        # Create in database
        session = await self.supabase_manager.create_session(workspace_id, user_id)

        # Cache in Redis
        await self.redis_manager.cache_session(session)

        return session

    async def get_session(self, session_id: str) -> Optional[OnboardingSession]:
        """
        Get session with cache fallback.

        Args:
            session_id: Session ID

        Returns:
            Session or None if not found
        """
        # Try cache first
        session = await self.redis_manager.get_cached_session(session_id)

        if session:
            return session

        # Fallback to database
        session = await self.supabase_manager.get_session(session_id)

        if session:
            # Cache for future requests
            await self.redis_manager.cache_session(session)

        return session

    async def update_session(self, session: OnboardingSession) -> OnboardingSession:
        """
        Update session in both cache and database.

        Args:
            session: Session to update

        Returns:
            Updated session
        """
        # Update in database
        updated_session = await self.supabase_manager.update_session(session)

        # Update cache
        await self.redis_manager.cache_session(updated_session)

        return updated_session

    async def update_step_data(
        self,
        session_id: str,
        step_id: int,
        data: Dict,
        status: StepStatus = StepStatus.COMPLETED,
    ) -> StepData:
        """
        Update step data in both cache and database.

        Args:
            session_id: Session ID
            step_id: Step ID
            data: Step data
            status: Step status

        Returns:
            Updated step data
        """
        # Update in database
        step_data = await self.supabase_manager.update_step_data(
            session_id, step_id, data, status
        )

        # Update cache
        await self.redis_manager.cache_step_data(step_data)

        # Update session timestamp
        await self.update_session_timestamp(session_id)

        return step_data

    async def get_step_data(self, session_id: str, step_id: int) -> Optional[StepData]:
        """
        Get step data with cache fallback.

        Args:
            session_id: Session ID
            step_id: Step ID

        Returns:
            Step data or None if not found
        """
        # Try cache first
        step_data = await self.redis_manager.get_cached_step_data(session_id, step_id)

        if step_data:
            return step_data

        # Fallback to database
        step_data = await self.supabase_manager.get_step_data(session_id, step_id)

        if step_data:
            # Cache for future requests
            await self.redis_manager.cache_step_data(step_data)

        return step_data

    async def update_session_timestamp(self, session_id: str):
        """Update session timestamp."""
        session = await self.get_session(session_id)
        if session:
            session.updated_at = datetime.utcnow()
            await self.update_session(session)

    async def complete_session(self, session_id: str) -> OnboardingSession:
        """Mark session as completed."""
        session = await self.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.utcnow()
        session.current_step = session.total_steps

        return await self.update_session(session)

    async def abandon_session(self, session_id: str) -> OnboardingSession:
        """Mark session as abandoned."""
        session = await self.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        session.status = SessionStatus.ABANDONED

        return await self.update_session(session)

    async def create_snapshot(
        self, session_id: str, description: Optional[str] = None
    ) -> SessionSnapshot:
        """Create a session snapshot."""
        return await self.supabase_manager.create_snapshot(session_id, description)

    async def get_snapshots(self, session_id: str) -> List[SessionSnapshot]:
        """Get all snapshots for a session."""
        return await self.supabase_manager.get_snapshots(session_id)

    async def restore_from_snapshot(
        self, session_id: str, snapshot_version: int
    ) -> OnboardingSession:
        """Restore session from a snapshot."""
        # Get snapshot data
        snapshots = await self.get_snapshots(session_id)
        target_snapshot = None

        for snapshot in snapshots:
            if snapshot.version == snapshot_version:
                target_snapshot = snapshot
                break

        if not target_snapshot:
            raise HTTPException(status_code=404, detail="Snapshot not found")

        # Restore session data
        session_data = target_snapshot.snapshot_data["session"]
        session = OnboardingSession(**session_data)
        session.version = target_snapshot.version

        # Update session
        updated_session = await self.update_session(session)

        # Restore step data
        steps_data = target_snapshot.snapshot_data.get("steps", [])
        for step_dict in steps_data:
            step_data = StepData(**step_dict)
            await self.redis_manager.cache_step_data(step_data)

        logger.info(f"Restored session {session_id} from snapshot {snapshot_version}")
        return updated_session

    async def get_user_sessions(
        self, user_id: str, limit: int = 10
    ) -> List[OnboardingSession]:
        """Get all sessions for a user."""
        try:
            client = await self.supabase_manager._get_client()
            result = (
                client.table("onboarding_sessions")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            sessions = []
            for session_dict in result.data if result.data else []:
                session_dict["created_at"] = datetime.fromisoformat(
                    session_dict["created_at"].replace("Z", "+00:00")
                )
                session_dict["updated_at"] = datetime.fromisoformat(
                    session_dict["updated_at"].replace("Z", "+00:00")
                )
                if session_dict.get("completed_at"):
                    session_dict["completed_at"] = datetime.fromisoformat(
                        session_dict["completed_at"].replace("Z", "+00:00")
                    )
                sessions.append(OnboardingSession(**session_dict))

            return sessions

        except Exception as e:
            logger.error(f"Failed to get user sessions for {user_id}: {e}")
            return []

    async def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        try:
            client = await self.supabase_manager._get_client()
            expiry_date = datetime.utcnow() - timedelta(days=7)  # 7 days expiry

            # Delete expired sessions
            result = (
                client.table("onboarding_sessions")
                .delete()
                .lt("updated_at", expiry_date.isoformat())
                .execute()
            )

            logger.info(f"Cleaned up expired sessions older than {expiry_date}")

        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")


# Pydantic models for API responses
class SessionResponse(BaseModel):
    """Response model for session data."""

    id: str
    workspace_id: str
    user_id: str
    current_step: int
    total_steps: int
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict] = None
    version: int


class StepDataResponse(BaseModel):
    """Response model for step data."""

    session_id: str
    step_id: int
    status: str
    data: Dict
    updated_at: datetime
    version: int
    validation_errors: Optional[List[str]] = None


class SessionListResponse(BaseModel):
    """Response model for session list."""

    sessions: List[SessionResponse]
    total_count: int
    has_more: bool


# Error classes
class SessionError(Exception):
    """Base session error."""

    pass


class SessionNotFoundError(SessionError):
    """Session not found error."""

    pass


class SessionExpiredError(SessionError):
    """Session expired error."""

    pass


class StepValidationError(SessionError):
    """Step validation error."""

    pass
