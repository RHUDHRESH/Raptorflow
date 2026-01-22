"""
Rate Limiting Manager for Payment System
Implements token bucket algorithm with comprehensive monitoring
Addresses critical rate limiting vulnerabilities identified in red team audit
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import redis
from functools import wraps
from collections import defaultdict

from backend.core.audit_logger import audit_logger, EventType, LogLevel

logger = logging.getLogger(__name__)

class RateLimitScope(Enum):
    """Rate limiting scope"""
    GLOBAL = "GLOBAL"           # Global rate limiting
    USER = "USER"               # User-specific rate limiting
    IP = "IP"                   # IP-based rate limiting
    ENDPOINT = "ENDPOINT"       # Endpoint-specific rate limiting
    API_KEY = "API_KEY"         # API key-based rate limiting
    SESSION = "SESSION"         # Session-based rate limiting

class RateLimitPeriod(Enum):
    """Rate limiting periods"""
    SECOND = "SECOND"
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"

class RateLimitAction(Enum):
    """Action when rate limit is exceeded"""
    REJECT = "REJECT"           # Reject request
    QUEUE = "QUEUE"             # Queue request
    THROTTLE = "THROTTLE"       # Throttle (delay) request
    WARN = "WARN"               # Allow but warn

@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    max_requests: int
    period: RateLimitPeriod
    scope: RateLimitScope
    action: RateLimitAction = RateLimitAction.REJECT
    burst_size: Optional[int] = None
    refill_rate: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RateLimitResult:
    """Rate limiting check result"""
    allowed: bool
    remaining_requests: int
    reset_time: datetime
    retry_after: Optional[float] = None
    action_taken: Optional[RateLimitAction] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TokenBucket:
    """Token bucket for rate limiting"""
    capacity: int
    tokens: float
    last_refill: float
    refill_rate: float
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self.refill_rate = refill_rate
    
    def consume(self, tokens: int = 1) -> bool:
        """Consume tokens from bucket"""
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        
        if elapsed > 0:
            tokens_to_add = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
    
    def get_tokens(self) -> float:
        """Get current token count"""
        self._refill()
        return self.tokens
    
    def time_until_available(self, tokens: int = 1) -> float:
        """Get time until tokens are available"""
        if self.tokens >= tokens:
            return 0
        
        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate

class RateLimitingManager:
    """
    Production-Ready Rate Limiting Manager
    Implements token bucket algorithm with comprehensive monitoring
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
        # Configuration
        self.default_configs = {
            RateLimitScope.GLOBAL: RateLimitConfig(
                max_requests=10000,
                period=RateLimitPeriod.MINUTE,
                scope=RateLimitScope.GLOBAL
            ),
            RateLimitScope.USER: RateLimitConfig(
                max_requests=100,
                period=RateLimitPeriod.MINUTE,
                scope=RateLimitScope.USER
            ),
            RateLimitScope.IP: RateLimitConfig(
                max_requests=1000,
                period=RateLimitPeriod.MINUTE,
                scope=RateLimitScope.IP
            ),
            RateLimitScope.ENDPOINT: RateLimitConfig(
                max_requests=500,
                period=RateLimitPeriod.MINUTE,
                scope=RateLimitScope.ENDPOINT
            )
        }
        
        # In-memory token buckets for high-frequency operations
        self._memory_buckets = defaultdict(dict)
        self._memory_bucket_cleanup_interval = 300  # 5 minutes
        
        # Redis keys
        self.bucket_prefix = "rate_limit_bucket:"
        self.metrics_prefix = "rate_limit_metrics:"
        self.config_prefix = "rate_limit_config:"
        
        # Monitoring
        self._metrics_collector = RateLimitMetricsCollector(redis_client)
        
        logger.info("Rate Limiting Manager initialized")
    
    def get_period_seconds(self, period: RateLimitPeriod) -> int:
        """Get period in seconds"""
        period_map = {
            RateLimitPeriod.SECOND: 1,
            RateLimitPeriod.MINUTE: 60,
            RateLimitPeriod.HOUR: 3600,
            RateLimitPeriod.DAY: 86400,
            RateLimitPeriod.WEEK: 604800,
            RateLimitPeriod.MONTH: 2592000  # 30 days
        }
        return period_map.get(period, 60)
    
    def get_refill_rate(self, config: RateLimitConfig) -> float:
        """Calculate token refill rate"""
        period_seconds = self.get_period_seconds(config.period)
        if config.refill_rate:
            return config.refill_rate
        
        # Default refill rate: tokens per second
        return config.max_requests / period_seconds
    
    async def check_rate_limit(
        self,
        identifier: str,
        config: RateLimitConfig,
        tokens_requested: int = 1
    ) -> RateLimitResult:
        """
        Check rate limit using token bucket algorithm
        """
        try:
            # Generate bucket key
            bucket_key = f"{self.bucket_prefix}{config.scope.value}:{identifier}"
            
            # Get or create token bucket
            bucket = await self._get_or_create_bucket(bucket_key, config)
            
            # Try to consume tokens
            consumed = bucket.consume(tokens_requested)
            
            # Calculate remaining requests
            remaining_requests = int(bucket.get_tokens())
            
            # Calculate reset time
            reset_time = datetime.now() + timedelta(seconds=bucket.time_until_available(tokens_requested))
            
            # Determine action
            action_taken = None
            retry_after = None
            
            if not consumed:
                action_taken = config.action
                
                if config.action == RateLimitAction.REJECT:
                    retry_after = bucket.time_until_available(tokens_requested)
                elif config.action == RateLimitAction.THROTTLE:
                    # Implement throttling delay
                    delay = bucket.time_until_available(tokens_requested)
                    if delay > 0:
                        await asyncio.sleep(min(delay, 5.0))  # Max 5 second delay
                        # Retry after delay
                        consumed = bucket.consume(tokens_requested)
                        if consumed:
                            action_taken = None
                            remaining_requests = int(bucket.get_tokens())
                            reset_time = datetime.now()
            
            # Update bucket in Redis
            await self._update_bucket(bucket_key, bucket, config)
            
            # Record metrics
            await self._metrics_collector.record_request(
                scope=config.scope.value,
                identifier=identifier,
                allowed=consumed,
                tokens_requested=tokens_requested,
                remaining_tokens=remaining_requests,
                action_taken=action_taken
            )
            
            # Log rate limit events
            if not consumed and config.action == RateLimitAction.REJECT:
                await audit_logger.log_security_violation(
                    violation_type="rate_limit_exceeded",
                    request_data={
                        "scope": config.scope.value,
                        "identifier": identifier,
                        "tokens_requested": tokens_requested,
                        "remaining_tokens": remaining_requests,
                        "retry_after": retry_after
                    }
                )
            
            result = RateLimitResult(
                allowed=consumed,
                remaining_requests=remaining_requests,
                reset_time=reset_time,
                retry_after=retry_after,
                action_taken=action_taken,
                metadata={
                    "scope": config.scope.value,
                    "identifier": identifier,
                    "bucket_capacity": bucket.capacity,
                    "current_tokens": bucket.tokens
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Fail open - allow request if rate limiting fails
            return RateLimitResult(
                allowed=True,
                remaining_requests=999999,
                reset_time=datetime.now() + timedelta(hours=1),
                metadata={"error": str(e)}
            )
    
    async def _get_or_create_bucket(self, bucket_key: str, config: RateLimitConfig) -> TokenBucket:
        """Get or create token bucket"""
        try:
            # Try to get from Redis first
            bucket_data = self.redis.get(bucket_key)
            
            if bucket_data:
                bucket_dict = json.loads(bucket_data)
                bucket = TokenBucket(
                    capacity=bucket_dict["capacity"],
                    refill_rate=bucket_dict["refill_rate"]
                )
                bucket.tokens = bucket_dict["tokens"]
                bucket.last_refill = bucket_dict["last_refill"]
                return bucket
            
            # Create new bucket
            capacity = config.burst_size or config.max_requests
            refill_rate = self.get_refill_rate(config)
            
            bucket = TokenBucket(capacity, refill_rate)
            
            return bucket
            
        except Exception as e:
            logger.error(f"Error getting/creating bucket: {e}")
            # Fallback to memory bucket
            return self._get_memory_bucket(bucket_key, config)
    
    def _get_memory_bucket(self, bucket_key: str, config: RateLimitConfig) -> TokenBucket:
        """Get or create memory bucket (fallback)"""
        if bucket_key not in self._memory_buckets:
            capacity = config.burst_size or config.max_requests
            refill_rate = self.get_refill_rate(config)
            self._memory_buckets[bucket_key] = TokenBucket(capacity, refill_rate)
        
        return self._memory_buckets[bucket_key]
    
    async def _update_bucket(self, bucket_key: str, bucket: TokenBucket, config: RateLimitConfig):
        """Update bucket in Redis"""
        try:
            bucket_data = {
                "capacity": bucket.capacity,
                "tokens": bucket.tokens,
                "last_refill": bucket.last_refill,
                "refill_rate": bucket.refill_rate
            }
            
            # Set with expiration based on period
            period_seconds = self.get_period_seconds(config.period)
            self.redis.setex(
                bucket_key,
                period_seconds * 2,  # Keep bucket for 2 periods
                json.dumps(bucket_data)
            )
            
        except Exception as e:
            logger.error(f"Error updating bucket: {e}")
    
    def rate_limit(
        self,
        scope: RateLimitScope,
        max_requests: Optional[int] = None,
        period: Optional[RateLimitPeriod] = None,
        action: RateLimitAction = RateLimitAction.REJECT,
        identifier_param: str = "user_id",
        tokens: int = 1
    ):
        """
        Decorator for rate limiting functions
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Get identifier
                identifier = kwargs.get(identifier_param)
                
                if not identifier:
                    # Use IP address as fallback
                    identifier = kwargs.get("ip_address", "anonymous")
                
                # Get config
                config = self._get_config(scope, max_requests, period, action)
                
                # Check rate limit
                result = await self.check_rate_limit(identifier, config, tokens)
                
                if not result.allowed:
                    if result.action_taken == RateLimitAction.REJECT:
                        raise RateLimitExceeded(
                            f"Rate limit exceeded for {scope.value}: {identifier}",
                            retry_after=result.retry_after,
                            reset_time=result.reset_time
                        )
                    elif result.action_taken == RateLimitAction.WARN:
                        # Add warning to kwargs
                        kwargs["_rate_limit_warning"] = {
                            "remaining_requests": result.remaining_requests,
                            "reset_time": result.reset_time
                        }
                
                # Add rate limit info to kwargs
                kwargs["_rate_limit_info"] = {
                    "remaining_requests": result.remaining_requests,
                    "reset_time": result.reset_time,
                    "metadata": result.metadata
                }
                
                # Execute function
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def _get_config(
        self,
        scope: RateLimitScope,
        max_requests: Optional[int],
        period: Optional[RateLimitPeriod],
        action: RateLimitAction
    ) -> RateLimitConfig:
        """Get rate limit configuration"""
        if max_requests and period:
            # Custom configuration
            return RateLimitConfig(
                max_requests=max_requests,
                period=period,
                scope=scope,
                action=action
            )
        else:
            # Default configuration
            default_config = self.default_configs.get(scope)
            if default_config:
                config = RateLimitConfig(
                    max_requests=default_config.max_requests,
                    period=default_config.period,
                    scope=scope,
                    action=action
                )
                return config
            else:
                # Fallback configuration
                return RateLimitConfig(
                    max_requests=100,
                    period=RateLimitPeriod.MINUTE,
                    scope=scope,
                    action=action
                )
    
    async def get_rate_limit_status(
        self,
        identifier: str,
        scope: RateLimitScope
    ) -> Optional[RateLimitResult]:
        """Get current rate limit status"""
        try:
            config = self.default_configs.get(scope)
            if not config:
                return None
            
            bucket_key = f"{self.bucket_prefix}{scope.value}:{identifier}"
            bucket = await self._get_or_create_bucket(bucket_key, config)
            
            remaining_requests = int(bucket.get_tokens())
            reset_time = datetime.now() + timedelta(seconds=bucket.time_until_available(1))
            
            return RateLimitResult(
                allowed=remaining_requests > 0,
                remaining_requests=remaining_requests,
                reset_time=reset_time,
                metadata={
                    "scope": scope.value,
                    "identifier": identifier,
                    "bucket_capacity": bucket.capacity,
                    "current_tokens": bucket.tokens
                }
            )
            
        except Exception as e:
            logger.error(f"Error getting rate limit status: {e}")
            return None
    
    async def reset_rate_limit(self, identifier: str, scope: RateLimitScope) -> bool:
        """Reset rate limit for identifier"""
        try:
            bucket_key = f"{self.bucket_prefix}{scope.value}:{identifier}"
            self.redis.delete(bucket_key)
            
            # Remove from memory buckets
            if bucket_key in self._memory_buckets:
                del self._memory_buckets[bucket_key]
            
            await audit_logger.log_event(
                event_type=EventType.RATE_LIMIT_RESET,
                level=LogLevel.INFO,
                request_data={
                    "scope": scope.value,
                    "identifier": identifier
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error resetting rate limit: {e}")
            return False
    
    async def cleanup_expired_buckets(self) -> int:
        """Clean up expired token buckets"""
        try:
            cleaned_count = 0
            
            # Clean memory buckets
            current_time = time.time()
            expired_keys = []
            
            for key, bucket in self._memory_buckets.items():
                # Remove buckets not used for 5 minutes
                if current_time - bucket.last_refill > self._memory_bucket_cleanup_interval:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._memory_buckets[key]
                cleaned_count += 1
            
            await audit_logger.log_event(
                event_type=EventType.RATE_LIMIT_CLEANUP_COMPLETED,
                level=LogLevel.DEBUG,
                request_data={"cleaned_count": cleaned_count}
            )
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0
    
    async def get_metrics(self, scope: Optional[RateLimitScope] = None) -> Dict[str, Any]:
        """Get rate limiting metrics"""
        return await self._metrics_collector.get_metrics(scope)
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for rate limiting manager"""
        try:
            # Check Redis connection
            try:
                self.redis.ping()
                redis_healthy = True
            except Exception as e:
                redis_healthy = False
                redis_error = str(e)
            
            # Check active buckets
            try:
                bucket_keys = self.redis.keys(f"{self.bucket_prefix}*")
                active_buckets = len(bucket_keys)
            except Exception:
                active_buckets = 0
            
            # Check memory buckets
            memory_buckets = len(self._memory_buckets)
            
            overall_healthy = redis_healthy
            
            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "message": "Rate limiting manager is operational" if overall_healthy else "Rate limiting manager has issues",
                "features": {
                    "token_bucket_algorithm": True,
                    "multiple_scopes": True,
                    "configurable_actions": True,
                    "memory_fallback": True,
                    "metrics_collection": True,
                    "automatic_cleanup": True,
                    "decorator_support": True
                },
                "configuration": {
                    "default_scopes": [scope.value for scope in self.default_configs.keys()],
                    "memory_bucket_cleanup_interval": self._memory_bucket_cleanup_interval
                },
                "runtime": {
                    "active_buckets": active_buckets,
                    "memory_buckets": memory_buckets
                },
                "dependencies": {
                    "redis": "healthy" if redis_healthy else f"unhealthy: {redis_error}"
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "error": str(e)
            }

class RateLimitMetricsCollector:
    """Metrics collector for rate limiting"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.metrics_prefix = "rate_limit_metrics:"
    
    async def record_request(
        self,
        scope: str,
        identifier: str,
        allowed: bool,
        tokens_requested: int,
        remaining_tokens: int,
        action_taken: Optional[RateLimitAction]
    ):
        """Record rate limiting request"""
        try:
            timestamp = datetime.now()
            minute_key = f"{self.metrics_prefix}{scope}:{timestamp.strftime('%Y%m%d%H%M')}"
            
            # Increment counters
            pipe = self.redis.pipeline()
            
            if allowed:
                pipe.hincrby(minute_key, "allowed_requests", 1)
            else:
                pipe.hincrby(minute_key, "rejected_requests", 1)
                
                if action_taken:
                    pipe.hincrby(minute_key, f"action_{action_taken.value}", 1)
            
            pipe.hincrby(minute_key, "total_requests", 1)
            pipe.hincrby(minute_key, "tokens_consumed", tokens_requested)
            pipe.hset(minute_key, "last_updated", timestamp.isoformat())
            
            # Expire after 1 hour
            pipe.expire(minute_key, 3600)
            
            pipe.execute()
            
        except Exception as e:
            logger.error(f"Error recording metrics: {e}")
    
    async def get_metrics(self, scope: Optional[RateLimitScope] = None) -> Dict[str, Any]:
        """Get rate limiting metrics"""
        try:
            metrics = {}
            
            if scope:
                # Get metrics for specific scope
                scope_metrics = await self._get_scope_metrics(scope.value)
                metrics[scope.value] = scope_metrics
            else:
                # Get metrics for all scopes
                for scope_enum in RateLimitScope:
                    scope_metrics = await self._get_scope_metrics(scope_enum.value)
                    metrics[scope_enum.value] = scope_metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {}
    
    async def _get_scope_metrics(self, scope: str) -> Dict[str, Any]:
        """Get metrics for specific scope"""
        try:
            # Get last 5 minutes of data
            now = datetime.now()
            metrics_data = {
                "allowed_requests": 0,
                "rejected_requests": 0,
                "total_requests": 0,
                "tokens_consumed": 0,
                "rejection_rate": 0.0,
                "minute_breakdown": []
            }
            
            for minutes_ago in range(5):
                timestamp = now - timedelta(minutes=minutes_ago)
                minute_key = f"{self.metrics_prefix}{scope}:{timestamp.strftime('%Y%m%d%H%M')}"
                
                minute_data = self.redis.hgetall(minute_key)
                
                if minute_data:
                    allowed = int(minute_data.get("allowed_requests", 0))
                    rejected = int(minute_data.get("rejected_requests", 0))
                    total = int(minute_data.get("total_requests", 0))
                    tokens = int(minute_data.get("tokens_consumed", 0))
                    
                    metrics_data["allowed_requests"] += allowed
                    metrics_data["rejected_requests"] += rejected
                    metrics_data["total_requests"] += total
                    metrics_data["tokens_consumed"] += tokens
                    
                    metrics_data["minute_breakdown"].append({
                        "minute": minutes_ago,
                        "allowed": allowed,
                        "rejected": rejected,
                        "total": total,
                        "tokens": tokens
                    })
            
            # Calculate rejection rate
            if metrics_data["total_requests"] > 0:
                metrics_data["rejection_rate"] = (
                    metrics_data["rejected_requests"] / metrics_data["total_requests"]
                ) * 100
            
            return metrics_data
            
        except Exception as e:
            logger.error(f"Error getting scope metrics: {e}")
            return {}

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    
    def __init__(self, message: str, retry_after: Optional[float] = None, reset_time: Optional[datetime] = None):
        super().__init__(message)
        self.retry_after = retry_after
        self.reset_time = reset_time

# Global rate limiting manager instance
rate_limiting_manager = None

def get_rate_limiting_manager(redis_client: redis.Redis) -> RateLimitingManager:
    """Get or create rate limiting manager instance"""
    global rate_limiting_manager
    if rate_limiting_manager is None:
        rate_limiting_manager = RateLimitingManager(redis_client)
    return rate_limiting_manager
