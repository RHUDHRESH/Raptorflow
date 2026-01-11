# REDIS ARCHITECTURE

> Upstash Redis for Sessions, Cache, Rate Limiting, Queues

---

## 1. REDIS OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           UPSTASH REDIS                                     │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │    SESSIONS     │  │     CACHE       │  │   RATE LIMIT    │             │
│  │                 │  │                 │  │                 │             │
│  │ - Working mem   │  │ - Foundation    │  │ - API limits    │             │
│  │ - Auth sessions │  │ - ICPs          │  │ - Agent limits  │             │
│  │ - Approval      │  │ - Semantic      │  │ - Budget limits │             │
│  │   gates         │  │ - LLM responses │  │                 │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │     QUEUES      │  │    PUBSUB       │  │    COUNTERS     │             │
│  │                 │  │                 │  │                 │             │
│  │ - Agent tasks   │  │ - Real-time     │  │ - Usage tracking│             │
│  │ - Webhooks      │  │   updates       │  │ - Daily tokens  │             │
│  │ - Emails        │  │ - Notifications │  │ - Monthly cost  │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. UPSTASH SETUP

### 2.1 Environment Configuration

```env
# .env
UPSTASH_REDIS_URL=https://xxx-xxx.upstash.io
UPSTASH_REDIS_TOKEN=AXXXXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2.2 Redis Client

```python
# backend/core/redis.py
from upstash_redis import Redis
from upstash_redis.asyncio import Redis as AsyncRedis
import os
import json
from typing import Any, TypeVar, Generic
from datetime import timedelta

T = TypeVar('T')

class RedisClient:
    """Upstash Redis client wrapper with typed operations."""

    def __init__(self):
        self.url = os.getenv("UPSTASH_REDIS_URL")
        self.token = os.getenv("UPSTASH_REDIS_TOKEN")
        self._sync_client: Redis | None = None
        self._async_client: AsyncRedis | None = None

    @property
    def sync(self) -> Redis:
        """Get synchronous client."""
        if self._sync_client is None:
            self._sync_client = Redis(url=self.url, token=self.token)
        return self._sync_client

    @property
    def async_client(self) -> AsyncRedis:
        """Get asynchronous client."""
        if self._async_client is None:
            self._async_client = AsyncRedis(url=self.url, token=self.token)
        return self._async_client

    # ═══════════════════════════════════════════════════════════════════
    # BASIC OPERATIONS
    # ═══════════════════════════════════════════════════════════════════

    async def get(self, key: str) -> str | None:
        """Get string value."""
        return await self.async_client.get(key)

    async def set(
        self,
        key: str,
        value: str,
        ex: int | None = None,  # Expiry in seconds
        px: int | None = None,  # Expiry in milliseconds
        nx: bool = False,       # Only set if not exists
        xx: bool = False        # Only set if exists
    ) -> bool:
        """Set string value."""
        return await self.async_client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)

    async def delete(self, *keys: str) -> int:
        """Delete keys."""
        return await self.async_client.delete(*keys)

    async def exists(self, *keys: str) -> int:
        """Check if keys exist."""
        return await self.async_client.exists(*keys)

    async def expire(self, key: str, seconds: int) -> bool:
        """Set key expiry."""
        return await self.async_client.expire(key, seconds)

    # ═══════════════════════════════════════════════════════════════════
    # JSON OPERATIONS
    # ═══════════════════════════════════════════════════════════════════

    async def get_json(self, key: str) -> dict | list | None:
        """Get JSON value."""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_json(
        self,
        key: str,
        value: dict | list,
        ex: int | None = None
    ) -> bool:
        """Set JSON value."""
        return await self.set(key, json.dumps(value), ex=ex)

    # ═══════════════════════════════════════════════════════════════════
    # HASH OPERATIONS
    # ═══════════════════════════════════════════════════════════════════

    async def hget(self, key: str, field: str) -> str | None:
        """Get hash field."""
        return await self.async_client.hget(key, field)

    async def hset(self, key: str, field: str, value: str) -> int:
        """Set hash field."""
        return await self.async_client.hset(key, field, value)

    async def hgetall(self, key: str) -> dict:
        """Get all hash fields."""
        return await self.async_client.hgetall(key)

    async def hmset(self, key: str, mapping: dict) -> bool:
        """Set multiple hash fields."""
        return await self.async_client.hmset(key, mapping)

    async def hincrby(self, key: str, field: str, amount: int = 1) -> int:
        """Increment hash field."""
        return await self.async_client.hincrby(key, field, amount)

    async def hincrbyfloat(self, key: str, field: str, amount: float) -> float:
        """Increment hash field by float."""
        return await self.async_client.hincrbyfloat(key, field, amount)

    # ═══════════════════════════════════════════════════════════════════
    # LIST OPERATIONS (FOR QUEUES)
    # ═══════════════════════════════════════════════════════════════════

    async def lpush(self, key: str, *values: str) -> int:
        """Push to left of list."""
        return await self.async_client.lpush(key, *values)

    async def rpush(self, key: str, *values: str) -> int:
        """Push to right of list."""
        return await self.async_client.rpush(key, *values)

    async def lpop(self, key: str) -> str | None:
        """Pop from left of list."""
        return await self.async_client.lpop(key)

    async def rpop(self, key: str) -> str | None:
        """Pop from right of list."""
        return await self.async_client.rpop(key)

    async def lrange(self, key: str, start: int, end: int) -> list:
        """Get range from list."""
        return await self.async_client.lrange(key, start, end)

    async def llen(self, key: str) -> int:
        """Get list length."""
        return await self.async_client.llen(key)

    # ═══════════════════════════════════════════════════════════════════
    # COUNTER OPERATIONS
    # ═══════════════════════════════════════════════════════════════════

    async def incr(self, key: str) -> int:
        """Increment counter."""
        return await self.async_client.incr(key)

    async def incrby(self, key: str, amount: int) -> int:
        """Increment counter by amount."""
        return await self.async_client.incrby(key, amount)

    async def incrbyfloat(self, key: str, amount: float) -> float:
        """Increment counter by float."""
        return await self.async_client.incrbyfloat(key, amount)


# Singleton instance
_redis: RedisClient | None = None

def get_redis() -> RedisClient:
    global _redis
    if _redis is None:
        _redis = RedisClient()
    return _redis
```

---

## 3. KEY PATTERNS

```python
# backend/core/redis_keys.py

class RedisKeys:
    """Centralized Redis key patterns."""

    # ═══════════════════════════════════════════════════════════════════
    # SESSION KEYS
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def working_memory(session_id: str) -> str:
        """Working memory for agent session."""
        return f"wm:{session_id}"

    @staticmethod
    def approval_gate(gate_id: str) -> str:
        """Approval gate pending action."""
        return f"approval:{gate_id}"

    @staticmethod
    def onboarding_session(workspace_id: str) -> str:
        """Onboarding session state."""
        return f"onboarding:{workspace_id}"

    # ═══════════════════════════════════════════════════════════════════
    # CACHE KEYS
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def foundation_cache(workspace_id: str) -> str:
        """Cached foundation data."""
        return f"cache:foundation:{workspace_id}"

    @staticmethod
    def icps_cache(workspace_id: str) -> str:
        """Cached ICP profiles."""
        return f"cache:icps:{workspace_id}"

    @staticmethod
    def semantic_cache(workspace_id: str) -> str:
        """Semantic query cache (hash)."""
        return f"semantic:{workspace_id}"

    @staticmethod
    def llm_response_cache(query_hash: str) -> str:
        """Cached LLM response."""
        return f"llm:{query_hash}"

    # ═══════════════════════════════════════════════════════════════════
    # RATE LIMIT KEYS
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def rate_limit_api(user_id: str, endpoint: str) -> str:
        """API rate limit counter."""
        return f"rl:api:{user_id}:{endpoint}"

    @staticmethod
    def rate_limit_agent(user_id: str) -> str:
        """Agent execution rate limit."""
        return f"rl:agent:{user_id}"

    @staticmethod
    def rate_limit_minute(user_id: str) -> str:
        """Per-minute rate limit."""
        return f"rl:min:{user_id}"

    # ═══════════════════════════════════════════════════════════════════
    # USAGE TRACKING KEYS
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def usage_daily(user_id: str, date: str) -> str:
        """Daily usage counter. Date format: YYYY-MM-DD"""
        return f"usage:{user_id}:{date}"

    @staticmethod
    def usage_monthly(user_id: str, month: str) -> str:
        """Monthly usage counter. Month format: YYYY-MM"""
        return f"usage:{user_id}:{month}"

    @staticmethod
    def budget(user_id: str) -> str:
        """Current budget tracking."""
        return f"budget:{user_id}"

    # ═══════════════════════════════════════════════════════════════════
    # QUEUE KEYS
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def queue_agent_tasks() -> str:
        """Agent task queue."""
        return "queue:agent_tasks"

    @staticmethod
    def queue_webhooks() -> str:
        """Webhook processing queue."""
        return "queue:webhooks"

    @staticmethod
    def queue_emails() -> str:
        """Email sending queue."""
        return "queue:emails"

    # ═══════════════════════════════════════════════════════════════════
    # PREFERENCES KEYS
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def user_preferences(workspace_id: str) -> str:
        """User preferences (learned from feedback)."""
        return f"prefs:{workspace_id}"
```

---

## 4. SESSION MANAGEMENT

### 4.1 Working Memory

```python
# backend/services/session_manager.py
from core.redis import get_redis
from core.redis_keys import RedisKeys
from dataclasses import dataclass, asdict
from typing import Any
import json

@dataclass
class WorkingMemoryState:
    session_id: str
    workspace_id: str
    user_id: str

    current_agent: str | None = None
    current_task: str | None = None

    recent_messages: list[dict] = None
    foundation_summary: str | None = None
    active_icps: list[dict] = None

    pending_approvals: list[dict] = None
    last_output: dict | None = None

    def __post_init__(self):
        if self.recent_messages is None:
            self.recent_messages = []
        if self.active_icps is None:
            self.active_icps = []
        if self.pending_approvals is None:
            self.pending_approvals = []

class SessionManager:
    """Manages working memory sessions in Redis."""

    def __init__(self):
        self.redis = get_redis()
        self.session_ttl = 3600  # 1 hour

    async def create_session(
        self,
        session_id: str,
        workspace_id: str,
        user_id: str
    ) -> WorkingMemoryState:
        """Create a new session."""
        state = WorkingMemoryState(
            session_id=session_id,
            workspace_id=workspace_id,
            user_id=user_id
        )

        await self.save_session(state)
        return state

    async def get_session(self, session_id: str) -> WorkingMemoryState | None:
        """Get session state."""
        key = RedisKeys.working_memory(session_id)
        data = await self.redis.get_json(key)

        if data:
            return WorkingMemoryState(**data)
        return None

    async def save_session(self, state: WorkingMemoryState):
        """Save session state."""
        key = RedisKeys.working_memory(state.session_id)

        # Limit recent messages
        state.recent_messages = state.recent_messages[-10:]

        await self.redis.set_json(key, asdict(state), ex=self.session_ttl)

    async def update_session(
        self,
        session_id: str,
        **updates
    ) -> WorkingMemoryState | None:
        """Update session fields."""
        state = await self.get_session(session_id)
        if not state:
            return None

        for key, value in updates.items():
            if hasattr(state, key):
                setattr(state, key, value)

        await self.save_session(state)
        return state

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):
        """Add message to session."""
        state = await self.get_session(session_id)
        if state:
            state.recent_messages.append({
                "role": role,
                "content": content
            })
            await self.save_session(state)

    async def delete_session(self, session_id: str):
        """Delete session."""
        key = RedisKeys.working_memory(session_id)
        await self.redis.delete(key)

    async def extend_session(self, session_id: str, extra_seconds: int = 3600):
        """Extend session TTL."""
        key = RedisKeys.working_memory(session_id)
        await self.redis.expire(key, self.session_ttl + extra_seconds)
```

---

## 5. CACHING

### 5.1 Foundation Cache

```python
# backend/services/cache_manager.py
from core.redis import get_redis
from core.redis_keys import RedisKeys
from core.database import get_supabase_client

class CacheManager:
    """Manages Redis caching for frequently accessed data."""

    def __init__(self):
        self.redis = get_redis()

        # TTLs
        self.foundation_ttl = 3600  # 1 hour
        self.icps_ttl = 3600
        self.semantic_ttl = 86400  # 24 hours

    # ═══════════════════════════════════════════════════════════════════
    # FOUNDATION CACHE
    # ═══════════════════════════════════════════════════════════════════

    async def get_foundation(self, workspace_id: str) -> dict | None:
        """Get foundation from cache or database."""
        key = RedisKeys.foundation_cache(workspace_id)

        # Try cache first
        cached = await self.redis.get_json(key)
        if cached:
            return cached

        # Load from database
        supabase = get_supabase_client()
        result = supabase.table("foundations").select(
            "summary, brand_voice, messaging_guardrails, soundbite_library"
        ).eq("workspace_id", workspace_id).single().execute()

        if result.data:
            # Cache it
            await self.redis.set_json(key, result.data, ex=self.foundation_ttl)
            return result.data

        return None

    async def invalidate_foundation(self, workspace_id: str):
        """Invalidate foundation cache after update."""
        key = RedisKeys.foundation_cache(workspace_id)
        await self.redis.delete(key)

    # ═══════════════════════════════════════════════════════════════════
    # ICP CACHE
    # ═══════════════════════════════════════════════════════════════════

    async def get_icps(self, workspace_id: str) -> list[dict]:
        """Get ICPs from cache or database."""
        key = RedisKeys.icps_cache(workspace_id)

        cached = await self.redis.get_json(key)
        if cached:
            return cached

        supabase = get_supabase_client()
        result = supabase.table("icp_profiles").select("*").eq(
            "workspace_id", workspace_id
        ).execute()

        if result.data:
            await self.redis.set_json(key, result.data, ex=self.icps_ttl)
            return result.data

        return []

    async def invalidate_icps(self, workspace_id: str):
        """Invalidate ICP cache after update."""
        key = RedisKeys.icps_cache(workspace_id)
        await self.redis.delete(key)

    # ═══════════════════════════════════════════════════════════════════
    # SEMANTIC CACHE (for LLM responses)
    # ═══════════════════════════════════════════════════════════════════

    async def get_semantic_cached(
        self,
        workspace_id: str,
        query_hash: str
    ) -> dict | None:
        """Get semantically cached LLM response."""
        key = RedisKeys.semantic_cache(workspace_id)
        return await self.redis.hget(key, query_hash)

    async def set_semantic_cache(
        self,
        workspace_id: str,
        query_hash: str,
        response: dict
    ):
        """Cache LLM response."""
        key = RedisKeys.semantic_cache(workspace_id)
        await self.redis.hset(key, query_hash, json.dumps(response))
        await self.redis.expire(key, self.semantic_ttl)
```

---

## 6. RATE LIMITING

```python
# backend/services/rate_limiter.py
from core.redis import get_redis
from core.redis_keys import RedisKeys
from fastapi import HTTPException
from datetime import datetime

class RateLimiter:
    """Redis-based rate limiting."""

    def __init__(self):
        self.redis = get_redis()

        # Default limits
        self.limits = {
            "api": {"requests": 100, "window": 60},      # 100 req/min
            "agent": {"requests": 20, "window": 60},     # 20 agent calls/min
            "daily": {"requests": 1000, "window": 86400} # 1000/day
        }

    async def check_limit(
        self,
        user_id: str,
        limit_type: str = "api",
        endpoint: str = "default"
    ) -> bool:
        """Check if request is within rate limit."""

        config = self.limits.get(limit_type, self.limits["api"])

        if limit_type == "api":
            key = RedisKeys.rate_limit_api(user_id, endpoint)
        elif limit_type == "agent":
            key = RedisKeys.rate_limit_agent(user_id)
        else:
            key = RedisKeys.rate_limit_minute(user_id)

        # Get current count
        count = await self.redis.get(key)
        count = int(count) if count else 0

        if count >= config["requests"]:
            return False

        # Increment
        await self.redis.incr(key)

        # Set expiry if first request
        if count == 0:
            await self.redis.expire(key, config["window"])

        return True

    async def enforce_limit(
        self,
        user_id: str,
        limit_type: str = "api",
        endpoint: str = "default"
    ):
        """Enforce rate limit, raise exception if exceeded."""

        allowed = await self.check_limit(user_id, limit_type, endpoint)

        if not allowed:
            config = self.limits.get(limit_type, self.limits["api"])
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {config['requests']} requests per {config['window']} seconds."
            )

    async def get_remaining(
        self,
        user_id: str,
        limit_type: str = "api",
        endpoint: str = "default"
    ) -> dict:
        """Get remaining requests and reset time."""

        config = self.limits.get(limit_type, self.limits["api"])

        if limit_type == "api":
            key = RedisKeys.rate_limit_api(user_id, endpoint)
        elif limit_type == "agent":
            key = RedisKeys.rate_limit_agent(user_id)
        else:
            key = RedisKeys.rate_limit_minute(user_id)

        count = await self.redis.get(key)
        count = int(count) if count else 0

        ttl = await self.redis.async_client.ttl(key)

        return {
            "limit": config["requests"],
            "remaining": max(0, config["requests"] - count),
            "reset_in_seconds": max(0, ttl)
        }
```

---

## 7. USAGE TRACKING

```python
# backend/services/usage_tracker.py
from core.redis import get_redis
from core.redis_keys import RedisKeys
from core.database import get_supabase_client
from datetime import datetime, date

class UsageTracker:
    """Track usage and enforce budget limits."""

    def __init__(self):
        self.redis = get_redis()

    async def record_usage(
        self,
        user_id: str,
        workspace_id: str,
        tokens_input: int,
        tokens_output: int,
        cost_usd: float,
        agent_type: str
    ):
        """Record usage in Redis and database."""

        today = date.today().isoformat()
        month = today[:7]  # YYYY-MM

        # Update daily counter in Redis
        daily_key = RedisKeys.usage_daily(user_id, today)
        await self.redis.hincrbyfloat(daily_key, "tokens_input", tokens_input)
        await self.redis.hincrbyfloat(daily_key, "tokens_output", tokens_output)
        await self.redis.hincrbyfloat(daily_key, "cost_usd", cost_usd)
        await self.redis.hincrby(daily_key, "requests", 1)
        await self.redis.hincrby(daily_key, f"agent:{agent_type}", 1)
        await self.redis.expire(daily_key, 86400 * 2)  # 2 days

        # Update monthly counter
        monthly_key = RedisKeys.usage_monthly(user_id, month)
        await self.redis.hincrbyfloat(monthly_key, "cost_usd", cost_usd)
        await self.redis.expire(monthly_key, 86400 * 35)  # 35 days

        # Async save to database (can be done in background)
        await self._save_to_database(
            user_id, workspace_id, today,
            tokens_input, tokens_output, cost_usd, agent_type
        )

    async def _save_to_database(
        self,
        user_id: str,
        workspace_id: str,
        date_str: str,
        tokens_input: int,
        tokens_output: int,
        cost_usd: float,
        agent_type: str
    ):
        """Save usage record to database."""
        supabase = get_supabase_client()

        # Upsert daily record
        supabase.table("usage_records").upsert({
            "user_id": user_id,
            "workspace_id": workspace_id,
            "date": date_str,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "cost_usd": cost_usd,
            "agent_usage": {agent_type: 1}
        }, on_conflict="user_id,date").execute()

    async def get_daily_usage(self, user_id: str, date_str: str = None) -> dict:
        """Get daily usage summary."""
        if not date_str:
            date_str = date.today().isoformat()

        key = RedisKeys.usage_daily(user_id, date_str)
        data = await self.redis.hgetall(key)

        return {
            "date": date_str,
            "tokens_input": int(float(data.get("tokens_input", 0))),
            "tokens_output": int(float(data.get("tokens_output", 0))),
            "cost_usd": float(data.get("cost_usd", 0)),
            "requests": int(data.get("requests", 0))
        }

    async def get_monthly_usage(self, user_id: str, month: str = None) -> dict:
        """Get monthly usage summary."""
        if not month:
            month = date.today().isoformat()[:7]

        key = RedisKeys.usage_monthly(user_id, month)
        data = await self.redis.hgetall(key)

        return {
            "month": month,
            "cost_usd": float(data.get("cost_usd", 0))
        }

    async def check_budget(self, user_id: str, estimated_cost: float) -> dict:
        """Check if user can afford the operation."""

        # Get user's budget limit
        supabase = get_supabase_client()
        user = supabase.table("users").select(
            "budget_limit_monthly"
        ).eq("id", user_id).single().execute()

        budget_limit = float(user.data.get("budget_limit_monthly", 1.0))

        # Get current month usage
        month = date.today().isoformat()[:7]
        usage = await self.get_monthly_usage(user_id, month)
        current_usage = usage["cost_usd"]

        remaining = budget_limit - current_usage
        can_afford = remaining >= estimated_cost

        return {
            "can_afford": can_afford,
            "budget_limit": budget_limit,
            "current_usage": current_usage,
            "remaining": remaining,
            "estimated_cost": estimated_cost
        }

    async def enforce_budget(self, user_id: str, estimated_cost: float):
        """Enforce budget limit."""
        budget = await self.check_budget(user_id, estimated_cost)

        if not budget["can_afford"]:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=402,
                detail=f"Budget exceeded. Remaining: ${budget['remaining']:.4f}, Required: ${estimated_cost:.4f}"
            )
```

---

## 8. QUEUES

```python
# backend/services/queue_manager.py
from core.redis import get_redis
from core.redis_keys import RedisKeys
import json
import uuid
from datetime import datetime

class QueueManager:
    """Redis-based job queues."""

    def __init__(self):
        self.redis = get_redis()

    async def enqueue(
        self,
        queue_name: str,
        job_type: str,
        payload: dict,
        priority: int = 5
    ) -> str:
        """Add job to queue."""
        job_id = str(uuid.uuid4())

        job = {
            "id": job_id,
            "type": job_type,
            "payload": payload,
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }

        key = f"queue:{queue_name}"
        await self.redis.rpush(key, json.dumps(job))

        return job_id

    async def dequeue(self, queue_name: str) -> dict | None:
        """Get next job from queue."""
        key = f"queue:{queue_name}"
        job_data = await self.redis.lpop(key)

        if job_data:
            return json.loads(job_data)
        return None

    async def queue_length(self, queue_name: str) -> int:
        """Get queue length."""
        key = f"queue:{queue_name}"
        return await self.redis.llen(key)

    # Convenience methods
    async def enqueue_agent_task(self, workspace_id: str, task: dict) -> str:
        """Queue an agent task."""
        return await self.enqueue(
            "agent_tasks",
            "agent_execution",
            {"workspace_id": workspace_id, **task}
        )

    async def enqueue_webhook(self, webhook_type: str, payload: dict) -> str:
        """Queue a webhook for processing."""
        return await self.enqueue(
            "webhooks",
            webhook_type,
            payload
        )

    async def enqueue_email(
        self,
        to: str,
        subject: str,
        body: str,
        template: str = None
    ) -> str:
        """Queue an email for sending."""
        return await self.enqueue(
            "emails",
            "send_email",
            {"to": to, "subject": subject, "body": body, "template": template}
        )
```

---

## 9. INITIALIZATION

```python
# backend/core/startup.py
from core.redis import get_redis

async def verify_redis_connection():
    """Verify Redis is accessible on startup."""
    redis = get_redis()

    try:
        # Test connection
        await redis.set("health:check", "ok", ex=10)
        value = await redis.get("health:check")

        if value != "ok":
            raise Exception("Redis health check failed")

        print("✓ Redis connection verified")
        return True

    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        raise


# Call in FastAPI startup
@app.on_event("startup")
async def startup():
    await verify_redis_connection()
```
