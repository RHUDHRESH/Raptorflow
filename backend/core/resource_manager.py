"""
RaptorFlow Resource Manager
Provides robust resource cleanup and memory leak prevention.
"""

import asyncio
import gc
import logging
import psutil
import threading
import time
import weakref
from typing import Dict, Any, Optional, List, Callable, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from contextlib import asynccontextmanager, contextmanager
import tracemalloc

from core.enhanced_exceptions import (
    SystemError,
    handle_system_error
)

logger = logging.getLogger("raptorflow.resource_manager")


class ResourceType(Enum):
    """Types of managed resources."""
    DATABASE_CONNECTION = "database_connection"
    HTTP_CLIENT = "http_client"
    FILE_HANDLE = "file_handle"
    TEMP_FILE = "temp_file"
    MEMORY_BUFFER = "memory_buffer"
    ASYNC_TASK = "async_task"
    THREAD = "thread"
    SEMAPHORE = "semaphore"
    LOCK = "lock"
    CUSTOM = "custom"


@dataclass
class ResourceInfo:
    """Information about a managed resource."""
    resource_id: str
    resource_type: ResourceType
    created_at: datetime
    last_accessed: datetime
    size_bytes: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    cleanup_func: Optional[Callable] = None
    ref_count: int = 0
    is_active: bool = True


@dataclass
class MemoryMetrics:
    """Memory usage metrics."""
    total_allocated: int = 0
    total_freed: int = 0
    peak_usage: int = 0
    current_usage: int = 0
    gc_runs: int = 0
    gc_time: float = 0.0
    leaks_detected: int = 0


@dataclass
class ResourceMetrics:
    """Resource management metrics."""
    total_resources: int = 0
    active_resources: int = 0
    cleaned_resources: int = 0
    failed_cleanups: int = 0
    memory_metrics: MemoryMetrics = field(default_factory=MemoryMetrics)


class ResourceManager:
    """
    Comprehensive resource manager with automatic cleanup and leak detection.
    """
    
    def __init__(self, cleanup_interval: float = 60.0, max_resource_age: float = 3600.0):
        self.cleanup_interval = cleanup_interval
        self.max_resource_age = max_resource_age
        self._resources: Dict[str, ResourceInfo] = {}
        self._resource_refs: Dict[str, weakref.ref] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        self._metrics = ResourceMetrics()
        self._resource_counter = 0
        self._lock = threading.RLock()
        
        # Start memory tracking
        tracemalloc.start()
        self._last_gc_time = time.time()
    
    async def initialize(self):
        """Initialize the resource manager."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Resource manager initialized")
    
    async def shutdown(self):
        """Shutdown the resource manager and clean up all resources."""
        logger.info("Shutting down resource manager...")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Clean up all resources
        await self.cleanup_all_resources()
        
        # Final garbage collection
        await self.force_garbage_collection()
        
        # Stop memory tracking
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        
        logger.info("Resource manager shutdown complete")
    
    def register_resource(
        self,
        resource: Any,
        resource_type: ResourceType,
        cleanup_func: Optional[Callable] = None,
        size_bytes: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register a resource for automatic cleanup.
        """
        with self._lock:
            resource_id = self._generate_resource_id()
            
            # Create resource info
            resource_info = ResourceInfo(
                resource_id=resource_id,
                resource_type=resource_type,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                size_bytes=size_bytes,
                metadata=metadata or {},
                cleanup_func=cleanup_func,
                ref_count=1
            )
            
            # Store resource info and weak reference
            self._resources[resource_id] = resource_info
            self._resource_refs[resource_id] = weakref.ref(
                resource,
                lambda ref: self._resource_deallocated(resource_id)
            )
            
            # Update metrics
            self._metrics.total_resources += 1
            self._metrics.active_resources += 1
            if size_bytes:
                self._metrics.memory_metrics.total_allocated += size_bytes
            
            logger.debug(f"Registered resource {resource_id} of type {resource_type.value}")
            return resource_id
    
    def access_resource(self, resource_id: str) -> Optional[Any]:
        """
        Access a resource and update its last accessed time.
        """
        with self._lock:
            if resource_id not in self._resources:
                return None
            
            resource_info = self._resources[resource_id]
            if not resource_info.is_active:
                return None
            
            # Update access time and ref count
            resource_info.last_accessed = datetime.utcnow()
            resource_info.ref_count += 1
            
            # Get the actual resource via weak reference
            resource_ref = self._resource_refs.get(resource_id)
            if resource_ref:
                resource = resource_ref()
                return resource
            
            return None
    
    def release_resource(self, resource_id: str) -> bool:
        """
        Release a resource reference.
        """
        with self._lock:
            if resource_id not in self._resources:
                return False
            
            resource_info = self._resources[resource_id]
            if resource_info.ref_count > 0:
                resource_info.ref_count -= 1
            
            # Schedule cleanup if no more references
            if resource_info.ref_count == 0:
                asyncio.create_task(self._cleanup_resource(resource_id))
            
            return True
    
    async def cleanup_resource(self, resource_id: str) -> bool:
        """
        Manually clean up a specific resource.
        """
        return await self._cleanup_resource(resource_id)
    
    async def cleanup_all_resources(self) -> Dict[str, Any]:
        """
        Clean up all registered resources.
        """
        cleanup_results = {
            "success": 0,
            "failed": 0,
            "already_cleaned": 0
        }
        
        with self._lock:
            resource_ids = list(self._resources.keys())
        
        for resource_id in resource_ids:
            success = await self._cleanup_resource(resource_id)
            if success:
                cleanup_results["success"] += 1
            else:
                cleanup_results["failed"] += 1
        
        logger.info(f"Cleanup completed: {cleanup_results}")
        return cleanup_results
    
    async def _cleanup_resource(self, resource_id: str) -> bool:
        """
        Internal method to clean up a resource.
        """
        with self._lock:
            if resource_id not in self._resources:
                return True  # Already cleaned
            
            resource_info = self._resources[resource_id]
            if not resource_info.is_active:
                return True  # Already cleaned
            
            try:
                # Call cleanup function if provided
                if resource_info.cleanup_func:
                    if asyncio.iscoroutinefunction(resource_info.cleanup_func):
                        await resource_info.cleanup_func()
                    else:
                        resource_info.cleanup_func()
                
                # Get resource size for metrics
                size_bytes = resource_info.size_bytes
                
                # Mark as inactive
                resource_info.is_active = False
                self._metrics.active_resources -= 1
                self._metrics.cleaned_resources += 1
                
                if size_bytes:
                    self._metrics.memory_metrics.total_freed += size_bytes
                
                logger.debug(f"Cleaned up resource {resource_id}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to cleanup resource {resource_id}: {e}")
                self._metrics.failed_cleanups += 1
                return False
    
    def _resource_deallocated(self, resource_id: str):
        """
        Callback when a resource is deallocated by garbage collector.
        """
        with self._lock:
            if resource_id in self._resources:
                resource_info = self._resources[resource_id]
                resource_info.is_active = False
                self._metrics.active_resources -= 1
                self._metrics.cleaned_resources += 1
                logger.debug(f"Resource {resource_id} deallocated by GC")
    
    async def _cleanup_loop(self):
        """
        Periodic cleanup of old and unused resources.
        """
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._periodic_cleanup()
                await self._check_memory_usage()
                await self._detect_memory_leaks()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _periodic_cleanup(self):
        """
        Clean up old and unused resources.
        """
        current_time = datetime.utcnow()
        resources_to_cleanup = []
        
        with self._lock:
            for resource_id, resource_info in self._resources.items():
                if not resource_info.is_active:
                    continue
                
                # Check if resource is too old
                age = (current_time - resource_info.created_at).total_seconds()
                if age > self.max_resource_age:
                    resources_to_cleanup.append(resource_id)
                    continue
                
                # Check if resource hasn't been accessed recently
                last_access_age = (current_time - resource_info.last_accessed).total_seconds()
                if last_access_age > self.max_resource_age / 2 and resource_info.ref_count == 0:
                    resources_to_cleanup.append(resource_id)
        
        # Clean up identified resources
        for resource_id in resources_to_cleanup:
            await self._cleanup_resource(resource_id)
        
        if resources_to_cleanup:
            logger.info(f"Periodic cleanup: cleaned {len(resources_to_cleanup)} old resources")
    
    async def _check_memory_usage(self):
        """
        Check memory usage and trigger garbage collection if needed.
        """
        try:
            # Get current memory usage
            process = psutil.Process()
            memory_info = process.memory_info()
            current_memory = memory_info.rss
            
            # Update metrics
            self._metrics.memory_metrics.current_usage = current_memory
            self._metrics.memory_metrics.peak_usage = max(
                self._metrics.memory_metrics.peak_usage,
                current_memory
            )
            
            # Trigger GC if memory usage is high
            if current_memory > 500 * 1024 * 1024:  # 500MB
                await self.force_garbage_collection()
                
        except Exception as e:
            logger.error(f"Error checking memory usage: {e}")
    
    async def _detect_memory_leaks(self):
        """
        Detect potential memory leaks using tracemalloc.
        """
        if not tracemalloc.is_tracing():
            return
        
        try:
            # Get memory snapshot
            snapshot = tracemalloc.take_snapshot()
            
            # Find top memory allocations
            top_stats = snapshot.statistics('lineno')[:10]
            
            # Check for suspicious patterns
            leaks_detected = 0
            for stat in top_stats:
                if stat.size > 10 * 1024 * 1024:  # 10MB
                    leaks_detected += 1
                    logger.warning(f"Potential memory leak detected: {stat}")
            
            self._metrics.memory_metrics.leaks_detected = leaks_detected
            
        except Exception as e:
            logger.error(f"Error detecting memory leaks: {e}")
    
    async def force_garbage_collection(self):
        """
        Force garbage collection and update metrics.
        """
        start_time = time.time()
        
        # Run garbage collection
        collected = gc.collect()
        
        # Update metrics
        gc_time = time.time() - start_time
        self._metrics.memory_metrics.gc_runs += 1
        self._metrics.memory_metrics.gc_time += gc_time
        
        logger.debug(f"Garbage collection completed: {collected} objects collected in {gc_time:.3f}s")
    
    def _generate_resource_id(self) -> str:
        """Generate a unique resource ID."""
        self._resource_counter += 1
        return f"resource_{int(time.time())}_{self._resource_counter}"
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current resource management metrics."""
        with self._lock:
            return {
                "total_resources": self._metrics.total_resources,
                "active_resources": self._metrics.active_resources,
                "cleaned_resources": self._metrics.cleaned_resources,
                "failed_cleanups": self._metrics.failed_cleanups,
                "memory_metrics": {
                    "total_allocated": self._metrics.memory_metrics.total_allocated,
                    "total_freed": self._metrics.memory_metrics.total_freed,
                    "peak_usage": self._metrics.memory_metrics.peak_usage,
                    "current_usage": self._metrics.memory_metrics.current_usage,
                    "gc_runs": self._metrics.memory_metrics.gc_runs,
                    "gc_time": self._metrics.memory_metrics.gc_time,
                    "leaks_detected": self._metrics.memory_metrics.leaks_detected
                },
                "config": {
                    "cleanup_interval": self.cleanup_interval,
                    "max_resource_age": self.max_resource_age
                }
            }
    
    def get_resource_info(self) -> List[Dict[str, Any]]:
        """Get information about all managed resources."""
        with self._lock:
            return [
                {
                    "resource_id": info.resource_id,
                    "resource_type": info.resource_type.value,
                    "created_at": info.created_at.isoformat(),
                    "last_accessed": info.last_accessed.isoformat(),
                    "size_bytes": info.size_bytes,
                    "ref_count": info.ref_count,
                    "is_active": info.is_active,
                    "metadata": info.metadata
                }
                for info in self._resources.values()
            ]


# Global resource manager instance
_resource_manager: Optional[ResourceManager] = None


async def get_resource_manager() -> ResourceManager:
    """Get the global resource manager instance."""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
        await _resource_manager.initialize()
    return _resource_manager


# Context managers and decorators
@asynccontextmanager
async def managed_resource(
    resource: Any,
    resource_type: ResourceType,
    cleanup_func: Optional[Callable] = None,
    size_bytes: Optional[int] = None
):
    """
    Context manager for automatically managed resources.
    """
    manager = await get_resource_manager()
    resource_id = manager.register_resource(
        resource, resource_type, cleanup_func, size_bytes
    )
    
    try:
        yield resource_id, resource
    finally:
        await manager.cleanup_resource(resource_id)


@contextmanager
def managed_sync_resource(
    resource: Any,
    resource_type: ResourceType,
    cleanup_func: Optional[Callable] = None,
    size_bytes: Optional[int] = None
):
    """
    Context manager for synchronously managed resources.
    """
    # Note: This is a simplified version for sync resources
    try:
        yield resource
    finally:
        if cleanup_func:
            cleanup_func()


def auto_cleanup(
    resource_type: ResourceType,
    size_bytes: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Decorator for automatic resource cleanup.
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            manager = await get_resource_manager()
            
            # Create resource from function
            resource = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Register resource
            cleanup_func = getattr(resource, 'close', getattr(resource, 'cleanup', None))
            resource_id = manager.register_resource(
                resource, resource_type, cleanup_func, size_bytes, metadata
            )
            
            return resource_id, resource
        
        def sync_wrapper(*args, **kwargs):
            # For sync functions, just call and return
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


# Utility functions
async def cleanup_on_interval(interval: float = 300.0):
    """
    Periodic cleanup utility.
    """
    manager = await get_resource_manager()
    
    while True:
        await asyncio.sleep(interval)
        await manager.cleanup_all_resources()


if __name__ == "__main__":
    # Test resource manager
    async def test_resource_manager():
        manager = ResourceManager()
        await manager.initialize()
        
        # Test resource registration and cleanup
        class TestResource:
            def __init__(self, name):
                self.name = name
            
            def close(self):
                print(f"Closing {self.name}")
        
        resource = TestResource("test")
        resource_id = manager.register_resource(
            resource,
            ResourceType.CUSTOM,
            cleanup_func=resource.close
        )
        
        print(f"Registered resource: {resource_id}")
        print(manager.get_metrics())
        
        # Cleanup
        await manager.cleanup_resource(resource_id)
        await manager.shutdown()
    
    asyncio.run(test_resource_manager())
