"""
AgentMemoryManager for Raptorflow agent system.
Manages agent memory, context persistence, and knowledge retrieval.
"""

import asyncio
import hashlib
import json
import logging
import re
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from ..base import BaseAgent
from backend.agents.config import ModelTier
from ..exceptions import MemoryError, ValidationError
from ..state import AgentState

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Memory types."""

    EPISODIC = "episodic"  # Specific events and experiences
    SEMANTIC = "semantic"  # General knowledge and facts
    PROCEDURAL = "procedural"  # Skills and procedures
    WORKING = "working"  # Temporary active memory
    LONG_TERM = "long_term"  # Persistent storage


class MemoryStatus(Enum):
    """Memory status."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    FORGOTTEN = "forgotten"
    CORRUPTED = "corrupted"


class RetrievalMethod(Enum):
    """Memory retrieval methods."""

    EXACT_MATCH = "exact_match"
    SEMANTIC_SEARCH = "semantic_search"
    CONTEXTUAL = "contextual"
    TEMPORAL = "temporal"
    ASSOCIATIVE = "associative"


@dataclass
class MemoryEntry:
    """Memory entry."""

    memory_id: str
    memory_type: MemoryType
    agent_id: str
    workspace_id: str
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    last_accessed: datetime
    access_count: int
    importance_score: float
    tags: List[str] = field(default_factory=list)
    related_memories: List[str] = field(default_factory=list)
    expires_at: Optional[datetime] = None
    status: MemoryStatus = MemoryStatus.ACTIVE


@dataclass
class MemoryFragment:
    """Memory fragment for partial retrieval."""

    fragment_id: str
    memory_id: str
    content: str
    context: Dict[str, Any]
    relevance_score: float
    extracted_at: datetime


@dataclass
class MemoryAssociation:
    """Association between memories."""

    association_id: str
    source_memory_id: str
    target_memory_id: str
    association_type: str
    strength: float
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryQuery:
    """Memory query for retrieval."""

    query_id: str
    query_text: str
    agent_id: str
    workspace_id: str
    retrieval_method: RetrievalMethod
    filters: Dict[str, Any] = field(default_factory=dict)
    limit: int = 10
    threshold: float = 0.5
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryResult:
    """Memory retrieval result."""

    query_id: str
    memories: List[MemoryEntry]
    fragments: List[MemoryFragment]
    relevance_scores: List[float]
    retrieval_time_ms: float
    total_found: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryConfig:
    """Memory manager configuration."""

    max_working_memory_size: int = 100
    max_long_term_memory_size: int = 10000
    memory_ttl_days: int = 30
    consolidation_interval_hours: int = 24
    importance_decay_rate: float = 0.1
    association_threshold: float = 0.3
    compression_enabled: bool = True
    indexing_enabled: bool = True
    semantic_search_enabled: bool = True


class AgentMemoryManager:
    """Manages agent memory with intelligent storage and retrieval."""

    def __init__(self, config: MemoryConfig = None):
        self.config = config or MemoryConfig()

        # Memory storage
        self._memories: Dict[str, MemoryEntry] = {}
        self._working_memory: deque = deque(maxlen=self.config.max_working_memory_size)
        self._long_term_memory: Dict[str, MemoryEntry] = {}
        self._memory_fragments: Dict[str, List[MemoryFragment]] = defaultdict(list)

        # Associations
        self._associations: Dict[str, List[MemoryAssociation]] = defaultdict(list)
        self._association_index: Dict[str, set] = defaultdict(set)

        # Indexes
        self._content_index: Dict[str, set] = defaultdict(
            set
        )  # Content keywords to memory IDs
        self._tag_index: Dict[str, set] = defaultdict(set)  # Tags to memory IDs
        self._temporal_index: List[tuple] = []  # (timestamp, memory_id)

        # Background tasks
        self._background_tasks: Set[asyncio.Task] = set()
        self._running = False

        # Event handlers
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)

        # Locks
        self._memory_lock = asyncio.Lock()

        # Statistics
        self._stats = {
            "memories_created": 0,
            "memories_accessed": 0,
            "memories_forgotten": 0,
            "associations_created": 0,
            "queries_executed": 0,
            "consolidations_run": 0,
        }

        # Start background tasks
        self._start_background_tasks()

    async def store_memory(
        self,
        memory_type: MemoryType,
        agent_id: str,
        workspace_id: str,
        content: Dict[str, Any],
        metadata: Dict[str, Any] = None,
        tags: List[str] = None,
        importance_score: float = 0.5,
        ttl_days: int = None,
    ) -> str:
        """Store a new memory."""
        async with self._memory_lock:
            # Generate memory ID
            memory_id = str(uuid.uuid4())

            # Create memory entry
            memory = MemoryEntry(
                memory_id=memory_id,
                memory_type=memory_type,
                agent_id=agent_id,
                workspace_id=workspace_id,
                content=content.copy(),
                metadata=metadata or {},
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=0,
                importance_score=importance_score,
                tags=tags or [],
                expires_at=datetime.now()
                + timedelta(days=ttl_days or self.config.memory_ttl_days),
            )

            # Store in appropriate memory
            if memory_type == MemoryType.WORKING:
                self._working_memory.append(memory)
            else:
                self._long_term_memory[memory_id] = memory

            # Add to main storage
            self._memories[memory_id] = memory

            # Index content
            if self.config.indexing_enabled:
                await self._index_memory(memory)

            # Create associations
            await self._create_associations(memory)

            # Update statistics
            self._stats["memories_created"] += 1

            # Emit event
            await self._emit_event(
                "memory_stored",
                {
                    "memory_id": memory_id,
                    "memory_type": memory_type.value,
                    "agent_id": agent_id,
                    "workspace_id": workspace_id,
                },
            )

            logger.info(f"Stored memory: {memory_id} ({memory_type.value})")

            return memory_id

    async def retrieve_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a specific memory."""
        async with self._memory_lock:
            memory = self._memories.get(memory_id)

            if not memory:
                return None

            # Check if memory is expired
            if memory.expires_at and datetime.now() > memory.expires_at:
                await self._forget_memory(memory_id)
                return None

            # Update access statistics
            memory.last_accessed = datetime.now()
            memory.access_count += 1

            # Update importance based on access
            await self._update_importance(memory)

            # Update statistics
            self._stats["memories_accessed"] += 1

            return memory

    async def search_memories(self, query: MemoryQuery) -> MemoryResult:
        """Search memories based on query."""
        start_time = datetime.now()

        async with self._memory_lock:
            # Update statistics
            self._stats["queries_executed"] += 1

            # Perform search based on method
            if query.retrieval_method == RetrievalMethod.EXACT_MATCH:
                memories, scores = await self._exact_match_search(query)
            elif query.retrieval_method == RetrievalMethod.SEMANTIC_SEARCH:
                memories, scores = await self._semantic_search(query)
            elif query.retrieval_method == RetrievalMethod.CONTEXTUAL:
                memories, scores = await self._contextual_search(query)
            elif query.retrieval_method == RetrievalMethod.TEMPORAL:
                memories, scores = await self._temporal_search(query)
            elif query.retrieval_method == RetrievalMethod.ASSOCIATIVE:
                memories, scores = await self._associative_search(query)
            else:
                memories, scores = await self._default_search(query)

            # Extract fragments
            fragments = await self._extract_fragments(memories, query)

            # Calculate retrieval time
            retrieval_time_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Create result
            result = MemoryResult(
                query_id=query.query_id,
                memories=memories[: query.limit],
                fragments=fragments,
                relevance_scores=scores[: query.limit],
                retrieval_time_ms=retrieval_time_ms,
                total_found=len(memories),
                metadata={
                    "method": query.retrieval_method.value,
                    "threshold": query.threshold,
                    "filters_applied": len(query.filters),
                },
            )

            return result

    async def update_memory(
        self,
        memory_id: str,
        content: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None,
        tags: List[str] = None,
        importance_score: float = None,
    ) -> bool:
        """Update an existing memory."""
        async with self._memory_lock:
            memory = self._memories.get(memory_id)

            if not memory:
                raise MemoryError(f"Memory not found: {memory_id}")

            # Update fields
            if content is not None:
                memory.content = content.copy()
                # Re-index content
                if self.config.indexing_enabled:
                    await self._reindex_memory(memory)

            if metadata is not None:
                memory.metadata = metadata.copy()

            if tags is not None:
                # Update tag index
                await self._update_tag_index(memory, tags)
                memory.tags = tags.copy()

            if importance_score is not None:
                memory.importance_score = importance_score

            # Update last accessed
            memory.last_accessed = datetime.now()

            logger.info(f"Updated memory: {memory_id}")

            return True

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory."""
        async with self._memory_lock:
            memory = self._memories.get(memory_id)

            if not memory:
                raise MemoryError(f"Memory not found: {memory_id}")

            # Remove from storage
            if memory_id in self._long_term_memory:
                del self._long_term_memory[memory_id]

            # Remove from working memory
            working_memory_list = list(self._working_memory)
            self._working_memory.clear()
            for mem in working_memory_list:
                if mem.memory_id != memory_id:
                    self._working_memory.append(mem)

            # Remove from main storage
            del self._memories[memory_id]

            # Remove from indexes
            await self._remove_from_indexes(memory_id)

            # Remove associations
            await self._remove_associations(memory_id)

            # Update statistics
            self._stats["memories_forgotten"] += 1

            # Emit event
            await self._emit_event(
                "memory_deleted",
                {
                    "memory_id": memory_id,
                    "agent_id": memory.agent_id,
                    "workspace_id": memory.workspace_id,
                },
            )

            logger.info(f"Deleted memory: {memory_id}")

            return True

    async def create_association(
        self,
        source_memory_id: str,
        target_memory_id: str,
        association_type: str,
        strength: float = 0.5,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """Create an association between memories."""
        async with self._memory_lock:
            # Check if memories exist
            if (
                source_memory_id not in self._memories
                or target_memory_id not in self._memories
            ):
                raise MemoryError("One or both memories not found")

            # Create association
            association = MemoryAssociation(
                association_id=str(uuid.uuid4()),
                source_memory_id=source_memory_id,
                target_memory_id=target_memory_id,
                association_type=association_type,
                strength=strength,
                created_at=datetime.now(),
                metadata=metadata or {},
            )

            # Store association
            self._associations[source_memory_id].append(association)
            self._association_index[source_memory_id].add(target_memory_id)

            # Update memory relationships
            self._memories[source_memory_id].related_memories.append(target_memory_id)
            self._memories[target_memory_id].related_memories.append(source_memory_id)

            # Update statistics
            self._stats["associations_created"] += 1

            logger.info(
                f"Created association: {source_memory_id} -> {target_memory_id} ({association_type})"
            )

            return association.association_id

    async def get_related_memories(
        self, memory_id: str, max_depth: int = 2
    ) -> List[MemoryEntry]:
        """Get memories related to a given memory."""
        async with self._memory_lock:
            related = set()
            visited = set()
            queue = [(memory_id, 0)]

            while queue:
                current_id, depth = queue.pop(0)

                if current_id in visited or depth > max_depth:
                    continue

                visited.add(current_id)

                # Get direct associations
                for association in self._associations[current_id]:
                    target_id = association.target_memory_id

                    if target_id in self._memories and target_id not in visited:
                        related.add(target_id)
                        queue.append((target_id, depth + 1))

            # Convert to memory entries
            return [
                self._memories[memory_id]
                for memory_id in related
                if memory_id in self._memories
            ]

    async def consolidate_memories(self) -> int:
        """Consolidate and optimize memory storage."""
        async with self._memory_lock:
            consolidated_count = 0

            # Move old working memories to long-term
            working_memories = list(self._working_memory)
            for memory in working_memories:
                if (
                    datetime.now() - memory.created_at
                ).total_seconds() > 3600:  # 1 hour
                    # Move to long-term memory
                    self._long_term_memory[memory.memory_id] = memory

                    # Remove from working memory
                    self._working_memory = deque(
                        [
                            m
                            for m in self._working_memory
                            if m.memory_id != memory.memory_id
                        ],
                        maxlen=self.config.max_working_memory_size,
                    )

                    consolidated_count += 1

            # Decay importance scores
            for memory in self._memories.values():
                memory.importance_score *= 1 - self.config.importance_decay_rate

            # Remove expired memories
            expired_count = await self._remove_expired_memories()

            # Update statistics
            self._stats["consolidations_run"] += 1

            logger.info(
                f"Consolidated {consolidated_count} memories, removed {expired_count} expired"
            )

            return consolidated_count + expired_count

    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        async with self._memory_lock:
            # Count by type
            type_counts = defaultdict(int)
            for memory in self._memories.values():
                type_counts[memory.memory_type.value] += 1

            # Count by status
            status_counts = defaultdict(int)
            for memory in self._memories.values():
                status_counts[memory.status.value] += 1

            # Calculate average importance
            importance_scores = [m.importance_score for m in self._memories.values()]
            avg_importance = (
                sum(importance_scores) / len(importance_scores)
                if importance_scores
                else 0
            )

            return {
                "total_memories": len(self._memories),
                "working_memory_size": len(self._working_memory),
                "long_term_memory_size": len(self._long_term_memory),
                "memory_types": dict(type_counts),
                "memory_statuses": dict(status_counts),
                "total_associations": sum(
                    len(associations) for associations in self._associations.values()
                ),
                "average_importance": avg_importance,
                "index_entries": len(self._content_index) + len(self._tag_index),
                "statistics": self._stats.copy(),
            }

    async def _index_memory(self, memory: MemoryEntry):
        """Index memory content for search."""
        # Index content keywords
        content_text = json.dumps(memory.content, default=str)
        keywords = self._extract_keywords(content_text)

        for keyword in keywords:
            self._content_index[keyword].add(memory.memory_id)

        # Index tags
        for tag in memory.tags:
            self._tag_index[tag].add(memory.memory_id)

        # Index temporally
        self._temporal_index.append((memory.created_at, memory.memory_id))
        self._temporal_index.sort(key=lambda x: x[0])

    async def _reindex_memory(self, memory: MemoryEntry):
        """Re-index memory after content update."""
        # Remove old index entries
        await self._remove_from_indexes(memory.memory_id)

        # Add new index entries
        await self._index_memory(memory)

    async def _remove_from_indexes(self, memory_id: str):
        """Remove memory from all indexes."""
        # Remove from content index
        for keyword, memory_ids in self._content_index.items():
            memory_ids.discard(memory_id)
            if not memory_ids:
                del self._content_index[keyword]

        # Remove from tag index
        for tag, memory_ids in self._tag_index.items():
            memory_ids.discard(memory_id)
            if not memory_ids:
                del self._tag_index[tag]

        # Remove from temporal index
        self._temporal_index = [
            (ts, mid) for ts, mid in self._temporal_index if mid != memory_id
        ]

    async def _update_tag_index(self, memory: MemoryEntry, new_tags: List[str]):
        """Update tag index for memory."""
        # Remove old tag entries
        for old_tag in memory.tags:
            if old_tag in self._tag_index:
                self._tag_index[old_tag].discard(memory.memory_id)
                if not self._tag_index[old_tag]:
                    del self._tag_index[old_tag]

        # Add new tag entries
        for new_tag in new_tags:
            self._tag_index[new_tag].add(memory.memory_id)

    async def _create_associations(self, memory: MemoryEntry):
        """Create automatic associations for new memory."""
        # Find similar memories based on content
        content_text = json.dumps(memory.content, default=str)
        keywords = self._extract_keywords(content_text)

        for keyword in keywords:
            if keyword in self._content_index:
                for related_memory_id in self._content_index[keyword]:
                    if related_memory_id != memory.memory_id:
                        # Calculate association strength
                        related_memory = self._memories.get(related_memory_id)
                        if related_memory:
                            strength = self._calculate_similarity(
                                memory, related_memory
                            )

                            if strength >= self.config.association_threshold:
                                await self.create_association(
                                    memory.memory_id,
                                    related_memory_id,
                                    "content_similarity",
                                    strength,
                                )

    async def _remove_associations(self, memory_id: str):
        """Remove all associations for a memory."""
        # Remove outgoing associations
        if memory_id in self._associations:
            del self._associations[memory_id]

        # Remove incoming associations
        for source_id, associations in self._associations.items():
            self._associations[source_id] = [
                assoc for assoc in associations if assoc.target_memory_id != memory_id
            ]

        # Remove from association index
        if memory_id in self._association_index:
            del self._association_index[memory_id]

        # Remove from other memory's related lists
        for memory in self._memories.values():
            memory.related_memories = [
                mid for mid in memory.related_memories if mid != memory_id
            ]

    async def _extract_fragments(
        self, memories: List[MemoryEntry], query: MemoryQuery
    ) -> List[MemoryFragment]:
        """Extract relevant fragments from memories."""
        fragments = []

        for memory in memories:
            content_text = json.dumps(memory.content, default=str)

            # Extract relevant sentences/paragraphs
            sentences = re.split(r"[.!?]+", content_text)

            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    # Calculate relevance
                    relevance = self._calculate_text_relevance(
                        sentence, query.query_text
                    )

                    if relevance >= query.threshold:
                        fragment = MemoryFragment(
                            fragment_id=str(uuid.uuid4()),
                            memory_id=memory.memory_id,
                            content=sentence.strip(),
                            context={
                                "sentence_index": i,
                                "memory_type": memory.memory_type.value,
                            },
                            relevance_score=relevance,
                            extracted_at=datetime.now(),
                        )
                        fragments.append(fragment)

        # Sort by relevance
        fragments.sort(key=lambda f: f.relevance_score, reverse=True)

        return fragments[: query.limit]

    async def _exact_match_search(
        self, query: MemoryQuery
    ) -> tuple[List[MemoryEntry], List[float]]:
        """Perform exact match search."""
        results = []
        scores = []

        query_lower = query.query_text.lower()

        for memory in self._memories.values():
            # Apply filters
            if not self._passes_filters(memory, query.filters):
                continue

            # Check content match
            content_text = json.dumps(memory.content, default=str).lower()

            if query_lower in content_text:
                relevance = 1.0  # Exact match gets full score
                results.append(memory)
                scores.append(relevance)

        return results, scores

    async def _semantic_search(
        self, query: MemoryQuery
    ) -> tuple[List[MemoryEntry], List[float]]:
        """Perform semantic search (placeholder)."""
        # In production, would use actual semantic similarity
        results = []
        scores = []

        query_keywords = self._extract_keywords(query.query_text)

        for memory in self._memories.values():
            if not self._passes_filters(memory, query.filters):
                continue

            content_text = json.dumps(memory.content, default=str)
            content_keywords = self._extract_keywords(content_text)

            # Calculate keyword overlap
            overlap = len(set(query_keywords) & set(content_keywords))
            total_keywords = len(set(query_keywords) | set(content_keywords))

            if total_keywords > 0:
                relevance = overlap / total_keywords

                if relevance >= query.threshold:
                    results.append(memory)
                    scores.append(relevance)

        return results, scores

    async def _contextual_search(
        self, query: MemoryQuery
    ) -> tuple[List[MemoryEntry], List[float]]:
        """Perform contextual search."""
        # Use context from query to guide search
        context = query.context

        results = []
        scores = []

        for memory in self._memories.values():
            if not self._passes_filters(memory, query.filters):
                continue

            # Calculate contextual relevance
            relevance = self._calculate_contextual_relevance(
                memory, query.query_text, context
            )

            if relevance >= query.threshold:
                results.append(memory)
                scores.append(relevance)

        return results, scores

    async def _temporal_search(
        self, query: MemoryQuery
    ) -> tuple[List[MemoryEntry], List[float]]:
        """Perform temporal search."""
        results = []
        scores = []

        # Get time range from context if available
        time_range = query.context.get("time_range")

        for memory in self._memories.values():
            if not self._passes_filters(memory, query.filters):
                continue

            # Check temporal relevance
            if time_range:
                # Filter by time range
                if time_range["start"] <= memory.created_at <= time_range["end"]:
                    relevance = 1.0
                else:
                    continue
            else:
                # Recent memories get higher scores
                hours_ago = (datetime.now() - memory.created_at).total_seconds() / 3600
                relevance = max(0, 1 - hours_ago / 24)  # Decay over 24 hours

            if relevance >= query.threshold:
                results.append(memory)
                scores.append(relevance)

        return results, scores

    async def _associative_search(
        self, query: MemoryQuery
    ) -> tuple[List[MemoryEntry], List[float]]:
        """Perform associative search."""
        results = []
        scores = []

        # First find memories matching query
        base_memories, base_scores = await self._exact_match_search(query)

        # Then find related memories
        for memory in base_memories:
            related_memories = await self.get_related_memories(
                memory.memory_id, max_depth=2
            )

            for related_memory in related_memories:
                if related_memory not in results and self._passes_filters(
                    related_memory, query.filters
                ):
                    # Calculate association-based relevance
                    relevance = 0.7  # Base score for association

                    # Boost by importance
                    relevance *= related_memory.importance_score

                    results.append(related_memory)
                    scores.append(relevance)

        return results, scores

    async def _default_search(
        self, query: MemoryQuery
    ) -> tuple[List[MemoryEntry], List[float]]:
        """Default search method."""
        # Combine multiple search methods
        all_results = []
        all_scores = []

        # Try exact match first
        exact_results, exact_scores = await self._exact_match_search(query)
        all_results.extend(exact_results)
        all_scores.extend(exact_scores)

        # If not enough results, try semantic search
        if len(all_results) < query.limit:
            semantic_results, semantic_scores = await self._semantic_search(query)

            for memory, score in zip(semantic_results, semantic_scores):
                if memory not in all_results:
                    all_results.append(memory)
                    all_scores.append(score)

        # Sort by relevance
        sorted_results = sorted(
            zip(all_results, all_scores), key=lambda x: x[1], reverse=True
        )

        if sorted_results:
            results, scores = zip(*sorted_results)
            return list(results), list(scores)
        else:
            return [], []

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction (in production, would use NLP)
        words = re.findall(r"\b\w+\b", text.lower())

        # Filter out common words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "can",
            "must",
        }

        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        # Return unique keywords
        return list(set(keywords))

    def _calculate_similarity(
        self, memory1: MemoryEntry, memory2: MemoryEntry
    ) -> float:
        """Calculate similarity between two memories."""
        # Simple similarity calculation (in production, would use more sophisticated methods)
        content1 = json.dumps(memory1.content, default=str)
        content2 = json.dumps(memory2.content, default=str)

        keywords1 = set(self._extract_keywords(content1))
        keywords2 = set(self._extract_keywords(content2))

        if not keywords1 or not keywords2:
            return 0.0

        intersection = keywords1 & keywords2
        union = keywords1 | keywords2

        return len(intersection) / len(union)

    def _calculate_text_relevance(self, text: str, query: str) -> float:
        """Calculate relevance of text to query."""
        query_keywords = set(self._extract_keywords(query))
        text_keywords = set(self._extract_keywords(text))

        if not query_keywords:
            return 0.0

        intersection = query_keywords & text_keywords

        return len(intersection) / len(query_keywords)

    def _calculate_contextual_relevance(
        self, memory: MemoryEntry, query: str, context: Dict[str, Any]
    ) -> float:
        """Calculate contextual relevance."""
        base_relevance = self._calculate_text_relevance(
            json.dumps(memory.content, default=str), query
        )

        # Apply context boosts
        context_boost = 1.0

        # Boost by agent match
        if context.get("agent_id") and memory.agent_id == context["agent_id"]:
            context_boost *= 1.5

        # Boost by workspace match
        if (
            context.get("workspace_id")
            and memory.workspace_id == context["workspace_id"]
        ):
            context_boost *= 1.3

        # Boost by memory type
        preferred_types = context.get("memory_types", [])
        if memory.memory_type.value in preferred_types:
            context_boost *= 1.2

        # Boost by tags
        preferred_tags = context.get("tags", [])
        if any(tag in memory.tags for tag in preferred_tags):
            context_boost *= 1.1

        return min(base_relevance * context_boost, 1.0)

    def _passes_filters(self, memory: MemoryEntry, filters: Dict[str, Any]) -> bool:
        """Check if memory passes filters."""
        if not filters:
            return True

        # Filter by agent
        if "agent_id" in filters and memory.agent_id != filters["agent_id"]:
            return False

        # Filter by workspace
        if "workspace_id" in filters and memory.workspace_id != filters["workspace_id"]:
            return False

        # Filter by memory type
        if (
            "memory_type" in filters
            and memory.memory_type.value != filters["memory_type"]
        ):
            return False

        # Filter by tags
        if "tags" in filters:
            required_tags = set(filters["tags"])
            memory_tags = set(memory.tags)
            if not required_tags.issubset(memory_tags):
                return False

        # Filter by importance
        if (
            "min_importance" in filters
            and memory.importance_score < filters["min_importance"]
        ):
            return False

        # Filter by time range
        if "time_range" in filters:
            time_range = filters["time_range"]
            if not (time_range["start"] <= memory.created_at <= time_range["end"]):
                return False

        return True

    async def _update_importance(self, memory: MemoryEntry):
        """Update memory importance based on access patterns."""
        # Boost importance based on recent access
        hours_since_access = (
            datetime.now() - memory.last_accessed
        ).total_seconds() / 3600

        if hours_since_access < 1:
            memory.importance_score = min(1.0, memory.importance_score * 1.1)
        elif hours_since_access < 24:
            memory.importance_score = min(1.0, memory.importance_score * 1.05)

    async def _remove_expired_memories(self) -> int:
        """Remove expired memories."""
        expired_count = 0
        now = datetime.now()

        expired_memory_ids = [
            memory_id
            for memory_id, memory in self._memories.items()
            if memory.expires_at and now > memory.expires_at
        ]

        for memory_id in expired_memory_ids:
            await self._forget_memory(memory_id)
            expired_count += 1

        return expired_count

    async def _forget_memory(self, memory_id: str):
        """Forget a memory (mark as forgotten)."""
        if memory_id in self._memories:
            self._memories[memory_id].status = MemoryStatus.FORGOTTEN

            # Remove from active storage
            if memory_id in self._long_term_memory:
                del self._long_term_memory[memory_id]

            # Remove from working memory
            working_memory_list = list(self._working_memory)
            self._working_memory.clear()
            for mem in working_memory_list:
                if mem.memory_id != memory_id:
                    self._working_memory.append(mem)

    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit memory management event."""
        event_data = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            **data,
        }

        # Call event handlers
        for handler in self._event_handlers[event_type]:
            try:
                await handler(event_data)
            except Exception as e:
                logger.error(f"Event handler failed: {e}")

    def add_event_handler(self, event_type: str, handler: Callable):
        """Add event handler."""
        self._event_handlers[event_type].append(handler)

    def _start_background_tasks(self):
        """Start background tasks."""
        self._running = True

        # Consolidation task
        self._background_tasks.add(asyncio.create_task(self._consolidation_loop()))

    async def _consolidation_loop(self):
        """Background consolidation loop."""
        while self._running:
            try:
                await self.consolidate_memories()

                # Sleep for consolidation interval
                await asyncio.sleep(self.config.consolidation_interval_hours * 3600)

            except Exception as e:
                logger.error(f"Consolidation loop failed: {e}")
                await asyncio.sleep(3600)  # Retry after 1 hour

    async def stop(self):
        """Stop memory manager."""
        self._running = False

        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self._background_tasks, return_exceptions=True)

        self._background_tasks.clear()

        logger.info("Memory manager stopped")
