"""
CRITICAL FIXES for Redis Infrastructure Security Issues

IMMEDIATE ACTION REQUIRED - These fixes address critical vulnerabilities
identified in final red team analysis.
"""

import hashlib
import hmac
import os
import re
import secrets
from typing import Any, Dict, List, Optional


# CRITICAL FIX 1: Job Payload Validation
class JobPayloadValidator:
    """Validates job payloads to prevent code execution and data corruption."""

    def __init__(self):
        self.max_payload_size = 1024 * 1024  # 1MB
        self.allowed_characters = re.compile(r'^[a-zA-Z0-9\s\-_.:,()\'"/]+$')
        self.dangerous_patterns = [
            r"__import__",
            r"eval\s*\(",
            r"exec\s*\(",
            r"open\s*\(",
            r"file\s*\(",
            r"subprocess",
            r"os\.system",
            r"pickle",
            r"marshal",
            r"base64",
        ]

    def validate_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize job payload."""
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary")

        # Size check
        payload_str = str(payload)
        if len(payload_str) > self.max_payload_size:
            raise ValueError(f"Payload too large: {len(payload_str)} bytes")

        # Content validation
        self._check_dangerous_content(payload_str)

        # Recursive validation
        return self._validate_dict(payload)

    def _check_dangerous_content(self, content: str):
        """Check for dangerous patterns in content."""
        for pattern in self.dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                raise ValueError(f"Dangerous content detected: {pattern}")

    def _validate_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively validate dictionary."""
        validated = {}
        for key, value in data.items():
            # Key validation
            if not isinstance(key, str) or len(key) > 256:
                raise ValueError("Invalid key format")

            if not self.allowed_characters.match(key):
                raise ValueError(f"Invalid characters in key: {key}")

            # Value validation
            validated_value = self._validate_value(value)
            validated[key] = validated_value

        return validated

    def _validate_value(self, value: Any) -> Any:
        """Validate individual value."""
        if isinstance(value, str):
            if len(value) > 10000:  # 10KB max per string
                raise ValueError("String value too large")
            if not self.allowed_characters.match(value):
                raise ValueError("Invalid characters in string value")
            return value
        elif isinstance(value, (int, float, bool)):
            return value
        elif isinstance(value, list):
            if len(value) > 1000:  # Max 1000 items
                raise ValueError("List too large")
            return [self._validate_value(item) for item in value]
        elif isinstance(value, dict):
            return self._validate_dict(value)
        elif value is None:
            return None
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")


# CRITICAL FIX 2: Rate Limiting Validation
class RateLimitValidator:
    """Validates rate limit configurations to prevent bypass."""

    def __init__(self):
        self.max_requests_per_minute = 1000
        self.max_requests_per_hour = 10000
        self.max_burst_size = 100

    def validate_rate_limit_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate rate limiting configuration."""
        if not isinstance(config, dict):
            raise ValueError("Rate limit config must be a dictionary")

        # Validate limits
        requests_per_minute = config.get("requests_per_minute", 60)
        requests_per_hour = config.get("requests_per_hour", 1000)
        burst_size = config.get("burst_size", 10)

        if requests_per_minute > self.max_requests_per_minute:
            raise ValueError(f"Requests per minute too high: {requests_per_minute}")

        if requests_per_hour > self.max_requests_per_hour:
            raise ValueError(f"Requests per hour too high: {requests_per_hour}")

        if burst_size > self.max_burst_size:
            raise ValueError(f"Burst size too high: {burst_size}")

        return {
            "requests_per_minute": min(
                requests_per_minute, self.max_requests_per_minute
            ),
            "requests_per_hour": min(requests_per_hour, self.max_requests_per_hour),
            "burst_size": min(burst_size, self.max_burst_size),
        }


# CRITICAL FIX 3: Session Security
class SessionValidator:
    """Validates session data to prevent session hijacking."""

    def __init__(self):
        self.session_timeout = 3600  # 1 hour
        self.max_sessions_per_user = 10
        self.required_fields = ["user_id", "workspace_id", "created_at"]

    def validate_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate session data."""
        if not isinstance(session_data, dict):
            raise ValueError("Session data must be a dictionary")

        # Check required fields
        for field in self.required_fields:
            if field not in session_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate session timeout
        created_at = session_data.get("created_at")
        if isinstance(created_at, str):
            try:
                from datetime import datetime

                created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                from datetime import datetime, timezone

                if (
                    datetime.now(timezone.utc) - created_dt
                ).seconds > self.session_timeout:
                    raise ValueError("Session expired")
            except ValueError:
                raise ValueError("Invalid created_at format")

        # Sanitize session data
        return self._sanitize_session_data(session_data)

    def _sanitize_session_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from session."""
        sensitive_fields = ["password", "token", "secret", "key"]
        sanitized = data.copy()

        for field in sensitive_fields:
            if field in sanitized:
                del sanitized[field]

        return sanitized


# CRITICAL FIX 4: Cache Key Validation
class CacheKeyValidator:
    """Validates cache keys to prevent cache poisoning."""

    def __init__(self):
        self.max_key_length = 256
        self.allowed_key_pattern = re.compile(r"^[a-zA-Z0-9_\-:]+$")

    def validate_cache_key(self, key: str) -> str:
        """Validate cache key."""
        if not isinstance(key, str):
            raise ValueError("Cache key must be a string")

        if len(key) > self.max_key_length:
            raise ValueError(f"Cache key too long: {len(key)}")

        if not self.allowed_key_pattern.match(key):
            raise ValueError(f"Invalid cache key format: {key}")

        # Prevent path traversal
        if ".." in key or key.startswith("/"):
            raise ValueError("Invalid cache key path")

        return key


# CRITICAL FIX 5: Usage Data Validation
class UsageDataValidator:
    """Validates usage tracking data to prevent fraud."""

    def __init__(self):
        self.max_usage_events_per_request = 100
        self.allowed_event_types = ["api_call", "storage", "compute", "network"]

    def validate_usage_data(self, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate usage tracking data."""
        if not isinstance(usage_data, dict):
            raise ValueError("Usage data must be a dictionary")

        # Validate events
        events = usage_data.get("events", [])
        if len(events) > self.max_usage_events_per_request:
            raise ValueError(f"Too many usage events: {len(events)}")

        validated_events = []
        for event in events:
            validated_event = self._validate_usage_event(event)
            validated_events.append(validated_event)

        return {**usage_data, "events": validated_events}

    def _validate_usage_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual usage event."""
        if not isinstance(event, dict):
            raise ValueError("Usage event must be a dictionary")

        event_type = event.get("type")
        if event_type not in self.allowed_event_types:
            raise ValueError(f"Invalid event type: {event_type}")

        # Validate quantities
        quantity = event.get("quantity", 0)
        if not isinstance(quantity, (int, float)) or quantity < 0:
            raise ValueError("Invalid quantity value")

        return {
            "type": event_type,
            "quantity": quantity,
            "timestamp": event.get("timestamp"),
            "metadata": event.get("metadata", {}),
        }


# Security Event Logger
class SecurityEventLogger:
    """Logs security events for monitoring."""

    def __init__(self):
        self.log_level = os.getenv("SECURITY_LOG_LEVEL", "INFO")

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event."""
        event = {
            "event_type": event_type,
            "timestamp": str(datetime.now()),
            "details": details,
            "severity": self._get_event_severity(event_type),
        }

        # In production, send to security monitoring system
        print(f"SECURITY EVENT: {event}")

    def _get_event_severity(self, event_type: str) -> str:
        """Determine event severity."""
        high_severity_events = [
            "payload_validation_failed",
            "rate_limit_exceeded",
            "session_hijack_attempt",
            "cache_pollution_attempt",
            "usage_fraud_detected",
        ]

        return "HIGH" if event_type in high_severity_events else "MEDIUM"
