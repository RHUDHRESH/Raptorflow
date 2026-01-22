"""
Comprehensive security validation system for agent operations.
Provides security checks, threat detection, and protection mechanisms.
"""

import hashlib
import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for agent operations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Types of security threats."""

    INJECTION = "injection"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    DENIAL_OF_SERVICE = "denial_of_service"
    MALICIOUS_CONTENT = "malicious_content"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RESOURCE_ABUSE = "resource_abuse"


@dataclass
class SecurityEvent:
    """Security event record."""

    timestamp: datetime
    threat_type: ThreatType
    severity: SecurityLevel
    description: str
    source: str
    user_id: Optional[str]
    workspace_id: Optional[str]
    details: Dict[str, Any]
    blocked: bool = False
    action_taken: Optional[str] = None


@dataclass
class SecurityPolicy:
    """Security policy configuration."""

    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    max_concurrent_requests: int = 10
    max_input_length: int = 50000
    max_output_length: int = 100000
    blocked_ips: Set[str] = None
    blocked_users: Set[str] = None
    allowed_domains: Set[str] = None
    require_authentication: bool = True
    enable_content_filtering: bool = True
    enable_rate_limiting: bool = True
    enable_monitoring: bool = True

    def __post_init__(self):
        if self.blocked_ips is None:
            self.blocked_ips = set()
        if self.blocked_users is None:
            self.blocked_users = set()
        if self.allowed_domains is None:
            self.allowed_domains = set()


class SecurityValidator:
    """Comprehensive security validation system."""

    def __init__(self, policy: Optional[SecurityPolicy] = None):
        self.policy = policy or SecurityPolicy()
        self.security_events: List[SecurityEvent] = []
        self.blocked_entities: Dict[str, Set[str]] = {
            "ips": set(),
            "users": set(),
            "workspaces": set(),
        }
        self.request_counts: Dict[str, List[datetime]] = {}
        self.concurrent_requests: Dict[str, int] = {}

        # Security patterns
        self.injection_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"eval\s*\(",
            r"document\.",
            r"window\.",
            r"localStorage",
            r"sessionStorage",
            r"__import__",
            r"exec\s*\(",
            r"import\s+",
            r"from\s+\w+\s+import",
            r"base64",
            r"data:text/html",
            r"file://",
            r"ftp://",
        ]

        self.privilege_escalation_patterns = [
            r"admin",
            r"root",
            r"sudo",
            r"privilege",
            r"escalate",
            r"system",
            r"config",
            r"password",
            r"token",
            r"secret",
            r"key",
            r"auth",
            r"credential",
        ]

        self.data_exfiltration_patterns = [
            r"export",
            r"download",
            r"extract",
            r"dump",
            r"backup",
            r"copy.*all",
            r"select.*\*",
            r"cat.*etc",
            r"ls.*-la",
        ]

    async def validate_request(
        self,
        request_data: Dict[str, Any],
        client_ip: Optional[str] = None,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """Validate a request for security threats."""
        try:
            # Check blocked entities
            if client_ip and client_ip in self.policy.blocked_ips:
                return False, "IP address blocked"

            if user_id and user_id in self.policy.blocked_users:
                return False, "User blocked"

            # Rate limiting check
            if self.policy.enable_rate_limiting:
                rate_ok, rate_error = await self._check_rate_limits(
                    client_ip, user_id, workspace_id
                )
                if not rate_ok:
                    return False, rate_error

            # Input validation
            input_ok, input_error = self._validate_input(request_data)
            if not input_ok:
                return False, input_error

            # Content filtering
            if self.policy.enable_content_filtering:
                content_ok, content_error = self._filter_content(request_data)
                if not content_ok:
                    return False, content_error

            # Resource abuse check
            resource_ok, resource_error = self._check_resource_abuse(
                client_ip, user_id, workspace_id
            )
            if not resource_ok:
                return False, resource_error

            # Authorization check
            if self.policy.require_authentication:
                auth_ok, auth_error = self._check_authorization(request_data)
                if not auth_ok:
                    return False, auth_error

            return True, None

        except Exception as e:
            logger.error(f"Security validation error: {e}")
            return False, f"Security validation failed: {str(e)}"

    async def _check_rate_limits(
        self,
        client_ip: Optional[str],
        user_id: Optional[str],
        workspace_id: Optional[str],
    ) -> tuple[bool, Optional[str]]:
        """Check rate limiting constraints."""
        now = datetime.now()

        # Check per-minute limits
        for entity_id, limit in [
            (f"ip:{client_ip}", self.policy.max_requests_per_minute),
            (f"user:{user_id}", self.policy.max_requests_per_minute),
            (f"workspace:{workspace_id}", self.policy.max_requests_per_minute),
        ]:
            if not entity_id or entity_id.endswith(":"):
                continue

            # Clean old requests
            if entity_id in self.request_counts:
                self.request_counts[entity_id] = [
                    req_time
                    for req_time in self.request_counts[entity_id]
                    if (now - req_time).total_seconds() < 60
                ]
            else:
                self.request_counts[entity_id] = []

            # Check limit
            if len(self.request_counts[entity_id]) >= limit:
                self._log_security_event(
                    ThreatType.DENIAL_OF_SERVICE,
                    SecurityLevel.HIGH,
                    f"Rate limit exceeded: {len(self.request_counts[entity_id])}/{limit}",
                    entity_id,
                    user_id,
                    workspace_id,
                    {"limit": limit, "current": len(self.request_counts[entity_id])},
                )
                return False, f"Rate limit exceeded: {limit} requests per minute"

            # Add current request
            self.request_counts[entity_id].append(now)

        # Check per-hour limits
        for entity_id, limit in [
            (f"user:{user_id}", self.policy.max_requests_per_hour),
            (f"workspace:{workspace_id}", self.policy.max_requests_per_hour),
        ]:
            if not entity_id or entity_id.endswith(":"):
                continue

            # Count requests in last hour
            if entity_id in self.request_counts:
                hour_count = len(
                    [
                        req_time
                        for req_time in self.request_counts[entity_id]
                        if (now - req_time).total_seconds() < 3600
                    ]
                )

                if hour_count >= limit:
                    self._log_security_event(
                        ThreatType.DENIAL_OF_SERVICE,
                        SecurityLevel.MEDIUM,
                        f"Hourly rate limit exceeded: {hour_count}/{limit}",
                        entity_id,
                        user_id,
                        workspace_id,
                        {"limit": limit, "current": hour_count},
                    )
                    return (
                        False,
                        f"Hourly rate limit exceeded: {limit} requests per hour",
                    )

        return True, None

    def _validate_input(
        self, request_data: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate input data for security threats."""
        # Check input length
        request_str = str(request_data)
        if len(request_str) > self.policy.max_input_length:
            return (
                False,
                f"Input too large: {len(request_str)} > {self.policy.max_input_length}",
            )

        # Check for injection attacks
        for pattern in self.injection_patterns:
            if re.search(pattern, request_str, re.IGNORECASE | re.DOTALL):
                self._log_security_event(
                    ThreatType.INJECTION,
                    SecurityLevel.CRITICAL,
                    f"Injection pattern detected: {pattern}",
                    "input_validation",
                    request_data.get("user_id"),
                    request_data.get("workspace_id"),
                    {"pattern": pattern},
                )
                return False, f"Potentially malicious content detected"

        # Check for privilege escalation attempts
        for pattern in self.privilege_escalation_patterns:
            if re.search(pattern, request_str, re.IGNORECASE):
                self._log_security_event(
                    ThreatType.PRIVILEGE_ESCALATION,
                    SecurityLevel.HIGH,
                    f"Privilege escalation attempt: {pattern}",
                    "input_validation",
                    request_data.get("user_id"),
                    request_data.get("workspace_id"),
                    {"pattern": pattern},
                )
                return False, f"Unauthorized operation attempted"

        # Check for data exfiltration attempts
        for pattern in self.data_exfiltration_patterns:
            if re.search(pattern, request_str, re.IGNORECASE):
                self._log_security_event(
                    ThreatType.DATA_EXFILTRATION,
                    SecurityLevel.HIGH,
                    f"Data exfiltration attempt: {pattern}",
                    "input_validation",
                    request_data.get("user_id"),
                    request_data.get("workspace_id"),
                    {"pattern": pattern},
                )
                return False, f"Data access violation detected"

        return True, None

    def _filter_content(
        self, request_data: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Filter content for malicious patterns."""
        content_fields = ["request", "prompt", "message", "text"]

        for field in content_fields:
            if field in request_data:
                content = str(request_data[field])

                # Check for suspicious keywords
                suspicious_keywords = [
                    "hack",
                    "crack",
                    "exploit",
                    "payload",
                    "shell",
                    "backdoor",
                    "malware",
                    "virus",
                    "trojan",
                ]

                for keyword in suspicious_keywords:
                    if keyword.lower() in content.lower():
                        self._log_security_event(
                            ThreatType.MALICIOUS_CONTENT,
                            SecurityLevel.MEDIUM,
                            f"Suspicious keyword detected: {keyword}",
                            "content_filtering",
                            request_data.get("user_id"),
                            request_data.get("workspace_id"),
                            {"keyword": keyword, "field": field},
                        )
                        # Don't block, just log for monitoring

        return True, None

    def _check_resource_abuse(
        self,
        client_ip: Optional[str],
        user_id: Optional[str],
        workspace_id: Optional[str],
    ) -> tuple[bool, Optional[str]]:
        """Check for resource abuse patterns."""
        # Check concurrent requests
        for entity_id in [f"user:{user_id}", f"workspace:{workspace_id}"]:
            if not entity_id or entity_id.endswith(":"):
                continue

            current_count = self.concurrent_requests.get(entity_id, 0)
            if current_count >= self.policy.max_concurrent_requests:
                self._log_security_event(
                    ThreatType.DENIAL_OF_SERVICE,
                    SecurityLevel.MEDIUM,
                    f"Concurrent request limit exceeded: {current_count}",
                    entity_id,
                    user_id,
                    workspace_id,
                    {"limit": self.policy.max_concurrent_requests},
                )
                return False, f"Too many concurrent requests"

        return True, None

    def _check_authorization(
        self, request_data: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Check authorization for the request."""
        # Check if user_id is present
        if not request_data.get("user_id"):
            return False, "Authentication required"

        # Check workspace access
        if not request_data.get("workspace_id"):
            return False, "Workspace ID required"

        # Additional authorization checks can be added here
        # For now, just basic validation
        return True, None

    def _log_security_event(
        self,
        threat_type: ThreatType,
        severity: SecurityLevel,
        description: str,
        source: str,
        user_id: Optional[str],
        workspace_id: Optional[str],
        details: Dict[str, Any],
    ):
        """Log a security event."""
        event = SecurityEvent(
            timestamp=datetime.now(),
            threat_type=threat_type,
            severity=severity,
            description=description,
            source=source,
            user_id=user_id,
            workspace_id=workspace_id,
            details=details,
        )

        self.security_events.append(event)

        # Log to system logger
        log_level = {
            SecurityLevel.LOW: logging.INFO,
            SecurityLevel.MEDIUM: logging.WARNING,
            SecurityLevel.HIGH: logging.ERROR,
            SecurityLevel.CRITICAL: logging.CRITICAL,
        }.get(severity, logging.INFO)

        logger.log(
            log_level,
            f"Security Event [{severity.value.upper()}] {threat_type.value}: {description}",
        )

        # Auto-block for critical threats
        if severity == SecurityLevel.CRITICAL:
            self._auto_block(source, user_id, workspace_id)

    def _auto_block(
        self, source: str, user_id: Optional[str], workspace_id: Optional[str]
    ):
        """Automatically block entities for critical threats."""
        if user_id:
            self.policy.blocked_users.add(user_id)
            self.blocked_entities["users"].add(user_id)
            logger.warning(f"Auto-blocked user: {user_id}")

        if workspace_id:
            self.blocked_entities["workspaces"].add(workspace_id)
            logger.warning(f"Auto-blocked workspace: {workspace_id}")

    def increment_concurrent_request(
        self,
        client_ip: Optional[str],
        user_id: Optional[str],
        workspace_id: Optional[str],
    ):
        """Increment concurrent request count."""
        for entity_id in [f"user:{user_id}", f"workspace:{workspace_id}"]:
            if entity_id and not entity_id.endswith(":"):
                self.concurrent_requests[entity_id] = (
                    self.concurrent_requests.get(entity_id, 0) + 1
                )

    def decrement_concurrent_request(
        self,
        client_ip: Optional[str],
        user_id: Optional[str],
        workspace_id: Optional[str],
    ):
        """Decrement concurrent request count."""
        for entity_id in [f"user:{user_id}", f"workspace:{workspace_id}"]:
            if entity_id and not entity_id.endswith(":"):
                self.concurrent_requests[entity_id] = max(
                    self.concurrent_requests.get(entity_id, 0) - 1, 0
                )

    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics."""
        now = datetime.now()
        recent_events = [
            event
            for event in self.security_events
            if (now - event.timestamp).total_seconds() < 3600  # Last hour
        ]

        threat_counts = {}
        for event in recent_events:
            threat_counts[event.threat_type.value] = (
                threat_counts.get(event.threat_type.value, 0) + 1
            )

        return {
            "total_events": len(self.security_events),
            "recent_events": len(recent_events),
            "blocked_ips": len(self.policy.blocked_ips),
            "blocked_users": len(self.policy.blocked_users),
            "blocked_workspaces": len(self.blocked_entities["workspaces"]),
            "concurrent_requests": dict(self.concurrent_requests),
            "threat_distribution": threat_counts,
            "policy": {
                "max_requests_per_minute": self.policy.max_requests_per_minute,
                "max_requests_per_hour": self.policy.max_requests_per_hour,
                "max_concurrent_requests": self.policy.max_concurrent_requests,
            },
        }

    def get_recent_events(
        self,
        hours: int = 24,
        threat_type: Optional[ThreatType] = None,
        severity: Optional[SecurityLevel] = None,
    ) -> List[SecurityEvent]:
        """Get recent security events with optional filtering."""
        cutoff = datetime.now() - timedelta(hours=hours)

        events = [event for event in self.security_events if event.timestamp >= cutoff]

        if threat_type:
            events = [event for event in events if event.threat_type == threat_type]

        if severity:
            events = [event for event in events if event.severity == severity]

        return sorted(events, key=lambda x: x.timestamp, reverse=True)

    def clear_old_events(self, days: int = 30):
        """Clear old security events."""
        cutoff = datetime.now() - timedelta(days=days)
        old_count = len(self.security_events)
        self.security_events = [
            event for event in self.security_events if event.timestamp >= cutoff
        ]
        logger.info(
            f"Cleared {old_count - len(self.security_events)} old security events"
        )


# Global security validator instance
_security_validator: Optional[SecurityValidator] = None


def get_security_validator() -> SecurityValidator:
    """Get the global security validator instance."""
    global _security_validator
    if _security_validator is None:
        _security_validator = SecurityValidator()
    return _security_validator


async def validate_agent_request(
    request_data: Dict[str, Any],
    client_ip: Optional[str] = None,
    user_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
) -> tuple[bool, Optional[str]]:
    """Validate agent request for security (convenience function)."""
    validator = get_security_validator()
    return await validator.validate_request(
        request_data, client_ip, user_id, workspace_id
    )


def get_security_stats() -> Dict[str, Any]:
    """Get security statistics (convenience function)."""
    validator = get_security_validator()
    return validator.get_security_stats()


def get_recent_security_events(
    hours: int = 24,
    threat_type: Optional[ThreatType] = None,
    severity: Optional[SecurityLevel] = None,
) -> List[Dict[str, Any]]:
    """Get recent security events (convenience function)."""
    validator = get_security_validator()
    events = validator.get_recent_events(hours, threat_type, severity)
    return [
        {
            "timestamp": event.timestamp.isoformat(),
            "threat_type": event.threat_type.value,
            "severity": event.severity.value,
            "description": event.description,
            "source": event.source,
            "user_id": event.user_id,
            "workspace_id": event.workspace_id,
            "details": event.details,
            "blocked": event.blocked,
            "action_taken": event.action_taken,
        }
        for event in events
    ]


# Security middleware for FastAPI
class SecurityMiddleware:
    """FastAPI middleware for security validation."""

    def __init__(self, app):
        self.app = app
        self.validator = get_security_validator()

    async def __call__(self, scope, receive, send):
        """Middleware implementation."""
        # This would be implemented as proper FastAPI middleware
        # For now, it's a placeholder
        await self.app(scope, receive, send)
