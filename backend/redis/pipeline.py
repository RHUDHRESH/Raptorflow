"""
Redis pipeline operations for batch processing.

Provides atomic operations and reduced round trips for improved performance.
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .client import get_redis


@dataclass
class RedisOp:
    """Individual Redis operation for pipeline execution."""
    operation: str  # "set", "get", "delete", "expire", etc.
    key: str
    value: Optional[Any] = None
    ex: Optional[int] = None
    px: Optional[int] = None
    nx: bool = False
    xx: bool = False
    return_key: Optional[str] = None


@dataclass
class PipelineResult:
    """Result of pipeline execution."""
    success_count: int
    error_count: int
    results: List[Any]
    errors: List[str]
    execution_time_ms: float


class RedisPipeline:
    """Redis pipeline for batching operations."""

    def __init__(self):
        self.redis = get_redis()
        self.operations: List[RedisOp] = []
        self._return_keys: List[str] = []

    def add_set(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = None,
        px: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
        return_key: bool = False
    ) -> "RedisPipeline":
        """Add SET operation to pipeline."""
        op = RedisOp(
            operation="set",
            key=key,
            value=value,
            ex=ex,
            px=px,
            nx=nx,
            xx=xx
        )
        self.operations.append(op)

        if return_key:
            self._return_keys.append(key)

        return self

    def add_get(
        self,
        key: str,
        return_key: bool = False
    ) -> "RedisPipeline":
        """Add GET operation to pipeline."""
        op = RedisOp(operation="get", key=key)
        self.operations.append(op)

        if return_key:
            self._return_keys.append(key)

        return self

    def add_delete(
        self,
        key: str,
        return_key: bool = False
    ) -> "RedisPipeline":
        """Add DELETE operation to pipeline."""
        op = RedisOp(operation="delete", key=key)
        self.operations.append(op)

        if return_key:
            self._return_keys.append(key)

        return self

    def add_exists(
        self,
        key: str,
        return_key: bool = False
    ) -> "RedisPipeline":
        """Add EXISTS operation to pipeline."""
        op = RedisOp(operation="exists", key=key)
        self.operations.append(op)

        if return_key:
            self._return_keys.append(key)

        return self

    def add_expire(
        self,
        key: str,
        seconds: int,
        return_key: bool = False
    ) -> "RedisPipeline":
        """Add EXPIRE operation to pipeline."""
        op = RedisOp(operation="expire", key=key, ex=seconds)
        self.operations.append(op)

        return self

    def add_incr(
        self,
        key: str,
        amount: int = 1,
        return_key: bool = False
    ) -> "RedisPipeline:
        """Add INCR operation to pipeline."""
        op = RedisOp(operation="incr", key=key, value=amount)
        self.operations.append(op)

        if return_key:
            self._return_keys.append(key)

        return self

    def add_decr(
        self,
        key: str,
        amount: int = 1,
        return_key: bool = False
    ) -> "RedisPipeline":
        """Add DECR operation to pipeline."""
        op = RedisOp(operation="decr", key=key, value=amount)
        self.operations.append(op)

        if return_key:
            self._return_keys.append(key)

        return self

    def add_hset(
        self,
        key: str,
        field: str,
        value: str,
        return_key: bool = False
    ) -> "RedisPipeline":
        """Add HSET operation to pipeline."""
        op = RedisOp(operation="hset", key=key, value={field: value})
        self.operations.append(op)

        return self

    def add_hget(
        self,
        key: str,
        field: str,
        return_key: bool = False
    ) -> "RedisRedisPipeline":
        """Add HGET operation to pipeline."""
        op = RedisOp(operation="hget", key=key, value=field)
        self.operations.append(op)

        if return_key:
            self._return_keys.append(key)

        return self

    def add_hgetall(
        self,
        key: str,
        return_key: bool = False
    ) -> "RedisRedisPipeline":
        """Add HGETALL operation to pipeline."""
        op = RedisOp(operation="hgetall", key=key)
        self.operations.append(op)

        if return_key:
            self._return_keys.append(key)

        return self

    def add_lpush(
        self,
        key: str,
        *values: str,
        return_key: bool = False
    ) -> "RedisPipeline":
        """Add LPUSH operation to pipeline."""
        op = RedisOp(operation="lpush", key=key, value=list(values))
        self.operations.append(op)

        return self

    def add_rpush(
        self,
        key: str,
        *values: str,
        return_key: bool = False
    ) -> "RedisPipeline":
        """Add RPUSH operation to pipeline."""
        op = Op(operation="rpush", key=key, value=list(values))
        self.operations.append(op)

        return self

    def add_lpop(
        self,
        key: str,
        return_key: bool = False
    ) -> "RedisPipeline":
        """Add LPOP operation to pipeline."""
        op = RedisOp(operation="lpop", key=key)
        self.operations.append(op)

        if return_key:
            self._return_keys.append(key)

        return self

    def add_rpop(
        self,
        key: str,
        return_key: bool = False
    ) -> "RedisPipeline":
        """Add RPOP operation to pipeline."""
        op = RedisOp(operation="rpop", key=key)
        self.operations.append(op)

        if return_key:
            self._return_keys.append(key)

        return self

    def add_lrange(
        self,
        key: str,
        start: int,
        end: int,
        return_key: bool = False
    ) -> "RedisPipeline":
        """Add LRANGE operation to pipeline."""
        op = RedisOp(operation="lrange", key=key, value=[start, end])
        self.operations.append(op)

        return self

    def add_llen(
        self,
        key: str,
        return_key: bool = False
    ) -> "RedisPipeline":
        """Add LLEN operation to pipeline."""
        op = RedisOp(operation="llen", key=key)
        self.operations.append(op)

        if return_key:
            self._return_keys.append(key)

        return self

    def clear(self) -> "RedisPipeline":
        """Clear all operations from pipeline."""
        self.operations.clear()
        self._return_keys.clear()
        return self

    def count(self) -> int:
        """Get number of operations in pipeline."""
        return len(self.operations)

    def is_empty(self) -> bool:
        """Check if pipeline is empty."""
        return len(self.operations) == 0

    async def execute(self) -> PipelineResult:
        """Execute all operations in pipeline."""
        if not self.operations:
            return PipelineResult(
                success_count=0,
                error_count=0,
                results=[],
                errors=[],
                execution_time_ms=0.0
            )

        start_time = datetime.now()

        try:
            # Convert operations to Redis pipeline format
            pipeline_ops = []
            for op in self.operations:
                if op.operation == "set":
                    pipeline_ops.append(
                        ("SET", op.key, op.value, op.ex, op.px, op.nx, op.xx)
                    )
                elif op.operation == "get":
                    pipeline_ops.append(("GET", op.key))
                elif op.operation == "delete":
                    pipeline_ops.append(("DEL", op.key))
                elif op.operation == "exists":
                    pipeline_ops.append(("EXISTS", op.key))
                elif op.operation == "expire":
                    pipeline_ops.append(("EXPIRE", op.key, op.ex))
                elif op.operation == "incr":
                    pipeline_ops.append(("INCR", op.key, op.value))
                elif op.operation == "decr":
                    pipeline_ops.append(("DECR", op.key, op.value))
                elif op.operation == "hset":
                    pipeline_ops.append(("HSET", op.key, op.value))
                elif op.operation == "hget":
                    pipeline_ops.append(("HGET", op.key, op.value))
                elif op.operation == "hgetall":
                    pipeline_ops.append(("HGETALL", op.key))
                elif op.operation == "lpush":
                    pipeline_ops.append(("LPUSH", op.key, op.value))
                elif op.operation == "rpush":
                    pipeline_ops.append(("RPUSH", op.key, op.value))
                elif op.operation == "lpop":
                    pipeline_ops.append(("LPOP", op.key))
                elif op.operation == "rpop":
                    pipeline_ops.append(("RPOP", op.key))
                elif op.operation == "lrange":
                    pipeline_ops.append(("LRANGE", op.key, op.value))
                elif op.operation == "llen":
                    pipeline_ops.append(("LLEN", op.key))

            # Execute pipeline
            results = await self.redis.async_client.pipeline(pipeline_ops)

            # Process results
            success_count = 0
            error_count = 0
            processed_results = []
            errors = []

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    errors.append(f"Operation {i}: {str(result)}")
                    error_count += 1
                else:
                    processed_results.append(result)
                    success_count += 1

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return PipelineResult(
                success_count=success_count,
                error_count=error_count,
                results=processed_results,
                errors=errors,
                execution_time_ms=execution_time
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return PipelineResult(
                success_count=0,
                error_count=len(self.operations),
                results=[],
                errors=[str(e)],
                execution_time_ms=execution_time
            )
        finally:
            # Clear operations after execution
            self.clear()

    async def execute_transaction(self, operations: List[RedisOp]) -> PipelineResult:
        """Execute operations as a transaction."""
        # Add MULTI/EXEC for transaction
        self.operations = operations.copy()

        # Add MULTI at start
        self.operations.insert(0, RedisOp(operation="MULTI"))

        # Add EXEC at end
        self.operations.append(RedisOp(operation="EXEC"))

        return await self.execute()

    async def batch_get(
        self,
        keys: List[str]
    ) -> Dict[str, Any]:
        """Batch GET operations for multiple keys."""
        pipeline = RedisPipeline()

        for key in keys:
            pipeline.add_get(key, return_key=True)

        result = await pipeline.execute()

        # Map results back to keys
        if result.success_count == len(keys):
            return dict(zip(keys, result.results))
        else:
            # Partial success - return what we can
            partial_results = {}
            for i, key in enumerate(keys):
                if i < len(result.results):
                    partial_results[key] = result.results[i]
            return partial_results

    async def batch_set(
        self,
        items: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> int:
        """Batch SET operations for multiple key-value pairs."""
        pipeline = RedisPipeline()

        for key, value in items.items():
            pipeline.add_set(key, value, ttl=ttl)

        result = await pipeline.execute()
        return result.success_count

    async def batch_delete(
        self,
        keys: List[str]
    ) -> int:
        """Batch DELETE operations for multiple keys."""
        pipeline = RedisPipeline()

        for key in keys:
            pipeline.add_delete(key)

        result = await pipeline.execute()
        return result.success_count

    async def batch_exists(
        self,
        keys: List[str]
    ) -> Dict[str, bool]:
        """Batch EXISTS operations for multiple keys."""
        pipeline = RedisPipeline()

        for key in keys:
            pipeline.add_exists(key, return_key=True)

        result = await pipeline.execute()

        # Map results back to keys
        if result.success_count == len(keys):
            return dict(zip(keys, [bool(r) for r in result.results]))
        else:
            # Partial success - return what we can
            partial_results = {}
            for i, key in enumerate(keys):
                if i < len(result.results):
                    partial_results[key] = bool(result.results[i])
            return partial_results

    async def atomic_increment(
        self,
        key: str,
        amount: int = 1,
        ttl: Optional[int] = None
    ) -> int:
        """Atomically increment a counter."""
        pipeline = RedisPipeline()
        pipeline.add_incr(key, amount, return_key=True)

        if ttl:
            pipeline.add_expire(key, ttl)

        result = await pipeline.execute()

        return result.results[0] if result.success_count > 0 else 0

    async def atomic_decrement(
        self,
        key: str,
        amount: int = 1,
        ttl: Optional[int] = None
    ) -> int:
        """Atomically decrement a counter."""
        pipeline = RedisPipeline()
        pipeline.add_decr(key, amount, return_key=True)

        if ttl:
            pipeline.add_expire(key, ttl)

        result = await pipeline.execute()

        return result.results[0] if result.success_count > 0 else 0

    async def compare_and_set(
        self,
        key: str,
        expected: Any,
        new_value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Compare and set atomically (CAS)."""
        pipeline = RedisPipeline()

        # First check if key exists and has expected value
        pipeline.add_get(key, return_key=True)

        # Use Lua script for atomic compare-and-set
        lua_script = """
        local current = redis.call('GET', KEYS[1])
        if current == ARGV[1] then
            return redis.call('SET', KEYS[1], ARGV[2], ARGV[3])
        end
        return current
        """

        # Add Lua script execution
        pipeline.operations.clear()
        pipeline.operations.append(RedisOp(
            operation="eval",
            key="lua",
            value=lua_script,
            keys=[key, str(expected), str(new_value), str(ttl or "")]
        ))

        result = await pipeline.execute()

        return result.results[0] == expected

    async def get_and_set(
        self,
        key: str,
        new_value: Any,
        ttl: Optional[int] = None
    ) -> Any:
        """Get current value and set new value atomically."""
        pipeline = RedisPipeline()

        # Get current value
        pipeline.add_get(key, return_key=True)

        # Set new value
        pipeline.add_set(key, new_value, ttl=ttl)

        result = await pipeline.execute()

        # Return original value
        return result.results[0]

    async def queue_push(
        self,
        queue_name: str,
        *items: str,
        ttl: Optional[int] = None
    ) -> int:
        """Push items to queue."""
        key = f"queue:{queue_name}"

        pipeline = RedisPipeline()
        for item in items:
            pipeline.add_lpush(key, item)

        if ttl:
            pipeline.add_expire(key, ttl)

        result = await pipeline.execute()
        return result.results[0] if result.success_count > 0 else 0

    async def queue_pop(
        self,
        queue_name: str,
        timeout: Optional[int] = None
    ) -> Optional[str]:
        """Pop item from queue."""
        key = f"queue:{queue_name}"

        pipeline = RedisPipeline()
        pipeline.add_lpop(key)

        result = await pipeline.execute()

        return result.results[0] if result.success_count > 0 else None

    async def queue_peek(
        self,
        queue_name: str
    ) -> Optional[List[str]]:
        """Peek at queue items without removing them."""
        key = f"queue:{queue_name}"

        pipeline = RedisPipeline()
        pipeline.add_lrange(key, 0, -1)

        result = await pipeline.execute()

        return result.results[0] if result.success_count > 0 else []

    async def queue_length(
        self,
        queue_name: str
    ) -> int:
        """Get queue length."""
        key = f"queue:{queue_name}"

        pipeline = RedisPipeline()
        pipeline.add_llen(key)

        result = await pipeline.execute()

        return result.results[0] if result.success_count > 0 else 0

    async def queue_clear(
        self,
        queue_name: str
    ) -> int:
        """Clear all items from queue."""
        key = f"queue:{queue_name}"

        pipeline = RedisPipeline()
        pipeline.add_delete(key)

        result = await pipeline.execute()
        return result.success_count

    async def hash_set_multiple(
        self,
        key: str,
        mapping: Dict[str, str],
        ttl: Optional[int] = None
    ) -> int:
        """Set multiple hash fields in a single operation."""
        pipeline = RedisPipeline()

        for field, value in mapping.items():
            pipeline.add_hset(key, field, value)

        if ttl:
            pipeline.add_expire(key, ttl)

        result = await pipeline.execute()
        return result.success_count

    async def hash_get_multiple(
        self,
        key: str,
        fields: List[str]
    ) -> Dict[str, str]:
        """Get multiple hash fields."""
        pipeline = RedisPipeline()

        for field in fields:
            pipeline.add_hget(key, field, return_key=True)

        result = await pipeline.execute()

        if result.success_count == len(fields):
            return dict(zip(fields, result.results))
        else:
            # Partial success
            partial_results = {}
            for i, field in enumerate(fields):
                if i < len(result.results):
                    partial_results[field] = result.results[i]
            return partial_results

    async def hash_delete_multiple(
        self,
        key: str,
        *fields: str
    ) -> int:
        """Delete multiple hash fields."""
        pipeline = RedisPipeline()

        for field in fields:
            pipeline.add_hdel(key, field)

        result = await pipeline.execute()
        return result.success_count

    async def get_memory_usage(self) -> Dict[str, Any]:
        """Get Redis memory usage statistics."""
        try:
            info = await self.redis.async_client.info()
            return {
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "total_system_memory": info.get("total_system_memory", 0),
                "total_system_memory_human": info.get("total_system_memory_human", "0B"),
                "redis_version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "peak_memory": info.get("used_memory_peak", 0)
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_connection_info(self) -> Dict[str, Any]:
        """Get Redis connection information."""
        try:
            info = await self.redis.async_client.info()
            return {
                "redis_version": info.get("redis_version", "unknown"),
                "mode": info.get("mode", "standalone"),
                "os": info.get("os", "unknown"),
                "arch_bits": info.get("arch_bits", "unknown"),
                "process_id": info.get("process_id", "unknown"),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec", 0)
            }
        except Exception as e:
            return {"error": str(e)}

    def get_operation_count(self) -> int:
        """Get number of operations in current pipeline."""
        return len(self.operations)

    def get_return_keys(self) -> List[str]:
        """Get list of keys that will be returned."""
        return self._return_keys.copy()


# Utility functions for common pipeline patterns
async def batch_cache_operations(
    operations: List[Dict[str, Any]],
    workspace_id: str,
    ttl: int = 3600
) -> Dict[str, Any]:
    """Batch cache operations."""
    cache_service = CacheService()

    # Separate operations by type
    get_ops = []
    set_ops = []

    for op in operations:
        if "get" in op:
            get_ops.append(op)
        elif "set" in op:
            set_ops.append(op)

    # Execute GET operations
    if get_ops:
        pipeline = RedisPipeline()
        for op in get_ops:
            pipeline.add_get(f"cache:{workspace_id}:{op['key']}", return_key=True)

        get_results = await pipeline.execute()

        # Map results back
        for op in get_ops:
            if op.get("key") in get_results.results:
                op["result"] = get_results.results[op["key"]]

    # Execute SET operations
    if set_ops:
        pipeline = RedisPipeline()
        for op in set_ops:
            pipeline.add_set(f"cache:{workspace_id}:{op['key']}", op["value"], ttl)

        set_results = await pipeline.execute()

        # Map results back
        for op in set_ops:
            op["success"] = set_results.success_count > 0

    return {"get_results": get_ops, "set_results": set_ops}


async def queue_batch_operations(
    queue_name: str,
    operations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Batch queue operations."""
    pipeline = RedisPipeline()

    for op in operations:
        op_type = op.get("type", "push")

        if op_type == "push":
            pipeline.add_lpush(f"queue:{queue_name}", op.get("item", ""))
        elif op_type == "pop":
            pipeline.add_lpop(f"queue:{queue_name}")
        elif op_type == "peek":
            pipeline.add_lrange(f"queue:{queue_name}", 0, -1)
        elif op_type == "length":
            pipeline.add_llen(f"queue:{queue_name}")
        elif op_type == "clear":
            pipeline.add_delete(f"queue:{queue_name}")

    return await pipeline.execute()


# Context manager for pipeline operations
class RedisPipelineContext:
    """Context manager for Redis pipeline operations."""

    def __init__(self):
        self.pipeline = RedisPipeline()

    def __enter__(self):
        return self.pipeline

    async def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            # Execute pipeline normally
            await self.pipeline.execute()
        return False

    def add_operation(self, operation: RedisOp) -> "RedisPipeline":
        """Add operation to pipeline."""
        return self.pipeline.add_operation(operation)

    async def execute(self) -> PipelineResult:
        """Execute pipeline and return results."""
        return await self.pipeline.execute()


# Global pipeline instance
_pipeline = RedisPipeline()


def get_pipeline() -> RedisPipeline:
    """Get global pipeline instance."""
    return _pipeline


def create_pipeline() -> RedisPipeline:
    """Create new pipeline instance."""
    return RedisPipeline()


# Decorator for pipeline operations
def pipeline_operation(
    *operations: RedisOp,
    return_key: bool = False
):
    """Decorator to wrap function in pipeline operations."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            pipeline = RedisPipeline()

            # Add all operations
            for op in operations:
                pipeline.add_operation(op, return_key)

            # Execute pipeline
            result = await pipeline.execute()

            # Return results if requested
            if return_key and result.success_count > 0:
                return result.results[0]
            elif result.success_count > 0:
                return result.results
            else:
                return None

        return wrapper
    return decorator
