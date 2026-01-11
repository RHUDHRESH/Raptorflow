"""
Redis Lua scripts for atomic operations.

Provides pre-compiled Lua scripts for complex atomic operations
that cannot be achieved with individual Redis commands.
"""

from typing import Any, Dict, List, Optional

from .client import get_redis


class LuaScriptManager:
    """Manages Redis Lua scripts for atomic operations."""

    def __init__(self):
        self.redis = get_redis()
        self.scripts: Dict[str, str] = {}
        self.sha_cache: Dict[str, str] = {}

        # Register all scripts
        self._register_scripts()

    def _register_scripts(self):
        """Register all Lua scripts."""

        # Sliding window rate limiting
        self.scripts[
            "RATE_LIMIT_SCRIPT"
        ] = """
        -- Sliding window rate limiting
        -- KEYS[1]: rate limit key
        -- ARGV[1]: window size in seconds
        -- ARGV[2]: max requests
        -- ARGV[3]: current timestamp
        -- ARGV[4]: request count (usually 1)

        local key = KEYS[1]
        local window = tonumber(ARGV[1])
        local max_requests = tonumber(ARGV[2])
        local current_time = tonumber(ARGV[3])
        local request_count = tonumber(ARGV[4])

        -- Remove expired entries
        local cutoff_time = current_time - window
        redis.call('ZREMRANGEBYSCORE', key, 0, cutoff_time)

        -- Count current requests
        local current_requests = redis.call('ZCARD', key)

        -- Check if under limit
        if current_requests < max_requests then
            -- Add current request
            redis.call('ZADD', key, current_time, current_time)
            redis.call('EXPIRE', key, window)
            return {1, max_requests - current_requests - 1}
        else
            -- Over limit
            return {0, 0}
        end
        """

        # Atomic queue dequeue
        self.scripts[
            "QUEUE_DEQUEUE_SCRIPT"
        ] = """
        -- Atomic queue dequeue with priority support
        -- KEYS[1]: queue key
        -- KEYS[2]: processing key
        -- ARGV[1]: current timestamp
        -- ARGV[2]: processing timeout
        -- ARGV[3]: max items to dequeue

        local queue_key = KEYS[1]
        local processing_key = KEYS[2]
        local current_time = tonumber(ARGV[1])
        local timeout = tonumber(ARGV[2])
        local max_items = tonumber(ARGV[3])

        -- Move expired items back to queue
        local expired_items = redis.call('ZRANGEBYSCORE', processing_key, 0, current_time - timeout)
        if #expired_items > 0 then
            for i, item in ipairs(expired_items) do
                local item_data = redis.call('HGET', processing_key, item)
                if item_data then
                    redis.call('LPUSH', queue_key, item_data)
                    redis.call('HDEL', processing_key, item)
                end
            end
        end

        -- Dequeue items
        local dequeued = {}
        local count = 0

        while count < max_items and redis.call('LLEN', queue_key) > 0 do
            local item = redis.call('LPOP', queue_key)
            if item then
                -- Add to processing queue with timestamp
                local item_id = current_time .. '_' .. count
                redis.call('HSET', processing_key, item_id, item)
                redis.call('ZADD', processing_key, current_time, item_id)
                redis.call('EXPIRE', processing_key, timeout)

                table.insert(dequeued, item)
                count = count + 1
            end
        end

        return dequeued
        """

        # Distributed lock with retry
        self.scripts[
            "DISTRIBUTED_LOCK_SCRIPT"
        ] = """
        -- Distributed lock with automatic expiration
        -- KEYS[1]: lock key
        -- ARGV[1]: lock value (unique identifier)
        -- ARGV[2]: expiration time in seconds
        -- ARGV[3]: current timestamp

        local lock_key = KEYS[1]
        local lock_value = ARGV[1]
        local expiration = tonumber(ARGV[2])
        local current_time = tonumber(ARGV[3])

        -- Check if lock exists and is expired
        local existing_value = redis.call('GET', lock_key)
        if existing_value then
            local parts = {}
            for part in string.gmatch(existing_value, "[^:]+") do
                table.insert(parts, part)
            end

            if #parts >= 2 then
                local lock_timestamp = tonumber(parts[2])
                if current_time - lock_timestamp < expiration then
                    -- Lock is still valid
                    return {0, existing_value}
                end
            end
        end

        -- Acquire lock
        local new_value = lock_value .. ':' .. current_time
        redis.call('SET', lock_key, new_value, 'EX', expiration)
        return {1, new_value}
        """

        # Compare and set with versioning
        self.scripts[
            "COMPARE_SET_SCRIPT"
        ] = """
        -- Compare and set with version checking
        -- KEYS[1]: data key
        -- KEYS[2]: version key
        -- ARGV[1]: expected version
        -- ARGV[2]: new value
        -- ARGV[3]: new version
        -- ARGV[4]: expiration

        local data_key = KEYS[1]
        local version_key = KEYS[2]
        local expected_version = ARGV[1]
        local new_value = ARGV[2]
        local new_version = ARGV[3]
        local expiration = tonumber(ARGV[4])

        -- Get current version
        local current_version = redis.call('GET', version_key)

        if current_version == expected_version then
            -- Version matches, update data
            redis.call('SET', data_key, new_value, 'EX', expiration)
            redis.call('SET', version_key, new_version, 'EX', expiration)
            return {1, new_version}
        else
            -- Version mismatch
            return {0, current_version}
        end
        """

        # Increment with overflow protection
        self.scripts[
            "INCREMENT_OVERFLOW_SCRIPT"
        ] = """
        -- Increment with overflow protection
        -- KEYS[1]: counter key
        -- ARGV[1]: increment amount
        -- ARGV[2]: maximum value
        -- ARGV[3]: reset value (optional)
        -- ARGV[4]: expiration

        local counter_key = KEYS[1]
        local increment = tonumber(ARGV[1])
        local max_value = tonumber(ARGV[2])
        local reset_value = tonumber(ARGV[3]) or 0
        local expiration = tonumber(ARGV[4])

        local current = tonumber(redis.call('GET', counter_key)) or 0
        local new_value = current + increment

        if new_value > max_value then
            new_value = reset_value
        end

        redis.call('SET', counter_key, new_value, 'EX', expiration)
        return new_value
        """

        # Batch operations with rollback
        self.scripts[
            "BATCH_OPERATIONS_SCRIPT"
        ] = """
        -- Batch operations with atomic rollback on failure
        -- KEYS[1]: batch key
        -- ARGV[1]: operation count
        -- ARGV[2-n]: operations (type:key:value:expiration)

        local batch_key = KEYS[1]
        local op_count = tonumber(ARGV[1])
        local results = {}
        local failed = false

        -- Process each operation
        for i = 1, op_count do
            local op_data = ARGV[i + 1]
            local parts = {}
            for part in string.gmatch(op_data, "[^:]+") do
                table.insert(parts, part)
            end

            local op_type = parts[1]
            local op_key = parts[2]
            local op_value = parts[3]
            local op_expiration = tonumber(parts[4]) or 0

            if op_type == 'SET' then
                if op_expiration > 0 then
                    redis.call('SET', op_key, op_value, 'EX', op_expiration)
                else
                    redis.call('SET', op_key, op_value)
                end
                table.insert(results, {1, op_key, op_value})
            elseif op_type == 'DEL' then
                local deleted = redis.call('DEL', op_key)
                table.insert(results, {deleted, op_key, op_value})
            elseif op_type == 'INCR' then
                local new_value = redis.call('INCR', op_key, op_value)
                table.insert(results, {1, op_key, new_value})
            else
                failed = true
                table.insert(results, {0, op_key, 'ERROR: Unknown operation'})
            end
        end

        if failed then
            -- Rollback operations
            for i = #results, 1, -1 do
                local result = results[i]
                if result[1] == 1 then
                    redis.call('DEL', result[2])
                end
            end
            return {0, 'Batch failed and rolled back'}
        else
            return {1, results}
        end
        """

        # Cache invalidation with pattern matching
        self.scripts[
            "CACHE_INVALIDATION_SCRIPT"
        ] = """
        -- Cache invalidation with pattern matching
        -- KEYS[1]: pattern key
        -- ARGV[1]: pattern to match
        -- ARGV[2]: workspace_id (optional)

        local pattern_key = KEYS[1]
        local pattern = ARGV[1]
        local workspace_id = ARGV[2]

        local invalidated = 0

        -- Get all keys matching pattern
        local keys = redis.call('KEYS', pattern)

        for i, key in ipairs(keys) do
            -- Check workspace isolation if provided
            if workspace_id then
                if string.find(key, workspace_id) then
                    redis.call('DEL', key)
                    invalidated = invalidated + 1
                end
            else
                redis.call('DEL', key)
                invalidated = invalidated + 1
            end
        end

        return invalidated
        """

        # Session cleanup with activity tracking
        self.scripts[
            "SESSION_CLEANUP_SCRIPT"
        ] = """
        -- Session cleanup with activity tracking
        -- KEYS[1]: session index key
        -- ARGV[1]: current timestamp
        -- ARGV[2]: session timeout
        -- ARGV[3]: max sessions per user

        local index_key = KEYS[1]
        local current_time = tonumber(ARGV[1])
        local timeout = tonumber(ARGV[2])
        local max_sessions = tonumber(ARGV[3])

        local cleaned = 0
        local user_sessions = {}

        -- Get all session entries
        local sessions = redis.call('HGETALL', index_key)

        for i = 1, #sessions, 2 do
            local session_id = sessions[i]
            local session_data = sessions[i + 1]

            -- Parse session data
            local data = {}
            for part in string.gmatch(session_data, "[^,]+") do
                local key_value = {}
                for kv in string.gmatch(part, "[^:]+") do
                    table.insert(key_value, kv)
                end
                if #key_value >= 2 then
                    data[key_value[1]] = key_value[2]
                end
            end

            -- Check if session is expired
            local last_active = tonumber(data['last_active'] or '0')
            if current_time - last_active > timeout then
                -- Remove expired session
                redis.call('DEL', 'session:' .. session_id)
                redis.call('HDEL', index_key, session_id)
                cleaned = cleaned + 1
            else
                -- Track active sessions per user
                local user_id = data['user_id']
                if user_id then
                    if not user_sessions[user_id] then
                        user_sessions[user_id] = 0
                    end
                    user_sessions[user_id] = user_sessions[user_id] + 1
                end
            end
        end

        -- Enforce max sessions per user
        for user_id, count in pairs(user_sessions) do
            if count > max_sessions then
                -- Get user's sessions sorted by last active
                local user_sessions_list = {}
                for i = 1, #sessions, 2 do
                    local session_id = sessions[i]
                    local session_data = sessions[i + 1]

                    if string.find(session_data, 'user_id:' .. user_id) then
                        table.insert(user_sessions_list, {session_id, session_data})
                    end
                end

                -- Sort by last active (oldest first)
                table.sort(user_sessions_list, function(a, b)
                    local a_time = tonumber(string.match(a[2], 'last_active:(%d+)') or '0')
                    local b_time = tonumber(string.match(b[2], 'last_active:(%d+)') or '0')
                    return a_time < b_time
                end)

                -- Remove oldest sessions
                local to_remove = count - max_sessions
                for i = 1, to_remove do
                    if user_sessions_list[i] then
                        local session_id = user_sessions_list[i][1]
                        redis.call('DEL', 'session:' .. session_id)
                        redis.call('HDEL', index_key, session_id)
                        cleaned = cleaned + 1
                    end
                end
            end
        end

        return cleaned
        """

        # Usage tracking with daily limits
        self.scripts[
            "USAGE_TRACKING_SCRIPT"
        ] = """
        -- Usage tracking with daily limits
        -- KEYS[1]: usage key
        -- ARGV[1]: workspace_id
        -- ARGV[2]: usage type (tokens, cost, requests)
        -- ARGV[3]: amount
        -- ARGV[4]: daily limit
        -- ARGV[5]: current timestamp
        -- ARGV[6]: timezone offset

        local usage_key = KEYS[1]
        local workspace_id = ARGV[1]
        local usage_type = ARGV[2]
        local amount = tonumber(ARGV[3])
        local daily_limit = tonumber(ARGV[4])
        local current_time = tonumber(ARGV[5])
        local timezone_offset = tonumber(ARGV[6])

        -- Calculate day key
        local day_timestamp = current_time + timezone_offset
        local day_key = math.floor(day_timestamp / 86400)
        local daily_key = usage_key .. ':' .. day_key

        -- Get current usage
        local current_usage = tonumber(redis.call('HGET', daily_key, usage_type)) or 0

        -- Check if adding amount would exceed limit
        if current_usage + amount > daily_limit then
            return {0, current_usage, daily_limit - current_usage}
        end

        -- Update usage
        local new_usage = current_usage + amount
        redis.call('HSET', daily_key, usage_type, new_usage)
        redis.call('EXPIRE', daily_key, 86400 * 7) -- Keep for 7 days

        -- Update total usage
        local total_key = usage_key .. ':total'
        redis.call('HINCRBY', total_key, usage_type, amount)
        redis.call('EXPIRE', total_key, 86400 * 90) -- Keep for 90 days

        return {1, new_usage, daily_limit - new_usage}
        """

        # Queue priority management
        self.scripts[
            "QUEUE_PRIORITY_SCRIPT"
        ] = """
        -- Queue priority management
        -- KEYS[1]: queue key
        -- ARGV[1]: item data
        -- ARGV[2]: priority (higher = more important)
        -- ARGV[3]: current timestamp
        -- ARGV[4]: max queue size

        local queue_key = KEYS[1]
        local item_data = ARGV[1]
        local priority = tonumber(ARGV[2])
        local current_time = tonumber(ARGV[3])
        local max_size = tonumber(ARGV[4])

        -- Check queue size
        local current_size = redis.call('LLEN', queue_key)

        if current_size >= max_size then
            -- Remove lowest priority item
            local lowest_priority = 999999
            local lowest_index = -1

            -- Scan queue to find lowest priority item
            local items = redis.call('LRANGE', queue_key, 0, -1)
            for i, item in ipairs(items) do
                local item_parts = {}
                for part in string.gmatch(item, "[^|]+") do
                    table.insert(item_parts, part)
                end

                if #item_parts >= 2 then
                    local item_priority = tonumber(item_parts[2]) or 0
                    if item_priority < lowest_priority then
                        lowest_priority = item_priority
                        lowest_index = i
                    end
                end
            end

            -- Remove lowest priority if new item has higher priority
            if lowest_index > 0 and priority > lowest_priority then
                redis.call('LREM', queue_key, 1, items[lowest_index])
            else
                return {0, 'Queue full and new item has lower priority'}
            end
        end

        -- Add new item with priority
        local priority_item = item_data .. '|' .. priority .. '|' .. current_time
        redis.call('LPUSH', queue_key, priority_item)

        return {1, 'Item added to queue'}
        """

        # Atomic counter with statistics
        self.scripts[
            "COUNTER_STATS_SCRIPT"
        ] = """
        -- Atomic counter with statistics
        -- KEYS[1]: counter key
        -- KEYS[2]: stats key
        -- ARGV[1]: increment amount
        -- ARGV[2]: current timestamp
        -- ARGV[3]: reset interval (hourly, daily, monthly)
        -- ARGV[4]: expiration

        local counter_key = KEYS[1]
        local stats_key = KEYS[2]
        local increment = tonumber(ARGV[1])
        local current_time = tonumber(ARGV[2])
        local reset_interval = ARGV[3]
        local expiration = tonumber(ARGV[4])

        -- Increment counter
        local new_value = redis.call('INCRBY', counter_key, increment)
        redis.call('EXPIRE', counter_key, expiration)

        -- Update statistics
        local time_key
        if reset_interval == 'hourly' then
            time_key = math.floor(current_time / 3600)
        elseif reset_interval == 'daily' then
            time_key = math.floor(current_time / 86400)
        elseif reset_interval == 'monthly' then
            time_key = math.floor(current_time / (86400 * 30))
        else
            time_key = current_time
        end

        local stats_field = reset_interval .. ':' .. time_key
        redis.call('HINCRBY', stats_key, stats_field, increment)
        redis.call('EXPIRE', stats_key, expiration * 2)

        -- Get historical stats
        local stats = redis.call('HGETALL', stats_key)
        local total = 0
        local count = 0

        for i = 1, #stats, 2 do
            if string.find(stats[i], reset_interval .. ':') then
                total = total + tonumber(stats[i + 1])
                count = count + 1
            end
        end

        local average = 0
        if count > 0 then
            average = total / count
        end

        return {new_value, total, average}
        """

    async def register_scripts(self) -> Dict[str, str]:
        """Register all scripts with Redis."""
        results = {}

        for name, script in self.scripts.items():
            try:
                # Try to load script
                sha = await self.redis.async_client.script_load(script)
                self.sha_cache[name] = sha
                results[name] = sha
            except Exception as e:
                results[name] = f"Error: {str(e)}"

        return results

    async def execute_script(
        self, script_name: str, keys: List[str], args: List[str]
    ) -> Any:
        """Execute a registered Lua script."""
        if script_name not in self.scripts:
            raise ValueError(f"Script '{script_name}' not found")

        if script_name not in self.sha_cache:
            # Register script first
            await self.register_scripts()

        sha = self.sha_cache[script_name]

        try:
            return await self.redis.async_client.evalsha(sha, len(keys), *keys, *args)
        except Exception as e:
            # Script might have been flushed, try to reload
            if "NOSCRIPT" in str(e):
                await self.register_scripts()
                sha = self.sha_cache[script_name]
                return await self.redis.async_client.evalsha(
                    sha, len(keys), *keys, *args
                )
            else:
                raise

    async def rate_limit_sliding_window(
        self, key: str, window_seconds: int, max_requests: int, request_count: int = 1
    ) -> tuple[bool, int]:
        """Execute sliding window rate limiting."""
        current_time = int(datetime.now().timestamp())

        result = await self.execute_script(
            "RATE_LIMIT_SCRIPT",
            [key],
            [
                str(window_seconds),
                str(max_requests),
                str(current_time),
                str(request_count),
            ],
        )

        return bool(result[0]), result[1]

    async def queue_dequeue_atomic(
        self,
        queue_key: str,
        processing_key: str,
        timeout: int = 300,
        max_items: int = 1,
    ) -> List[str]:
        """Execute atomic queue dequeue."""
        current_time = int(datetime.now().timestamp())

        result = await self.execute_script(
            "QUEUE_DEQUEUE_SCRIPT",
            [queue_key, processing_key],
            [str(current_time), str(timeout), str(max_items)],
        )

        return result if isinstance(result, list) else []

    async def distributed_lock(
        self, lock_key: str, lock_value: str, expiration: int = 30
    ) -> tuple[bool, str]:
        """Execute distributed lock."""
        current_time = int(datetime.now().timestamp())

        result = await self.execute_script(
            "DISTRIBUTED_LOCK_SCRIPT",
            [lock_key],
            [lock_value, str(expiration), str(current_time)],
        )

        return bool(result[0]), result[1]

    async def compare_and_set(
        self,
        data_key: str,
        version_key: str,
        expected_version: str,
        new_value: str,
        new_version: str,
        expiration: int = 3600,
    ) -> tuple[bool, str]:
        """Execute compare and set."""
        result = await self.execute_script(
            "COMPARE_SET_SCRIPT",
            [data_key, version_key],
            [expected_version, new_value, new_version, str(expiration)],
        )

        return bool(result[0]), result[1]

    async def increment_overflow(
        self,
        counter_key: str,
        increment: int,
        max_value: int,
        reset_value: int = 0,
        expiration: int = 3600,
    ) -> int:
        """Execute increment with overflow protection."""
        result = await self.execute_script(
            "INCREMENT_OVERFLOW_SCRIPT",
            [counter_key],
            [str(increment), str(max_value), str(reset_value), str(expiration)],
        )

        return result

    async def batch_operations(
        self, operations: List[Dict[str, Any]], expiration: int = 3600
    ) -> tuple[bool, Any]:
        """Execute batch operations with rollback."""
        batch_key = f"batch:{int(datetime.now().timestamp())}"

        # Prepare operation data
        op_data = [str(len(operations))]
        for op in operations:
            op_str = f"{op['type']}:{op['key']}:{op['value']}:{expiration}"
            op_data.append(op_str)

        result = await self.execute_script(
            "BATCH_OPERATIONS_SCRIPT", [batch_key], op_data
        )

        # Clean up batch key
        await self.redis.delete(batch_key)

        return bool(result[0]), result[1]

    async def invalidate_cache_pattern(
        self, pattern: str, workspace_id: Optional[str] = None
    ) -> int:
        """Execute cache invalidation."""
        pattern_key = f"pattern:{int(datetime.now().timestamp())}"

        args = [pattern]
        if workspace_id:
            args.append(workspace_id)

        result = await self.execute_script(
            "CACHE_INVALIDATION_SCRIPT", [pattern_key], args
        )

        # Clean up pattern key
        await self.redis.delete(pattern_key)

        return result

    async def cleanup_sessions(
        self,
        session_index_key: str,
        timeout: int = 1800,
        max_sessions_per_user: int = 5,
    ) -> int:
        """Execute session cleanup."""
        current_time = int(datetime.now().timestamp())

        result = await self.execute_script(
            "SESSION_CLEANUP_SCRIPT",
            [session_index_key],
            [str(current_time), str(timeout), str(max_sessions_per_user)],
        )

        return result

    async def track_usage(
        self,
        usage_key: str,
        workspace_id: str,
        usage_type: str,
        amount: int,
        daily_limit: int,
        timezone_offset: int = 0,
    ) -> tuple[bool, int, int]:
        """Execute usage tracking."""
        current_time = int(datetime.now().timestamp())

        result = await self.execute_script(
            "USAGE_TRACKING_SCRIPT",
            [usage_key],
            [
                workspace_id,
                usage_type,
                str(amount),
                str(daily_limit),
                str(current_time),
                str(timezone_offset),
            ],
        )

        return bool(result[0]), result[1], result[2]

    async def queue_priority_push(
        self, queue_key: str, item_data: str, priority: int, max_size: int = 1000
    ) -> tuple[bool, str]:
        """Execute priority queue push."""
        current_time = int(datetime.now().timestamp())

        result = await self.execute_script(
            "QUEUE_PRIORITY_SCRIPT",
            [queue_key],
            [item_data, str(priority), str(current_time), str(max_size)],
        )

        return bool(result[0]), result[1]

    async def counter_with_stats(
        self,
        counter_key: str,
        stats_key: str,
        increment: int,
        reset_interval: str = "daily",
        expiration: int = 86400,
    ) -> tuple[int, int, float]:
        """Execute counter with statistics."""
        current_time = int(datetime.now().timestamp())

        result = await self.execute_script(
            "COUNTER_STATS_SCRIPT",
            [counter_key, stats_key],
            [str(increment), str(current_time), reset_interval, str(expiration)],
        )

        return result[0], result[1], result[2]

    def get_script_list(self) -> List[str]:
        """Get list of available scripts."""
        return list(self.scripts.keys())

    def get_script(self, script_name: str) -> Optional[str]:
        """Get script source code."""
        return self.scripts.get(script_name)

    def is_script_registered(self, script_name: str) -> bool:
        """Check if script is registered with Redis."""
        return script_name in self.sha_cache


# Global script manager instance
_script_manager = LuaScriptManager()


def get_script_manager() -> LuaScriptManager:
    """Get global script manager instance."""
    return _script_manager


async def register_all_scripts() -> Dict[str, str]:
    """Register all scripts with Redis."""
    return await _script_manager.register_scripts()


# Convenience functions for common operations
async def rate_limit(
    key: str, window_seconds: int, max_requests: int, request_count: int = 1
) -> tuple[bool, int]:
    """Rate limiting with sliding window."""
    return await _script_manager.rate_limit_sliding_window(
        key, window_seconds, max_requests, request_count
    )


async def distributed_lock(
    key: str, value: str, expiration: int = 30
) -> tuple[bool, str]:
    """Distributed lock."""
    return await _script_manager.distributed_lock(key, value, expiration)


async def compare_and_set(
    data_key: str,
    version_key: str,
    expected_version: str,
    new_value: str,
    new_version: str,
    expiration: int = 3600,
) -> tuple[bool, str]:
    """Compare and set."""
    return await _script_manager.compare_and_set(
        data_key, version_key, expected_version, new_value, new_version, expiration
    )


async def atomic_increment(
    key: str,
    increment: int = 1,
    max_value: int = 1000000,
    reset_value: int = 0,
    expiration: int = 3600,
) -> int:
    """Atomic increment with overflow protection."""
    return await _script_manager.increment_overflow(
        key, increment, max_value, reset_value, expiration
    )


async def batch_execute(
    operations: List[Dict[str, Any]], expiration: int = 3600
) -> tuple[bool, Any]:
    """Execute batch operations."""
    return await _script_manager.batch_operations(operations, expiration)


async def invalidate_cache(pattern: str, workspace_id: Optional[str] = None) -> int:
    """Invalidate cache by pattern."""
    return await _script_manager.invalidate_cache_pattern(pattern, workspace_id)


async def queue_dequeue(
    queue_key: str, processing_key: str, timeout: int = 300, max_items: int = 1
) -> List[str]:
    """Atomic queue dequeue."""
    return await _script_manager.queue_dequeue_atomic(
        queue_key, processing_key, timeout, max_items
    )


async def priority_queue_push(
    queue_key: str, item_data: str, priority: int, max_size: int = 1000
) -> tuple[bool, str]:
    """Push to priority queue."""
    return await _script_manager.queue_priority_push(
        queue_key, item_data, priority, max_size
    )
