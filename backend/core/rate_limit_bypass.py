"""
Rate Limit Bypass Manager
=========================

Advanced rate limit bypass system with premium user handling, emergency scenarios,
and intelligent bypass authorization.

Features:
- Premium user bypass management
- Emergency scenario handling
- Bypass authorization and auditing
- Temporary bypass grants
- Bypass usage tracking
- Security and compliance controls
"""

import asyncio
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


class BypassType(Enum):
    """Types of rate limit bypasses."""
    PREMIUM_USER = "premium_user"
    EMERGENCY = "emergency"
    MAINTENANCE = "maintenance"
    ADMIN_OVERRIDE = "admin_override"
    API_KEY = "api_key"
    WHITELIST = "whitelist"
    TEMPORARY = "temporary"


class BypassStatus(Enum):
    """Bypass status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    PENDING = "pending"


class EmergencyLevel(Enum):
    """Emergency scenario levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BypassReason(Enum):
    """Reasons for bypass approval."""
    SYSTEM_MAINTENANCE = "system_maintenance"
    BUSINESS_CRITICAL = "business_critical"
    SECURITY incident = "security_incident"
    PERFORMANCE_ISSUE = "performance_issue"
    CUSTOMER_EMERGENCY = "customer_emergency"
    TESTING = "testing"
    COMPLIANCE = "compliance"


@dataclass
class BypassRule:
    """Rate limit bypass rule."""
    
    rule_id: str
    name: str
    description: str
    bypass_type: BypassType
    priority: int  # Higher priority rules take precedence
    
    # Scope
    client_ids: List[str] = field(default_factory=list)
    user_tiers: List[str] = field(default_factory=list)
    endpoints: List[str] = field(default_factory=list)
    ip_addresses: List[str] = field(default_factory=list)
    
    # Conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Bypass settings
    bypass_percentage: float = 100.0  # 100% = full bypass
    max_requests_per_hour: Optional[int] = None
    allowed_endpoints: List[str] = field(default_factory=list)
    
    # Time constraints
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    
    # Authorization
    required_approval: bool = False
    approved_by: Optional[str] = None
    approval_reason: Optional[str] = None
    
    # State
    enabled: bool = True
    status: BypassStatus = BypassStatus.ACTIVE
    usage_count: int = 0
    last_used: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class BypassRequest:
    """Bypass request for approval."""
    
    request_id: str
    client_id: str
    endpoint: str
    bypass_type: BypassType
    reason: BypassReason
    description: str
    
    # Request details
    requested_duration_minutes: int
    max_requests_needed: Optional[int] = None
    
    # Requester information
    requested_by: str
    requester_role: str = ""
    
    # Approval workflow
    status: BypassStatus = BypassStatus.PENDING
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    approval_comments: str = ""
    
    # Timestamps
    requested_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class BypassUsage:
    """Bypass usage tracking."""
    
    usage_id: str
    rule_id: str
    client_id: str
    endpoint: str
    
    # Usage details
    timestamp: datetime
    request_allowed: bool
    original_limit: int
    bypassed_limit: int
    bypass_reason: str
    
    # Context
    user_tier: str
    ip_address: str
    user_agent: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class BypassConfig:
    """Configuration for bypass manager."""
    
    # Authorization
    require_approval_for_emergency: bool = True
    require_approval_for_premium: bool = False
    auto_approve_critical_emergency: bool = True
    
    # Limits
    max_bypass_duration_minutes: int = 1440  # 24 hours
    max_concurrent_bypasses: int = 100
    max_premium_bypass_percentage: float = 200.0  # 2x normal limits
    
    # Emergency settings
    emergency_auto_bypass: bool = True
    emergency_bypass_duration_minutes: int = 60
    critical_emergency_bypass_duration_minutes: int = 180
    
    # Security
    enable_audit_logging: bool = True
    enable_usage_tracking: bool = True
    enable_anomaly_detection: bool = True
    
    # Performance
    bypass_cache_ttl_seconds: int = 300
    enable_bypass_caching: bool = True
    
    # Retention
    usage_retention_days: int = 30
    request_retention_days: int = 90


class RateLimitBypassManager:
    """Advanced rate limit bypass manager."""
    
    def __init__(self, config: BypassConfig = None):
        self.config = config or BypassConfig()
        
        # Bypass rules and requests
        self.bypass_rules: Dict[str, BypassRule] = {}
        self.bypass_requests: Dict[str, BypassRequest] = {}
        self.active_bypasses: Dict[str, BypassRule] = {}
        
        # Usage tracking
        self.bypass_usage: deque = deque(maxlen=10000)
        self.usage_statistics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Emergency state
        self.emergency_active: bool = False
        self.emergency_level: EmergencyLevel = EmergencyLevel.LOW
        self.emergency_start_time: Optional[datetime] = None
        self.emergency_rules: List[str] = []
        
        # Authorization
        self.approval_queue: deque = deque(maxlen=1000)
        self.approval_history: deque = deque(maxlen=5000)
        
        # Caching
        self.bypass_cache: Dict[str, Any] = {}
        
        # Statistics
        self.total_bypasses_granted = 0
        self.total_bypass_requests = 0
        self.total_emergency_activations = 0
        
        # Background tasks
        self._running = False
        self._cleanup_task = None
        self._emergency_monitor_task = None
        
        # Initialize default bypass rules
        self._initialize_default_rules()
        
        logger.info("Rate Limit Bypass Manager initialized")
    
    def _initialize_default_rules(self) -> None:
        """Initialize default bypass rules."""
        default_rules = [
            # Premium user bypass
            BypassRule(
                rule_id="premium_user_bypass",
                name="Premium User Bypass",
                description="Automatic bypass for premium users",
                bypass_type=BypassType.PREMIUM_USER,
                priority=10,
                user_tiers=["premium", "enterprise"],
                bypass_percentage=self.config.max_premium_bypass_percentage,
                required_approval=False,
                created_by="system"
            ),
            
            # Emergency bypass
            BypassRule(
                rule_id="emergency_bypass",
                name="Emergency Bypass",
                description="Emergency scenario bypass",
                bypass_type=BypassType.EMERGENCY,
                priority=100,
                bypass_percentage=1000.0,  # 10x normal limits
                required_approval=self.config.require_approval_for_emergency,
                created_by="system"
            ),
            
            # Admin override
            BypassRule(
                rule_id="admin_override",
                name="Admin Override",
                description="Administrator override capability",
                bypass_type=BypassType.ADMIN_OVERRIDE,
                priority=90,
                bypass_percentage=500.0,  # 5x normal limits
                required_approval=False,
                created_by="system"
            ),
            
            # Maintenance bypass
            BypassRule(
                rule_id="maintenance_bypass",
                name="Maintenance Bypass",
                description="System maintenance bypass",
                bypass_type=BypassType.MAINTENANCE,
                priority=50,
                bypass_percentage=200.0,  # 2x normal limits
                required_approval=True,
                created_by="system"
            )
        ]
        
        for rule in default_rules:
            self.bypass_rules[rule.rule_id] = rule
    
    async def start(self) -> None:
        """Start the bypass manager."""
        if self._running:
            logger.warning("Rate Limit Bypass Manager is already running")
            return
        
        self._running = True
        
        # Start background tasks
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self._emergency_monitor_task = asyncio.create_task(self._emergency_monitor_loop())
        
        logger.info("Rate Limit Bypass Manager started")
    
    async def stop(self) -> None:
        """Stop the bypass manager."""
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
        
        if self._emergency_monitor_task:
            self._emergency_monitor_task.cancel()
            try:
                await self._emergency_monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Rate Limit Bypass Manager stopped")
    
    async def check_bypass(
        self,
        client_id: str,
        endpoint: str,
        user_tier: str,
        ip_address: str,
        context: Dict[str, Any] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if request should bypass rate limits."""
        try:
            current_time = datetime.now()
            context = context or {}
            
            # Check cache first
            cache_key = f"bypass_{client_id}_{endpoint}"
            if self.config.enable_bypass_caching and cache_key in self.bypass_cache:
                cached_result = self.bypass_cache[cache_key]
                if cached_result["expires_at"] > current_time:
                    return cached_result["allowed"], cached_result["details"]
            
            # Find applicable bypass rules
            applicable_rules = await self._find_applicable_rules(
                client_id, endpoint, user_tier, ip_address, current_time
            )
            
            if not applicable_rules:
                return False, {"reason": "No applicable bypass rules"}
            
            # Apply highest priority rule
            bypass_rule = max(applicable_rules, key=lambda x: x.priority)
            
            # Check if bypass is allowed
            allowed, details = await self._apply_bypass_rule(
                bypass_rule, client_id, endpoint, user_tier, context, current_time
            )
            
            # Track usage
            if self.config.enable_usage_tracking:
                await self._track_bypass_usage(
                    bypass_rule, client_id, endpoint, user_tier, ip_address, allowed, details
                )
            
            # Cache result
            if self.config.enable_bypass_caching:
                self.bypass_cache[cache_key] = {
                    "allowed": allowed,
                    "details": details,
                    "expires_at": current_time + timedelta(seconds=self.config.bypass_cache_ttl_seconds)
                }
            
            return allowed, details
            
        except Exception as e:
            logger.error(f"Bypass check failed: {e}")
            return False, {"reason": "Bypass check failed", "error": str(e)}
    
    async def _find_applicable_rules(
        self,
        client_id: str,
        endpoint: str,
        user_tier: str,
        ip_address: str,
        current_time: datetime
    ) -> List[BypassRule]:
        """Find applicable bypass rules."""
        applicable_rules = []
        
        for rule in self.bypass_rules.values():
            if not rule.enabled or rule.status != BypassStatus.ACTIVE:
                continue
            
            # Check time constraints
            if rule.start_time and current_time < rule.start_time:
                continue
            if rule.end_time and current_time > rule.end_time:
                continue
            if rule.duration_minutes:
                rule_start = rule.created_at + timedelta(minutes=rule.duration_minutes)
                if current_time > rule_start:
                    continue
            
            # Check scope
            if rule.client_ids and client_id not in rule.client_ids:
                continue
            if rule.user_tiers and user_tier not in rule.user_tiers:
                continue
            if rule.endpoints and endpoint not in rule.endpoints:
                continue
            if rule.ip_addresses and ip_address not in rule.ip_addresses:
                continue
            
            # Check conditions
            if not await self._evaluate_rule_conditions(rule, client_id, endpoint, user_tier):
                continue
            
            applicable_rules.append(rule)
        
        return applicable_rules
    
    async def _evaluate_rule_conditions(
        self,
        rule: BypassRule,
        client_id: str,
        endpoint: str,
        user_tier: str
    ) -> bool:
        """Evaluate bypass rule conditions."""
        try:
            for condition_key, condition_value in rule.conditions.items():
                if condition_key == "emergency_active":
                    if self.emergency_active != condition_value:
                        return False
                
                elif condition_key == "emergency_level":
                    if self.emergency_level.value != condition_value:
                        return False
                
                elif condition_key == "usage_threshold":
                    # Check if client has exceeded usage threshold
                    client_usage = self.usage_statistics.get(client_id, {})
                    current_usage = client_usage.get("requests_today", 0)
                    if current_usage < condition_value:
                        return False
                
                elif condition_key == "specific_endpoints":
                    if endpoint not in condition_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rule condition evaluation failed: {e}")
            return False
    
    async def _apply_bypass_rule(
        self,
        rule: BypassRule,
        client_id: str,
        endpoint: str,
        user_tier: str,
        context: Dict[str, Any],
        current_time: datetime
    ) -> Tuple[bool, Dict[str, Any]]:
        """Apply bypass rule and determine if request is allowed."""
        try:
            # Update rule usage
            rule.usage_count += 1
            rule.last_used = current_time
            
            # Check if endpoint is allowed
            if rule.allowed_endpoints and endpoint not in rule.allowed_endpoints:
                return False, {
                    "reason": "Endpoint not in allowed list",
                    "rule_id": rule.rule_id,
                    "allowed_endpoints": rule.allowed_endpoints
                }
            
            # Check request limits
            if rule.max_requests_per_hour:
                client_usage = self.usage_statistics[client_id]
                hourly_usage = client_usage.get("requests_this_hour", 0)
                if hourly_usage >= rule.max_requests_per_hour:
                    return False, {
                        "reason": "Hourly bypass limit exceeded",
                        "rule_id": rule.rule_id,
                        "hourly_usage": hourly_usage,
                        "max_requests_per_hour": rule.max_requests_per_hour
                    }
            
            # Allow bypass
            details = {
                "bypassed": True,
                "rule_id": rule.rule_id,
                "rule_name": rule.name,
                "bypass_type": rule.bypass_type.value,
                "bypass_percentage": rule.bypass_percentage,
                "reason": f"Bypass granted via {rule.name}"
            }
            
            return True, details
            
        except Exception as e:
            logger.error(f"Bypass rule application failed: {e}")
            return False, {"reason": "Bypass rule application failed", "error": str(e)}
    
    async def _track_bypass_usage(
        self,
        rule: BypassRule,
        client_id: str,
        endpoint: str,
        user_tier: str,
        ip_address: str,
        allowed: bool,
        details: Dict[str, Any]
    ) -> None:
        """Track bypass usage for analytics."""
        try:
            usage = BypassUsage(
                usage_id=f"usage_{int(time.time())}_{hashlib.md5(f'{client_id}{endpoint}'.encode()).hexdigest()[:8]}",
                rule_id=rule.rule_id,
                client_id=client_id,
                endpoint=endpoint,
                timestamp=datetime.now(),
                request_allowed=allowed,
                original_limit=details.get("original_limit", 0),
                bypassed_limit=details.get("bypassed_limit", 0),
                bypass_reason=details.get("reason", ""),
                user_tier=user_tier,
                ip_address=ip_address,
                user_agent=details.get("user_agent", "")
            )
            
            self.bypass_usage.append(usage)
            
            # Update usage statistics
            if client_id not in self.usage_statistics:
                self.usage_statistics[client_id] = {
                    "total_bypasses": 0,
                    "requests_today": 0,
                    "requests_this_hour": 0,
                    "last_bypass": None
                }
            
            stats = self.usage_statistics[client_id]
            stats["total_bypasses"] += 1
            stats["last_bypass"] = usage.timestamp
            
            # Update hourly and daily counters
            current_time = usage.timestamp
            hour_key = current_time.strftime("%Y%m%d%H")
            day_key = current_time.strftime("%Y%m%d")
            
            if "hourly_usage" not in stats:
                stats["hourly_usage"] = defaultdict(int)
            if "daily_usage" not in stats:
                stats["daily_usage"] = defaultdict(int)
            
            stats["hourly_usage"][hour_key] += 1
            stats["daily_usage"][day_key] += 1
            stats["requests_this_hour"] = stats["hourly_usage"][hour_key]
            stats["requests_today"] = stats["daily_usage"][day_key]
            
        except Exception as e:
            logger.error(f"Bypass usage tracking failed: {e}")
    
    async def request_bypass(
        self,
        client_id: str,
        endpoint: str,
        bypass_type: BypassType,
        reason: BypassReason,
        description: str,
        requested_duration_minutes: int,
        requested_by: str,
        requester_role: str = "",
        max_requests_needed: Optional[int] = None
    ) -> BypassRequest:
        """Request a bypass for approval."""
        try:
            request_id = f"req_{int(time.time())}_{hashlib.md5(f'{client_id}{endpoint}'.encode()).hexdigest()[:8]}"
            
            request = BypassRequest(
                request_id=request_id,
                client_id=client_id,
                endpoint=endpoint,
                bypass_type=bypass_type,
                reason=reason,
                description=description,
                requested_duration_minutes=requested_duration_minutes,
                max_requests_needed=max_requests_needed,
                requested_by=requested_by,
                requester_role=requester_role,
                expires_at=datetime.now() + timedelta(minutes=requested_duration_minutes)
            )
            
            # Check if auto-approval is possible
            if await self._should_auto_approve(request):
                request.status = BypassStatus.ACTIVE
                request.reviewed_by = "system"
                request.reviewed_at = datetime.now()
                request.approval_comments = "Auto-approved"
                
                # Create bypass rule
                await self._create_bypass_from_request(request)
            else:
                # Add to approval queue
                self.approval_queue.append(request)
            
            self.bypass_requests[request_id] = request
            self.total_bypass_requests += 1
            
            logger.info(f"Bypass request created: {request_id}")
            return request
            
        except Exception as e:
            logger.error(f"Bypass request creation failed: {e}")
            raise
    
    async def _should_auto_approve(self, request: BypassRequest) -> bool:
        """Determine if bypass request should be auto-approved."""
        try:
            # Auto-approve critical emergencies
            if (request.bypass_type == BypassType.EMERGENCY and 
                request.reason == BypassReason.BUSINESS_CRITICAL and
                self.config.auto_approve_critical_emergency):
                return True
            
            # Auto-approve premium users if no approval required
            if (request.bypass_type == BypassType.PREMIUM_USER and 
                not self.config.require_approval_for_premium):
                return True
            
            # Auto-approve admin requests
            if request.bypass_type == BypassType.ADMIN_OVERRIDE:
                return True
            
            # Auto-approve short duration testing bypasses
            if (request.reason == BypassReason.TESTING and 
                request.requested_duration_minutes <= 30):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Auto-approval check failed: {e}")
            return False
    
    async def _create_bypass_from_request(self, request: BypassRequest) -> BypassRule:
        """Create bypass rule from approved request."""
        rule_id = f"auto_{request.request_id}"
        
        rule = BypassRule(
            rule_id=rule_id,
            name=f"Auto-bypass for {request.client_id}",
            description=request.description,
            bypass_type=request.bypass_type,
            priority=50,
            client_ids=[request.client_id],
            endpoints=[request.endpoint],
            bypass_percentage=100.0,
            max_requests_per_hour=request.max_requests_needed,
            duration_minutes=request.requested_duration_minutes,
            required_approval=False,
            approved_by=request.reviewed_by,
            approval_reason=request.approval_comments,
            created_by=request.requested_by,
            start_time=datetime.now(),
            end_time=request.expires_at
        )
        
        self.bypass_rules[rule_id] = rule
        self.active_bypasses[rule_id] = rule
        self.total_bypasses_granted += 1
        
        return rule
    
    async def approve_bypass_request(
        self,
        request_id: str,
        approved_by: str,
        approval_comments: str = ""
    ) -> bool:
        """Approve a bypass request."""
        try:
            if request_id not in self.bypass_requests:
                return False
            
            request = self.bypass_requests[request_id]
            
            if request.status != BypassStatus.PENDING:
                return False
            
            request.status = BypassStatus.ACTIVE
            request.reviewed_by = approved_by
            request.reviewed_at = datetime.now()
            request.approval_comments = approval_comments
            
            # Create bypass rule
            await self._create_bypass_from_request(request)
            
            # Record approval
            self.approval_history.append({
                "request_id": request_id,
                "action": "approved",
                "approved_by": approved_by,
                "approved_at": datetime.now(),
                "comments": approval_comments
            })
            
            logger.info(f"Bypass request approved: {request_id} by {approved_by}")
            return True
            
        except Exception as e:
            logger.error(f"Bypass request approval failed: {e}")
            return False
    
    async def deny_bypass_request(
        self,
        request_id: str,
        denied_by: str,
        denial_reason: str = ""
    ) -> bool:
        """Deny a bypass request."""
        try:
            if request_id not in self.bypass_requests:
                return False
            
            request = self.bypass_requests[request_id]
            
            if request.status != BypassStatus.PENDING:
                return False
            
            request.status = BypassStatus.REVOKED
            request.reviewed_by = denied_by
            request.reviewed_at = datetime.now()
            request.approval_comments = denial_reason
            
            # Record denial
            self.approval_history.append({
                "request_id": request_id,
                "action": "denied",
                "denied_by": denied_by,
                "denied_at": datetime.now(),
                "reason": denial_reason
            })
            
            logger.info(f"Bypass request denied: {request_id} by {denied_by}")
            return True
            
        except Exception as e:
            logger.error(f"Bypass request denial failed: {e}")
            return False
    
    async def activate_emergency_mode(
        self,
        level: EmergencyLevel,
        reason: str,
        activated_by: str,
        duration_minutes: Optional[int] = None
    ) -> bool:
        """Activate emergency bypass mode."""
        try:
            self.emergency_active = True
            self.emergency_level = level
            self.emergency_start_time = datetime.now()
            
            # Set duration
            if duration_minutes is None:
                if level == EmergencyLevel.CRITICAL:
                    duration_minutes = self.config.critical_emergency_bypass_duration_minutes
                elif level == EmergencyLevel.HIGH:
                    duration_minutes = self.config.emergency_bypass_duration_minutes
                else:
                    duration_minutes = 30
            
            # Activate emergency bypass rule
            emergency_rule = self.bypass_rules["emergency_bypass"]
            emergency_rule.enabled = True
            emergency_rule.start_time = datetime.now()
            emergency_rule.duration_minutes = duration_minutes
            emergency_rule.conditions["emergency_active"] = True
            emergency_rule.conditions["emergency_level"] = level.value
            
            self.active_bypasses["emergency_bypass"] = emergency_rule
            self.emergency_rules.append("emergency_bypass")
            
            self.total_emergency_activations += 1
            
            logger.warning(f"Emergency mode activated: {level.value} by {activated_by} - {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Emergency mode activation failed: {e}")
            return False
    
    async def deactivate_emergency_mode(self, deactivated_by: str) -> bool:
        """Deactivate emergency bypass mode."""
        try:
            self.emergency_active = False
            self.emergency_level = EmergencyLevel.LOW
            self.emergency_start_time = None
            
            # Deactivate emergency bypass rule
            emergency_rule = self.bypass_rules["emergency_bypass"]
            emergency_rule.enabled = False
            emergency_rule.conditions = {}
            
            # Remove from active bypasses
            if "emergency_bypass" in self.active_bypasses:
                del self.active_bypasses["emergency_bypass"]
            
            self.emergency_rules.clear()
            
            logger.info(f"Emergency mode deactivated by {deactivated_by}")
            return True
            
        except Exception as e:
            logger.error(f"Emergency mode deactivation failed: {e}")
            return False
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self._running:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
                current_time = datetime.now()
                
                # Clean expired bypass rules
                expired_rules = []
                for rule_id, rule in self.bypass_rules.items():
                    if rule.end_time and current_time > rule.end_time:
                        rule.status = BypassStatus.EXPIRED
                        rule.enabled = False
                        expired_rules.append(rule_id)
                
                # Remove from active bypasses
                for rule_id in expired_rules:
                    if rule_id in self.active_bypasses:
                        del self.active_bypasses[rule_id]
                
                # Clean expired requests
                expired_requests = []
                for request_id, request in self.bypass_requests.items():
                    if request.expires_at and current_time > request.expires_at:
                        if request.status == BypassStatus.ACTIVE:
                            request.status = BypassStatus.EXPIRED
                        expired_requests.append(request_id)
                
                # Clean old usage data
                usage_cutoff = current_time - timedelta(days=self.config.usage_retention_days)
                self.bypass_usage = deque(
                    [usage for usage in self.bypass_usage if usage.timestamp > usage_cutoff],
                    maxlen=10000
                )
                
                # Clean old approval history
                approval_cutoff = current_time - timedelta(days=self.config.request_retention_days)
                self.approval_history = deque(
                    [approval for approval in self.approval_history if approval.get("approved_at", approval.get("denied_at")) > approval_cutoff],
                    maxlen=5000
                )
                
                # Clean bypass cache
                cache_cutoff = current_time - timedelta(seconds=self.config.bypass_cache_ttl_seconds)
                self.bypass_cache = {
                    k: v for k, v in self.bypass_cache.items()
                    if v.get("expires_at", datetime.min) > cache_cutoff
                }
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    async def _emergency_monitor_loop(self) -> None:
        """Background emergency monitoring loop."""
        while self._running:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                if self.emergency_active and self.emergency_start_time:
                    # Auto-deactivate emergency after duration
                    emergency_rule = self.bypass_rules.get("emergency_bypass")
                    if emergency_rule and emergency_rule.duration_minutes:
                        expiry_time = self.emergency_start_time + timedelta(minutes=emergency_rule.duration_minutes)
                        if datetime.now() > expiry_time:
                            await self.deactivate_emergency_mode("system")
                            logger.info("Emergency mode auto-deactivated after duration expired")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Emergency monitor loop error: {e}")
    
    def get_bypass_stats(self) -> Dict[str, Any]:
        """Get comprehensive bypass statistics."""
        current_time = datetime.now()
        
        # Bypass rule statistics
        rule_stats = {
            "total_rules": len(self.bypass_rules),
            "active_rules": len([r for r in self.bypass_rules.values() if r.enabled and r.status == BypassStatus.ACTIVE]),
            "rules_by_type": defaultdict(int),
            "total_usage": sum(r.usage_count for r in self.bypass_rules.values())
        }
        
        for rule in self.bypass_rules.values():
            rule_stats["rules_by_type"][rule.bypass_type.value] += 1
        
        # Request statistics
        request_stats = {
            "total_requests": self.total_bypass_requests,
            "pending_requests": len([r for r in self.bypass_requests.values() if r.status == BypassStatus.PENDING]),
            "approved_requests": len([r for r in self.bypass_requests.values() if r.status == BypassStatus.ACTIVE]),
            "denied_requests": len([r for r in self.bypass_requests.values() if r.status == BypassStatus.REVOKED]),
            "requests_by_type": defaultdict(int),
            "requests_by_reason": defaultdict(int)
        }
        
        for request in self.bypass_requests.values():
            request_stats["requests_by_type"][request.bypass_type.value] += 1
            request_stats["requests_by_reason"][request.reason.value] += 1
        
        # Usage statistics
        usage_stats = {
            "total_usage_events": len(self.bypass_usage),
            "unique_clients": len(set(usage.client_id for usage in self.bypass_usage)),
            "usage_by_type": defaultdict(int),
            "recent_usage_24h": len([
                usage for usage in self.bypass_usage
                if usage.timestamp > current_time - timedelta(hours=24)
            ])
        }
        
        for usage in self.bypass_usage:
            rule = self.bypass_rules.get(usage.rule_id)
            if rule:
                usage_stats["usage_by_type"][rule.bypass_type.value] += 1
        
        # Emergency statistics
        emergency_stats = {
            "emergency_active": self.emergency_active,
            "emergency_level": self.emergency_level.value,
            "emergency_start_time": self.emergency_start_time.isoformat() if self.emergency_start_time else None,
            "total_activations": self.total_emergency_activations,
            "active_emergency_rules": len(self.emergency_rules)
        }
        
        return {
            "total_bypasses_granted": self.total_bypasses_granted,
            "rule_statistics": rule_stats,
            "request_statistics": request_stats,
            "usage_statistics": usage_stats,
            "emergency_statistics": emergency_stats,
            "approval_queue_size": len(self.approval_queue),
            "cache_size": len(self.bypass_cache),
            "config": {
                "require_approval_for_emergency": self.config.require_approval_for_emergency,
                "max_bypass_duration_minutes": self.config.max_bypass_duration_minutes,
                "enable_audit_logging": self.config.enable_audit_logging,
                "enable_usage_tracking": self.config.enable_usage_tracking
            },
            "running": self._running,
            "timestamp": current_time.isoformat()
        }
    
    def get_pending_requests(self) -> List[BypassRequest]:
        """Get pending bypass requests."""
        return [
            request for request in self.bypass_requests.values()
            if request.status == BypassStatus.PENDING
        ]
    
    def get_active_bypasses(self) -> List[BypassRule]:
        """Get currently active bypass rules."""
        return list(self.active_bypasses.values())


# Global bypass manager instance
_rate_limit_bypass_manager: Optional[RateLimitBypassManager] = None


def get_rate_limit_bypass_manager(config: BypassConfig = None) -> RateLimitBypassManager:
    """Get or create global rate limit bypass manager instance."""
    global _rate_limit_bypass_manager
    if _rate_limit_bypass_manager is None:
        _rate_limit_bypass_manager = RateLimitBypassManager(config)
    return _rate_limit_bypass_manager


async def start_rate_limit_bypass(config: BypassConfig = None):
    """Start the global rate limit bypass manager."""
    bypass = get_rate_limit_bypass_manager(config)
    await bypass.start()


async def stop_rate_limit_bypass():
    """Stop the global rate limit bypass manager."""
    global _rate_limit_bypass_manager
    if _rate_limit_bypass_manager:
        await _rate_limit_bypass_manager.stop()


async def check_rate_limit_bypass(
    client_id: str,
    endpoint: str,
    user_tier: str,
    ip_address: str,
    context: Dict[str, Any] = None
) -> Tuple[bool, Dict[str, Any]]:
    """Check if request should bypass rate limits."""
    bypass = get_rate_limit_bypass_manager()
    return await bypass.check_bypass(client_id, endpoint, user_tier, ip_address, context)


def get_bypass_stats() -> Dict[str, Any]:
    """Get bypass statistics."""
    bypass = get_rate_limit_bypass_manager()
    return bypass.get_bypass_stats()
