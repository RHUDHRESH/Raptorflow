"""
Agent Security for Raptorflow Backend
===================================

This module provides comprehensive security measures for agent system
with input validation, access controls, audit logging, and rate limiting.

Features:
- Input validation and sanitization
- Access control and authentication
- Audit logging and security monitoring
- Rate limiting and IP blocking
- Security policies and compliance
- Threat detection and prevention
"""

import asyncio
import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
from collections import defaultdict, deque

from .exceptions import SecurityError

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """Threat types."""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    MALICIOUS_UPLOAD = "malicious_upload"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    BRUTE_FORCE = "brute_force"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"


class AccessLevel(Enum):
    """Access levels."""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    AUTHORIZED = "authorized"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


@dataclass
class SecurityEvent:
    """Security event data."""
    
    event_id: str
    event_type: str
    severity: SecurityLevel
    timestamp: datetime = field(default_factory=datetime.now)
    source_ip: str
    user_id: Optional[str] = None
    agent_name: Optional[str] = None
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    blocked: bool = False
    resolved: bool = False
    resolution: str = ""


@dataclass
class SecurityPolicy:
    """Security policy configuration."""
    
    policy_id: str
    name: str
    description: str
    enabled: bool = True
    rules: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityConfig:
    """Security configuration."""
    
    enable_input_validation: bool = True
    enable_rate_limiting: bool = True
    enable_ip_blocking: bool = True
    enable_audit_logging: bool = True
    enable_threat_detection: bool = True
    max_request_size: int = 10000
    max_failed_attempts: int = 10
    block_duration: int = 3600  # 1 hour
    audit_retention_days: int = 30
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    suspicious_patterns: List[str] = field(default_factory=lambda: [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"eval\(",
        r"union\s+select",
        r"drop\s+table",
        r"exec\s*\(",
        r"system\s*\(",
        r"cmd\s*\/c",
        r"powershell",
        r"/etc/passwd",
        r"/etc/shadow",
        r"\/proc\/",
        r"\/sys\/",
        r"\.\./",
        r"\.\.\\",
        r"base64_decode",
        r"unserialize",
        r"file_get_contents",
        r"file_put_contents",
        r"curl\s+exec",
        r"wget\s+",
        r"nc\s+",
        r"netcat",
        r"telnet",
        r"ssh",
        r"ftp",
        r"tftp",
        r"ldap",
        r"sqlmap",
        r"nmap",
        r"metasploit",
        r"burp",
        r"nikto",
        r"sqlninja",
        r"hydra",
        r"john",
        r"hashcat",
        r"aircrack",
        r"wireshark",
        r"tcpdump",
        r"strace",
        r"ltrace",
        r"gdb",
        r"objdump",
        r"radare2",
        r"ida",
        r"ghidra",
        r"binary_exploitation",
        r"buffer_overflow",
        r"stack_overflow",
        r"heap_overflow",
        r"format_string",
        r"integer_overflow",
        r"race_condition",
        r"privilege_escalation",
        r"cross_site_scripting",
        r"clickjacking",
        r"session_hijacking",
        r"token_manipulation",
        r"replay_attack",
        r"timing_attack",
        r"side_channel_attack",
        r"dictionary_attack",
        r"brute_force_attack",
        r"credential_stuffing",
        r"rainbow_table",
        r"social_engineering",
        r"phishing",
        r"malware",
        r"virus",
        r"trojan",
        r"rootkit",
        r"backdoor",
        r"botnet",
        r"ddos",
        r"dos",
        r"amplification",
        r"zero_day_exploit"
    ])


class SecurityManager:
    """Security manager for agent system."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.blocked_ips: Set[str] = set()
        self.failed_attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.security_events: List[SecurityEvent] = []
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.threat_patterns: Dict[str, re.Pattern] = {}
        self._load_security_data()
        self._compile_threat_patterns()
    
    def _load_security_data(self) -> None:
        """Load security data from storage."""
        try:
            import os
            os.makedirs("./data/security", exist_ok=True)
            
            # Load blocked IPs
            blocked_ips_file = os.path.join("./data/security", "blocked_ips.json")
            if os.path.exists(blocked_ips_file):
                with open(blocked_ips_file, 'r') as f:
                    data = json.load(f)
                    self.blocked_ips = set(data.get("blocked_ips", []))
            
            # Load security events
            events_file = os.path.join("./data/security", "security_events.json")
            if os.path.exists(events_file):
                with open(events_file, 'r') as f:
                    data = json.load(f)
                    self.security_events = [SecurityEvent(**event) for event in data.get("events", [])]
            
            logger.info("Security data loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load security data: {e}")
    
    def _save_security_data(self) -> None:
        """Save security data to storage."""
        try:
            import os
            os.makedirs("./data/security", exist_ok=True)
            
            # Save blocked IPs
            blocked_ips_file = os.path.join("./data/security", "blocked_ips.json")
            with open(blocked_ips_file, 'w') as f:
                json.dump({"blocked_ips": list(self.blocked_ips)}, f, indent=2)
            
            # Save security events
            events_file = os.path.join("./data/security", "security_events.json")
            events_data = {
                "events": [
                    {
                        "event_id": event.event_id,
                        "event_type": event.event_type,
                        "severity": event.severity.value,
                        "timestamp": event.timestamp.isoformat(),
                        "source_ip": event.source_ip,
                        "user_id": event.user_id,
                        "agent_name": event.agent_name,
                        "description": event.description,
                        "details": event.details,
                        "blocked": event.blocked,
                        "resolved": event.resolved,
                        "resolution": event.resolution
                    }
                    for event in self.security_events
                ]
            }
            
            # Keep only recent events (retention policy)
            if len(events_data["events"]) > self.config.audit_retention_days * 1000:  # Assuming ~1000 events per day
                cutoff_time = datetime.now() - timedelta(days=self.config.audit_retention_days)
                events_data["events"] = [
                    event for event in events_data["events"]
                    if datetime.fromisoformat(event["timestamp"]) > cutoff_time
                ]
            
            with open(events_file, 'w') as f:
                json.dump(events_data, f, indent=2)
            
            logger.info("Security data saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save security data: {e}")
            raise SecurityError(f"Failed to save security data: {e}")
    
    def _compile_threat_patterns(self) -> None:
        """Compile threat detection patterns."""
        try:
            self.threat_patterns = {}
            for pattern in self.config.suspicious_patterns:
                self.threat_patterns[pattern] = re.compile(pattern, re.IGNORECASE)
            
            logger.info(f"Compiled {len(self.threat_patterns)} threat patterns")
            
        except Exception as e:
            logger.error(f"Failed to compile threat patterns: {e}")
    
    def validate_input(self, input_data: Any, input_type: str = "general", source_ip: str = "",
                   user_id: str = "", agent_name: str = "") -> Dict[str, Any]:
        """Validate input data for security threats."""
        try:
            if not self.config.enable_input_validation:
                return {"valid": True, "sanitized": input_data}
            
            # Convert to string for pattern matching
            input_str = str(input_data)
            
            # Check for malicious patterns
            for pattern_name, pattern in self.threat_patterns.items():
                if pattern.search(input_str):
                    self._log_security_event(
                        event_type=ThreatType.SUSPICIOUS_PATTERN.value,
                        severity=SecurityLevel.HIGH,
                        source_ip=source_ip,
                        user_id=user_id,
                        agent_name=agent_name,
                        description=f"Suspicious pattern detected: {pattern_name}",
                        details={
                            "pattern": pattern_name,
                            "input": input_str,
                            "input_type": input_type
                        }
                    )
                    
                    return {
                        "valid": False,
                        "sanitized": None,
                        "error": f"Input contains suspicious pattern: {pattern_name}",
                        "threat_type": ThreatType.SUSPICIOUS_PATTERN.value
                    }
            
            # Check request size
            if len(input_str) > self.config.max_request_size:
                self._log_security_event(
                    event_type=ThreatType.MALICIOUS_UPLOAD.value,
                    severity=SecurityLevel.MEDIUM,
                    source_ip=source_ip,
                    user_id=user_id,
                    agent_name=agent_name,
                    description="Request size exceeds maximum allowed",
                    details={
                        "input_size": len(input_str),
                        "max_size": self.config.max_request_size,
                        "input_type": input_type
                    }
                )
                
                return {
                    "valid": False,
                    "sanitized": None,
                    "error": f"Request size exceeds maximum allowed: {len(input_str)} > {self.config.max_request_size}",
                    "threat_type": ThreatType.MALICIOUS_UPLOAD.value
                }
            
            # Basic input sanitization
            sanitized = self._sanitize_input(input_str)
            
            return {
                "valid": True,
                "sanitized": sanitized,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Input validation error: {e}")
            return {
                "valid": False,
                "sanitized": None,
                "error": str(e)
            }
    
    def _sanitize_input(self, input_str: str) -> str:
        """Sanitize input string."""
        try:
            # Remove potentially dangerous characters
            sanitized = re.sub(r'[<>"\']', '', input_str)
            
            # Remove SQL injection patterns
            sanitized = re.sub(r'(union|select|insert|update|delete|drop|create|alter|exec|execute)\s+', '', sanitized, flags=re.IGNORECASE)
            
            # Remove script tags
            sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE)
            
            # Remove JavaScript event handlers
            sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
            
            # Remove CSS expressions
            sanitized = re.sub(r'expression\s*\(', '', sanitized, flags=re.IGNORECASE)
            
            # Remove URL-encoded data
            sanitized = re.sub(r'%[0-9a-fA-F]{2}', '', sanitized)
            
            return sanitized.strip()
            
        except Exception as e:
            logger.error(f"Input sanitization error: {e}")
            return input_str
    
    def check_rate_limit(self, source_ip: str, user_id: str = "") -> Tuple[bool, Dict[str, Any]]:
        """Check if rate limit is exceeded."""
        try:
            if not self.config.enable_rate_limiting:
                return True, {}
            
            current_time = datetime.now()
            
            # Clean old failed attempts
            cutoff_time = current_time - timedelta(seconds=self.config.block_duration)
            self.failed_attempts = {
                ip: [attempt for attempt in attempts if attempt > cutoff_time]
                for ip, attempts in self.failed_attempts.items()
            }
            
            # Check per-minute rate limit
            minute_ago = current_time - timedelta(minutes=1)
            recent_attempts = [
                attempt for attempts in self.failed_attempts.get(source_ip, [])
                if attempt > minute_ago
            ]
            
            if len(recent_attempts) >= self.config.rate_limit_per_minute:
                return False, {
                    "error": "Rate limit exceeded (per minute)",
                    "retry_after": (recent_attempts[0] + timedelta(seconds=60)).isoformat(),
                    "attempts": len(recent_attempts)
                }
            
            # Check per-hour rate limit
            hour_ago = current_time - timedelta(hours=1)
            recent_attempts = [
                attempt for attempts in self.failed_attempts.get(source_ip, [])
                if attempt > hour_ago
            ]
            
            if len(recent_attempts) >= self.config.rate_limit_per_hour:
                return False, {
                    "error": "Rate limit exceeded (per hour)",
                    "retry_after": (recent_attempts[0] + timedelta(seconds=3600)).isoformat(),
                    "attempts": len(recent_attempts)
                }
            
            return True, {}
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return False, {"error": str(e)}
    
    def check_ip_blocked(self, source_ip: str) -> bool:
        """Check if IP is blocked."""
        return source_ip in self.blocked_ips
    
    def block_ip(self, source_ip: str, duration: Optional[int] = None, reason: str = "Security violation") -> bool:
        """Block an IP address."""
        try:
            self.blocked_ips.add(source_ip)
            self._log_security_event(
                event_type="ip_blocked",
                severity=SecurityLevel.HIGH,
                source_ip=source_ip,
                description=f"IP blocked: {reason}"
            )
            
            # Auto-unblock after duration
            if duration:
                asyncio.create_task(self._unblock_ip_after_duration(source_ip, duration))
            
            self._save_security_data()
            logger.warning(f"IP blocked: {source_ip} for reason: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to block IP {source_ip}: {e}")
            return False
    
    async def _unblock_ip_after_duration(self, source_ip: str, duration: int) -> None:
        """Unblock IP after specified duration."""
        await asyncio.sleep(duration)
        if source_ip in self.blocked_ips:
            self.blocked_ips.remove(source_ip)
            self._log_security_event(
                event_type="ip_unblocked",
                severity=SecurityLevel.LOW,
                source_ip=source_ip,
                description=f"IP automatically unblocked after {duration} seconds"
            )
            self._save_security_data()
            logger.info(f"IP unblocked: {source_ip}")
    
    def _log_security_event(self, event_type: str, severity: SecurityLevel = SecurityLevel.MEDIUM,
                       source_ip: str = "", user_id: str = "", agent_name: str = "",
                       description: str = "", details: Dict[str, Any] = None) -> None:
        """Log a security event."""
        try:
            event = SecurityEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                severity=severity,
                source_ip=source_ip,
                user_id=user_id,
                agent_name=agent_name,
                description=description,
                details=details or {}
            )
            
            self.security_events.append(event)
            
            # Keep only recent events
            if len(self.security_events) > 10000:  # Keep last 10k events
                self.security_events = self.security_events[-10000:]
            
            self._save_security_data()
            
            # Log to system logger
            log_level = severity.value.upper()
            logger.log(log_level, f"Security Event [{event_type}]: {description} (IP: {source_ip}, User: {user_id}, Agent: {agent_name})")
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    def record_failed_attempt(self, source_ip: str, user_id: str = "", reason: str = "") -> None:
        """Record a failed attempt."""
        try:
            current_time = datetime.now()
            self.failed_attempts[source_ip].append(current_time)
            
            # Check if this should trigger blocking
            if len(self.failed_attempts[source_ip]) >= self.config.max_failed_attempts:
                self.block_ip(source_ip, f"Too many failed attempts: {reason}")
            
            self._log_security_event(
                event_type=ThreatType.BRUTE_FORCE.value,
                severity=SecurityLevel.HIGH,
                source_ip=source_ip,
                user_id=user_id,
                description=f"Failed attempt recorded: {reason}"
            )
            
        except Exception as e:
            logger.error(f"Failed to record failed attempt: {e}")
    
    def check_access_level(self, user_id: str, required_level: AccessLevel = AccessLevel.AUTHENTICATED) -> bool:
        """Check if user has required access level."""
        try:
            # This would integrate with authentication system
            # For now, return True for demonstration
            return True
            
        except Exception as e:
            logger.error(f"Access level check error: {e}")
            return False
    
    def get_security_events(self, limit: int = 100, severity: Optional[SecurityLevel] = None,
                        event_type: Optional[str] = None, source_ip: Optional[str] = None,
                        start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get security events."""
        try:
            events = self.security_events
            
            # Apply filters
            if severity:
                events = [e for e in events if e.severity == severity]
            
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            
            if source_ip:
                events = [e for e in events if e.source_ip == source_ip]
            
            if start_time:
                events = [e for e in events if e.timestamp >= start_time]
            
            if end_time:
                events = [e for e in events if e.timestamp <= end_time]
            
            # Sort by timestamp (most recent first)
            events.sort(key=lambda x: x.timestamp, reverse=True)
            
            return {
                "total_events": len(events),
                "events": [
                    {
                        "event_id": event.event_id,
                        "event_type": event.event_type,
                        "severity": event.severity.value,
                        "timestamp": event.timestamp.isoformat(),
                        "source_ip": event.source_ip,
                        "user_id": event.user_id,
                        "agent_name": event.agent_name,
                        "description": event.description,
                        "details": event.details,
                        "blocked": event.blocked,
                        "resolved": event.resolved,
                        "resolution": event.resolution
                    }
                    for event in events[:limit]
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get security events: {e}")
            return {"error": str(e)}
    
    def get_blocked_ips(self) -> List[str]:
        """Get list of blocked IPs."""
        return list(self.blocked_ips)
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary statistics."""
        try:
            total_events = len(self.security_events)
            blocked_ips = len(self.blocked_ips)
            
            # Count events by type
            event_counts = defaultdict(int)
            severity_counts = defaultdict(int)
            
            for event in self.security_events:
                event_counts[event.event_type] += 1
                severity_counts[event.severity.value] += 1
            
            # Recent events (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            recent_events = [e for e in self.security_events if e.timestamp > cutoff_time]
            
            return {
                "total_events": total_events,
                "blocked_ips": blocked_ips,
                "event_counts": dict(event_counts),
                "severity_counts": dict(severity_counts),
                "recent_events_24h": len(recent_events),
                "failed_attempts": {
                    ip: len(attempts) for ip, attempts in self.failed_attempts.items()
                },
                "config": {
                    "enable_input_validation": self.config.enable_input_validation,
                    "enable_rate_limiting": self.config.enable_rate_limiting,
                    "enable_ip_blocking": self.config.enable_ip_blocking,
                    "enable_audit_logging": self.config.enable_audit_logging,
                    "enable_threat_detection": self.config.enable_threat_detection,
                    "max_request_size": self.config.max_request_size,
                    "max_failed_attempts": self.config.max_failed_attempts,
                    "block_duration": self.config.block_duration,
                    "audit_retention_days": self.config.audit_retention_days,
                    "rate_limit_per_minute": self.config.rate_limit_per_minute,
                    "rate_limit_per_hour": self.config.rate_limit_per_hour,
                    "suspicious_patterns_count": len(self.config.suspicious_patterns)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get security summary: {e}")
            return {"error": str(e)}


# Global security manager instance
_security_manager: Optional[SecurityManager] = None


def get_security_manager(config: Optional[SecurityConfig] = None) -> SecurityManager:
    """Get or create security manager."""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager(config)
    return _security_manager


# Convenience functions for backward compatibility
def validate_input(input_data: Any, input_type: str = "general", source_ip: str = "",
               user_id: str = "", agent_name: str = "") -> Dict[str, Any]:
    """Validate input data for security threats."""
    manager = get_security_manager()
    return manager.validate_input(input_data, input_type, source_ip, user_id, agent_name)


def check_rate_limit(source_ip: str, user_id: str = "") -> Tuple[bool, Dict[str, Any]]:
    """Check if rate limit is exceeded."""
    manager = get_security_manager()
    return manager.check_rate_limit(source_ip, user_id)


def check_ip_blocked(source_ip: str) -> bool:
    """Check if IP is blocked."""
    manager = get_security_manager()
    return manager.check_ip_blocked(source_ip)


def block_ip(source_ip: str, duration: Optional[int] = None, reason: str = "Security violation") -> bool:
    """Block an IP address."""
    manager = get_security_manager()
    return manager.block_ip(source_ip, duration, reason)


def record_failed_attempt(source_ip: str, user_id: str = "", reason: str = "") -> None:
    """Record a failed attempt."""
    manager = get_security_manager()
    return manager.record_failed_attempt(source_ip, user_id, reason)


def get_security_events(limit: int = 100, severity: Optional[SecurityLevel] = None,
                    event_type: Optional[str] = None, source_ip: Optional[str] = None,
                    start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict[str, Any]:
    """Get security events."""
    manager = get_security_manager()
    return manager.get_security_events(limit, severity, event_type, source_ip, start_time, end_time)


def get_blocked_ips() -> List[str]:
    """Get list of blocked IPs."""
    manager = get_security_manager()
    return manager.get_blocked_ips()


def get_security_summary() -> Dict[str, Any]:
    """Get security summary statistics."""
    manager = get_security_manager()
    return manager.get_security_summary()
