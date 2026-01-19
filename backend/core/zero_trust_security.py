"""
Zero-Trust Security Architecture with Micro-Segmentation
Provides enterprise-grade security with identity verification, micro-segmentation, and lateral movement prevention.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import secrets
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger(__name__)


class TrustLevel(Enum):
    """Trust levels in zero-trust architecture."""
    UNTRUSTED = "untrusted"
    MINIMAL = "minimal"
    STANDARD = "standard"
    ELEVATED = "elevated"
    PRIVILEGED = "privileged"


class SegmentType(Enum):
    """Network segment types."""
    PUBLIC = "public"
    DMZ = "dmz"
    APPLICATION = "application"
    DATABASE = "database"
    ADMIN = "admin"
    MONITORING = "monitoring"


class AccessType(Enum):
    """Types of access requests."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    ADMIN = "admin"


@dataclass
class SecurityContext:
    """Security context for access decisions."""
    user_id: str
    session_id: str
    client_ip: str
    user_agent: str
    workspace_id: str
    trust_level: TrustLevel
    authentication_method: str
    mfa_verified: bool
    device_fingerprint: str
    geo_location: Optional[str] = None
    risk_score: float = 0.0


@dataclass
class NetworkSegment:
    """Network segment definition."""
    segment_id: str
    segment_type: SegmentType
    trust_level: TrustLevel
    allowed_sources: Set[str]
    allowed_destinations: Set[str]
    allowed_protocols: Set[str]
    required_trust_level: TrustLevel
    time_restrictions: Optional[Dict[str, Any]] = None
    geo_restrictions: Optional[Set[str]] = None


@dataclass
class AccessPolicy:
    """Access policy definition."""
    policy_id: str
    name: str
    description: str
    resource_pattern: str
    required_trust_level: TrustLevel
    allowed_access_types: Set[AccessType]
    conditions: Dict[str, Any]
    time_restrictions: Optional[Dict[str, Any]] = None
    rate_limits: Optional[Dict[str, int]] = None


@dataclass
class SecurityEvent:
    """Security event for audit and monitoring."""
    timestamp: datetime
    event_type: str
    user_id: str
    session_id: str
    client_ip: str
    resource: str
    action: str
    granted: bool
    trust_level: TrustLevel
    risk_score: float
    details: Dict[str, Any]


class ZeroTrustSecurity:
    """Zero-trust security implementation with micro-segmentation."""
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        self.encryption_key = encryption_key or self._generate_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Security state
        self.active_sessions: Dict[str, SecurityContext] = {}
        self.network_segments: Dict[str, NetworkSegment] = {}
        self.access_policies: Dict[str, AccessPolicy] = {}
        self.security_events: List[SecurityEvent] = []
        self.blocked_entities: Dict[str, Set[str]] = {
            "ips": set(),
            "users": set(),
            "sessions": set(),
            "devices": set(),
        }
        
        # Risk scoring
        self.risk_factors: Dict[str, float] = {
            "new_device": 0.3,
            "new_location": 0.2,
            "failed_auth": 0.4,
            "unusual_time": 0.1,
            "high_risk_country": 0.5,
            "suspicious_pattern": 0.6,
        }
        
        # Initialize default segments
        self._initialize_default_segments()
        self._initialize_default_policies()
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key."""
        password = b"raptorflow_zero_trust_key"
        salt = b"raptorflow_salt"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def _initialize_default_segments(self):
        """Initialize default network segments."""
        segments = [
            NetworkSegment(
                segment_id="public",
                segment_type=SegmentType.PUBLIC,
                trust_level=TrustLevel.UNTRUSTED,
                allowed_sources={"*"},
                allowed_destinations={"dmz"},
                allowed_protocols={"https", "http"},
                required_trust_level=TrustLevel.UNTRUSTED,
            ),
            NetworkSegment(
                segment_id="dmz",
                segment_type=SegmentType.DMZ,
                trust_level=TrustLevel.MINIMAL,
                allowed_sources={"public"},
                allowed_destinations={"application"},
                allowed_protocols={"https"},
                required_trust_level=TrustLevel.MINIMAL,
            ),
            NetworkSegment(
                segment_id="application",
                segment_type=SegmentType.APPLICATION,
                trust_level=TrustLevel.STANDARD,
                allowed_sources={"dmz"},
                allowed_destinations={"database"},
                allowed_protocols={"https", "grpc"},
                required_trust_level=TrustLevel.STANDARD,
            ),
            NetworkSegment(
                segment_id="database",
                segment_type=SegmentType.DATABASE,
                trust_level=TrustLevel.ELEVATED,
                allowed_sources={"application"},
                allowed_destinations=set(),
                allowed_protocols={"postgresql", "redis"},
                required_trust_level=TrustLevel.ELEVATED,
            ),
            NetworkSegment(
                segment_id="admin",
                segment_type=SegmentType.ADMIN,
                trust_level=TrustLevel.PRIVILEGED,
                allowed_sources={"application"},
                allowed_destinations={"*"},
                allowed_protocols={"https", "ssh"},
                required_trust_level=TrustLevel.PRIVILEGED,
            ),
        ]
        
        for segment in segments:
            self.network_segments[segment.segment_id] = segment
    
    def _initialize_default_policies(self):
        """Initialize default access policies."""
        policies = [
            AccessPolicy(
                policy_id="public_read",
                name="Public Read Access",
                description="Allow read access to public resources",
                resource_pattern="/public/*",
                required_trust_level=TrustLevel.UNTRUSTED,
                allowed_access_types={AccessType.READ},
                conditions={},
            ),
            AccessPolicy(
                policy_id="user_data_access",
                name="User Data Access",
                description="Allow users to access their own data",
                resource_pattern="/api/v1/users/{user_id}/*",
                required_trust_level=TrustLevel.STANDARD,
                allowed_access_types={AccessType.READ, AccessType.WRITE},
                conditions={"ownership_check": True},
            ),
            AccessPolicy(
                policy_id="admin_operations",
                name="Administrative Operations",
                description="Allow administrative operations",
                resource_pattern="/api/v1/admin/*",
                required_trust_level=TrustLevel.PRIVILEGED,
                allowed_access_types={AccessType.READ, AccessType.WRITE, AccessType.EXECUTE, AccessType.DELETE},
                conditions={"admin_role": True},
                rate_limits={"requests_per_minute": 30},
            ),
        ]
        
        for policy in policies:
            self.access_policies[policy.policy_id] = policy
    
    async def create_security_context(
        self,
        user_id: str,
        session_id: str,
        client_ip: str,
        user_agent: str,
        workspace_id: str,
        authentication_method: str,
        mfa_verified: bool = False,
        device_fingerprint: Optional[str] = None,
        geo_location: Optional[str] = None,
    ) -> SecurityContext:
        """Create and validate security context."""
        # Generate device fingerprint if not provided
        if not device_fingerprint:
            device_fingerprint = self._generate_device_fingerprint(client_ip, user_agent)
        
        # Calculate risk score
        risk_score = await self._calculate_risk_score(
            user_id, client_ip, device_fingerprint, geo_location
        )
        
        # Determine trust level
        trust_level = self._determine_trust_level(
            authentication_method, mfa_verified, risk_score
        )
        
        context = SecurityContext(
            user_id=user_id,
            session_id=session_id,
            client_ip=client_ip,
            user_agent=user_agent,
            workspace_id=workspace_id,
            trust_level=trust_level,
            authentication_method=authentication_method,
            mfa_verified=mfa_verified,
            device_fingerprint=device_fingerprint,
            geo_location=geo_location,
            risk_score=risk_score,
        )
        
        # Store session
        self.active_sessions[session_id] = context
        
        # Log session creation
        self._log_security_event(
            event_type="session_created",
            context=context,
            resource="session",
            action="create",
            granted=True,
            details={
                "authentication_method": authentication_method,
                "mfa_verified": mfa_verified,
                "risk_score": risk_score,
            }
        )
        
        return context
    
    def _generate_device_fingerprint(self, client_ip: str, user_agent: str) -> str:
        """Generate device fingerprint."""
        data = f"{client_ip}:{user_agent}:{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    async def _calculate_risk_score(
        self,
        user_id: str,
        client_ip: str,
        device_fingerprint: str,
        geo_location: Optional[str],
    ) -> float:
        """Calculate risk score based on various factors."""
        risk_score = 0.0
        
        # Check for new device
        if not self._is_known_device(user_id, device_fingerprint):
            risk_score += self.risk_factors["new_device"]
        
        # Check for new location
        if geo_location and not self._is_known_location(user_id, geo_location):
            risk_score += self.risk_factors["new_location"]
        
        # Check for suspicious IP
        if self._is_suspicious_ip(client_ip):
            risk_score += self.risk_factors["suspicious_pattern"]
        
        # Check for high-risk country
        if geo_location and self._is_high_risk_country(geo_location):
            risk_score += self.risk_factors["high_risk_country"]
        
        # Check time-based patterns
        if self._is_unusual_access_time(user_id):
            risk_score += self.risk_factors["unusual_time"]
        
        return min(risk_score, 1.0)
    
    def _is_known_device(self, user_id: str, device_fingerprint: str) -> bool:
        """Check if device is known for the user."""
        # In production, this would check a database
        # For now, simulate with recent sessions
        for session in self.active_sessions.values():
            if session.user_id == user_id and session.device_fingerprint == device_fingerprint:
                return True
        return False
    
    def _is_known_location(self, user_id: str, geo_location: str) -> bool:
        """Check if location is known for the user."""
        # In production, this would check a database
        for session in self.active_sessions.values():
            if session.user_id == user_id and session.geo_location == geo_location:
                return True
        return False
    
    def _is_suspicious_ip(self, client_ip: str) -> bool:
        """Check if IP is suspicious."""
        # Check against blocked IPs
        return client_ip in self.blocked_entities["ips"]
    
    def _is_high_risk_country(self, geo_location: str) -> bool:
        """Check if location is high-risk."""
        # In production, this would use threat intelligence
        high_risk_countries = {"CN", "RU", "KP", "IR"}
        return geo_location in high_risk_countries
    
    def _is_unusual_access_time(self, user_id: str) -> bool:
        """Check if access time is unusual for the user."""
        current_hour = datetime.now().hour
        # In production, this would analyze user's historical patterns
        # For now, consider 2 AM - 6 AM as unusual
        return 2 <= current_hour <= 6
    
    def _determine_trust_level(
        self,
        authentication_method: str,
        mfa_verified: bool,
        risk_score: float,
    ) -> TrustLevel:
        """Determine trust level based on authentication and risk."""
        if authentication_method == "certificate" and mfa_verified and risk_score < 0.1:
            return TrustLevel.PRIVILEGED
        elif authentication_method in ["sso", "oauth2"] and mfa_verified and risk_score < 0.3:
            return TrustLevel.ELEVATED
        elif authentication_method in ["password", "token"] and mfa_verified and risk_score < 0.5:
            return TrustLevel.STANDARD
        elif risk_score < 0.7:
            return TrustLevel.MINIMAL
        else:
            return TrustLevel.UNTRUSTED
    
    async def verify_access(
        self,
        session_id: str,
        resource: str,
        action: AccessType,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Verify access request using zero-trust principles."""
        # Get security context
        context = self.active_sessions.get(session_id)
        if not context:
            return False, "Invalid session"
        
        # Check if session is blocked
        if session_id in self.blocked_entities["sessions"]:
            return False, "Session blocked"
        
        # Check if user is blocked
        if context.user_id in self.blocked_entities["users"]:
            return False, "User blocked"
        
        # Check if IP is blocked
        if context.client_ip in self.blocked_entities["ips"]:
            return False, "IP blocked"
        
        # Verify network segmentation
        if not self._verify_network_segment(context, resource):
            return False, "Network segment violation"
        
        # Find applicable policies
        applicable_policies = self._find_applicable_policies(resource)
        if not applicable_policies:
            return False, "No applicable policy found"
        
        # Evaluate policies
        for policy in applicable_policies:
            granted, reason = await self._evaluate_policy(
                context, policy, resource, action, additional_context
            )
            if granted:
                self._log_security_event(
                    event_type="access_granted",
                    context=context,
                    resource=resource,
                    action=action.value,
                    granted=True,
                    details={"policy_id": policy.policy_id, "reason": reason},
                )
                return True, None
            else:
                self._log_security_event(
                    event_type="access_denied",
                    context=context,
                    resource=resource,
                    action=action.value,
                    granted=False,
                    details={"policy_id": policy.policy_id, "reason": reason},
                )
        
        return False, "Access denied by all policies"
    
    def _verify_network_segment(self, context: SecurityContext, resource: str) -> bool:
        """Verify network segmentation rules."""
        # Determine resource segment
        resource_segment = self._determine_resource_segment(resource)
        if not resource_segment:
            return True  # No segment restrictions
        
        segment = self.network_segments.get(resource_segment)
        if not segment:
            return True  # No segment defined
        
        # Check trust level requirement
        if self._trust_level_priority(context.trust_level) < self._trust_level_priority(segment.required_trust_level):
            return False
        
        # Check time restrictions
        if segment.time_restrictions:
            if not self._check_time_restrictions(segment.time_restrictions):
                return False
        
        # Check geo restrictions
        if segment.geo_restrictions and context.geo_location:
            if context.geo_location not in segment.geo_restrictions:
                return False
        
        return True
    
    def _determine_resource_segment(self, resource: str) -> Optional[str]:
        """Determine which segment a resource belongs to."""
        if resource.startswith("/public/"):
            return "public"
        elif resource.startswith("/api/v1/"):
            return "application"
        elif resource.startswith("/admin/"):
            return "admin"
        elif resource.startswith("/db/"):
            return "database"
        return None
    
    def _trust_level_priority(self, trust_level: TrustLevel) -> int:
        """Get numeric priority for trust level."""
        priorities = {
            TrustLevel.UNTRUSTED: 0,
            TrustLevel.MINIMAL: 1,
            TrustLevel.STANDARD: 2,
            TrustLevel.ELEVATED: 3,
            TrustLevel.PRIVILEGED: 4,
        }
        return priorities.get(trust_level, 0)
    
    def _check_time_restrictions(self, time_restrictions: Dict[str, Any]) -> bool:
        """Check time-based restrictions."""
        current_time = datetime.now()
        current_hour = current_time.hour
        current_day = current_time.weekday()
        
        # Check hour restrictions
        if "hours" in time_restrictions:
            allowed_hours = time_restrictions["hours"]
            if isinstance(allowed_hours, list) and current_hour not in allowed_hours:
                return False
            if isinstance(allowed_hours, dict):
                start = allowed_hours.get("start", 0)
                end = allowed_hours.get("end", 23)
                if not (start <= current_hour <= end):
                    return False
        
        # Check day restrictions
        if "days" in time_restrictions:
            allowed_days = time_restrictions["days"]
            if current_day not in allowed_days:
                return False
        
        return True
    
    def _find_applicable_policies(self, resource: str) -> List[AccessPolicy]:
        """Find policies applicable to the resource."""
        applicable = []
        
        for policy in self.access_policies.values():
            if self._resource_matches_pattern(resource, policy.resource_pattern):
                applicable.append(policy)
        
        return applicable
    
    def _resource_matches_pattern(self, resource: str, pattern: str) -> bool:
        """Check if resource matches policy pattern."""
        # Simple pattern matching - in production, use regex or path matching library
        if "*" in pattern:
            # Convert to regex
            regex_pattern = pattern.replace("*", ".*")
            import re
            return re.match(f"^{regex_pattern}$", resource) is not None
        else:
            return resource == pattern
    
    async def _evaluate_policy(
        self,
        context: SecurityContext,
        policy: AccessPolicy,
        resource: str,
        action: AccessType,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, str]:
        """Evaluate access policy."""
        # Check trust level
        if self._trust_level_priority(context.trust_level) < self._trust_level_priority(policy.required_trust_level):
            return False, f"Insufficient trust level. Required: {policy.required_trust_level.value}"
        
        # Check access type
        if action not in policy.allowed_access_types:
            return False, f"Access type {action.value} not allowed by policy"
        
        # Check conditions
        for condition, expected_value in policy.conditions.items():
            if not self._evaluate_condition(condition, expected_value, context, resource, additional_context):
                return False, f"Condition {condition} not met"
        
        # Check time restrictions
        if policy.time_restrictions:
            if not self._check_time_restrictions(policy.time_restrictions):
                return False, "Time restrictions not met"
        
        # Check rate limits
        if policy.rate_limits:
            if not await self._check_rate_limits(context, policy.rate_limits):
                return False, "Rate limit exceeded"
        
        return True, "Access granted"
    
    def _evaluate_condition(
        self,
        condition: str,
        expected_value: Any,
        context: SecurityContext,
        resource: str,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Evaluate policy condition."""
        if condition == "ownership_check":
            # Check if user owns the resource
            user_id_pattern = f"/users/{context.user_id}/"
            return user_id_pattern in resource
        
        elif condition == "admin_role":
            # Check if user has admin role
            # In production, this would check user roles from database
            return context.trust_level in [TrustLevel.ELEVATED, TrustLevel.PRIVILEGED]
        
        elif condition == "mfa_required":
            return context.mfa_verified
        
        elif condition == "low_risk":
            return context.risk_score < 0.3
        
        # Additional conditions can be added here
        
        return True
    
    async def _check_rate_limits(
        self,
        context: SecurityContext,
        rate_limits: Dict[str, int],
    ) -> bool:
        """Check rate limits for the policy."""
        # In production, this would use Redis or similar for distributed rate limiting
        # For now, simple in-memory tracking
        current_time = time.time()
        window_start = current_time - 60  # 1-minute window
        
        # Count recent requests for this user/policy
        recent_requests = [
            event for event in self.security_events
            if (event.user_id == context.user_id and
                event.timestamp >= datetime.fromtimestamp(window_start) and
                event.event_type == "access_granted")
        ]
        
        requests_per_minute = len(recent_requests)
        limit = rate_limits.get("requests_per_minute", float('inf'))
        
        return requests_per_minute <= limit
    
    def _log_security_event(
        self,
        event_type: str,
        context: SecurityContext,
        resource: str,
        action: str,
        granted: bool,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log security event."""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            user_id=context.user_id,
            session_id=context.session_id,
            client_ip=context.client_ip,
            resource=resource,
            action=action,
            granted=granted,
            trust_level=context.trust_level,
            risk_score=context.risk_score,
            details=details or {},
        )
        
        self.security_events.append(event)
        
        # Log to system logger
        level = logging.INFO if granted else logging.WARNING
        logger.log(
            level,
            f"Zero-Trust Event [{event_type}] {context.user_id} -> {resource} ({action}): {'GRANTED' if granted else 'DENIED'}"
        )
    
    def block_entity(self, entity_type: str, entity_id: str, reason: str = ""):
        """Block an entity (IP, user, session, device)."""
        if entity_type in self.blocked_entities:
            self.blocked_entities[entity_type].add(entity_id)
            logger.warning(f"Blocked {entity_type}: {entity_id} - {reason}")
    
    def unblock_entity(self, entity_type: str, entity_id: str):
        """Unblock an entity."""
        if entity_type in self.blocked_entities:
            self.blocked_entities[entity_type].discard(entity_id)
            logger.info(f"Unblocked {entity_type}: {entity_id}")
    
    def revoke_session(self, session_id: str, reason: str = ""):
        """Revoke a session."""
        if session_id in self.active_sessions:
            context = self.active_sessions[session_id]
            del self.active_sessions[session_id]
            self.block_entity("sessions", session_id, reason)
            logger.warning(f"Revoked session: {session_id} - {reason}")
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics."""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)
        
        recent_events_hour = [
            event for event in self.security_events
            if event.timestamp >= last_hour
        ]
        
        recent_events_day = [
            event for event in self.security_events
            if event.timestamp >= last_day
        ]
        
        # Calculate metrics
        total_requests = len([e for e in recent_events_hour if e.event_type == "access_granted"])
        denied_requests = len([e for e in recent_events_hour if e.event_type == "access_denied"])
        
        trust_level_distribution = {}
        for session in self.active_sessions.values():
            level = session.trust_level.value
            trust_level_distribution[level] = trust_level_distribution.get(level, 0) + 1
        
        return {
            "active_sessions": len(self.active_sessions),
            "blocked_entities": {
                entity_type: len(entities) 
                for entity_type, entities in self.blocked_entities.items()
            },
            "requests_last_hour": {
                "total": total_requests,
                "denied": denied_requests,
                "denial_rate": denied_requests / max(total_requests, 1),
            },
            "events_last_hour": len(recent_events_hour),
            "events_last_day": len(recent_events_day),
            "trust_level_distribution": trust_level_distribution,
            "average_risk_score": sum(s.risk_score for s in self.active_sessions.values()) / max(len(self.active_sessions), 1),
        }
    
    def get_security_events(
        self,
        hours: int = 24,
        event_type: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get security events with filtering."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        events = [
            event for event in self.security_events
            if event.timestamp >= cutoff
        ]
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        return [
            {
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type,
                "user_id": event.user_id,
                "session_id": event.session_id,
                "client_ip": event.client_ip,
                "resource": event.resource,
                "action": event.action,
                "granted": event.granted,
                "trust_level": event.trust_level.value,
                "risk_score": event.risk_score,
                "details": event.details,
            }
            for event in sorted(events, key=lambda x: x.timestamp, reverse=True)
        ]
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()


# Global zero-trust security instance
_zero_trust_security: Optional[ZeroTrustSecurity] = None


def get_zero_trust_security() -> ZeroTrustSecurity:
    """Get the global zero-trust security instance."""
    global _zero_trust_security
    if _zero_trust_security is None:
        _zero_trust_security = ZeroTrustSecurity()
    return _zero_trust_security


# Middleware for FastAPI integration
class ZeroTrustMiddleware:
    """FastAPI middleware for zero-trust security."""
    
    def __init__(self, app, security: Optional[ZeroTrustSecurity] = None):
        self.app = app
        self.security = security or get_zero_trust_security()
    
    async def __call__(self, scope, receive, send):
        """Middleware implementation."""
        if scope["type"] == "http":
            # Extract request information
            # This would be implemented as proper FastAPI middleware
            pass
        
        await self.app(scope, receive, send)
