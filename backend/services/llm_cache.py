"""
Semantic Caching Service for LLM responses
Uses Redis to cache semantically similar queries and responses
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from cache import CacheService
from client import get_redis

logger = logging.getLogger(__name__)


class LLMSemanticCache:
    """Semantic caching for LLM responses with similarity matching"""

    def __init__(self):
        self.cache = CacheService()
        self.redis = get_redis()
        self.similarity_threshold = 0.8  # Cosine similarity threshold
        self.max_cache_entries = 1000
        self.cache_ttl = 3600  # 1 hour

    def _generate_query_hash(self, query: str) -> str:
        """Generate hash for query normalization"""
        normalized = query.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for similarity matching"""
        # Simple keyword extraction (can be enhanced with NLP)
        words = text.lower().split()
        keywords = [word.strip(".,!?()[]{}\"'") for word in words if len(word) > 3]
        return list(set(keywords))  # Remove duplicates

    def _calculate_similarity(self, query1: str, query2: str) -> float:
        """Calculate semantic similarity between two queries"""
        keywords1 = set(self._extract_keywords(query1))
        keywords2 = set(self._extract_keywords(query2))

        if not keywords1 or not keywords2:
            return 0.0

        # Jaccard similarity
        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))

        return intersection / union if union > 0 else 0.0

    async def get_cached_response(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response using semantic similarity search

        Args:
            query: The input query to search for

        Returns:
            Cached response data if found, None otherwise
        """
        try:
            query_hash = self._generate_query_hash(query)
            keywords = self._extract_keywords(query)

            # First try exact match
            exact_key = f"llm_cache:exact:{query_hash}"
            exact_result = await self.redis.get_json(exact_key)
            if exact_result:
                logger.info(f"Exact cache hit for query: {query[:50]}...")
                return exact_result

            # Search for semantically similar queries
            semantic_key = f"llm_cache:semantic:{query_hash}"
            semantic_results = await self.redis.get_json(semantic_key)

            if semantic_results:
                # Check similarity with cached queries
                for cached_query, cached_data in semantic_results.items():
                    similarity = self._calculate_similarity(query, cached_query)

                    if similarity >= self.similarity_threshold:
                        logger.info(
                            f"Semantic cache hit (similarity: {similarity:.2f}) "
                            f"for query: {query[:50]}..."
                        )

                        # Update access time and hit count
                        cached_data["last_accessed"] = datetime.now().isoformat()
                        cached_data["hit_count"] = cached_data.get("hit_count", 0) + 1
                        cached_data["similarity_score"] = similarity

                        # Update the cache entry
                        await self.redis.set_json(
                            semantic_key, semantic_results, ex=self.cache_ttl
                        )

                        return cached_data

            # No cache hit
            logger.info(f"Cache miss for query: {query[:50]}...")
            return None

        except Exception as e:
            logger.error(f"Error getting cached response: {e}")
            return None

    async def cache_response(
        self, query: str, response: Any, metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Cache a response with semantic indexing

        Args:
            query: The input query
            response: The response to cache
            metadata: Additional metadata to store

        Returns:
            True if cached successfully, False otherwise
        """
        try:
            query_hash = self._generate_query_hash(query)

            # Prepare cache data
            cache_data = {
                "query": query,
                "response": response,
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "hit_count": 0,
                "keywords": self._extract_keywords(query),
                "metadata": metadata or {},
            }

            # Store exact match
            exact_key = f"llm_cache:exact:{query_hash}"
            await self.redis.set_json(exact_key, cache_data, ex=self.cache_ttl)

            # Update semantic index
            semantic_key = f"llm_cache:semantic:{query_hash}"
            existing_semantic = await self.redis.get_json(semantic_key) or {}

            # Add to semantic index (limit size)
            existing_semantic[query] = cache_data
            if len(existing_semantic) > 10:  # Keep only recent 10 entries
                # Remove oldest entry
                oldest_query = min(
                    existing_semantic.keys(),
                    key=lambda q: existing_semantic[q]["created_at"],
                )
                del existing_semantic[oldest_query]

            await self.redis.set_json(
                semantic_key, existing_semantic, ex=self.cache_ttl
            )

            # Update global cache index
            await self._update_global_index(query_hash, query)

            logger.info(f"Cached response for query: {query[:50]}...")
            return True

        except Exception as e:
            logger.error(f"Error caching response: {e}")
            return False

    async def _update_global_index(self, query_hash: str, query: str):
        """Update global cache index for management"""
        try:
            index_key = "llm_cache:global_index"
            existing_index = await self.redis.get_json(index_key) or {}

            existing_index[query_hash] = {
                "query": query,
                "created_at": datetime.now().isoformat(),
                "keywords": self._extract_keywords(query),
            }

            # Limit index size
            if len(existing_index) > self.max_cache_entries:
                # Remove oldest entries
                sorted_entries = sorted(
                    existing_index.items(), key=lambda x: x[1]["created_at"]
                )
                entries_to_remove = len(existing_index) - self.max_cache_entries
                for i in range(entries_to_remove):
                    del existing_index[sorted_entries[i][0]]

            await self.redis.set_json(index_key, existing_index, ex=self.cache_ttl * 2)

        except Exception as e:
            logger.error(f"Error updating global index: {e}")

    async def clear_cache(self, pattern: Optional[str] = None) -> bool:
        """
        Clear cache entries

        Args:
            pattern: Pattern to match (e.g., "llm_cache:*"), None for all

        Returns:
            True if cleared successfully
        """
        try:
            if pattern:
                # Delete matching keys
                keys = await self.redis.keys(pattern)
                if keys:
                    await self.redis.delete(*keys)
            else:
                # Clear all LLM cache
                patterns = [
                    "llm_cache:exact:*",
                    "llm_cache:semantic:*",
                    "llm_cache:global_index",
                ]
                for p in patterns:
                    keys = await self.redis.keys(p)
                    if keys:
                        await self.redis.delete(*keys)

            logger.info(f"Cleared cache with pattern: {pattern or 'all'}")
            return True

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics and performance metrics"""
        try:
            index_key = "llm_cache:global_index"
            global_index = await self.redis.get_json(index_key) or {}

            # Count exact and semantic cache entries
            exact_keys = await self.redis.keys("llm_cache:exact:*")
            semantic_keys = await self.redis.keys("llm_cache:semantic:*")

            stats = {
                "total_entries": len(global_index),
                "exact_cache_entries": len(exact_keys),
                "semantic_cache_entries": len(semantic_keys),
                "similarity_threshold": self.similarity_threshold,
                "cache_ttl_seconds": self.cache_ttl,
                "max_entries": self.max_cache_entries,
                "last_updated": datetime.now().isoformat(),
            }

            # Calculate hit rates (simplified)
            total_hits = sum(
                entry.get("hit_count", 0) for entry in global_index.values()
            )
            stats["total_hits"] = total_hits
            stats["average_hits_per_entry"] = (
                total_hits / len(global_index) if global_index else 0
            )

            return stats

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}


# Global instance
_semantic_cache: Optional[LLMSemanticCache] = None


def get_semantic_cache() -> LLMSemanticCache:
    """Get the global semantic cache instance"""
    global _semantic_cache
    if _semantic_cache is None:
        _semantic_cache = LLMSemanticCache()
    return _semantic_cache
