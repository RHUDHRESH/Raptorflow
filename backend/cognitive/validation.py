"""
Input Validation and Sanitization with Pydantic
Prevents garbage input from breaking the system
"""

import html
import logging
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import bleach
from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator

logger = logging.getLogger(__name__)


class ProcessingPhase(str, Enum):
    """Valid processing phases"""

    PERCEPTION = "perception"
    PLANNING = "planning"
    EXECUTION = "execution"
    REFLECTION = "reflection"
    HUMAN_LOOP = "human_loop"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class UserRole(str, Enum):
    """Valid user roles"""

    REGULAR = "regular"
    PREMIUM = "premium"
    ADMIN = "admin"
    EXECUTIVE = "executive"


class ContentType(str, Enum):
    """Valid content types"""

    TEXT = "text"
    EMAIL = "email"
    REPORT = "report"
    SOCIAL_POST = "social_post"
    AD_COPY = "ad_copy"
    BLOG_POST = "blog_post"
    LEGAL_DOCUMENT = "legal_document"
    FINANCIAL_ANALYSIS = "financial_analysis"


class SanitizedString(str):
    """Custom string type with automatic sanitization"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str):
            raise ValueError("Must be a string")

        # Remove HTML tags
        clean_value = bleach.clean(value)

        # Escape HTML entities
        clean_value = html.escape(clean_value)

        # Remove potentially dangerous characters
        clean_value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", clean_value)

        # Length validation
        if len(clean_value) > 100000:  # 100KB limit
            raise ValueError("Content too long")

        return cls(clean_value)


class SafeDict(dict):
    """Dictionary with sanitized keys and values"""

    def __init__(self, data: Dict[str, Any]):
        sanitized = {}
        for key, value in data.items():
            # Sanitize key
            clean_key = re.sub(r"[^a-zA-Z0-9_]", "", str(key))
            if not clean_key:
                continue

            # Sanitize value based on type
            if isinstance(value, str):
                clean_value = SanitizedString.validate(value)
            elif isinstance(value, dict):
                clean_value = SafeDict(value)
            elif isinstance(value, list):
                clean_value = [
                    SanitizedString.validate(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                clean_value = value

            sanitized[clean_key] = clean_value

        super().__init__(sanitized)


class UserContext(BaseModel):
    """Validated user context"""

    user_id: str = Field(..., min_length=1, max_length=100)
    user_role: UserRole = Field(default=UserRole.REGULAR)
    workspace_id: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    preferences: SafeDict = Field(default_factory=SafeDict)
    subscription_tier: str = Field(
        default="free", regex="^(free|starter|growth|enterprise)$"
    )
    budget_limit: float = Field(default=100.0, ge=0, le=1000000)

    @validator("user_id", "workspace_id")
    def sanitize_ids(cls, v):
        """Sanitize ID fields"""
        return re.sub(r"[^a-zA-Z0-9_-]", "", v)


class ProcessingRequest(BaseModel):
    """Validated processing request"""

    request: SanitizedString = Field(..., min_length=1, max_length=50000)
    session_id: str = Field(..., min_length=1, max_length=100)
    workspace_id: str = Field(..., min_length=1, max_length=100)
    user_context: UserContext
    recent_messages: Optional[List[SafeDict]] = Field(default=None, max_items=50)
    auto_execute: Optional[bool] = Field(default=False)
    content_type: Optional[ContentType] = Field(default=ContentType.TEXT)
    priority: int = Field(default=5, ge=1, le=10)

    @validator("session_id", "workspace_id")
    def sanitize_ids(cls, v):
        """Sanitize ID fields"""
        return re.sub(r"[^a-zA-Z0-9_-]", "", v)

    @validator("recent_messages")
    def validate_recent_messages(cls, v):
        """Validate recent messages"""
        if v is None:
            return v
        if len(v) > 50:
            raise ValueError("Too many recent messages")
        return v


class ProcessingConfig(BaseModel):
    """Validated processing configuration"""

    enable_auto_execution: bool = Field(default=False)
    quality_threshold: int = Field(default=70, ge=0, le=100)
    enable_human_approval: bool = Field(default=True)
    max_processing_time_minutes: int = Field(default=30, ge=1, le=180)
    max_tokens_per_request: int = Field(default=10000, ge=100, le=100000)
    max_cost_per_request: float = Field(default=10.0, ge=0.01, le=1000)
    rate_limit_requests_per_minute: int = Field(default=60, ge=1, le=1000)
    concurrent_requests_limit: int = Field(default=10, ge=1, le=100)


class ValidationResult(BaseModel):
    """Validation result"""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    sanitized_data: Optional[Dict[str, Any]] = None


class InputValidator:
    """Advanced input validator with sanitization"""

    def __init__(self):
        self.forbidden_patterns = [
            r"<script[^>]*>.*?</script>",  # Scripts
            r"javascript:",  # JavaScript URLs
            r"on\w+\s*=",  # Event handlers
            r"expression\s*\(",  # CSS expressions
            r"@import",  # CSS imports
            r"union\s+select",  # SQL injection
            r"drop\s+table",  # SQL injection
            r"insert\s+into",  # SQL injection
        ]
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.forbidden_patterns
        ]

    def validate_request(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate and sanitize request data"""
        errors = []
        warnings = []
        sanitized_data = {}

        try:
            # Validate main structure
            request = ProcessingRequest(**data)
            sanitized_data = request.dict()

            # Additional security checks
            self._check_for_malicious_content(str(request.request), errors)
            self._check_user_permissions(request.user_context, warnings)

        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
            # Try to extract what we can
            sanitized_data = self._extract_safe_data(data)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_data=sanitized_data if errors == [] else None,
        )

    def validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """Validate configuration"""
        errors = []
        warnings = []
        sanitized_data = None

        try:
            validated_config = ProcessingConfig(**config)
            sanitized_data = validated_config.dict()

            # Check for potentially dangerous settings
            if validated_config.max_tokens_per_request > 50000:
                warnings.append("High token limit may be costly")

            if validated_config.max_cost_per_request > 100:
                warnings.append("High cost limit may be expensive")

            if validated_config.concurrent_requests_limit > 50:
                warnings.append("High concurrency may impact performance")

        except Exception as e:
            errors.append(f"Config validation error: {str(e)}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_data=sanitized_data,
        )

    def _check_for_malicious_content(self, content: str, errors: List[str]):
        """Check for malicious patterns"""
        for pattern in self.compiled_patterns:
            if pattern.search(content):
                errors.append(
                    f"Potentially malicious content detected: {pattern.pattern}"
                )

    def _check_user_permissions(self, user_context: UserContext, warnings: List[str]):
        """Check user permissions and limits"""
        if user_context.subscription_tier == "free":
            if user_context.budget_limit > 10:
                warnings.append("Free tier budget limit seems high")

        if user_context.user_role == UserRole.REGULAR:
            # Regular users have limitations
            pass

    def _extract_safe_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract safe data even if validation fails"""
        safe_data = {}

        # Extract string fields safely
        for field in ["request", "session_id", "workspace_id"]:
            if field in data and isinstance(data[field], str):
                safe_data[field] = SanitizedString.validate(data[field])[
                    :1000
                ]  # Limit length

        # Extract user context safely
        if "user_context" in data and isinstance(data["user_context"], dict):
            safe_data["user_context"] = SafeDict(data["user_context"])

        return safe_data

    def sanitize_text(self, text: str, max_length: int = 10000) -> str:
        """Quick text sanitization"""
        if not isinstance(text, str):
            return ""

        # Remove HTML
        clean_text = bleach.clean(text)

        # Escape HTML
        clean_text = html.escape(clean_text)

        # Remove dangerous chars
        clean_text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", clean_text)

        # Limit length
        if len(clean_text) > max_length:
            clean_text = clean_text[:max_length]

        return clean_text


# Global validator instance
validator = InputValidator()
