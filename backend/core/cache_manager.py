"""
Unified Cache Management Interface
Provides a single interface to access all cache components
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from datetime import datetime

# Import all cache components
from comprehensive_cache import (
    get_comprehensive_cache,
    ComprehensiveCacheManager,
    CacheEntryPriority,
    CacheLevel,
)
from cache_key_generator import (
    get_cache_key_generator,
    CacheKeyGenerator,
    KeyScope,
    KeyGenerationStrategy,
)
from cache_warming import get_cache_warmer, CacheWarmer, WarmingStrategy
from cache_invalidation import (
    get_invalidation_manager,
    CacheInvalidationManager,
    InvalidationType,
    InvalidationScope,
)
from cache_compression import (
    get_compression_manager,
    CacheCompressionManager,
    CompressionAlgorithm,
    SerializationFormat,
)
from cache_analytics import get_cache_analytics, CacheAnalytics, TimeWindow, MetricType
from cache_health import get_health_monitor, CacheHealthMonitor, HealthStatus
from cache_distributed import (
    get_distributed_cache,
    DistributedCacheManager,
    ConsistencyLevel,
)
from cache_backup import get_backup_manager, CacheBackupManager, BackupType
from cache_optimizer import get_cache_optimizer, CacheOptimizer, OptimizationType
from cache_error_handler import get_error_handler, CacheErrorHandler

logger = logging.getLogger(__name__)


class UnifiedCacheManager:
    """Unified interface for all cache management operations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Cache components will be initialized lazily
        self._comprehensive_cache = None
        self._key_generator = None
        self._warmer = None
        self._invalidation_manager = None
        self._compression_manager = None
        self._analytics = None
        self._health_monitor = None
        self._distributed_cache = None
        self._backup_manager = None
        self._optimizer = None
        self._error_handler = None

        self._initialized = False

    async def initialize(self):
        """Initialize all cache components."""
        if self._initialized:
            return

        try:
            logger.info("Initializing unified cache manager...")

            # Initialize all components
            self._comprehensive_cache = await get_comprehensive_cache()
            self._key_generator = get_cache_key_generator()
            self._warmer = await get_cache_warmer()
            self._invalidation_manager = await get_invalidation_manager()
            self._compression_manager = get_compression_manager()
            self._analytics = await get_cache_analytics()
            self._health_monitor = await get_health_monitor()
            self._distributed_cache = await get_distributed_cache()
            self._backup_manager = await get_backup_manager()
            self._optimizer = await get_cache_optimizer()
            self._error_handler = await get_error_handler()

            self._initialized = True
            logger.info("Unified cache manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize unified cache manager: {e}")
            raise

    async def shutdown(self):
        """Shutdown all cache components."""
        if not self._initialized:
            return

        try:
            logger.info("Shutting down unified cache manager...")

            # Shutdown all components
            if self._comprehensive_cache:
                await self._comprehensive_cache.shutdown()
            if self._warmer:
                await self._warmer.shutdown()
            if self._analytics:
                await self._analytics.shutdown()
            if self._health_monitor:
                await self._health_monitor.shutdown()
            if self._distributed_cache:
                await self._distributed_cache.shutdown()
            if self._backup_manager:
                await self._backup_manager.shutdown()

            self._initialized = False
            logger.info("Unified cache manager shutdown successfully")

        except Exception as e:
            logger.error(f"Failed to shutdown unified cache manager: {e}")

    # Basic cache operations
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._initialized:
            await self.initialize()

        try:
            # Record access for analytics and optimization
            start_time = asyncio.get_event_loop().time()

            # Try to get from cache
            value = await self._comprehensive_cache.get(key)

            # Record metrics
            response_time = asyncio.get_event_loop().time() - start_time
            hit = value is not None

            await self._analytics.record_cache_hit(key, response_time, hit=hit)
            await self._optimizer.record_cache_access(key, "get", response_time, hit)

            return value

        except Exception as e:
            await self._error_handler.handle_error(e, "get", "comprehensive_cache", key)
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        priority: CacheEntryPriority = CacheEntryPriority.NORMAL,
        tags: Optional[Set[str]] = None,
    ) -> bool:
        """Set value in cache."""
        if not self._initialized:
            await self.initialize()

        try:
            # Compress value if beneficial
            compression_result = self._compression_manager.compress(value)
            compressed_value = compression_result.data

            # Set in cache
            success = await self._comprehensive_cache.set(
                key=key, value=compressed_value, ttl=ttl, priority=priority, tags=tags
            )

            # Record analytics
            await self._analytics.record_cache_set(
                key, len(str(value).encode()), compression_result.compression_ratio
            )

            return success

        except Exception as e:
            await self._error_handler.handle_error(e, "set", "comprehensive_cache", key)
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._initialized:
            await self.initialize()

        try:
            success = await self._comprehensive_cache.delete(key)
            return success

        except Exception as e:
            await self._error_handler.handle_error(
                e, "delete", "comprehensive_cache", key
            )
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate keys matching pattern."""
        if not self._initialized:
            await self.initialize()

        try:
            count = await self._comprehensive_cache.invalidate_pattern(pattern)
            return count

        except Exception as e:
            await self._error_handler.handle_error(
                e, "invalidate_pattern", "comprehensive_cache", pattern
            )
            return 0

    # Advanced cache operations
    async def generate_key(
        self,
        entity_type: str,
        entity_id: Optional[str] = None,
        action: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        scope: KeyScope = KeyScope.GLOBAL,
        strategy: Optional[KeyGenerationStrategy] = None,
    ) -> str:
        """Generate cache key with advanced strategies."""
        if not self._initialized:
            await self.initialize()

        return self._key_generator.generate_key(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            parameters=parameters,
            scope=scope,
            strategy=strategy,
        )

    async def warm_cache(self, entity_types: Optional[List[str]] = None) -> int:
        """Warm cache for specified entity types."""
        if not self._initialized:
            await self.initialize()

        try:
            # Get warming predictions
            predictions = await self._warmer.predict_warming_candidates()

            # Filter by entity types if specified
            if entity_types:
                predictions = [
                    p
                    for p in predictions
                    if any(entity_type in p.key for entity_type in entity_types)
                ]

            # Execute warming
            await self._warmer.warm_cache(predictions)

            return len(predictions)

        except Exception as e:
            await self._error_handler.handle_error(e, "warm_cache", "cache_warmer")
            return 0

    async def create_backup(
        self,
        backup_type: BackupType = BackupType.FULL,
        description: str = "Manual backup",
    ) -> str:
        """Create cache backup."""
        if not self._initialized:
            await self.initialize()

        try:
            backup_id = await self._backup_manager.create_backup(
                backup_type=backup_type, description=description
            )
            return backup_id

        except Exception as e:
            await self._error_handler.handle_error(e, "create_backup", "cache_backup")
            raise

    async def restore_backup(self, backup_id: str) -> bool:
        """Restore cache from backup."""
        if not self._initialized:
            await self.initialize()

        try:
            success = await self._backup_manager.restore_backup(backup_id)
            return success

        except Exception as e:
            await self._error_handler.handle_error(e, "restore_backup", "cache_backup")
            return False

    # Analytics and monitoring
    async def get_analytics_dashboard(
        self, time_window: TimeWindow = TimeWindow.HOURLY
    ) -> Dict[str, Any]:
        """Get comprehensive analytics dashboard."""
        if not self._initialized:
            await self.initialize()

        return await self._analytics.get_analytics_dashboard(time_window)

    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        if not self._initialized:
            await self.initialize()

        return await self._health_monitor.get_health_summary()

    async def get_optimization_recommendations(
        self, key_pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get optimization recommendations."""
        if not self._initialized:
            await self.initialize()

        recommendations = await self._optimizer.get_optimization_recommendations(
            key_pattern
        )
        return [rec.to_dict() for rec in recommendations]

    async def apply_optimization(self, recommendation: Dict[str, Any]) -> bool:
        """Apply optimization recommendation."""
        if not self._initialized:
            await self.initialize()

        try:
            # Convert dict back to recommendation object
            from cache_optimizer import OptimizationRecommendation

            # This is a simplified conversion
            rec = OptimizationRecommendation(
                optimization_type=recommendation.get("optimization_type"),
                target=recommendation.get("target"),
                recommendation=recommendation.get("recommendation"),
                confidence=recommendation.get("confidence", 0.0),
                expected_improvement=recommendation.get("expected_improvement", 0.0),
                reasoning=recommendation.get("reasoning", ""),
                timestamp=datetime.now(),
            )

            success = await self._optimizer.apply_optimization(rec)
            return success

        except Exception as e:
            await self._error_handler.handle_error(
                e, "apply_optimization", "cache_optimizer"
            )
            return False

    # Configuration and management
    async def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all components."""
        if not self._initialized:
            await self.initialize()

        try:
            stats = {
                "cache_stats": self._comprehensive_cache.get_comprehensive_stats(),
                "key_generation_stats": self._key_generator.get_generation_stats(),
                "warming_stats": self._warmer.get_warming_statistics(),
                "invalidation_stats": self._invalidation_manager.get_invalidation_statistics(),
                "compression_stats": self._compression_manager.get_compression_statistics(),
                "analytics_stats": await self._analytics.get_analytics_dashboard(),
                "health_stats": await self._health_monitor.get_health_summary(),
                "distributed_stats": self._distributed_cache.get_distributed_statistics(),
                "backup_stats": self._backup_manager.get_backup_statistics(),
                "optimization_stats": self._optimizer.get_optimization_statistics(),
                "error_stats": self._error_handler.get_error_statistics(),
                "timestamp": datetime.now().isoformat(),
                "initialized": self._initialized,
            }

            return stats

        except Exception as e:
            await self._error_handler.handle_error(
                e, "get_comprehensive_stats", "unified_manager"
            )
            return {"error": str(e)}

    async def configure_component(self, component: str, config: Dict[str, Any]):
        """Configure specific cache component."""
        if not self._initialized:
            await self.initialize()

        try:
            if component == "compression":
                # Update compression settings
                current_config = self._compression_manager.config
                current_config.update(config)
                logger.info(f"Updated compression configuration: {config}")

            elif component == "analytics":
                # Update analytics settings
                logger.info(f"Updated analytics configuration: {config}")

            elif component == "health":
                # Update health monitoring settings
                logger.info(f"Updated health monitoring configuration: {config}")

            else:
                logger.warning(f"Unknown component for configuration: {component}")

        except Exception as e:
            await self._error_handler.handle_error(
                e, "configure_component", "unified_manager"
            )

    # Distributed cache operations
    async def distributed_get(
        self, key: str, consistency: Optional[ConsistencyLevel] = None
    ) -> Optional[Any]:
        """Get value from distributed cache."""
        if not self._initialized:
            await self.initialize()

        return await self._distributed_cache.get(key, consistency)

    async def distributed_set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        consistency: Optional[ConsistencyLevel] = None,
    ) -> bool:
        """Set value in distributed cache."""
        if not self._initialized:
            await self.initialize()

        return await self._distributed_cache.set(key, value, ttl, consistency)

    # Utility methods
    def is_initialized(self) -> bool:
        """Check if cache manager is initialized."""
        return self._initialized

    async def wait_for_initialization(self, timeout: float = 30.0):
        """Wait for initialization to complete."""
        if self._initialized:
            return

        start_time = asyncio.get_event_loop().time()

        while not self._initialized:
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError("Cache manager initialization timeout")

            await asyncio.sleep(0.1)


# Global unified cache manager instance
_unified_cache_manager: Optional[UnifiedCacheManager] = None


async def get_unified_cache_manager() -> UnifiedCacheManager:
    """Get the global unified cache manager."""
    global _unified_cache_manager
    if _unified_cache_manager is None:
        _unified_cache_manager = UnifiedCacheManager()
        await _unified_cache_manager.initialize()
    return _unified_cache_manager


# Convenience functions for common operations
async def cache_get(key: str) -> Optional[Any]:
    """Get value from cache (convenience function)."""
    manager = await get_unified_cache_manager()
    return await manager.get(key)


async def cache_set(
    key: str,
    value: Any,
    ttl: Optional[int] = None,
    priority: CacheEntryPriority = CacheEntryPriority.NORMAL,
) -> bool:
    """Set value in cache (convenience function)."""
    manager = await get_unified_cache_manager()
    return await manager.set(key, value, ttl, priority)


async def cache_delete(key: str) -> bool:
    """Delete key from cache (convenience function)."""
    manager = await get_unified_cache_manager()
    return await manager.delete(key)


async def cache_invalidate_pattern(pattern: str) -> int:
    """Invalidate keys matching pattern (convenience function)."""
    manager = await get_unified_cache_manager()
    return await manager.invalidate_pattern(pattern)


async def get_cache_statistics() -> Dict[str, Any]:
    """Get comprehensive cache statistics (convenience function)."""
    manager = await get_unified_cache_manager()
    return await manager.get_comprehensive_stats()


async def warm_cache(entity_types: Optional[List[str]] = None) -> int:
    """Warm cache (convenience function)."""
    manager = await get_unified_cache_manager()
    return await manager.warm_cache(entity_types)


async def create_cache_backup(
    backup_type: BackupType = BackupType.FULL, description: str = "Manual backup"
) -> str:
    """Create cache backup (convenience function)."""
    manager = await get_unified_cache_manager()
    return await manager.create_backup(backup_type, description)


async def restore_cache_backup(backup_id: str) -> bool:
    """Restore cache backup (convenience function)."""
    manager = await get_unified_cache_manager()
    return await manager.restore_backup(backup_id)


async def get_cache_analytics(
    time_window: TimeWindow = TimeWindow.HOURLY,
) -> Dict[str, Any]:
    """Get cache analytics (convenience function)."""
    manager = await get_unified_cache_manager()
    return await manager.get_analytics_dashboard(time_window)


async def get_cache_health() -> Dict[str, Any]:
    """Get cache health status (convenience function)."""
    manager = await get_unified_cache_manager()
    return await manager.get_health_status()
