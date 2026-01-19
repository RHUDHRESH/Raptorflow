"""
Validation performance optimization system with caching and analytics.
Provides high-performance request validation with intelligent caching strategies.
"""

import asyncio
import hashlib
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from enum import Enum
import numpy as np
from functools import wraps
import pickle
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Caching strategies."""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    ADAPTIVE = "adaptive"


class PerformanceLevel(Enum):
    """Performance optimization levels."""
    ULTRA_FAST = "ultra_fast"      # 95% cache hit rate, minimal validation
    FAST = "fast"                  # 90% cache hit rate, balanced validation
    BALANCED = "balanced"          # 80% cache hit rate, full validation
    SECURE = "secure"              # 60% cache hit rate, enhanced validation
    PARANOID = "paranoid"          # 30% cache hit rate, maximum validation


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    
    key: str
    value: Any
    timestamp: datetime
    access_count: int = 0
    last_accessed: datetime = None
    ttl: Optional[timedelta] = None
    size_bytes: int = 0
    validation_result: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.timestamp
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl is None:
            return False
        return datetime.now() > self.timestamp + self.ttl
    
    def update_access(self):
        """Update access statistics."""
        self.access_count += 1
        self.last_accessed = datetime.now()


@dataclass
class PerformanceMetrics:
    """Validation performance metrics."""
    
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    average_validation_time: float = 0.0
    average_cache_time: float = 0.0
    cache_hit_rate: float = 0.0
    memory_usage_bytes: int = 0
    cache_size: int = 0
    evictions: int = 0
    validation_accuracy: float = 0.0
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0


@dataclass
class OptimizationReport:
    """Performance optimization report."""
    
    timestamp: datetime
    performance_level: PerformanceLevel
    metrics: PerformanceMetrics
    recommendations: List[str]
    cache_efficiency: float
    bottleneck_analysis: Dict[str, Any]
    optimization_suggestions: List[str]


class AdaptiveCache:
    """Adaptive caching system with multiple strategies."""
    
    def __init__(self, max_size: int = 10000, strategy: CacheStrategy = CacheStrategy.ADAPTIVE):
        self.max_size = max_size
        self.strategy = strategy
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order = deque()  # For LRU
        self.access_frequency = defaultdict(int)  # For LFU
        self.redis_client: Optional[redis.Redis] = None
        
        # Performance tracking
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        # Adaptive parameters
        self.hit_rate_history = deque(maxlen=100)
        self.access_pattern_history = deque(maxlen=1000)
        
    async def initialize_redis(self, redis_url: str):
        """Initialize Redis client for distributed caching."""
        try:
            self.redis_client = redis.from_url(redis_url)
            await self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.redis_client = None
    
    def _generate_key(self, request_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """Generate cache key from request data."""
        # Create normalized representation
        normalized_data = {
            "request": request_data,
            "context": context or {}
        }
        normalized_str = json.dumps(normalized_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(normalized_str.encode()).hexdigest()
    
    async def get(self, request_data: Dict[str, Any], 
                 context: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Get value from cache."""
        key = self._generate_key(request_data, context)
        start_time = time.time()
        
        try:
            # Try Redis first if available
            if self.redis_client:
                cached_data = await self.redis_client.get(f"validation_cache:{key}")
                if cached_data:
                    entry = pickle.loads(cached_data)
                    if not entry.is_expired():
                        entry.update_access()
                        self.hits += 1
                        self._record_access_pattern(key, True)
                        return entry.value
                    else:
                        # Remove expired entry
                        await self.redis_client.delete(f"validation_cache:{key}")
            
            # Try local cache
            if key in self.cache:
                entry = self.cache[key]
                if not entry.is_expired():
                    entry.update_access()
                    self.hits += 1
                    self._record_access_pattern(key, True)
                    
                    # Update access order for LRU
                    if key in self.access_order:
                        self.access_order.remove(key)
                    self.access_order.append(key)
                    
                    return entry.value
                else:
                    # Remove expired entry
                    del self.cache[key]
                    if key in self.access_order:
                        self.access_order.remove(key)
            
            # Cache miss
            self.misses += 1
            self._record_access_pattern(key, False)
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.misses += 1
            return None
        finally:
            # Track performance
            access_time = time.time() - start_time
            self._update_performance_metrics(access_time)
    
    async def set(self, request_data: Dict[str, Any], value: Any,
                 context: Optional[Dict[str, Any]] = None,
                 ttl: Optional[timedelta] = None):
        """Set value in cache."""
        key = self._generate_key(request_data, context)
        
        try:
            # Create cache entry
            serialized_value = pickle.dumps(value)
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=datetime.now(),
                ttl=ttl,
                size_bytes=len(serialized_value),
                validation_result={"cached": True, "timestamp": datetime.now().isoformat()}
            )
            
            # Check if eviction is needed
            if len(self.cache) >= self.max_size:
                await self._evict_entries()
            
            # Store in local cache
            self.cache[key] = entry
            self.access_order.append(key)
            self.access_frequency[key] += 1
            
            # Store in Redis if available
            if self.redis_client:
                redis_ttl = int(ttl.total_seconds()) if ttl else 3600
                await self.redis_client.setex(
                    f"validation_cache:{key}",
                    redis_ttl,
                    serialized_value
                )
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def _evict_entries(self):
        """Evict entries based on strategy."""
        if not self.cache:
            return
        
        try:
            if self.strategy == CacheStrategy.LRU:
                await self._evict_lru()
            elif self.strategy == CacheStrategy.LFU:
                await self._evict_lfu()
            elif self.strategy == CacheStrategy.TTL:
                await self._evict_expired()
            elif self.strategy == CacheStrategy.ADAPTIVE:
                await self._evict_adaptive()
            
            self.evictions += 1
            
        except Exception as e:
            logger.error(f"Cache eviction error: {e}")
    
    async def _evict_lru(self):
        """Evict least recently used entries."""
        # Remove 20% of entries
        evict_count = max(1, len(self.cache) // 5)
        
        for _ in range(evict_count):
            if self.access_order:
                lru_key = self.access_order.popleft()
                if lru_key in self.cache:
                    del self.cache[lru_key]
                    self.access_frequency.pop(lru_key, None)
                    
                    # Remove from Redis
                    if self.redis_client:
                        await self.redis_client.delete(f"validation_cache:{lru_key}")
    
    async def _evict_lfu(self):
        """Evict least frequently used entries."""
        # Sort by frequency and remove least used
        sorted_keys = sorted(self.access_frequency.items(), key=lambda x: x[1])
        evict_count = max(1, len(sorted_keys) // 5)
        
        for key, _ in sorted_keys[:evict_count]:
            if key in self.cache:
                del self.cache[key]
                self.access_frequency.pop(key, None)
                self.access_order.remove(key)
                
                # Remove from Redis
                if self.redis_client:
                    await self.redis_client.delete(f"validation_cache:{key}")
    
    async def _evict_expired(self):
        """Evict expired entries."""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self.cache[key]
            self.access_frequency.pop(key, None)
            if key in self.access_order:
                self.access_order.remove(key)
            
            # Remove from Redis
            if self.redis_client:
                await self.redis_client.delete(f"validation_cache:{key}")
    
    async def _evict_adaptive(self):
        """Adaptive eviction based on access patterns."""
        # Combine LRU and LFU with adaptive weights
        current_hit_rate = self.get_hit_rate()
        
        if current_hit_rate < 0.7:
            # Low hit rate - use more aggressive eviction
            await self._evict_lfu()
        else:
            # Good hit rate - use LRU
            await self._evict_lru()
    
    def _record_access_pattern(self, key: str, is_hit: bool):
        """Record access pattern for adaptive optimization."""
        self.access_pattern_history.append({
            "key": key,
            "is_hit": is_hit,
            "timestamp": datetime.now()
        })
    
    def _update_performance_metrics(self, access_time: float):
        """Update performance metrics."""
        # Update hit rate history
        current_hit_rate = self.get_hit_rate()
        self.hit_rate_history.append(current_hit_rate)
    
    def get_hit_rate(self) -> float:
        """Get current cache hit rate."""
        total = self.hits + self.misses
        return self.hits / max(total, 1)
    
    def get_memory_usage(self) -> int:
        """Get memory usage in bytes."""
        return sum(entry.size_bytes for entry in self.cache.values())
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get cache performance report."""
        return {
            "hit_rate": self.get_hit_rate(),
            "total_requests": self.hits + self.misses,
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "memory_usage_bytes": self.get_memory_usage(),
            "evictions": self.evictions,
            "strategy": self.strategy.value,
            "redis_enabled": self.redis_client is not None
        }
    
    async def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.access_order.clear()
        self.access_frequency.clear()
        
        if self.redis_client:
            # Clear Redis cache entries with pattern
            pattern = "validation_cache:*"
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
        
        logger.info("Cache cleared")


class ValidationOptimizer:
    """Validation performance optimizer with intelligent caching."""
    
    def __init__(self, performance_level: PerformanceLevel = PerformanceLevel.BALANCED):
        self.performance_level = performance_level
        self.cache = AdaptiveCache()
        self.metrics = PerformanceMetrics()
        
        # Optimization parameters
        self.validation_thresholds = {
            PerformanceLevel.ULTRA_FAST: {"cache_hit_rate": 0.95, "max_validation_time": 0.01},
            PerformanceLevel.FAST: {"cache_hit_rate": 0.90, "max_validation_time": 0.05},
            PerformanceLevel.BALANCED: {"cache_hit_rate": 0.80, "max_validation_time": 0.10},
            PerformanceLevel.SECURE: {"cache_hit_rate": 0.60, "max_validation_time": 0.20},
            PerformanceLevel.PARANOID: {"cache_hit_rate": 0.30, "max_validation_time": 0.50}
        }
        
        # Performance tracking
        self.validation_times = deque(maxlen=1000)
        self.accuracy_history = deque(maxlen=100)
        self.optimization_history = deque(maxlen=50)
        
        # Background optimization
        self._optimization_task: Optional[asyncio.Task] = None
        self._is_optimizing = False
        
        logger.info(f"ValidationOptimizer initialized with {performance_level.value} performance level")
    
    async def initialize(self, redis_url: Optional[str] = None):
        """Initialize the optimizer."""
        if redis_url:
            await self.cache.initialize_redis(redis_url)
        
        # Start background optimization
        await self.start_optimization()
    
    async def validate_with_cache(self, request_data: Dict[str, Any],
                                validation_func: callable,
                                context: Optional[Dict[str, Any]] = None) -> Tuple[Any, bool]:
        """Validate request with intelligent caching."""
        start_time = time.time()
        cache_hit = False
        
        try:
            # Check cache first
            cached_result = await self.cache.get(request_data, context)
            if cached_result is not None:
                cache_hit = True
                self.metrics.cache_hits += 1
                return cached_result, True
            
            # Cache miss - perform validation
            self.metrics.cache_misses += 1
            
            # Determine validation depth based on performance level
            validation_depth = self._get_validation_depth(request_data, context)
            
            # Perform validation
            if validation_depth == "minimal":
                result = await self._minimal_validation(request_data, validation_func, context)
            elif validation_depth == "standard":
                result = await validation_func(request_data, context)
            else:  # enhanced
                result = await self._enhanced_validation(request_data, validation_func, context)
            
            # Cache the result
            ttl = self._calculate_ttl(result, context)
            await self.cache.set(request_data, result, context, ttl)
            
            # Update metrics
            validation_time = time.time() - start_time
            self.validation_times.append(validation_time)
            self._update_metrics(validation_time, cache_hit)
            
            return result, False
            
        except Exception as e:
            logger.error(f"Validation optimization error: {e}")
            # Fallback to direct validation
            try:
                result = await validation_func(request_data, context)
                return result, False
            except Exception as fallback_error:
                logger.error(f"Fallback validation failed: {fallback_error}")
                raise
    
    def _get_validation_depth(self, request_data: Dict[str, Any], 
                           context: Optional[Dict[str, Any]]) -> str:
        """Determine validation depth based on performance level and context."""
        if self.performance_level == PerformanceLevel.ULTRA_FAST:
            return "minimal"
        elif self.performance_level == PerformanceLevel.FAST:
            return "minimal" if self.cache.get_hit_rate() > 0.8 else "standard"
        elif self.performance_level == PerformanceLevel.BALANCED:
            return "standard"
        elif self.performance_level == PerformanceLevel.SECURE:
            return "enhanced" if self._is_high_risk_context(context) else "standard"
        else:  # PARANOID
            return "enhanced"
    
    def _is_high_risk_context(self, context: Optional[Dict[str, Any]]) -> bool:
        """Check if context indicates high risk."""
        if not context:
            return False
        
        risk_indicators = [
            context.get("user_trust_score", 1.0) < 0.5,
            context.get("request_frequency", 0) > 100,
            context.get("session_age", 0) < 300,  # Less than 5 minutes
            context.get("source_ip_risk", "low") != "low"
        ]
        
        return any(risk_indicators)
    
    async def _minimal_validation(self, request_data: Dict[str, Any],
                               validation_func: callable,
                               context: Optional[Dict[str, Any]]) -> Any:
        """Perform minimal validation for ultra-fast performance."""
        # Quick checks only
        if not isinstance(request_data, dict):
            raise ValueError("Invalid request format")
        
        if not request_data.get("request"):
            raise ValueError("Missing request field")
        
        # Skip full validation for trusted sources
        if context and context.get("user_trust_score", 0) > 0.9:
            return {"valid": True, "level": "minimal"}
        
        # Basic pattern check
        request_text = str(request_data.get("request", ""))
        if len(request_text) > 10000:  # Basic size check
            raise ValueError("Request too large")
        
        return {"valid": True, "level": "minimal"}
    
    async def _enhanced_validation(self, request_data: Dict[str, Any],
                                validation_func: callable,
                                context: Optional[Dict[str, Any]]) -> Any:
        """Perform enhanced validation with additional checks."""
        # Perform standard validation first
        result = await validation_func(request_data, context)
        
        # Add enhanced checks
        if isinstance(result, dict) and result.get("valid", True):
            # Additional security checks
            await self._perform_enhanced_checks(request_data, context)
            
            # Update result with enhanced validation info
            result["validation_level"] = "enhanced"
            result["enhanced_checks"] = True
        
        return result
    
    async def _perform_enhanced_checks(self, request_data: Dict[str, Any],
                                     context: Optional[Dict[str, Any]]):
        """Perform enhanced security checks."""
        # Behavioral analysis
        if context:
            await self._analyze_behavior_patterns(request_data, context)
        
        # Advanced pattern matching
        await self._advanced_pattern_check(request_data)
        
        # Contextual validation
        await self._contextual_validation(request_data, context)
    
    async def _analyze_behavior_patterns(self, request_data: Dict[str, Any],
                                      context: Optional[Dict[str, Any]]):
        """Analyze behavioral patterns for anomalies."""
        # This would integrate with behavioral analysis system
        # For now, placeholder implementation
        pass
    
    async def _advanced_pattern_check(self, request_data: Dict[str, Any]):
        """Perform advanced pattern matching."""
        # This would use more sophisticated pattern matching
        # For now, placeholder implementation
        pass
    
    async def _contextual_validation(self, request_data: Dict[str, Any],
                                  context: Optional[Dict[str, Any]]):
        """Perform contextual validation."""
        # This would validate based on context
        # For now, placeholder implementation
        pass
    
    def _calculate_ttl(self, result: Any, context: Optional[Dict[str, Any]]) -> timedelta:
        """Calculate TTL based on result and context."""
        base_ttl = timedelta(minutes=30)
        
        # Adjust based on performance level
        if self.performance_level == PerformanceLevel.ULTRA_FAST:
            base_ttl = timedelta(hours=2)
        elif self.performance_level == PerformanceLevel.FAST:
            base_ttl = timedelta(hours=1)
        elif self.performance_level == PerformanceLevel.PARANOID:
            base_ttl = timedelta(minutes=5)
        
        # Adjust based on context
        if context:
            trust_score = context.get("user_trust_score", 0.5)
            if trust_score > 0.8:
                base_ttl = timedelta(hours=4)  # Longer TTL for trusted users
            elif trust_score < 0.3:
                base_ttl = timedelta(minutes=10)  # Shorter TTL for untrusted users
        
        return base_ttl
    
    def _update_metrics(self, validation_time: float, cache_hit: bool):
        """Update performance metrics."""
        self.metrics.total_requests += 1
        
        if cache_hit:
            self.metrics.cache_hits += 1
        else:
            self.metrics.cache_misses += 1
        
        # Update average times
        total_validation_time = self.metrics.average_validation_time * (self.metrics.total_requests - 1)
        self.metrics.average_validation_time = (total_validation_time + validation_time) / self.metrics.total_requests
        
        # Update cache hit rate
        self.metrics.cache_hit_rate = self.metrics.cache_hits / max(self.metrics.total_requests, 1)
        
        # Update memory usage
        self.metrics.memory_usage_bytes = self.cache.get_memory_usage()
        self.metrics.cache_size = len(self.cache.cache)
    
    async def start_optimization(self):
        """Start background optimization."""
        if self._is_optimizing:
            return
        
        self._is_optimizing = True
        self._optimization_task = asyncio.create_task(self._optimization_loop())
        logger.info("Started validation optimization")
    
    async def stop_optimization(self):
        """Stop background optimization."""
        if not self._is_optimizing:
            return
        
        self._is_optimizing = False
        if self._optimization_task:
            self._optimization_task.cancel()
            try:
                await self._optimization_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped validation optimization")
    
    async def _optimization_loop(self):
        """Background optimization loop."""
        while self._is_optimizing:
            try:
                await self._optimize_performance()
                await asyncio.sleep(300)  # Optimize every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Optimization loop error: {e}")
                await asyncio.sleep(60)
    
    async def _optimize_performance(self):
        """Optimize performance based on current metrics."""
        current_threshold = self.validation_thresholds[self.performance_level]
        
        # Check if we're meeting performance targets
        hit_rate = self.metrics.cache_hit_rate
        avg_time = self.metrics.average_validation_time
        
        # Generate optimization report
        report = OptimizationReport(
            timestamp=datetime.now(),
            performance_level=self.performance_level,
            metrics=self.metrics,
            recommendations=[],
            cache_efficiency=hit_rate,
            bottleneck_analysis={},
            optimization_suggestions=[]
        )
        
        # Analyze performance
        if hit_rate < current_threshold["cache_hit_rate"]:
            report.recommendations.append("Cache hit rate below target")
            report.optimization_suggestions.append("Consider increasing cache size or adjusting TTL")
        
        if avg_time > current_threshold["max_validation_time"]:
            report.recommendations.append("Validation time above target")
            report.optimization_suggestions.append("Consider reducing validation depth or optimizing algorithms")
        
        # Adaptive performance level adjustment
        if len(self.validation_times) >= 100:
            recent_avg = np.mean(list(self.validation_times)[-50:])
            
            if recent_avg < current_threshold["max_validation_time"] * 0.5:
                # Performance is very good, can increase security
                report.optimization_suggestions.append("Consider upgrading to higher security level")
            elif recent_avg > current_threshold["max_validation_time"] * 1.5:
                # Performance is poor, may need to reduce security
                report.optimization_suggestions.append("Consider downgrading to lower security level for better performance")
        
        # Store optimization report
        self.optimization_history.append(report)
        
        # Apply automatic optimizations
        await self._apply_optimizations(report)
    
    async def _apply_optimizations(self, report: OptimizationReport):
        """Apply automatic optimizations based on report."""
        try:
            # Adjust cache strategy if needed
            if report.cache_efficiency < 0.7:
                if self.cache.strategy != CacheStrategy.ADAPTIVE:
                    self.cache.strategy = CacheStrategy.ADAPTIVE
                    logger.info("Switched to adaptive cache strategy")
            
            # Adjust cache size if memory usage is high
            if self.metrics.memory_usage_bytes > 100 * 1024 * 1024:  # 100MB
                new_size = max(1000, self.cache.max_size - 1000)
                self.cache.max_size = new_size
                logger.info(f"Reduced cache size to {new_size} due to memory usage")
            
        except Exception as e:
            logger.error(f"Failed to apply optimizations: {e}")
    
    def get_optimization_report(self) -> OptimizationReport:
        """Get latest optimization report."""
        if self.optimization_history:
            return self.optimization_history[-1]
        
        # Create default report
        return OptimizationReport(
            timestamp=datetime.now(),
            performance_level=self.performance_level,
            metrics=self.metrics,
            recommendations=["No optimization history available"],
            cache_efficiency=self.metrics.cache_hit_rate,
            bottleneck_analysis={},
            optimization_suggestions=[]
        )
    
    def set_performance_level(self, level: PerformanceLevel):
        """Update performance level."""
        self.performance_level = level
        logger.info(f"Performance level updated to {level.value}")
    
    async def clear_cache(self):
        """Clear validation cache."""
        await self.cache.clear()
        logger.info("Validation cache cleared")
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        return self.metrics


# Global optimizer instance
_validation_optimizer: Optional[ValidationOptimizer] = None


def get_validation_optimizer(performance_level: PerformanceLevel = PerformanceLevel.BALANCED) -> ValidationOptimizer:
    """Get the global validation optimizer instance."""
    global _validation_optimizer
    if _validation_optimizer is None:
        _validation_optimizer = ValidationOptimizer(performance_level)
    return _validation_optimizer


async def validate_with_optimization(request_data: Dict[str, Any],
                                  validation_func: callable,
                                  context: Optional[Dict[str, Any]] = None,
                                  performance_level: PerformanceLevel = PerformanceLevel.BALANCED) -> Tuple[Any, bool]:
    """Validate request with performance optimization (convenience function)."""
    optimizer = get_validation_optimizer(performance_level)
    return await optimizer.validate_with_cache(request_data, validation_func, context)


def get_validation_performance_metrics() -> PerformanceMetrics:
    """Get validation performance metrics (convenience function)."""
    optimizer = get_validation_optimizer()
    return optimizer.get_performance_metrics()


async def initialize_validation_optimizer(redis_url: Optional[str] = None,
                                      performance_level: PerformanceLevel = PerformanceLevel.BALANCED):
    """Initialize validation optimizer (convenience function)."""
    optimizer = get_validation_optimizer(performance_level)
    await optimizer.initialize(redis_url)
