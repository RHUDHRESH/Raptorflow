"""
Cache Invalidation Manager with Event-Driven and TTL-Based Eviction
Provides intelligent cache invalidation strategies
"""

import asyncio
import json
import logging
import threading
import time
import weakref
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

logger = logging.getLogger(__name__)


class InvalidationType(Enum):
    """Types of cache invalidation."""

    TTL_EXPIRY = "ttl_expiry"
    EVENT_DRIVEN = "event_driven"
    MANUAL = "manual"
    SIZE_BASED = "size_based"
    DEPENDENCY = "dependency"
    VERSION_MISMATCH = "version_mismatch"
    CONSISTENCY_CHECK = "consistency_check"


class InvalidationScope(Enum):
    """Scope of cache invalidation."""

    SINGLE_KEY = "single_key"
    PATTERN = "pattern"
    ENTITY_TYPE = "entity_type"
    USER_SCOPE = "user_scope"
    WORKSPACE_SCOPE = "workspace_scope"
    GLOBAL = "global"
    DEPENDENCY_GRAPH = "dependency_graph"


class InvalidationPriority(Enum):
    """Priority of invalidation operations."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


@dataclass
class InvalidationEvent:
    """Represents a cache invalidation event."""

    id: str
    type: InvalidationType
    scope: InvalidationScope
    target: str  # Key, pattern, or entity identifier
    reason: str
    timestamp: datetime
    priority: InvalidationPriority
    metadata: Dict[str, Any]
    callback: Optional[Callable] = None

    def __post_init__(self):
        if self.id is None:
            self.id = f"inv_{int(time.time() * 1000)}_{hash(self.target)}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.type.value,
            "scope": self.scope.value,
            "target": self.target,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "metadata": self.metadata,
        }


@dataclass
class DependencyRule:
    """Dependency rule for cache invalidation."""

    source_key_pattern: str
    dependent_key_pattern: str
    invalidation_type: InvalidationType
    cascade: bool = True
    delay_seconds: int = 0
    conditions: Dict[str, Any] = None

    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}

    def matches(self, source_key: str) -> bool:
        """Check if source key matches this rule."""
        import re

        return bool(re.match(self.source_key_pattern, source_key))

    def get_dependent_keys(self, source_key: str) -> List[str]:
        """Get dependent keys based on the rule."""
        import re

        # Extract variables from source key
        source_match = re.match(self.source_key_pattern, source_key)
        if not source_match:
            return []

        # Generate dependent keys using variables
        try:
            dependent_key = re.sub(
                self.source_key_pattern, self.dependent_key_pattern, source_key
            )
            return [dependent_key]
        except Exception:
            return []


class TTLManager:
    """Manages TTL-based cache expiration."""

    def __init__(self, cleanup_interval: int = 60):
        self.cleanup_interval = cleanup_interval
        self.ttl_store: Dict[str, datetime] = {}
        self.expiry_queue: List[Tuple[datetime, str]] = []
        self._lock = threading.RLock()

        # Background cleanup task
        self._cleanup_task = None
        self._running = False

    async def start(self):
        """Start the TTL manager."""
        if self._running:
            return

        self._running = True
        self._cleanup_task = asyncio.create_task(self._background_cleanup())
        logger.info("TTL manager started")

    async def stop(self):
        """Stop the TTL manager."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
        logger.info("TTL manager stopped")

    def set_ttl(self, key: str, ttl_seconds: int):
        """Set TTL for a key."""
        expiry_time = datetime.now() + timedelta(seconds=ttl_seconds)

        with self._lock:
            self.ttl_store[key] = expiry_time

            # Add to expiry queue (sorted by expiry time)
            self.expiry_queue.append((expiry_time, key))
            self.expiry_queue.sort(key=lambda x: x[0])

    def remove_ttl(self, key: str):
        """Remove TTL for a key."""
        with self._lock:
            self.ttl_store.pop(key, None)
            self.expiry_queue = [(t, k) for t, k in self.expiry_queue if k != key]

    def get_ttl(self, key: str) -> Optional[datetime]:
        """Get TTL for a key."""
        with self._lock:
            return self.ttl_store.get(key)

    def get_expired_keys(self) -> List[str]:
        """Get all expired keys."""
        current_time = datetime.now()
        expired_keys = []

        with self._lock:
            # Find expired keys from queue
            while self.expiry_queue and self.expiry_queue[0][0] <= current_time:
                expiry_time, key = self.expiry_queue.pop(0)

                # Double-check in store
                if key in self.ttl_store and self.ttl_store[key] <= current_time:
                    expired_keys.append(key)
                    del self.ttl_store[key]

        return expired_keys

    async def _background_cleanup(self):
        """Background cleanup of expired keys."""
        while self._running:
            try:
                expired_keys = self.get_expired_keys()

                if expired_keys:
                    # Trigger invalidation events for expired keys
                    from comprehensive_cache import get_comprehensive_cache

                    cache = await get_comprehensive_cache()

                    for key in expired_keys:
                        await cache.delete(key)
                        logger.debug(f"Expired key: {key}")

                await asyncio.sleep(self.cleanup_interval)

            except Exception as e:
                logger.error(f"TTL cleanup error: {e}")
                await asyncio.sleep(self.cleanup_interval)


class EventDrivenInvalidator:
    """Handles event-driven cache invalidation."""

    def __init__(self):
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.processing_task = None
        self._running = False

        # Event statistics
        self.event_stats = {
            "total_events": 0,
            "processed_events": 0,
            "failed_events": 0,
            "event_types": defaultdict(int),
        }

    async def start(self):
        """Start the event-driven invalidator."""
        if self._running:
            return

        self._running = True
        self.processing_task = asyncio.create_task(self._process_events())
        logger.info("Event-driven invalidator started")

    async def stop(self):
        """Stop the event-driven invalidator."""
        self._running = False
        if self.processing_task:
            self.processing_task.cancel()
        logger.info("Event-driven invalidator stopped")

    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to specific event type."""
        self.event_handlers[event_type].append(handler)
        logger.debug(f"Subscribed handler for event type: {event_type}")

    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from specific event type."""
        if handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            logger.debug(f"Unsubscribed handler for event type: {event_type}")

    async def emit_event(self, event: InvalidationEvent):
        """Emit an invalidation event."""
        try:
            await self.event_queue.put(event)
            self.event_stats["total_events"] += 1
            self.event_stats["event_types"][event.type.value] += 1
        except Exception as e:
            logger.error(f"Failed to emit event: {e}")
            self.event_stats["failed_events"] += 1

    async def _process_events(self):
        """Process events from the queue."""
        while self._running:
            try:
                # Get event with timeout
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)

                # Process event
                await self._handle_event(event)
                self.event_stats["processed_events"] += 1

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Event processing error: {e}")
                self.event_stats["failed_events"] += 1

    async def _handle_event(self, event: InvalidationEvent):
        """Handle a single invalidation event."""
        handlers = self.event_handlers.get(event.type.value, [])

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Event handler error: {e}")

        # Execute callback if provided
        if event.callback:
            try:
                if asyncio.iscoroutinefunction(event.callback):
                    await event.callback(event)
                else:
                    event.callback(event)
            except Exception as e:
                logger.error(f"Event callback error: {e}")

    def get_event_stats(self) -> Dict[str, Any]:
        """Get event processing statistics."""
        return {
            "event_stats": self.event_stats.copy(),
            "queue_size": self.event_queue.qsize(),
            "subscribed_handlers": {
                event_type: len(handlers)
                for event_type, handlers in self.event_handlers.items()
            },
        }


class DependencyManager:
    """Manages cache dependency relationships."""

    def __init__(self):
        self.dependency_rules: List[DependencyRule] = []
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)

    def add_dependency_rule(self, rule: DependencyRule):
        """Add a dependency rule."""
        self.dependency_rules.append(rule)
        logger.debug(
            f"Added dependency rule: {rule.source_key_pattern} -> {rule.dependent_key_pattern}"
        )

    def remove_dependency_rule(self, rule: DependencyRule):
        """Remove a dependency rule."""
        if rule in self.dependency_rules:
            self.dependency_rules.remove(rule)
            logger.debug(
                f"Removed dependency rule: {rule.source_key_pattern} -> {rule.dependent_key_pattern}"
            )

    def find_dependent_keys(self, source_key: str) -> List[str]:
        """Find all dependent keys for a source key."""
        dependent_keys = []

        for rule in self.dependency_rules:
            if rule.matches(source_key):
                keys = rule.get_dependent_keys(source_key)
                dependent_keys.extend(keys)

        return list(set(dependent_keys))  # Remove duplicates

    def build_dependency_graph(self, keys: List[str]):
        """Build dependency graph for given keys."""
        self.dependency_graph.clear()
        self.reverse_graph.clear()

        for key in keys:
            dependents = self.find_dependent_keys(key)
            self.dependency_graph[key].update(dependents)

            for dependent in dependents:
                self.reverse_graph[dependent].add(key)

    def get_invalidation_order(self, source_key: str) -> List[str]:
        """Get topological order for dependency invalidation."""
        # Build graph for this source key
        all_keys = {source_key}
        queue = [source_key]

        while queue:
            current = queue.pop(0)
            dependents = self.find_dependent_keys(current)

            for dependent in dependents:
                if dependent not in all_keys:
                    all_keys.add(dependent)
                    queue.append(dependent)

        # Build graph
        self.build_dependency_graph(list(all_keys))

        # Topological sort
        visited = set()
        order = []

        def visit(key):
            if key in visited:
                return

            visited.add(key)

            # Visit dependents first
            for dependent in self.dependency_graph.get(key, set()):
                visit(dependent)

            order.append(key)

        visit(source_key)
        return order


class CacheInvalidationManager:
    """Main cache invalidation manager."""

    def __init__(
        self, ttl_cleanup_interval: int = 60, max_concurrent_invalidations: int = 20
    ):
        self.max_concurrent_invalidations = max_concurrent_invalidations

        # Components
        self.ttl_manager = TTLManager(ttl_cleanup_interval)
        self.event_invalidator = EventDrivenInvalidator()
        self.dependency_manager = DependencyManager()

        # Invalidation state
        self.invalidation_queue: asyncio.Queue = asyncio.Queue()
        self.active_invalidations: Set[str] = set()
        self.invalidation_history: deque = deque(maxlen=1000)

        # Performance tracking
        self.stats = {
            "total_invalidations": 0,
            "successful_invalidations": 0,
            "failed_invalidations": 0,
            "average_invalidation_time": 0.0,
            "invalidation_by_type": defaultdict(int),
            "invalidation_by_scope": defaultdict(int),
        }

        # Background tasks
        self._processing_task = None
        self._running = False

        # Invalidation strategies
        self.invalidation_strategies = {
            InvalidationType.TTL_EXPIRY: self._handle_ttl_invalidation,
            InvalidationType.EVENT_DRIVEN: self._handle_event_invalidation,
            InvalidationType.MANUAL: self._handle_manual_invalidation,
            InvalidationType.SIZE_BASED: self._handle_size_invalidation,
            InvalidationType.DEPENDENCY: self._handle_dependency_invalidation,
            InvalidationType.VERSION_MISMATCH: self._handle_version_invalidation,
            InvalidationType.CONSISTENCY_CHECK: self._handle_consistency_invalidation,
        }

    async def initialize(self):
        """Initialize the invalidation manager."""
        # Start components
        await self.ttl_manager.start()
        await self.event_invalidator.start()

        # Start background processing
        self._running = True
        self._processing_task = asyncio.create_task(self._process_invalidations())

        # Register event handlers
        self.event_invalidator.subscribe(
            InvalidationType.DEPENDENCY.value, self._handle_dependency_event
        )

        logger.info("Cache invalidation manager initialized")

    async def shutdown(self):
        """Shutdown the invalidation manager."""
        self._running = False

        # Stop components
        await self.ttl_manager.stop()
        await self.event_invalidator.stop()

        # Cancel processing task
        if self._processing_task:
            self._processing_task.cancel()

        logger.info("Cache invalidation manager shutdown")

    async def invalidate(
        self,
        target: str,
        invalidation_type: InvalidationType = InvalidationType.MANUAL,
        scope: InvalidationScope = InvalidationScope.SINGLE_KEY,
        reason: str = "Manual invalidation",
        priority: InvalidationPriority = InvalidationPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
        callback: Optional[Callable] = None,
    ) -> str:
        """Queue cache invalidation."""
        event = InvalidationEvent(
            id=None,
            type=invalidation_type,
            scope=scope,
            target=target,
            reason=reason,
            timestamp=datetime.now(),
            priority=priority,
            metadata=metadata or {},
            callback=callback,
        )

        # Add to queue
        await self.invalidation_queue.put(event)

        logger.info(f"Queued invalidation: {event.id} - {target}")
        return event.id

    async def invalidate_by_pattern(
        self,
        pattern: str,
        reason: str = "Pattern invalidation",
        priority: InvalidationPriority = InvalidationPriority.NORMAL,
    ) -> str:
        """Invalidate cache entries matching pattern."""
        return await self.invalidate(
            target=pattern,
            invalidation_type=InvalidationType.MANUAL,
            scope=InvalidationScope.PATTERN,
            reason=reason,
            priority=priority,
        )

    async def invalidate_entity_type(
        self,
        entity_type: str,
        entity_id: Optional[str] = None,
        reason: str = "Entity invalidation",
    ) -> str:
        """Invalidate cache entries for entity type."""
        target = f"{entity_type}:{entity_id}" if entity_id else entity_type

        return await self.invalidate(
            target=target,
            invalidation_type=InvalidationType.MANUAL,
            scope=InvalidationScope.ENTITY_TYPE,
            reason=reason,
        )

    async def invalidate_user_scope(
        self, user_id: str, reason: str = "User scope invalidation"
    ) -> str:
        """Invalidate all cache entries for user."""
        return await self.invalidate(
            target=user_id,
            invalidation_type=InvalidationType.MANUAL,
            scope=InvalidationScope.USER_SCOPE,
            reason=reason,
        )

    async def invalidate_workspace_scope(
        self, workspace_id: str, reason: str = "Workspace scope invalidation"
    ) -> str:
        """Invalidate all cache entries for workspace."""
        return await self.invalidate(
            target=workspace_id,
            invalidation_type=InvalidationType.MANUAL,
            scope=InvalidationScope.WORKSPACE_SCOPE,
            reason=reason,
        )

    async def set_ttl_with_invalidation(
        self, key: str, ttl_seconds: int, reason: str = "TTL set"
    ):
        """Set TTL and schedule invalidation."""
        self.ttl_manager.set_ttl(key, ttl_seconds)

        # Schedule TTL invalidation event
        await self.invalidate(
            target=key,
            invalidation_type=InvalidationType.TTL_EXPIRY,
            scope=InvalidationScope.SINGLE_KEY,
            reason=reason,
            priority=InvalidationPriority.LOW,
        )

    def add_dependency_rule(
        self,
        source_pattern: str,
        dependent_pattern: str,
        cascade: bool = True,
        delay_seconds: int = 0,
    ):
        """Add dependency rule for automatic invalidation."""
        rule = DependencyRule(
            source_key_pattern=source_pattern,
            dependent_key_pattern=dependent_pattern,
            invalidation_type=InvalidationType.DEPENDENCY,
            cascade=cascade,
            delay_seconds=delay_seconds,
        )

        self.dependency_manager.add_dependency_rule(rule)

    async def _process_invalidations(self):
        """Process invalidation events from queue."""
        semaphore = asyncio.Semaphore(self.max_concurrent_invalidations)

        while self._running:
            try:
                # Get invalidation event
                event = await asyncio.wait_for(
                    self.invalidation_queue.get(), timeout=1.0
                )

                # Process with semaphore
                async def process_with_semaphore():
                    async with semaphore:
                        await self._execute_invalidation(event)

                asyncio.create_task(process_with_semaphore())

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Invalidation processing error: {e}")

    async def _execute_invalidation(self, event: InvalidationEvent):
        """Execute a single invalidation event."""
        start_time = time.time()

        try:
            # Check if already being processed
            if event.id in self.active_invalidations:
                return

            self.active_invalidations.add(event.id)

            # Get invalidation strategy
            strategy = self.invalidation_strategies.get(event.type)
            if not strategy:
                logger.error(f"No strategy for invalidation type: {event.type}")
                return

            # Execute strategy
            await strategy(event)

            # Update statistics
            self.stats["total_invalidations"] += 1
            self.stats["successful_invalidations"] += 1
            self.stats["invalidation_by_type"][event.type.value] += 1
            self.stats["invalidation_by_scope"][event.scope.value] += 1

            # Update processing time
            processing_time = time.time() - start_time
            current_avg = self.stats["average_invalidation_time"]
            self.stats["average_invalidation_time"] = (
                current_avg + processing_time
            ) / 2

            # Add to history
            self.invalidation_history.append(event.to_dict())

            logger.info(
                f"Invalidated: {event.id} - {event.target} in {processing_time:.3f}s"
            )

        except Exception as e:
            logger.error(f"Invalidation execution error: {e}")
            self.stats["failed_invalidations"] += 1

        finally:
            self.active_invalidations.discard(event.id)

    async def _handle_ttl_invalidation(self, event: InvalidationEvent):
        """Handle TTL-based invalidation."""
        from comprehensive_cache import get_comprehensive_cache

        cache = await get_comprehensive_cache()

        await cache.delete(event.target)
        self.ttl_manager.remove_ttl(event.target)

    async def _handle_event_invalidation(self, event: InvalidationEvent):
        """Handle event-driven invalidation."""
        # Emit to event system
        await self.event_invalidator.emit_event(event)

    async def _handle_manual_invalidation(self, event: InvalidationEvent):
        """Handle manual invalidation."""
        from comprehensive_cache import get_comprehensive_cache

        cache = await get_comprehensive_cache()

        if event.scope == InvalidationScope.SINGLE_KEY:
            await cache.delete(event.target)
        elif event.scope == InvalidationScope.PATTERN:
            await cache.invalidate_pattern(event.target)
        elif event.scope == InvalidationScope.ENTITY_TYPE:
            # Use key generator to find entity keys
            from cache_key_generator import invalidate_entity_cache

            entity_parts = event.target.split(":")
            entity_type = entity_parts[0]
            entity_id = entity_parts[1] if len(entity_parts) > 1 else None

            keys = invalidate_entity_cache(entity_type, entity_id)
            for key in keys:
                await cache.delete(key)
        elif event.scope == InvalidationScope.USER_SCOPE:
            # Invalidate all keys for user
            await cache.invalidate_pattern(f"*user:{event.target}*")
        elif event.scope == InvalidationScope.WORKSPACE_SCOPE:
            # Invalidate all keys for workspace
            await cache.invalidate_pattern(f"*workspace:{event.target}*")

    async def _handle_size_invalidation(self, event: InvalidationEvent):
        """Handle size-based invalidation."""
        # This would typically be handled by the cache itself
        # but we can trigger cleanup if needed
        pass

    async def _handle_dependency_invalidation(self, event: InvalidationEvent):
        """Handle dependency-based invalidation."""
        # Find dependent keys
        dependent_keys = self.dependency_manager.find_dependent_keys(event.target)

        # Get invalidation order
        invalidation_order = self.dependency_manager.get_invalidation_order(
            event.target
        )

        # Invalidate in order
        from comprehensive_cache import get_comprehensive_cache

        cache = await get_comprehensive_cache()

        for key in invalidation_order:
            await cache.delete(key)

            # Add delay if specified
            if event.metadata.get("delay_seconds", 0) > 0:
                await asyncio.sleep(event.metadata["delay_seconds"])

    async def _handle_version_invalidation(self, event: InvalidationEvent):
        """Handle version mismatch invalidation."""
        # Invalidate all keys with old version
        from comprehensive_cache import get_comprehensive_cache

        cache = await get_comprehensive_cache()

        version_pattern = f"*:{event.metadata.get('old_version', 'v1')}"
        await cache.invalidate_pattern(version_pattern)

    async def _handle_consistency_invalidation(self, event: InvalidationEvent):
        """Handle consistency check invalidation."""
        # Invalidate keys that failed consistency check
        from comprehensive_cache import get_comprehensive_cache

        cache = await get_comprehensive_cache()

        inconsistent_keys = event.metadata.get("inconsistent_keys", [])
        for key in inconsistent_keys:
            await cache.delete(key)

    async def _handle_dependency_event(self, event: InvalidationEvent):
        """Handle dependency events."""
        # Schedule dependency invalidation
        await self.invalidate(
            target=event.target,
            invalidation_type=InvalidationType.DEPENDENCY,
            scope=InvalidationScope.DEPENDENCY_GRAPH,
            reason=f"Dependency: {event.reason}",
            metadata=event.metadata,
        )

    def get_invalidation_stats(self) -> Dict[str, Any]:
        """Get invalidation statistics."""
        ttl_stats = {
            "active_ttls": len(self.ttl_manager.ttl_store),
            "expiry_queue_size": len(self.ttl_manager.expiry_queue),
        }

        event_stats = self.event_invalidator.get_event_stats()

        return {
            "invalidation_stats": self.stats.copy(),
            "ttl_stats": ttl_stats,
            "event_stats": event_stats,
            "queue_size": self.invalidation_queue.qsize(),
            "active_invalidations": len(self.active_invalidations),
            "dependency_rules": len(self.dependency_manager.dependency_rules),
            "history_size": len(self.invalidation_history),
        }


# Global invalidation manager instance
_invalidation_manager: Optional[CacheInvalidationManager] = None


async def get_invalidation_manager() -> CacheInvalidationManager:
    """Get the global invalidation manager."""
    global _invalidation_manager
    if _invalidation_manager is None:
        _invalidation_manager = CacheInvalidationManager()
        await _invalidation_manager.initialize()
    return _invalidation_manager


# Convenience functions
async def invalidate_cache(target: str, reason: str = "Manual invalidation") -> str:
    """Invalidate cache entry (convenience function)."""
    manager = await get_invalidation_manager()
    return await manager.invalidate(target, reason=reason)


async def invalidate_cache_pattern(
    pattern: str, reason: str = "Pattern invalidation"
) -> str:
    """Invalidate cache entries matching pattern (convenience function)."""
    manager = await get_invalidation_manager()
    return await manager.invalidate_by_pattern(pattern, reason)


async def set_cache_ttl(key: str, ttl_seconds: int):
    """Set TTL for cache key (convenience function)."""
    manager = await get_invalidation_manager()
    await manager.set_ttl_with_invalidation(key, ttl_seconds)


def add_cache_dependency(
    source_pattern: str, dependent_pattern: str, cascade: bool = True
):
    """Add cache dependency rule (convenience function)."""
    manager = get_invalidation_manager()
    manager.add_dependency_rule(source_pattern, dependent_pattern, cascade)


def get_invalidation_statistics() -> Dict[str, Any]:
    """Get invalidation statistics (convenience function)."""
    if _invalidation_manager:
        return _invalidation_manager.get_invalidation_stats()
    return {"error": "Invalidation manager not initialized"}
