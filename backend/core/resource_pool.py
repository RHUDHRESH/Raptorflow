"""
Resource pooling system for performance optimization.
Provides efficient resource management for connections, memory, and agent instances.
"""

import asyncio
import logging
import threading
import time
import weakref
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Set
from enum import Enum
import hashlib
import json

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources that can be pooled."""
    CONNECTION = "connection"
    AGENT_INSTANCE = "agent_instance"
    MEMORY_BUFFER = "memory_buffer"
    FILE_HANDLE = "file_handle"
    CACHE_ENTRY = "cache_entry"
    CUSTOM = "custom"


class PoolStatus(Enum):
    """Resource pool status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    EXHAUSTED = "exhausted"
    ERROR = "error"


@dataclass
class ResourceMetrics:
    """Metrics for a pooled resource."""
    resource_id: str
    resource_type: ResourceType
    created_at: datetime
    last_used: datetime
    usage_count: int = 0
    total_usage_time: float = 0.0
    error_count: int = 0
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def avg_usage_time(self) -> float:
        """Calculate average usage time."""
        return self.total_usage_time / self.usage_count if self.usage_count > 0 else 0.0
    
    @property
    def age_seconds(self) -> float:
        """Get resource age in seconds."""
        return (datetime.utcnow() - self.created_at).total_seconds()
    
    @property
    def idle_seconds(self) -> float:
        """Get idle time in seconds."""
        return (datetime.utcnow() - self.last_used).total_seconds()


@dataclass
class PoolStatistics:
    """Statistics for a resource pool."""
    pool_name: str
    resource_type: ResourceType
    total_resources: int
    active_resources: int
    idle_resources: int
    exhausted_resources: int
    total_acquisitions: int
    total_releases: int
    total_errors: int
    avg_wait_time: float
    peak_usage: int
    created_at: datetime
    last_updated: datetime
    
    @property
    def utilization_rate(self) -> float:
        """Calculate utilization rate."""
        return self.active_resources / self.total_resources if self.total_resources > 0 else 0.0
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate."""
        return self.total_errors / self.total_acquisitions if self.total_acquisitions > 0 else 0.0


class PooledResource:
    """Wrapper for pooled resources with tracking."""
    
    def __init__(
        self,
        resource: Any,
        resource_id: str,
        pool: 'ResourcePool',
        created_at: datetime = None
    ):
        self.resource = resource
        self.resource_id = resource_id
        self.pool = pool
        self.created_at = created_at or datetime.utcnow()
        self.last_used = self.created_at
        self.usage_count = 0
        self.total_usage_time = 0.0
        self.error_count = 0
        self.is_active = True
        self.metadata = {}
        self._acquisition_time = None
    
    def __enter__(self):
        self._acquisition_time = time.time()
        self.last_used = datetime.utcnow()
        self.usage_count += 1
        return self.resource
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error_count += 1
        
        if self._acquisition_time is not None:
            usage_time = time.time() - self._acquisition_time
            self.total_usage_time += usage_time
            self._acquisition_time = None
        
        # Return to pool
        self.pool.release(self)
    
    def get_metrics(self) -> ResourceMetrics:
        """Get resource metrics."""
        return ResourceMetrics(
            resource_id=self.resource_id,
            resource_type=self.pool.resource_type,
            created_at=self.created_at,
            last_used=self.last_used,
            usage_count=self.usage_count,
            total_usage_time=self.total_usage_time,
            error_count=self.error_count,
            is_active=self.is_active,
            metadata=self.metadata.copy()
        )


class ResourcePool(ABC):
    """Abstract base class for resource pools."""
    
    def __init__(
        self,
        pool_name: str,
        resource_type: ResourceType,
        max_size: int = 10,
        min_size: int = 1,
        max_idle_time: int = 300,  # 5 minutes
        health_check_interval: int = 60,  # 1 minute
        enable_metrics: bool = True
    ):
        self.pool_name = pool_name
        self.resource_type = resource_type
        self.max_size = max_size
        self.min_size = min_size
        self.max_idle_time = max_idle_time
        self.health_check_interval = health_check_interval
        self.enable_metrics = enable_metrics
        
        # Pool state
        self._available: List[PooledResource] = []
        self._in_use: Set[PooledResource] = set()
        self._exhausted: Set[PooledResource] = set()
        self._lock = threading.RLock()
        
        # Statistics
        self._total_acquisitions = 0
        self._total_releases = 0
        self._total_errors = 0
        self._total_wait_time = 0.0
        self._peak_usage = 0
        self._created_at = datetime.utcnow()
        
        # Background tasks
        self._health_check_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Initialize minimum resources
        self._initialize_min_resources()
        
        logger.info(f"Resource pool '{pool_name}' initialized: max_size={max_size}, min_size={min_size}")
    
    @abstractmethod
    def create_resource(self) -> Any:
        """Create a new resource instance."""
        pass
    
    @abstractmethod
    def destroy_resource(self, resource: Any) -> None:
        """Destroy a resource instance."""
        pass
    
    @abstractmethod
    def is_resource_healthy(self, resource: Any) -> bool:
        """Check if a resource is healthy."""
        pass
    
    @abstractmethod
    def reset_resource(self, resource: Any) -> None:
        """Reset resource to clean state."""
        pass
    
    def _initialize_min_resources(self):
        """Initialize minimum number of resources."""
        with self._lock:
            while len(self._available) + len(self._in_use) < self.min_size:
                try:
                    resource = self._create_pooled_resource()
                    self._available.append(resource)
                    logger.debug(f"Created initial resource {resource.resource_id}")
                except Exception as e:
                    logger.error(f"Failed to create initial resource: {e}")
                    break
    
    def _create_pooled_resource(self) -> PooledResource:
        """Create a new pooled resource."""
        resource = self.create_resource()
        resource_id = hashlib.md5(
            f"{self.pool_name}_{time.time()}_{id(resource)}".encode()
        ).hexdigest()[:16]
        
        return PooledResource(resource, resource_id, self)
    
    async def start(self):
        """Start background tasks."""
        if self._running:
            return
        
        self._running = True
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info(f"Resource pool '{self.pool_name}' started")
    
    async def stop(self):
        """Stop background tasks and cleanup resources."""
        self._running = False
        
        # Cancel background tasks
        if self._health_check_task:
            self._health_check_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(
            self._health_check_task, self._cleanup_task,
            return_exceptions=True
        )
        
        # Cleanup all resources
        with self._lock:
            all_resources = self._available + list(self._in_use) + list(self._exhausted)
            for pooled_resource in all_resources:
                try:
                    self.destroy_resource(pooled_resource.resource)
                except Exception as e:
                    logger.error(f"Failed to destroy resource {pooled_resource.resource_id}: {e}")
            
            self._available.clear()
            self._in_use.clear()
            self._exhausted.clear()
        
        logger.info(f"Resource pool '{self.pool_name}' stopped")
    
    def acquire(self, timeout: float = 30.0) -> PooledResource:
        """Acquire a resource from the pool."""
        start_time = time.time()
        
        try:
            with self._lock:
                # Try to get available resource
                if self._available:
                    pooled_resource = self._available.pop(0)
                    self._in_use.add(pooled_resource)
                    
                    # Check if resource is healthy
                    if not self.is_resource_healthy(pooled_resource.resource):
                        logger.warning(f"Resource {pooled_resource.resource_id} is unhealthy, destroying")
                        self._exhausted.add(pooled_resource)
                        self._in_use.remove(pooled_resource)
                        return self.acquire(timeout)  # Try again
                
                # Create new resource if under max size
                elif len(self._in_use) < self.max_size:
                    pooled_resource = self._create_pooled_resource()
                    self._in_use.add(pooled_resource)
                
                # Pool exhausted
                else:
                    wait_time = timeout - (time.time() - start_time)
                    if wait_time <= 0:
                        raise Exception(f"Resource pool '{self.pool_name}' exhausted")
                    
                    # Wait for resource to become available
                    self._lock.wait(wait_time)
                    return self.acquire(max(0, timeout - (time.time() - start_time)))
            
            # Update statistics
            self._total_acquisitions += 1
            wait_time = time.time() - start_time
            self._total_wait_time += wait_time
            self._peak_usage = max(self._peak_usage, len(self._in_use))
            
            logger.debug(f"Acquired resource {pooled_resource.resource_id} from pool '{self.pool_name}'")
            return pooled_resource
            
        except Exception as e:
            self._total_errors += 1
            logger.error(f"Failed to acquire resource from pool '{self.pool_name}': {e}")
            raise
    
    def release(self, pooled_resource: PooledResource):
        """Release a resource back to the pool."""
        try:
            with self._lock:
                if pooled_resource not in self._in_use:
                    logger.warning(f"Resource {pooled_resource.resource_id} not in use")
                    return
                
                self._in_use.remove(pooled_resource)
                
                # Reset resource
                try:
                    self.reset_resource(pooled_resource.resource)
                except Exception as e:
                    logger.error(f"Failed to reset resource {pooled_resource.resource_id}: {e}")
                    self._exhausted.add(pooled_resource)
                    return
                
                # Return to available pool
                self._available.append(pooled_resource)
                self._total_releases += 1
                
                # Notify waiting threads
                self._lock.notify_all()
                
                logger.debug(f"Released resource {pooled_resource.resource_id} to pool '{self.pool_name}'")
                
        except Exception as e:
            self._total_errors += 1
            logger.error(f"Failed to release resource {pooled_resource.resource_id}: {e}")
    
    def get_status(self) -> PoolStatus:
        """Get pool status."""
        with self._lock:
            total = len(self._available) + len(self._in_use)
            
            if total == 0:
                return PoolStatus.ERROR
            elif len(self._in_use) >= self.max_size:
                return PoolStatus.EXHAUSTED
            elif len(self._in_use) > self.max_size * 0.8:
                return PoolStatus.DEGRADED
            else:
                return PoolStatus.HEALTHY
    
    def get_statistics(self) -> PoolStatistics:
        """Get pool statistics."""
        with self._lock:
            avg_wait_time = self._total_wait_time / self._total_acquisitions if self._total_acquisitions > 0 else 0.0
            
            return PoolStatistics(
                pool_name=self.pool_name,
                resource_type=self.resource_type,
                total_resources=len(self._available) + len(self._in_use),
                active_resources=len(self._in_use),
                idle_resources=len(self._available),
                exhausted_resources=len(self._exhausted),
                total_acquisitions=self._total_acquisitions,
                total_releases=self._total_releases,
                total_errors=self._total_errors,
                avg_wait_time=avg_wait_time,
                peak_usage=self._peak_usage,
                created_at=self._created_at,
                last_updated=datetime.utcnow()
            )
    
    def get_resource_metrics(self) -> List[ResourceMetrics]:
        """Get metrics for all resources."""
        with self._lock:
            all_resources = self._available + list(self._in_use) + list(self._exhausted)
            return [resource.get_metrics() for resource in all_resources]
    
    async def _health_check_loop(self):
        """Background health check loop."""
        while self._running:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error in pool '{self.pool_name}': {e}")
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(self.max_idle_time // 2)
                await self._perform_cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error in pool '{self.pool_name}': {e}")
    
    async def _perform_health_checks(self):
        """Perform health checks on all resources."""
        with self._lock:
            resources_to_check = self._available.copy()
        
        unhealthy_resources = []
        
        for pooled_resource in resources_to_check:
            try:
                if not self.is_resource_healthy(pooled_resource.resource):
                    unhealthy_resources.append(pooled_resource)
            except Exception as e:
                logger.error(f"Health check failed for resource {pooled_resource.resource_id}: {e}")
                unhealthy_resources.append(pooled_resource)
        
        # Remove unhealthy resources
        if unhealthy_resources:
            with self._lock:
                for resource in unhealthy_resources:
                    if resource in self._available:
                        self._available.remove(resource)
                        self._exhausted.add(resource)
                        logger.warning(f"Resource {resource.resource_id} marked as exhausted")
    
    async def _perform_cleanup(self):
        """Perform cleanup of idle and exhausted resources."""
        with self._lock:
            # Remove exhausted resources and create new ones if needed
            exhausted_count = len(self._exhausted)
            for resource in list(self._exhausted):
                try:
                    self.destroy_resource(resource.resource)
                    self._exhausted.remove(resource)
                except Exception as e:
                    logger.error(f"Failed to destroy exhausted resource {resource.resource_id}: {e}")
            
            # Remove idle resources above minimum
            idle_to_remove = []
            for resource in self._available:
                if resource.idle_seconds > self.max_idle_time:
                    idle_to_remove.append(resource)
            
            # Keep minimum resources
            while len(idle_to_remove) > 0 and len(self._available) - len(idle_to_remove) >= self.min_size:
                resource = idle_to_remove.pop()
                self._available.remove(resource)
                try:
                    self.destroy_resource(resource.resource)
                    logger.debug(f"Destroyed idle resource {resource.resource_id}")
                except Exception as e:
                    logger.error(f"Failed to destroy idle resource {resource.resource_id}: {e}")
            
            # Replenish to minimum if needed
            current_total = len(self._available) + len(self._in_use)
            while current_total < self.min_size:
                try:
                    resource = self._create_pooled_resource()
                    self._available.append(resource)
                    current_total += 1
                    logger.debug(f"Created resource to maintain minimum pool size")
                except Exception as e:
                    logger.error(f"Failed to create resource during cleanup: {e}")
                    break


class ConnectionPool(ResourcePool):
    """Pool for database/network connections."""
    
    def __init__(
        self,
        pool_name: str,
        connection_factory: Callable[[], Any],
        **pool_kwargs
    ):
        self.connection_factory = connection_factory
        super().__init__(pool_name, ResourceType.CONNECTION, **pool_kwargs)
    
    def create_resource(self) -> Any:
        """Create a new connection."""
        return self.connection_factory()
    
    def destroy_resource(self, resource: Any) -> None:
        """Close and destroy connection."""
        try:
            if hasattr(resource, 'close'):
                resource.close()
            elif hasattr(resource, 'disconnect'):
                resource.disconnect()
        except Exception as e:
            logger.error(f"Failed to close connection: {e}")
    
    def is_resource_healthy(self, resource: Any) -> bool:
        """Check if connection is healthy."""
        try:
            if hasattr(resource, 'ping'):
                return resource.ping()
            elif hasattr(resource, 'is_connected'):
                return resource.is_connected()
            else:
                return True  # Assume healthy if no check method
        except Exception:
            return False
    
    def reset_resource(self, resource: Any) -> None:
        """Reset connection to clean state."""
        try:
            if hasattr(resource, 'reset'):
                resource.reset()
        except Exception as e:
            logger.error(f"Failed to reset connection: {e}")


class AgentInstancePool(ResourcePool):
    """Pool for agent instances."""
    
    def __init__(
        self,
        pool_name: str,
        agent_class: type,
        agent_kwargs: Dict[str, Any] = None,
        **pool_kwargs
    ):
        self.agent_class = agent_class
        self.agent_kwargs = agent_kwargs or {}
        super().__init__(pool_name, ResourceType.AGENT_INSTANCE, **pool_kwargs)
    
    def create_resource(self) -> Any:
        """Create a new agent instance."""
        return self.agent_class(**self.agent_kwargs)
    
    def destroy_resource(self, resource: Any) -> None:
        """Cleanup agent instance."""
        try:
            if hasattr(resource, 'cleanup'):
                resource.cleanup()
            elif hasattr(resource, 'close'):
                resource.close()
        except Exception as e:
            logger.error(f"Failed to cleanup agent instance: {e}")
    
    def is_resource_healthy(self, resource: Any) -> bool:
        """Check if agent instance is healthy."""
        try:
            # Check if agent has any error states
            if hasattr(resource, 'is_healthy'):
                return resource.is_healthy()
            return True
        except Exception:
            return False
    
    def reset_resource(self, resource: Any) -> None:
        """Reset agent to clean state."""
        try:
            if hasattr(resource, 'reset'):
                resource.reset()
            elif hasattr(resource, 'clear_context'):
                resource.clear_context()
        except Exception as e:
            logger.error(f"Failed to reset agent instance: {e}")


class MemoryBufferPool(ResourcePool):
    """Pool for memory buffers."""
    
    def __init__(
        self,
        pool_name: str,
        buffer_size: int = 1024 * 1024,  # 1MB
        **pool_kwargs
    ):
        self.buffer_size = buffer_size
        super().__init__(pool_name, ResourceType.MEMORY_BUFFER, **pool_kwargs)
    
    def create_resource(self) -> bytearray:
        """Create a new memory buffer."""
        return bytearray(self.buffer_size)
    
    def destroy_resource(self, resource: bytearray) -> None:
        """Clear memory buffer."""
        try:
            resource[:] = bytearray(len(resource))
        except Exception as e:
            logger.error(f"Failed to clear memory buffer: {e}")
    
    def is_resource_healthy(self, resource: bytearray) -> bool:
        """Check if memory buffer is healthy."""
        return isinstance(resource, bytearray) and len(resource) == self.buffer_size
    
    def reset_resource(self, resource: bytearray) -> None:
        """Reset memory buffer to zeros."""
        resource[:] = bytearray(self.buffer_size)


# Global pool registry
_pool_registry: Dict[str, ResourcePool] = {}
_registry_lock = threading.Lock()


def register_pool(pool: ResourcePool) -> None:
    """Register a resource pool globally."""
    with _registry_lock:
        _pool_registry[pool.pool_name] = pool
        logger.info(f"Registered resource pool '{pool.pool_name}'")


def get_pool(pool_name: str) -> Optional[ResourcePool]:
    """Get a registered resource pool."""
    with _registry_lock:
        return _pool_registry.get(pool_name)


def list_pools() -> List[str]:
    """List all registered pool names."""
    with _registry_lock:
        return list(_pool_registry.keys())


def get_all_pool_statistics() -> Dict[str, PoolStatistics]:
    """Get statistics for all registered pools."""
    with _registry_lock:
        return {
            name: pool.get_statistics()
            for name, pool in _pool_registry.items()
        }


async def start_all_pools():
    """Start all registered pools."""
    with _registry_lock:
        for pool in _pool_registry.values():
            await pool.start()


async def stop_all_pools():
    """Stop all registered pools."""
    with _registry_lock:
        for pool in _pool_registry.values():
            await pool.stop()


# Global memory pool instance
_memory_pool: Optional["ResourcePool"] = None


def get_memory_pool() -> Optional["ResourcePool"]:
    """Get the global memory pool instance."""
    global _memory_pool
    if _memory_pool is None:
        # Create a simple memory pool
        _memory_pool = ResourcePool(
            pool_name="memory_pool",
            factory=lambda: "memory_resource",  # Simple factory function
            max_size=100,
            min_size=10,
            timeout=30.0
        )
    return _memory_pool
