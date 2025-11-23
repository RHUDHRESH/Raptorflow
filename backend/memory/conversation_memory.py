"""
Conversation Memory - Session-Based Message Storage

This module implements short-term conversation memory using Redis as the backend.
Conversation memory stores message history for active sessions with automatic expiration.

Purpose:
--------
- Store conversation history for active user sessions
- Enable context-aware responses by providing message history to agents
- Automatically expire old sessions to manage memory usage
- Support rapid access to recent conversation context

Schema:
-------
Key Pattern: "conversation:{workspace_id}:{session_id}"
Value: JSON list of message objects
Each message:
{
    "role": str,           # "user", "assistant", "system"
    "content": str,        # Message content
    "timestamp": str,      # ISO 8601 timestamp
    "metadata": dict       # Optional metadata (agent_name, correlation_id, etc.)
}

TTL: 3600 seconds (1 hour) - automatically expires after inactivity

Storage Backend: Redis
- Fast in-memory access for real-time conversations
- Built-in TTL support for automatic cleanup
- Atomic list operations for thread-safe message appending

Dependencies:
-------------
- redis: For Redis client and connection pooling
- json: For serializing message objects
- datetime: For timestamp management
- config.settings: For Redis connection configuration

Usage Example:
--------------
from memory.conversation_memory import ConversationMemory
from uuid import UUID
from datetime import datetime

# Initialize conversation memory
conv_memory = ConversationMemory()

# Store a user message
await conv_memory.remember(
    key="session:abc123",
    value={
        "role": "user",
        "content": "Help me create a campaign",
        "timestamp": datetime.utcnow().isoformat()
    },
    workspace_id=UUID("..."),
    ttl=3600  # 1 hour
)

# Retrieve conversation history
messages = await conv_memory.recall(
    key="session:abc123",
    workspace_id=UUID("..."),
    default=[]
)

# Search recent messages
results = await conv_memory.search(
    query="campaign",
    workspace_id=UUID("..."),
    top_k=5
)
"""

import json
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime
import redis.asyncio as redis
from redis.asyncio import ConnectionPool
import structlog

from memory.base import BaseMemory, MemoryError
from config.settings import settings

logger = structlog.get_logger()


class ConversationMemory(BaseMemory):
    """
    Redis-based conversation memory for session-based message storage.

    This class manages conversation history using Redis lists, with automatic
    expiration to prevent memory bloat. Each session's messages are stored
    as a time-ordered list with TTL support.

    Attributes:
        redis_client: Async Redis client instance
        default_ttl: Default time-to-live in seconds (3600 = 1 hour)
        max_messages_per_session: Maximum messages to keep per session
    """

    def __init__(self, default_ttl: int = 3600, max_messages: int = 100):
        """
        Initialize conversation memory with Redis connection.

        Args:
            default_ttl: Default TTL in seconds for conversation sessions (default: 1 hour)
            max_messages: Maximum number of messages to keep per session (default: 100)
        """
        super().__init__(memory_type="conversation")
        self.default_ttl = default_ttl
        self.max_messages_per_session = max_messages
        self.redis_client: Optional[redis.Redis] = None
        self._pool: Optional[ConnectionPool] = None

    async def _get_client(self) -> redis.Redis:
        """
        Get or create Redis client with connection pooling.

        Returns:
            Async Redis client instance

        Raises:
            MemoryError: If connection to Redis fails
        """
        if self.redis_client is None:
            try:
                self._pool = ConnectionPool.from_url(
                    settings.REDIS_URL,
                    max_connections=settings.REDIS_MAX_CONNECTIONS,
                    socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                    decode_responses=True  # Auto-decode bytes to strings
                )
                self.redis_client = redis.Redis(connection_pool=self._pool)
                # Test connection
                await self.redis_client.ping()
                self.logger.info("Connected to Redis for conversation memory")
            except Exception as e:
                self.logger.error("Failed to connect to Redis", error=str(e))
                raise MemoryError(
                    f"Failed to connect to Redis: {str(e)}",
                    memory_type=self.memory_type,
                    operation="connect"
                )
        return self.redis_client

    def _make_key(self, key: str, workspace_id: UUID) -> str:
        """
        Generate Redis key with workspace prefix.

        Args:
            key: Session key (e.g., "session:abc123")
            workspace_id: Workspace UUID

        Returns:
            Full Redis key: "conversation:{workspace_id}:{key}"
        """
        return f"conversation:{workspace_id}:{key}"

    async def remember(
        self,
        key: str,
        value: Any,
        workspace_id: UUID,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> None:
        """
        Store a message in conversation history.

        Appends the message to the session's message list and sets/refreshes TTL.
        If the list exceeds max_messages, older messages are trimmed.

        Args:
            key: Session identifier (e.g., "session:abc123")
            value: Message object or dict to store
            workspace_id: Workspace UUID
            metadata: Optional metadata to merge with message
            ttl: Optional TTL override (seconds)

        Raises:
            MemoryError: If Redis operation fails
        """
        self._validate_workspace_id(workspace_id)
        client = await self._get_client()
        redis_key = self._make_key(key, workspace_id)
        ttl_seconds = ttl or self.default_ttl

        try:
            # Ensure value is a dict
            if isinstance(value, str):
                message = {"content": value, "role": "user"}
            elif isinstance(value, dict):
                message = value.copy()
            else:
                message = {"content": str(value), "role": "system"}

            # Add timestamp if not present
            if "timestamp" not in message:
                message["timestamp"] = datetime.utcnow().isoformat()

            # Merge metadata if provided
            if metadata:
                if "metadata" not in message:
                    message["metadata"] = {}
                message["metadata"].update(metadata)

            # Serialize message
            message_json = json.dumps(message)

            # Append to list
            await client.rpush(redis_key, message_json)

            # Trim list if it exceeds max messages
            list_length = await client.llen(redis_key)
            if list_length > self.max_messages_per_session:
                # Keep only the most recent max_messages
                await client.ltrim(redis_key, -self.max_messages_per_session, -1)

            # Set/refresh TTL
            await client.expire(redis_key, ttl_seconds)

            self.logger.debug(
                "Stored conversation message",
                key=key,
                workspace_id=str(workspace_id),
                ttl=ttl_seconds
            )

        except Exception as e:
            self.logger.error(
                "Failed to store conversation message",
                key=key,
                error=str(e)
            )
            raise MemoryError(
                f"Failed to store conversation message: {str(e)}",
                memory_type=self.memory_type,
                operation="remember"
            )

    async def recall(
        self,
        key: str,
        workspace_id: UUID,
        default: Any = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all messages from a conversation session.

        Args:
            key: Session identifier
            workspace_id: Workspace UUID
            default: Default value if session not found (default: None)

        Returns:
            List of message dictionaries, ordered chronologically

        Raises:
            MemoryError: If Redis operation fails
        """
        self._validate_workspace_id(workspace_id)
        client = await self._get_client()
        redis_key = self._make_key(key, workspace_id)

        try:
            # Get all messages from list
            messages_json = await client.lrange(redis_key, 0, -1)

            if not messages_json:
                self.logger.debug(
                    "No conversation found, returning default",
                    key=key,
                    workspace_id=str(workspace_id)
                )
                return default if default is not None else []

            # Deserialize messages
            messages = [json.loads(msg) for msg in messages_json]

            self.logger.debug(
                "Recalled conversation messages",
                key=key,
                workspace_id=str(workspace_id),
                message_count=len(messages)
            )

            return messages

        except Exception as e:
            self.logger.error(
                "Failed to recall conversation",
                key=key,
                error=str(e)
            )
            raise MemoryError(
                f"Failed to recall conversation: {str(e)}",
                memory_type=self.memory_type,
                operation="recall"
            )

    async def search(
        self,
        query: str,
        workspace_id: UUID,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for messages containing the query string.

        Performs simple keyword search across all sessions in the workspace.
        For more advanced semantic search, use SemanticMemory instead.

        Args:
            query: Search query string
            workspace_id: Workspace UUID
            top_k: Maximum number of results to return
            filters: Optional filters (e.g., session_id, role, date_from)

        Returns:
            List of matching messages with context

        Raises:
            MemoryError: If search operation fails
        """
        self._validate_workspace_id(workspace_id)
        client = await self._get_client()

        try:
            # Get all conversation keys for this workspace
            pattern = f"conversation:{workspace_id}:*"
            keys = []
            async for key in client.scan_iter(match=pattern):
                keys.append(key)

            results = []
            query_lower = query.lower()

            # Search through all sessions
            for redis_key in keys:
                messages_json = await client.lrange(redis_key, 0, -1)
                session_id = redis_key.split(":")[-1]

                for msg_json in messages_json:
                    message = json.loads(msg_json)

                    # Apply filters if provided
                    if filters:
                        if "role" in filters and message.get("role") != filters["role"]:
                            continue
                        if "session_id" in filters and session_id != filters["session_id"]:
                            continue

                    # Check if query matches content
                    content = message.get("content", "").lower()
                    if query_lower in content:
                        result = message.copy()
                        result["session_id"] = session_id
                        results.append(result)

                        if len(results) >= top_k:
                            break

                if len(results) >= top_k:
                    break

            self.logger.debug(
                "Conversation search completed",
                query=query,
                workspace_id=str(workspace_id),
                results_count=len(results)
            )

            return results[:top_k]

        except Exception as e:
            self.logger.error(
                "Failed to search conversations",
                query=query,
                error=str(e)
            )
            raise MemoryError(
                f"Failed to search conversations: {str(e)}",
                memory_type=self.memory_type,
                operation="search"
            )

    async def forget(
        self,
        key: str,
        workspace_id: UUID
    ) -> bool:
        """
        Delete a conversation session.

        Args:
            key: Session identifier to delete
            workspace_id: Workspace UUID

        Returns:
            True if deletion was successful

        Raises:
            MemoryError: If deletion operation fails
        """
        self._validate_workspace_id(workspace_id)
        client = await self._get_client()
        redis_key = self._make_key(key, workspace_id)

        try:
            deleted = await client.delete(redis_key)

            self.logger.debug(
                "Conversation session deleted",
                key=key,
                workspace_id=str(workspace_id),
                deleted=bool(deleted)
            )

            return bool(deleted)

        except Exception as e:
            self.logger.error(
                "Failed to delete conversation",
                key=key,
                error=str(e)
            )
            raise MemoryError(
                f"Failed to delete conversation: {str(e)}",
                memory_type=self.memory_type,
                operation="forget"
            )

    async def learn_from_feedback(
        self,
        key: str,
        feedback: Dict[str, Any],
        workspace_id: UUID
    ) -> None:
        """
        Update conversation based on feedback.

        For conversation memory, this is typically not used, but could be
        implemented to tag or annotate specific messages with feedback.

        Args:
            key: Session identifier
            feedback: Feedback data
            workspace_id: Workspace UUID
        """
        self.logger.debug(
            "learn_from_feedback not implemented for conversation memory",
            key=key,
            workspace_id=str(workspace_id)
        )
        # Could be extended to add feedback annotations to messages

    async def clear(self, workspace_id: UUID) -> bool:
        """
        Clear all conversation sessions for a workspace.

        Args:
            workspace_id: Workspace UUID to clear

        Returns:
            True if clearing was successful

        Raises:
            MemoryError: If clear operation fails
        """
        self._validate_workspace_id(workspace_id)
        client = await self._get_client()

        try:
            pattern = f"conversation:{workspace_id}:*"
            keys = []
            async for key in client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                await client.delete(*keys)

            self.logger.info(
                "Cleared all conversations for workspace",
                workspace_id=str(workspace_id),
                cleared_count=len(keys)
            )

            return True

        except Exception as e:
            self.logger.error(
                "Failed to clear conversations",
                workspace_id=str(workspace_id),
                error=str(e)
            )
            raise MemoryError(
                f"Failed to clear conversations: {str(e)}",
                memory_type=self.memory_type,
                operation="clear"
            )

    async def close(self):
        """Close Redis connection and cleanup resources."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
        self.logger.info("Closed conversation memory Redis connection")
