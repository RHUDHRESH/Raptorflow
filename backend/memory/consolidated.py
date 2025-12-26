import asyncio
import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from uuid import UUID, uuid4

from inference import InferenceProvider
from memory.manager import MemoryManager
from memory.swarm_learning import SwarmLearning
from models.cognitive import AgentMessage, CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.memory.consolidated")


@dataclass
class MemoryFragment:
    """Represents a single memory fragment from any agent."""

    id: str = field(default_factory=lambda: str(uuid4()))
    agent_id: str = ""
    agent_type: str = ""
    content: Any = None
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    importance_score: float = 0.5
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    tags: Set[str] = field(default_factory=set)
    memory_tier: str = "L1"  # L1, L2, L3
    workspace_id: str = ""
    thread_id: str = ""

    def __post_init__(self):
        """Validate fragment data after initialization."""
        if self.importance_score < 0 or self.importance_score > 1:
            raise ValueError(
                f"Invalid importance_score: {self.importance_score}. Must be between 0 and 1."
            )
        if self.memory_tier not in ["L1", "L2", "L3"]:
            raise ValueError(
                f"Invalid memory_tier: {self.memory_tier}. Must be L1, L2, or L3."
            )
        if not self.id:
            self.id = str(uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert fragment to dictionary for serialization."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "content": self.content,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "importance_score": self.importance_score,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat(),
            "tags": list(self.tags),
            "memory_tier": self.memory_tier,
            "workspace_id": self.workspace_id,
            "thread_id": self.thread_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryFragment":
        """Create fragment from dictionary."""
        # Handle timestamp conversion
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        if isinstance(data.get("last_accessed"), str):
            data["last_accessed"] = datetime.fromisoformat(data["last_accessed"])

        # Convert tags back to set
        if isinstance(data.get("tags"), list):
            data["tags"] = set(data["tags"])

        return cls(**data)


@dataclass
class ConsolidatedMemory:
    """Unified memory structure for swarm-wide consolidation."""

    workspace_id: str
    fragments: List[MemoryFragment] = field(default_factory=list)
    agent_profiles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    cross_agent_links: Dict[str, List[str]] = field(default_factory=dict)
    synthesized_knowledge: List[Dict[str, Any]] = field(default_factory=list)
    last_consolidation: datetime = field(default_factory=datetime.now)
    consolidation_interval: timedelta = field(
        default_factory=lambda: timedelta(minutes=5)
    )


class SwarmMemoryConsolidator:
    """
    SOTA Swarm Memory Consolidation System.
    Consolidates, caches, and optimizes memory across all swarm agents.
    """

    def __init__(self, workspace_id: str):
        if not workspace_id or not isinstance(workspace_id, str):
            raise ValueError("workspace_id must be a non-empty string")

        self.workspace_id = workspace_id
        self.memory_manager = MemoryManager()
        self.swarm_learning = SwarmLearning()
        self.consolidated_memory = ConsolidatedMemory(workspace_id=workspace_id)

        # Initialize embedder with error handling
        try:
            self.embedder = InferenceProvider.get_embeddings()
        except Exception as e:
            logger.error(f"Failed to initialize embedder: {e}")
            self.embedder = None

        # Performance optimization caches
        self._fragment_cache: Dict[str, MemoryFragment] = {}
        self._search_cache: Dict[str, List[MemoryFragment]] = {}
        self._cache_ttl = timedelta(minutes=10)
        self._last_cache_cleanup = datetime.now()

        # Memory deduplication
        self._content_hashes: Dict[str, str] = {}  # hash -> fragment_id

        # Agent memory tracking
        self._agent_memory_footprints: Dict[str, Dict[str, int]] = defaultdict(dict)

        # Thread safety locks
        self._consolidation_lock = asyncio.Lock()
        self._cache_lock = asyncio.Lock()

        logger.info(f"SwarmMemoryConsolidator initialized for workspace {workspace_id}")

    async def consolidate_agent_memories(
        self, 
        agent_ids: Optional[List[str]] = None,
        force_consolidation: bool = False
    ) -> ConsolidatedMemory:
        """
        Consolidates memories from all or specified agents.
        This is the core consolidation operation.
        """
        async with self._consolidation_lock:
            if not force_consolidation:
                time_since_last = datetime.now() - self.consolidated_memory.last_consolidation
                if time_since_last < self.consolidated_memory.consolidation_interval:
                    logger.debug("Skipping consolidation - interval not reached")
                    return self.consolidated_memory

            logger.info(f"Starting memory consolidation for workspace {self.workspace_id}")
            
            try:
                # 1. Gather memory fragments from all sources
                fragments = await self._gather_memory_fragments(agent_ids)
                
                # 2. Deduplicate and merge fragments
                deduplicated_fragments = await self._deduplicate_fragments(fragments)
                
                # 3. Score and rank fragments by importance
                scored_fragments = await self._score_fragments(deduplicated_fragments)
                
                # 4. Build cross-agent links
                cross_links = await self._build_cross_agent_links(scored_fragments)
                
                # 5. Synthesize swarm knowledge
                synthesized = await self._synthesize_swarm_knowledge(scored_fragments)
                
                # 6. Update consolidated memory
                self.consolidated_memory.fragments = scored_fragments
                self.consolidated_memory.cross_agent_links = cross_links
                self.consolidated_memory.synthesized_knowledge = synthesized
                self.consolidated_memory.last_consolidation = datetime.now()
                
                # 7. Update caches
                await self._update_caches(scored_fragments)
                
                # 8. Store consolidated insights back to memory tiers
                await self._store_consolidated_insights()
                
                logger.info(f"Consolidated {len(scored_fragments)} memory fragments from {len(set(f.agent_id for f in scored_fragments))} agents")
                
                return self.consolidated_memory
                
            except Exception as e:
                logger.error(f"Consolidation failed for workspace {self.workspace_id}: {e}")
                # Return previous state on failure
                return self.consolidated_memory

    async def _gather_memory_fragments(
        self, agent_ids: Optional[List[str]] = None
    ) -> List[MemoryFragment]:
        """Gathers memory fragments from L1, L2, L3 and agent-specific stores."""
        fragments = []

        # Gather from L1 (short-term)
        l1_fragments = await self._gather_l1_fragments(agent_ids)
        fragments.extend(l1_fragments)

        # Gather from L2 (episodic)
        l2_fragments = await self._gather_l2_fragments(agent_ids)
        fragments.extend(l2_fragments)

        # Gather from L3 (semantic)
        l3_fragments = await self._gather_l3_fragments(agent_ids)
        fragments.extend(l3_fragments)

        # Gather from swarm learning
        swarm_fragments = await self._gather_swarm_fragments(agent_ids)
        fragments.extend(swarm_fragments)

        return fragments

    async def _gather_l1_fragments(
        self, agent_ids: Optional[List[str]] = None
    ) -> List[MemoryFragment]:
        """Gathers fragments from L1 short-term memory."""
        fragments = []

        try:
            # Get all trace keys from L1
            patterns = ["trace:*", "swarm:learning:*", "swarm:feedback:*"]

            for pattern in patterns:
                # Note: This would need implementation for Upstash Redis pattern matching
                # For now, we'll simulate by checking known agent threads
                if agent_ids:
                    for agent_id in agent_ids:
                        key = pattern.replace("*", f"{agent_id}")
                        data = await self.memory_manager.l1.retrieve(key)
                        if data:
                            fragment = MemoryFragment(
                                agent_id=agent_id,
                                content=data,
                                memory_tier="L1",
                                workspace_id=self.workspace_id,
                            )
                            fragments.append(fragment)

        except Exception as e:
            logger.error(f"Failed to gather L1 fragments: {e}")

        return fragments

    async def _gather_l2_fragments(
        self, agent_ids: Optional[List[str]] = None
    ) -> List[MemoryFragment]:
        """Gathers fragments from L2 episodic memory."""
        fragments = []

        try:
            # Check if embedder is available
            if not self.embedder:
                logger.warning("Embedder not available, skipping L2 fragment gathering")
                return fragments

            # Search for recent episodic memories
            query = "agent memory trace learning outcome"
            query_embedding = await self.embedder.aembed_query(query)

            filters = {"type": "episodic"}
            if agent_ids:
                filters["agent_ids"] = agent_ids

            results = await self.memory_manager.l2.recall_similar(
                workspace_id=self.workspace_id,
                query_embedding=query_embedding,
                limit=50,
                filters=filters,
            )

            for result in results:
                fragment = MemoryFragment(
                    id=result["id"],
                    content=result["content"],
                    metadata=result.get("metadata", {}),
                    memory_tier="L2",
                    workspace_id=self.workspace_id,
                    importance_score=result.get("similarity", 0.5),
                )
                fragments.append(fragment)

        except Exception as e:
            logger.error(f"Failed to gather L2 fragments: {e}")

        return fragments

    async def _gather_l3_fragments(
        self, agent_ids: Optional[List[str]] = None
    ) -> List[MemoryFragment]:
        """Gathers fragments from L3 semantic memory."""
        fragments = []

        try:
            # Search for foundation knowledge
            query = "brand foundation strategy agent knowledge"
            results = await self.memory_manager.l3.search_foundation(
                workspace_id=self.workspace_id, query=query, limit=30
            )

            for result in results:
                fragment = MemoryFragment(
                    id=result["id"],
                    content=result["content"],
                    metadata=result.get("metadata", {}),
                    memory_tier="L3",
                    workspace_id=self.workspace_id,
                    importance_score=result.get("similarity", 0.5),
                )
                fragments.append(fragment)

        except Exception as e:
            logger.error(f"Failed to gather L3 fragments: {e}")

        return fragments

    async def _gather_swarm_fragments(
        self, agent_ids: Optional[List[str]] = None
    ) -> List[MemoryFragment]:
        """Gathers fragments from swarm learning system."""
        fragments = []

        try:
            # Get swarm knowledge
            swarm_context = await self.swarm_learning.retrieve_swarm_knowledge(
                workspace_id=self.workspace_id,
                query="agent collaboration learning outcome",
                limit=20,
            )

            for tier_name, tier_fragments in swarm_context.items():
                for fragment_data in tier_fragments:
                    fragment = MemoryFragment(
                        content=fragment_data.get("content", ""),
                        metadata=fragment_data.get("metadata", {}),
                        memory_tier=tier_name.upper(),
                        workspace_id=self.workspace_id,
                    )
                    fragments.append(fragment)

        except Exception as e:
            logger.error(f"Failed to gather swarm fragments: {e}")

        return fragments

    async def _deduplicate_fragments(
        self, fragments: List[MemoryFragment]
    ) -> List[MemoryFragment]:
        """Removes duplicate fragments based on content hashing."""
        seen_hashes = set()
        deduplicated = []

        for fragment in fragments:
            # Create content hash
            content_str = json.dumps(fragment.content, sort_keys=True)
            content_hash = hashlib.md5(content_str.encode()).hexdigest()

            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                fragment.metadata["content_hash"] = content_hash
                deduplicated.append(fragment)
                self._content_hashes[content_hash] = fragment.id
            else:
                # Merge metadata from duplicate
                existing_fragment_id = self._content_hashes[content_hash]
                for existing in deduplicated:
                    if existing.id == existing_fragment_id:
                        existing.metadata.update(fragment.metadata)
                        existing.access_count += fragment.access_count
                        break

        logger.info(
            f"Deduplicated {len(fragments)} fragments to {len(deduplicated)} unique fragments"
        )
        return deduplicated

    async def _score_fragments(
        self, fragments: List[MemoryFragment]
    ) -> List[MemoryFragment]:
        """Scores fragments by importance, relevance, and utility."""
        for fragment in fragments:
            # Base importance score
            score = fragment.importance_score

            # Recency boost
            hours_old = (datetime.now() - fragment.timestamp).total_seconds() / 3600
            recency_boost = max(0, 1 - (hours_old / 24))  # Decay over 24 hours
            score += recency_boost * 0.2

            # Access frequency boost
            access_boost = min(fragment.access_count / 10, 1) * 0.1
            score += access_boost

            # Agent type importance
            agent_importance = {
                "strategist": 0.3,
                "researcher": 0.25,
                "creative": 0.2,
                "quality": 0.15,
                "supervisor": 0.1,
            }
            score += agent_importance.get(fragment.agent_type, 0) * 0.2

            # Memory tier importance
            tier_importance = {"L3": 0.3, "L2": 0.2, "L1": 0.1}
            score += tier_importance.get(fragment.memory_tier, 0) * 0.1

            fragment.importance_score = min(score, 1.0)

        # Sort by importance score
        return sorted(fragments, key=lambda f: f.importance_score, reverse=True)

    async def _build_cross_agent_links(
        self, fragments: List[MemoryFragment]
    ) -> Dict[str, List[str]]:
        """Builds links between related fragments across different agents."""
        links = defaultdict(list)

        # Group fragments by content similarity
        for i, fragment1 in enumerate(fragments):
            for fragment2 in fragments[i + 1 :]:
                if fragment1.agent_id != fragment2.agent_id:
                    similarity = await self._calculate_fragment_similarity(
                        fragment1, fragment2
                    )
                    if similarity > 0.7:  # High similarity threshold
                        links[fragment1.id].append(fragment2.id)
                        links[fragment2.id].append(fragment1.id)

        return dict(links)

    async def _calculate_fragment_similarity(
        self, f1: MemoryFragment, f2: MemoryFragment
    ) -> float:
        """Calculates similarity between two fragments."""
        if not f1.embedding or not f2.embedding:
            return 0.0

        # Check embedding dimensions match
        if len(f1.embedding) != len(f2.embedding):
            return 0.0

        # Cosine similarity with error handling
        try:
            dot_product = sum(a * b for a, b in zip(f1.embedding, f2.embedding))
            magnitude1 = sum(a * a for a in f1.embedding) ** 0.5
            magnitude2 = sum(b * b for b in f2.embedding) ** 0.5

            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0

            similarity = dot_product / (magnitude1 * magnitude2)
            # Ensure similarity is between 0 and 1
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Error calculating fragment similarity: {e}")
            return 0.0

    async def _synthesize_swarm_knowledge(
        self, fragments: List[MemoryFragment]
    ) -> List[Dict[str, Any]]:
        """Synthesizes high-level knowledge from consolidated fragments."""
        synthesized = []

        try:
            # Group top fragments by themes
            top_fragments = [f for f in fragments if f.importance_score > 0.7]

            if len(top_fragments) < 3:
                return synthesized

            # Create synthesis prompts for different themes
            themes = {
                "strategy": [
                    f for f in top_fragments if "strategy" in str(f.content).lower()
                ],
                "performance": [
                    f
                    for f in top_fragments
                    if "outcome" in str(f.content).lower()
                    or "result" in str(f.content).lower()
                ],
                "collaboration": [
                    f
                    for f in top_fragments
                    if "team" in str(f.content).lower()
                    or "coordination" in str(f.content).lower()
                ],
            }

            for theme, themed_fragments in themes.items():
                if len(themed_fragments) >= 2:
                    synthesis = await self._synthesize_theme(theme, themed_fragments)
                    synthesized.append(synthesis)

        except Exception as e:
            logger.error(f"Failed to synthesize swarm knowledge: {e}")

        return synthesized

    async def _synthesize_theme(
        self, theme: str, fragments: List[MemoryFragment]
    ) -> Dict[str, Any]:
        """Synthesizes knowledge for a specific theme."""
        try:
            # Prepare content for synthesis
            content_snippets = [
                f"Agent {f.agent_id} ({f.agent_type}): {str(f.content)[:200]}..."
                for f in fragments[:5]  # Limit to prevent context overflow
            ]

            synthesis_prompt = f"""
            Synthesize the following {theme} insights from multiple agents:
            {' '.join(content_snippets)}

            Extract the top 3 key insights and patterns.
            """

            # Initialize LLM with error handling
            try:
                llm = InferenceProvider.get_model(model_tier="reasoning")
                response = await llm.ainvoke(synthesis_prompt)
                insights = response.content
            except Exception as e:
                logger.error(f"LLM synthesis failed for theme {theme}: {e}")
                insights = f"LLM synthesis failed: {str(e)}"

            return {
                "theme": theme,
                "insights": insights,
                "contributing_agents": list(set(f.agent_id for f in fragments)),
                "confidence": sum(f.importance_score for f in fragments)
                / len(fragments) if fragments else 0.0,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to synthesize theme {theme}: {e}")
            return {
                "theme": theme,
                "insights": f"Synthesis failed: {str(e)}",
                "contributing_agents": [],
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat(),
            }

    async def _update_caches(self, fragments: List[MemoryFragment]):
        """Updates internal caches for fast retrieval."""
        # Update fragment cache
        for fragment in fragments:
            self._fragment_cache[fragment.id] = fragment

        # Clean old cache entries
        await self._cleanup_expired_cache()

        logger.info(f"Updated caches with {len(fragments)} fragments")

    async def _cleanup_expired_cache(self):
        """Cleans up expired cache entries."""
        async with self._cache_lock:
            if datetime.now() - self._last_cache_cleanup < self._cache_ttl:
                return

            # Clean fragment cache
            expired_fragments = [
                fid
                for fid, fragment in self._fragment_cache.items()
                if datetime.now() - fragment.timestamp > self._cache_ttl
            ]

            for fid in expired_fragments:
                del self._fragment_cache[fid]

            # Clean search cache
            self._search_cache.clear()

            self._last_cache_cleanup = datetime.now()
            logger.info(f"Cleaned {len(expired_fragments)} expired cache entries")

    async def _store_consolidated_insights(self):
        """Stores consolidated insights back to memory tiers."""
        try:
            # Check if embedder is available
            if not self.embedder:
                logger.warning("Embedder not available, skipping insight storage")
                return

            # Store synthesized knowledge to L3
            for synthesis in self.consolidated_memory.synthesized_knowledge:
                content = json.dumps(synthesis)
                embedding = await self.embedder.aembed_query(content)

                await self.memory_manager.l3.remember_foundation(
                    workspace_id=self.workspace_id,
                    content=content,
                    embedding=embedding,
                    metadata={
                        "type": "synthesized",
                        "theme": synthesis["theme"],
                        "agents": synthesis["contributing_agents"],
                        "confidence": synthesis["confidence"],
                    },
                )

        except Exception as e:
            logger.error(f"Failed to store consolidated insights: {e}")

    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Returns comprehensive memory statistics."""
        try:
            stats = {
                "workspace_id": self.workspace_id,
                "total_fragments": len(self.consolidated_memory.fragments),
                "active_agents": list(set(f.agent_id for f in self.consolidated_memory.fragments)),
                "memory_tiers": {
                    tier: len([f for f in self.consolidated_memory.fragments if f.memory_tier == tier])
                    for tier in ["L1", "L2", "L3"]
                },
                "average_importance": sum(f.importance_score for f in self.consolidated_memory.fragments) / len(self.consolidated_memory.fragments) if self.consolidated_memory.fragments else 0,
                "cross_agent_links": len(self.consolidated_memory.cross_agent_links),
                "synthesized_insights": len(self.consolidated_memory.synthesized_knowledge),
                "last_consolidation": self.consolidated_memory.last_consolidation.isoformat(),
                "cache_performance": {
                    "fragment_cache_size": len(self._fragment_cache),
                    "search_cache_size": len(self._search_cache),
                    "last_cleanup": self._last_cache_cleanup.isoformat()
                }
            }
            return stats
        except Exception as e:
            logger.error(f"Failed to get memory statistics: {e}")
            return {"error": str(e)}

    async def search_consolidated_memory(
        self,
        query: str,
        agent_filter: Optional[List[str]] = None,
        tier_filter: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[MemoryFragment]:
        """
        Fast search across consolidated memory with caching.
        """
        cache_key = f"{hash(query)}_{agent_filter}_{tier_filter}_{limit}"

        # Check cache first
        if cache_key in self._search_cache:
            logger.debug(f"Search cache hit for query: {query[:50]}...")
            return self._search_cache[cache_key][:limit]

        # Perform search
        query_embedding = await self.embedder.aembed_query(query)

        # Search through fragments
        scored_fragments = []
        for fragment in self.consolidated_memory.fragments:
            # Apply filters
            if agent_filter and fragment.agent_id not in agent_filter:
                continue
            if tier_filter and fragment.memory_tier not in tier_filter:
                continue

            # Calculate similarity
            if fragment.embedding:
                similarity = await self._calculate_fragment_similarity(
                    MemoryFragment(embedding=query_embedding), fragment
                )
                scored_fragments.append((fragment, similarity))

        # Sort by similarity and importance
        scored_fragments.sort(
            key=lambda x: (x[1] * 0.7 + x[0].importance_score * 0.3), reverse=True
        )

        results = [f for f, _ in scored_fragments[:limit]]

        # Cache results
        self._search_cache[cache_key] = results

        logger.info(
            f"Search returned {len(results)} fragments for query: {query[:50]}..."
        )
        return results

    async def get_agent_memory_summary(self, agent_id: str) -> Dict[str, Any]:
        """Returns memory summary for a specific agent."""
        agent_fragments = [
            f for f in self.consolidated_memory.fragments if f.agent_id == agent_id
        ]

        return {
            "agent_id": agent_id,
            "total_fragments": len(agent_fragments),
            "memory_tiers": {
                tier: len([f for f in agent_fragments if f.memory_tier == tier])
                for tier in ["L1", "L2", "L3"]
            },
            "average_importance": (
                sum(f.importance_score for f in agent_fragments) / len(agent_fragments)
                if agent_fragments
                else 0
            ),
            "most_accessed": (
                max(agent_fragments, key=lambda f: f.access_count)
                if agent_fragments
                else None
            ),
            "recent_activity": len(
                [
                    f
                    for f in agent_fragments
                    if (datetime.now() - f.timestamp).total_seconds() < 3600
                ]
            ),
        }

    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Returns comprehensive memory statistics."""
        fragments = self.consolidated_memory.fragments

        return {
            "workspace_id": self.workspace_id,
            "total_fragments": len(fragments),
            "unique_agents": len(set(f.agent_id for f in fragments)),
            "memory_tiers": {
                tier: len([f for f in fragments if f.memory_tier == tier])
                for tier in ["L1", "L2", "L3"]
            },
            "average_importance": (
                sum(f.importance_score for f in fragments) / len(fragments)
                if fragments
                else 0
            ),
            "cross_agent_links": len(self.consolidated_memory.cross_agent_links),
            "synthesized_insights": len(self.consolidated_memory.synthesized_knowledge),
            "cache_size": len(self._fragment_cache),
            "last_consolidation": self.consolidated_memory.last_consolidation.isoformat(),
        }


class SwarmMemoryCache:
    """
    High-performance cache layer for swarm memory operations.
    Provides millisecond-latency access to consolidated memories.
    """

    def __init__(self, consolidator: SwarmMemoryConsolidator):
        self.consolidator = consolidator
        self._hot_cache: Dict[str, Any] = {}
        self._access_patterns: Dict[str, List[datetime]] = defaultdict(list)
        self._cache_lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Gets value from hot cache with access pattern tracking."""
        async with self._cache_lock:
            if key in self._hot_cache:
                self._access_patterns[key].append(datetime.now())
                return self._hot_cache[key]
            return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """Sets value in hot cache with TTL."""
        async with self._cache_lock:
            self._hot_cache[key] = value
            # Schedule expiration (simplified - in production use proper TTL)
            asyncio.create_task(self._expire_key(key, ttl))

    async def _expire_key(self, key: str, ttl: int):
        """Expires a cache key after TTL seconds."""
        await asyncio.sleep(ttl)
        async with self._cache_lock:
            if key in self._hot_cache:
                del self._hot_cache[key]
                if key in self._access_patterns:
                    del self._access_patterns[key]

    async def get_hot_fragments(self, limit: int = 50) -> List[MemoryFragment]:
        """Returns most frequently accessed fragments."""
        # Sort by access frequency
        sorted_keys = sorted(
            self._access_patterns.keys(),
            key=lambda k: len(self._access_patterns[k]),
            reverse=True,
        )

        hot_fragments = []
        for key in sorted_keys[:limit]:
            if key in self._hot_cache:
                hot_fragments.append(self._hot_cache[key])

        return hot_fragments


# Factory function for easy instantiation
def create_swarm_memory_consolidator(workspace_id: str) -> SwarmMemoryConsolidator:
    """Creates a new swarm memory consolidator instance."""
    return SwarmMemoryConsolidator(workspace_id=workspace_id)
