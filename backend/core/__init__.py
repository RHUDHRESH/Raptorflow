"""
Infrastructure Module - Core infrastructure components.

Provides database, cache, storage, and rate limiting utilities.

Architecture:
├── database/   - Database connections and pool management
├── cache/      - Redis caching layer
├── storage/    - File storage (Supabase Storage, etc.)
├── rate_limiting/ - Rate limiting utilities
└── tasks/     - Async task queue
"""

from backend.core.database import (
    DatabasePool,
    get_db_client,
    get_pool,
    close_pool,
    execute_query,
    execute_one,
    execute_write,
    get_pool_stats,
    get_supabase_client,
    get_supabase_admin,
    reset_supabase_clients,
    query_monitor,
    QueryMonitor,
)
from backend.core.cache import CacheClient, get_cache_client
from backend.core.cache.redis import (
    get_redis_client,
    reset_redis_client,
)
from backend.core.cache.decorator import cached, invalidate_cache
from backend.core.storage import StorageClient, get_storage_client
from backend.core.storage.manager import StorageManager, get_storage_manager
from backend.core.rate_limiting import RateLimiter
from backend.core.tasks.async_tasks import (
    TaskQueue,
    task_queue,
    run_in_background,
)

__all__ = [
    "DatabasePool",
    "get_db_client",
    "get_pool",
    "close_pool",
    "execute_query",
    "execute_one",
    "execute_write",
    "get_pool_stats",
    "get_supabase_client",
    "get_supabase_admin",
    "reset_supabase_clients",
    "QueryMonitor",
    "query_monitor",
    "CacheClient",
    "get_cache_client",
    "get_redis_client",
    "reset_redis_client",
    "cached",
    "invalidate_cache",
    "StorageClient",
    "get_storage_client",
    "StorageManager",
    "get_storage_manager",
    "RateLimiter",
    "TaskQueue",
    "task_queue",
    "run_in_background",
]
