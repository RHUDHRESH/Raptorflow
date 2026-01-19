"""
Intelligent Cache Key Generator with Semantic Hashing
Provides advanced key generation strategies for optimal cache performance
"""

import hashlib
import json
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class KeyGenerationStrategy(Enum):
    """Cache key generation strategies."""
    
    SIMPLE_HASH = "simple_hash"
    SEMANTIC_HASH = "semantic_hash"
    HIERARCHICAL = "hierarchical"
    VERSIONED = "versioned"
    CONTEXT_AWARE = "context_aware"
    ADAPTIVE = "adaptive"


class KeyScope(Enum):
    """Cache key scopes for isolation."""
    
    GLOBAL = "global"
    USER = "user"
    WORKSPACE = "workspace"
    SESSION = "session"
    AGENT = "agent"
    API_ENDPOINT = "api_endpoint"


@dataclass
class KeyMetadata:
    """Metadata for cache keys."""
    
    scope: KeyScope
    entity_type: str
    entity_id: Optional[str]
    context: Dict[str, Any]
    version: str
    tags: Set[str]
    created_at: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at


class SemanticHashGenerator:
    """Generates semantic hashes for similar requests."""
    
    def __init__(self):
        # Common semantic patterns
        self.semantic_patterns = {
            # User query patterns
            'user_query': [
                r'generate|create|make',
                r'analyze|examine|investigate',
                r'update|modify|change',
                r'delete|remove|clear',
                r'list|show|get|fetch'
            ],
            
            # Entity types
            'entity_types': [
                r'icp|customer|persona',
                r'campaign|marketing|promotion',
                r'report|analytics|metrics',
                r'user|account|profile',
                r'agent|ai|model'
            ],
            
            # Action modifiers
            'modifiers': [
                r'quick|fast|immediate',
                r'detailed|comprehensive|complete',
                r'summary|brief|overview',
                r'draft|temp|temporary'
            ],
            
            # Data types
            'data_types': [
                r'text|content|message',
                r'data|information|stats',
                r'file|document|attachment',
                r'image|media|visual'
            ]
        }
        
        # Semantic similarity cache
        self._similarity_cache: Dict[str, float] = {}
    
    def extract_semantic_features(self, text: str) -> Dict[str, List[str]]:
        """Extract semantic features from text."""
        text_lower = text.lower()
        features = {}
        
        for category, patterns in self.semantic_patterns.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    matches.append(pattern)
            features[category] = matches
        
        return features
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        # Check cache first
        cache_key = f"{hash(text1)}_{hash(text2)}"
        if cache_key in self._similarity_cache:
            return self._similarity_cache[cache_key]
        
        features1 = self.extract_semantic_features(text1)
        features2 = self.extract_semantic_features(text2)
        
        # Calculate Jaccard similarity for each category
        similarities = []
        for category in features1:
            if category in features2:
                set1 = set(features1[category])
                set2 = set(features2[category])
                
                if set1 or set2:
                    intersection = len(set1.intersection(set2))
                    union = len(set1.union(set2))
                    similarity = intersection / union if union > 0 else 0
                    similarities.append(similarity)
        
        # Average similarity across all categories
        overall_similarity = sum(similarities) / len(similarities) if similarities else 0
        
        # Cache result
        self._similarity_cache[cache_key] = overall_similarity
        
        return overall_similarity
    
    def generate_semantic_hash(self, text: str, context: Dict[str, Any] = None) -> str:
        """Generate semantic hash for text."""
        features = self.extract_semantic_features(text)
        
        # Combine features with context
        hash_data = {
            'features': features,
            'context': context or {},
            'normalized_text': self._normalize_text(text)
        }
        
        # Generate hash
        hash_string = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(hash_string.encode()).hexdigest()[:16]
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for semantic hashing."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\-_]', ' ', text)
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = text.split()
        words = [word for word in words if word not in stop_words]
        
        return ' '.join(words)


class HierarchicalKeyGenerator:
    """Generates hierarchical cache keys for better organization."""
    
    def __init__(self):
        self.hierarchy_levels = [
            'scope',
            'entity_type',
            'entity_id',
            'action',
            'parameters',
            'version'
        ]
    
    def generate_hierarchical_key(
        self,
        scope: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        action: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        version: str = "v1"
    ) -> str:
        """Generate hierarchical cache key."""
        key_parts = [scope, entity_type]
        
        if entity_id:
            key_parts.append(entity_id)
        
        if action:
            key_parts.append(action)
        
        if parameters:
            # Sort parameters for consistency
            param_string = json.dumps(parameters, sort_keys=True, separators=(',', ':'))
            param_hash = hashlib.md5(param_string.encode()).hexdigest()[:8]
            key_parts.append(param_hash)
        
        key_parts.append(version)
        
        return ':'.join(key_parts)


class VersionedKeyGenerator:
    """Generates versioned cache keys for cache invalidation."""
    
    def __init__(self):
        self.versions: Dict[str, str] = {}
        self.version_history: Dict[str, List[str]] = defaultdict(list)
    
    def get_version(self, entity_type: str, entity_id: str = None) -> str:
        """Get current version for entity."""
        key = f"{entity_type}:{entity_id}" if entity_id else entity_type
        return self.versions.get(key, "v1")
    
    def increment_version(self, entity_type: str, entity_id: str = None) -> str:
        """Increment version for entity."""
        key = f"{entity_type}:{entity_id}" if entity_id else entity_type
        
        current_version = self.versions.get(key, "v1")
        version_number = int(current_version[1:]) + 1
        new_version = f"v{version_number}"
        
        # Update version
        self.versions[key] = new_version
        self.version_history[key].append(new_version)
        
        return new_version
    
    def generate_versioned_key(
        self,
        base_key: str,
        entity_type: str,
        entity_id: str = None
    ) -> str:
        """Generate versioned cache key."""
        version = self.get_version(entity_type, entity_id)
        return f"{base_key}:{version}"


class ContextAwareKeyGenerator:
    """Generates context-aware cache keys."""
    
    def __init__(self):
        self.context_weights = {
            'user_id': 0.3,
            'workspace_id': 0.25,
            'session_id': 0.2,
            'role': 0.1,
            'permissions': 0.1,
            'locale': 0.05
        }
    
    def generate_context_key(
        self,
        base_key: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate context-aware cache key."""
        # Filter and weight context
        weighted_context = {}
        
        for key, value in context.items():
            if key in self.context_weights and value is not None:
                weighted_context[key] = {
                    'value': str(value),
                    'weight': self.context_weights[key]
                }
        
        # Generate context hash
        context_string = json.dumps(weighted_context, sort_keys=True, separators=(',', ':'))
        context_hash = hashlib.md5(context_string.encode()).hexdigest()[:12]
        
        return f"{base_key}:{context_hash}"


class AdaptiveKeyGenerator:
    """Adaptive key generator that learns optimal strategies."""
    
    def __init__(self):
        self.strategy_performance: Dict[str, Dict[str, float]] = defaultdict(lambda: {
            'hit_rate': 0.0,
            'collision_rate': 0.0,
            'generation_time': 0.0,
            'usage_count': 0
        })
        
        self.current_strategy = KeyGenerationStrategy.SEMANTIC_HASH
        self.adaptation_interval = 1000  # Adapt after 1000 uses
        self.usage_count = 0
    
    def select_optimal_strategy(
        self,
        request_type: str,
        context: Dict[str, Any]
    ) -> KeyGenerationStrategy:
        """Select optimal key generation strategy based on context."""
        # Analyze request characteristics
        is_user_query = 'query' in request_type or 'text' in context
        is_api_call = 'endpoint' in request_type or 'method' in context
        has_complex_context = len(context) > 3
        is_frequently_accessed = context.get('access_frequency', 0) > 10
        
        # Strategy selection logic
        if is_frequently_accessed and not has_complex_context:
            return KeyGenerationStrategy.SIMPLE_HASH
        
        elif is_user_query:
            return KeyGenerationStrategy.SEMANTIC_HASH
        
        elif is_api_call:
            return KeyGenerationStrategy.HIERARCHICAL
        
        elif has_complex_context:
            return KeyGenerationStrategy.CONTEXT_AWARE
        
        else:
            return KeyGenerationStrategy.ADAPTIVE
    
    def update_strategy_performance(
        self,
        strategy: KeyGenerationStrategy,
        hit: bool,
        collision: bool,
        generation_time: float
    ):
        """Update strategy performance metrics."""
        strategy_name = strategy.value
        metrics = self.strategy_performance[strategy_name]
        
        # Update metrics with exponential moving average
        alpha = 0.1
        
        metrics['hit_rate'] = (alpha * (1.0 if hit else 0.0) + 
                             (1 - alpha) * metrics['hit_rate'])
        metrics['collision_rate'] = (alpha * (1.0 if collision else 0.0) + 
                                   (1 - alpha) * metrics['collision_rate'])
        metrics['generation_time'] = (alpha * generation_time + 
                                    (1 - alpha) * metrics['generation_time'])
        metrics['usage_count'] += 1
        
        # Check if adaptation is needed
        self.usage_count += 1
        if self.usage_count >= self.adaptation_interval:
            self._adapt_strategy()
            self.usage_count = 0
    
    def _adapt_strategy(self):
        """Adapt to best performing strategy."""
        best_strategy = None
        best_score = -1
        
        for strategy_name, metrics in self.strategy_performance.items():
            if metrics['usage_count'] > 0:
                # Calculate performance score
                score = (
                    metrics['hit_rate'] * 0.5 -
                    metrics['collision_rate'] * 0.3 -
                    metrics['generation_time'] * 0.2
                )
                
                if score > best_score:
                    best_score = score
                    best_strategy = KeyGenerationStrategy(strategy_name)
        
        if best_strategy:
            self.current_strategy = best_strategy
            logger.info(f"Adapted to strategy: {best_strategy.value}")


class CacheKeyGenerator:
    """Main cache key generator with multiple strategies."""
    
    def __init__(self, default_strategy: KeyGenerationStrategy = KeyGenerationStrategy.SEMANTIC_HASH):
        self.default_strategy = default_strategy
        
        # Initialize strategy generators
        self.semantic_generator = SemanticHashGenerator()
        self.hierarchical_generator = HierarchicalKeyGenerator()
        self.versioned_generator = VersionedKeyGenerator()
        self.context_generator = ContextAwareKeyGenerator()
        self.adaptive_generator = AdaptiveKeyGenerator()
        
        # Key metadata storage
        self.key_metadata: Dict[str, KeyMetadata] = {}
        
        # Performance tracking
        self.generation_stats = {
            'total_keys': 0,
            'strategy_usage': defaultdict(int),
            'average_generation_time': 0.0,
            'collision_count': 0
        }
        
        # Key collision detection
        self.key_reverse_map: Dict[str, Set[str]] = defaultdict(set)
    
    def generate_key(
        self,
        entity_type: str,
        entity_id: Optional[str] = None,
        action: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        strategy: Optional[KeyGenerationStrategy] = None,
        scope: KeyScope = KeyScope.GLOBAL,
        version: str = "v1",
        tags: Optional[Set[str]] = None
    ) -> str:
        """Generate cache key using specified or optimal strategy."""
        start_time = time.time()
        
        # Prepare inputs
        context = context or {}
        parameters = parameters or {}
        tags = tags or set()
        strategy = strategy or self.default_strategy
        
        # Select optimal strategy if adaptive
        if strategy == KeyGenerationStrategy.ADAPTIVE:
            strategy = self.adaptive_generator.select_optimal_strategy(entity_type, context)
        
        # Generate key based on strategy
        if strategy == KeyGenerationStrategy.SIMPLE_HASH:
            key = self._generate_simple_hash(entity_type, entity_id, action, parameters)
        
        elif strategy == KeyGenerationStrategy.SEMANTIC_HASH:
            key = self._generate_semantic_key(entity_type, entity_id, action, parameters, context)
        
        elif strategy == KeyGenerationStrategy.HIERARCHICAL:
            key = self._generate_hierarchical_key(entity_type, entity_id, action, parameters, version)
        
        elif strategy == KeyGenerationStrategy.VERSIONED:
            base_key = self._generate_simple_hash(entity_type, entity_id, action, parameters)
            key = self.versioned_generator.generate_versioned_key(base_key, entity_type, entity_id)
        
        elif strategy == KeyGenerationStrategy.CONTEXT_AWARE:
            base_key = self._generate_simple_hash(entity_type, entity_id, action, parameters)
            key = self.context_generator.generate_context_key(base_key, context)
        
        else:
            # Default to semantic hash
            key = self._generate_semantic_key(entity_type, entity_id, action, parameters, context)
        
        # Add scope prefix
        key = f"{scope.value}:{key}"
        
        # Update metadata
        generation_time = time.time() - start_time
        self._update_key_metadata(key, scope, entity_type, entity_id, context, version, tags)
        self._update_generation_stats(strategy, generation_time)
        
        # Check for collisions
        self._check_collision(key, entity_type, entity_id, action, parameters)
        
        return key
    
    def _generate_simple_hash(
        self,
        entity_type: str,
        entity_id: Optional[str],
        action: Optional[str],
        parameters: Dict[str, Any]
    ) -> str:
        """Generate simple hash-based key."""
        key_data = {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'action': action,
            'parameters': parameters
        }
        
        key_string = json.dumps(key_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def _generate_semantic_key(
        self,
        entity_type: str,
        entity_id: Optional[str],
        action: Optional[str],
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Generate semantic hash-based key."""
        # Combine all components for semantic analysis
        combined_text = f"{entity_type} {entity_id or ''} {action or ''}"
        
        # Add parameter keys (not values) for semantic matching
        if parameters:
            param_keys = ' '.join(parameters.keys())
            combined_text += f" {param_keys}"
        
        # Generate semantic hash
        semantic_hash = self.semantic_generator.generate_semantic_hash(combined_text, context)
        
        # Add entity-specific hash for uniqueness
        entity_data = f"{entity_type}:{entity_id}:{action}"
        entity_hash = hashlib.md5(entity_data.encode()).hexdigest()[:8]
        
        return f"semantic:{semantic_hash}:{entity_hash}"
    
    def _generate_hierarchical_key(
        self,
        entity_type: str,
        entity_id: Optional[str],
        action: Optional[str],
        parameters: Dict[str, Any],
        version: str
    ) -> str:
        """Generate hierarchical key."""
        return self.hierarchical_generator.generate_hierarchical_key(
            scope="cache",
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            parameters=parameters,
            version=version
        )
    
    def _update_key_metadata(
        self,
        key: str,
        scope: KeyScope,
        entity_type: str,
        entity_id: Optional[str],
        context: Dict[str, Any],
        version: str,
        tags: Set[str]
    ):
        """Update key metadata."""
        metadata = KeyMetadata(
            scope=scope,
            entity_type=entity_type,
            entity_id=entity_id,
            context=context.copy(),
            version=version,
            tags=tags.copy(),
            created_at=datetime.now()
        )
        
        self.key_metadata[key] = metadata
    
    def _update_generation_stats(
        self,
        strategy: KeyGenerationStrategy,
        generation_time: float
    ):
        """Update generation statistics."""
        self.generation_stats['total_keys'] += 1
        self.generation_stats['strategy_usage'][strategy.value] += 1
        
        # Update average generation time
        current_avg = self.generation_stats['average_generation_time']
        self.generation_stats['average_generation_time'] = (
            (current_avg + generation_time) / 2
        )
        
        # Update adaptive generator performance
        if hasattr(self, '_last_hit'):
            self.adaptive_generator.update_strategy_performance(
                strategy, self._last_hit, False, generation_time
            )
    
    def _check_collision(
        self,
        key: str,
        entity_type: str,
        entity_id: Optional[str],
        action: Optional[str],
        parameters: Dict[str, Any]
    ):
        """Check for key collisions."""
        # Create signature for collision detection
        signature = f"{entity_type}:{entity_id}:{action}:{hash(json.dumps(parameters, sort_keys=True))}"
        
        if signature in self.key_reverse_map:
            # Check if this is a true collision (different data, same key)
            existing_keys = self.key_reverse_map[signature]
            if key not in existing_keys:
                self.generation_stats['collision_count'] += 1
                logger.warning(f"Key collision detected: {key}")
        
        self.key_reverse_map[signature].add(key)
    
    def invalidate_by_entity(
        self,
        entity_type: str,
        entity_id: Optional[str] = None
    ) -> List[str]:
        """Invalidate all keys for specific entity."""
        keys_to_invalidate = []
        
        for key, metadata in self.key_metadata.items():
            if (metadata.entity_type == entity_type and 
                (entity_id is None or metadata.entity_id == entity_id)):
                keys_to_invalidate.append(key)
        
        # Increment version for versioned keys
        self.versioned_generator.increment_version(entity_type, entity_id)
        
        return keys_to_invalidate
    
    def invalidate_by_scope(self, scope: KeyScope) -> List[str]:
        """Invalidate all keys for specific scope."""
        keys_to_invalidate = []
        
        for key, metadata in self.key_metadata.items():
            if metadata.scope == scope:
                keys_to_invalidate.append(key)
        
        return keys_to_invalidate
    
    def invalidate_by_tags(self, tags: Set[str]) -> List[str]:
        """Invalidate all keys with specific tags."""
        keys_to_invalidate = []
        
        for key, metadata in self.key_metadata.items():
            if metadata.tags.intersection(tags):
                keys_to_invalidate.append(key)
        
        return keys_to_invalidate
    
    def get_key_metadata(self, key: str) -> Optional[KeyMetadata]:
        """Get metadata for a specific key."""
        metadata = self.key_metadata.get(key)
        if metadata:
            metadata.access_count += 1
            metadata.last_accessed = datetime.now()
        return metadata
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get key generation statistics."""
        return {
            'total_keys': self.generation_stats['total_keys'],
            'strategy_usage': dict(self.generation_stats['strategy_usage']),
            'average_generation_time': self.generation_stats['average_generation_time'],
            'collision_count': self.generation_stats['collision_count'],
            'collision_rate': (
                self.generation_stats['collision_count'] / 
                max(self.generation_stats['total_keys'], 1)
            ),
            'adaptive_strategy': self.adaptive_generator.current_strategy.value,
            'key_metadata_count': len(self.key_metadata)
        }
    
    def analyze_key_patterns(self) -> Dict[str, Any]:
        """Analyze key generation patterns."""
        # Analyze entity types
        entity_type_counts = defaultdict(int)
        scope_counts = defaultdict(int)
        
        for metadata in self.key_metadata.values():
            entity_type_counts[metadata.entity_type] += 1
            scope_counts[metadata.scope.value] += 1
        
        # Analyze access patterns
        access_counts = [m.access_count for m in self.key_metadata.values()]
        avg_access = sum(access_counts) / len(access_counts) if access_counts else 0
        
        return {
            'entity_type_distribution': dict(entity_type_counts),
            'scope_distribution': dict(scope_counts),
            'average_access_count': avg_access,
            'total_metadata_entries': len(self.key_metadata),
            'most_common_entity_type': max(entity_type_counts.items(), key=lambda x: x[1])[0] if entity_type_counts else None
        }


# Global key generator instance
_key_generator: Optional[CacheKeyGenerator] = None


def get_cache_key_generator() -> CacheKeyGenerator:
    """Get the global cache key generator."""
    global _key_generator
    if _key_generator is None:
        _key_generator = CacheKeyGenerator()
    return _key_generator


# Convenience functions
def generate_cache_key(
    entity_type: str,
    entity_id: Optional[str] = None,
    action: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
    scope: KeyScope = KeyScope.GLOBAL
) -> str:
    """Generate cache key (convenience function)."""
    generator = get_cache_key_generator()
    return generator.generate_key(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        parameters=parameters,
        context=context,
        scope=scope
    )


def invalidate_entity_cache(
    entity_type: str,
    entity_id: Optional[str] = None
) -> List[str]:
    """Invalidate cache for entity (convenience function)."""
    generator = get_cache_key_generator()
    return generator.invalidate_by_entity(entity_type, entity_id)


def get_key_generation_stats() -> Dict[str, Any]:
    """Get key generation statistics (convenience function)."""
    generator = get_cache_key_generator()
    return generator.get_generation_stats()
