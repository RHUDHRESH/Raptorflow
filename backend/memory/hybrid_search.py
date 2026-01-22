"""
Hybrid search system with semantic and keyword search plus reranking.

This module provides advanced search capabilities combining
vector similarity search with traditional keyword search, followed
by intelligent reranking for optimal results.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ..core.supabase import get_supabase_client
from .embeddings import get_embedding_model
from .models import MemoryChunk, MemoryType
from .vector_store import VectorMemory

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Enhanced search result with multiple scores."""

    chunk: MemoryChunk
    semantic_score: float
    keyword_score: float
    hybrid_score: float
    rerank_score: float
    final_score: float
    match_type: str  # 'semantic', 'keyword', 'hybrid'
    metadata: Dict[str, Any]


@dataclass
class SearchConfig:
    """Configuration for hybrid search."""

    semantic_weight: float = 0.7
    keyword_weight: float = 0.3
    rerank_enabled: bool = True
    rerank_top_k: int = 20
    final_limit: int = 10
    include_metadata: bool = True
    boost_recent: bool = True
    boost_recent_hours: int = 24
    min_score_threshold: float = 0.1


class HybridSearchEngine:
    """
    Advanced hybrid search engine with reranking capabilities.

    Combines semantic vector search with keyword search,
    applies intelligent reranking, and provides optimal results.
    """

    def __init__(
        self, vector_memory: VectorMemory, config: Optional[SearchConfig] = None
    ):
        """
        Initialize hybrid search engine.

        Args:
            vector_memory: Vector memory instance
            config: Search configuration
        """
        self.vector_memory = vector_memory
        self.embedding_model = get_embedding_model()
        self.supabase = get_supabase_client()
        self.config = config or SearchConfig()

        # Initialize keyword search index
        self._init_keyword_index()

    def _init_keyword_index(self):
        """Initialize keyword search capabilities."""
        self.keyword_index = {}
        self.index_last_updated = None
        self.index_update_interval = 3600  # 1 hour

    async def search(
        self,
        workspace_id: str,
        query: str,
        memory_types: Optional[List[MemoryType]] = None,
        filters: Optional[Dict[str, Any]] = None,
        config: Optional[SearchConfig] = None,
    ) -> List[SearchResult]:
        """
        Perform hybrid search with semantic and keyword components.

        Args:
            workspace_id: Workspace identifier
            query: Search query
            memory_types: Optional memory type filters
            filters: Additional search filters
            config: Override search configuration

        Returns:
            List of enhanced search results
        """
        search_config = config or self.config

        try:
            # Perform semantic search
            semantic_results = await self._semantic_search(
                workspace_id, query, memory_types, filters
            )

            # Perform keyword search
            keyword_results = await self._keyword_search(
                workspace_id, query, memory_types, filters
            )

            # Combine and score results
            hybrid_results = await self._combine_results(
                semantic_results, keyword_results, search_config
            )

            # Apply reranking if enabled
            if search_config.rerank_enabled:
                hybrid_results = await self._rerank_results(
                    hybrid_results, query, search_config
                )

            # Apply final filtering and sorting
            final_results = await self._finalize_results(hybrid_results, search_config)

            return final_results

        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return []

    async def _semantic_search(
        self,
        workspace_id: str,
        query: str,
        memory_types: Optional[List[MemoryType]],
        filters: Optional[Dict[str, Any]],
    ) -> List[SearchResult]:
        """Perform semantic vector search."""
        try:
            # Get vector search results
            chunks = await self.vector_memory.search(
                workspace_id=workspace_id,
                query=query,
                memory_types=memory_types,
                limit=self.config.rerank_top_k * 2,  # Get more for reranking
            )

            results = []
            for chunk in chunks:
                # Calculate semantic score
                semantic_score = chunk.score or 0.0

                # Apply recency boost if enabled
                recency_boost = self._calculate_recency_boost(chunk)
                boosted_score = semantic_score * (1.0 + recency_boost)

                result = SearchResult(
                    chunk=chunk,
                    semantic_score=semantic_score,
                    keyword_score=0.0,
                    hybrid_score=boosted_score,
                    rerank_score=0.0,
                    final_score=boosted_score,
                    match_type="semantic",
                    metadata={
                        "created_at": (
                            chunk.created_at.isoformat() if chunk.created_at else None
                        ),
                        "memory_type": (
                            chunk.memory_type.value if chunk.memory_type else None
                        ),
                    },
                )
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    async def _keyword_search(
        self,
        workspace_id: str,
        query: str,
        memory_types: Optional[List[MemoryType]],
        filters: Optional[Dict[str, Any]],
    ) -> List[SearchResult]:
        """Perform keyword-based search."""
        try:
            # Build keyword search query
            keywords = self._extract_keywords(query)

            if not keywords:
                return []

            # Search in Supabase using full-text search
            query_builder = self.supabase.table("memory_vectors")

            # Apply workspace filter
            query_builder = query_builder.select("*").eq("workspace_id", workspace_id)

            # Apply memory type filter
            if memory_types:
                type_values = [mt.value for mt in memory_types]
                query_builder = query_builder.in_("memory_type", type_values)

            # Apply keyword search
            keyword_conditions = []
            for keyword in keywords:
                keyword_conditions.append(f"content.ilike.%{keyword}%")

            if keyword_conditions:
                # Combine conditions with OR
                query_builder = query_builder.or_(*keyword_conditions)

            # Execute query
            result = query_builder.limit(self.config.rerank_top_k * 2).execute()

            results = []
            if result.data:
                for row in result.data:
                    # Convert to MemoryChunk
                    chunk = MemoryChunk(
                        id=row["id"],
                        workspace_id=row["workspace_id"],
                        memory_type=MemoryType(row["memory_type"]),
                        content=row["content"],
                        metadata=row.get("metadata", {}),
                        reference_id=row.get("reference_id"),
                        reference_table=row.get("reference_table"),
                        created_at=(
                            datetime.fromisoformat(row["created_at"])
                            if row.get("created_at")
                            else None
                        ),
                    )

                    # Calculate keyword score
                    keyword_score = self._calculate_keyword_score(
                        chunk.content, keywords
                    )

                    # Apply recency boost
                    recency_boost = self._calculate_recency_boost(chunk)
                    boosted_score = keyword_score * (1.0 + recency_boost)

                    result = SearchResult(
                        chunk=chunk,
                        semantic_score=0.0,
                        keyword_score=keyword_score,
                        hybrid_score=boosted_score,
                        rerank_score=0.0,
                        final_score=boosted_score,
                        match_type="keyword",
                        metadata={
                            "created_at": (
                                chunk.created_at.isoformat()
                                if chunk.created_at
                                else None
                            ),
                            "memory_type": (
                                chunk.memory_type.value if chunk.memory_type else None
                            ),
                            "keyword_matches": keywords,
                        },
                    )
                    results.append(result)

            return results

        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []

    async def _combine_results(
        self,
        semantic_results: List[SearchResult],
        keyword_results: List[SearchResult],
        config: SearchConfig,
    ) -> List[SearchResult]:
        """Combine semantic and keyword results."""
        combined = {}

        # Add semantic results
        for result in semantic_results:
            chunk_id = result.chunk.id
            combined[chunk_id] = result
            combined[chunk_id].hybrid_score = (
                result.semantic_score * config.semantic_weight
            )

        # Add or merge keyword results
        for result in keyword_results:
            chunk_id = result.chunk.id

            if chunk_id in combined:
                # Merge with existing result
                existing = combined[chunk_id]
                existing.keyword_score = result.keyword_score
                existing.hybrid_score = (
                    existing.semantic_score * config.semantic_weight
                    + result.keyword_score * config.keyword_weight
                )
                existing.match_type = "hybrid"
            else:
                # Add new result
                result.hybrid_score = result.keyword_score * config.keyword_weight
                combined[chunk_id] = result

        return list(combined.values())

    async def _rerank_results(
        self, results: List[SearchResult], query: str, config: SearchConfig
    ) -> List[SearchResult]:
        """Apply intelligent reranking to results."""
        try:
            # Get top candidates for reranking
            top_results = sorted(results, key=lambda x: x.hybrid_score, reverse=True)[
                : config.rerank_top_k
            ]

            # Get query embedding for similarity calculations
            query_embedding = self.embedding_model.encode(query)

            # Rerank each result
            for result in top_results:
                # Get content embedding
                content_embedding = await self._get_chunk_embedding(result.chunk)

                if content_embedding:
                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(
                        query_embedding, content_embedding
                    )

                    # Apply reranking factors
                    rerank_score = self._apply_reranking_factors(
                        result, similarity, query
                    )

                    result.rerank_score = rerank_score
                    result.final_score = result.hybrid_score * 0.7 + rerank_score * 0.3
                else:
                    result.final_score = result.hybrid_score

            return results

        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            return results

    async def _finalize_results(
        self, results: List[SearchResult], config: SearchConfig
    ) -> List[SearchResult]:
        """Apply final filtering and sorting."""
        # Filter by minimum score threshold
        filtered_results = [
            result
            for result in results
            if result.final_score >= config.min_score_threshold
        ]

        # Sort by final score
        sorted_results = sorted(
            filtered_results, key=lambda x: x.final_score, reverse=True
        )

        # Apply final limit
        final_results = sorted_results[: config.final_limit]

        return final_results

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query."""
        # Simple keyword extraction - can be enhanced with NLP
        import re

        # Remove special characters and split
        words = re.findall(r"\b\w+\b", query.lower())

        # Filter out common stop words
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

        return keywords

    def _calculate_keyword_score(self, content: str, keywords: List[str]) -> float:
        """Calculate keyword match score."""
        content_lower = content.lower()

        # Count keyword matches
        matches = 0
        total_keywords = len(keywords)

        for keyword in keywords:
            if keyword in content_lower:
                matches += 1
                # Bonus for exact phrase matches
                if keyword in content_lower.split():
                    matches += 0.5

        # Normalize score
        if total_keywords == 0:
            return 0.0

        return min(matches / total_keywords, 1.0)

    def _calculate_recency_boost(self, chunk: MemoryChunk) -> float:
        """Calculate recency boost for recent content."""
        if not self.config.boost_recent or not chunk.created_at:
            return 0.0

        now = datetime.utcnow()
        age_hours = (now - chunk.created_at).total_seconds() / 3600

        if age_hours <= self.config.boost_recent_hours:
            # Linear boost from 0.0 to 0.2 for recent content
            boost = 0.2 * (1.0 - age_hours / self.config.boost_recent_hours)
            return boost

        return 0.0

    async def _get_chunk_embedding(self, chunk: MemoryChunk) -> Optional[List[float]]:
        """Get embedding for a chunk."""
        try:
            # Create searchable text
            text = chunk.content
            if chunk.metadata:
                text += " " + " ".join(
                    str(v) for v in chunk.metadata.values() if isinstance(v, str)
                )

            # Get embedding
            embedding = self.embedding_model.encode(text)
            return embedding

        except Exception as e:
            logger.error(f"Error getting chunk embedding: {e}")
            return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between vectors."""
        if not vec1 or not vec2:
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(a * a for a in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _apply_reranking_factors(
        self, result: SearchResult, similarity: float, query: str
    ) -> float:
        """Apply various reranking factors."""
        score = similarity

        # Factor 1: Content type boost
        if result.chunk.memory_type:
            type_boosts = {
                MemoryType.FOUNDATION: 1.1,
                MemoryType.ICP: 1.05,
                MemoryType.MOVE: 1.0,
                MemoryType.RESEARCH: 1.0,
                MemoryType.CONVERSATION: 0.95,
            }
            score *= type_boosts.get(result.chunk.memory_type, 1.0)

        # Factor 2: Length penalty (prefer concise, relevant content)
        content_length = len(result.chunk.content)
        if content_length > 2000:
            score *= 0.9  # Penalty for very long content
        elif content_length < 50:
            score *= 0.8  # Penalty for very short content

        # Factor 3: Query term density
        query_terms = set(query.lower().split())
        content_terms = set(result.chunk.content.lower().split())
        overlap = len(query_terms & content_terms)
        if query_terms:
            density_bonus = min(overlap / len(query_terms), 0.2)
            score += density_bonus

        # Factor 4: Metadata quality
        if result.chunk.metadata:
            metadata_score = len(result.chunk.metadata) / 10.0  # Normalize
            score += min(metadata_score, 0.1)

        return min(score, 1.0)  # Cap at 1.0

    async def get_search_analytics(
        self, workspace_id: str, query: str, results: List[SearchResult]
    ) -> Dict[str, Any]:
        """Get analytics about search performance."""
        if not results:
            return {}

        # Calculate statistics
        semantic_count = len([r for r in results if r.match_type == "semantic"])
        keyword_count = len([r for r in results if r.match_type == "keyword"])
        hybrid_count = len([r for r in results if r.match_type == "hybrid"])

        avg_score = sum(r.final_score for r in results) / len(results)
        avg_semantic_score = sum(r.semantic_score for r in results) / len(results)
        avg_keyword_score = sum(r.keyword_score for r in results) / len(results)

        # Memory type distribution
        type_distribution = {}
        for result in results:
            if result.chunk.memory_type:
                type_name = result.chunk.memory_type.value
                type_distribution[type_name] = type_distribution.get(type_name, 0) + 1

        return {
            "query": query,
            "total_results": len(results),
            "match_types": {
                "semantic": semantic_count,
                "keyword": keyword_count,
                "hybrid": hybrid_count,
            },
            "scores": {
                "average_final_score": avg_score,
                "average_semantic_score": avg_semantic_score,
                "average_keyword_score": avg_keyword_score,
            },
            "type_distribution": type_distribution,
            "search_config": {
                "semantic_weight": self.config.semantic_weight,
                "keyword_weight": self.config.keyword_weight,
                "rerank_enabled": self.config.rerank_enabled,
            },
        }


# Global search engine instance
_hybrid_search_engine: Optional[HybridSearchEngine] = None


def get_hybrid_search_engine(
    vector_memory: VectorMemory, config: Optional[SearchConfig] = None
) -> HybridSearchEngine:
    """Get global hybrid search engine instance."""
    global _hybrid_search_engine
    if _hybrid_search_engine is None:
        _hybrid_search_engine = HybridSearchEngine(vector_memory, config)
    return _hybrid_search_engine
