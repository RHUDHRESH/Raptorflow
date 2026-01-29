"""
Redis integration for agent sessions.
Persists and restores agent state from Redis for checkpoint/resume functionality.
"""

import json
import logging
import time
from typing import Any, Dict, Optional

from .agents.state import AgentState
from .redis.client import Redis

logger = logging.getLogger(__name__)


async def persist_agent_state(
    session_id: str, state: AgentState, redis_client: Redis
) -> bool:
    """
    Persist agent state to Redis.

    Args:
        session_id: Session identifier
        state: Agent state to persist
        redis_client: Redis client

    Returns:
        Success status
    """
    try:
        # Prepare state for storage
        serializable_state = _prepare_state_for_storage(state)

        # Store in Redis with TTL
        key = f"agent_session:{session_id}"
        ttl = 3600 * 24  # 24 hours

        await redis_client.setex(key, ttl, json.dumps(serializable_state))

        # Store session metadata
        metadata_key = f"agent_session_meta:{session_id}"
        metadata = {
            "session_id": session_id,
            "workspace_id": state.get("workspace_id"),
            "user_id": state.get("user_id"),
            "current_agent": state.get("current_agent"),
            "created_at": time.time(),
            "last_updated": time.time(),
            "messages_count": len(state.get("messages", [])),
            "tokens_used": state.get("tokens_used", 0),
            "cost_usd": state.get("cost_usd", 0.0),
        }

        await redis_client.setex(metadata_key, ttl, json.dumps(metadata))

        logger.info(f"Persisted agent state for session {session_id}")

        return True

    except Exception as e:
        logger.error(f"Error persisting agent state: {e}")
        return False


async def restore_agent_state(
    session_id: str, redis_client: Redis
) -> Optional[AgentState]:
    """
    Restore agent state from Redis.

    Args:
        session_id: Session identifier
        redis_client: Redis client

    Returns:
        Restored agent state or None
    """
    try:
        key = f"agent_session:{session_id}"

        # Check if session exists
        if not await redis_client.exists(key):
            logger.info(f"No agent state found for session {session_id}")
            return None

        # Get serialized state
        serialized_state = await redis_client.get(key)
        if not serialized_state:
            return None

        # Deserialize state
        state_data = json.loads(serialized_state)

        # Restore state
        state = _restore_state_from_storage(state_data)

        # Update last accessed time
        metadata_key = f"agent_session_meta:{session_id}"
        if await redis_client.exists(metadata_key):
            metadata = json.loads(await redis_client.get(metadata_key))
            metadata["last_updated"] = time.time()
            await redis_client.setex(metadata_key, 3600 * 24, json.dumps(metadata))

        logger.info(f"Restored agent state for session {session_id}")

        return state

    except Exception as e:
        logger.error(f"Error restoring agent state: {e}")
        return None


def _prepare_state_for_storage(state: AgentState) -> Dict[str, Any]:
    """
    Prepare agent state for Redis storage.

    Args:
        state: Agent state

    Returns:
        Serializable state dictionary
    """
    serializable = {}

    # Copy basic fields
    for key, value in state.items():
        if key in [
            "workspace_id",
            "user_id",
            "session_id",
            "current_agent",
            "messages",
            "tokens_used",
            "cost_usd",
            "pending_approval",
            "approval_gate_id",
            "error",
            "output",
        ]:
            serializable[key] = value
        elif key in [
            "routing_path",
            "memory_context",
            "foundation_summary",
            "active_icps",
        ]:
            # These might contain complex objects, convert to strings
            serializable[key] = str(value) if value is not None else None
        else:
            # Skip complex objects that can't be serialized
            continue

    return serializable


def _restore_state_from_storage(state_data: Dict[str, Any]) -> AgentState:
    """
    Restore agent state from stored data.

    Args:
        state_data: Stored state data

    Returns:
        Restored agent state
    """
    state = AgentState()

    # Restore basic fields
    for key, value in state_data.items():
        if key in ["workspace_id", "user_id", "session_id", "current_agent"]:
            state[key] = value
        elif key in ["messages", "tokens_used", "cost_usd"]:
            state[key] = value if value is not None else []
        elif key in ["pending_approval", "approval_gate_id"]:
            state[key] = value
        elif key in [
            "routing_path",
            "memory_context",
            "foundation_summary",
            "active_icps",
        ]:
            # Convert back from string representation
            state[key] = value
        elif key == "error":
            state[key] = value

    return state


async def list_active_sessions(redis_client: Redis, workspace_id: str = None) -> list:
    """
    List active agent sessions.

    Args:
        redis_client: Redis client
        workspace_id: Optional workspace ID filter

    Returns:
        List of session metadata
    """
    try:
        pattern = "agent_session_meta:*"
        if workspace_id:
            pattern = f"agent_session_meta:*"  # Would need to filter after

        keys = await redis_client.keys(pattern)

        sessions = []
        for key in keys:
            metadata = await redis_client.get(key)
            if metadata:
                session_data = json.loads(metadata)
                if not workspace_id or session_data.get("workspace_id") == workspace_id:
                    sessions.append(session_data)

        return sessions

    except Exception as e:
        logger.error(f"Error listing active sessions: {e}")
        return []


async def delete_agent_session(session_id: str, redis_client: Redis) -> bool:
    """
    Delete agent session from Redis.

    Args:
        session_id: Session identifier
        redis_client: Redis client

    Returns:
        Success status
    """
    try:
        # Delete session state
        state_key = f"agent_session:{session_id}"
        await redis_client.delete(state_key)

        # Delete metadata
        metadata_key = f"agent_session_meta:{session_id}"
        await redis_client.delete(metadata_key)

        logger.info(f"Deleted agent session {session_id}")

        return True

    except Exception as e:
        logger.error(f"Error deleting agent session: {e}")
        return False


class SessionManager:
    """
    Manages agent sessions with Redis persistence.
    """

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.active_sessions = {}

    async def create_session(
        self, workspace_id: str, user_id: str, initial_state: AgentState = None
    ) -> str:
        """
        Create new agent session.

        Args:
            workspace_id: Workspace ID
            user_id: User ID
            initial_state: Initial agent state

        Returns:
            Session ID
        """
        session_id = f"session_{workspace_id}_{user_id}_{int(time.time())}"

        # Create initial state if not provided
        if not initial_state:
            initial_state = AgentState()

        initial_state.update(
            {
                "session_id": session_id,
                "workspace_id": workspace_id,
                "user_id": user_id,
                "created_at": time.time(),
            }
        )

        # Persist session
        await self.persist_session(session_id, initial_state)

        # Track in memory
        self.active_sessions[session_id] = initial_state

        logger.info(f"Created new agent session: {session_id}")

        return session_id

    async def persist_session(self, session_id: str, state: AgentState) -> bool:
        """
        Persist session state to Redis.

        Args:
            session_id: Session ID
            state: Agent state

        Returns:
            Success status
        """
        success = await persist_agent_state(session_id, state, self.redis_client)

        if success:
            self.active_sessions[session_id] = state

        return success

    async def get_session(self, session_id: str) -> Optional[AgentState]:
        """
        Get session state.

        Args:
            session_id: Session ID

        Returns:
            Agent state or None
        """
        # Check memory first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]

        # Try Redis
        state = await restore_agent_state(session_id, self.redis_client)

        if state:
            self.active_sessions[session_id] = state

        return state

    async def update_session(self, session_id: str, **updates) -> bool:
        """
        Update session with new data.

        Args:
            session_id: Session ID
            **updates: Updates to apply

        Returns:
            Success status
        """
        state = await self.get_session(session_id)

        if not state:
            return False

        state.update(updates)
        state["last_updated"] = time.time()

        return await self.persist_session(session_id, state)

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete session.

        Args:
            session_id: Session ID

        Returns:
            Success status
        """
        # Remove from memory
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

        # Delete from Redis
        return await delete_agent_session(session_id, self.redis_client)

    async def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """
        Clean up expired sessions.

        Args:
            max_age_hours: Maximum age in hours
        """
        current_time = time.time()
        expired_sessions = []

        for session_id, state in self.active_sessions.items():
            age_hours = (current_time - state.get("created_at", 0)) / 3600
            if age_hours > max_age_hours:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            await self.delete_session(session_id)

        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
