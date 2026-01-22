"""
Atomic operations for Redis.
Provides thread-safe operations using Redis atomic commands.
"""

import logging
from decimal import Decimal
from typing import Any, Optional, Union

from .client import RedisClient
from .lua_scripts import LuaScripts

logger = logging.getLogger(__name__)


class AtomicOperations:
    """Atomic operations using Redis commands and Lua scripts."""

    def __init__(self, redis_client: RedisClient = None):
        """Initialize atomic operations."""
        self.redis = redis_client or RedisClient()
        self.lua_scripts = LuaScripts()

    async def increment(self, key: str, amount: int = 1) -> int:
        """Atomically increment a key by the specified amount."""
        try:
            result = await self.redis.incrby(key, amount)
            logger.debug(f"Incremented {key} by {amount}, new value: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to increment {key}: {e}")
            raise

    async def decrement(self, key: str, amount: int = 1) -> int:
        """Atomically decrement a key by the specified amount."""
        try:
            result = await self.redis.decrby(key, amount)
            logger.debug(f"Decremented {key} by {amount}, new value: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to decrement {key}: {e}")
            raise

    async def increment_float(self, key: str, amount: float = 1.0) -> float:
        """Atomically increment a key by the specified float amount."""
        try:
            result = await self.redis.incrbyfloat(key, amount)
            logger.debug(f"Incremented {key} by {amount}, new value: {result}")
            return float(result)
        except Exception as e:
            logger.error(f"Failed to increment float {key}: {e}")
            raise

    async def compare_and_set(self, key: str, expected: Any, new_value: Any) -> bool:
        """Atomically set key if current value matches expected value."""
        try:
            # Use Lua script for atomic compare-and-set
            script = """
            local current = redis.call('GET', KEYS[1])
            if current == ARGV[1] then
                redis.call('SET', KEYS[1], ARGV[2])
                return 1
            else
                return 0
            end
            """

            # Convert values to strings for Redis
            expected_str = str(expected) if expected is not None else ""
            new_value_str = str(new_value) if new_value is not None else ""

            result = await self.redis.eval(script, 1, key, expected_str, new_value_str)
            success = bool(result)

            logger.debug(
                f"Compare-and-set {key}: expected={expected}, new={new_value}, success={success}"
            )
            return success

        except Exception as e:
            logger.error(f"Failed to compare-and-set {key}: {e}")
            raise

    async def get_and_set(self, key: str, new_value: Any) -> Any:
        """Atomically get current value and set new value."""
        try:
            # Use GETSET command for atomic get-and-set
            old_value = await self.redis.getset(key, str(new_value))

            # Parse old value based on type hints if possible
            if old_value is not None:
                try:
                    # Try to parse as JSON first
                    import json

                    return json.loads(old_value)
                except (json.JSONDecodeError, TypeError):
                    # Return as string if not valid JSON
                    return old_value

            logger.debug(
                f"Get-and-set {key}: new_value={new_value}, old_value={old_value}"
            )
            return old_value

        except Exception as e:
            logger.error(f"Failed to get-and-set {key}: {e}")
            raise

    async def atomic_add_to_set(self, key: str, member: str) -> bool:
        """Atomically add member to a set."""
        try:
            result = await self.redis.sadd(key, member)
            added = bool(result)
            logger.debug(f"Added {member} to set {key}: {added}")
            return added
        except Exception as e:
            logger.error(f"Failed to add to set {key}: {e}")
            raise

    async def atomic_remove_from_set(self, key: str, member: str) -> bool:
        """Atomically remove member from a set."""
        try:
            result = await self.redis.srem(key, member)
            removed = bool(result)
            logger.debug(f"Removed {member} from set {key}: {removed}")
            return removed
        except Exception as e:
            logger.error(f"Failed to remove from set {key}: {e}")
            raise

    async def atomic_add_to_list(self, key: str, *values: str) -> int:
        """Atomically add values to the end of a list."""
        try:
            result = await self.redis.rpush(key, *values)
            logger.debug(
                f"Added {len(values)} values to list {key}, new length: {result}"
            )
            return result
        except Exception as e:
            logger.error(f"Failed to add to list {key}: {e}")
            raise

    async def atomic_pop_from_list(
        self, key: str, direction: str = "right"
    ) -> Optional[str]:
        """Atomically pop value from list."""
        try:
            if direction == "left":
                result = await self.redis.lpop(key)
            else:
                result = await self.redis.rpop(key)

            logger.debug(f"Popped from {direction} of list {key}: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to pop from list {key}: {e}")
            raise

    async def atomic_list_length(self, key: str) -> int:
        """Atomically get list length."""
        try:
            result = await self.redis.llen(key)
            logger.debug(f"List {key} length: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to get list length {key}: {e}")
            raise

    async def atomic_hash_set(self, key: str, field: str, value: Any) -> bool:
        """Atomically set hash field."""
        try:
            result = await self.redis.hset(key, field, str(value))
            logger.debug(f"Set hash {key}[{field}] = {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to set hash field {key}[{field}]: {e}")
            raise

    async def atomic_hash_get(self, key: str, field: str) -> Optional[Any]:
        """Atomically get hash field."""
        try:
            result = await self.redis.hget(key, field)
            logger.debug(f"Got hash {key}[{field}] = {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to get hash field {key}[{field}]: {e}")
            raise

    async def atomic_hash_increment(self, key: str, field: str, amount: int = 1) -> int:
        """Atomically increment hash field."""
        try:
            result = await self.redis.hincrby(key, field, amount)
            logger.debug(
                f"Incremented hash {key}[{field}] by {amount}, new value: {result}"
            )
            return result
        except Exception as e:
            logger.error(f"Failed to increment hash field {key}[{field}]: {e}")
            raise

    async def atomic_hash_delete(self, key: str, *fields: str) -> int:
        """Atomically delete hash fields."""
        try:
            result = await self.redis.hdel(key, *fields)
            logger.debug(f"Deleted {result} fields from hash {key}")
            return result
        except Exception as e:
            logger.error(f"Failed to delete hash fields {key}: {e}")
            raise

    async def atomic_set_add_if_not_exists(self, key: str, member: str) -> bool:
        """Atomically add to set only if member doesn't exist."""
        try:
            result = await self.redis.sadd(key, member)
            added = bool(result)
            logger.debug(f"Added {member} to set {key} if not exists: {added}")
            return added
        except Exception as e:
            logger.error(f"Failed to add to set if not exists {key}: {e}")
            raise

    async def atomic_sorted_set_add(self, key: str, score: float, member: str) -> bool:
        """Atomically add member to sorted set."""
        try:
            result = await self.redis.zadd(key, {member: score})
            added = bool(result)
            logger.debug(
                f"Added {member} to sorted set {key} with score {score}: {added}"
            )
            return added
        except Exception as e:
            logger.error(f"Failed to add to sorted set {key}: {e}")
            raise

    async def atomic_sorted_set_increment_score(
        self, key: str, member: str, increment: float
    ) -> float:
        """Atomically increment member score in sorted set."""
        try:
            result = await self.redis.zincrby(key, increment, member)
            new_score = float(result)
            logger.debug(
                f"Incremented score for {member} in sorted set {key} by {increment}, new score: {new_score}"
            )
            return new_score
        except Exception as e:
            logger.error(f"Failed to increment sorted set score {key}: {e}")
            raise

    async def atomic_bit_set(self, key: str, offset: int, value: bool) -> bool:
        """Atomically set bit at offset."""
        try:
            result = await self.redis.setbit(key, offset, 1 if value else 0)
            old_value = bool(result)
            logger.debug(f"Set bit {key}[{offset}] = {value}, old value: {old_value}")
            return old_value
        except Exception as e:
            logger.error(f"Failed to set bit {key}[{offset}]: {e}")
            raise

    async def atomic_bit_get(self, key: str, offset: int) -> bool:
        """Atomically get bit at offset."""
        try:
            result = await self.redis.getbit(key, offset)
            bit_value = bool(result)
            logger.debug(f"Got bit {key}[{offset}] = {bit_value}")
            return bit_value
        except Exception as e:
            logger.error(f"Failed to get bit {key}[{offset}]: {e}")
            raise

    async def atomic_hyperloglog_add(self, key: str, *elements: str) -> bool:
        """Atomically add elements to HyperLogLog."""
        try:
            result = await self.redis.pfadd(key, *elements)
            added = bool(result)
            logger.debug(
                f"Added {len(elements)} elements to HyperLogLog {key}: {added}"
            )
            return added
        except Exception as e:
            logger.error(f"Failed to add to HyperLogLog {key}: {e}")
            raise

    async def atomic_hyperloglog_count(self, key: str) -> int:
        """Atomically get HyperLogLog cardinality."""
        try:
            result = await self.redis.pfcount(key)
            logger.debug(f"HyperLogLog {key} count: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to get HyperLogLog count {key}: {e}")
            raise

    async def atomic_publish_message(self, channel: str, message: str) -> int:
        """Atomically publish message to channel."""
        try:
            result = await self.redis.publish(channel, message)
            subscribers = result
            logger.debug(
                f"Published message to {channel}, reached {subscribers} subscribers"
            )
            return subscribers
        except Exception as e:
            logger.error(f"Failed to publish message to {channel}: {e}")
            raise

    async def atomic_expire_if_exists(self, key: str, seconds: int) -> bool:
        """Atomically set expiry only if key exists."""
        try:
            result = await self.redis.expire(key, seconds)
            logger.debug(f"Set expiry for {key} to {seconds}s: {bool(result)}")
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to set expiry for {key}: {e}")
            raise

    async def atomic_rename_if_new(self, old_key: str, new_key: str) -> bool:
        """Atomically rename key only if new key doesn't exist."""
        try:
            result = await self.redis.renamenx(old_key, new_key)
            renamed = bool(result)
            logger.debug(f"Renamed {old_key} to {new_key}: {renamed}")
            return renamed
        except Exception as e:
            logger.error(f"Failed to rename {old_key} to {new_key}: {e}")
            raise

    async def atomic_get_multiple_keys(self, *keys: str) -> list:
        """Atomically get multiple keys."""
        try:
            result = await self.redis.mget(*keys)
            logger.debug(f"Got {len(keys)} keys atomically")
            return result
        except Exception as e:
            logger.error(f"Failed to get multiple keys: {e}")
            raise

    async def atomic_set_multiple_keys(self, mapping: dict, expire: int = None) -> bool:
        """Atomically set multiple keys using MSET."""
        try:
            # Convert all values to strings
            string_mapping = {k: str(v) for k, v in mapping.items()}

            if expire:
                # Use pipeline for setting with expiry
                pipe = self.redis.pipeline()
                pipe.mset(string_mapping)
                for key in mapping.keys():
                    pipe.expire(key, expire)
                await pipe.execute()
            else:
                await self.redis.mset(string_mapping)

            logger.debug(f"Set {len(mapping)} keys atomically")
            return True
        except Exception as e:
            logger.error(f"Failed to set multiple keys: {e}")
            raise


# Global atomic operations instance
_atomic_ops: AtomicOperations = None


def get_atomic_operations(redis_client: RedisClient = None) -> AtomicOperations:
    """Get the global atomic operations instance."""
    global _atomic_ops
    if _atomic_ops is None or redis_client:
        _atomic_ops = AtomicOperations(redis_client)
    return _atomic_ops
