"""
Intelligent Caching System for OCR
Document similarity detection and smart caching with ML-based similarity
"""

import asyncio
import hashlib
import json
import pickle
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, deque
import redis
import sqlite3
from pathlib import Path

from .models import OCRModelResult, DocumentCharacteristics


@dataclass
class CacheEntry:
    """Cache entry for OCR results."""
    document_hash: str
    extracted_text: str
    confidence_score: float
    processing_time: float
    model_used: str
    page_count: int
    detected_language: str
    structured_data: Optional[Dict[str, Any]]
    document_features: Dict[str, Any]
    created_at: datetime
    last_accessed: datetime
    access_count: int
    size_bytes: int


@dataclass
class SimilarityMatch:
    """Document similarity match result."""
    cached_hash: str
    similarity_score: float
    similarity_type: str  # "exact", "high", "medium", "low"
    confidence_adjustment: float
    applicable: bool
    cached_result: Optional[CacheEntry]


@dataclass
class CacheStatistics:
    """Cache performance statistics."""
    total_entries: int
    hit_rate: float
    miss_rate: float
    average_similarity_score: float
    cache_size_mb: float
    eviction_count: int
    similarity_cache_hits: int
    exact_matches: int
    partial_matches: int


class DocumentFeatureExtractor:
    """Extracts features from documents for similarity detection."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feature_weights = config.get("feature_weights", {
            "text_length": 0.1,
            "word_count": 0.15,
            "unique_words": 0.2,
            "character_distribution": 0.15,
            "language": 0.1,
            "document_type": 0.1,
            "complexity": 0.1,
            "quality": 0.1
        })

    async def extract_features(self, 
                             document_data: bytes, 
                             characteristics: DocumentCharacteristics,
                             extracted_text: str = "") -> Dict[str, Any]:
        """Extract comprehensive features from document."""
        features = {}
        
        # Basic text features
        if extracted_text:
            features.update(self._extract_text_features(extracted_text))
        
        # Document characteristics
        features.update(self._extract_characteristic_features(characteristics))
        
        # Content-based features
        features.update(self._extract_content_features(document_data))
        
        # Structural features
        features.update(self._extract_structural_features(extracted_text))
        
        # Quality features
        features.update(self._extract_quality_features(characteristics))
        
        return features

    def _extract_text_features(self, text: str) -> Dict[str, Any]:
        """Extract features from text content."""
        if not text:
            return {
                "text_length": 0,
                "word_count": 0,
                "unique_words": 0,
                "avg_word_length": 0,
                "sentence_count": 0,
                "punctuation_ratio": 0,
                "numeric_ratio": 0,
                "uppercase_ratio": 0
            }
        
        words = text.split()
        unique_words = set(words.lower())
        
        # Basic counts
        text_length = len(text)
        word_count = len(words)
        unique_word_count = len(unique_words)
        
        # Ratios
        punctuation_chars = set(".,!?;:'\"()-")
        punctuation_count = sum(1 for c in text if c in punctuation_chars)
        numeric_count = sum(1 for c in text if c.isdigit())
        uppercase_count = sum(1 for c in text if c.isupper())
        
        return {
            "text_length": text_length,
            "word_count": word_count,
            "unique_words": unique_word_count,
            "avg_word_length": np.mean([len(w) for w in words]) if words else 0,
            "sentence_count": len(text.split('.')),
            "punctuation_ratio": punctuation_count / text_length if text_length > 0 else 0,
            "numeric_ratio": numeric_count / text_length if text_length > 0 else 0,
            "uppercase_ratio": uppercase_count / text_length if text_length > 0 else 0
        }

    def _extract_characteristic_features(self, characteristics: DocumentCharacteristics) -> Dict[str, Any]:
        """Extract features from document characteristics."""
        return {
            "document_type": characteristics.document_type.value,
            "complexity": characteristics.complexity.value,
            "language": characteristics.language,
            "language_category": characteristics.language_category.value,
            "volume": characteristics.volume.value,
            "has_tables": characteristics.has_tables,
            "has_forms": characteristics.has_forms,
            "has_mathematical_content": characteristics.has_mathematical_content,
            "has_handwriting": characteristics.has_handwriting,
            "image_quality": characteristics.image_quality,
            "resolution_dpi": characteristics.resolution_dpi or 0,
            "page_count": characteristics.page_count,
            "file_size_mb": characteristics.file_size_mb,
            "skew_angle": characteristics.skew_angle,
            "noise_level": characteristics.noise_level,
            "contrast_ratio": characteristics.contrast_ratio
        }

    def _extract_content_features(self, document_data: bytes) -> Dict[str, Any]:
        """Extract content-based features from raw document data."""
        # Hash-based features
        data_hash = hashlib.md5(document_data).hexdigest()
        
        # Statistical features
        data_array = np.frombuffer(document_data, dtype=np.uint8)
        
        return {
            "data_hash": data_hash,
            "data_size": len(document_data),
            "byte_mean": np.mean(data_array) if len(data_array) > 0 else 0,
            "byte_std": np.std(data_array) if len(data_array) > 0 else 0,
            "byte_entropy": self._calculate_entropy(data_array),
            "compression_ratio": self._estimate_compression_ratio(document_data)
        }

    def _extract_structural_features(self, text: str) -> Dict[str, Any]:
        """Extract structural features from text."""
        if not text:
            return {
                "line_count": 0,
                "avg_line_length": 0,
                "paragraph_count": 0,
                "tab_count": 0,
                "space_ratio": 0
            }
        
        lines = text.split('\n')
        paragraphs = text.split('\n\n')
        
        return {
            "line_count": len(lines),
            "avg_line_length": np.mean([len(line) for line in lines]) if lines else 0,
            "paragraph_count": len(paragraphs),
            "tab_count": text.count('\t'),
            "space_ratio": text.count(' ') / len(text) if text else 0
        }

    def _extract_quality_features(self, characteristics: DocumentCharacteristics) -> Dict[str, Any]:
        """Extract quality-related features."""
        return {
            "quality_score": characteristics.image_quality,
            "noise_score": characteristics.noise_level,
            "contrast_score": characteristics.contrast_ratio,
            "skew_score": abs(characteristics.skew_angle) / 45.0,  # Normalized
            "resolution_score": min(characteristics.resolution_dpi / 300, 1.0) if characteristics.resolution_dpi else 0
        }

    def _calculate_entropy(self, data_array: np.ndarray) -> float:
        """Calculate entropy of data."""
        if len(data_array) == 0:
            return 0.0
        
        # Calculate histogram
        hist, _ = np.histogram(data_array, bins=256)
        hist = hist / len(data_array)  # Normalize
        
        # Calculate entropy
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        return entropy

    def _estimate_compression_ratio(self, data: bytes) -> float:
        """Estimate compression ratio."""
        # Simple heuristic based on data patterns
        unique_bytes = len(set(data))
        total_bytes = len(data)
        
        return unique_bytes / total_bytes if total_bytes > 0 else 0


class DocumentSimilarityDetector:
    """Advanced document similarity detection using multiple algorithms."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.similarity_thresholds = config.get("similarity_thresholds", {
            "exact": 0.95,
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        })
        self.algorithm_weights = config.get("algorithm_weights", {
            "hash_based": 0.3,
            "feature_based": 0.4,
            "content_based": 0.3
        })

    async def find_similar_documents(self, 
                                    query_features: Dict[str, Any],
                                    cache_entries: List[CacheEntry],
                                    max_results: int = 10) -> List[SimilarityMatch]:
        """Find similar documents in cache."""
        matches = []
        
        for entry in cache_entries:
            # Calculate similarity using multiple algorithms
            similarity_scores = await self._calculate_similarity_scores(query_features, entry.document_features)
            
            # Combine scores
            combined_score = self._combine_similarity_scores(similarity_scores)
            
            # Determine similarity type
            similarity_type = self._determine_similarity_type(combined_score)
            
            # Check if applicable
            applicable = self._is_applicable(query_features, entry.document_features, combined_score)
            
            # Calculate confidence adjustment
            confidence_adjustment = self._calculate_confidence_adjustment(combined_score, similarity_type)
            
            match = SimilarityMatch(
                cached_hash=entry.document_hash,
                similarity_score=combined_score,
                similarity_type=similarity_type,
                confidence_adjustment=confidence_adjustment,
                applicable=applicable,
                cached_result=entry if applicable else None
            )
            
            matches.append(match)
        
        # Sort by similarity score
        matches.sort(key=lambda m: m.similarity_score, reverse=True)
        
        return matches[:max_results]

    async def _calculate_similarity_scores(self, query_features: Dict[str, Any], cached_features: Dict[str, Any]) -> Dict[str, float]:
        """Calculate similarity scores using different algorithms."""
        scores = {}
        
        # Hash-based similarity
        scores["hash_based"] = self._hash_similarity(query_features, cached_features)
        
        # Feature-based similarity
        scores["feature_based"] = self._feature_similarity(query_features, cached_features)
        
        # Content-based similarity
        scores["content_based"] = self._content_similarity(query_features, cached_features)
        
        return scores

    def _hash_similarity(self, query_features: Dict[str, Any], cached_features: Dict[str, Any]) -> float:
        """Calculate hash-based similarity."""
        # Exact hash match
        if query_features.get("data_hash") == cached_features.get("data_hash"):
            return 1.0
        
        # Partial hash similarity (for similar content)
        query_hash = query_features.get("data_hash", "")
        cached_hash = cached_features.get("data_hash", "")
        
        if query_hash and cached_hash:
            # Compare first few characters of hash
            common_chars = sum(1 for a, b in zip(query_hash, cached_hash) if a == b)
            similarity = common_chars / min(len(query_hash), len(cached_hash))
            return similarity
        
        return 0.0

    def _feature_similarity(self, query_features: Dict[str, Any], cached_features: Dict[str, Any]) -> float:
        """Calculate feature-based similarity."""
        similarity_scores = []
        
        # Numerical features
        numerical_features = [
            "text_length", "word_count", "unique_words", "avg_word_length",
            "sentence_count", "punctuation_ratio", "numeric_ratio", "uppercase_ratio",
            "data_size", "byte_mean", "byte_std", "byte_entropy", "compression_ratio",
            "line_count", "avg_line_length", "paragraph_count", "tab_count",
            "space_ratio", "quality_score", "noise_score", "contrast_score",
            "skew_score", "resolution_score"
        ]
        
        for feature in numerical_features:
            query_val = query_features.get(feature, 0)
            cached_val = cached_features.get(feature, 0)
            
            if query_val == 0 and cached_val == 0:
                similarity = 1.0
            else:
                # Normalized difference
                max_val = max(abs(query_val), abs(cached_val), 1)
                similarity = 1.0 - abs(query_val - cached_val) / max_val
            
            similarity_scores.append(similarity)
        
        # Categorical features
        categorical_features = [
            "document_type", "complexity", "language", "language_category",
            "volume", "has_tables", "has_forms", "has_mathematical_content", "has_handwriting"
        ]
        
        for feature in categorical_features:
            query_val = str(query_features.get(feature, ""))
            cached_val = str(cached_features.get(feature, ""))
            
            similarity = 1.0 if query_val == cached_val else 0.0
            similarity_scores.append(similarity)
        
        return np.mean(similarity_scores) if similarity_scores else 0.0

    def _content_similarity(self, query_features: Dict[str, Any], cached_features: Dict[str, Any]) -> float:
        """Calculate content-based similarity."""
        # Text length similarity
        query_length = query_features.get("text_length", 0)
        cached_length = cached_features.get("text_length", 0)
        
        if query_length == 0 and cached_length == 0:
            length_similarity = 1.0
        else:
            max_length = max(query_length, cached_length, 1)
            length_similarity = 1.0 - abs(query_length - cached_length) / max_length
        
        # Word count similarity
        query_words = query_features.get("word_count", 0)
        cached_words = cached_features.get("word_count", 0)
        
        if query_words == 0 and cached_words == 0:
            word_similarity = 1.0
        else:
            max_words = max(query_words, cached_words, 1)
            word_similarity = 1.0 - abs(query_words - cached_words) / max_words
        
        # Combined content similarity
        return (length_similarity + word_similarity) / 2

    def _combine_similarity_scores(self, scores: Dict[str, float]) -> float:
        """Combine similarity scores from different algorithms."""
        combined_score = 0.0
        
        for algorithm, score in scores.items():
            weight = self.algorithm_weights.get(algorithm, 0.33)
            combined_score += score * weight
        
        return combined_score

    def _determine_similarity_type(self, similarity_score: float) -> str:
        """Determine similarity type based on score."""
        thresholds = self.similarity_thresholds
        
        if similarity_score >= thresholds["exact"]:
            return "exact"
        elif similarity_score >= thresholds["high"]:
            return "high"
        elif similarity_score >= thresholds["medium"]:
            return "medium"
        elif similarity_score >= thresholds["low"]:
            return "low"
        else:
            return "very_low"

    def _is_applicable(self, query_features: Dict[str, Any], cached_features: Dict[str, Any], similarity_score: float) -> bool:
        """Determine if cached result is applicable to query."""
        # High similarity is generally applicable
        if similarity_score >= self.similarity_thresholds["high"]:
            return True
        
        # Medium similarity with same document type
        if (similarity_score >= self.similarity_thresholds["medium"] and
            query_features.get("document_type") == cached_features.get("document_type")):
            return True
        
        # Same language and complexity for medium similarity
        if (similarity_score >= self.similarity_thresholds["medium"] and
            query_features.get("language") == cached_features.get("language") and
            query_features.get("complexity") == cached_features.get("complexity")):
            return True
        
        return False

    def _calculate_confidence_adjustment(self, similarity_score: float, similarity_type: str) -> float:
        """Calculate confidence adjustment based on similarity."""
        # Exact matches get full confidence
        if similarity_type == "exact":
            return 0.0
        
        # High similarity gets small adjustment
        if similarity_type == "high":
            return -0.05
        
        # Medium similarity gets moderate adjustment
        if similarity_type == "medium":
            return -0.1
        
        # Low similarity gets significant adjustment
        if similarity_type == "low":
            return -0.2
        
        # Very low similarity gets large adjustment
        return -0.3


class DistributedCache:
    """Distributed cache implementation using Redis."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = None
        self.local_cache = {}
        self.cache_stats = defaultdict(int)
        
        # Initialize Redis connection
        redis_config = config.get("redis", {})
        if redis_config.get("enabled", False):
            try:
                self.redis_client = redis.Redis(
                    host=redis_config.get("host", "localhost"),
                    port=redis_config.get("port", 6379),
                    db=redis_config.get("db", 0),
                    password=redis_config.get("password"),
                    decode_responses=False
                )
                # Test connection
                self.redis_client.ping()
            except Exception as e:
                print(f"Redis connection failed: {e}, using local cache only")

    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key."""
        try:
            # Try Redis first
            if self.redis_client:
                data = self.redis_client.get(key)
                if data:
                    entry = pickle.loads(data)
                    entry.last_accessed = datetime.utcnow()
                    entry.access_count += 1
                    # Update access time in Redis
                    await self._update_access_stats(key, entry)
                    self.cache_stats["redis_hits"] += 1
                    return entry
            
            # Fallback to local cache
            if key in self.local_cache:
                entry = self.local_cache[key]
                entry.last_accessed = datetime.utcnow()
                entry.access_count += 1
                self.cache_stats["local_hits"] += 1
                return entry
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            print(f"Cache get error: {e}")
            self.cache_stats["errors"] += 1
            return None

    async def set(self, key: str, entry: CacheEntry, ttl: Optional[int] = None):
        """Set cache entry."""
        try:
            # Set in Redis
            if self.redis_client:
                data = pickle.dumps(entry)
                if ttl:
                    self.redis_client.setex(key, ttl, data)
                else:
                    self.redis_client.set(key, data)
            
            # Set in local cache
            self.local_cache[key] = entry
            self.cache_stats["sets"] += 1
            
        except Exception as e:
            print(f"Cache set error: {e}")
            self.cache_stats["errors"] += 1

    async def delete(self, key: str):
        """Delete cache entry."""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            
            if key in self.local_cache:
                del self.local_cache[key]
            
            self.cache_stats["deletes"] += 1
            
        except Exception as e:
            print(f"Cache delete error: {e}")
            self.cache_stats["errors"] += 1

    async def _update_access_stats(self, key: str, entry: CacheEntry):
        """Update access statistics in Redis."""
        try:
            if self.redis_client:
                data = pickle.dumps(entry)
                self.redis_client.set(key, data)
        except Exception as e:
            print(f"Access stats update error: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = sum(self.cache_stats.values())
        
        return {
            "total_requests": total_requests,
            "redis_hits": self.cache_stats["redis_hits"],
            "local_hits": self.cache_stats["local_hits"],
            "misses": self.cache_stats["misses"],
            "sets": self.cache_stats["sets"],
            "deletes": self.cache_stats["deletes"],
            "errors": self.cache_stats["errors"],
            "hit_rate": (self.cache_stats["redis_hits"] + self.cache_stats["local_hits"]) / total_requests if total_requests > 0 else 0,
            "local_cache_size": len(self.local_cache),
            "redis_connected": self.redis_client is not None
        }


class AdaptiveCachePolicy:
    """Adaptive cache policy for intelligent eviction and TTL management."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_cache_size = config.get("max_cache_size_mb", 1024) * 1024 * 1024  # Convert to bytes
        self.default_ttl = config.get("default_ttl_hours", 24) * 3600  # Convert to seconds
        self.access_history = deque(maxlen=1000)
        self.size_history = deque(maxlen=100)

    async def should_cache(self, entry: CacheEntry) -> bool:
        """Determine if entry should be cached."""
        # Don't cache very large entries
        if entry.size_bytes > self.max_cache_size * 0.1:  # 10% of max size
            return False
        
        # Don't cache very low confidence results
        if entry.confidence_score < 0.3:
            return False
        
        # Cache high confidence results
        if entry.confidence_score > 0.8:
            return True
        
        # Cache based on document type
        if entry.document_features.get("document_type") in ["invoice", "receipt", "form"]:
            return True
        
        # Cache based on processing time
        if entry.processing_time > 5.0:  # Expensive to process
            return True
        
        return False

    async def calculate_ttl(self, entry: CacheEntry) -> int:
        """Calculate TTL for cache entry."""
        base_ttl = self.default_ttl
        
        # Adjust based on confidence
        if entry.confidence_score > 0.9:
            base_ttl *= 2  # Keep high confidence results longer
        elif entry.confidence_score < 0.5:
            base_ttl *= 0.5  # Keep low confidence results shorter
        
        # Adjust based on access patterns
        if entry.access_count > 10:
            base_ttl *= 1.5  # Keep frequently accessed entries longer
        
        # Adjust based on document type
        doc_type = entry.document_features.get("document_type")
        if doc_type in ["invoice", "receipt"]:
            base_ttl *= 1.2  # Keep business documents longer
        
        return int(base_ttl)

    async def select_eviction_candidates(self, current_size: int, entries: List[CacheEntry]) -> List[str]:
        """Select entries for eviction when cache is full."""
        if current_size <= self.max_cache_size:
            return []
        
        # Calculate eviction score for each entry
        eviction_scores = []
        
        for entry in entries:
            score = self._calculate_eviction_score(entry)
            eviction_scores.append((entry.document_hash, score))
        
        # Sort by eviction score (higher score = more likely to evict)
        eviction_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Calculate how many to evict
        target_size = self.max_cache_size * 0.8  # Evict to 80% of max size
        size_to_free = current_size - target_size
        
        candidates = []
        size_freed = 0
        
        for hash_val, score in eviction_scores:
            if size_freed >= size_to_free:
                break
            
            # Find entry and calculate size
            for entry in entries:
                if entry.document_hash == hash_val:
                    candidates.append(hash_val)
                    size_freed += entry.size_bytes
                    break
        
        return candidates

    def _calculate_eviction_score(self, entry: CacheEntry) -> float:
        """Calculate eviction score for cache entry."""
        score = 0.0
        
        # Age factor (older entries more likely to be evicted)
        age_hours = (datetime.utcnow() - entry.created_at).total_seconds() / 3600
        score += age_hours * 0.3
        
        # Access frequency factor (less accessed more likely to be evicted)
        access_frequency = entry.access_count / max(age_hours, 1)
        score -= access_frequency * 0.2
        
        # Confidence factor (low confidence more likely to be evicted)
        score += (1.0 - entry.confidence_score) * 0.2
        
        # Size factor (larger entries more likely to be evicted)
        size_mb = entry.size_bytes / (1024 * 1024)
        score += size_mb * 0.1
        
        # Document type factor (some types less important)
        doc_type = entry.document_features.get("document_type", "")
        if doc_type in ["test", "sample"]:
            score += 0.2
        
        return max(0.0, score)


class IntelligentCache:
    """Main intelligent caching system for OCR results."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feature_extractor = DocumentFeatureExtractor(config.get("feature_extractor", {}))
        self.similarity_detector = DocumentSimilarityDetector(config.get("similarity_detector", {}))
        self.distributed_cache = DistributedCache(config.get("distributed_cache", {}))
        self.cache_policy = AdaptiveCachePolicy(config.get("cache_policy", {}))
        
        # Cache statistics
        self.total_requests = 0
        self.cache_hits = 0
        self.similarity_hits = 0
        self.exact_matches = 0

    async def get_or_process(self, 
                           document_data: bytes,
                           characteristics: DocumentCharacteristics,
                           processing_func: callable) -> Tuple[OCRModelResult, bool]:
        """Get result from cache or process document."""
        self.total_requests += 1
        
        # Generate document hash
        document_hash = self._generate_document_hash(document_data)
        
        # Try exact cache match first
        cached_result = await self.distributed_cache.get(document_hash)
        if cached_result:
            self.cache_hits += 1
            self.exact_matches += 1
            
            # Convert to OCRModelResult
            result = self._cache_entry_to_result(cached_result)
            return result, True
        
        # Extract features for similarity detection
        features = await self.feature_extractor.extract_features(
            document_data, characteristics
        )
        
        # Search for similar documents
        cache_entries = await self._get_all_cache_entries()
        similar_matches = await self.similarity_detector.find_similar_documents(
            features, cache_entries
        )
        
        # Check for applicable similar match
        for match in similar_matches:
            if match.applicable and match.cached_result:
                self.similarity_hits += 1
                
                # Adjust confidence based on similarity
                adjusted_confidence = max(
                    0.0,
                    match.cached_result.confidence_score + match.confidence_adjustment
                )
                
                # Create result with adjusted confidence
                result = self._cache_entry_to_result(match.cached_result)
                result.confidence_score = adjusted_confidence
                
                return result, True
        
        # Process document
        result = await processing_func(document_data, characteristics)
        
        # Create cache entry
        cache_entry = await self._create_cache_entry(
            document_hash, result, characteristics, features
        )
        
        # Check if should cache
        if await self.cache_policy.should_cache(cache_entry):
            ttl = await self.cache_policy.calculate_ttl(cache_entry)
            await self.distributed_cache.set(document_hash, cache_entry, ttl)
        
        return result, False

    async def store_result(self, 
                          document_data: bytes,
                          result: OCRModelResult,
                          characteristics: DocumentCharacteristics):
        """Store OCR result in cache."""
        # Generate document hash
        document_hash = self._generate_document_hash(document_data)
        
        # Extract features
        features = await self.feature_extractor.extract_features(
            document_data, characteristics, result.extracted_text
        )
        
        # Create cache entry
        cache_entry = await self._create_cache_entry(
            document_hash, result, characteristics, features
        )
        
        # Store if applicable
        if await self.cache_policy.should_cache(cache_entry):
            ttl = await self.cache_policy.calculate_ttl(cache_entry)
            await self.distributed_cache.set(document_hash, cache_entry, ttl)

    async def invalidate_cache(self, pattern: Optional[str] = None):
        """Invalidate cache entries."""
        if pattern:
            # Invalidate entries matching pattern
            entries = await self._get_all_cache_entries()
            for entry in entries:
                if pattern in entry.document_hash:
                    await self.distributed_cache.delete(entry.document_hash)
        else:
            # Clear all cache
            entries = await self._get_all_cache_entries()
            for entry in entries:
                await self.distributed_cache.delete(entry.document_hash)

    def get_cache_statistics(self) -> CacheStatistics:
        """Get comprehensive cache statistics."""
        cache_stats = self.distributed_cache.get_statistics()
        
        # Calculate additional statistics
        hit_rate = self.cache_hits / self.total_requests if self.total_requests > 0 else 0
        similarity_hit_rate = self.similarity_hits / self.total_requests if self.total_requests > 0 else 0
        exact_match_rate = self.exact_matches / self.total_requests if self.total_requests > 0 else 0
        
        # Get cache size
        entries = asyncio.run(self._get_all_cache_entries())
        total_size = sum(entry.size_bytes for entry in entries)
        cache_size_mb = total_size / (1024 * 1024)
        
        return CacheStatistics(
            total_entries=len(entries),
            hit_rate=hit_rate,
            miss_rate=1 - hit_rate,
            average_similarity_score=0.0,  # Would calculate from similarity matches
            cache_size_mb=cache_size_mb,
            eviction_count=cache_stats.get("deletes", 0),
            similarity_cache_hits=self.similarity_hits,
            exact_matches=self.exact_matches,
            partial_matches=self.similarity_hits - self.exact_matches
        )

    def _generate_document_hash(self, document_data: bytes) -> str:
        """Generate document hash."""
        return hashlib.sha256(document_data).hexdigest()

    def _cache_entry_to_result(self, entry: CacheEntry) -> OCRModelResult:
        """Convert cache entry to OCRModelResult."""
        return OCRModelResult(
            model_name=entry.model_used,
            extracted_text=entry.extracted_text,
            confidence_score=entry.confidence_score,
            processing_time=entry.processing_time,
            structured_data=entry.structured_data,
            page_count=entry.page_count,
            detected_language=entry.detected_language,
            metadata={
                "cached": True,
                "cache_timestamp": entry.created_at.isoformat(),
                "access_count": entry.access_count
            }
        )

    async def _create_cache_entry(self, 
                                document_hash: str,
                                result: OCRModelResult,
                                characteristics: DocumentCharacteristics,
                                features: Dict[str, Any]) -> CacheEntry:
        """Create cache entry from OCR result."""
        entry_size = len(pickle.dumps(result)) + len(json.dumps(features))
        
        return CacheEntry(
            document_hash=document_hash,
            extracted_text=result.extracted_text,
            confidence_score=result.confidence_score,
            processing_time=result.processing_time,
            model_used=result.model_name,
            page_count=result.page_count,
            detected_language=result.detected_language,
            structured_data=result.structured_data,
            document_features=features,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            access_count=1,
            size_bytes=entry_size
        )

    async def _get_all_cache_entries(self) -> List[CacheEntry]:
        """Get all cache entries (simplified implementation)."""
        # In production, would use Redis SCAN or similar
        # For now, return empty list
        return []
