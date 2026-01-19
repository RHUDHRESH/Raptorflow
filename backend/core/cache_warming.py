"""
Cache Warmer with ML-based Prediction of Access Patterns
Intelligently warms cache based on predicted access patterns
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
import pickle
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class WarmingStrategy(Enum):
    """Cache warming strategies."""
    
    HISTORICAL_BASED = "historical_based"
    PREDICTIVE_ML = "predictive_ml"
    HYBRID = "hybrid"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"


class AccessPattern(Enum):
    """Common access patterns."""
    
    TIME_BASED = "time_based"           # Peak hours, business hours
    SEQUENTIAL = "sequential"           # Sequential access patterns
    RANDOM = "random"                   # Random access patterns
    BURST = "burst"                    # Burst access patterns
    STEADY = "steady"                  # Steady access patterns
    SEASONAL = "seasonal"              # Seasonal patterns


@dataclass
class AccessRecord:
    """Record of cache access."""
    
    key: str
    timestamp: datetime
    access_type: str  # 'get', 'set', 'delete'
    entity_type: str
    entity_id: Optional[str]
    context: Dict[str, Any]
    response_time: float
    hit: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for ML processing."""
        return {
            'key': self.key,
            'timestamp': self.timestamp.timestamp(),
            'access_type': self.access_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'context': self.context,
            'response_time': self.response_time,
            'hit': self.hit,
            'hour': self.timestamp.hour,
            'day_of_week': self.timestamp.weekday(),
            'day_of_month': self.timestamp.day,
            'month': self.timestamp.month
        }


@dataclass
class WarmingPrediction:
    """Prediction for cache warming."""
    
    key: str
    probability: float
    predicted_access_time: datetime
    confidence: float
    pattern_type: AccessPattern
    warming_priority: int
    estimated_benefit: float
    ttl_suggestion: int


class AccessPatternAnalyzer:
    """Analyzes access patterns to predict future accesses."""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.access_history: deque = deque(maxlen=window_size)
        self.pattern_cache: Dict[str, AccessPattern] = {}
        
        # Pattern detection thresholds
        self.burst_threshold = 10  # accesses in 1 minute
        self.steady_threshold = 0.5  # accesses per minute average
        self.seasonal_threshold = 0.7  # correlation threshold
    
    def record_access(self, record: AccessRecord):
        """Record a cache access."""
        self.access_history.append(record)
        
        # Update pattern cache if needed
        if len(self.access_history) % 100 == 0:
            self._update_pattern_cache()
    
    def detect_pattern(self, key: str) -> AccessPattern:
        """Detect access pattern for a specific key."""
        if key in self.pattern_cache:
            return self.pattern_cache[key]
        
        # Get recent accesses for this key
        key_accesses = [r for r in self.access_history if r.key == key]
        
        if len(key_accesses) < 10:
            return AccessPattern.RANDOM
        
        # Analyze time intervals
        timestamps = [r.timestamp for r in key_accesses]
        intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                    for i in range(len(timestamps)-1)]
        
        # Calculate statistics
        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        # Check for burst pattern
        recent_accesses = [r for r in key_accesses 
                         if (datetime.now() - r.timestamp).total_seconds() < 300]
        if len(recent_accesses) >= self.burst_threshold:
            return AccessPattern.BURST
        
        # Check for steady pattern
        accesses_per_minute = len(key_accesses) / ((datetime.now() - timestamps[0]).total_seconds() / 60)
        if accesses_per_minute >= self.steady_threshold and std_interval < avg_interval * 0.5:
            return AccessPattern.STEADY
        
        # Check for time-based pattern
        hours = [r.timestamp.hour for r in key_accesses]
        hour_counts = defaultdict(int)
        for hour in hours:
            hour_counts[hour] += 1
        
        if len(hour_counts) < 8 and max(hour_counts.values()) > len(key_accesses) * 0.3:
            return AccessPattern.TIME_BASED
        
        # Check for sequential pattern
        key_parts = key.split(':')
        if len(key_parts) > 1 and key_parts[-1].isdigit():
            # Check if there are sequential keys
            base_key = ':'.join(key_parts[:-1])
            sequential_keys = [k for k in self.pattern_cache.keys() 
                           if k.startswith(base_key)]
            if len(sequential_keys) > 5:
                return AccessPattern.SEQUENTIAL
        
        # Default to random
        return AccessPattern.RANDOM
    
    def _update_pattern_cache(self):
        """Update pattern cache with recent data."""
        # Get unique keys from recent history
        recent_keys = set(r.key for r in self.access_history)
        
        for key in recent_keys:
            pattern = self.detect_pattern(key)
            self.pattern_cache[key] = pattern
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics about detected patterns."""
        pattern_counts = defaultdict(int)
        
        for pattern in self.pattern_cache.values():
            pattern_counts[pattern.value] += 1
        
        return {
            'total_patterns': len(self.pattern_cache),
            'pattern_distribution': dict(pattern_counts),
            'most_common_pattern': max(pattern_counts.items(), key=lambda x: x[1])[0] if pattern_counts else None
        }


class MLPredictor:
    """Machine learning predictor for cache access."""
    
    def __init__(self):
        self.model = None
        self.feature_columns = [
            'hour', 'day_of_week', 'day_of_month', 'month',
            'entity_type_encoded', 'access_frequency', 'recency_score'
        ]
        self.is_trained = False
        self.training_data: List[Dict[str, Any]] = []
        
        # Simple rule-based model for initial implementation
        self.rule_weights = {
            'time_based': {'hour_weight': 0.3, 'day_weight': 0.2},
            'frequency_based': {'recent_weight': 0.4, 'historical_weight': 0.3},
            'context_based': {'entity_weight': 0.2, 'user_weight': 0.1}
        }
    
    def add_training_data(self, records: List[AccessRecord]):
        """Add training data from access records."""
        for record in records:
            features = self._extract_features(record)
            label = 1 if record.hit else 0  # Predict cache hits
            
            self.training_data.append({
                'features': features,
                'label': label,
                'timestamp': record.timestamp
            })
        
        # Limit training data size
        if len(self.training_data) > 10000:
            self.training_data = self.training_data[-10000:]
    
    def train(self):
        """Train the ML model."""
        if len(self.training_data) < 100:
            logger.warning("Insufficient training data for ML model")
            return
        
        try:
            # Extract features and labels
            X = [data['features'] for data in self.training_data]
            y = [data['label'] for data in self.training_data]
            
            # For now, use simple statistical model
            # In production, this would use scikit-learn or similar
            self._train_simple_model(X, y)
            self.is_trained = True
            
            logger.info(f"ML model trained with {len(self.training_data)} samples")
            
        except Exception as e:
            logger.error(f"Failed to train ML model: {e}")
    
    def predict_access_probability(
        self,
        key: str,
        entity_type: str,
        context: Dict[str, Any],
        future_time: datetime
    ) -> float:
        """Predict probability of access at future time."""
        if not self.is_trained:
            return self._rule_based_prediction(key, entity_type, context, future_time)
        
        try:
            features = self._extract_features_for_prediction(
                key, entity_type, context, future_time
            )
            
            # Simple prediction based on trained weights
            probability = self._predict_with_simple_model(features)
            
            return max(0.0, min(1.0, probability))
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._rule_based_prediction(key, entity_type, context, future_time)
    
    def _extract_features(self, record: AccessRecord) -> List[float]:
        """Extract features from access record."""
        # Encode entity type
        entity_type_map = {'user': 1, 'campaign': 2, 'icp': 3, 'report': 4, 'agent': 5}
        entity_type_encoded = entity_type_map.get(record.entity_type, 0)
        
        # Calculate access frequency (last hour)
        recent_time = record.timestamp - timedelta(hours=1)
        recent_accesses = [r for r in self.training_data 
                         if r['timestamp'] > recent_time]
        access_frequency = len(recent_accesses)
        
        # Calculate recency score
        age_hours = (datetime.now() - record.timestamp).total_seconds() / 3600
        recency_score = 1.0 / (1.0 + age_hours)
        
        return [
            record.timestamp.hour,
            record.timestamp.weekday(),
            record.timestamp.day,
            record.timestamp.month,
            entity_type_encoded,
            access_frequency,
            recency_score
        ]
    
    def _extract_features_for_prediction(
        self,
        key: str,
        entity_type: str,
        context: Dict[str, Any],
        future_time: datetime
    ) -> List[float]:
        """Extract features for prediction."""
        entity_type_map = {'user': 1, 'campaign': 2, 'icp': 3, 'report': 4, 'agent': 5}
        entity_type_encoded = entity_type_map.get(entity_type, 0)
        
        # Get historical frequency for this key pattern
        key_pattern = ':'.join(key.split(':')[:-1]) if ':' in key else key
        historical_accesses = [d for d in self.training_data 
                             if key_pattern in str(d.get('features', []))]
        access_frequency = len(historical_accesses)
        
        # Calculate recency score
        recency_score = 1.0  # Future access has high recency
        
        return [
            future_time.hour,
            future_time.weekday(),
            future_time.day,
            future_time.month,
            entity_type_encoded,
            access_frequency,
            recency_score
        ]
    
    def _train_simple_model(self, X: List[List[float]], y: List[int]):
        """Train simple statistical model."""
        # Calculate feature weights based on correlation with labels
        if len(X) == 0 or len(y) == 0:
            return
        
        # Simple correlation-based weights
        feature_weights = []
        for i in range(len(X[0])):
            feature_values = [row[i] for row in X]
            correlation = np.corrcoef(feature_values, y)[0, 1] if len(set(feature_values)) > 1 else 0
            feature_weights.append(max(0, correlation))
        
        self.model = {'weights': feature_weights, 'bias': np.mean(y)}
    
    def _predict_with_simple_model(self, features: List[float]) -> float:
        """Predict with simple linear model."""
        if not self.model:
            return 0.5
        
        weights = self.model['weights']
        bias = self.model['bias']
        
        # Linear combination
        prediction = bias
        for i, (feature, weight) in enumerate(zip(features, weights)):
            if i < len(weight):
                prediction += feature * weight
        
        # Sigmoid activation
        return 1.0 / (1.0 + np.exp(-prediction))
    
    def _rule_based_prediction(
        self,
        key: str,
        entity_type: str,
        context: Dict[str, Any],
        future_time: datetime
    ) -> float:
        """Rule-based prediction when ML model is not available."""
        probability = 0.5  # Base probability
        
        # Time-based rules
        hour = future_time.hour
        if 9 <= hour <= 17:  # Business hours
            probability += 0.2
        elif 18 <= hour <= 22:  # Evening hours
            probability += 0.1
        
        # Entity type rules
        high_priority_entities = {'user', 'campaign', 'icp'}
        if entity_type in high_priority_entities:
            probability += 0.15
        
        # Context-based rules
        if context.get('user_id'):
            probability += 0.1
        if context.get('workspace_id'):
            probability += 0.1
        
        return max(0.0, min(1.0, probability))


class CacheWarmer:
    """Main cache warmer with ML-based prediction."""
    
    def __init__(
        self,
        strategy: WarmingStrategy = WarmingStrategy.HYBRID,
        warming_interval: int = 300,  # 5 minutes
        max_concurrent_warmings: int = 10
    ):
        self.strategy = strategy
        self.warming_interval = warming_interval
        self.max_concurrent_warmings = max_concurrent_warmings
        
        # Components
        self.pattern_analyzer = AccessPatternAnalyzer()
        self.ml_predictor = MLPredictor()
        
        # Warming state
        self.is_warming = False
        self.warming_queue: asyncio.Queue = asyncio.Queue()
        self.warming_tasks: Set[asyncio.Task] = set()
        self.warming_history: List[WarmingPrediction] = []
        
        # Performance tracking
        self.stats = {
            'total_warmings': 0,
            'successful_warmings': 0,
            'failed_warmings': 0,
            'average_warming_time': 0.0,
            'cache_hit_improvement': 0.0,
            'predictions_made': 0,
            'prediction_accuracy': 0.0
        }
        
        # Background tasks
        self._warming_task = None
        self._training_task = None
        
        # Data generators for warming
        self.data_generators: Dict[str, callable] = {}
    
    async def initialize(self):
        """Initialize the cache warmer."""
        # Start background tasks
        self._warming_task = asyncio.create_task(self._background_warming())
        self._training_task = asyncio.create_task(self._background_training())
        
        logger.info("Cache warmer initialized")
    
    def register_data_generator(self, entity_type: str, generator: callable):
        """Register data generator for entity type."""
        self.data_generators[entity_type] = generator
        logger.info(f"Registered data generator for {entity_type}")
    
    def record_access(self, record: AccessRecord):
        """Record cache access for pattern analysis."""
        self.pattern_analyzer.record_access(record)
        
        # Add to ML training data
        self.ml_predictor.add_training_data([record])
    
    async def predict_warming_candidates(
        self,
        time_horizon: timedelta = timedelta(hours=1)
    ) -> List[WarmingPrediction]:
        """Predict cache warming candidates."""
        candidates = []
        current_time = datetime.now()
        future_time = current_time + time_horizon
        
        # Get unique keys from access history
        unique_keys = set(r.key for r in self.pattern_analyzer.access_history)
        
        for key in unique_keys:
            try:
                # Get entity type from key
                key_parts = key.split(':')
                entity_type = key_parts[1] if len(key_parts) > 1 else 'unknown'
                
                # Get context for this key
                context = {}
                for record in self.pattern_analyzer.access_history:
                    if record.key == key:
                        context = record.context
                        break
                
                # Predict access probability
                probability = self.ml_predictor.predict_access_probability(
                    key, entity_type, context, future_time
                )
                
                if probability > 0.3:  # Threshold for warming
                    # Detect pattern
                    pattern = self.pattern_analyzer.detect_pattern(key)
                    
                    # Calculate warming priority
                    priority = self._calculate_warming_priority(
                        key, probability, pattern
                    )
                    
                    # Estimate benefit
                    benefit = self._estimate_warming_benefit(
                        key, probability, pattern
                    )
                    
                    # Suggest TTL
                    ttl_suggestion = self._suggest_ttl(pattern, probability)
                    
                    prediction = WarmingPrediction(
                        key=key,
                        probability=probability,
                        predicted_access_time=future_time,
                        confidence=min(probability * 1.2, 1.0),
                        pattern_type=pattern,
                        warming_priority=priority,
                        estimated_benefit=benefit,
                        ttl_suggestion=ttl_suggestion
                    )
                    
                    candidates.append(prediction)
                    
            except Exception as e:
                logger.error(f"Error predicting for key {key}: {e}")
        
        # Sort by priority
        candidates.sort(key=lambda x: x.warming_priority, reverse=True)
        
        # Limit to top candidates
        max_candidates = min(50, len(candidates))
        self.stats['predictions_made'] += max_candidates
        
        return candidates[:max_candidates]
    
    async def warm_cache(self, predictions: List[WarmingPrediction]):
        """Warm cache based on predictions."""
        if not predictions:
            return
        
        self.is_warming = True
        start_time = time.time()
        
        try:
            # Create warming tasks
            semaphore = asyncio.Semaphore(self.max_concurrent_warmings)
            
            async def warm_single_prediction(prediction: WarmingPrediction):
                async with semaphore:
                    return await self._warm_single_entry(prediction)
            
            # Execute warming tasks
            tasks = [warm_single_prediction(p) for p in predictions]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            successful = sum(1 for r in results if r is True)
            failed = sum(1 for r in results if r is False)
            
            self.stats['total_warmings'] += len(predictions)
            self.stats['successful_warmings'] += successful
            self.stats['failed_warmings'] += failed
            
            # Update warming time
            warming_time = time.time() - start_time
            current_avg = self.stats['average_warming_time']
            self.stats['average_warming_time'] = (
                (current_avg + warming_time) / 2
            )
            
            logger.info(f"Warmed {successful}/{len(predictions)} cache entries in {warming_time:.2f}s")
            
        finally:
            self.is_warming = False
    
    async def _warm_single_entry(self, prediction: WarmingPrediction) -> bool:
        """Warm a single cache entry."""
        try:
            # Get entity type from key
            key_parts = prediction.key.split(':')
            entity_type = key_parts[1] if len(key_parts) > 1 else 'unknown'
            
            # Generate data if generator is available
            if entity_type in self.data_generators:
                generator = self.data_generators[entity_type]
                data = await generator(prediction.key, prediction.pattern_type)
                
                if data:
                    # Store in cache
                    from .comprehensive_cache import get_comprehensive_cache
                    cache = await get_comprehensive_cache()
                    
                    success = await cache.set(
                        key=prediction.key,
                        value=data,
                        ttl=prediction.ttl_suggestion,
                        priority='HIGH' if prediction.warming_priority > 7 else 'NORMAL'
                    )
                    
                    return success
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to warm entry {prediction.key}: {e}")
            return False
    
    def _calculate_warming_priority(
        self,
        key: str,
        probability: float,
        pattern: AccessPattern
    ) -> int:
        """Calculate warming priority (1-10)."""
        priority = int(probability * 10)
        
        # Adjust based on pattern
        pattern_multipliers = {
            AccessPattern.TIME_BASED: 1.2,
            AccessPattern.BURST: 1.5,
            AccessPattern.STEADY: 1.3,
            AccessPattern.SEQUENTIAL: 1.1,
            AccessPattern.SEASONAL: 1.4,
            AccessPattern.RANDOM: 0.8
        }
        
        multiplier = pattern_multipliers.get(pattern, 1.0)
        priority = int(priority * multiplier)
        
        return max(1, min(10, priority))
    
    def _estimate_warming_benefit(
        self,
        key: str,
        probability: float,
        pattern: AccessPattern
    ) -> float:
        """Estimate benefit of warming this entry."""
        # Base benefit from probability
        benefit = probability * 10.0
        
        # Pattern-based adjustments
        pattern_benefits = {
            AccessPattern.TIME_BASED: 8.0,
            AccessPattern.BURST: 10.0,
            AccessPattern.STEADY: 7.0,
            AccessPattern.SEQUENTIAL: 6.0,
            AccessPattern.SEASONAL: 9.0,
            AccessPattern.RANDOM: 3.0
        }
        
        benefit += pattern_benefits.get(pattern, 5.0)
        
        # Historical performance adjustment
        historical_accesses = [r for r in self.pattern_analyzer.access_history if r.key == key]
        if historical_accesses:
            avg_response_time = np.mean([r.response_time for r in historical_accesses])
            benefit += avg_response_time * 2.0  # Faster response = higher benefit
        
        return benefit
    
    def _suggest_ttl(self, pattern: AccessPattern, probability: float) -> int:
        """Suggest TTL based on pattern and probability."""
        base_ttl = 3600  # 1 hour
        
        # Pattern-based TTL adjustments
        ttl_multipliers = {
            AccessPattern.TIME_BASED: 0.5,  # Shorter TTL for time-based
            AccessPattern.BURST: 0.3,        # Very short for burst
            AccessPattern.STEADY: 2.0,       # Longer for steady
            AccessPattern.SEQUENTIAL: 1.5,    # Medium-long for sequential
            AccessPattern.SEASONAL: 4.0,      # Long for seasonal
            AccessPattern.RANDOM: 0.8         # Short for random
        }
        
        multiplier = ttl_multipliers.get(pattern, 1.0)
        ttl = int(base_ttl * multiplier * probability)
        
        return max(300, min(86400, ttl))  # 5 min to 24 hours
    
    async def _background_warming(self):
        """Background warming task."""
        while True:
            try:
                await asyncio.sleep(self.warming_interval)
                
                if not self.is_warming:
                    # Predict warming candidates
                    predictions = await self.predict_warming_candidates()
                    
                    if predictions:
                        # Warm cache
                        await self.warm_cache(predictions)
                        
                        # Store predictions for analysis
                        self.warming_history.extend(predictions)
                        
                        # Limit history size
                        if len(self.warming_history) > 1000:
                            self.warming_history = self.warming_history[-1000:]
                
            except Exception as e:
                logger.error(f"Background warming error: {e}")
    
    async def _background_training(self):
        """Background ML model training."""
        while True:
            try:
                await asyncio.sleep(3600)  # Train every hour
                
                # Train ML model
                self.ml_predictor.train()
                
                # Clean old training data
                cutoff_time = datetime.now() - timedelta(days=7)
                self.ml_predictor.training_data = [
                    d for d in self.ml_predictor.training_data
                    if d['timestamp'] > cutoff_time
                ]
                
            except Exception as e:
                logger.error(f"Background training error: {e}")
    
    def get_warming_stats(self) -> Dict[str, Any]:
        """Get warming statistics."""
        pattern_stats = self.pattern_analyzer.get_pattern_statistics()
        
        return {
            'warming_stats': self.stats.copy(),
            'pattern_stats': pattern_stats,
            'is_warming': self.is_warming,
            'warming_queue_size': self.warming_queue.qsize(),
            'active_warming_tasks': len(self.warming_tasks),
            'ml_model_trained': self.ml_predictor.is_trained,
            'training_data_size': len(self.ml_predictor.training_data),
            'registered_generators': list(self.data_generators.keys())
        }
    
    async def shutdown(self):
        """Shutdown the cache warmer."""
        if self._warming_task:
            self._warming_task.cancel()
        
        if self._training_task:
            self._training_task.cancel()
        
        # Cancel warming tasks
        for task in self.warming_tasks:
            task.cancel()
        
        logger.info("Cache warmer shutdown")


# Global cache warmer instance
_cache_warmer: Optional[CacheWarmer] = None


async def get_cache_warmer() -> CacheWarmer:
    """Get the global cache warmer."""
    global _cache_warmer
    if _cache_warmer is None:
        _cache_warmer = CacheWarmer()
        await _cache_warmer.initialize()
    return _cache_warmer


# Convenience functions
async def record_cache_access(
    key: str,
    access_type: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    response_time: float = 0.0,
    hit: bool = False
):
    """Record cache access (convenience function)."""
    record = AccessRecord(
        key=key,
        timestamp=datetime.now(),
        access_type=access_type,
        entity_type=entity_type,
        entity_id=entity_id,
        context=context or {},
        response_time=response_time,
        hit=hit
    )
    
    warmer = await get_cache_warmer()
    warmer.record_access(record)


async def trigger_cache_warming():
    """Trigger cache warming (convenience function)."""
    warmer = await get_cache_warmer()
    predictions = await warmer.predict_warming_candidates()
    await warmer.warm_cache(predictions)
    return len(predictions)


def get_warming_statistics() -> Dict[str, Any]:
    """Get warming statistics (convenience function)."""
    if _cache_warmer:
        return _cache_warmer.get_warming_stats()
    return {"error": "Cache warmer not initialized"}
