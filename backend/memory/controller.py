"""
Simplified memory controller with intelligent cleanup and optimization.
Replaces over-engineered 4-memory system with a simple Redis-based approach.
Only maintains 2 memory types: vector (for search) and working (for context).
Enhanced with predictive cleanup and memory optimization.
"""

import logging
import json
import os
import asyncio
import time
import gc
import psutil
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass

try:
    import redis
except ImportError:
    redis = None

logger = logging.getLogger(__name__)


@dataclass
class MemoryStats:
    """Memory usage statistics"""
    total_memory_mb: float
    used_memory_mb: float
    available_memory_mb: float
    usage_percentage: float
    process_memory_mb: float
    redis_memory_mb: Optional[float] = None


@dataclass
class CleanupOperation:
    """Cleanup operation result"""
    operation_type: str
    items_cleaned: int
    memory_freed_mb: float
    duration_ms: float
    success: bool
    error_message: Optional[str] = None


class MemoryError(Exception):
    """Custom exception for memory-related errors."""
    pass


class SimpleMemoryController:
    """Simplified memory controller with intelligent cleanup and optimization.
    
    Maintains only 2 memory types:
    1. Vector memory - For semantic search and retrieval
    2. Working memory - For current context and session data
    
    Enhanced with:
    - Predictive memory cleanup
    - Intelligent garbage collection
    - Memory pressure monitoring
    - Automatic optimization
    """
    
    def __init__(self):
        """Initialize simplified memory controller with optimization."""
        self.redis_client = None
        self.memory_store = {}  # Start with fallback storage
        self._initialize_redis()
        
        # Memory type tracking
        self.memory_types = {
            "vector": "v_",      # Vector embeddings for semantic search
            "working": "w_",     # Current context and session data
            "cache": "c_",       # Temporary cache data
            "bcm": "bcm_"        # BCM KV namespace
        }
        
        # Performance metrics
        self.metrics = {
            "total_operations": 0,
            "redis_hits": 0,
            "fallback_hits": 0,
            "errors": 0,
            "operation_times": [],
            "last_health_check": None,
            "health_status": "unknown"
        }
        
        # Memory optimization metrics
        self.cleanup_metrics = {
            "total_cleanups": 0,
            "items_cleaned": 0,
            "memory_freed_mb": 0.0,
            "last_cleanup": None,
            "cleanup_history": deque(maxlen=100)
        }
        
        # Memory pressure thresholds
        self.memory_thresholds = {
            "warning": 70,      # 70% memory usage
            "critical": 85,     # 85% memory usage
            "emergency": 95      # 95% memory usage
        }
        
        # Cleanup configuration
        self.cleanup_config = {
            "auto_cleanup": True,
            "cleanup_interval": 300,  # 5 minutes
            "max_cache_age": 3600,    # 1 hour
            "max_working_age": 1800,  # 30 minutes
            "cleanup_batch_size": 100
        }
        
        # BCM-specific TTL configuration
        self.bcm_ttl_config = {
            "tier0": 3600,  # 1 hour for hot path
            "tier1": 86400,  # 24 hours for light RAG
            "tier2": 604800  # 1 week for cold storage
        }
        
        # Start background cleanup task
        self._cleanup_task = None
        if self.cleanup_config["auto_cleanup"]:
            self._start_cleanup_task()
    
    def _initialize_redis(self):
        """Initialize Redis connection with pooling."""
        if not redis:
            logger.warning("Redis not available - using in-memory fallback")
            self.redis_client = None
            self.memory_store = {}
            return
        
        try:
            # Try connection pooling first
            try:
                import asyncio
                from backend.core.connections import get_redis_pool
                
                async def init_pool():
                    redis_pool = await get_redis_pool()
                    if redis_pool._initialized:
                        self.redis_client = redis_pool._redis_client
                        self.memory_store = None
                        logger.info("Redis memory controller initialized with connection pooling")
                        return True
                    else:
                        return False
                
                # Run async initialization in sync context
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, create a task
                    task = asyncio.create_task(init_pool())
                    # Don't wait here to avoid blocking
                else:
                    # If loop is not running, run directly
                    success = loop.run_until_complete(init_pool())
                    if not success:
                        raise Exception("Failed to initialize Redis pool")
                
            except ImportError:
                # Fall back to direct Redis connection
                pass
            
            # Fallback to direct Redis connection
            redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            # Test connection
            redis_client.ping()
            self.redis_client = redis_client
            self.memory_store = None  # Use Redis when available
            logger.info("Redis memory controller initialized with direct connection")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            logger.warning("Falling back to in-memory storage")
            self.redis_client = None
            self.memory_store = {}
    
    async def store_memory(self, key: str, value: Any, ttl: int = 3600, memory_type: str = "working") -> bool:
        """Store a value in memory with optional TTL and memory type."""
        start_time = time.time()
        self.metrics["total_operations"] += 1
        
        try:
            # Validate inputs
            if not key or not isinstance(key, str):
                raise MemoryError(f"Invalid key: {key}")
            
            if memory_type not in self.memory_types:
                raise MemoryError(f"Invalid memory type: {memory_type}")
            
            # Prefix key based on memory type
            prefixed_key = f"{self.memory_types[memory_type]}{key}"
            
            data = {
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "ttl": ttl,
                "memory_type": memory_type,
                "stored_by": "SimpleMemoryController"
            }
            
            if self.redis_client:
                success = self.redis_client.setex(prefixed_key, ttl, json.dumps(data))
                if success:
                    self.metrics["redis_hits"] += 1
                    logger.debug(f"Stored {memory_type} memory key: {prefixed_key}")
                else:
                    raise MemoryError(f"Redis failed to store key: {prefixed_key}")
            else:
                self.memory_store[prefixed_key] = data
                self.metrics["fallback_hits"] += 1
                logger.debug(f"Stored {memory_type} memory key in fallback: {prefixed_key}")
            
            # Record operation time
            operation_time = time.time() - start_time
            self.metrics["operation_times"].append(operation_time)
            if len(self.metrics["operation_times"]) > 1000:  # Keep last 1000 operations
                self.metrics["operation_times"] = self.metrics["operation_times"][-1000:]
            
            return True
            
        except Exception as e:
            self.metrics["errors"] += 1
            operation_time = time.time() - start_time
            logger.error(f"Failed to store {memory_type} memory key '{key}' after {operation_time:.3f}s: {e}")
            return False
    
    async def retrieve_memory(self, key: str, memory_type: str = "working") -> Optional[Any]:
        """Retrieve a value from memory."""
        self.metrics["total_operations"] += 1
        
        try:
            # Prefix key based on memory type
            prefixed_key = f"{self.memory_types.get(memory_type, 'w_')}{key}"
            
            if self.redis_client:
                data = self.redis_client.get(prefixed_key)
                if data:
                    result = json.loads(data)
                    self.metrics["redis_hits"] += 1
                    logger.debug(f"Retrieved {memory_type} memory key: {prefixed_key}")
                    return result.get("value")
                self.metrics["redis_hits"] += 1
            else:
                result = self.memory_store.get(prefixed_key)
                if result:
                    self.metrics["fallback_hits"] += 1
                    logger.debug(f"Retrieved {memory_type} memory key from fallback: {prefixed_key}")
                    return result.get("value")
                self.metrics["fallback_hits"] += 1
            
            return None
            
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Failed to retrieve {memory_type} memory key '{key}': {e}")
            return None
    
    async def store_vector(self, text: str, vector: List[float], metadata: Dict[str, Any] = None) -> str:
        """Store vector embedding for semantic search."""
        import hashlib
        
        # Generate vector ID from text hash
        vector_id = hashlib.md5(text.encode()).hexdigest()
        
        vector_data = {
            "text": text,
            "vector": vector,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        # Store with vector memory type
        success = await self.store_memory(
            vector_id, 
            vector_data, 
            ttl=86400,  # 24 hours
            memory_type="vector"
        )
        
        if success:
            logger.debug(f"Stored vector embedding: {vector_id}")
        
        return vector_id
    
    async def search_vectors(self, query_vector: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar vectors (simplified implementation)."""
        try:
            # Get all vector memories
            vector_keys = []
            if self.redis_client:
                # Get all vector keys
                for key in self.redis_client.keys(f"{self.memory_types['vector']}*"):
                    vector_keys.append(key)
            else:
                # Get all vector keys from fallback
                for key in self.memory_store.keys():
                    if key.startswith(self.memory_types['vector']):
                        vector_keys.append(key)
            
            # Simple similarity search (in production, would use proper vector similarity)
            results = []
            for key in vector_keys[:limit]:
                if self.redis_client:
                    data = self.redis_client.get(key)
                    if data:
                        vector_data = json.loads(data)
                        results.append({
                            "id": key.replace(self.memory_types['vector'], ''),
                            "text": vector_data.get("text"),
                            "metadata": vector_data.get("metadata", {}),
                            "similarity_score": 0.8  # Placeholder similarity
                        })
                else:
                    vector_data = self.memory_store.get(key)
                    if vector_data:
                        results.append({
                            "id": key.replace(self.memory_types['vector'], ''),
                            "text": vector_data.get("text"),
                            "metadata": vector_data.get("metadata", {}),
                            "similarity_score": 0.8  # Placeholder similarity
                        })
            
            logger.debug(f"Vector search returned {len(results)} results")
            return results
            
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def clear_memory_by_type(self, memory_type: str) -> bool:
        """Clear all memory of a specific type."""
        try:
            prefix = self.memory_types.get(memory_type, f"{memory_type}_")
            
            if self.redis_client:
                # Get all keys with prefix
                keys = self.redis_client.keys(f"{prefix}*")
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"Cleared {len(keys)} {memory_type} memory entries from Redis")
            else:
                # Clear from fallback
                keys_to_remove = [k for k in self.memory_store.keys() if k.startswith(prefix)]
                for key in keys_to_remove:
                    del self.memory_store[key]
                logger.info(f"Cleared {len(keys_to_remove)} {memory_type} memory entries from fallback")
            
            return True
            
        except Exception as e:
            self.metrics["errors"] += 1
            logger.error(f"Failed to clear {memory_type} memory: {e}")
            return False
    
    async def search_memory(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memory by simple key matching."""
        try:
            results = []
            
            if self.redis_client:
                keys = self.redis_client.keys(f"*{query}*")
                for key in keys[:limit]:
                    data = self.redis_client.get(key)
                    if data:
                        results.append(json.loads(data))
            else:
                for key in self.memory_store.keys():
                    if query in key:
                        results.append(self.memory_store[key])
                        if len(results) >= limit:
                            break
            
            logger.debug(f"Memory search for '{query}' found {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Memory search failed for '{query}': {e}")
            return []
    
    async def clear_memory(self, pattern: str = "*") -> bool:
        """Clear memory keys matching pattern."""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            else:
                keys_to_remove = [k for k in self.memory_store.keys() if pattern in k]
                for key in keys_to_remove:
                    del self.memory_store[key]
            
            logger.info(f"Cleared memory keys matching pattern: {pattern}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear memory pattern '{pattern}': {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of the memory system."""
        start_time = time.time()
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        try:
            # Check Redis connection
            if self.redis_client:
                try:
                    redis_start = time.time()
                    self.redis_client.ping()
                    redis_time = time.time() - redis_start
                    health_status["checks"]["redis"] = {
                        "status": "healthy",
                        "response_time": f"{redis_time:.3f}s",
                        "type": "direct_connection"
                    }
                except Exception as e:
                    health_status["checks"]["redis"] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
                    health_status["status"] = "degraded"
            else:
                health_status["checks"]["redis"] = {
                    "status": "not_available",
                    "fallback": "in_memory"
                }
            
            # Check fallback memory
            if self.memory_store is not None:
                try:
                    test_key = "health_check_test"
                    test_value = {"test": True, "timestamp": datetime.now().isoformat()}
                    self.memory_store[test_key] = test_value
                    retrieved = self.memory_store.get(test_key)
                    del self.memory_store[test_key]
                    
                    if retrieved and retrieved.get("test"):
                        health_status["checks"]["fallback_memory"] = {
                            "status": "healthy",
                            "type": "in_memory"
                        }
                    else:
                        health_status["checks"]["fallback_memory"] = {
                            "status": "unhealthy",
                            "error": "Failed to retrieve test data"
                        }
                        health_status["status"] = "unhealthy"
                except Exception as e:
                    health_status["checks"]["fallback_memory"] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
                    health_status["status"] = "unhealthy"
            
            # Performance check
            if self.metrics["operation_times"]:
                avg_time = sum(self.metrics["operation_times"]) / len(self.metrics["operation_times"])
                max_time = max(self.metrics["operation_times"])
                min_time = min(self.metrics["operation_times"])
                
                health_status["checks"]["performance"] = {
                    "status": "healthy" if avg_time < 0.1 else "degraded",
                    "avg_operation_time": f"{avg_time:.3f}s",
                    "max_operation_time": f"{max_time:.3f}s",
                    "min_operation_time": f"{min_time:.3f}s",
                    "total_operations": len(self.metrics["operation_times"])
                }
                
                if avg_time > 0.5:
                    health_status["status"] = "degraded"
            else:
                health_status["checks"]["performance"] = {
                    "status": "unknown",
                    "message": "No operations recorded yet"
                }
            
            # Error rate check
            total_ops = self.metrics["total_operations"]
            if total_ops > 0:
                error_rate = (self.metrics["errors"] / total_ops) * 100
                health_status["checks"]["error_rate"] = {
                    "status": "healthy" if error_rate < 5 else "degraded",
                    "error_rate": f"{error_rate:.2f}%",
                    "total_errors": self.metrics["errors"],
                    "total_operations": total_ops
                }
                
                if error_rate > 10:
                    health_status["status"] = "unhealthy"
            
            # Update metrics
            self.metrics["last_health_check"] = datetime.now().isoformat()
            self.metrics["health_status"] = health_status["status"]
            
            health_status["check_duration"] = f"{time.time() - start_time:.3f}s"
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            logger.error(f"Memory health check failed: {e}")
        
        return health_status
    
    def _start_cleanup_task(self):
        """Start background cleanup task."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                self._cleanup_task = asyncio.create_task(self._cleanup_loop())
                logger.info("Memory cleanup task started")
        except Exception as e:
            logger.error(f"Failed to start cleanup task: {e}")
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_config["cleanup_interval"])
                await self._perform_intelligent_cleanup()
            except asyncio.CancelledError:
                logger.info("Memory cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    async def _perform_intelligent_cleanup(self):
        """Perform intelligent memory cleanup based on current usage."""
        start_time = time.time()
        
        try:
            # Get current memory stats
            memory_stats = self.get_memory_stats()
            usage_percentage = memory_stats.get("usage_percentage", 0)
            
            # Determine cleanup level based on memory pressure
            if usage_percentage >= self.memory_thresholds["emergency"]:
                cleanup_level = "emergency"
            elif usage_percentage >= self.memory_thresholds["critical"]:
                cleanup_level = "critical"
            elif usage_percentage >= self.memory_thresholds["warning"]:
                cleanup_level = "warning"
            else:
                cleanup_level = "maintenance"
            
            # Perform cleanup operations
            cleanup_results = []
            
            if cleanup_level in ["emergency", "critical", "warning"]:
                # Clean expired cache items
                cache_result = await self._cleanup_expired_cache()
                cleanup_results.append(cache_result)
                
                # Clean old working memory
                working_result = await self._cleanup_old_working_memory()
                cleanup_results.append(working_result)
            
            if cleanup_level in ["emergency", "critical"]:
                # Clean old vector memory
                vector_result = await self._cleanup_old_vector_memory()
                cleanup_results.append(vector_result)
                
                # Force garbage collection
                gc_result = await self._force_garbage_collection()
                cleanup_results.append(gc_result)
                
                # Clean old BCM memory
                bcm_result = await self._cleanup_old_bcm_memory()
                cleanup_results.append(bcm_result)
            
            if cleanup_level == "emergency":
                # Emergency cleanup - clear all cache
                emergency_result = await self._emergency_cleanup()
                cleanup_results.append(emergency_result)
            
            # Update cleanup metrics
            total_items_cleaned = sum(r.items_cleaned for r in cleanup_results)
            total_memory_freed = sum(r.memory_freed_mb for r in cleanup_results)
            cleanup_duration = (time.time() - start_time) * 1000
            
            self.cleanup_metrics["total_cleanups"] += 1
            self.cleanup_metrics["items_cleaned"] += total_items_cleaned
            self.cleanup_metrics["memory_freed_mb"] += total_memory_freed
            self.cleanup_metrics["last_cleanup"] = datetime.now().isoformat()
            
            # Record cleanup operation
            cleanup_op = CleanupOperation(
                operation_type=f"intelligent_cleanup_{cleanup_level}",
                items_cleaned=total_items_cleaned,
                memory_freed_mb=total_memory_freed,
                duration_ms=cleanup_duration,
                success=True
            )
            self.cleanup_metrics["cleanup_history"].append(cleanup_op)
            
            logger.info(f"Intelligent cleanup completed: {cleanup_level}, "
                       f"items: {total_items_cleaned}, memory: {total_memory_freed:.1f}MB")
            
        except Exception as e:
            logger.error(f"Intelligent cleanup failed: {e}")
            
            # Record failed cleanup
            cleanup_op = CleanupOperation(
                operation_type="intelligent_cleanup_failed",
                items_cleaned=0,
                memory_freed_mb=0.0,
                duration_ms=(time.time() - start_time) * 1000,
                success=False,
                error_message=str(e)
            )
            self.cleanup_metrics["cleanup_history"].append(cleanup_op)
    
    async def _cleanup_expired_cache(self) -> CleanupOperation:
        """Clean expired cache items."""
        start_time = time.time()
        items_cleaned = 0
        memory_freed = 0.0
        
        try:
            if self.redis_client:
                # Clean Redis cache
                pattern = self.memory_types["cache"] + "*"
                keys = self.redis_client.keys(pattern)
                
                if keys:
                    # Check TTL for each key
                    expired_keys = []
                    for key in keys:
                        ttl = self.redis_client.ttl(key)
                        if ttl == -1:  # No expiration set, check age
                            # For simplicity, delete cache keys older than max age
                            expired_keys.append(key)
                        elif ttl == -2:  # Already expired
                            expired_keys.append(key)
                    
                    if expired_keys:
                        # Delete in batches
                        batch_size = self.cleanup_config["cleanup_batch_size"]
                        for i in range(0, len(expired_keys), batch_size):
                            batch = expired_keys[i:i + batch_size]
                            self.redis_client.delete(*batch)
                            items_cleaned += len(batch)
                        
                        memory_freed = items_cleaned * 0.1  # Estimate 0.1MB per item
            else:
                # Clean fallback cache
                cache_prefix = self.memory_types["cache"]
                keys_to_delete = []
                
                for key in list(self.memory_store.keys()):
                    if key.startswith(cache_prefix):
                        keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    del self.memory_store[key]
                    items_cleaned += 1
                
                memory_freed = items_cleaned * 0.05  # Estimate 0.05MB per item
            
            duration = (time.time() - start_time) * 1000
            return CleanupOperation(
                operation_type="cache_cleanup",
                items_cleaned=items_cleaned,
                memory_freed_mb=memory_freed,
                duration_ms=duration,
                success=True
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return CleanupOperation(
                operation_type="cache_cleanup",
                items_cleaned=0,
                memory_freed_mb=0.0,
                duration_ms=duration,
                success=False,
                error_message=str(e)
            )
    
    async def _cleanup_old_working_memory(self) -> CleanupOperation:
        """Clean old working memory items."""
        start_time = time.time()
        items_cleaned = 0
        memory_freed = 0.0
        
        try:
            cutoff_time = time.time() - self.cleanup_config["max_working_age"]
            
            if self.redis_client:
                # Clean Redis working memory
                pattern = self.memory_types["working"] + "*"
                keys = self.redis_client.keys(pattern)
                
                old_keys = []
                for key in keys:
                    # Get key creation time (simplified - using key name timestamp)
                    try:
                        key_parts = key.decode().split(":")
                        if len(key_parts) > 1:
                            timestamp = float(key_parts[-1])
                            if timestamp < cutoff_time:
                                old_keys.append(key)
                    except (ValueError, IndexError):
                        continue
                
                if old_keys:
                    batch_size = self.cleanup_config["cleanup_batch_size"]
                    for i in range(0, len(old_keys), batch_size):
                        batch = old_keys[i:i + batch_size]
                        self.redis_client.delete(*batch)
                        items_cleaned += len(batch)
                    
                    memory_freed = items_cleaned * 0.2  # Estimate 0.2MB per working memory item
            else:
                # Clean fallback working memory
                working_prefix = self.memory_types["working"]
                keys_to_delete = []
                
                for key in list(self.memory_store.keys()):
                    if key.startswith(working_prefix):
                        try:
                            key_parts = key.split(":")
                            if len(key_parts) > 1:
                                timestamp = float(key_parts[-1])
                                if timestamp < cutoff_time:
                                    keys_to_delete.append(key)
                        except (ValueError, IndexError):
                            continue
                
                for key in keys_to_delete:
                    del self.memory_store[key]
                    items_cleaned += 1
                
                memory_freed = items_cleaned * 0.1  # Estimate 0.1MB per item
            
            duration = (time.time() - start_time) * 1000
            return CleanupOperation(
                operation_type="working_memory_cleanup",
                items_cleaned=items_cleaned,
                memory_freed_mb=memory_freed,
                duration_ms=duration,
                success=True
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return CleanupOperation(
                operation_type="working_memory_cleanup",
                items_cleaned=0,
                memory_freed_mb=0.0,
                duration_ms=duration,
                success=False,
                error_message=str(e)
            )
    
    async def _cleanup_old_vector_memory(self) -> CleanupOperation:
        """Clean old vector memory items."""
        start_time = time.time()
        items_cleaned = 0
        memory_freed = 0.0
        
        try:
            # Vector memory cleanup is more conservative
            # Only clean very old items (older than 24 hours)
            cutoff_time = time.time() - (24 * 3600)
            
            if self.redis_client:
                pattern = self.memory_types["vector"] + "*"
                keys = self.redis_client.keys(pattern)
                
                old_keys = []
                for key in keys:
                    try:
                        key_parts = key.decode().split(":")
                        if len(key_parts) > 1:
                            timestamp = float(key_parts[-1])
                            if timestamp < cutoff_time:
                                old_keys.append(key)
                    except (ValueError, IndexError):
                        continue
                
                if old_keys:
                    # Delete in smaller batches for vector memory
                    batch_size = 50  # Smaller batches for vector data
                    for i in range(0, len(old_keys), batch_size):
                        batch = old_keys[i:i + batch_size]
                        self.redis_client.delete(*batch)
                        items_cleaned += len(batch)
                    
                    memory_freed = items_cleaned * 1.0  # Estimate 1MB per vector item
            else:
                # Similar logic for fallback storage
                vector_prefix = self.memory_types["vector"]
                keys_to_delete = []
                
                for key in list(self.memory_store.keys()):
                    if key.startswith(vector_prefix):
                        try:
                            key_parts = key.split(":")
                            if len(key_parts) > 1:
                                timestamp = float(key_parts[-1])
                                if timestamp < cutoff_time:
                                    keys_to_delete.append(key)
                        except (ValueError, IndexError):
                            continue
                
                for key in keys_to_delete:
                    del self.memory_store[key]
                    items_cleaned += 1
                
                memory_freed = items_cleaned * 0.5  # Estimate 0.5MB per vector item
            
            duration = (time.time() - start_time) * 1000
            return CleanupOperation(
                operation_type="vector_memory_cleanup",
                items_cleaned=items_cleaned,
                memory_freed_mb=memory_freed,
                duration_ms=duration,
                success=True
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return CleanupOperation(
                operation_type="vector_memory_cleanup",
                items_cleaned=0,
                memory_freed_mb=0.0,
                duration_ms=duration,
                success=False,
                error_message=str(e)
            )
    
    async def _force_garbage_collection(self) -> CleanupOperation:
        """Force Python garbage collection."""
        start_time = time.time()
        
        try:
            # Force garbage collection
            collected = gc.collect()
            
            # Get memory before and after GC
            process = psutil.Process()
            memory_before = process.memory_info().rss / (1024 * 1024)  # MB
            
            # Additional GC cycles
            gc.collect()
            gc.collect()
            
            memory_after = process.memory_info().rss / (1024 * 1024)  # MB
            memory_freed = max(0, memory_before - memory_after)
            
            duration = (time.time() - start_time) * 1000
            return CleanupOperation(
                operation_type="garbage_collection",
                items_cleaned=collected,
                memory_freed_mb=memory_freed,
                duration_ms=duration,
                success=True
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return CleanupOperation(
                operation_type="garbage_collection",
                items_cleaned=0,
                memory_freed_mb=0.0,
                duration_ms=duration,
                success=False,
                error_message=str(e)
            )
    
    async def _emergency_cleanup(self) -> CleanupOperation:
        """Emergency cleanup - clear all cache and old data."""
        start_time = time.time()
        items_cleaned = 0
        memory_freed = 0.0
        
        try:
            if self.redis_client:
                # Clear all cache
                cache_pattern = self.memory_types["cache"] + "*"
                cache_keys = self.redis_client.keys(cache_pattern)
                if cache_keys:
                    self.redis_client.delete(*cache_keys)
                    items_cleaned += len(cache_keys)
                
                # Clear old working memory (older than 5 minutes)
                working_pattern = self.memory_types["working"] + "*"
                working_keys = self.redis_client.keys(working_pattern)
                
                old_working_keys = []
                cutoff_time = time.time() - 300  # 5 minutes
                
                for key in working_keys:
                    try:
                        key_parts = key.decode().split(":")
                        if len(key_parts) > 1:
                            timestamp = float(key_parts[-1])
                            if timestamp < cutoff_time:
                                old_working_keys.append(key)
                    except (ValueError, IndexError):
                        continue
                
                if old_working_keys:
                    self.redis_client.delete(*old_working_keys)
                    items_cleaned += len(old_working_keys)
                
                memory_freed = items_cleaned * 0.3  # Estimate
            else:
                # Emergency cleanup for fallback storage
                keys_to_delete = []
                
                for key in list(self.memory_store.keys()):
                    if key.startswith(self.memory_types["cache"]):
                        keys_to_delete.append(key)
                    elif key.startswith(self.memory_types["working"]):
                        try:
                            key_parts = key.split(":")
                            if len(key_parts) > 1:
                                timestamp = float(key_parts[-1])
                                if timestamp < time.time() - 300:  # 5 minutes
                                    keys_to_delete.append(key)
                        except (ValueError, IndexError):
                            continue
                
                for key in keys_to_delete:
                    del self.memory_store[key]
                    items_cleaned += 1
                
                memory_freed = items_cleaned * 0.2  # Estimate
            
            duration = (time.time() - start_time) * 1000
            return CleanupOperation(
                operation_type="emergency_cleanup",
                items_cleaned=items_cleaned,
                memory_freed_mb=memory_freed,
                duration_ms=duration,
                success=True
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return CleanupOperation(
                operation_type="emergency_cleanup",
                items_cleaned=0,
                memory_freed_mb=0.0,
                duration_ms=duration,
                success=False,
                error_message=str(e)
            )
    
    async def _cleanup_old_bcm_memory(self) -> CleanupOperation:
        """Clean old BCM memory items."""
        start_time = time.time()
        items_cleaned = 0
        memory_freed = 0.0
        
        try:
            if self.redis_client:
                pattern = self.memory_types["bcm"] + "*"
                keys = self.redis_client.keys(pattern)
                
                # BCM items have their own TTL, we just need to enforce max age
                max_age = 30 * 86400  # 30 days max for any BCM
                old_keys = []
                
                for key in keys:
                    ttl = self.redis_client.ttl(key)
                    if ttl == -1:  # No TTL set, check creation time
                        created_at = self.redis_client.hget(key, "created_at")
                        if created_at:
                            created_time = datetime.fromisoformat(created_at.decode()).timestamp()
                            if time.time() - created_time > max_age:
                                old_keys.append(key)
                    elif ttl == -2:  # Already expired
                        old_keys.append(key)
            
                if old_keys:
                    batch_size = self.cleanup_config["cleanup_batch_size"]
                    for i in range(0, len(old_keys), batch_size):
                        batch = old_keys[i:i + batch_size]
                        self.redis_client.delete(*batch)
                        items_cleaned += len(batch)
                
                memory_freed = items_cleaned * 0.5  # Estimate 0.5MB per BCM
            else:
                # Fallback cleanup
                bcm_prefix = self.memory_types["bcm"]
                keys_to_delete = []
                max_age = 30 * 86400  # 30 days
                
                for key in list(self.memory_store.keys()):
                    if key.startswith(bcm_prefix):
                        item = self.memory_store[key]
                        created_at = item.get("timestamp")
                        if created_at:
                            try:
                                created_time = datetime.fromisoformat(created_at).timestamp()
                                if time.time() - created_time > max_age:
                                    keys_to_delete.append(key)
                            except (ValueError, TypeError):
                                continue
            
                for key in keys_to_delete:
                    del self.memory_store[key]
                    items_cleaned += 1
            
                memory_freed = items_cleaned * 0.3  # Estimate 0.3MB per BCM
        
            duration = (time.time() - start_time) * 1000
            return CleanupOperation(
                operation_type="bcm_cleanup",
                items_cleaned=items_cleaned,
                memory_freed_mb=memory_freed,
                duration_ms=duration,
                success=True
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return CleanupOperation(
                operation_type="bcm_cleanup",
                items_cleaned=0,
                memory_freed_mb=0.0,
                duration_ms=duration,
                success=False,
                error_message=str(e)
            )
    
    async def store_bcm(self, workspace_id: str, manifest: Dict[str, Any], tier: str = "tier0") -> bool:
        """Store BCM manifest with tier-based TTL."""
        try:
            if tier not in self.bcm_ttl_config:
                raise ValueError(f"Invalid BCM tier: {tier}")
            
            ttl = self.bcm_ttl_config[tier]
            key = f"{workspace_id}:{tier}"
            return await self.store_memory(
                key=key,
                value=manifest,
                ttl=ttl,
                memory_type="bcm"
            )
        except Exception as e:
            logger.error(f"Failed to store BCM: {e}")
            return False

    async def retrieve_bcm(self, workspace_id: str, tier: str = "tier0") -> Optional[Dict[str, Any]]:
        """Retrieve BCM manifest by workspace and tier."""
        try:
            key = f"{workspace_id}:{tier}"
            return await self.retrieve_memory(
                key=key,
                memory_type="bcm"
            )
        except Exception as e:
            logger.error(f"Failed to retrieve BCM: {e}")
            return None

    async def clear_bcm(self, workspace_id: str) -> bool:
        """Clear all BCM entries for a workspace."""
        try:
            # Clear all tiers
            for tier in self.bcm_ttl_config:
                key = f"{workspace_id}:{tier}"
                if self.redis_client:
                    self.redis_client.delete(f"{self.memory_types['bcm']}{key}")
                elif self.memory_store:
                    full_key = f"{self.memory_types['bcm']}{key}"
                    if full_key in self.memory_store:
                        del self.memory_store[full_key]
            return True
        except Exception as e:
            logger.error(f"Failed to clear BCM: {e}")
            return False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        try:
            # System memory stats
            memory = psutil.virtual_memory()
            process = psutil.Process()
            process_memory = process.memory_info().rss / (1024 * 1024)  # MB
            
            base_stats = {
                "system_memory": {
                    "total_mb": memory.total / (1024 * 1024),
                    "used_mb": memory.used / (1024 * 1024),
                    "available_mb": memory.available / (1024 * 1024),
                    "usage_percentage": memory.percent
                },
                "process_memory_mb": process_memory,
                "memory_types": list(self.memory_types.keys()),
                "total_operations": self.metrics["total_operations"],
                "redis_hits": self.metrics["redis_hits"],
                "fallback_hits": self.metrics["fallback_hits"],
                "errors": self.metrics["errors"],
                "redis_hit_rate": 0,
                "fallback_hit_rate": 0,
                "error_rate": 0
            }
            
            # Calculate rates
            total = self.metrics["total_operations"]
            if total > 0:
                base_stats["redis_hit_rate"] = (self.metrics["redis_hits"] / total) * 100
                base_stats["fallback_hit_rate"] = (self.metrics["fallback_hits"] / total) * 100
                base_stats["error_rate"] = (self.metrics["errors"] / total) * 100
            
            # Add cleanup metrics
            base_stats["cleanup_metrics"] = {
                "total_cleanups": self.cleanup_metrics["total_cleanups"],
                "items_cleaned": self.cleanup_metrics["items_cleaned"],
                "memory_freed_mb": self.cleanup_metrics["memory_freed_mb"],
                "last_cleanup": self.cleanup_metrics["last_cleanup"],
                "avg_cleanup_time_ms": 0,
                "cleanup_success_rate": 0
            }
            
            # Calculate cleanup success rate
            cleanup_history = list(self.cleanup_metrics["cleanup_history"])
            if cleanup_history:
                successful_cleanups = sum(1 for c in cleanup_history if c.success)
                base_stats["cleanup_metrics"]["cleanup_success_rate"] = (
                    successful_cleanups / len(cleanup_history) * 100
                )
                
                avg_duration = sum(c.duration_ms for c in cleanup_history) / len(cleanup_history)
                base_stats["cleanup_metrics"]["avg_cleanup_time_ms"] = avg_duration
            
            # Add Redis-specific stats
            if self.redis_client:
                try:
                    info = self.redis_client.info()
                    base_stats["redis"] = {
                        "type": "redis",
                        "memory_usage": info.get("used_memory_human", "Unknown"),
                        "connected_clients": info.get("connected_clients", 0),
                        "total_commands_processed": info.get("total_commands_processed", 0),
                        "keyspace_hits": info.get("keyspace_hits", 0),
                        "keyspace_misses": info.get("keyspace_misses", 0)
                    }
                except Exception as e:
                    base_stats["redis"] = {"error": str(e)}
            else:
                base_stats["redis"] = {"type": "fallback"}
            
            # Add health status
            base_stats["health"] = {
                "status": self.metrics.get("health_status", "unknown"),
                "last_check": self.metrics.get("last_health_check")
            }
            
            return base_stats
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {"error": str(e), "status": "error"}
    
    def get_cleanup_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get cleanup operation history."""
        history = list(self.cleanup_metrics["cleanup_history"])[-limit:]
        return [
            {
                "operation_type": op.operation_type,
                "items_cleaned": op.items_cleaned,
                "memory_freed_mb": op.memory_freed_mb,
                "duration_ms": op.duration_ms,
                "success": op.success,
                "error_message": op.error_message
            }
            for op in history
        ]
    
    async def manual_cleanup(self, cleanup_type: str = "standard") -> Dict[str, Any]:
        """Trigger manual cleanup."""
        logger.info(f"Manual cleanup triggered: {cleanup_type}")
        
        if cleanup_type == "cache_only":
            result = await self._cleanup_expired_cache()
        elif cleanup_type == "working_only":
            result = await self._cleanup_old_working_memory()
        elif cleanup_type == "vector_only":
            result = await self._cleanup_old_vector_memory()
        elif cleanup_type == "gc_only":
            result = await self._force_garbage_collection()
        elif cleanup_type == "emergency":
            result = await self._emergency_cleanup()
        else:
            # Standard cleanup
            await self._perform_intelligent_cleanup()
            return {"status": "completed", "type": "intelligent_cleanup"}
        
        return {
            "status": "completed",
            "type": cleanup_type,
            "items_cleaned": result.items_cleaned,
            "memory_freed_mb": result.memory_freed_mb,
            "duration_ms": result.duration_ms,
            "success": result.success
        }
    
    def stop_cleanup_task(self):
        """Stop the background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None
            logger.info("Memory cleanup task stopped")
    
    def __del__(self):
        """Cleanup when controller is destroyed."""
        self.stop_cleanup_task()


# Alias for backward compatibility
MemoryController = SimpleMemoryController


# Convenience function for backward compatibility
def get_memory_controller():
    """Get simplified memory controller instance."""
    return SimpleMemoryController()
