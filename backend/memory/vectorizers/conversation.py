"""
Conversation vectorizer for conversation and session data.

This module provides the ConversationVectorizer class for converting
conversation messages into searchable vector embeddings.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from chunker import ContentChunker
from embeddings import get_embedding_model
from vector_store import VectorMemory

from ..models import MemoryChunk, MemoryType

logger = logging.getLogger(__name__)


class ConversationVectorizer:
    """
    Vectorizer for conversation and session data.

    Extracts and vectorizes conversation messages, decisions,
    action items, and key conversation elements.
    """

    def __init__(self, vector_store: Optional[VectorMemory] = None):
        """
        Initialize conversation vectorizer.

        Args:
            vector_store: Vector memory store instance
        """
        self.vector_store = vector_store or VectorMemory()
        self.embedding_model = get_embedding_model()
        self.chunker = ContentChunker(chunk_size=300, overlap=30)

        # Message type priorities for search ranking
        self.message_priorities = {
            "decision": 1.0,
            "action_item": 0.9,
            "key_insight": 0.8,
            "user_question": 0.7,
            "assistant_response": 0.6,
            "system_message": 0.5,
            "tool_call": 0.4,
            "tool_result": 0.4,
        }

    async def vectorize_conversation(
        self, workspace_id: str, session_id: str, messages: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Vectorize conversation messages and store in vector memory.

        Args:
            workspace_id: Workspace identifier
            session_id: Session identifier
            messages: List of conversation messages

        Returns:
            List of created chunk IDs
        """
        chunk_ids = []

        try:
            # Process each message
            for i, message in enumerate(messages):
                chunks = await self._vectorize_message(
                    workspace_id, session_id, message, i
                )
                chunk_ids.extend(chunks)

            # Extract and vectorize conversation-level elements
            conversation_chunks = await self._extract_conversation_elements(
                workspace_id, session_id, messages
            )
            chunk_ids.extend(conversation_chunks)

            logger.info(
                f"Vectorized conversation with {len(chunk_ids)} chunks for session {session_id}"
            )
            return chunk_ids

        except Exception as e:
            logger.error(f"Error vectorizing conversation: {e}")
            raise

    async def _vectorize_message(
        self,
        workspace_id: str,
        session_id: str,
        message: Dict[str, Any],
        message_index: int,
    ) -> List[str]:
        """
        Vectorize a single conversation message.

        Args:
            workspace_id: Workspace identifier
            session_id: Session identifier
            message: Message data
            message_index: Index of message in conversation

        Returns:
            List of created chunk IDs
        """
        chunk_ids = []

        # Extract message content
        content = message.get("content", "")
        role = message.get("role", "unknown")

        if not content or len(content.strip()) < 5:
            return chunk_ids

        # Split into chunks if needed
        chunks = self.chunker.chunk(content)

        # Create memory chunks
        for i, chunk_text in enumerate(chunks):
            metadata = {
                "session_id": session_id,
                "message_index": message_index,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "role": role,
                "priority": self.message_priorities.get(role, 0.5),
            }

            # Add role-specific metadata
            if role == "user":
                metadata["content_type"] = "user_message"
                # Check if this is a question
                if "?" in chunk_text:
                    metadata["message_type"] = "question"
            elif role == "assistant":
                metadata["content_type"] = "assistant_message"
            elif role == "system":
                metadata["content_type"] = "system_message"
            elif role == "tool":
                metadata["content_type"] = "tool_message"

            # Add tool call information if present
            if "tool_calls" in message:
                metadata["tool_calls"] = message["tool_calls"]

            chunk = MemoryChunk(
                workspace_id=workspace_id,
                memory_type=MemoryType.CONVERSATION,
                content=chunk_text,
                metadata=metadata,
                reference_id=session_id,
                reference_table="conversation_sessions",
            )

            chunk_id = await self.vector_store.store(chunk)
            chunk_ids.append(chunk_id)

        return chunk_ids

    async def _extract_conversation_elements(
        self, workspace_id: str, session_id: str, messages: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Extract and vectorize conversation-level elements.

        Args:
            workspace_id: Workspace identifier
            session_id: Session identifier
            messages: List of conversation messages

        Returns:
            List of created chunk IDs
        """
        chunk_ids = []

        try:
            # Extract decisions
            decisions = self._extract_decisions(messages)
            for decision in decisions:
                chunk = MemoryChunk(
                    workspace_id=workspace_id,
                    memory_type=MemoryType.CONVERSATION,
                    content=decision,
                    metadata={
                        "session_id": session_id,
                        "content_type": "decision",
                        "priority": 1.0,
                    },
                    reference_id=session_id,
                    reference_table="conversation_sessions",
                )
                chunk_id = await self.vector_store.store(chunk)
                chunk_ids.append(chunk_id)

            # Extract action items
            action_items = self._extract_action_items(messages)
            for action_item in action_items:
                chunk = MemoryChunk(
                    workspace_id=workspace_id,
                    memory_type=MemoryType.CONVERSATION,
                    content=action_item,
                    metadata={
                        "session_id": session_id,
                        "content_type": "action_item",
                        "priority": 0.9,
                    },
                    reference_id=session_id,
                    reference_table="conversation_sessions",
                )
                chunk_id = await self.vector_store.store(chunk)
                chunk_ids.append(chunk_id)

            # Extract key insights
            insights = self._extract_insights(messages)
            for insight in insights:
                chunk = MemoryChunk(
                    workspace_id=workspace_id,
                    memory_type=MemoryType.CONVERSATION,
                    content=insight,
                    metadata={
                        "session_id": session_id,
                        "content_type": "key_insight",
                        "priority": 0.8,
                    },
                    reference_id=session_id,
                    reference_table="conversation_sessions",
                )
                chunk_id = await self.vector_store.store(chunk)
                chunk_ids.append(chunk_id)

        except Exception as e:
            logger.error(f"Error extracting conversation elements: {e}")

        return chunk_ids

    def _extract_decisions(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        Extract decisions from conversation messages.

        Args:
            messages: List of conversation messages

        Returns:
            List of decision statements
        """
        decisions = []
        decision_keywords = [
            "decide",
            "decision",
            "chosen",
            "selected",
            "agreed",
            "concluded",
            "determined",
            "finalized",
            "approved",
        ]

        for message in messages:
            content = message.get("content", "").lower()
            if any(keyword in content for keyword in decision_keywords):
                # Extract the decision statement
                sentences = content.split(".")
                for sentence in sentences:
                    if any(keyword in sentence for keyword in decision_keywords):
                        decision = sentence.strip()
                        if len(decision) > 10:
                            decisions.append(decision)

        return decisions

    def _extract_action_items(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        Extract action items from conversation messages.

        Args:
            messages: List of conversation messages

        Returns:
            List of action item statements
        """
        action_items = []
        action_keywords = [
            "will",
            "shall",
            "need to",
            "should",
            "must",
            "action item",
            "next step",
            "follow up",
            "task",
        ]

        for message in messages:
            content = message.get("content", "").lower()
            if any(keyword in content for keyword in action_keywords):
                # Extract the action statement
                sentences = content.split(".")
                for sentence in sentences:
                    if any(keyword in sentence for keyword in action_keywords):
                        action = sentence.strip()
                        if len(action) > 10:
                            action_items.append(action)

        return action_items

    def _extract_insights(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        Extract key insights from conversation messages.

        Args:
            messages: List of conversation messages

        Returns:
            List of insight statements
        """
        insights = []
        insight_keywords = [
            "insight",
            "realize",
            "understand",
            "discover",
            "found",
            "learned",
            "observed",
            "noted",
            "interesting",
        ]

        for message in messages:
            content = message.get("content", "").lower()
            if any(keyword in content for keyword in insight_keywords):
                # Extract the insight statement
                sentences = content.split(".")
                for sentence in sentences:
                    if any(keyword in sentence for keyword in insight_keywords):
                        insight = sentence.strip()
                        if len(insight) > 10:
                            insights.append(insight)

        return insights

    async def search_conversations(
        self,
        workspace_id: str,
        query: str,
        content_type_filter: Optional[List[str]] = None,
        session_filter: Optional[str] = None,
        limit: int = 10,
    ) -> List[MemoryChunk]:
        """
        Search conversation vectors with optional filtering.

        Args:
            workspace_id: Workspace identifier
            query: Search query
            content_type_filter: Optional list of content types to filter by
            session_filter: Optional session ID to filter by
            limit: Maximum number of results

        Returns:
            List of matching memory chunks
        """
        chunks = await self.vector_store.search(
            workspace_id=workspace_id,
            query=query,
            memory_types=[MemoryType.CONVERSATION],
            limit=limit * 2,  # Get more for filtering
        )

        # Apply filters
        if content_type_filter or session_filter:
            chunks = [
                chunk
                for chunk in chunks
                if chunk.metadata
                and (
                    (
                        not content_type_filter
                        or chunk.metadata.get("content_type") in content_type_filter
                    )
                    and (
                        not session_filter
                        or chunk.metadata.get("session_id") == session_filter
                    )
                )
            ]

        # Sort by priority and relevance
        chunks.sort(
            key=lambda x: (
                x.metadata.get("priority", 0.5) if x.metadata else 0.5,
                x.score or 0.0,
            ),
            reverse=True,
        )

        return chunks[:limit]

    async def get_session_history(
        self, workspace_id: str, session_id: str, limit: int = 50
    ) -> List[MemoryChunk]:
        """
        Get conversation history for a specific session.

        Args:
            workspace_id: Workspace identifier
            session_id: Session identifier
            limit: Maximum number of results

        Returns:
            List of conversation chunks for the session
        """
        return await self.search_conversations(
            workspace_id=workspace_id, query="", session_filter=session_id, limit=limit
        )

    async def get_decisions(
        self, workspace_id: str, session_id: Optional[str] = None, limit: int = 20
    ) -> List[MemoryChunk]:
        """
        Get decisions from conversations.

        Args:
            workspace_id: Workspace identifier
            session_id: Optional session ID to filter by
            limit: Maximum number of results

        Returns:
            List of decision chunks
        """
        return await self.search_conversations(
            workspace_id=workspace_id,
            query="decision decided chosen selected",
            content_type_filter=["decision"],
            session_filter=session_id,
            limit=limit,
        )

    async def get_action_items(
        self, workspace_id: str, session_id: Optional[str] = None, limit: int = 20
    ) -> List[MemoryChunk]:
        """
        Get action items from conversations.

        Args:
            workspace_id: Workspace identifier
            session_id: Optional session ID to filter by
            limit: Maximum number of results

        Returns:
            List of action item chunks
        """
        return await self.search_conversations(
            workspace_id=workspace_id,
            query="action task next step follow up",
            content_type_filter=["action_item"],
            session_filter=session_id,
            limit=limit,
        )

    async def delete_conversation_vectors(
        self, workspace_id: str, session_id: str
    ) -> int:
        """
        Delete all vectors for a conversation session.

        Args:
            workspace_id: Workspace identifier
            session_id: Session identifier

        Returns:
            Number of deleted chunks
        """
        try:
            # Search for conversation chunks
            chunks = await self.vector_store.search(
                workspace_id=workspace_id,
                query="",
                memory_types=[MemoryType.CONVERSATION],
                limit=1000,  # Large limit to get all conversation chunks
            )

            # Filter chunks by session_id
            session_chunks = [
                chunk
                for chunk in chunks
                if chunk.metadata and chunk.metadata.get("session_id") == session_id
            ]

            # Delete chunks
            deleted_count = 0
            for chunk in session_chunks:
                if chunk.id:
                    await self.vector_store.delete(chunk.id)
                    deleted_count += 1

            logger.info(
                f"Deleted {deleted_count} conversation vectors for session {session_id}"
            )
            return deleted_count

        except Exception as e:
            logger.error(f"Error deleting conversation vectors: {e}")
            return 0
