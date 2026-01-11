"""
Production-ready security utilities for RaptorFlow
Input sanitization, validation, and security helpers
"""

import hashlib
import html
import logging
import re
import secrets
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SecurityConfig:
    """Security configuration settings"""

    max_password_length: int = 128
    min_password_length: int = 8
    max_email_length: int = 254
    max_name_length: int = 100
    allowed_mime_types: List[str] = None

    def __post_init__(self):
        if self.allowed_mime_types is None:
            self.allowed_mime_types = [
                "text/plain",
                "text/html",
                "text/css",
                "text/javascript",
                "application/json",
                "application/pdf",
                "image/jpeg",
                "image/png",
                "image/gif",
                "image/webp",
            ]


class SecurityValidator:
    """Production-ready input validation and sanitization"""

    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()

        # Pre-compiled regex patterns for performance
        self.email_pattern = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        self.uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            re.IGNORECASE,
        )
        self.slug_pattern = re.compile(r"^[a-z0-9-]+$")
        self.dangerous_chars_pattern = re.compile(r'[<>"\'\x00-\x1f\x7f-\x9f]')

    def sanitize_input(self, text: str, allow_html: bool = False) -> str:
        """
        Sanitize user input to prevent XSS

        Args:
            text: Input text to sanitize
            allow_html: Whether to allow certain HTML tags

        Returns:
            Sanitized text
        """
        if not text or not isinstance(text, str):
            return ""

        # Remove null bytes and control characters
        text = "".join(char for char in text if ord(char) >= 32 or char in "\n\r\t")

        if not allow_html:
            # Escape HTML entities
            text = html.escape(text)

        # Remove dangerous patterns
        text = self.dangerous_chars_pattern.sub("", text)

        # Normalize whitespace
        text = " ".join(text.split())

        return text.strip()

    def validate_email(self, email: str) -> bool:
        """
        Validate email format with comprehensive checks

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False

        # Length check
        if len(email) > self.config.max_email_length:
            return False

        # Regex validation
        if not self.email_pattern.match(email):
            return False

        # Additional validation
        local, domain = email.rsplit("@", 1)

        # Local part validation
        if len(local) == 0 or len(local) > 64:
            return False

        # Domain validation
        if len(domain) == 0 or len(domain) > 253:
            return False

        # No consecutive dots
        if ".." in email:
            return False

        # No leading/trailing dots or hyphens
        if email.startswith(".") or email.endswith("."):
            return False
        if email.startswith("-") or email.endswith("-"):
            return False

        return True

    def validate_uuid(self, uuid_str: str) -> bool:
        """
        Validate UUID format

        Args:
            uuid_str: UUID string to validate

        Returns:
            True if valid, False otherwise
        """
        if not uuid_str or not isinstance(uuid_str, str):
            return False

        return bool(self.uuid_pattern.match(uuid_str))

    def validate_slug(self, slug: str) -> bool:
        """
        Validate slug format (URL-safe identifier)

        Args:
            slug: Slug string to validate

        Returns:
            True if valid, False otherwise
        """
        if not slug or not isinstance(slug, str):
            return False

        if len(slug) < 1 or len(slug) > 100:
            return False

        return bool(self.slug_pattern.match(slug))

    def validate_name(self, name: str) -> bool:
        """
        Validate person/organization name

        Args:
            name: Name string to validate

        Returns:
            True if valid, False otherwise
        """
        if not name or not isinstance(name, str):
            return False

        # Length check
        if len(name.strip()) < 1 or len(name) > self.config.max_name_length:
            return False

        # Check for dangerous characters
        if self.dangerous_chars_pattern.search(name):
            return False

        return True

    def sanitize_json_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively sanitize JSON input

        Args:
            data: Dictionary to sanitize

        Returns:
            Sanitized dictionary
        """
        if not isinstance(data, dict):
            return {}

        sanitized = {}
        for key, value in data.items():
            # Sanitize keys
            clean_key = self.sanitize_input(str(key))

            if isinstance(value, str):
                sanitized[clean_key] = self.sanitize_input(value)
            elif isinstance(value, dict):
                sanitized[clean_key] = self.sanitize_json_input(value)
            elif isinstance(value, list):
                sanitized[clean_key] = [
                    self.sanitize_input(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                sanitized[clean_key] = value

        return sanitized

    def hash_api_key(self, api_key: str) -> str:
        """
        Hash API key for secure storage

        Args:
            api_key: API key to hash

        Returns:
            Hashed API key
        """
        if not api_key:
            raise ValueError("API key cannot be empty")

        # Use SHA-256 with salt
        salt = secrets.token_hex(32)
        hashed = hashlib.sha256((salt + api_key).encode()).hexdigest()

        return f"{salt}:{hashed}"

    def verify_api_key(self, api_key: str, hashed_key: str) -> bool:
        """
        Verify API key against stored hash

        Args:
            api_key: API key to verify
            hashed_key: Stored hashed key

        Returns:
            True if valid, False otherwise
        """
        if not api_key or not hashed_key or ":" not in hashed_key:
            return False

        try:
            salt, stored_hash = hashed_key.split(":", 1)
            computed_hash = hashlib.sha256((salt + api_key).encode()).hexdigest()

            return secrets.compare_digest(computed_hash, stored_hash)
        except Exception as e:
            logger.error(f"Error verifying API key: {e}")
            return False

    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate cryptographically secure token

        Args:
            length: Token length in bytes

        Returns:
            Secure token string
        """
        return secrets.token_urlsafe(length)

    def validate_file_upload(self, filename: str, content_type: str, size: int) -> bool:
        """
        Validate file upload for security

        Args:
            filename: Original filename
            content_type: MIME type
            size: File size in bytes

        Returns:
            True if valid, False otherwise
        """
        # Check filename
        if not filename or ".." in filename or "/" in filename:
            return False

        # Check file extension
        allowed_extensions = {
            ".txt",
            ".pdf",
            ".doc",
            ".docx",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
        }
        file_ext = "." + filename.split(".")[-1].lower() if "." in filename else ""

        if file_ext not in allowed_extensions:
            return False

        # Check MIME type
        if content_type not in self.config.allowed_mime_types:
            return False

        # Check file size (10MB limit)
        if size > 10 * 1024 * 1024:
            return False

        return True


# Global validator instance
_security_validator: Optional[SecurityValidator] = None


def get_security_validator() -> SecurityValidator:
    """Get global security validator singleton"""
    global _security_validator
    if _security_validator is None:
        _security_validator = SecurityValidator()
    return _security_validator


# Convenience functions
def sanitize_input(text: str, allow_html: bool = False) -> str:
    """Sanitize user input"""
    return get_security_validator().sanitize_input(text, allow_html)


def validate_email(email: str) -> bool:
    """Validate email format"""
    return get_security_validator().validate_email(email)


def validate_uuid(uuid_str: str) -> bool:
    """Validate UUID format"""
    return get_security_validator().validate_uuid(uuid_str)


def hash_api_key(api_key: str) -> str:
    """Hash API key"""
    return get_security_validator().hash_api_key(api_key)


def generate_secure_token(length: int = 32) -> str:
    """Generate secure token"""
    return get_security_validator().generate_secure_token(length)
