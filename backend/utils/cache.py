"""
Redis-based caching layer for RaptorFlow
Includes distributed locks, rate limiting, and cache management.
"""

import json
import hashlib
import uuid
from typing import Any, Optional
import redis.asyncio as redis
from backend.config.settings import get_settings
import structlog

settings = get_settings()

logger = structlog.get_logger()


class CacheClient:
    """Async Redis cache client"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        
    async def connect(self):
        """
        Establish Redis connection with retry logic.
        Supports both localhost and Upstash Redis.
        """
        for attempt in range(settings.REDIS_RETRIES):
            try:
                # Build connection kwargs
                conn_kwargs = {
                    "max_connections": settings.REDIS_MAX_CONNECTIONS,
                    "socket_timeout": settings.REDIS_SOCKET_TIMEOUT,
                    "decode_responses": True,
                }

                # Add SSL for Upstash/production
                if settings.REDIS_SSL or "upstash" in settings.REDIS_URL:
                    conn_kwargs["ssl"] = True
                    conn_kwargs["ssl_certfile"] = None
                    conn_kwargs["ssl_keyfile"] = None
                    conn_kwargs["ssl_cert_reqs"] = "required"
                    logger.info("Using SSL for Redis connection (Upstash)")

                self.redis = await redis.from_url(
                    settings.REDIS_URL,
                    **conn_kwargs
                )

                # Test connection
                await self.redis.ping()
                logger.info(
                    "✓ Redis cache connected",
                    url=settings.REDIS_URL.split("@")[-1] if "@" in settings.REDIS_URL else "localhost",
                    attempt=attempt + 1
                )
                return

            except Exception as e:
                logger.warning(
                    f"Redis connection attempt {attempt + 1}/{settings.REDIS_RETRIES} failed",
                    error=str(e)
                )

                if attempt < settings.REDIS_RETRIES - 1:
                    import asyncio
                    await asyncio.sleep(settings.REDIS_RETRY_DELAY)
                else:
                    logger.error("Failed to connect to Redis after all retries", error=str(e))
                    raise
            
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis cache disconnected")
    
    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key with prefix"""
        # Hash long identifiers to keep keys manageable
        if len(identifier) > 100:
            identifier = hashlib.md5(identifier.encode()).hexdigest()
        return f"raptorflow:{prefix}:{identifier}"
    
    async def get(self, prefix: str, identifier: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None
            
        key = self._generate_key(prefix, identifier)
        try:
            value = await self.redis.get(key)
            if value:
                logger.debug("Cache hit", key=key)
                return json.loads(value)
            logger.debug("Cache miss", key=key)
            return None
        except Exception as e:
            logger.warning("Cache get failed", key=key, error=str(e))
            return None
    
    async def set(
        self, 
        prefix: str, 
        identifier: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL (seconds)"""
        if not self.redis:
            return False
            
        key = self._generate_key(prefix, identifier)
        try:
            serialized = json.dumps(value)
            if ttl:
                await self.redis.setex(key, ttl, serialized)
            else:
                await self.redis.set(key, serialized)
            logger.debug("Cache set", key=key, ttl=ttl)
            return True
        except Exception as e:
            logger.warning("Cache set failed", key=key, error=str(e))
            return False
    
    async def delete(self, prefix: str, identifier: str) -> bool:
        """Delete value from cache"""
        if not self.redis:
            return False
            
        key = self._generate_key(prefix, identifier)
        try:
            await self.redis.delete(key)
            logger.debug("Cache deleted", key=key)
            return True
        except Exception as e:
            logger.warning("Cache delete failed", key=key, error=str(e))
            return False
    
    async def exists(self, prefix: str, identifier: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis:
            return False

        key = self._generate_key(prefix, identifier)
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.warning("Cache exists check failed", key=key, error=str(e))
            return False

    async def incr(self, key: str, expire: Optional[int] = None) -> int:
        """
        Increment counter in cache (for rate limiting). Returns new count.

        SECURITY: Uses Lua script for atomic increment with expiry to prevent race conditions.
        Ensures expiry is set atomically on first increment without gap vulnerabilities.
        """
        if not self.redis:
            return 1

        try:
            if expire:
                # Use Lua script for atomic increment with expiry
                # This prevents race condition between INCR and EXPIRE
                lua_script = """
local count = redis.call('incr', KEYS[1])
if count == 1 then
    redis.call('expire', KEYS[1], ARGV[1])
end
return count
"""
                # Register and execute Lua script atomically
                script = self.redis.register_script(lua_script)
                count = await script(keys=[key], args=[expire])
                return int(count)
            else:
                # Simple increment without expiry
                count = await self.redis.incr(key)
                return count
        except Exception as e:
            logger.warning("Cache incr failed", key=key, error=str(e))
            return 1

    async def ping(self) -> bool:
        """Check Redis connection"""
        if not self.redis:
            return False
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.warning("Redis ping failed", error=str(e))
            return False

    # ==================== DISTRIBUTED LOCKS ====================
    # For preventing race conditions in payment processing, webhooks, etc.

    async def acquire_lock(self, key: str, ttl: int = 30, token: Optional[str] = None) -> Optional[str]:
        """
        Acquire a distributed lock with atomic SET NX.

        Args:
            key: Lock key (e.g., 'lock:webhook:transaction_id')
            ttl: Lock TTL in seconds (default 30)
            token: Optional unique token. If None, generates UUID.

        Returns:
            Lock token if acquired, None if lock already held by another process

        Usage:
            lock_token = await redis_cache.acquire_lock('lock:webhook:MT123', ttl=30)
            if lock_token:
                try:
                    # Process payment webhook
                finally:
                    await redis_cache.release_lock('lock:webhook:MT123', lock_token)
        """
        if not self.redis:
            return None

        try:
            # Generate unique token if not provided
            if not token:
                token = str(uuid.uuid4())

            # Use SET NX EX for atomic lock acquisition
            # SET (set), NX (only if not exists), EX (expire in seconds)
            lock_key = f"raptorflow:lock:{key}"
            acquired = await self.redis.set(
                lock_key,
                token,
                nx=True,  # Only set if key doesn't exist
                ex=ttl    # Expire in ttl seconds
            )

            if acquired:
                logger.debug("Lock acquired", key=key, token=token[:8], ttl=ttl)
                return token
            else:
                logger.debug("Lock already held", key=key)
                return None

        except Exception as e:
            logger.error("Failed to acquire lock", key=key, error=str(e))
            return None

    async def release_lock(self, key: str, token: str) -> bool:
        """
        Release a distributed lock (only if token matches).

        SECURITY: Uses Lua script to prevent accidental/malicious unlock by wrong process.

        Args:
            key: Lock key
            token: Lock token (must match to release)

        Returns:
            True if lock was released, False if token didn't match or lock doesn't exist
        """
        if not self.redis:
            return False

        try:
            lock_key = f"raptorflow:lock:{key}"

            # Lua script ensures atomic check-and-delete
            # Prevents process A from releasing process B's lock
            lua_script = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
"""
            script = self.redis.register_script(lua_script)
            deleted = await script(keys=[lock_key], args=[token])

            if deleted:
                logger.debug("Lock released", key=key, token=token[:8])
                return True
            else:
                logger.warning("Lock release failed - token mismatch or lock expired", key=key)
                return False

        except Exception as e:
            logger.error("Failed to release lock", key=key, error=str(e))
            return False

    async def lock_exists(self, key: str) -> bool:
        """
        Check if a lock exists.

        Args:
            key: Lock key

        Returns:
            True if lock is currently held, False otherwise
        """
        if not self.redis:
            return False

        try:
            lock_key = f"raptorflow:lock:{key}"
            exists = await self.redis.exists(lock_key)
            return exists > 0
        except Exception as e:
            logger.warning("Lock exists check failed", key=key, error=str(e))
            return False

    async def extend_lock(self, key: str, token: str, additional_ttl: int = 10) -> bool:
        """
        Extend a lock's TTL (only if token matches).

        Args:
            key: Lock key
            token: Lock token (must match to extend)
            additional_ttl: Additional seconds to extend

        Returns:
            True if lock was extended, False if token didn't match
        """
        if not self.redis:
            return False

        try:
            lock_key = f"raptorflow:lock:{key}"

            # Lua script: check token and extend expire time
            lua_script = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('expire', KEYS[1], ARGV[2])
else
    return 0
end
"""
            script = self.redis.register_script(lua_script)
            extended = await script(keys=[lock_key], args=[token, additional_ttl])

            if extended:
                logger.debug("Lock extended", key=key, token=token[:8], additional_ttl=additional_ttl)
                return True
            else:
                logger.warning("Lock extend failed - token mismatch or lock expired", key=key)
                return False

        except Exception as e:
            logger.error("Failed to extend lock", key=key, error=str(e))
            return False

    # ==================== SESSION MANAGEMENT ====================
    # User sessions, refresh tokens, logout tracking

    async def create_session(
        self,
        user_id: str,
        session_data: dict,
        ttl: int = 86400  # 24 hours default
    ) -> str:
        """
        Create a user session with data.

        Args:
            user_id: User UUID
            session_data: Dict with session info (refresh_token, ip, user_agent, etc.)
            ttl: Session TTL in seconds (default 24 hours)

        Returns:
            session_id (unique identifier for this session)

        Usage:
            session_id = await redis_cache.create_session(
                user_id="uuid-123",
                session_data={
                    "refresh_token": "refresh_token_jwt",
                    "ip": "192.168.1.1",
                    "user_agent": "Mozilla/5.0...",
                    "device": "chrome-linux"
                },
                ttl=86400
            )
        """
        if not self.redis:
            return None

        try:
            from datetime import datetime, timezone

            # Generate unique session ID
            session_id = str(uuid.uuid4())

            # Store session with user_id reference for easy lookup
            session_key = f"raptorflow:session:{session_id}"
            user_sessions_key = f"raptorflow:user_sessions:{user_id}"

            # Add session data with user_id for auditing
            session_data_with_meta = {
                **session_data,
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "session_id": session_id
            }

            # Store session with TTL
            serialized = json.dumps(session_data_with_meta)
            await self.redis.setex(session_key, ttl, serialized)

            # Also track all sessions per user (for logout-all functionality)
            await self.redis.sadd(user_sessions_key, session_id)
            # Sessions list expires when last session expires (max)
            await self.redis.expire(user_sessions_key, ttl + 3600)

            logger.debug(
                "Session created",
                user_id=user_id,
                session_id=session_id[:8],
                ttl=ttl
            )
            return session_id

        except Exception as e:
            logger.error("Failed to create session", user_id=user_id, error=str(e))
            return None

    async def get_session(self, session_id: str) -> Optional[dict]:
        """
        Retrieve session data.

        Args:
            session_id: Session ID

        Returns:
            Session data dict if exists, None if expired/invalid
        """
        if not self.redis:
            return None

        try:
            session_key = f"raptorflow:session:{session_id}"
            data = await self.redis.get(session_key)

            if data:
                logger.debug("Session retrieved", session_id=session_id[:8])
                return json.loads(data)
            else:
                logger.debug("Session not found or expired", session_id=session_id[:8])
                return None

        except Exception as e:
            logger.error("Failed to get session", session_id=session_id[:8], error=str(e))
            return None

    async def destroy_session(self, session_id: str) -> bool:
        """
        Destroy a single session (logout).

        Args:
            session_id: Session ID to destroy

        Returns:
            True if session was destroyed, False if not found
        """
        if not self.redis:
            return False

        try:
            session_key = f"raptorflow:session:{session_id}"

            # Get session first to get user_id for cleanup
            session_data = await self.get_session(session_id)
            if session_data:
                user_id = session_data.get("user_id")
                user_sessions_key = f"raptorflow:user_sessions:{user_id}"

                # Remove from user's session set
                if user_id:
                    await self.redis.srem(user_sessions_key, session_id)

            # Delete session
            deleted = await self.redis.delete(session_key)

            if deleted:
                logger.info("Session destroyed", session_id=session_id[:8])
                return True
            else:
                logger.warning("Session not found for destruction", session_id=session_id[:8])
                return False

        except Exception as e:
            logger.error("Failed to destroy session", session_id=session_id[:8], error=str(e))
            return False

    async def destroy_all_user_sessions(self, user_id: str) -> int:
        """
        Destroy ALL sessions for a user (logout all devices).

        SECURITY: Used when user changes password or we detect suspicious activity.

        Args:
            user_id: User UUID

        Returns:
            Number of sessions destroyed
        """
        if not self.redis:
            return 0

        try:
            user_sessions_key = f"raptorflow:user_sessions:{user_id}"

            # Get all session IDs for this user
            session_ids = await self.redis.smembers(user_sessions_key)

            if not session_ids:
                logger.info("No active sessions to destroy", user_id=user_id)
                return 0

            # Delete each session
            destroyed_count = 0
            for session_id in session_ids:
                session_key = f"raptorflow:session:{session_id}"
                await self.redis.delete(session_key)
                destroyed_count += 1

            # Delete the user's session set
            await self.redis.delete(user_sessions_key)

            logger.warning(
                "All user sessions destroyed",
                user_id=user_id,
                count=destroyed_count
            )
            return destroyed_count

        except Exception as e:
            logger.error(
                "Failed to destroy all user sessions",
                user_id=user_id,
                error=str(e)
            )
            return 0

    async def refresh_session_ttl(self, session_id: str, new_ttl: int = 86400) -> bool:
        """
        Extend a session's TTL (used by refresh token endpoint).

        Args:
            session_id: Session ID
            new_ttl: New TTL in seconds

        Returns:
            True if session TTL was extended, False if session not found
        """
        if not self.redis:
            return False

        try:
            session_key = f"raptorflow:session:{session_id}"

            # Check if session exists
            exists = await self.redis.exists(session_key)
            if not exists:
                logger.warning("Session not found for TTL refresh", session_id=session_id[:8])
                return False

            # Extend TTL
            await self.redis.expire(session_key, new_ttl)

            logger.debug(
                "Session TTL refreshed",
                session_id=session_id[:8],
                new_ttl=new_ttl
            )
            return True

        except Exception as e:
            logger.error(
                "Failed to refresh session TTL",
                session_id=session_id[:8],
                error=str(e)
            )
            return False

    async def get_user_sessions(self, user_id: str) -> list:
        """
        Get all active sessions for a user.

        SECURITY: Used for user to see all logged-in devices.

        Args:
            user_id: User UUID

        Returns:
            List of session dicts
        """
        if not self.redis:
            return []

        try:
            user_sessions_key = f"raptorflow:user_sessions:{user_id}"

            # Get all session IDs
            session_ids = await self.redis.smembers(user_sessions_key)

            if not session_ids:
                return []

            # Fetch all session data
            sessions = []
            for session_id in session_ids:
                session_data = await self.get_session(session_id)
                if session_data:  # Skip expired sessions
                    sessions.append(session_data)

            logger.debug(
                "User sessions retrieved",
                user_id=user_id,
                count=len(sessions)
            )
            return sessions

        except Exception as e:
            logger.error(
                "Failed to get user sessions",
                user_id=user_id,
                error=str(e)
            )
            return []

    # ==================== QUEUE MANAGEMENT ====================
    # For job processing, webhook retries, background tasks

    async def add_to_queue(
        self,
        queue_name: str,
        item: Any
    ) -> bool:
        """
        Add an item to a queue (uses list LPUSH).

        Args:
            queue_name: Name of the queue
            item: Item to queue (dict, string, etc.)

        Returns:
            True if item was added, False on error

        Usage:
            # Queue a payment reconciliation task
            await redis_cache.add_to_queue(
                "payment_reconciliation",
                {"user_id": "123", "transaction_id": "MT123..."}
            )
        """
        if not self.redis:
            return False

        try:
            queue_key = f"raptorflow:queue:{queue_name}"
            serialized = json.dumps(item)
            await self.redis.lpush(queue_key, serialized)
            logger.debug("Item added to queue", queue=queue_name)
            return True
        except Exception as e:
            logger.error("Failed to add item to queue", queue=queue_name, error=str(e))
            return False

    async def get_from_queue(
        self,
        queue_name: str,
        blocking: bool = False,
        timeout: int = 0
    ) -> Optional[Any]:
        """
        Pop an item from a queue (uses list RPOP or BRPOP).

        Args:
            queue_name: Name of the queue
            blocking: If True, block until item available (BRPOP)
            timeout: Timeout in seconds for blocking (0 = infinite)

        Returns:
            Item dict if available, None if queue empty or timeout

        Usage:
            # Non-blocking pop
            item = await redis_cache.get_from_queue("payment_reconciliation")

            # Blocking pop (wait up to 5 seconds)
            item = await redis_cache.get_from_queue(
                "payment_reconciliation",
                blocking=True,
                timeout=5
            )
        """
        if not self.redis:
            return None

        try:
            queue_key = f"raptorflow:queue:{queue_name}"

            if blocking:
                # BRPOP blocks until item available or timeout
                result = await self.redis.brpop(queue_key, timeout=timeout)
                if result:
                    # BRPOP returns (key, value) tuple
                    _, serialized = result
                    logger.debug("Item popped from queue (blocking)", queue=queue_name)
                    return json.loads(serialized)
            else:
                # RPOP non-blocking
                serialized = await self.redis.rpop(queue_key)
                if serialized:
                    logger.debug("Item popped from queue", queue=queue_name)
                    return json.loads(serialized)

            return None
        except Exception as e:
            logger.error("Failed to pop from queue", queue=queue_name, error=str(e))
            return None

    async def queue_length(self, queue_name: str) -> int:
        """
        Get number of items in queue.

        Args:
            queue_name: Name of the queue

        Returns:
            Number of items in queue

        Usage:
            length = await redis_cache.queue_length("payment_reconciliation")
            print(f"Queue has {length} items")
        """
        if not self.redis:
            return 0

        try:
            queue_key = f"raptorflow:queue:{queue_name}"
            length = await self.redis.llen(queue_key)
            return length
        except Exception as e:
            logger.warning("Failed to get queue length", queue=queue_name, error=str(e))
            return 0

    async def peek_queue(
        self,
        queue_name: str,
        count: int = 10
    ) -> list:
        """
        View items in queue without removing them (uses LRANGE).

        Args:
            queue_name: Name of the queue
            count: Number of items to peek (from front)

        Returns:
            List of items in queue (up to count items)

        Usage:
            # Peek first 10 items without removing
            items = await redis_cache.peek_queue("payment_reconciliation", count=10)
            for item in items:
                print(item)
        """
        if not self.redis:
            return []

        try:
            queue_key = f"raptorflow:queue:{queue_name}"
            # LRANGE 0 count-1 gets first 'count' items
            serialized_items = await self.redis.lrange(queue_key, 0, count - 1)

            if not serialized_items:
                return []

            items = []
            for serialized in serialized_items:
                try:
                    items.append(json.loads(serialized))
                except json.JSONDecodeError:
                    logger.warning("Failed to deserialize queue item", queue=queue_name)

            logger.debug("Queue peeked", queue=queue_name, count=len(items))
            return items
        except Exception as e:
            logger.error("Failed to peek queue", queue=queue_name, error=str(e))
            return []

    async def get_all_queue_items(self, queue_name: str) -> list:
        """
        Get ALL items in queue without removing them.

        Args:
            queue_name: Name of the queue

        Returns:
            List of all items in queue

        Usage:
            all_items = await redis_cache.get_all_queue_items("payment_reconciliation")
            # Useful for debugging or status checks
        """
        if not self.redis:
            return []

        try:
            queue_key = f"raptorflow:queue:{queue_name}"
            length = await self.redis.llen(queue_key)

            if length == 0:
                return []

            # LRANGE 0 -1 gets all items
            serialized_items = await self.redis.lrange(queue_key, 0, -1)

            items = []
            for serialized in serialized_items:
                try:
                    items.append(json.loads(serialized))
                except json.JSONDecodeError:
                    logger.warning("Failed to deserialize queue item", queue=queue_name)

            logger.debug(
                "All queue items retrieved",
                queue=queue_name,
                count=len(items)
            )
            return items
        except Exception as e:
            logger.error("Failed to get all queue items", queue=queue_name, error=str(e))
            return []

    async def clear_queue(self, queue_name: str) -> bool:
        """
        Clear entire queue (delete all items).

        SECURITY: Use with caution - this deletes all queued items.

        Args:
            queue_name: Name of the queue to clear

        Returns:
            True if queue was cleared, False on error

        Usage:
            # Clear all failed reconciliation items
            await redis_cache.clear_queue("payment_reconciliation_failed")
        """
        if not self.redis:
            return False

        try:
            queue_key = f"raptorflow:queue:{queue_name}"
            deleted = await self.redis.delete(queue_key)

            logger.warning("Queue cleared", queue=queue_name, deleted=bool(deleted))
            return bool(deleted)
        except Exception as e:
            logger.error("Failed to clear queue", queue=queue_name, error=str(e))
            return False

    # ==================== PUB/SUB MESSAGING ====================
    # For real-time updates: payment notifications, alerts, live dashboards

    async def publish(self, channel: str, message: Any) -> int:
        """
        Publish a message to a channel.

        Args:
            channel: Channel name to publish to
            message: Message to publish (dict, string, etc.)

        Returns:
            Number of subscribers that received the message

        Usage:
            # Notify about payment completion
            subscribers = await redis_cache.publish(
                "payment:user-uuid-123",
                {"status": "completed", "amount": 500}
            )
            logger.info(f"Payment update sent to {subscribers} subscribers")
        """
        if not self.redis:
            return 0

        try:
            channel_key = f"raptorflow:{channel}"
            serialized = json.dumps(message)
            num_subscribers = await self.redis.publish(channel_key, serialized)
            logger.debug(
                "Message published",
                channel=channel,
                subscribers=num_subscribers
            )
            return num_subscribers
        except Exception as e:
            logger.error("Failed to publish message", channel=channel, error=str(e))
            return 0

    async def subscribe(self, *channels: str) -> redis.client.PubSub:
        """
        Subscribe to one or more channels.

        IMPORTANT: This is a blocking operation. Returns a PubSub object that
        you must iterate over to receive messages.

        Args:
            *channels: Channel names to subscribe to

        Returns:
            PubSub object for receiving messages

        Usage:
            # Subscribe to payment updates for a user
            pubsub = await redis_cache.subscribe("payment:user-uuid-123")
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    print(f"Payment update: {data}")
        """
        if not self.redis:
            return None

        try:
            pubsub = self.redis.pubsub()
            # Add raptorflow: prefix to channels
            full_channels = [f"raptorflow:{channel}" for channel in channels]
            await pubsub.subscribe(*full_channels)
            logger.info("Subscribed to channels", channels=channels)
            return pubsub
        except Exception as e:
            logger.error("Failed to subscribe", channels=channels, error=str(e))
            return None

    async def unsubscribe(self, pubsub: redis.client.PubSub, *channels: str) -> None:
        """
        Unsubscribe from channels.

        Args:
            pubsub: PubSub object returned from subscribe()
            *channels: Channel names to unsubscribe from

        Usage:
            await redis_cache.unsubscribe(pubsub, "payment:user-uuid-123")
        """
        if not pubsub:
            return

        try:
            full_channels = [f"raptorflow:{channel}" for channel in channels]
            await pubsub.unsubscribe(*full_channels)
            logger.info("Unsubscribed from channels", channels=channels)
        except Exception as e:
            logger.error("Failed to unsubscribe", channels=channels, error=str(e))

    async def close_subscription(self, pubsub: redis.client.PubSub) -> None:
        """
        Close a subscription and clean up resources.

        Args:
            pubsub: PubSub object to close

        Usage:
            await redis_cache.close_subscription(pubsub)
        """
        if not pubsub:
            return

        try:
            await pubsub.close()
            logger.debug("Subscription closed")
        except Exception as e:
            logger.warning("Error closing subscription", error=str(e))

    async def publish_to_user(
        self,
        user_id: str,
        event_type: str,
        data: dict
    ) -> int:
        """
        Publish an event to a user's channel.

        Args:
            user_id: User UUID to send to
            event_type: Type of event (payment, alert, etc.)
            data: Event data

        Returns:
            Number of subscribers that received the message

        Usage:
            # Notify user about successful payment
            await redis_cache.publish_to_user(
                "user-uuid-123",
                "payment.completed",
                {"transaction_id": "MT123...", "amount": 500}
            )
        """
        if not self.redis:
            return 0

        try:
            channel = f"user:{user_id}:{event_type}"
            message = {
                "type": event_type,
                "data": data,
                "timestamp": __import__('datetime').datetime.now(
                    __import__('datetime').timezone.utc
                ).isoformat()
            }
            return await self.publish(channel, message)
        except Exception as e:
            logger.error(
                "Failed to publish to user",
                user_id=user_id,
                event_type=event_type,
                error=str(e)
            )
            return 0


redis_cache = CacheClient()
# Legacy alias for backward compatibility
cache = redis_cache


# Convenience functions for specific cache types
async def cache_research(query: str, result: Any) -> bool:
    """Cache research results for 7 days"""
    return await redis_cache.set("research", query, result, settings.CACHE_TTL_RESEARCH)


async def get_cached_research(query: str) -> Optional[Any]:
    """Get cached research results"""
    return await redis_cache.get("research", query)


async def cache_persona(icp_id: str, persona: Any) -> bool:
    """Cache persona data for 30 days"""
    return await redis_cache.set("persona", icp_id, persona, settings.CACHE_TTL_PERSONA)


async def get_cached_persona(icp_id: str) -> Optional[Any]:
    """Get cached persona data"""
    return await redis_cache.get("persona", icp_id)


async def cache_content(content_id: str, content: Any) -> bool:
    """Cache generated content for 24 hours"""
    return await redis_cache.set("content", content_id, content, settings.CACHE_TTL_CONTENT)


async def get_cached_content(content_id: str) -> Optional[Any]:
    """Get cached content"""
    return await redis_cache.get("content", content_id)


# ==================== SESSION CONVENIENCE FUNCTIONS ====================

async def create_user_session(
    user_id: str,
    refresh_token: str,
    ip_address: str,
    user_agent: str,
    device: str = "web",
    ttl: int = 86400
) -> str:
    """
    Create a user session with common metadata.

    Args:
        user_id: User UUID
        refresh_token: JWT refresh token
        ip_address: Client IP address
        user_agent: Browser user agent
        device: Device type (web, mobile, desktop)
        ttl: Session TTL in seconds

    Returns:
        session_id
    """
    return await redis_cache.create_session(
        user_id,
        {
            "refresh_token": refresh_token,
            "ip": ip_address,
            "user_agent": user_agent,
            "device": device,
        },
        ttl=ttl
    )


async def verify_session(session_id: str) -> Optional[str]:
    """
    Verify a session exists and return user_id.

    Args:
        session_id: Session ID to verify

    Returns:
        user_id if valid, None if expired/invalid
    """
    session = await redis_cache.get_session(session_id)
    if session:
        return session.get("user_id")
    return None


async def logout_user(session_id: str) -> bool:
    """
    Logout a user by destroying their session.

    Args:
        session_id: Session to destroy

    Returns:
        True if logged out, False if already logged out
    """
    return await redis_cache.destroy_session(session_id)


async def logout_all_devices(user_id: str) -> int:
    """
    Logout user from ALL devices.

    Args:
        user_id: User UUID

    Returns:
        Number of sessions destroyed
    """
    return await redis_cache.destroy_all_user_sessions(user_id)


# ==================== QUEUE CONVENIENCE FUNCTIONS ====================

async def enqueue_payment_reconciliation(user_id: str, transaction_id: str) -> bool:
    """
    Queue a payment reconciliation task.

    Args:
        user_id: User UUID
        transaction_id: Transaction ID to reconcile

    Returns:
        True if queued successfully
    """
    return await redis_cache.add_to_queue(
        "payment_reconciliation",
        {
            "user_id": user_id,
            "transaction_id": transaction_id,
            "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
        }
    )


async def dequeue_payment_reconciliation() -> Optional[dict]:
    """
    Dequeue a payment reconciliation task (non-blocking).

    Returns:
        Task dict if available, None if queue empty
    """
    return await redis_cache.get_from_queue("payment_reconciliation")


async def get_reconciliation_queue_status() -> dict:
    """
    Get status of payment reconciliation queue.

    Returns:
        Dict with queue length and pending items
    """
    length = await redis_cache.queue_length("payment_reconciliation")
    return {
        "queue_name": "payment_reconciliation",
        "pending_items": length,
        "status": "active" if length > 0 else "empty"
    }


async def enqueue_webhook_retry(
    webhook_type: str,
    user_id: str,
    event_data: dict
) -> bool:
    """
    Queue a webhook retry task.

    Args:
        webhook_type: Type of webhook (payment, autopay, etc.)
        user_id: User UUID
        event_data: Event data to retry

    Returns:
        True if queued successfully
    """
    return await redis_cache.add_to_queue(
        f"webhook_retry_{webhook_type}",
        {
            "user_id": user_id,
            "event_data": event_data,
            "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
            "retry_count": 0
        }
    )


async def dequeue_webhook_retry(webhook_type: str) -> Optional[dict]:
    """
    Dequeue a webhook retry task.

    Args:
        webhook_type: Type of webhook to retry

    Returns:
        Task dict if available, None if queue empty
    """
    return await redis_cache.get_from_queue(f"webhook_retry_{webhook_type}")


# ==================== PUB/SUB CONVENIENCE FUNCTIONS ====================

async def notify_payment_update(user_id: str, status: str, amount: float, transaction_id: str) -> int:
    """
    Notify user about payment status change.

    Args:
        user_id: User UUID
        status: Payment status (completed, failed, pending)
        amount: Payment amount
        transaction_id: Transaction ID

    Returns:
        Number of subscribers that received the notification
    """
    return await redis_cache.publish_to_user(
        user_id,
        "payment.updated",
        {
            "status": status,
            "amount": amount,
            "transaction_id": transaction_id
        }
    )


async def notify_subscription_event(user_id: str, event: str, plan_id: str) -> int:
    """
    Notify user about subscription event.

    Args:
        user_id: User UUID
        event: Event type (activated, cancelled, upgraded, etc.)
        plan_id: Subscription plan ID

    Returns:
        Number of subscribers that received the notification
    """
    return await redis_cache.publish_to_user(
        user_id,
        "subscription.event",
        {
            "event": event,
            "plan_id": plan_id
        }
    )


async def notify_security_alert(user_id: str, alert_type: str, message: str) -> int:
    """
    Notify user about security-related alert.

    Args:
        user_id: User UUID
        alert_type: Type of alert (login_attempt, token_revoked, etc.)
        message: Alert message

    Returns:
        Number of subscribers that received the alert
    """
    return await redis_cache.publish_to_user(
        user_id,
        "security.alert",
        {
            "alert_type": alert_type,
            "message": message
        }
    )


async def subscribe_to_user_events(user_id: str, *event_types: str) -> redis.client.PubSub:
    """
    Subscribe to events for a specific user.

    Args:
        user_id: User UUID to subscribe to
        *event_types: Event types to listen for (payment.updated, subscription.event, etc.)

    Returns:
        PubSub object for receiving messages
    """
    channels = [f"user:{user_id}:{event_type}" for event_type in event_types]
    return await redis_cache.subscribe(*channels)


class RedisCache:
    """
    Convenience wrapper for redis cache with simplified API.
    Used by content agents for caching generated content.
    """

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache using full key"""
        if not cache.redis:
            return None
        try:
            value = await cache.redis.get(f"raptorflow:{key}")
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning("Redis get failed", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        if not cache.redis:
            return False
        try:
            serialized = json.dumps(value)
            full_key = f"raptorflow:{key}"
            if ttl:
                await cache.redis.setex(full_key, ttl, serialized)
            else:
                await cache.redis.set(full_key, serialized)
            return True
        except Exception as e:
            logger.warning("Redis set failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not cache.redis:
            return False
        try:
            await cache.redis.delete(f"raptorflow:{key}")
            return True
        except Exception as e:
            logger.warning("Redis delete failed", key=key, error=str(e))
            return False


# Global redis_cache instance for content agents
redis_cache = RedisCache()
