"""
Intelligent API Rate Limiting with Behavioral Analysis
Provides adaptive rate limiting based on user behavior patterns and threat intelligence.
"""

import asyncio
import time
import json
import logging
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from collections import defaultdict, deque
import statistics
import math

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    ADAPTIVE = "adaptive"
    BEHAVIORAL = "behavioral"


class ThreatLevel(Enum):
    """Threat levels for rate limiting."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserType(Enum):
    """User types for rate limiting."""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    user_type: UserType
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int
    strategy: RateLimitStrategy
    adaptive_threshold: float = 0.8
    behavioral_weight: float = 0.3
    
    # Advanced settings
    enable_throttling: bool = True
    enable_blocking: bool = True
    enable_adaptive: bool = True
    enable_behavioral: bool = True
    
    # Time windows
    window_size_minutes: int = 1
    sliding_window_size: int = 10
    
    # Behavioral parameters
    anomaly_threshold: float = 2.0
    learning_rate: float = 0.1
    history_size: int = 1000


@dataclass
class RateLimitEvent:
    """Rate limit event record."""
    timestamp: datetime
    user_id: str
    client_ip: str
    endpoint: str
    method: str
    user_agent: str
    response_status: int
    response_time_ms: int
    blocked: bool
    reason: Optional[str]
    remaining_requests: int
    reset_time: datetime


@dataclass
class BehavioralProfile:
    """User behavioral profile for rate limiting."""
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    # Request patterns
    typical_request_rate: float
    typical_endpoints: Dict[str, int]
    typical_response_times: List[float]
    typical_hours: Set[int]
    
    # Behavioral metrics
    burst_frequency: float
    error_rate: float
    timeout_rate: float
    concurrent_requests: float
    
    # Anomaly detection
    anomaly_score: float
    last_anomaly: Optional[datetime]
    anomaly_count: int
    
    # Trust score
    trust_score: float
    risk_score: float
    
    # History
    request_history: deque
    blocked_requests: int


class IntelligentRateLimiter:
    """Intelligent rate limiter with behavioral analysis."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        
        # Rate limit configurations
        self.rate_configs: Dict[UserType, RateLimitConfig] = self._initialize_rate_configs()
        
        # Storage
        self.user_profiles: Dict[str, BehavioralProfile] = {}
        self.rate_limit_events: deque = deque(maxlen=10000)
        self.active_requests: Dict[str, int] = defaultdict(int)
        
        # Rate limiting state
        self.request_counters: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.token_buckets: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.blocked_entities: Dict[str, Set[str]] = {
            "users": set(),
            "ips": set(),
            "endpoints": set(),
        }
        
        # Behavioral analysis
        self.behavioral_models = self._initialize_behavioral_models()
        self.anomaly_detector = AnomalyDetector()
        
        # Background tasks
        self._cleanup_task = None
        self._analysis_task = None
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration."""
        return {
            "enable_behavioral_analysis": True,
            "enable_adaptive_rate_limiting": True,
            "enable_threat_intelligence": True,
            "cleanup_interval_minutes": 60,
            "analysis_interval_minutes": 5,
            "default_burst_ratio": 2.0,
            "trust_decay_rate": 0.1,
            "min_trust_score": 0.0,
            "max_trust_score": 1.0,
        }
    
    def _initialize_rate_configs(self) -> Dict[UserType, RateLimitConfig]:
        """Initialize rate limit configurations for different user types."""
        return {
            UserType.FREE: RateLimitConfig(
                user_type=UserType.FREE,
                requests_per_minute=60,
                requests_per_hour=1000,
                requests_per_day=10000,
                burst_limit=120,
                strategy=RateLimitStrategy.ADAPTIVE,
                adaptive_threshold=0.7,
                behavioral_weight=0.4,
            ),
            UserType.PRO: RateLimitConfig(
                user_type=UserType.PRO,
                requests_per_minute=120,
                requests_per_hour=2500,
                requests_per_day=50000,
                burst_limit=240,
                strategy=RateLimitStrategy.BEHAVIORAL,
                adaptive_threshold=0.8,
                behavioral_weight=0.3,
            ),
            UserType.ENTERPRISE: RateLimitConfig(
                user_type=UserType.ENTERPRISE,
                requests_per_minute=300,
                requests_per_hour=10000,
                requests_per_day=1000000,
                burst_limit=600,
                strategy=RateLimitStrategy.BEHAVIORAL,
                adaptive_threshold=0.9,
                behavioral_weight=0.2,
            ),
            UserType.ADMIN: RateLimitConfig(
                user_type=UserType.ADMIN,
                requests_per_minute=500,
                requests_per_hour=20000,
                requests_per_day=2000000,
                burst_limit=1000,
                strategy=RateLimitStrategy.TOKEN_BUCKET,
                adaptive_threshold=0.95,
                behavioral_weight=0.1,
            ),
        }
    
    def _initialize_behavioral_models(self) -> Dict[str, Any]:
        """Initialize behavioral analysis models."""
        return {
            "request_rate_model": {
                "mean": 0.0,
                "std": 1.0,
                "window_size": 100,
            },
            "endpoint_model": {
                "frequencies": defaultdict(int),
                "total": 0,
            },
            "temporal_model": {
                "hourly_patterns": [0.0] * 24,
                "daily_patterns": [0.0] * 7,
            },
            "response_time_model": {
                "mean": 0.0,
                "std": 1.0,
                "percentiles": {},
            }
        }
    
    async def check_rate_limit(
        self,
        user_id: str,
        user_type: UserType,
        client_ip: str,
        endpoint: str,
        method: str,
        user_agent: str = "",
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if request should be rate limited."""
        # Get rate limit configuration
        config = self.rate_configs[user_type]
        
        # Check if user is blocked
        if user_id in self.blocked_entities["users"]:
            return False, self._create_block_response("User blocked", user_id, config)
        
        # Check if IP is blocked
        if client_ip in self.blocked_entities["users"]:
            return False, self._create_block_response("IP blocked", user_id, config)
        
        # Get or create behavioral profile
        profile = await self._get_or_create_profile(user_id)
        
        # Behavioral analysis
        if config.enable_behavioral and self.config["enable_behavioral_analysis"]:
            behavioral_result = await self._analyze_behavior(profile, endpoint, method)
            if behavioral_result["block"]:
                return False, self._create_behavioral_block_response(behavioral_result, config)
        
        # Rate limiting based on strategy
        if config.strategy == RateLimitStrategy.FIXED_WINDOW:
            return await self._check_fixed_window(user_id, config)
        elif config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return await self._check_sliding_window(user_id, config)
        elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return await self._check_token_bucket(user_id, config)
        elif config.strategy == RateLimitStrategy.ADAPTIVE:
            return await self._check_adaptive(user_id, profile, config)
        elif config.strategy == RateLimitStrategy.BEHAVIORAL:
            return await self._check_behavioral(user_id, profile, config)
        else:
            return await self._check_fixed_window(user_id, config)
    
    async def _get_or_create_profile(self, user_id: str) -> BehavioralProfile:
        """Get or create behavioral profile."""
        if user_id not in self.user_profiles:
            profile = BehavioralProfile(
                user_id=user_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                typical_request_rate=0.0,
                typical_endpoints=defaultdict(int),
                typical_response_times=[],
                typical_hours=set(),
                burst_frequency=0.0,
                error_rate=0.0,
                timeout_rate=0.0,
                concurrent_requests=0.0,
                anomaly_score=0.0,
                last_anomaly=None,
                anomaly_count=0,
                trust_score=0.5,  # Start with neutral trust
                risk_score=0.5,
                request_history=deque(maxlen=1000),
                blocked_requests=0,
            )
            self.user_profiles[user_id] = profile
        
        return self.user_profiles[user_id]
    
    async def _analyze_behavior(
        self,
        profile: BehavioralProfile,
        endpoint: str,
        method: str,
    ) -> Dict[str, Any]:
        """Analyze user behavior for anomalies."""
        current_time = datetime.now()
        
        # Calculate current request rate
        recent_requests = [
            req for req in profile.request_history
            if (current_time - req["timestamp"]).total_seconds() <= 60
        ]
        current_rate = len(recent_requests)
        
        # Detect anomalies
        anomalies = []
        
        # Request rate anomaly
        if profile.typical_request_rate > 0:
            rate_deviation = abs(current_rate - profile.typical_request_rate) / profile.typical_request_rate
            if rate_deviation > 2.0:  # 200% deviation
                anomalies.append({
                    "type": "request_rate_anomaly",
                    "severity": "high",
                    "value": rate_deviation,
                    "description": f"Request rate {current_rate} is {rate_deviation:.1f}x typical"
                })
        
        # Endpoint anomaly
        if endpoint not in profile.typical_endpoints:
            anomalies.append({
                "type": "new_endpoint",
                "severity": "medium",
                "value": endpoint,
                "description": f"Access to new endpoint: {endpoint}"
            })
        
        # Time-based anomaly
        current_hour = current_time.hour
        if profile.typical_hours and current_hour not in profile.typical_hours:
            anomalies.append({
                "type": "unusual_time",
                "severity": "low",
                "value": current_hour,
                "description": f"Access at unusual hour: {current_hour}:00"
            })
        
        # Calculate overall anomaly score
        anomaly_score = min(len(anomalies) * 0.3, 1.0)
        
        # Update profile
        profile.anomaly_score = anomaly_score
        if anomalies:
            profile.last_anomaly = current_time
            profile.anomaly_count += 1
        
        # Determine if should block
        should_block = anomaly_score > 0.8 or any(a["severity"] == "high" for a in anomalies)
        
        return {
            "block": should_block,
            "anomaly_score": anomaly_score,
            "anomalies": anomalies,
            "current_rate": current_rate,
            "typical_rate": profile.typical_request_rate,
        }
    
    async def _check_fixed_window(self, user_id: str, config: RateLimitConfig) -> Tuple[bool, Dict[str, Any]]:
        """Check fixed window rate limiting."""
        current_time = datetime.now()
        window_start = current_time.replace(second=0, microsecond=0)
        
        # Get requests in current window
        user_requests = self.request_counters[user_id]
        window_requests = [
            req_time for req_time in user_requests
            if req_time >= window_start
        ]
        
        request_count = len(window_requests)
        remaining = max(0, config.requests_per_minute - request_count)
        reset_time = window_start + timedelta(minutes=1)
        
        if request_count >= config.requests_per_minute:
            return False, self._create_rate_limit_response(config, remaining, reset_time, "Fixed window limit exceeded")
        
        return True, self._create_success_response(config, remaining, reset_time)
    
    async def _check_sliding_window(self, user_id: str, config: RateLimitConfig) -> Tuple[bool, Dict[str, Any]]:
        """Check sliding window rate limiting."""
        current_time = datetime.now()
        window_start = current_time - timedelta(minutes=config.sliding_window_size)
        
        # Get requests in sliding window
        user_requests = self.request_counters[user_id]
        window_requests = [
            req_time for req_time in user_requests
            if req_time >= window_start
        ]
        
        request_count = len(window_requests)
        rate_per_minute = request_count / config.sliding_window_size
        remaining = max(0, config.requests_per_minute - rate_per_minute)
        reset_time = current_time + timedelta(seconds=60)
        
        if rate_per_minute >= config.requests_per_minute:
            return False, self._create_rate_limit_response(config, remaining, reset_time, "Sliding window limit exceeded")
        
        return True, self._create_success_response(config, remaining, reset_time)
    
    async def _check_token_bucket(self, user_id: str, config: RateLimitConfig) -> Tuple[bool, Dict[str, Any]]:
        """Check token bucket rate limiting."""
        current_time = time.time()
        bucket = self.token_buckets[user_id]
        
        # Initialize bucket if not exists
        if "tokens" not in bucket:
            bucket["tokens"] = config.requests_per_minute
            bucket["last_refill"] = current_time
        
        # Refill tokens
        time_passed = current_time - bucket["last_refill"]
        tokens_to_add = time_passed * (config.requests_per_minute / 60.0)
        bucket["tokens"] = min(bucket["tokens"] + tokens_to_add, config.requests_per_minute)
        bucket["last_refill"] = current_time
        
        # Check if request can be processed
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            remaining = int(bucket["tokens"])
            reset_time = datetime.now() + timedelta(seconds=60)
            return True, self._create_success_response(config, remaining, reset_time)
        else:
            # Calculate time until next token
            time_until_token = (1.0 - bucket["tokens"]) * 60.0 / config.requests_per_minute
            reset_time = datetime.now() + timedelta(seconds=time_until_token)
            return False, self._create_rate_limit_response(config, 0, reset_time, "Token bucket empty")
    
    async def _check_adaptive(self, user_id: str, profile: BehavioralProfile, config: RateLimitConfig) -> Tuple[bool, Dict[str, Any]]:
        """Check adaptive rate limiting based on user behavior."""
        # Calculate adaptive limit based on trust score
        trust_multiplier = 0.5 + (profile.trust_score * 1.5)  # 0.5x to 2.0x based on trust
        adaptive_limit = int(config.requests_per_minute * trust_multiplier)
        
        # Apply anomaly penalty
        if profile.anomaly_score > 0.5:
            anomaly_penalty = 1.0 - profile.anomaly_score
            adaptive_limit = int(adaptive_limit * anomaly_penalty)
        
        # Check against adaptive limit
        current_time = datetime.now()
        window_start = current_time.replace(second=0, microsecond=0)
        
        user_requests = self.request_counters[user_id]
        window_requests = [
            req_time for req_time in user_requests
            if req_time >= window_start
        ]
        
        request_count = len(window_requests)
        remaining = max(0, adaptive_limit - request_count)
        reset_time = window_start + timedelta(minutes=1)
        
        if request_count >= adaptive_limit:
            return False, self._create_rate_limit_response(config, remaining, reset_time, f"Adaptive limit exceeded: {adaptive_limit}")
        
        return True, self._create_success_response(config, remaining, reset_time)
    
    async def _check_behavioral(self, user_id: str, profile: BehavioralProfile, config: RateLimitConfig) -> Tuple[bool, Dict[str, Any]]:
        """Check behavioral rate limiting."""
        # Calculate behavioral limit
        base_limit = config.requests_per_minute
        
        # Adjust based on trust score
        trust_adjustment = 0.5 + (profile.trust_score * 1.0)
        
        # Adjust based on anomaly score
        anomaly_adjustment = 1.0 - (profile.anomaly_score * 0.8)
        
        # Calculate final limit
        behavioral_limit = int(base_limit * trust_adjustment * anomaly_adjustment)
        behavioral_limit = max(behavioral_limit, base_limit // 4)  # Minimum 25% of base
        
        # Check current usage
        current_time = datetime.now()
        window_start = current_time.replace(second=0, microsecond=0)
        
        user_requests = self.request_counters[user_id]
        window_requests = [
            req_time for req_time in user_requests
            if req_time >= window_start
        ]
        
        request_count = len(window_requests)
        remaining = max(0, behavioral_limit - request_count)
        reset_time = window_start + timedelta(minutes=1)
        
        if request_count >= behavioral_limit:
            return False, self._create_rate_limit_response(config, remaining, reset_time, f"Behavioral limit exceeded: {behavioral_limit}")
        
        return True, self._create_success_response(config, remaining, reset_time)
    
    def _create_success_response(self, config: RateLimitConfig, remaining: int, reset_time: datetime) -> Dict[str, Any]:
        """Create successful rate limit response."""
        return {
            "allowed": True,
            "limit": config.requests_per_minute,
            "remaining": remaining,
            "reset_time": reset_time.isoformat(),
            "retry_after": None,
            "headers": {
                "X-RateLimit-Limit": str(config.requests_per_minute),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(reset_time.timestamp())),
            }
        }
    
    def _create_rate_limit_response(self, config: RateLimitConfig, remaining: int, reset_time: datetime, reason: str) -> Dict[str, Any]:
        """Create rate limit exceeded response."""
        retry_after = max(1, int((reset_time - datetime.now()).total_seconds()))
        
        return {
            "allowed": False,
            "limit": config.requests_per_minute,
            "remaining": remaining,
            "reset_time": reset_time.isoformat(),
            "retry_after": retry_after,
            "reason": reason,
            "headers": {
                "X-RateLimit-Limit": str(config.requests_per_minute),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(reset_time.timestamp())),
                "Retry-After": str(retry_after),
            }
        }
    
    def _create_block_response(self, reason: str, user_id: str, config: RateLimitConfig) -> Dict[str, Any]:
        """Create block response."""
        return {
            "allowed": False,
            "blocked": True,
            "reason": reason,
            "user_id": user_id,
            "reset_time": None,
            "retry_after": 3600,  # 1 hour
            "headers": {
                "X-RateLimit-Limited": "true",
                "X-RateLimit-Reason": reason,
                "Retry-After": "3600",
            }
        }
    
    def _create_behavioral_block_response(self, behavioral_result: Dict[str, Any], config: RateLimitConfig) -> Dict[str, Any]:
        """Create behavioral block response."""
        return {
            "allowed": False,
            "blocked": True,
            "reason": "Behavioral anomaly detected",
            "anomaly_score": behavioral_result["anomaly_score"],
            "anomalies": behavioral_result["anomalies"],
            "reset_time": (datetime.now() + timedelta(minutes=15)).isoformat(),
            "retry_after": 900,  # 15 minutes
            "headers": {
                "X-RateLimit-Limited": "true",
                "X-RateLimit-Reason": "behavioral_anomaly",
                "X-Anomaly-Score": str(behavioral_result["anomaly_score"]),
                "Retry-After": "900",
            }
        }
    
    async def record_request(
        self,
        user_id: str,
        client_ip: str,
        endpoint: str,
        method: str,
        user_agent: str,
        response_status: int,
        response_time_ms: int,
        rate_limit_result: Dict[str, Any],
    ):
        """Record request for behavioral analysis."""
        current_time = datetime.now()
        
        # Add to request history
        self.request_counters[user_id].append(current_time)
        
        # Update user profile
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            profile.request_history.append({
                "timestamp": current_time,
                "endpoint": endpoint,
                "method": method,
                "status": response_status,
                "response_time": response_time_ms,
            })
            
            # Update behavioral metrics
            await self._update_behavioral_metrics(profile, endpoint, response_status, response_time_ms)
        
        # Create rate limit event
        event = RateLimitEvent(
            timestamp=current_time,
            user_id=user_id,
            client_ip=client_ip,
            endpoint=endpoint,
            method=method,
            user_agent=user_agent,
            response_status=response_status,
            response_time_ms=response_time_ms,
            blocked=not rate_limit_result.get("allowed", True),
            reason=rate_limit_result.get("reason"),
            remaining_requests=rate_limit_result.get("remaining", 0),
            reset_time=datetime.fromisoformat(rate_limit_result.get("reset_time", current_time.isoformat())),
        )
        
        self.rate_limit_events.append(event)
    
    async def _update_behavioral_metrics(
        self,
        profile: BehavioralProfile,
        endpoint: str,
        response_status: int,
        response_time_ms: int,
    ):
        """Update behavioral metrics for user profile."""
        profile.updated_at = datetime.now()
        
        # Update endpoint frequencies
        profile.typical_endpoints[endpoint] += 1
        
        # Update response times
        profile.typical_response_times.append(response_time_ms / 1000.0)  # Convert to seconds
        if len(profile.typical_response_times) > 100:
            profile.typical_response_times = profile.typical_response_times[-50:]
        
        # Update error rate
        if response_status >= 400:
            profile.error_rate = (profile.error_rate * 0.9) + 0.1  # Exponential moving average
        else:
            profile.error_rate = profile.error_rate * 0.9
        
        # Update typical request rate
        recent_requests = [
            req for req in profile.request_history
            if (datetime.now() - req["timestamp"]).total_seconds() <= 300  # Last 5 minutes
        ]
        profile.typical_request_rate = len(recent_requests) / 5.0  # Requests per minute
        
        # Update typical hours
        current_hour = datetime.now().hour
        profile.typical_hours.add(current_hour)
        
        # Update trust score based on behavior
        await self._update_trust_score(profile)
    
    async def _update_trust_score(self, profile: BehavioralProfile):
        """Update trust score based on user behavior."""
        # Base trust score starts at 0.5
        trust_score = 0.5
        
        # Positive factors
        if profile.error_rate < 0.05:  # Low error rate
            trust_score += 0.2
        if profile.anomaly_score < 0.1:  # Low anomaly score
            trust_score += 0.2
        if profile.blocked_requests == 0:  # No blocked requests
            trust_score += 0.1
        
        # Negative factors
        if profile.error_rate > 0.2:  # High error rate
            trust_score -= 0.3
        if profile.anomaly_score > 0.5:  # High anomaly score
            trust_score -= 0.3
        if profile.blocked_requests > 5:  # Many blocked requests
            trust_score -= 0.2
        
        # Clamp between 0 and 1
        profile.trust_score = max(0.0, min(1.0, trust_score))
        profile.risk_score = 1.0 - profile.trust_score
    
    def block_entity(self, entity_type: str, entity_id: str, reason: str = "", duration_minutes: int = 60):
        """Block an entity (user, IP, endpoint)."""
        if entity_type in self.blocked_entities:
            self.blocked_entities[entity_type].add(entity_id)
            logger.warning(f"Blocked {entity_type}: {entity_id} - {reason}")
            
            # Schedule unblock
            if duration_minutes > 0:
                asyncio.create_task(self._schedule_unblock(entity_type, entity_id, duration_minutes))
    
    async def _schedule_unblock(self, entity_type: str, entity_id: str, duration_minutes: int):
        """Schedule unblocking of an entity."""
        await asyncio.sleep(duration_minutes * 60)
        self.unblock_entity(entity_type, entity_id)
    
    def unblock_entity(self, entity_type: str, entity_id: str):
        """Unblock an entity."""
        if entity_type in self.blocked_entities:
            self.blocked_entities[entity_type].discard(entity_id)
            logger.info(f"Unblocked {entity_type}: {entity_id}")
    
    def get_rate_limit_metrics(self) -> Dict[str, Any]:
        """Get rate limiting metrics."""
        current_time = datetime.now()
        last_hour = current_time - timedelta(hours=1)
        
        # Recent events
        recent_events = [
            event for event in self.rate_limit_events
            if event.timestamp >= last_hour
        ]
        
        # Calculate metrics
        total_requests = len(recent_events)
        blocked_requests = len([e for e in recent_events if e.blocked])
        
        # User type distribution
        user_type_metrics = {}
        for user_type in UserType:
            user_type_metrics[user_type.value] = {
                "total_requests": 0,
                "blocked_requests": 0,
                "block_rate": 0.0,
            }
        
        # Behavioral metrics
        trust_scores = [profile.trust_score for profile in self.user_profiles.values()]
        anomaly_scores = [profile.anomaly_score for profile in self.user_profiles.values()]
        
        return {
            "total_requests": total_requests,
            "blocked_requests": blocked_requests,
            "block_rate": blocked_requests / max(total_requests, 1),
            "active_profiles": len(self.user_profiles),
            "blocked_entities": {
                entity_type: len(entities) 
                for entity_type, entities in self.blocked_entities.items()
            },
            "user_type_metrics": user_type_metrics,
            "behavioral_metrics": {
                "average_trust_score": statistics.mean(trust_scores) if trust_scores else 0.0,
                "average_anomaly_score": statistics.mean(anomaly_scores) if anomaly_scores else 0.0,
                "high_risk_users": len([score for score in trust_scores if score < 0.3]),
                "anomalous_users": len([score for score in anomaly_scores if score > 0.5]),
            },
            "rate_limit_strategies": {
                user_type.value: config.strategy.value 
                for user_type, config in self.rate_configs.items()
            },
        }
    
    def get_user_profile(self, user_id: str) -> Optional[BehavioralProfile]:
        """Get behavioral profile for user."""
        return self.user_profiles.get(user_id)
    
    def export_rate_limit_data(self, hours: int = 24) -> Dict[str, Any]:
        """Export rate limiting data for analysis."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        events = [
            asdict(event) for event in self.rate_limit_events
            if event.timestamp >= cutoff
        ]
        
        profiles = {
            user_id: asdict(profile) 
            for user_id, profile in self.user_profiles.items()
        }
        
        return {
            "export_timestamp": datetime.now().isoformat(),
            "period_hours": hours,
            "events": events,
            "profiles": profiles,
            "metrics": self.get_rate_limit_metrics(),
        }


class AnomalyDetector:
    """Anomaly detection for behavioral analysis."""
    
    def __init__(self):
        self.thresholds = {
            "request_rate_zscore": 2.0,
            "response_time_zscore": 2.5,
            "error_rate_threshold": 0.2,
            "endpoint_deviation_threshold": 0.8,
        }
    
    def detect_request_rate_anomaly(self, current_rate: float, historical_rates: List[float]) -> bool:
        """Detect request rate anomaly using z-score."""
        if len(historical_rates) < 10:
            return False
        
        mean_rate = statistics.mean(historical_rates)
        std_rate = statistics.stdev(historical_rates)
        
        if std_rate == 0:
            return False
        
        z_score = abs(current_rate - mean_rate) / std_rate
        return z_score > self.thresholds["request_rate_zscore"]
    
    def detect_response_time_anomaly(self, current_time: float, historical_times: List[float]) -> bool:
        """Detect response time anomaly."""
        if len(historical_times) < 10:
            return False
        
        mean_time = statistics.mean(historical_times)
        std_time = statistics.stdev(historical_times)
        
        if std_time == 0:
            return False
        
        z_score = abs(current_time - mean_time) / std_time
        return z_score > self.thresholds["response_time_zscore"]
    
    def detect_error_rate_anomaly(self, current_error_rate: float) -> bool:
        """Detect error rate anomaly."""
        return current_error_rate > self.thresholds["error_rate_threshold"]
    
    def detect_endpoint_anomaly(self, current_endpoint: str, endpoint_frequencies: Dict[str, int]) -> bool:
        """Detect endpoint access anomaly."""
        total_requests = sum(endpoint_frequencies.values())
        if total_requests == 0:
            return True
        
        endpoint_frequency = endpoint_frequencies.get(current_endpoint, 0) / total_requests
        return endpoint_frequency < (1.0 / len(endpoint_frequencies)) * self.thresholds["endpoint_deviation_threshold"]


# Global rate limiter instance
_intelligent_rate_limiter: Optional[IntelligentRateLimiter] = None


def get_intelligent_rate_limiter() -> IntelligentRateLimiter:
    """Get the global intelligent rate limiter instance."""
    global _intelligent_rate_limiter
    if _intelligent_rate_limiter is None:
        _intelligent_rate_limiter = IntelligentRateLimiter()
    return _intelligent_rate_limiter
