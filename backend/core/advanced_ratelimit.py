import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("raptorflow.ratelimit")


class RateLimitType(Enum):
    """Types of rate limiting."""

    GLOBAL = "global"
    PER_USER = "per_user"
    PER_TENANT = "per_tenant"
    PER_ENDPOINT = "per_endpoint"
    PER_IP = "per_ip"


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration."""

    name: str
    limit_type: RateLimitType
    requests: int
    window_seconds: int
    burst_limit: Optional[int] = None
    priority: int = 0  # Higher priority rules override lower ones

    def __post_init__(self):
        if self.burst_limit is None:
            self.burst_limit = int(self.requests * 1.5)  # 50% burst capacity


@dataclass
class RateLimitState:
    """Current rate limit state for a key."""

    current_requests: int = 0
    window_start: datetime = field(default_factory=datetime.utcnow)
    last_request: Optional[datetime] = None
    blocked_until: Optional[datetime] = None
    total_requests: int = 0  # Lifetime counter


class AdvancedRateLimiter:
    """
    Production-grade rate limiting with per-user/tenant support and multiple strategies.
    """

    def __init__(self):
        self.rules: List[RateLimitRule] = []
        self.states: Dict[str, RateLimitState] = {}
        self.global_stats: Dict[str, Any] = {
            "total_requests": 0,
            "blocked_requests": 0,
            "active_keys": 0,
        }
        self._lock = asyncio.Lock()

    def add_rule(self, rule: RateLimitRule):
        """Add a rate limiting rule."""
        self.rules.append(rule)
        # Sort by priority (highest first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
        logger.info(f"Added rate limit rule: {rule.name} ({rule.limit_type.value})")

    def get_key_for_request(
        self,
        rule: RateLimitRule,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> str:
        """Generate rate limit key based on rule type."""
        key_parts = [rule.name]

        if rule.limit_type == RateLimitType.GLOBAL:
            key_parts.append("global")
        elif rule.limit_type == RateLimitType.PER_USER and user_id:
            key_parts.append(f"user:{user_id}")
        elif rule.limit_type == RateLimitType.PER_TENANT and tenant_id:
            key_parts.append(f"tenant:{tenant_id}")
        elif rule.limit_type == RateLimitType.PER_IP and ip_address:
            # Hash IP for privacy
            ip_hash = hashlib.sha256(ip_address.encode()).hexdigest()[:16]
            key_parts.append(f"ip:{ip_hash}")
        elif rule.limit_type == RateLimitType.PER_ENDPOINT and endpoint:
            key_parts.append(f"endpoint:{endpoint}")

        return ":".join(key_parts)

    async def is_allowed(
        self,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Check if request is allowed based on all rules."""
        async with self._lock:
            results = []

            for rule in self.rules:
                key = self.get_key_for_request(
                    rule, user_id, tenant_id, ip_address, endpoint
                )

                result = await self._check_rule(rule, key)
                results.append(result)

                # If any rule blocks, immediately return blocked
                if not result["allowed"]:
                    self.global_stats["blocked_requests"] += 1
                    return {
                        "allowed": False,
                        "rule": rule.name,
                        "limit": rule.requests,
                        "window": rule.window_seconds,
                        "remaining": result["remaining"],
                        "reset_time": result["reset_time"],
                        "retry_after": result["retry_after"],
                    }

            # All rules passed
            self.global_stats["total_requests"] += 1
            return {
                "allowed": True,
                "rules_checked": len(results),
                "remaining": min(r["remaining"] for r in results),
            }

    async def _check_rule(self, rule: RateLimitRule, key: str) -> Dict[str, Any]:
        """Check a specific rate limit rule."""
        now = datetime.utcnow()

        # Get or create state
        if key not in self.states:
            self.states[key] = RateLimitState()

        state = self.states[key]

        # Check if currently blocked
        if state.blocked_until and now < state.blocked_until:
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": state.blocked_until.isoformat(),
                "retry_after": int((state.blocked_until - now).total_seconds()),
            }

        # Check if window has expired
        if now - state.window_start > timedelta(seconds=rule.window_seconds):
            # Reset window
            state.current_requests = 0
            state.window_start = now

        # Check burst limit first
        if state.current_requests >= rule.burst_limit:
            # Block for the remainder of the window
            state.blocked_until = state.window_start + timedelta(
                seconds=rule.window_seconds
            )
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": state.blocked_until.isoformat(),
                "retry_after": int((state.blocked_until - now).total_seconds()),
            }

        # Check regular limit
        if state.current_requests >= rule.requests:
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": (
                    state.window_start + timedelta(seconds=rule.window_seconds)
                ).isoformat(),
                "retry_after": int(
                    (
                        state.window_start
                        + timedelta(seconds=rule.window_seconds)
                        - now
                    ).total_seconds()
                ),
            }

        # Allow request
        state.current_requests += 1
        state.last_request = now
        state.total_requests += 1

        remaining = rule.requests - state.current_requests
        reset_time = state.window_start + timedelta(seconds=rule.window_seconds)

        return {
            "allowed": True,
            "remaining": max(0, remaining),
            "reset_time": reset_time.isoformat(),
            "retry_after": 0,
        }

    async def get_rate_limit_info(
        self,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get current rate limit information without consuming a request."""
        async with self._lock:
            info = {}

            for rule in self.rules:
                key = self.get_key_for_request(
                    rule, user_id, tenant_id, ip_address, endpoint
                )

                if key in self.states:
                    state = self.states[key]
                    now = datetime.utcnow()

                    # Calculate remaining requests
                    if now - state.window_start > timedelta(
                        seconds=rule.window_seconds
                    ):
                        remaining = rule.requests
                        reset_time = now + timedelta(seconds=rule.window_seconds)
                    else:
                        remaining = max(0, rule.requests - state.current_requests)
                        reset_time = state.window_start + timedelta(
                            seconds=rule.window_seconds
                        )

                    info[rule.name] = {
                        "limit": rule.requests,
                        "remaining": remaining,
                        "window_seconds": rule.window_seconds,
                        "reset_time": reset_time.isoformat(),
                        "current_requests": state.current_requests,
                        "total_requests": state.total_requests,
                    }

            return info

    async def reset_limits(
        self,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
    ):
        """Reset rate limits for specific criteria."""
        async with self._lock:
            keys_to_remove = []

            for rule in self.rules:
                key = self.get_key_for_request(
                    rule, user_id, tenant_id, ip_address, endpoint
                )
                keys_to_remove.append(key)

            for key in keys_to_remove:
                if key in self.states:
                    del self.states[key]

            logger.info(f"Reset rate limits for user={user_id}, tenant={tenant_id}")

    async def cleanup_expired_states(self):
        """Clean up expired rate limit states."""
        async with self._lock:
            now = datetime.utcnow()
            expired_keys = []

            for key, state in self.states.items():
                # Remove states that haven't been used for 24 hours
                if state.last_request and now - state.last_request > timedelta(
                    hours=24
                ):
                    expired_keys.append(key)

            for key in expired_keys:
                del self.states[key]

            if expired_keys:
                logger.debug(
                    f"Cleaned up {len(expired_keys)} expired rate limit states"
                )

    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global rate limiting statistics."""
        async with self._lock:
            self.global_stats["active_keys"] = len(self.states)

            # Calculate active users/tenants
            active_users = set()
            active_tenants = set()

            for key, state in self.states.items():
                if (
                    state.last_request
                    and datetime.utcnow() - state.last_request < timedelta(hours=1)
                ):
                    if "user:" in key:
                        user_id = key.split("user:")[1].split(":")[0]
                        active_users.add(user_id)
                    elif "tenant:" in key:
                        tenant_id = key.split("tenant:")[1].split(":")[0]
                        active_tenants.add(tenant_id)

            return {
                **self.global_stats,
                "active_users": len(active_users),
                "active_tenants": len(active_tenants),
                "total_rules": len(self.rules),
                "total_states": len(self.states),
            }


class RateLimitMiddleware:
    """FastAPI middleware for advanced rate limiting."""

    def __init__(self, app, rate_limiter: AdvancedRateLimiter):
        self.app = app
        self.rate_limiter = rate_limiter

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Extract request information
            headers = dict(scope.get("headers", []))

            # Get user/tenant info (would come from auth middleware)
            user_id = getattr(scope, "user_id", None)
            tenant_id = getattr(scope, "tenant_id", None)

            # Get IP address
            ip_address = self._get_client_ip(scope)

            # Get endpoint
            endpoint = f"{scope['method']} {scope['path']}"

            # Check rate limits
            result = await self.rate_limiter.is_allowed(
                user_id=user_id,
                tenant_id=tenant_id,
                ip_address=ip_address,
                endpoint=endpoint,
            )

            if not result["allowed"]:
                # Send rate limit response
                await self._send_rate_limit_response(send, result)
                return

            # Add rate limit headers
            await self._add_rate_limit_headers(send, result)

            # Process request
            await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    def _get_client_ip(self, scope: Dict[str, Any]) -> str:
        """Extract client IP from request."""
        headers = dict(scope.get("headers", []))

        # Check for forwarded IP
        forwarded_for = headers.get(b"x-forwarded-for", b"").decode()
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check for real IP
        real_ip = headers.get(b"x-real-ip", b"").decode()
        if real_ip:
            return real_ip

        # Fall back to client from scope
        client = scope.get("client")
        if client:
            return client[0]

        return "unknown"

    async def _send_rate_limit_response(self, send, result: Dict[str, Any]):
        """Send rate limit exceeded response."""
        from fastapi.responses import JSONResponse

        response = JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Rate limit exceeded. Try again in {result['retry_after']} seconds.",
                "limit": result["limit"],
                "window": result["window"],
                "retry_after": result["retry_after"],
            },
        )

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(result["limit"])
        response.headers["X-RateLimit-Remaining"] = str(result["remaining"])
        response.headers["X-RateLimit-Reset"] = result["reset_time"]
        response.headers["Retry-After"] = str(result["retry_after"])

        await response(scope, receive, send)

    async def _add_rate_limit_headers(self, send, result: Dict[str, Any]):
        """Add rate limit headers to response."""
        # This would be handled by response middleware
        pass


# Global rate limiter
_advanced_rate_limiter: Optional[AdvancedRateLimiter] = None


def get_advanced_rate_limiter() -> AdvancedRateLimiter:
    """Get the global advanced rate limiter instance."""
    global _advanced_rate_limiter
    if _advanced_rate_limiter is None:
        _advanced_rate_limiter = AdvancedRateLimiter()
        _setup_default_rules()
    return _advanced_rate_limiter


def _setup_default_rules():
    """Setup default rate limiting rules."""
    limiter = get_advanced_rate_limiter()

    # Global rate limit
    limiter.add_rule(
        RateLimitRule(
            name="global_limit",
            limit_type=RateLimitType.GLOBAL,
            requests=1000,
            window_seconds=60,
            priority=1,
        )
    )

    # Per-user rate limit
    limiter.add_rule(
        RateLimitRule(
            name="user_limit",
            limit_type=RateLimitType.PER_USER,
            requests=100,
            window_seconds=60,
            priority=10,
        )
    )

    # Per-tenant rate limit
    limiter.add_rule(
        RateLimitRule(
            name="tenant_limit",
            limit_type=RateLimitType.PER_TENANT,
            requests=500,
            window_seconds=60,
            priority=8,
        )
    )

    # Per-IP rate limit
    limiter.add_rule(
        RateLimitRule(
            name="ip_limit",
            limit_type=RateLimitType.PER_IP,
            requests=50,
            window_seconds=60,
            priority=5,
        )
    )

    # Expensive endpoints (lower limits)
    limiter.add_rule(
        RateLimitRule(
            name="expensive_endpoints",
            limit_type=RateLimitType.PER_ENDPOINT,
            requests=10,
            window_seconds=60,
            priority=15,
        )
    )


async def start_advanced_rate_limiting():
    """Start the advanced rate limiting system."""
    limiter = get_advanced_rate_limiter()

    # Start cleanup task
    asyncio.create_task(_periodic_cleanup())

    logger.info("Advanced rate limiting started")


async def stop_advanced_rate_limiting():
    """Stop the advanced rate limiting system."""
    logger.info("Advanced rate limiting stopped")


async def _periodic_cleanup():
    """Periodic cleanup of expired rate limit states."""
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            limiter = get_advanced_rate_limiter()
            await limiter.cleanup_expired_states()
            logger.debug("Completed rate limit cleanup")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error during rate limit cleanup: {e}")


# Decorator for rate limiting
def rate_limit(
    requests: int,
    window_seconds: int,
    per_user: bool = True,
    per_tenant: bool = False,
    per_ip: bool = False,
):
    """Decorator for rate limiting specific endpoints."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            limiter = get_advanced_rate_limiter()

            # Extract context from kwargs
            user_id = kwargs.get("user_id")
            tenant_id = kwargs.get("tenant_id")
            ip_address = kwargs.get("ip_address")
            endpoint = kwargs.get("endpoint", f"{func.__module__}.{func.__name__}")

            # Check rate limit
            result = await limiter.is_allowed(
                user_id=user_id,
                tenant_id=tenant_id,
                ip_address=ip_address,
                endpoint=endpoint,
            )

            if not result["allowed"]:
                from fastapi import HTTPException

                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "retry_after": result["retry_after"],
                    },
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
