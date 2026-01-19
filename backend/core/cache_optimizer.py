"""
Cache Optimizer with ML-Based Access Pattern Prediction and Optimization
Uses machine learning to optimize cache performance automatically
"""

import asyncio
import json
import logging
import time
import numpy as np
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import threading
import pickle

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Types of cache optimizations."""
    
    TTL_OPTIMIZATION = "ttl_optimization"
    SIZE_OPTIMIZATION = "size_optimization"
    EVICTION_POLICY = "eviction_policy"
    PREFETCH_STRATEGY = "prefetch_strategy"
    COMPRESSION_SETTINGS = "compression_settings"
    DISTRIBUTION_STRATEGY = "distribution_strategy"


class AccessPattern(Enum):
    """Access patterns for optimization."""
    
    SEQUENTIAL = "sequential"
    RANDOM = "random"
    TEMPORAL_LOCALITY = "temporal_locality"
    SPATIAL_LOCALITY = "spatial_locality"
    BURST = "burst"
    STEADY = "steady"
    PERIODIC = "periodic"


@dataclass
class AccessRecord:
    """Record of cache access for ML training."""
    
    key: str
    timestamp: datetime
    access_type: str  # get, set, delete
    response_time: float
    key_hash: str
    key_length: int
    hour_of_day: int
    day_of_week: int
    user_id: Optional[str]
    workspace_id: Optional[str]
    entity_type: str
    hit: bool
    
    def to_features(self) -> List[float]:
        """Convert to feature vector for ML."""
        return [
            self.key_length,
            self.hour_of_day / 24.0,
            self.day_of_week / 7.0,
            float(self.user_id is not None),
            float(self.workspace_id is not None),
            hash(self.entity_type) % 100 / 100.0,
            self.timestamp.timestamp() % 86400 / 86400.0,  # Time of day normalized
        ]


@dataclass
class OptimizationRecommendation:
    """Optimization recommendation."""
    
    optimization_type: OptimizationType
    target: str  # key, pattern, or global
    recommendation: Dict[str, Any]
    confidence: float
    expected_improvement: float
    reasoning: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class PatternDetector:
    """Detects access patterns in cache usage."""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.access_history: deque = deque(maxlen=window_size)
        self.pattern_cache: Dict[str, AccessPattern] = {}
        
        # Pattern detection thresholds
        self.sequential_threshold = 0.8
        self.temporal_threshold = 300  # 5 minutes
        self.burst_threshold = 10  # 10 accesses in 1 minute
    
    def add_access(self, record: AccessRecord):
        """Add access record for pattern detection."""
        self.access_history.append(record)
        
        # Update pattern cache periodically
        if len(self.access_history) % 100 == 0:
            self._update_patterns()
    
    def detect_pattern(self, key_prefix: str) -> AccessPattern:
        """Detect access pattern for key prefix."""
        if key_prefix in self.pattern_cache:
            return self.pattern_cache[key_prefix]
        
        # Get recent accesses for this key prefix
        recent_accesses = [
            r for r in self.access_history 
            if r.key.startswith(key_prefix)
        ]
        
        if len(recent_accesses) < 10:
            return AccessPattern.RANDOM
        
        # Analyze patterns
        pattern = self._analyze_access_pattern(recent_accesses)
        self.pattern_cache[key_prefix] = pattern
        
        return pattern
    
    def _analyze_access_pattern(self, accesses: List[AccessRecord]) -> AccessPattern:
        """Analyze access pattern from list of accesses."""
        if not accesses:
            return AccessPattern.RANDOM
        
        # Sort by timestamp
        accesses.sort(key=lambda x: x.timestamp)
        
        # Check for sequential pattern
        if self._is_sequential(accesses):
            return AccessPattern.SEQUENTIAL
        
        # Check for temporal locality
        if self._has_temporal_locality(accesses):
            return AccessPattern.TEMPORAL_LOCALITY
        
        # Check for burst pattern
        if self._has_burst_pattern(accesses):
            return AccessPattern.BURST
        
        # Check for steady pattern
        if self._has_steady_pattern(accesses):
            return AccessPattern.STEADY
        
        # Check for periodic pattern
        if self._has_periodic_pattern(accesses):
            return AccessPattern.PERIODIC
        
        return AccessPattern.RANDOM
    
    def _is_sequential(self, accesses: List[AccessRecord]) -> bool:
        """Check if accesses are sequential."""
        if len(accesses) < 5:
            return False
        
        # Extract numeric parts from keys
        numeric_parts = []
        for access in accesses:
            parts = access.key.split(':')
            if parts and parts[-1].isdigit():
                numeric_parts.append(int(parts[-1]))
        
        if len(numeric_parts) < 5:
            return False
        
        # Check if numbers are sequential
        for i in range(1, len(numeric_parts)):
            if numeric_parts[i] != numeric_parts[i-1] + 1:
                return False
        
        return True
    
    def _has_temporal_locality(self, accesses: List[AccessRecord]) -> bool:
        """Check if accesses show temporal locality."""
        if len(accesses) < 10:
            return False
        
        # Check if accesses are clustered in time
        time_diffs = []
        for i in range(1, len(accesses)):
            diff = (accesses[i].timestamp - accesses[i-1].timestamp).total_seconds()
            time_diffs.append(diff)
        
        # If most time differences are small, we have temporal locality
        small_diffs = sum(1 for diff in time_diffs if diff < self.temporal_threshold)
        return small_diffs / len(time_diffs) > self.sequential_threshold
    
    def _has_burst_pattern(self, accesses: List[AccessRecord]) -> bool:
        """Check if accesses show burst pattern."""
        # Count accesses in sliding windows
        for i in range(len(accesses) - 4):
            window_start = accesses[i].timestamp
            window_end = window_start + timedelta(minutes=1)
            
            burst_count = sum(1 for access in accesses[i:i+5] 
                           if window_start <= access.timestamp <= window_end)
            
            if burst_count >= self.burst_threshold:
                return True
        
        return False
    
    def _has_steady_pattern(self, accesses: List[AccessRecord]) -> bool:
        """Check if accesses show steady pattern."""
        if len(accesses) < 20:
            return False
        
        # Calculate access rate over time windows
        time_windows = []
        current_time = accesses[0].timestamp
        
        while current_time <= accesses[-1].timestamp:
            window_end = current_time + timedelta(minutes=5)
            window_accesses = [a for a in accesses 
                             if current_time <= a.timestamp < window_end]
            time_windows.append(len(window_accesses))
            current_time = window_end
        
        if len(time_windows) < 4:
            return False
        
        # Check if access rate is consistent
        avg_rate = np.mean(time_windows)
        variance = np.var(time_windows)
        
        return variance < (avg_rate * 0.2)  # Low variance indicates steady pattern
    
    def _has_periodic_pattern(self, accesses: List[AccessRecord]) -> bool:
        """Check if accesses show periodic pattern."""
        if len(accesses) < 20:
            return False
        
        # Look for repeating intervals
        intervals = []
        for i in range(1, len(accesses)):
            interval = (accesses[i].timestamp - accesses[i-1].timestamp).total_seconds()
            intervals.append(interval)
        
        # Check for common intervals
        interval_counts = defaultdict(int)
        for interval in intervals:
            # Round to nearest minute for pattern detection
            rounded = int(interval / 60) * 60
            interval_counts[rounded] += 1
        
        # If we have a dominant interval, it's periodic
        if interval_counts:
            most_common_interval = max(interval_counts.values())
            return most_common_interval > len(intervals) * 0.3
        
        return False
    
    def _update_patterns(self):
        """Update pattern cache for all key prefixes."""
        # Get unique key prefixes
        key_prefixes = set()
        for access in self.access_history:
            parts = access.key.split(':')
            if len(parts) > 1:
                key_prefixes.add(':'.join(parts[:-1]))
        
        # Update patterns for each prefix
        for prefix in key_prefixes:
            self.detect_pattern(prefix)


class MLOptimizer:
    """Machine learning-based cache optimizer."""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.training_data: List[AccessRecord] = []
        self.feature_history: List[List[float]] = []
        self.target_history: List[float] = []
        
        # Optimization models
        self.ttl_model = None
        self.size_model = None
        self.eviction_model = None
        
        self.is_trained = False
        self.last_training_time = None
        
        # Initialize models if sklearn is available
        if SKLEARN_AVAILABLE:
            self.ttl_model = RandomForestRegressor(n_estimators=50, random_state=42)
            self.size_model = RandomForestRegressor(n_estimators=50, random_state=42)
            self.eviction_model = RandomForestRegressor(n_estimators=50, random_state=42)
    
    def add_training_data(self, records: List[AccessRecord]):
        """Add training data for ML models."""
        self.training_data.extend(records)
        
        # Limit training data size
        if len(self.training_data) > 10000:
            self.training_data = self.training_data[-10000:]
        
        # Extract features and targets
        for record in records:
            features = record.to_features()
            self.feature_history.append(features)
            
            # Targets for different optimization tasks
            self.target_history.append([
                self._calculate_optimal_ttl(record),
                self._calculate_optimal_size(record),
                self._calculate_optimal_eviction_score(record)
            ])
    
    def train_models(self):
        """Train ML optimization models."""
        if not SKLEARN_AVAILABLE or len(self.feature_history) < 100:
            logger.warning("Insufficient data or sklearn not available for ML training")
            return
        
        try:
            # Prepare training data
            X = np.array(self.feature_history)
            y_ttl = np.array([t[0] for t in self.target_history])
            y_size = np.array([t[1] for t in self.target_history])
            y_eviction = np.array([t[2] for t in self.target_history])
            
            # Split data
            X_train, X_test, y_ttl_train, y_ttl_test = train_test_split(
                X, y_ttl, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train models
            self.ttl_model.fit(X_train_scaled, y_ttl_train)
            self.size_model.fit(X_train_scaled, y_size_train)
            self.eviction_model.fit(X_train_scaled, y_eviction_train)
            
            # Evaluate models
            ttl_score = self.ttl_model.score(X_test_scaled, y_ttl_test)
            size_score = self.size_model.score(X_test_scaled, y_size_train)
            eviction_score = self.eviction_model.score(X_test_scaled, y_eviction_train)
            
            self.is_trained = True
            self.last_training_time = datetime.now()
            
            logger.info(f"ML models trained - TTL: {ttl_score:.3f}, Size: {size_score:.3f}, Eviction: {eviction_score:.3f}")
            
        except Exception as e:
            logger.error(f"Failed to train ML models: {e}")
    
    def predict_optimal_ttl(self, record: AccessRecord) -> int:
        """Predict optimal TTL for cache entry."""
        if not self.is_trained or not SKLEARN_AVAILABLE:
            return self._calculate_optimal_ttl(record)
        
        try:
            features = np.array([record.to_features()])
            features_scaled = self.scaler.transform(features)
            
            predicted_ttl = self.ttl_model.predict(features_scaled)[0]
            
            # Clamp to reasonable range
            return max(60, min(86400, int(predicted_ttl)))  # 1 minute to 24 hours
            
        except Exception as e:
            logger.error(f"TTL prediction error: {e}")
            return self._calculate_optimal_ttl(record)
    
    def predict_optimal_size(self, record: AccessRecord) -> int:
        """Predict optimal cache size for key pattern."""
        if not self.is_trained or not SKLEARN_AVAILABLE:
            return self._calculate_optimal_size(record)
        
        try:
            features = np.array([record.to_features()])
            features_scaled = self.scaler.transform(features)
            
            predicted_size = self.size_model.predict(features_scaled)[0]
            
            # Clamp to reasonable range
            return max(1024, min(10 * 1024 * 1024, int(predicted_size)))  # 1KB to 10MB
            
        except Exception as e:
            logger.error(f"Size prediction error: {e}")
            return self._calculate_optimal_size(record)
    
    def predict_optimal_eviction_policy(self, record: AccessRecord) -> str:
        """Predict optimal eviction policy."""
        if not self.is_trained or not SKLEARN_AVAILABLE:
            return "score_based"
        
        try:
            features = np.array([record.to_features()])
            features_scaled = self.scaler.transform(features)
            
            eviction_score = self.eviction_model.predict(features_scaled)[0]
            
            # Map score to policy
            if eviction_score < 0.3:
                return "lru"
            elif eviction_score < 0.6:
                return "lfu"
            else:
                return "score_based"
                
        except Exception as e:
            logger.error(f"Eviction prediction error: {e}")
            return "score_based"
    
    def _calculate_optimal_ttl(self, record: AccessRecord) -> int:
        """Calculate optimal TTL using heuristics."""
        base_ttl = 3600  # 1 hour
        
        # Adjust based on access time
        if record.hour_of_day >= 9 and record.hour_of_day <= 17:  # Business hours
            base_ttl = int(base_ttl * 0.5)  # Shorter TTL during business hours
        
        # Adjust based on day of week
        if record.day_of_week >= 5:  # Weekend
            base_ttl = int(base_ttl * 2)  # Longer TTL on weekends
        
        # Adjust based on hit rate (if available)
        if hasattr(record, 'hit_rate') and record.hit_rate > 0.8:
            base_ttl = int(base_ttl * 1.5)  # Longer TTL for high hit rate
        
        return base_ttl
    
    def _calculate_optimal_size(self, record: AccessRecord) -> int:
        """Calculate optimal cache size using heuristics."""
        base_size = 1024 * 1024  # 1MB
        
        # Adjust based on key length
        if record.key_length > 50:
            base_size = int(base_size * 1.5)  # Larger keys need more space
        
        # Adjust based on entity type
        if record.entity_type in ['user', 'campaign']:
            base_size = int(base_size * 2)  # Important entities get more space
        
        return base_size
    
    def _calculate_optimal_eviction_score(self, record: AccessRecord) -> float:
        """Calculate optimal eviction policy score."""
        # Simple heuristic based on access pattern
        score = 0.5  # Default to middle
        
        if record.hit:
            score += 0.1  # Hits suggest current policy is working
        
        if record.response_time < 0.1:
            score += 0.1  # Fast responses suggest good caching
        
        return min(1.0, max(0.0, score))


class CacheOptimizer:
    """Main cache optimizer with ML-based predictions."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Components
        self.pattern_detector = PatternDetector(
            window_size=config.get('pattern_window_size', 1000)
        )
        self.ml_optimizer = MLOptimizer()
        
        # Optimization state
        self.optimization_history: List[OptimizationRecommendation] = []
        self.active_optimizations: Dict[str, OptimizationRecommendation] = {}
        
        # Configuration
        self.optimization_interval = config.get('optimization_interval', 3600)  # 1 hour
        self.auto_optimization_enabled = config.get('auto_optimization_enabled', True)
        self.min_confidence_threshold = config.get('min_confidence_threshold', 0.7)
        
        # Background tasks
        self._optimization_task = None
        self._training_task = None
        self._running = False
        
        # Performance tracking
        self.performance_metrics = {
            'optimizations_applied': 0,
            'performance_improvement': 0.0,
            'ml_accuracy': 0.0
        }
    
    async def initialize(self):
        """Initialize cache optimizer."""
        # Start background tasks
        self._running = True
        self._optimization_task = asyncio.create_task(self._background_optimization())
        self._training_task = asyncio.create_task(self._background_training())
        
        logger.info("Cache optimizer initialized")
    
    async def shutdown(self):
        """Shutdown cache optimizer."""
        self._running = False
        
        if self._optimization_task:
            self._optimization_task.cancel()
        
        if self._training_task:
            self._training_task.cancel()
        
        logger.info("Cache optimizer shutdown")
    
    def record_access(
        self,
        key: str,
        access_type: str,
        response_time: float,
        hit: bool,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None
    ):
        """Record cache access for optimization."""
        record = AccessRecord(
            key=key,
            timestamp=datetime.now(),
            access_type=access_type,
            response_time=response_time,
            key_hash=hash(key) % 1000,
            key_length=len(key),
            hour_of_day=datetime.now().hour,
            day_of_week=datetime.now().weekday(),
            user_id=user_id,
            workspace_id=workspace_id,
            entity_type=self._extract_entity_type(key),
            hit=hit
        )
        
        # Add to pattern detector and ML optimizer
        self.pattern_detector.add_access(record)
        self.ml_optimizer.add_training_data([record])
    
    async def get_optimization_recommendations(
        self,
        key_pattern: Optional[str] = None
    ) -> List[OptimizationRecommendation]:
        """Get optimization recommendations."""
        recommendations = []
        
        # TTL optimization
        ttl_rec = await self._analyze_ttl_optimization(key_pattern)
        if ttl_rec:
            recommendations.append(ttl_rec)
        
        # Size optimization
        size_rec = await self._analyze_size_optimization(key_pattern)
        if size_rec:
            recommendations.append(size_rec)
        
        # Eviction policy optimization
        eviction_rec = await self._analyze_eviction_optimization(key_pattern)
        if eviction_rec:
            recommendations.append(eviction_rec)
        
        # Prefetch strategy optimization
        prefetch_rec = await self._analyze_prefetch_optimization(key_pattern)
        if prefetch_rec:
            recommendations.append(prefetch_rec)
        
        # Sort by confidence and expected improvement
        recommendations.sort(
            key=lambda x: (x.confidence * x.expected_improvement),
            reverse=True
        )
        
        return recommendations
    
    async def apply_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Apply optimization recommendation."""
        try:
            success = False
            
            if recommendation.optimization_type == OptimizationType.TTL_OPTIMIZATION:
                success = await self._apply_ttl_optimization(recommendation)
            elif recommendation.optimization_type == OptimizationType.SIZE_OPTIMIZATION:
                success = await self._apply_size_optimization(recommendation)
            elif recommendation.optimization_type == OptimizationType.EVICTION_POLICY:
                success = await self._apply_eviction_optimization(recommendation)
            elif recommendation.optimization_type == OptimizationType.PREFETCH_STRATEGY:
                success = await self._apply_prefetch_optimization(recommendation)
            
            if success:
                self.performance_metrics['optimizations_applied'] += 1
                self.active_optimizations[recommendation.target] = recommendation
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to apply optimization: {e}")
            return False
    
    async def _analyze_ttl_optimization(
        self,
        key_pattern: Optional[str]
    ) -> Optional[OptimizationRecommendation]:
        """Analyze TTL optimization opportunities."""
        # Get recent access data for pattern
        if not key_pattern:
            return None
        
        pattern = self.pattern_detector.detect_pattern(key_pattern)
        
        # Generate recommendation based on pattern
        if pattern == AccessPattern.TEMPORAL_LOCALITY:
            # Temporal locality suggests longer TTL
            recommendation = OptimizationRecommendation(
                optimization_type=OptimizationType.TTL_OPTIMIZATION,
                target=key_pattern,
                recommendation={'ttl_multiplier': 2.0, 'reason': 'temporal_locality'},
                confidence=0.8,
                expected_improvement=0.15,
                reasoning="Access pattern shows temporal locality, increasing TTL will improve hit rate",
                timestamp=datetime.now()
            )
        elif pattern == AccessPattern.BURST:
            # Burst pattern suggests shorter TTL with prefetch
            recommendation = OptimizationRecommendation(
                optimization_type=OptimizationType.TTL_OPTIMIZATION,
                target=key_pattern,
                recommendation={'ttl_multiplier': 0.5, 'enable_prefetch': True},
                confidence=0.7,
                expected_improvement=0.10,
                reasoning="Burst pattern detected, shorter TTL with prefetch will optimize performance",
                timestamp=datetime.now()
            )
        else:
            return None
        
        return recommendation
    
    async def _analyze_size_optimization(
        self,
        key_pattern: Optional[str]
    ) -> Optional[OptimizationRecommendation]:
        """Analyze size optimization opportunities."""
        if not key_pattern:
            return None
        
        # Get access pattern
        pattern = self.pattern_detector.detect_pattern(key_pattern)
        
        # Analyze based on pattern
        if pattern == AccessPattern.SEQUENTIAL:
            recommendation = OptimizationRecommendation(
                optimization_type=OptimizationType.SIZE_OPTIMIZATION,
                target=key_pattern,
                recommendation={'size_multiplier': 1.5, 'reason': 'sequential_access'},
                confidence=0.6,
                expected_improvement=0.05,
                reasoning="Sequential access pattern benefits from larger cache allocation",
                timestamp=datetime.now()
            )
        else:
            return None
        
        return recommendation
    
    async def _analyze_eviction_optimization(
        self,
        key_pattern: Optional[str]
    ) -> Optional[OptimizationRecommendation]:
        """Analyze eviction policy optimization."""
        if not key_pattern:
            return None
        
        pattern = self.pattern_detector.detect_pattern(key_pattern)
        
        if pattern == AccessPattern.TEMPORAL_LOCALITY:
            recommendation = OptimizationRecommendation(
                optimization_type=OptimizationType.EVICTION_POLICY,
                target=key_pattern,
                recommendation={'policy': 'lru', 'reason': 'temporal_locality'},
                confidence=0.7,
                expected_improvement=0.12,
                reasoning="LRU eviction policy optimal for temporal locality patterns",
                timestamp=datetime.now()
            )
        elif pattern == AccessPattern.RANDOM:
            recommendation = OptimizationRecommendation(
                optimization_type=OptimizationType.EVICTION_POLICY,
                target=key_pattern,
                recommendation={'policy': 'lfu', 'reason': 'random_access'},
                confidence=0.6,
                expected_improvement=0.08,
                reasoning="LFU eviction policy better for random access patterns",
                timestamp=datetime.now()
            )
        else:
            return None
        
        return recommendation
    
    async def _analyze_prefetch_optimization(
        self,
        key_pattern: Optional[str]
    ) -> Optional[OptimizationRecommendation]:
        """Analyze prefetch optimization opportunities."""
        if not key_pattern:
            return None
        
        pattern = self.pattern_detector.detect_pattern(key_pattern)
        
        if pattern == AccessPattern.SEQUENTIAL:
            recommendation = OptimizationRecommendation(
                optimization_type=OptimizationType.PREFETCH_STRATEGY,
                target=key_pattern,
                recommendation={'prefetch_count': 3, 'strategy': 'sequential'},
                confidence=0.8,
                expected_improvement=0.20,
                reasoning="Sequential pattern detected, prefetch next keys will improve performance",
                timestamp=datetime.now()
            )
        else:
            return None
        
        return recommendation
    
    async def _apply_ttl_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Apply TTL optimization."""
        # This would integrate with the cache system
        # For now, just log the recommendation
        logger.info(f"Applying TTL optimization: {recommendation.recommendation}")
        return True
    
    async def _apply_size_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Apply size optimization."""
        logger.info(f"Applying size optimization: {recommendation.recommendation}")
        return True
    
    async def _apply_eviction_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Apply eviction policy optimization."""
        logger.info(f"Applying eviction optimization: {recommendation.recommendation}")
        return True
    
    async def _apply_prefetch_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Apply prefetch optimization."""
        logger.info(f"Applying prefetch optimization: {recommendation.recommendation}")
        return True
    
    def _extract_entity_type(self, key: str) -> str:
        """Extract entity type from cache key."""
        parts = key.split(':')
        if len(parts) > 1:
            return parts[1]
        return 'unknown'
    
    async def _background_optimization(self):
        """Background optimization task."""
        while self._running:
            try:
                await asyncio.sleep(self.optimization_interval)
                
                if self.auto_optimization_enabled:
                    # Generate optimization recommendations
                    recommendations = await self.get_optimization_recommendations()
                    
                    # Apply high-confidence recommendations
                    for rec in recommendations:
                        if rec.confidence >= self.min_confidence_threshold:
                            await self.apply_optimization(rec)
                
            except Exception as e:
                logger.error(f"Background optimization error: {e}")
                await asyncio.sleep(self.optimization_interval)
    
    async def _background_training(self):
        """Background ML training task."""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Train every hour
                
                # Train ML models
                self.ml_optimizer.train_models()
                
            except Exception as e:
                logger.error(f"Background training error: {e}")
                await asyncio.sleep(3600)
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics."""
        return {
            'performance_metrics': self.performance_metrics.copy(),
            'active_optimizations': len(self.active_optimizations),
            'optimization_history_size': len(self.optimization_history),
            'ml_model_trained': self.ml_optimizer.is_trained,
            'last_training_time': self.ml_optimizer.last_training_time.isoformat() if self.ml_optimizer.last_training_time else None,
            'auto_optimization_enabled': self.auto_optimization_enabled,
            'optimization_interval': self.optimization_interval
        }


# Global cache optimizer instance
_cache_optimizer: Optional[CacheOptimizer] = None


async def get_cache_optimizer() -> CacheOptimizer:
    """Get the global cache optimizer."""
    global _cache_optimizer
    if _cache_optimizer is None:
        # Default configuration
        config = {
            'optimization_interval': 3600,  # 1 hour
            'auto_optimization_enabled': True,
            'min_confidence_threshold': 0.7,
            'pattern_window_size': 1000
        }
        _cache_optimizer = CacheOptimizer(config)
        await _cache_optimizer.initialize()
    return _cache_optimizer


# Convenience functions
async def record_cache_access(
    key: str,
    access_type: str,
    response_time: float,
    hit: bool,
    user_id: Optional[str] = None,
    workspace_id: Optional[str] = None
):
    """Record cache access (convenience function)."""
    optimizer = await get_cache_optimizer()
    optimizer.record_access(key, access_type, response_time, hit, user_id, workspace_id)


async def get_optimization_recommendations(key_pattern: Optional[str] = None) -> List[OptimizationRecommendation]:
    """Get optimization recommendations (convenience function)."""
    optimizer = await get_cache_optimizer()
    return await optimizer.get_optimization_recommendations(key_pattern)


def get_optimization_statistics() -> Dict[str, Any]:
    """Get optimization statistics (convenience function)."""
    if _cache_optimizer:
        return _cache_optimizer.get_optimization_stats()
    return {"error": "Cache optimizer not initialized"}
