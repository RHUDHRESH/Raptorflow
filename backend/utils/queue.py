"""
Redis-based task queue for async agent operations.

Includes:
- Traditional task queue (enqueue/dequeue with priority levels)
- Pub/Sub messaging (integrated with RaptorBus)
"""

import json
import asyncio
from typing import Any, Callable, Dict, Optional, Union
from enum import Enum
import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
from backend.config.settings import settings
import structlog

logger = structlog.get_logger()


class Priority(str, Enum):
    """Task priority levels"""
    HIGH = "high"  # Time-sensitive posts, user-facing operations
    MEDIUM = "medium"  # Content drafts, research
    LOW = "low"  # Background analytics, ambient search


class TaskQueue:
    """Async Redis task queue with priority support"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self._running = False
        self._workers: Dict[Priority, asyncio.Task] = {}
        
    async def connect(self):
        """Establish Redis connection"""
        try:
            self.redis = await redis.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("Task queue connected")
        except Exception as e:
            logger.error("Failed to connect to Redis queue", error=str(e))
            raise
            
    async def disconnect(self):
        """Close Redis connection and stop workers"""
        self._running = False
        
        # Cancel all workers
        for worker in self._workers.values():
            worker.cancel()
            
        # Wait for workers to finish
        if self._workers:
            await asyncio.gather(*self._workers.values(), return_exceptions=True)
            
        if self.redis:
            await self.redis.close()
            logger.info("Task queue disconnected")
    
    def _get_queue_name(self, priority: Priority) -> str:
        """Get Redis list name for priority"""
        return f"raptorflow:queue:{priority.value}"
    
    async def enqueue(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: Priority = Priority.MEDIUM,
        correlation_id: Optional[str] = None
    ) -> str:
        """Add task to queue"""
        if not self.redis:
            raise RuntimeError("Queue not connected")
            
        task = {
            "type": task_type,
            "payload": payload,
            "correlation_id": correlation_id,
            "priority": priority.value
        }
        
        queue_name = self._get_queue_name(priority)
        task_json = json.dumps(task)
        
        await self.redis.rpush(queue_name, task_json)
        logger.info(
            "Task enqueued",
            task_type=task_type,
            priority=priority.value,
            correlation_id=correlation_id
        )
        
        return correlation_id or "no-correlation-id"
    
    async def dequeue(self, priority: Priority, timeout: int = 1) -> Optional[Dict[str, Any]]:
        """Remove and return task from queue (blocking)"""
        if not self.redis:
            return None
            
        queue_name = self._get_queue_name(priority)
        
        try:
            # BLPOP returns tuple (queue_name, value) or None
            result = await self.redis.blpop([queue_name], timeout=timeout)
            if result:
                _, task_json = result
                task = json.loads(task_json)
                logger.debug(
                    "Task dequeued",
                    task_type=task.get("type"),
                    priority=priority.value
                )
                return task
        except Exception as e:
            logger.error("Failed to dequeue task", error=str(e), priority=priority.value)
            
        return None
    
    async def start_workers(
        self,
        handlers: Dict[str, Callable],
        workers_per_priority: int = 2
    ):
        """Start background workers for each priority level"""
        self._running = True
        
        for priority in Priority:
            for i in range(workers_per_priority):
                worker_name = f"worker-{priority.value}-{i}"
                task = asyncio.create_task(
                    self._worker_loop(priority, handlers, worker_name)
                )
                self._workers[f"{priority.value}_{i}"] = task
                
        logger.info(
            "Workers started",
            total_workers=len(self._workers),
            workers_per_priority=workers_per_priority
        )
    
    async def _worker_loop(
        self,
        priority: Priority,
        handlers: Dict[str, Callable],
        worker_name: str
    ):
        """Worker loop that processes tasks"""
        logger.info("Worker started", name=worker_name, priority=priority.value)
        
        while self._running:
            try:
                task = await self.dequeue(priority, timeout=1)
                if not task:
                    continue
                    
                task_type = task.get("type")
                handler = handlers.get(task_type)
                
                if not handler:
                    logger.warning(
                        "No handler for task type",
                        task_type=task_type,
                        worker=worker_name
                    )
                    continue
                
                # Execute handler
                try:
                    await handler(task["payload"], task.get("correlation_id"))
                    logger.info(
                        "Task completed",
                        task_type=task_type,
                        worker=worker_name
                    )
                except Exception as e:
                    logger.error(
                        "Task handler failed",
                        task_type=task_type,
                        error=str(e),
                        worker=worker_name
                    )
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Worker error", error=str(e), worker=worker_name)
                await asyncio.sleep(1)  # Brief pause before retry
                
        logger.info("Worker stopped", name=worker_name)

    # ========================================================================
    # PUB/SUB METHODS (integrated with RaptorBus)
    # ========================================================================

    async def publish(self, channel: str, message: Union[str, Dict]) -> int:
        """
        Publish a message to a Redis channel.

        Args:
            channel: Channel name
            message: Message (string or dict, which will be JSON serialized)

        Returns:
            Number of subscribers that received the message
        """
        if not self.redis:
            raise RuntimeError("Queue not connected")

        if isinstance(message, dict):
            message = json.dumps(message)

        num_subscribers = await self.redis.publish(channel, message)

        logger.debug(
            "Message published",
            channel=channel,
            subscribers=num_subscribers
        )

        return num_subscribers

    async def subscribe(self, channels: Union[str, list]) -> redis.client.PubSub:
        """
        Subscribe to one or more channels.

        Args:
            channels: Single channel name or list of channel names

        Returns:
            PubSub object for listening to messages

        Usage:
            pubsub = await queue.subscribe(["channel1", "channel2"])
            async for message in pubsub.listen():
                print(message)
        """
        if not self.redis:
            raise RuntimeError("Queue not connected")

        pubsub = self.redis.pubsub()

        if isinstance(channels, str):
            channels = [channels]

        await pubsub.subscribe(*channels)

        logger.debug("Subscribed to channels", channels=channels)

        return pubsub

    async def psubscribe(self, patterns: Union[str, list]) -> redis.client.PubSub:
        """
        Subscribe to channels matching patterns.

        Args:
            patterns: Single pattern or list of patterns (e.g., "sys.alert.*")

        Returns:
            PubSub object for listening to messages
        """
        if not self.redis:
            raise RuntimeError("Queue not connected")

        pubsub = self.redis.pubsub()

        if isinstance(patterns, str):
            patterns = [patterns]

        await pubsub.psubscribe(*patterns)

        logger.debug("Subscribed to patterns", patterns=patterns)

        return pubsub

    async def publish_and_persist(
        self,
        channel: str,
        message: Dict,
        ttl_seconds: int = 3600,
    ) -> str:
        """
        Publish a message and persist it for potential replay.

        Args:
            channel: Channel name
            message: Message dict
            ttl_seconds: How long to keep message in cache

        Returns:
            Unique message ID
        """
        from uuid import uuid4

        if not self.redis:
            raise RuntimeError("Queue not connected")

        message_id = str(uuid4())

        # Publish
        await self.publish(channel, message)

        # Persist
        cache_key = f"msg:{channel}:{message_id}"
        await self.redis.setex(
            cache_key,
            ttl_seconds,
            json.dumps(message)
        )

        logger.debug(
            "Message published and persisted",
            channel=channel,
            message_id=message_id,
            ttl=ttl_seconds
        )

        return message_id


# Global queue instance
redis_queue = TaskQueue()
# Legacy alias for backward compatibility
queue = redis_queue

