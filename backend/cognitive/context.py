"""
Cognitive Context Builder for Integration Components

Builds comprehensive context for cognitive processing.
Implements PROMPT 63 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from ..models import Entity, EntityType


@dataclass
class ContextSource:
    """A source of context information."""

    source_type: str  # "foundation", "icp", "history", "workspace", "user"
    source_id: str
    data: Dict[str, Any]
    confidence: float  # 0-1 scale
    last_updated: datetime
    relevance_score: float  # 0-1 scale


@dataclass
class CognitiveContext:
    """Complete cognitive context for processing."""

    context_id: str
    workspace_id: str
    user_id: str
    session_id: Optional[str]

    # Core context data
    foundation_data: Dict[str, Any] = field(default_factory=dict)
    icp_data: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    workspace_context: Dict[str, Any] = field(default_factory=dict)
    user_context: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    sources: List[ContextSource] = field(default_factory=list)
    entities: List[Entity] = field(default_factory=list)
    topics: Set[str] = field(default_factory=set)
    constraints: List[Dict[str, Any]] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    # Configuration
    max_history_items: int = 50
    context_ttl_hours: int = 24


class CognitiveContextBuilder:
    """
    Builds comprehensive context for cognitive processing.

    Aggregates data from multiple sources for rich understanding.
    """

    def __init__(self, storage_client=None, cache_client=None):
        """
        Initialize the context builder.

        Args:
            storage_client: Storage client for persistent data
            cache_client: Cache client for temporary data
        """
        self.storage_client = storage_client
        self.cache_client = cache_client

        # Context source priorities
        self.source_priorities = {
            "foundation": 1.0,
            "icp": 0.9,
            "workspace": 0.8,
            "user": 0.7,
            "history": 0.6,
        }

        # Context caching
        self.context_cache: Dict[str, CognitiveContext] = {}
        self.cache_ttl = timedelta(hours=1)

    async def build_context(
        self,
        workspace_id: str,
        user_id: str,
        session_id: str = None,
        force_refresh: bool = False,
    ) -> CognitiveContext:
        """
        Build comprehensive cognitive context.

        Args:
            workspace_id: Workspace ID
            user_id: User ID
            session_id: Session ID for conversation context
            force_refresh: Force refresh of cached context

        Returns:
            Complete cognitive context
        """
        # Generate context ID
        context_id = f"{workspace_id}_{user_id}_{session_id or 'default'}"

        # Check cache first
        if not force_refresh:
            cached_context = self._get_cached_context(context_id)
            if cached_context and not self._is_context_expired(cached_context):
                cached_context.last_accessed = datetime.now()
                return cached_context

        # Build new context
        context = CognitiveContext(
            context_id=context_id,
            workspace_id=workspace_id,
            user_id=user_id,
            session_id=session_id,
        )

        # Gather context from different sources
        await self._gather_foundation_context(context)
        await self._gather_icp_context(context)
        await self._gather_workspace_context(context)
        await self._gather_user_context(context)
        await self._gather_conversation_history(context)

        # Process and enrich context
        await self._process_entities(context)
        await self._extract_topics(context)
        await self._identify_constraints(context)

        # Set expiration
        context.expires_at = datetime.now() + timedelta(hours=context.context_ttl_hours)

        # Cache the context
        self._cache_context(context)

        return context

    async def update_context(
        self, context_id: str, updates: Dict[str, Any]
    ) -> CognitiveContext:
        """
        Update an existing context with new information.

        Args:
            context_id: Context ID to update
            updates: Updates to apply

        Returns:
            Updated context
        """
        context = self._get_cached_context(context_id)
        if not context:
            raise ValueError(f"Context {context_id} not found")

        # Apply updates
        for key, value in updates.items():
            if hasattr(context, key):
                setattr(context, key, value)
            else:
                context.metadata[key] = value

        # Update timestamp
        context.last_accessed = datetime.now()

        # Re-cache
        self._cache_context(context)

        return context

    async def _gather_foundation_context(self, context: CognitiveContext) -> None:
        """Gather foundation data context."""
        if not self.storage_client:
            return

        try:
            # Get foundation data for workspace
            foundation_data = await self.storage_client.get(
                "foundation_data", context.workspace_id
            )

            if foundation_data:
                context.foundation_data = foundation_data

                # Add as context source
                source = ContextSource(
                    source_type="foundation",
                    source_id=context.workspace_id,
                    data=foundation_data,
                    confidence=0.9,
                    last_updated=datetime.now(),
                    relevance_score=self.source_priorities["foundation"],
                )
                context.sources.append(source)

        except Exception as e:
            print(f"Error gathering foundation context: {e}")

    async def _gather_icp_context(self, context: CognitiveContext) -> None:
        """Gather ICP (Ideal Customer Profile) context."""
        if not self.storage_client:
            return

        try:
            # Get ICP data for workspace
            icp_data = await self.storage_client.get(
                "icp_profiles", context.workspace_id
            )

            if icp_data:
                context.icp_data = icp_data

                # Add as context source
                source = ContextSource(
                    source_type="icp",
                    source_id=context.workspace_id,
                    data=icp_data,
                    confidence=0.8,
                    last_updated=datetime.now(),
                    relevance_score=self.source_priorities["icp"],
                )
                context.sources.append(source)

        except Exception as e:
            print(f"Error gathering ICP context: {e}")

    async def _gather_workspace_context(self, context: CognitiveContext) -> None:
        """Gather workspace-specific context."""
        if not self.storage_client:
            return

        try:
            # Get workspace information
            workspace_data = await self.storage_client.get(
                "workspaces", context.workspace_id
            )

            if workspace_data:
                context.workspace_context = workspace_data

                # Add as context source
                source = ContextSource(
                    source_type="workspace",
                    source_id=context.workspace_id,
                    data=workspace_data,
                    confidence=0.9,
                    last_updated=datetime.now(),
                    relevance_score=self.source_priorities["workspace"],
                )
                context.sources.append(source)

        except Exception as e:
            print(f"Error gathering workspace context: {e}")

    async def _gather_user_context(self, context: CognitiveContext) -> None:
        """Gather user-specific context."""
        if not self.storage_client:
            return

        try:
            # Get user preferences and history
            user_data = await self.storage_client.get("user_profiles", context.user_id)

            if user_data:
                context.user_context = user_data

                # Add as context source
                source = ContextSource(
                    source_type="user",
                    source_id=context.user_id,
                    data=user_data,
                    confidence=0.8,
                    last_updated=datetime.now(),
                    relevance_score=self.source_priorities["user"],
                )
                context.sources.append(source)

        except Exception as e:
            print(f"Error gathering user context: {e}")

    async def _gather_conversation_history(self, context: CognitiveContext) -> None:
        """Gather conversation history context."""
        if not context.session_id or not self.storage_client:
            return

        try:
            # Get conversation history
            history_key = f"conversation_{context.session_id}"
            history_data = await self.storage_client.get(
                "conversation_history", history_key
            )

            if history_data:
                # Limit to recent items
                recent_history = history_data[-context.max_history_items :]
                context.conversation_history = recent_history

                # Add as context source
                source = ContextSource(
                    source_type="history",
                    source_id=context.session_id,
                    data={"history": recent_history},
                    confidence=0.7,
                    last_updated=datetime.now(),
                    relevance_score=self.source_priorities["history"],
                )
                context.sources.append(source)

        except Exception as e:
            print(f"Error gathering conversation history: {e}")

    async def _process_entities(self, context: CognitiveContext) -> None:
        """Extract and process entities from context."""
        all_text = ""

        # Collect text from all context sources
        text_sources = [
            json.dumps(context.foundation_data),
            json.dumps(context.icp_data),
            json.dumps(context.workspace_context),
            json.dumps(context.user_context),
            json.dumps(context.conversation_history),
        ]

        all_text = " ".join(text_sources)

        # Extract entities (simple implementation)
        entities = self._extract_entities_from_text(all_text)
        context.entities = entities

    def _extract_entities_from_text(self, text: str) -> List[Entity]:
        """Extract entities from text (simple implementation)."""
        import re

        entities = []

        # Extract company names
        company_pattern = (
            r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+Inc\.?|Corp\.?|LLC|Ltd\.?)\b"
        )
        for match in re.finditer(company_pattern, text):
            entities.append(
                Entity(
                    text=match.group(),
                    type=EntityType.COMPANY,
                    confidence=0.7,
                    start_pos=match.start(),
                    end_pos=match.end(),
                )
            )

        # Extract monetary values
        money_pattern = r"\$\d+(?:,\d{3})*(?:\.\d{2})?"
        for match in re.finditer(money_pattern, text):
            entities.append(
                Entity(
                    text=match.group(),
                    type=EntityType.MONEY,
                    confidence=0.9,
                    start_pos=match.start(),
                    end_pos=match.end(),
                )
            )

        # Extract dates
        date_pattern = r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
        for match in re.finditer(date_pattern, text):
            entities.append(
                Entity(
                    text=match.group(),
                    type=EntityType.DATE,
                    confidence=0.8,
                    start_pos=match.start(),
                    end_pos=match.end(),
                )
            )

        return entities

    async def _extract_topics(self, context: CognitiveContext) -> None:
        """Extract topics from context."""
        topics = set()

        # Extract from foundation data
        if context.foundation_data:
            foundation_topics = self._extract_topics_from_dict(context.foundation_data)
            topics.update(foundation_topics)

        # Extract from ICP data
        if context.icp_data:
            icp_topics = self._extract_topics_from_dict(context.icp_data)
            topics.update(icp_topics)

        # Extract from conversation history
        if context.conversation_history:
            for item in context.conversation_history:
                if isinstance(item, dict) and "content" in item:
                    history_topics = self._extract_topics_from_text(item["content"])
                    topics.update(history_topics)

        context.topics = topics

    def _extract_topics_from_dict(self, data: Dict[str, Any]) -> Set[str]:
        """Extract topics from dictionary data."""
        topics = set()

        # Common topic fields
        topic_fields = ["industry", "sector", "category", "type", "focus", "specialty"]

        for field in topic_fields:
            if field in data:
                value = data[field]
                if isinstance(value, str):
                    topics.add(value.lower())
                elif isinstance(value, list):
                    topics.update(
                        item.lower() for item in value if isinstance(item, str)
                    )

        return topics

    def _extract_topics_from_text(self, text: str) -> Set[str]:
        """Extract topics from text (simple implementation)."""
        topics = set()

        # Common business topics
        business_topics = [
            "marketing",
            "sales",
            "finance",
            "operations",
            "technology",
            "customer",
            "product",
            "service",
            "strategy",
            "growth",
            "revenue",
            "profit",
            "cost",
            "budget",
            "investment",
        ]

        text_lower = text.lower()

        for topic in business_topics:
            if topic in text_lower:
                topics.add(topic)

        return topics

    async def _identify_constraints(self, context: CognitiveContext) -> None:
        """Identify constraints from context."""
        constraints = []

        # Budget constraints
        if context.user_context and "budget_limits" in context.user_context:
            constraints.append(
                {
                    "type": "budget",
                    "description": "User budget limits",
                    "value": context.user_context["budget_limits"],
                }
            )

        # Workspace constraints
        if context.workspace_context and "policies" in context.workspace_context:
            constraints.append(
                {
                    "type": "policy",
                    "description": "Workspace policies",
                    "value": context.workspace_context["policies"],
                }
            )

        # ICP constraints
        if context.icp_data and "restrictions" in context.icp_data:
            constraints.append(
                {
                    "type": "icp",
                    "description": "ICP-based restrictions",
                    "value": context.icp_data["restrictions"],
                }
            )

        context.constraints = constraints

    def _get_cached_context(self, context_id: str) -> Optional[CognitiveContext]:
        """Get context from cache."""
        return self.context_cache.get(context_id)

    def _cache_context(self, context: CognitiveContext) -> None:
        """Cache context."""
        self.context_cache[context.context_id] = context

        # Clean old contexts if cache is too large
        if len(self.context_cache) > 100:
            self._cleanup_cache()

    def _is_context_expired(self, context: CognitiveContext) -> bool:
        """Check if context is expired."""
        if context.expires_at:
            return datetime.now() > context.expires_at

        # Default TTL check
        return datetime.now() > context.created_at + self.cache_ttl

    def _cleanup_cache(self) -> None:
        """Clean up expired contexts from cache."""
        now = datetime.now()

        expired_contexts = [
            context_id
            for context_id, context in self.context_cache.items()
            if self._is_context_expired(context)
        ]

        for context_id in expired_contexts:
            del self.context_cache[context_id]

    async def get_context_summary(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of context without full data."""
        context = self._get_cached_context(context_id)
        if not context:
            return None

        return {
            "context_id": context.context_id,
            "workspace_id": context.workspace_id,
            "user_id": context.user_id,
            "session_id": context.session_id,
            "sources_count": len(context.sources),
            "entities_count": len(context.entities),
            "topics_count": len(context.topics),
            "constraints_count": len(context.constraints),
            "created_at": context.created_at.isoformat(),
            "last_accessed": context.last_accessed.isoformat(),
            "expires_at": (
                context.expires_at.isoformat() if context.expires_at else None
            ),
            "source_types": list(set(source.source_type for source in context.sources)),
        }

    async def search_contexts(
        self, workspace_id: str = None, user_id: str = None, topics: List[str] = None
    ) -> List[str]:
        """Search for contexts matching criteria."""
        matching_contexts = []

        for context_id, context in self.context_cache.items():
            # Check workspace filter
            if workspace_id and context.workspace_id != workspace_id:
                continue

            # Check user filter
            if user_id and context.user_id != user_id:
                continue

            # Check topics filter
            if topics and not any(topic in context.topics for topic in topics):
                continue

            matching_contexts.append(context_id)

        return matching_contexts

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_contexts = len(self.context_cache)
        expired_contexts = sum(
            1
            for context in self.context_cache.values()
            if self._is_context_expired(context)
        )

        source_type_counts = {}
        for context in self.context_cache.values():
            for source in context.sources:
                source_type = source.source_type
                source_type_counts[source_type] = (
                    source_type_counts.get(source_type, 0) + 1
                )

        return {
            "total_cached_contexts": total_contexts,
            "expired_contexts": expired_contexts,
            "active_contexts": total_contexts - expired_contexts,
            "source_type_distribution": source_type_counts,
            "cache_hit_ratio": getattr(self, "cache_hits", 0)
            / max(getattr(self, "cache_requests", 1), 1),
        }
