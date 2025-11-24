"""
Context Bus for Shared State Management

Provides a shared scratchpad for agents collaborating on the same task.
Enables real-time coordination and resource locking.
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import redis


class ContextBus:
    """Shared context for multi-agent workflows"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hour

    def set_context(
        self,
        correlation_id: str,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set a context variable"""

        if ttl is None:
            ttl = self.default_ttl

        ctx_key = f"context:{correlation_id}:{key}"

        # Serialize value
        if isinstance(value, dict):
            serialized = json.dumps(value)
        elif isinstance(value, list):
            serialized = json.dumps(value)
        elif isinstance(value, (str, int, float, bool)):
            serialized = json.dumps(value)
        else:
            # Try to convert to JSON-serializable format
            serialized = json.dumps(value.__dict__ if hasattr(value, '__dict__') else str(value))

        self.redis.setex(ctx_key, ttl, serialized)
        return True

    def get_context(
        self,
        correlation_id: str,
        key: str,
        default: Any = None
    ) -> Any:
        """Get a context variable"""

        ctx_key = f"context:{correlation_id}:{key}"
        val = self.redis.get(ctx_key)

        if val is None:
            return default

        try:
            return json.loads(val.decode('utf-8') if isinstance(val, bytes) else val)
        except json.JSONDecodeError:
            return val

    def get_all_context(self, correlation_id: str) -> Dict[str, Any]:
        """Get entire context for a correlation_id"""

        pattern = f"context:{correlation_id}:*"
        keys = self.redis.keys(pattern)

        context = {}
        for key_bytes in keys:
            key = key_bytes.decode('utf-8') if isinstance(key_bytes, bytes) else key_bytes
            field = key.split(":")[-1]  # Extract field name

            value = self.redis.get(key_bytes)
            if value:
                try:
                    context[field] = json.loads(value.decode('utf-8') if isinstance(value, bytes) else value)
                except json.JSONDecodeError:
                    context[field] = value

        return context

    def update_context(
        self,
        correlation_id: str,
        updates: Dict[str, Any],
        ttl: Optional[int] = None
    ):
        """Update multiple context variables at once"""

        for key, value in updates.items():
            self.set_context(correlation_id, key, value, ttl)

    def delete_context(self, correlation_id: str, key: Optional[str] = None):
        """Delete context variable(s)"""

        if key is None:
            # Delete entire context
            pattern = f"context:{correlation_id}:*"
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
        else:
            ctx_key = f"context:{correlation_id}:{key}"
            self.redis.delete(ctx_key)

    def lock(
        self,
        correlation_id: str,
        resource: str,
        agent_id: str,
        ttl: int = 60
    ) -> bool:
        """
        Acquire exclusive lock on a resource

        Returns:
            True if lock acquired, False if already locked
        """

        lock_key = f"lock:{correlation_id}:{resource}"
        result = self.redis.set(lock_key, agent_id, nx=True, ex=ttl)
        return result is not None

    def unlock(self, correlation_id: str, resource: str, agent_id: str) -> bool:
        """Release a lock (only if held by this agent)"""

        lock_key = f"lock:{correlation_id}:{resource}"
        holder = self.redis.get(lock_key)

        if holder and holder.decode('utf-8') == agent_id:
            self.redis.delete(lock_key)
            return True

        return False

    def is_locked(self, correlation_id: str, resource: str) -> Optional[str]:
        """Check if resource is locked and return lock holder"""

        lock_key = f"lock:{correlation_id}:{resource}"
        holder = self.redis.get(lock_key)
        return holder.decode('utf-8') if holder else None

    def watch_context(
        self,
        correlation_id: str,
        key: str,
        poll_interval: float = 1.0,
        timeout: float = 60.0
    ) -> Any:
        """
        Block until context variable is set

        Useful for agent A waiting for agent B to set a value
        """

        import time

        start_time = time.time()
        ctx_key = f"context:{correlation_id}:{key}"

        while time.time() - start_time < timeout:
            val = self.redis.get(ctx_key)
            if val:
                try:
                    return json.loads(val.decode('utf-8') if isinstance(val, bytes) else val)
                except json.JSONDecodeError:
                    return val

            time.sleep(poll_interval)

        # Timeout
        return None

    def list_contexts(self, correlation_id: str) -> List[str]:
        """List all context keys for a correlation_id"""

        pattern = f"context:{correlation_id}:*"
        keys = self.redis.keys(pattern)

        return [
            key.decode('utf-8').split(":")[-1] if isinstance(key, bytes) else key.split(":")[-1]
            for key in keys
        ]

    def increment(
        self,
        correlation_id: str,
        key: str,
        delta: int = 1
    ) -> int:
        """Increment a numeric context value"""

        ctx_key = f"context:{correlation_id}:{key}"

        # Get current value
        current = self.redis.get(ctx_key)
        if current:
            value = int(json.loads(current.decode('utf-8') if isinstance(current, bytes) else current))
        else:
            value = 0

        # Increment
        value += delta

        # Set back
        self.set_context(correlation_id, key, value)

        return value


# Example usage:
"""
from backend.messaging.context_bus import ContextBus

ctx_bus = ContextBus(redis_client)

# Agent A sets initial context
ctx_bus.set_context("move-789", "strategy_phase", "planning")
ctx_bus.set_context("move-789", "target_cohorts", ["cohort-A", "cohort-B"])

# Agent B reads context
cohorts = ctx_bus.get_context("move-789", "target_cohorts")

# Agent C locks a resource
if ctx_bus.lock("move-789", "email_draft", "COPY-01"):
    # Write draft
    ctx_bus.set_context("move-789", "email_draft", draft_content)
    # ... do work ...
    ctx_bus.unlock("move-789", "email_draft", "COPY-01")
else:
    # Someone else is working on it
    lock_holder = ctx_bus.is_locked("move-789", "email_draft")
    print(f"Locked by {lock_holder}")

# Agent D waits for email draft
draft = ctx_bus.watch_context("move-789", "email_draft", timeout=120)
"""
