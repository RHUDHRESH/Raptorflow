"""
Dynamic Rate Limiter
====================

Advanced dynamic rate limiting with user tier integration, business rules,
and intelligent limit adjustments based on real-time conditions.

Features:
- User tier-based rate limiting
- Business rule engine
- Dynamic limit adjustments
- Context-aware rate limiting
- Time-based rule variations
- Custom limit policies
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


class UserTier(Enum):
    """User tiers for rate limiting."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"
    CUSTOM = "custom"


class RuleType(Enum):
    """Types of business rules."""
    TIER_BASED = "tier_based"
    TIME_BASED = "time_based"
    USAGE_BASED = "usage_based"
    FEATURE_BASED = "feature_based"
    BUSINESS_RULE = "business_rule"
    EMERGENCY_RULE = "emergency_rule"


class AdjustmentType(Enum):
    """Types of limit adjustments."""
    MULTIPLIER = "multiplier"
    ADDITIVE = "additive"
    PERCENTAGE = "percentage"
    ABSOLUTE = "absolute"


@dataclass
class TierLimits:
    """Rate limits for a user tier."""
    
    tier: UserTier
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int
    concurrent_connections: int
    
    # Advanced limits
    endpoint_limits: Dict[str, int] = field(default_factory=dict)
    feature_limits: Dict[str, int] = field(default_factory=dict)
    
    # Business rules
    auto_scaling_enabled: bool = False
    priority_support: bool = False
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class BusinessRule:
    """Business rule for rate limiting."""
    
    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    priority: int  # Higher priority rules override lower ones
    
    # Rule conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Rule actions
    adjustment_type: AdjustmentType
    adjustment_value: float
    
    # Time constraints
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    days_of_week: List[int] = field(default_factory=list)
    hours_of_day: List[int] = field(default_factory=list)
    
    # Rule state
    enabled: bool = True
    hit_count: int = 0
    last_hit: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DynamicLimitResult:
    """Result of dynamic rate limit calculation."""
    
    allowed: bool
    effective_limits: Dict[str, int]
    applied_rules: List[str]
    adjustment_factor: float
    reason: str
    
    # Context
    client_id: str
    user_tier: UserTier
    endpoint: str
    
    # Timestamps
    calculated_at: datetime = field(default_factory=datetime.now)
    reset_times: Dict[str, datetime] = field(default_factory=dict)
    
    # Additional info
    remaining_requests: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class DynamicConfig:
    """Configuration for dynamic rate limiter."""
    
    # Rule processing
    max_rules_per_request: int = 50
    rule_cache_ttl_seconds: int = 300
    enable_rule_caching: bool = True
    
    # Adjustments
    max_multiplier: float = 10.0
    min_multiplier: float = 0.1
    max_additive_increase: int = 10000
    max_additive_decrease: int = 5000
    
    # Performance
    enable_async_processing: bool = True
    batch_size: int = 100
    processing_timeout_seconds: int = 5
    
    # Business rules
    enable_time_based_rules: bool = True
    enable_usage_based_rules: bool = True
    enable_emergency_rules: bool = True
    
    # Monitoring
    enable_metrics: bool = True
    metrics_retention_days: int = 30


class DynamicRateLimiter:
    """Dynamic rate limiter with business rules engine."""
    
    def __init__(self, config: DynamicConfig = None):
        self.config = config or DynamicConfig()
        
        # Tier configurations
        self.tier_limits: Dict[UserTier, TierLimits] = {}
        self.custom_tier_limits: Dict[str, TierLimits] = {}
        
        # Business rules
        self.business_rules: Dict[str, BusinessRule] = {}
        self.rule_cache: Dict[str, Any] = {}
        
        # Dynamic state
        self.active_adjustments: Dict[str, Dict[str, Any]] = {}
        self.usage_tracking: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Statistics
        self.total_requests_processed = 0
        self.total_rules_applied = 0
        self.total_adjustments_made = 0
        
        # Background tasks
        self._running = False
        self._cleanup_task = None
        
        # Initialize default tier limits
        self._initialize_default_tiers()
        
        # Initialize default business rules
        self._initialize_default_rules()
        
        logger.info("Dynamic Rate Limiter initialized")
    
    def _initialize_default_tiers(self) -> None:
        """Initialize default tier limits."""
        default_tiers = {
            UserTier.FREE: TierLimits(
                tier=UserTier.FREE,
                requests_per_minute=60,
                requests_per_hour=1000,
                requests_per_day=10000,
                burst_limit=120,
                concurrent_connections=5,
                auto_scaling_enabled=False,
                priority_support=False
            ),
            UserTier.BASIC: TierLimits(
                tier=UserTier.BASIC,
                requests_per_minute=120,
                requests_per_hour=2500,
                requests_per_day=50000,
                burst_limit=240,
                concurrent_connections=10,
                auto_scaling_enabled=False,
                priority_support=False
            ),
            UserTier.PRO: TierLimits(
                tier=UserTier.PRO,
                requests_per_minute=300,
                requests_per_hour=10000,
                requests_per_day=500000,
                burst_limit=600,
                concurrent_connections=25,
                auto_scaling_enabled=True,
                priority_support=True
            ),
            UserTier.ENTERPRISE: TierLimits(
                tier=UserTier.ENTERPRISE,
                requests_per_minute=1000,
                requests_per_hour=50000,
                requests_per_day=5000000,
                burst_limit=2000,
                concurrent_connections=100,
                auto_scaling_enabled=True,
                priority_support=True
            ),
            UserTier.PREMIUM: TierLimits(
                tier=UserTier.PREMIUM,
                requests_per_minute=2000,
                requests_per_hour=100000,
                requests_per_day=10000000,
                burst_limit=4000,
                concurrent_connections=200,
                auto_scaling_enabled=True,
                priority_support=True
            )
        }
        
        for tier, limits in default_tiers.items():
            self.tier_limits[tier] = limits
    
    def _initialize_default_rules(self) -> None:
        """Initialize default business rules."""
        default_rules = [
            # Business hours boost
            BusinessRule(
                rule_id="business_hours_boost",
                name="Business Hours Boost",
                description="Increase limits during business hours for paid tiers",
                rule_type=RuleType.TIME_BASED,
                priority=10,
                conditions={"user_tier": ["pro", "enterprise", "premium"]},
                adjustment_type=AdjustmentType.MULTIPLIER,
                adjustment_value=1.5,
                hours_of_day=list(range(9, 18)),  # 9 AM to 6 PM
                days_of_week=[0, 1, 2, 3, 4]  # Monday to Friday
            ),
            
            # Weekend reduction for free tier
            BusinessRule(
                rule_id="weekend_free_reduction",
                name="Weekend Free Tier Reduction",
                description="Reduce limits for free tier on weekends",
                rule_type=RuleType.TIME_BASED,
                priority=20,
                conditions={"user_tier": ["free"]},
                adjustment_type=AdjustmentType.MULTIPLIER,
                adjustment_value=0.7,
                days_of_week=[5, 6]  # Saturday, Sunday
            ),
            
            # High usage penalty
            BusinessRule(
                rule_id="high_usage_penalty",
                name="High Usage Penalty",
                description="Reduce limits for high usage users",
                rule_type=RuleType.USAGE_BASED,
                priority=15,
                conditions={
                    "daily_usage_ratio": {"gt": 0.9},  # More than 90% of daily limit
                    "user_tier": ["free", "basic"]
                },
                adjustment_type=AdjustmentType.MULTIPLIER,
                adjustment_value=0.8
            ),
            
            # Emergency capacity rule
            BusinessRule(
                rule_id="emergency_capacity",
                name="Emergency Capacity",
                description="Emergency capacity reduction during high load",
                rule_type=RuleType.EMERGENCY_RULE,
                priority=100,  # Highest priority
                conditions={"system_load": {"gt": 0.9}},
                adjustment_type=AdjustmentType.MULTIPLIER,
                adjustment_value=0.5
            ),
            
            # VIP customer boost
            BusinessRule(
                rule_id="vip_boost",
                name="VIP Customer Boost",
                description="Boost limits for VIP customers",
                rule_type=RuleType.BUSINESS_RULE,
                priority=5,
                conditions={"is_vip": True},
                adjustment_type=AdjustmentType.MULTIPLIER,
                adjustment_value=2.0
            ),
            
            # Feature-based limits
            BusinessRule(
                rule_id="api_feature_limits",
                name="API Feature Limits",
                description="Apply limits based on API features used",
                rule_type=RuleType.FEATURE_BASED,
                priority=25,
                conditions={"feature": ["advanced_analytics", "ml_prediction"]},
                adjustment_type=AdjustmentType.ADDITIVE,
                adjustment_value=-100  # Reduce by 100 requests
            )
        ]
        
        for rule in default_rules:
            self.business_rules[rule.rule_id] = rule
    
    async def start(self) -> None:
        """Start the dynamic rate limiter."""
        if self._running:
            logger.warning("Dynamic Rate Limiter is already running")
            return
        
        self._running = True
        
        # Start background tasks
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Dynamic Rate Limiter started")
    
    async def stop(self) -> None:
        """Stop the dynamic rate limiter."""
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
        
        logger.info("Dynamic Rate Limiter stopped")
    
    async def check_rate_limit(
        self,
        client_id: str,
        user_tier: str,
        endpoint: str,
        context: Dict[str, Any] = None
    ) -> DynamicLimitResult:
        """Check rate limit with dynamic adjustments."""
        try:
            current_time = datetime.now()
            context = context or {}
            
            # Get base limits for tier
            tier_enum = UserTier(user_tier.lower())
            base_limits = self._get_tier_limits(tier_enum, client_id)
            
            # Apply business rules
            effective_limits, applied_rules = await self._apply_business_rules(
                client_id, tier_enum, endpoint, base_limits, context, current_time
            )
            
            # Check usage against limits
            allowed, remaining = await self._check_usage_against_limits(
                client_id, effective_limits, current_time
            )
            
            # Calculate reset times
            reset_times = self._calculate_reset_times(current_time)
            
            # Create result
            result = DynamicLimitResult(
                allowed=allowed,
                effective_limits=effective_limits,
                applied_rules=applied_rules,
                adjustment_factor=self._calculate_adjustment_factor(base_limits, effective_limits),
                reason=self._generate_reason(allowed, applied_rules),
                client_id=client_id,
                user_tier=tier_enum,
                endpoint=endpoint,
                reset_times=reset_times,
                remaining_requests=remaining,
                metadata={
                    "base_limits": asdict(base_limits),
                    "context": context
                }
            )
            
            # Update usage tracking
            await self._update_usage_tracking(client_id, endpoint, allowed, current_time)
            
            self.total_requests_processed += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Return conservative fallback
            return DynamicLimitResult(
                allowed=False,
                effective_limits={"requests_per_minute": 10},
                applied_rules=[],
                adjustment_factor=1.0,
                reason="Rate limit check failed",
                client_id=client_id,
                user_tier=UserTier.FREE,
                endpoint=endpoint
            )
    
    def _get_tier_limits(self, tier: UserTier, client_id: str) -> TierLimits:
        """Get tier limits for a client."""
        # Check for custom tier limits first
        if client_id in self.custom_tier_limits:
            return self.custom_tier_limits[client_id]
        
        # Return default tier limits
        return self.tier_limits.get(tier, self.tier_limits[UserTier.FREE])
    
    async def _apply_business_rules(
        self,
        client_id: str,
        user_tier: UserTier,
        endpoint: str,
        base_limits: TierLimits,
        context: Dict[str, Any],
        current_time: datetime
    ) -> Tuple[Dict[str, int], List[str]]:
        """Apply business rules to adjust limits."""
        effective_limits = {
            "requests_per_minute": base_limits.requests_per_minute,
            "requests_per_hour": base_limits.requests_per_hour,
            "requests_per_day": base_limits.requests_per_day,
            "burst_limit": base_limits.burst_limit,
            "concurrent_connections": base_limits.concurrent_connections
        }
        
        applied_rules = []
        
        # Sort rules by priority (higher priority first)
        sorted_rules = sorted(
            self.business_rules.values(),
            key=lambda x: x.priority,
            reverse=True
        )
        
        for rule in sorted_rules:
            if not rule.enabled:
                continue
            
            # Check if rule conditions are met
            if await self._evaluate_rule_conditions(rule, user_tier, endpoint, context, current_time):
                # Apply rule adjustment
                await self._apply_rule_adjustment(rule, effective_limits)
                applied_rules.append(rule.rule_id)
                
                # Update rule statistics
                rule.hit_count += 1
                rule.last_hit = current_time
                
                self.total_rules_applied += 1
        
        # Apply endpoint-specific limits
        if endpoint in base_limits.endpoint_limits:
            effective_limits["endpoint_limit"] = base_limits.endpoint_limits[endpoint]
        
        return effective_limits, applied_rules
    
    async def _evaluate_rule_conditions(
        self,
        rule: BusinessRule,
        user_tier: UserTier,
        endpoint: str,
        context: Dict[str, Any],
        current_time: datetime
    ) -> bool:
        """Evaluate if rule conditions are met."""
        try:
            # Check time constraints
            if rule.start_time and current_time < rule.start_time:
                return False
            if rule.end_time and current_time > rule.end_time:
                return False
            if rule.days_of_week and current_time.weekday() not in rule.days_of_week:
                return False
            if rule.hours_of_day and current_time.hour not in rule.hours_of_day:
                return False
            
            # Check rule conditions
            for condition_key, condition_value in rule.conditions.items():
                if condition_key == "user_tier":
                    if isinstance(condition_value, list):
                        if user_tier.value not in condition_value:
                            return False
                    elif user_tier.value != condition_value:
                        return False
                
                elif condition_key == "is_vip":
                    if context.get("is_vip", False) != condition_value:
                        return False
                
                elif condition_key == "feature":
                    if isinstance(condition_value, list):
                        client_features = context.get("features", [])
                        if not any(f in client_features for f in condition_value):
                            return False
                
                elif isinstance(condition_value, dict):
                    # Handle comparison operators
                    for op, value in condition_value.items():
                        actual_value = context.get(condition_key, 0)
                        
                        if op == "gt" and actual_value <= value:
                            return False
                        elif op == "lt" and actual_value >= value:
                            return False
                        elif op == "eq" and actual_value != value:
                            return False
                        elif op == "ne" and actual_value == value:
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rule condition evaluation failed: {e}")
            return False
    
    async def _apply_rule_adjustment(self, rule: BusinessRule, limits: Dict[str, int]) -> None:
        """Apply rule adjustment to limits."""
        try:
            for limit_key in limits:
                if rule.adjustment_type == AdjustmentType.MULTIPLIER:
                    limits[limit_key] = int(limits[limit_key] * rule.adjustment_value)
                elif rule.adjustment_type == AdjustmentType.ADDITIVE:
                    limits[limit_key] = int(limits[limit_key] + rule.adjustment_value)
                elif rule.adjustment_type == AdjustmentType.PERCENTAGE:
                    limits[limit_key] = int(limits[limit_key] * (1 + rule.adjustment_value / 100))
                elif rule.adjustment_type == AdjustmentType.ABSOLUTE:
                    limits[limit_key] = int(rule.adjustment_value)
                
                # Apply constraints
                limits[limit_key] = max(1, limits[limit_key])  # Minimum 1
                
                if rule.adjustment_type == AdjustmentType.MULTIPLIER:
                    limits[limit_key] = min(
                        limits[limit_key],
                        int(10000 * self.config.max_multiplier)  # Reasonable upper bound
                    )
            
            self.total_adjustments_made += 1
            
        except Exception as e:
            logger.error(f"Rule adjustment failed: {e}")
    
    async def _check_usage_against_limits(
        self,
        client_id: str,
        limits: Dict[str, int],
        current_time: datetime
    ) -> Tuple[bool, Dict[str, int]]:
        """Check current usage against limits."""
        usage = self.usage_tracking[client_id]
        remaining = {}
        
        # Check minute limit
        minute_key = current_time.strftime("%Y%m%d%H%M")
        minute_usage = usage.get("minute_usage", {}).get(minute_key, 0)
        remaining["requests_per_minute"] = max(0, limits["requests_per_minute"] - minute_usage)
        
        # Check hour limit
        hour_key = current_time.strftime("%Y%m%d%H")
        hour_usage = usage.get("hour_usage", {}).get(hour_key, 0)
        remaining["requests_per_hour"] = max(0, limits["requests_per_hour"] - hour_usage)
        
        # Check day limit
        day_key = current_time.strftime("%Y%m%d")
        day_usage = usage.get("day_usage", {}).get(day_key, 0)
        remaining["requests_per_day"] = max(0, limits["requests_per_day"] - day_usage)
        
        # Check concurrent connections
        concurrent_usage = usage.get("concurrent_connections", 0)
        remaining["concurrent_connections"] = max(0, limits["concurrent_connections"] - concurrent_usage)
        
        # Determine if allowed
        allowed = all(
            remaining[limit_key] > 0
            for limit_key in ["requests_per_minute", "requests_per_hour", "requests_per_day"]
        )
        
        return allowed, remaining
    
    def _calculate_reset_times(self, current_time: datetime) -> Dict[str, datetime]:
        """Calculate reset times for different limits."""
        return {
            "requests_per_minute": current_time.replace(second=0, microsecond=0) + timedelta(minutes=1),
            "requests_per_hour": current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1),
            "requests_per_day": current_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        }
    
    def _calculate_adjustment_factor(self, base_limits: TierLimits, effective_limits: Dict[str, int]) -> float:
        """Calculate overall adjustment factor."""
        if "requests_per_minute" in effective_limits:
            return effective_limits["requests_per_minute"] / base_limits.requests_per_minute
        return 1.0
    
    def _generate_reason(self, allowed: bool, applied_rules: List[str]) -> str:
        """Generate reason for rate limit decision."""
        if allowed:
            if applied_rules:
                return f"Request allowed with rules applied: {', '.join(applied_rules)}"
            else "Request allowed with base limits"
        else:
            if applied_rules:
                return f"Request blocked by rules: {', '.join(applied_rules)}"
            else "Request blocked by base limits"
    
    async def _update_usage_tracking(
        self,
        client_id: str,
        endpoint: str,
        allowed: bool,
        current_time: datetime
    ) -> None:
        """Update usage tracking for client."""
        if not allowed:
            return
        
        usage = self.usage_tracking[client_id]
        
        # Update minute usage
        minute_key = current_time.strftime("%Y%m%d%H%M")
        if "minute_usage" not in usage:
            usage["minute_usage"] = defaultdict(int)
        usage["minute_usage"][minute_key] += 1
        
        # Update hour usage
        hour_key = current_time.strftime("%Y%m%d%H")
        if "hour_usage" not in usage:
            usage["hour_usage"] = defaultdict(int)
        usage["hour_usage"][hour_key] += 1
        
        # Update day usage
        day_key = current_time.strftime("%Y%m%d")
        if "day_usage" not in usage:
            usage["day_usage"] = defaultdict(int)
        usage["day_usage"][day_key] += 1
        
        # Update endpoint usage
        if "endpoint_usage" not in usage:
            usage["endpoint_usage"] = defaultdict(int)
        usage["endpoint_usage"][endpoint] += 1
        
        # Update last activity
        usage["last_activity"] = current_time
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                
                current_time = datetime.now()
                
                # Clean old usage data
                cutoff_time = current_time - timedelta(days=2)
                
                for client_id, usage in list(self.usage_tracking.items()):
                    # Clean minute usage
                    if "minute_usage" in usage:
                        usage["minute_usage"] = defaultdict(int, {
                            k: v for k, v in usage["minute_usage"].items()
                            if datetime.strptime(k, "%Y%m%d%H%M") > cutoff_time
                        })
                    
                    # Clean hour usage
                    if "hour_usage" in usage:
                        usage["hour_usage"] = defaultdict(int, {
                            k: v for k, v in usage["hour_usage"].items()
                            if datetime.strptime(k, "%Y%m%d%H") > cutoff_time
                        })
                    
                    # Clean day usage
                    if "day_usage" in usage:
                        usage["day_usage"] = defaultdict(int, {
                            k: v for k, v in usage["day_usage"].items()
                            if datetime.strptime(k, "%Y%m%d") > cutoff_time
                        })
                    
                    # Remove inactive clients
                    if usage.get("last_activity") and usage["last_activity"] < cutoff_time:
                        del self.usage_tracking[client_id]
                
                # Clean rule cache
                if self.config.enable_rule_caching:
                    cache_cutoff = current_time - timedelta(seconds=self.config.rule_cache_ttl_seconds)
                    self.rule_cache = {
                        k: v for k, v in self.rule_cache.items()
                        if v.get("cached_at", datetime.min) > cache_cutoff
                    }
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    def add_business_rule(self, rule: BusinessRule) -> None:
        """Add a new business rule."""
        self.business_rules[rule.rule_id] = rule
        logger.info(f"Business rule added: {rule.rule_id}")
    
    def update_business_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing business rule."""
        if rule_id not in self.business_rules:
            return False
        
        rule = self.business_rules[rule_id]
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        rule.updated_at = datetime.now()
        logger.info(f"Business rule updated: {rule_id}")
        return True
    
    def delete_business_rule(self, rule_id: str) -> bool:
        """Delete a business rule."""
        if rule_id not in self.business_rules:
            return False
        
        del self.business_rules[rule_id]
        logger.info(f"Business rule deleted: {rule_id}")
        return True
    
    def add_custom_tier_limits(self, client_id: str, limits: TierLimits) -> None:
        """Add custom tier limits for a client."""
        self.custom_tier_limits[client_id] = limits
        logger.info(f"Custom tier limits added for client: {client_id}")
    
    def remove_custom_tier_limits(self, client_id: str) -> bool:
        """Remove custom tier limits for a client."""
        if client_id in self.custom_tier_limits:
            del self.custom_tier_limits[client_id]
            logger.info(f"Custom tier limits removed for client: {client_id}")
            return True
        return False
    
    def get_client_usage(self, client_id: str) -> Dict[str, Any]:
        """Get usage statistics for a client."""
        usage = self.usage_tracking.get(client_id, {})
        
        # Calculate current usage
        current_time = datetime.now()
        minute_key = current_time.strftime("%Y%m%d%H%M")
        hour_key = current_time.strftime("%Y%m%d%H")
        day_key = current_time.strftime("%Y%m%d")
        
        return {
            "client_id": client_id,
            "current_minute_usage": usage.get("minute_usage", {}).get(minute_key, 0),
            "current_hour_usage": usage.get("hour_usage", {}).get(hour_key, 0),
            "current_day_usage": usage.get("day_usage", {}).get(day_key, 0),
            "concurrent_connections": usage.get("concurrent_connections", 0),
            "last_activity": usage.get("last_activity"),
            "endpoint_usage": dict(usage.get("endpoint_usage", {}))
        }
    
    def get_dynamic_limiter_stats(self) -> Dict[str, Any]:
        """Get comprehensive dynamic limiter statistics."""
        current_time = datetime.now()
        
        # Rule statistics
        rule_stats = {
            "total_rules": len(self.business_rules),
            "enabled_rules": len([r for r in self.business_rules.values() if r.enabled]),
            "rules_by_type": defaultdict(int),
            "top_hit_rules": []
        }
        
        for rule in self.business_rules.values():
            rule_stats["rules_by_type"][rule.rule_type.value] += 1
        
        # Top hit rules
        top_rules = sorted(
            self.business_rules.values(),
            key=lambda x: x.hit_count,
            reverse=True
        )[:10]
        
        rule_stats["top_hit_rules"] = [
            {"rule_id": r.rule_id, "name": r.name, "hit_count": r.hit_count}
            for r in top_rules
        ]
        
        # Tier statistics
        tier_stats = {
            "default_tiers": len(self.tier_limits),
            "custom_tiers": len(self.custom_tier_limits),
            "tier_distribution": defaultdict(int)
        }
        
        # Usage statistics
        usage_stats = {
            "active_clients": len(self.usage_tracking),
            "total_daily_requests": sum(
                usage.get("day_usage", {}).get(current_time.strftime("%Y%m%d"), 0)
                for usage in self.usage_tracking.values()
            )
        }
        
        return {
            "total_requests_processed": self.total_requests_processed,
            "total_rules_applied": self.total_rules_applied,
            "total_adjustments_made": self.total_adjustments_made,
            "rule_statistics": rule_stats,
            "tier_statistics": tier_stats,
            "usage_statistics": usage_stats,
            "config": {
                "max_rules_per_request": self.config.max_rules_per_request,
                "enable_rule_caching": self.config.enable_rule_caching,
                "enable_time_based_rules": self.config.enable_time_based_rules,
                "enable_usage_based_rules": self.config.enable_usage_based_rules
            },
            "running": self._running,
            "timestamp": current_time.isoformat()
        }


# Global dynamic rate limiter instance
_dynamic_rate_limiter: Optional[DynamicRateLimiter] = None


def get_dynamic_rate_limiter(config: DynamicConfig = None) -> DynamicRateLimiter:
    """Get or create global dynamic rate limiter instance."""
    global _dynamic_rate_limiter
    if _dynamic_rate_limiter is None:
        _dynamic_rate_limiter = DynamicRateLimiter(config)
    return _dynamic_rate_limiter


async def start_dynamic_rate_limiter(config: DynamicConfig = None):
    """Start the global dynamic rate limiter."""
    limiter = get_dynamic_rate_limiter(config)
    await limiter.start()


async def stop_dynamic_rate_limiter():
    """Stop the global dynamic rate limiter."""
    global _dynamic_rate_limiter
    if _dynamic_rate_limiter:
        await _dynamic_rate_limiter.stop()


async def check_dynamic_rate_limit(
    client_id: str,
    user_tier: str,
    endpoint: str,
    context: Dict[str, Any] = None
) -> DynamicLimitResult:
    """Check dynamic rate limit."""
    limiter = get_dynamic_rate_limiter()
    return await limiter.check_rate_limit(client_id, user_tier, endpoint, context)


def get_dynamic_limiter_stats() -> Dict[str, Any]:
    """Get dynamic limiter statistics."""
    limiter = get_dynamic_rate_limiter()
    return limiter.get_dynamic_limiter_stats()
