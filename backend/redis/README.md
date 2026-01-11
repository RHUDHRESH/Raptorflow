# Redis Services for Raptorflow Backend

This directory contains the Redis-based services that power the Raptorflow backend system. Redis is used for caching, session management, rate limiting, job queuing, and real-time communication.

## Overview

The Redis layer provides:
- **Session Management**: User session storage and tracking
- **Caching**: Application-level caching with TTL support
- **Rate Limiting**: API rate limiting with sliding windows
- **Job Queuing**: Background job processing with priority queues
- **Pub/Sub**: Real-time messaging and event distribution
- **Distributed Locks**: Coordination and synchronization
- **Atomic Operations**: Thread-safe Redis operations
- **Usage Tracking**: Token and cost usage monitoring

## Architecture

### Key Components

```
redis/
├── client.py              # Redis client wrapper
├── config.py              # Configuration and settings
├── keys.py                # Key pattern definitions
├── session.py              # Session management
├── session_models.py       # Session data models
├── cache.py                # Caching service
├── cache_decorators.py     # Cache decorators
├── rate_limit.py           # Rate limiting service
├── rate_limit_config.py    # Rate limit configurations
├── usage.py                # Usage tracking
├── usage_models.py         # Usage data models
├── queue.py                # Job queue service
├── queue_models.py         # Queue data models
├── worker.py               # Queue worker
├── worker_models.py        # Worker data models
├── pubsub.py               # Pub/Sub messaging
├── locks.py                # Distributed locks
├── atomic.py               # Atomic operations
├── pipeline.py             # Redis pipeline operations
├── lua_scripts.py          # Lua scripts for atomic operations
├── ttl_manager.py          # TTL management
├── metrics.py              # Redis metrics collection
├── health.py               # Health checking
├── backup.py               # Backup and restore
├── cleanup.py              # Cleanup operations
└── README.md               # This file
```

## Configuration

### Environment Variables

```bash
# Redis Configuration
UPSTASH_REDIS_URL=redis://your-redis-url:6379
UPSTASH_REDIS_TOKEN=your-redis-token
REDIS_KEY_PREFIX=raptorflow:
REDIS_DEFAULT_TTL=3600
REDIS_MAX_CONNECTIONS=10
```

### Key Patterns

All Redis keys follow a consistent pattern:

```
session:{session_id}              # User sessions
cache:{workspace_id}:{key}        # Cache entries
rate:{user_id}:{endpoint}         # Rate limiting
queue:{queue_name}                # Job queues
pubsub:{channel}                   # Pub/Sub channels
lock:{resource}                    # Distributed locks
usage:{workspace_id}:{period}      # Usage tracking
```

## Usage Examples

### Session Management

```python
from redis.session import SessionService
from redis.session_models import SessionData

session_service = SessionService()

# Create session
session_id = await session_service.create_session(
    user_id="user-123",
    workspace_id="workspace-456",
    metadata={"source": "web"}
)

# Get session
session_data = await session_service.get_session(session_id)

# Update session
await session_service.update_session(session_id, {
    "current_agent": "icp_architect",
    "last_activity": datetime.utcnow()
})

# Extend session
await session_service.extend_session(session_id, 1800)  # 30 minutes

# Delete session
await session_service.delete_session(session_id)
```

### Caching

```python
from redis.cache import CacheService

cache_service = CacheService()

# Set cache
await cache_service.set("workspace-123", "user_profile", profile_data, ttl=3600)

# Get cache
profile = await cache_service.get("workspace-123", "user_profile")

# Get or set with factory function
profile = await cache_service.get_or_set(
    "workspace-123",
    "user_profile",
    lambda: fetch_user_profile("user-123"),
    ttl=3600
)

# Clear workspace cache
await cache_service.clear_workspace("workspace-123")
```

### Rate Limiting

```python
from redis.rate_limit import RateLimitService

rate_limit_service = RateLimitService()

# Check rate limit
result = await rate_limit_service.check_limit(
    user_id="user-123",
    endpoint="/api/v1/agents/execute",
    limit=10,
    window_seconds=60
)

if result.allowed:
    # Process request
    pass
else:
    # Rate limit exceeded
    print(f"Rate limit exceeded. Reset at: {result.reset_at}")

# Record request
await rate_limit_service.record_request("user-123", "/api/v1/agents/execute")
```

### Job Queue

```python
from redis.queue import QueueService

queue_service = QueueService()

# Enqueue job
job_id = await queue_service.enqueue(
    queue_name="default",
    job_data={"task": "process_document", "document_id": "doc-123"},
    priority=1
)

# Dequeue job
job = await queue_service.dequeue("default")

# Peek at queue
next_job = await queue_service.peek("default")

# Get queue length
length = await queue_service.queue_length("default")

# Clear queue
await queue_service.clear_queue("default")
```

### Distributed Locks

```python
from redis.locks import DistributedLock

lock = DistributedLock()

# Acquire lock
acquired = await lock.acquire("resource_name", timeout=30)

if acquired:
    try:
        # Critical section
        await perform_critical_operation()
    finally:
        # Release lock
        await lock.release("resource_name")

# Use context manager
async with lock("resource_name", timeout=30):
    await perform_critical_operation()
```

### Pub/Sub Messaging

```python
from redis.pubsub import PubSubService

pubsub = PubSubService()

# Publish message
await pubsub.publish("events", {"type": "user_created", "user_id": "user-123"})

# Subscribe to messages
async def message_handler(channel, message):
    data = json.loads(message)
    print(f"Received on {channel}: {data}")

await pubsub.subscribe("events", message_handler)
```

## Advanced Features

### Lua Scripts

Redis Lua scripts provide atomic operations:

```python
from redis.lua_scripts import LuaScripts

lua_scripts = LuaScripts()

# Rate limiting script
result = await redis_client.eval(
    lua_scripts.RATE_LIMIT_SCRIPT,
    1,  # Number of keys
    "rate:user-123:/api/v1/test",  # Key
    10,  # Limit
    60,  # Window
    int(time.time())  # Current time
)
```

### Pipeline Operations

Batch multiple Redis operations:

```python
from redis.pipeline import RedisPipeline

pipeline = RedisPipeline()

# Batch operations
operations = [
    ("SET", "key1", "value1"),
    ("SET", "key2", "value2"),
    ("INCR", "counter"),
    ("EXPIRE", "key1", 3600),
]

results = await pipeline.execute(operations)
```

### Atomic Operations

Thread-safe operations:

```python
from redis.atomic import AtomicOperations

atomic = AtomicOperations()

# Compare and set
success = await atomic.compare_and_set("key", "expected", "new_value")

# Get and set
old_value = await atomic.get_and_set("key", "new_value")

# Increment with atomicity
new_value = await atomic.increment("counter", amount=5)
```

## Performance Optimization

### Connection Pooling

```python
from redis.client import RedisClient

# Client automatically manages connection pool
redis_client = RedisClient()

# Configure pool size in settings
REDIS_MAX_CONNECTIONS = 20
```

### Memory Management

```python
from redis.ttl_manager import TTLManager

ttl_manager = TTLManager()

# Set TTL with automatic cleanup
await ttl_manager.set_ttl("key", 3600)

# Clean up expired keys
await ttl_manager.cleanup_expired()
```

### Monitoring

```python
from redis.metrics import RedisMetrics

metrics = RedisMetrics()

# Get Redis metrics
redis_metrics = await metrics.get_metrics()

print(f"Memory used: {redis_metrics['memory_used']}")
print(f"Keys count: {redis_metrics['keys_count']}")
print(f"Ops per second: {redis_metrics['ops_per_second']}")
```

## Testing

### Unit Tests

```python
import pytest
from redis.session import SessionService

@pytest.mark.asyncio
async def test_session_creation():
    session_service = SessionService()

    session_id = await session_service.create_session(
        user_id="test-user",
        workspace_id="test-workspace"
    )

    assert session_id is not None
    assert len(session_id) == 36  # UUID length
```

### Mock Testing

```python
from unittest.mock import AsyncMock
from redis.client import RedisClient

# Mock Redis client
mock_redis = AsyncMock()
mock_redis.set.return_value = True

# Use mock in tests
session_service = SessionService(mock_redis)
```

## Health Checking

```python
from redis.health import RedisHealthChecker

health_checker = RedisHealthChecker()

# Check connection
is_connected = await health_checker.check_connection()

# Check latency
latency_ms = await health_checker.check_latency()

# Check memory
memory_status = await health_checker.check_memory()
```

## Backup and Restore

```python
from redis.backup import RedisBackup

backup = RedisBackup()

# Backup all keys
backup_data = await backup.backup_keys("*")

# Restore keys
await backup.restore_keys(backup_data)

# Export to file
await backup.export_to_file("*", "backup.json")
```

## Cleanup and Maintenance

```python
from redis.cleanup import RedisCleanup

cleanup = RedisCleanup()

# Clean expired sessions
cleaned_sessions = await cleanup.cleanup_expired_sessions()

# Clean old cache
cleaned_cache = await cleanup.cleanup_old_cache()

# Clean stale locks
cleaned_locks = await cleanup.cleanup_stale_locks()
```

## Error Handling

All Redis services include comprehensive error handling:

```python
from redis.client import RedisClient

redis_client = RedisClient()

try:
    result = await redis_client.get("nonexistent_key")
except RedisConnectionError:
    logger.error("Redis connection failed")
except RedisTimeoutError:
    logger.error("Redis operation timed out")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

## Security

### Authentication

Redis connections use secure authentication:

```python
# Upstash Redis with token
UPSTASH_REDIS_URL="https://your-redis.upstash.com"
UPSTASH_REDIS_TOKEN="your-secure-token"
```

### Data Encryption

Sensitive data should be encrypted before storage:

```python
import json
from cryptography.fernet import Fernet

# Encrypt sensitive data
key = Fernet.generate_key()
fernet = Fernet(key)
encrypted_data = fernet.encrypt(json.dumps(data).encode())

# Store encrypted data
await redis_client.set("sensitive:data", encrypted_data)
```

## Monitoring and Alerting

### Metrics Collection

```python
from redis.metrics import RedisMetrics

metrics = RedisMetrics()

# Collect metrics
redis_metrics = await metrics.get_metrics()

# Alert on high memory usage
if redis_metrics['memory_used'] > threshold:
    await send_alert("High Redis memory usage")
```

### Health Monitoring

```python
from redis.health import RedisHealthChecker

health_checker = RedisHealthChecker()

# Continuous health monitoring
async def monitor_redis_health():
    while True:
        health = await health_checker.check_connection()
        if not health:
            await send_alert("Redis health check failed")
        await asyncio.sleep(60)  # Check every minute
```

## Best Practices

### Key Naming

- Use consistent key patterns
- Include namespace prefixes
- Use descriptive names
- Avoid key collisions

### TTL Management

- Set appropriate TTL for all keys
- Use shorter TTL for temporary data
- Implement cleanup for expired keys

### Error Handling

- Always handle connection errors
- Implement retry logic for transient failures
- Log errors with context

### Performance

- Use pipelines for batch operations
- Implement connection pooling
- Monitor memory usage
- Use Lua scripts for atomic operations

## Troubleshooting

### Common Issues

1. **Connection Errors**: Check Redis URL and token
2. **Memory Issues**: Monitor key count and TTL
3. **Performance Issues**: Check for blocking operations
4. **Data Consistency**: Use atomic operations

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Debug Redis operations
redis_client = RedisClient()
redis_client.debug = True
```

## Contributing

When adding new Redis services:

1. Follow existing code patterns
2. Include comprehensive error handling
3. Add unit tests
4. Update documentation
5. Consider performance implications

## Support

For Redis-related issues:
1. Check Redis logs
2. Verify connection configuration
3. Monitor memory usage
4. Review key patterns and TTL settings

For code-related issues:
1. Check error messages and logs
2. Review documentation
3. Create issue with reproduction steps
4. Include relevant configuration details
