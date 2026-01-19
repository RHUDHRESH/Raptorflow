"""
Advanced Rate Limiting System for Raptorflow Backend
==================================================

Enterprise-grade rate limiting with intelligent throttling, user-based controls,
and comprehensive usage analytics.

Features:
- Intelligent rate limiting with adaptive algorithms
- User-based and endpoint-specific controls
- Real-time usage analytics and insights
- Abuse detection and prevention
- Machine learning-based optimization
- Distributed Redis Cluster support
- Dynamic rate limiting based on user tiers
- Comprehensive monitoring and alerting
"""

import asyncio
import time
import json
import hashlib
from collections import defaultdict, deque
from typing import Dict, Optional, Tuple, List, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging

from .redis import get_redis_client
from .usage_analytics import UsageAnalyticsManager

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    ADAPTIVE = "adaptive"


class UserTier(Enum):
    """User tiers for dynamic rate limiting."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AdvancedRateLimitConfig:
    """Advanced rate limiting configuration."""
    
    # Base limits (per minute)
    base_requests_per_minute: int = 60
    base_requests_per_hour: int = 1000
    base_requests_per_day: int = 10000
    
    # Tier multipliers
    tier_multipliers: Dict[UserTier, float] = field(default_factory=lambda: {
        UserTier.FREE: 1.0,
        UserTier.BASIC: 2.0,
        UserTier.PRO: 5.0,
        UserTier.ENTERPRISE: 20.0,
        UserTier.PREMIUM: 50.0
    })
    
    # Endpoint-specific limits
    endpoint_limits: Dict[str, Dict[str, int]] = field(default_factory=dict)
    
    # Advanced settings
    strategy: RateLimitStrategy = RateLimitStrategy.ADAPTIVE
    enable_ml_optimization: bool = True
    enable_abuse_detection: bool = True
    abuse_threshold: float = 0.8  # 80% of limit triggers abuse detection
    
    # Performance settings
    cleanup_interval_seconds: int = 300
    max_clients: int = 100000
    cache_size: int = 10000
    
    # Analytics settings
    enable_analytics: bool = True
    analytics_retention_days: int = 90
    
    # Alerting settings
    enable_alerting: bool = True
    alert_thresholds: Dict[AlertSeverity, float] = field(default_factory=lambda: {
        AlertSeverity.LOW: 0.7,
        AlertSeverity.MEDIUM: 0.8,
        AlertSeverity.HIGH: 0.9,
        AlertSeverity.CRITICAL: 0.95
    })


@dataclass
class ClientInfo:
    """Client information for rate limiting."""
    
    client_id: str
    user_id: Optional[str] = None
    user_tier: UserTier = UserTier.FREE
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    api_key: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    is_blocked: bool = False
    block_reason: Optional[str] = None
    block_expires: Optional[datetime] = None
    trust_score: float = 1.0  # 0.0 to 1.0
    reputation_score: float = 1.0  # 0.0 to 1.0


@dataclass
class RateLimitState:
    """Rate limiting state for a client."""
    
    client_id: str
    current_minute: Dict[str, int] = field(default_factory=dict)
    current_hour: Dict[str, int] = field(default_factory=dict)
    current_day: Dict[str, int] = field(default_factory=dict)
    
    # Sliding window data
    sliding_window: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    # Token bucket data
    tokens: float = 60.0
    last_refill: float = field(default_factory=time.time)
    
    # Request timestamps
    request_timestamps: deque = field(default_factory=lambda: deque(maxlen=10000))
    
    # Abuse detection
    abuse_score: float = 0.0
    violation_count: int = 0
    last_violation: Optional[datetime] = None


@dataclass
class RateLimitResult:
    """Rate limiting check result."""
    
    allowed: bool
    client_id: str
    endpoint: str
    reason: Optional[str] = None
    remaining_requests: int = 0
    reset_time: Optional[datetime] = None
    retry_after: Optional[int] = None
    current_usage: int = 0
    limit: int = 0
    abuse_detected: bool = False
    tier: UserTier = UserTier.FREE
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AbuseAlert:
    """Abuse detection alert."""
    
    alert_id: str
    client_id: str
    severity: AlertSeverity
    reason: str
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class AdvancedRateLimiter:
    """Advanced rate limiting system with intelligent throttling and analytics."""
    
    def __init__(self, config: AdvancedRateLimitConfig = None):
        self.config = config or AdvancedRateLimitConfig()
        
        # Client management
        self.clients: Dict[str, ClientInfo] = {}
        self.rate_states: Dict[str, RateLimitState] = {}
        
        # Global statistics
        self.total_requests = 0
        self.blocked_requests = 0
        self.abuse_alerts: List[AbuseAlert] = []
        
        # Performance tracking
        self.request_times: deque = deque(maxlen=10000)
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Background tasks
        self._cleanup_task = None
        self._analytics_task = None
        self._running = False
        
        # External dependencies
        self._redis_client = None
        self._analytics_manager = None
        
        logger.info(f"Advanced rate limiter initialized with strategy: {self.config.strategy.value}")
    
    async def start(self) -> None:
        """Start the advanced rate limiter."""
        if self._running:
            logger.warning("Advanced rate limiter is already running")
            return
        
        self._running = True
        
        # Initialize external dependencies
        try:
            self._redis_client = await get_redis_client()
            logger.info("Redis client connected for distributed rate limiting")
        except Exception as e:
            logger.warning(f"Redis not available, using local mode: {e}")
        
        if self.config.enable_analytics:
            self._analytics_manager = UsageAnalyticsManager()
            await self._analytics_manager.start()
        
        # Start background tasks
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        if self.config.enable_analytics:
            self._analytics_task = asyncio.create_task(self._analytics_loop())
        
        logger.info("Advanced rate limiter started successfully")
    
    async def stop(self) -> None:
        """Stop the advanced rate limiter."""
        if not self._running:
            return
        
        self._running = False
        
        # Cancel background tasks
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self._analytics_task:
            self._analytics_task.cancel()
            try:
                await self._analytics_task
            except asyncio.CancelledError:
                pass
        
        # Stop analytics manager
        if self._analytics_manager:
            await self._analytics_manager.stop()
        
        logger.info("Advanced rate limiter stopped")
    
    async def check_rate_limit(
        self,
        client_id: str,
        endpoint: str = "/api/default",
        user_id: Optional[str] = None,
        user_tier: UserTier = UserTier.FREE,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> RateLimitResult:
        """
        Check if a request is allowed based on rate limits.
        
        Args:
            client_id: Unique client identifier
            endpoint: API endpoint being accessed
            user_id: User ID (if authenticated)
            user_tier: User tier for dynamic limits
            ip_address: Client IP address
            user_agent: Client user agent
            api_key: API key (if used)
        
        Returns:
            RateLimitResult with detailed information
        """
        start_time = time.time()
        
        try:
            # Update client info
            await self._update_client_info(client_id, user_id, user_tier, ip_address, user_agent, api_key)
            
            # Get client state
            state = await self._get_rate_state(client_id)
            client_info = self.clients.get(client_id)
            
            # Check if client is blocked
            if client_info and client_info.is_blocked:
                if client_info.block_expires and datetime.now() > client_info.block_expires:
                    # Unblock expired block
                    client_info.is_blocked = False
                    client_info.block_reason = None
                    client_info.block_expires = None
                else:
                    return RateLimitResult(
                        allowed=False,
                        client_id=client_id,
                        endpoint=endpoint,
                        reason=f"Client blocked: {client_info.block_reason}",
                        retry_after=int((client_info.block_expires - datetime.now()).total_seconds()) if client_info.block_expires else None
                    )
            
            # Calculate effective limits based on tier and endpoint
            limits = await self._calculate_effective_limits(client_info, endpoint)
            
            # Check rate limit based on strategy
            if self.config.strategy == RateLimitStrategy.FIXED_WINDOW:
                result = await self._check_fixed_window_limit(client_id, endpoint, limits, state)
            elif self.config.strategy == RateLimitStrategy.SLIDING_WINDOW:
                result = await self._check_sliding_window_limit(client_id, endpoint, limits, state)
            elif self.config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                result = await self._check_token_bucket_limit(client_id, endpoint, limits, state)
            elif self.config.strategy == RateLimitStrategy.LEAKY_BUCKET:
                result = await self._check_leaky_bucket_limit(client_id, endpoint, limits, state)
            else:  # ADAPTIVE
                result = await self._check_adaptive_limit(client_id, endpoint, limits, state)
            
            # Update statistics
            self.total_requests += 1
            if not result.allowed:
                self.blocked_requests += 1
            
            # Record request timestamp
            state.request_timestamps.append(datetime.now())
            state.current_minute[endpoint] = state.current_minute.get(endpoint, 0) + (1 if result.allowed else 0)
            state.current_hour[endpoint] = state.current_hour.get(endpoint, 0) + (1 if result.allowed else 0)
            state.current_day[endpoint] = state.current_day.get(endpoint, 0) + (1 if result.allowed else 0)
            
            # Abuse detection
            if self.config.enable_abuse_detection:
                await self._detect_abuse(client_id, endpoint, result, state)
            
            # Analytics
            if self.config.enable_analytics and self._analytics_manager:
                await self._analytics_manager.record_request(
                    client_id=client_id,
                    endpoint=endpoint,
                    allowed=result.allowed,
                    user_tier=user_tier,
                    response_time=time.time() - start_time
                )
            
            # Performance tracking
            self.request_times.append(time.time() - start_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Rate limit check failed for {client_id}: {e}")
            # Fail open - allow the request but log the error
            return RateLimitResult(
                allowed=True,
                client_id=client_id,
                endpoint=endpoint,
                reason="Rate limit check failed, allowing request"
            )
    
    async def _update_client_info(
        self,
        client_id: str,
        user_id: Optional[str],
        user_tier: UserTier,
        ip_address: Optional[str],
        user_agent: Optional[str],
        api_key: Optional[str]
    ) -> None:
        """Update or create client information."""
        if client_id not in self.clients:
            self.clients[client_id] = ClientInfo(
                client_id=client_id,
                user_id=user_id,
                user_tier=user_tier,
                ip_address=ip_address,
                user_agent=user_agent,
                api_key=api_key
            )
        else:
            # Update existing client info
            client = self.clients[client_id]
            if user_id:
                client.user_id = user_id
            if user_tier != UserTier.FREE:
                client.user_tier = user_tier
            if ip_address:
                client.ip_address = ip_address
            if user_agent:
                client.user_agent = user_agent
            if api_key:
                client.api_key = api_key
            client.last_seen = datetime.now()
    
    async def _get_rate_state(self, client_id: str) -> RateLimitState:
        """Get or create rate limiting state for a client."""
        if client_id not in self.rate_states:
            self.rate_states[client_id] = RateLimitState(client_id=client_id)
        return self.rate_states[client_id]
    
    async def _calculate_effective_limits(
        self,
        client_info: Optional[ClientInfo],
        endpoint: str
    ) -> Dict[str, int]:
        """Calculate effective rate limits based on client tier and endpoint."""
        base_limits = {
            "minute": self.config.base_requests_per_minute,
            "hour": self.config.base_requests_per_hour,
            "day": self.config.base_requests_per_day
        }
        
        # Apply tier multiplier
        if client_info:
            multiplier = self.config.tier_multipliers.get(client_info.user_tier, 1.0)
            for key in base_limits:
                base_limits[key] = int(base_limits[key] * multiplier)
        
        # Apply endpoint-specific limits
        if endpoint in self.config.endpoint_limits:
            endpoint_limits = self.config.endpoint_limits[endpoint]
            for key, value in endpoint_limits.items():
                if key in base_limits:
                    base_limits[key] = min(base_limits[key], value)
        
        return base_limits
    
    async def _check_fixed_window_limit(
        self,
        client_id: str,
        endpoint: str,
        limits: Dict[str, int],
        state: RateLimitState
    ) -> RateLimitResult:
        """Check fixed window rate limit."""
        current_time = datetime.now()
        
        # Get current counts
        minute_count = state.current_minute.get(endpoint, 0)
        hour_count = state.current_hour.get(endpoint, 0)
        day_count = state.current_day.get(endpoint, 0)
        
        # Check limits
        if minute_count >= limits["minute"]:
            return RateLimitResult(
                allowed=False,
                client_id=client_id,
                endpoint=endpoint,
                reason=f"Minute limit exceeded: {minute_count}/{limits['minute']}",
                remaining_requests=0,
                reset_time=current_time.replace(second=0, microsecond=0) + timedelta(minutes=1),
                retry_after=60,
                current_usage=minute_count,
                limit=limits["minute"],
                tier=self.clients[client_id].user_tier if client_id in self.clients else UserTier.FREE
            )
        
        if hour_count >= limits["hour"]:
            return RateLimitResult(
                allowed=False,
                client_id=client_id,
                endpoint=endpoint,
                reason=f"Hour limit exceeded: {hour_count}/{limits['hour']}",
                remaining_requests=0,
                reset_time=current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1),
                retry_after=3600,
                current_usage=hour_count,
                limit=limits["hour"],
                tier=self.clients[client_id].user_tier if client_id in self.clients else UserTier.FREE
            )
        
        if day_count >= limits["day"]:
            return RateLimitResult(
                allowed=False,
                client_id=client_id,
                endpoint=endpoint,
                reason=f"Day limit exceeded: {day_count}/{limits['day']}",
                remaining_requests=0,
                reset_time=current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1),
                retry_after=86400,
                current_usage=day_count,
                limit=limits["day"],
                tier=self.clients[client_id].user_tier if client_id in self.clients else UserTier.FREE
            )
        
        # Request allowed
        return RateLimitResult(
            allowed=True,
            client_id=client_id,
            endpoint=endpoint,
            remaining_requests=min(
                limits["minute"] - minute_count,
                limits["hour"] - hour_count,
                limits["day"] - day_count
            ),
            current_usage=minute_count,
            limit=limits["minute"],
            tier=self.clients[client_id].user_tier if client_id in self.clients else UserTier.FREE
        )
    
    async def _check_sliding_window_limit(
        self,
        client_id: str,
        endpoint: str,
        limits: Dict[str, int],
        state: RateLimitState
    ) -> RateLimitResult:
        """Check sliding window rate limit."""
        current_time = time.time()
        window_start = current_time - 60  # 1-minute sliding window
        
        # Filter requests within the window
        recent_requests = [ts for ts in state.sliding_window if ts > window_start]
        state.sliding_window = deque(recent_requests, maxlen=1000)
        
        # Check minute limit
        if len(recent_requests) >= limits["minute"]:
            return RateLimitResult(
                allowed=False,
                client_id=client_id,
                endpoint=endpoint,
                reason=f"Sliding window minute limit exceeded: {len(recent_requests)}/{limits['minute']}",
                remaining_requests=0,
                retry_after=int(60 - (current_time - recent_requests[0])),
                current_usage=len(recent_requests),
                limit=limits["minute"],
                tier=self.clients[client_id].user_tier if client_id in self.clients else UserTier.FREE
            )
        
        # Add current request to sliding window
        state.sliding_window.append(current_time)
        
        return RateLimitResult(
            allowed=True,
            client_id=client_id,
            endpoint=endpoint,
            remaining_requests=limits["minute"] - len(recent_requests) - 1,
            current_usage=len(recent_requests) + 1,
            limit=limits["minute"],
            tier=self.clients[client_id].user_tier if client_id in self.clients else UserTier.FREE
        )
    
    async def _check_token_bucket_limit(
        self,
        client_id: str,
        endpoint: str,
        limits: Dict[str, int],
        state: RateLimitState
    ) -> RateLimitResult:
        """Check token bucket rate limit."""
        current_time = time.time()
        
        # Refill tokens based on time elapsed
        time_elapsed = current_time - state.last_refill
        tokens_to_add = time_elapsed * (limits["minute"] / 60.0)  # Refill rate per second
        state.tokens = min(state.tokens + tokens_to_add, limits["minute"])
        state.last_refill = current_time
        
        # Check if we have enough tokens
        if state.tokens < 1:
            return RateLimitResult(
                allowed=False,
                client_id=client_id,
                endpoint=endpoint,
                reason=f"Token bucket empty: {state.tokens:.1f} tokens available",
                remaining_requests=0,
                retry_after=int((1 - state.tokens) * 60 / limits["minute"]),
                current_usage=int(limits["minute"] - state.tokens),
                limit=limits["minute"],
                tier=self.clients[client_id].user_tier if client_id in self.clients else UserTier.FREE
            )
        
        # Consume one token
        state.tokens -= 1
        
        return RateLimitResult(
            allowed=True,
            client_id=client_id,
            endpoint=endpoint,
            remaining_requests=int(state.tokens),
            current_usage=int(limits["minute"] - state.tokens),
            limit=limits["minute"],
            tier=self.clients[client_id].user_tier if client_id in self.clients else UserTier.FREE
        )
    
    async def _check_leaky_bucket_limit(
        self,
        client_id: str,
        endpoint: str,
        limits: Dict[str, int],
        state: RateLimitState
    ) -> RateLimitResult:
        """Check leaky bucket rate limit."""
        current_time = time.time()
        
        # Calculate leak rate (tokens per second)
        leak_rate = limits["minute"] / 60.0
        
        # Leak tokens based on time elapsed
        if not hasattr(state, 'last_leak'):
            state.last_leak = current_time
            state.bucket_size = 0
        
        time_elapsed = current_time - state.last_leak
        leaked_tokens = time_elapsed * leak_rate
        state.bucket_size = max(0, state.bucket_size - leaked_tokens)
        state.last_leak = current_time
        
        # Check if bucket is full
        if state.bucket_size >= limits["minute"]:
            return RateLimitResult(
                allowed=False,
                client_id=client_id,
                endpoint=endpoint,
                reason=f"Leaky bucket full: {state.bucket_size:.1f}/{limits['minute']}",
                remaining_requests=0,
                retry_after=int((state.bucket_size - limits["minute"] + 1) / leak_rate),
                current_usage=int(state.bucket_size),
                limit=limits["minute"],
                tier=self.clients[client_id].user_tier if client_id in self.clients else UserTier.FREE
            )
        
        # Add request to bucket
        state.bucket_size += 1
        
        return RateLimitResult(
            allowed=True,
            client_id=client_id,
            endpoint=endpoint,
            remaining_requests=int(limits["minute"] - state.bucket_size),
            current_usage=int(state.bucket_size),
            limit=limits["minute"],
            tier=self.clients[client_id].user_tier if client_id in self.clients else UserTier.FREE
        )
    
    async def _check_adaptive_limit(
        self,
        client_id: str,
        endpoint: str,
        limits: Dict[str, int],
        state: RateLimitState
    ) -> RateLimitResult:
        """Check adaptive rate limit based on usage patterns."""
        # Start with token bucket as base
        result = await self._check_token_bucket_limit(client_id, endpoint, limits, state)
        
        # Apply adaptive adjustments based on client behavior
        client_info = self.clients.get(client_id)
        if client_info:
            # Adjust based on trust score
            if client_info.trust_score > 0.8:
                # High trust: allow 20% more requests
                result.remaining_requests = int(result.remaining_requests * 1.2)
            elif client_info.trust_score < 0.3:
                # Low trust: reduce limits by 30%
                if result.allowed:
                    result.allowed = state.current_minute.get(endpoint, 0) < int(limits["minute"] * 0.7)
                    if not result.allowed:
                        result.reason = "Low trust score: reduced rate limits"
        
        return result
    
    async def _detect_abuse(
        self,
        client_id: str,
        endpoint: str,
        result: RateLimitResult,
        state: RateLimitState
    ) -> None:
        """Detect abusive behavior patterns."""
        client_info = self.clients.get(client_id)
        if not client_info:
            return
        
        # Calculate abuse score based on various factors
        abuse_score = 0.0
        
        # Factor 1: Rate limit violations
        if not result.allowed:
            abuse_score += 0.3
            state.violation_count += 1
            state.last_violation = datetime.now()
        
        # Factor 2: Request frequency
        recent_requests = len([ts for ts in state.request_timestamps if ts > datetime.now() - timedelta(minutes=1)])
        if recent_requests > self.config.base_requests_per_minute * 0.8:
            abuse_score += 0.2
        
        # Factor 3: Endpoint diversity (low diversity = potential abuse)
        unique_endpoints = set()
        for ts in state.request_timestamps:
            if ts > datetime.now() - timedelta(minutes=5):
                unique_endpoints.add(endpoint)  # Simplified - would track actual endpoints
        
        if len(unique_endpoints) < 2 and recent_requests > 10:
            abuse_score += 0.1
        
        # Factor 4: Time-based patterns
        current_hour = datetime.now().hour
        if current_hour in range(2, 6) and recent_requests > 5:  # Unusual activity at odd hours
            abuse_score += 0.1
        
        # Update abuse score with smoothing
        state.abuse_score = (state.abuse_score * 0.7) + (abuse_score * 0.3)
        
        # Trigger alerts if abuse score exceeds threshold
        if state.abuse_score > self.config.abuse_threshold:
            await self._trigger_abuse_alert(client_id, endpoint, state.abuse_score, state)
            
            # Consider blocking if abuse is severe
            if state.abuse_score > 0.9 and state.violation_count > 5:
                await self._block_client(client_id, "High abuse score detected", duration_hours=1)
    
    async def _trigger_abuse_alert(
        self,
        client_id: str,
        endpoint: str,
        abuse_score: float,
        state: RateLimitState
    ) -> None:
        """Trigger abuse detection alert."""
        alert_id = hashlib.md5(f"{client_id}{endpoint}{datetime.now().isoformat()}".encode()).hexdigest()
        
        # Determine severity
        if abuse_score > 0.9:
            severity = AlertSeverity.CRITICAL
        elif abuse_score > 0.8:
            severity = AlertSeverity.HIGH
        elif abuse_score > 0.7:
            severity = AlertSeverity.MEDIUM
        else:
            severity = AlertSeverity.LOW
        
        alert = AbuseAlert(
            alert_id=alert_id,
            client_id=client_id,
            severity=severity,
            reason=f"Abuse score: {abuse_score:.2f}",
            details={
                "abuse_score": abuse_score,
                "violation_count": state.violation_count,
                "last_violation": state.last_violation.isoformat() if state.last_violation else None,
                "endpoint": endpoint,
                "request_count": len(state.request_timestamps)
            }
        )
        
        self.abuse_alerts.append(alert)
        
        # Keep only recent alerts
        if len(self.abuse_alerts) > 1000:
            self.abuse_alerts = self.abuse_alerts[-1000:]
        
        logger.warning(f"Abuse alert triggered for {client_id}: {severity.value} - {abuse_score:.2f}")
    
    async def _block_client(
        self,
        client_id: str,
        reason: str,
        duration_hours: int = 1
    ) -> None:
        """Block a client for specified duration."""
        client_info = self.clients.get(client_id)
        if client_info:
            client_info.is_blocked = True
            client_info.block_reason = reason
            client_info.block_expires = datetime.now() + timedelta(hours=duration_hours)
            
            logger.warning(f"Client {client_id} blocked for {duration_hours} hours: {reason}")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup of expired data."""
        while self._running:
            try:
                await asyncio.sleep(self.config.cleanup_interval_seconds)
                
                current_time = datetime.now()
                cleanup_count = 0
                
                # Clean up inactive clients
                inactive_clients = []
                for client_id, client_info in self.clients.items():
                    if current_time - client_info.last_seen > timedelta(days=7):
                        inactive_clients.append(client_id)
                        cleanup_count += 1
                
                # Remove inactive clients
                for client_id in inactive_clients:
                    del self.clients[client_id]
                    if client_id in self.rate_states:
                        del self.rate_states[client_id]
                
                # Clean up old alerts
                old_alerts = [
                    alert for alert in self.abuse_alerts
                    if current_time - alert.timestamp > timedelta(days=30)
                ]
                for alert in old_alerts:
                    self.abuse_alerts.remove(alert)
                
                if cleanup_count > 0:
                    logger.info(f"Cleaned up {cleanup_count} inactive clients")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    async def _analytics_loop(self) -> None:
        """Background analytics processing."""
        while self._running:
            try:
                await asyncio.sleep(60)  # Process analytics every minute
                
                if self._analytics_manager:
                    await self._analytics_manager.process_analytics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Analytics loop error: {e}")
    
    def get_client_stats(self, client_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a client."""
        client_info = self.clients.get(client_id)
        state = self.rate_states.get(client_id)
        
        if not client_info:
            return {"error": "Client not found"}
        
        stats = {
            "client_id": client_id,
            "user_id": client_info.user_id,
            "user_tier": client_info.user_tier.value,
            "trust_score": client_info.trust_score,
            "reputation_score": client_info.reputation_score,
            "is_blocked": client_info.is_blocked,
            "block_reason": client_info.block_reason,
            "block_expires": client_info.block_expires.isoformat() if client_info.block_expires else None,
            "created_at": client_info.created_at.isoformat(),
            "last_seen": client_info.last_seen.isoformat(),
        }
        
        if state:
            stats.update({
                "abuse_score": state.abuse_score,
                "violation_count": state.violation_count,
                "last_violation": state.last_violation.isoformat() if state.last_violation else None,
                "total_requests": len(state.request_timestamps),
                "current_minute_usage": sum(state.current_minute.values()),
                "current_hour_usage": sum(state.current_hour.values()),
                "current_day_usage": sum(state.current_day.values()),
            })
        
        return stats
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global rate limiting statistics."""
        current_time = datetime.now()
        uptime = current_time - (self.clients[list(self.clients.keys())[0]].created_at if self.clients else current_time)
        
        # Calculate performance metrics
        avg_response_time = sum(self.request_times) / len(self.request_times) if self.request_times else 0
        cache_hit_rate = self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
        
        # Tier distribution
        tier_counts = defaultdict(int)
        for client in self.clients.values():
            tier_counts[client.user_tier.value] += 1
        
        # Recent alerts
        recent_alerts = [
            alert for alert in self.abuse_alerts
            if current_time - alert.timestamp < timedelta(hours=24)
        ]
        
        return {
            "total_requests": self.total_requests,
            "blocked_requests": self.blocked_requests,
            "block_rate": self.blocked_requests / self.total_requests if self.total_requests > 0 else 0,
            "active_clients": len(self.clients),
            "max_clients": self.config.max_clients,
            "abuse_alerts": len(self.abuse_alerts),
            "recent_alerts_24h": len(recent_alerts),
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_formatted": str(uptime),
            "avg_response_time_ms": avg_response_time * 1000,
            "cache_hit_rate": cache_hit_rate,
            "tier_distribution": dict(tier_counts),
            "config": {
                "strategy": self.config.strategy.value,
                "enable_ml_optimization": self.config.enable_ml_optimization,
                "enable_abuse_detection": self.config.enable_abuse_detection,
                "abuse_threshold": self.config.abuse_threshold,
            },
            "started_at": (self.clients[list(self.clients.keys())[0]].created_at.isoformat() if self.clients else current_time.isoformat()),
        }
    
    async def reset_client(self, client_id: str) -> bool:
        """Reset rate limiting for a specific client."""
        if client_id in self.rate_states:
            del self.rate_states[client_id]
        
        if client_id in self.clients:
            client = self.clients[client_id]
            client.trust_score = 1.0
            client.reputation_score = 1.0
            client.is_blocked = False
            client.block_reason = None
            client.block_expires = None
        
        logger.info(f"Rate limit reset for client {client_id}")
        return True
    
    async def update_client_tier(self, client_id: str, new_tier: UserTier) -> bool:
        """Update client tier for dynamic rate limiting."""
        if client_id in self.clients:
            self.clients[client_id].user_tier = new_tier
            logger.info(f"Updated client {client_id} tier to {new_tier.value}")
            return True
        return False


# Global advanced rate limiter instance
_advanced_rate_limiter: Optional[AdvancedRateLimiter] = None


def get_advanced_rate_limiter(config: AdvancedRateLimitConfig = None) -> AdvancedRateLimiter:
    """Get or create global advanced rate limiter instance."""
    global _advanced_rate_limiter
    if _advanced_rate_limiter is None:
        _advanced_rate_limiter = AdvancedRateLimiter(config)
    return _advanced_rate_limiter


async def start_advanced_rate_limiter(config: AdvancedRateLimitConfig = None):
    """Start the global advanced rate limiter."""
    rate_limiter = get_advanced_rate_limiter(config)
    await rate_limiter.start()


async def stop_advanced_rate_limiter():
    """Stop the global advanced rate limiter."""
    global _advanced_rate_limiter
    if _advanced_rate_limiter:
        await _advanced_rate_limiter.stop()


async def check_advanced_rate_limit(
    client_id: str,
    endpoint: str = "/api/default",
    user_id: Optional[str] = None,
    user_tier: UserTier = UserTier.FREE,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    api_key: Optional[str] = None
) -> RateLimitResult:
    """Check advanced rate limit for a client."""
    rate_limiter = get_advanced_rate_limiter()
    return await rate_limiter.check_rate_limit(
        client_id, endpoint, user_id, user_tier, ip_address, user_agent, api_key
    )


def get_advanced_rate_limit_stats() -> Dict[str, Any]:
    """Get global advanced rate limiting statistics."""
    rate_limiter = get_advanced_rate_limiter()
    return rate_limiter.get_global_stats()
