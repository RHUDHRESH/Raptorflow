"""
Webhook Security Manager
Implements comprehensive webhook security with nonce validation, timestamp checking, and replay attack prevention
Addresses critical webhook security vulnerabilities identified in red team audit
"""

import hashlib
import hmac
import json
import logging
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

import redis
from core.supabase_mgr import get_supabase_admin


class WebhookSecurityError(Exception):
    """Webhook security error"""

    def __init__(
        self, message: str, error_type: str, context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_type = error_type
        self.context = context or {}
        super().__init__(message)


class WebhookSecurityManager:
    """
    Comprehensive webhook security manager
    Implements nonce validation, timestamp checking, and replay attack prevention
    """

    def __init__(self):
        """Initialize webhook security manager"""
        self.logger = logging.getLogger(__name__)
        self.supabase = get_supabase_admin()

        # Security configuration
        self.NONCE_EXPIRY = 300  # 5 minutes
        self.TIMESTAMP_TOLERANCE = 300  # 5 minutes
        self.MAX_WEBHOOK_SIZE = 1024 * 1024  # 1MB

        # Redis connection for nonce tracking
        try:
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
                decode_responses=True,
            )
            self.redis_client.ping()
            self.logger.info("Webhook security manager initialized with Redis")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    def validate_webhook(
        self, webhook_data: Dict[str, Any], signature: str, salt_key: str
    ) -> bool:
        """
        Validate webhook with comprehensive security checks
        """
        try:
            # 1. Basic validation
            self._validate_basic_webhook(webhook_data)

            # 2. Size validation
            self._validate_webhook_size(webhook_data)

            # 3. Timestamp validation
            self._validate_timestamp(webhook_data)

            # 4. Nonce validation (replay attack prevention)
            self._validate_nonce(webhook_data)

            # 5. Signature validation
            self._validate_signature(webhook_data, signature, salt_key)

            # 6. Store nonce for replay protection
            self._store_nonce(webhook_data)

            self.logger.info("Webhook validation passed")
            return True

        except WebhookSecurityError:
            raise
        except Exception as e:
            self.logger.error(f"Webhook validation failed: {str(e)}")
            raise WebhookSecurityError(
                "Webhook validation failed",
                "VALIDATION_FAILED",
                {"original_error": str(e)},
            )

    def _validate_basic_webhook(self, webhook_data: Dict[str, Any]):
        """Validate basic webhook structure"""
        required_fields = ["merchantTransactionId", "code", "data"]

        for field in required_fields:
            if field not in webhook_data:
                raise WebhookSecurityError(
                    f"Missing required field: {field}", "MISSING_FIELD"
                )

        # Validate merchantTransactionId format
        merchant_id = webhook_data["merchantTransactionId"]
        if not isinstance(merchant_id, str) or len(merchant_id) < 8:
            raise WebhookSecurityError(
                "Invalid merchantTransactionId format", "INVALID_TRANSACTION_ID"
            )

        # Validate webhook code
        valid_codes = ["PAYMENT_SUCCESS", "PAYMENT_FAILED", "PAYMENT_PENDING"]
        if webhook_data["code"] not in valid_codes:
            raise WebhookSecurityError(
                f"Invalid webhook code: {webhook_data['code']}", "INVALID_WEBHOOK_CODE"
            )

    def _validate_webhook_size(self, webhook_data: Dict[str, Any]):
        """Validate webhook size to prevent DoS attacks"""
        webhook_json = json.dumps(webhook_data)
        webhook_size = len(webhook_json.encode("utf-8"))

        if webhook_size > self.MAX_WEBHOOK_SIZE:
            raise WebhookSecurityError(
                f"Webhook size exceeds limit: {webhook_size} bytes", "WEBHOOK_TOO_LARGE"
            )

    def _validate_timestamp(self, webhook_data: Dict[str, Any]):
        """Validate webhook timestamp to prevent replay attacks"""
        if "timestamp" not in webhook_data:
            raise WebhookSecurityError("Missing timestamp field", "MISSING_TIMESTAMP")

        try:
            webhook_timestamp = int(webhook_data["timestamp"])
            current_timestamp = int(time.time())

            # Check if timestamp is within tolerance
            time_diff = abs(current_timestamp - webhook_timestamp)

            if time_diff > self.TIMESTAMP_TOLERANCE:
                raise WebhookSecurityError(
                    f"Timestamp too old or too far in future: {time_diff} seconds",
                    "TIMESTAMP_OUT_OF_RANGE",
                )

        except (ValueError, TypeError):
            raise WebhookSecurityError(
                "Invalid timestamp format", "INVALID_TIMESTAMP_FORMAT"
            )

    def _validate_nonce(self, webhook_data: Dict[str, Any]):
        """Validate nonce to prevent replay attacks"""
        if not self.redis_client:
            # Fallback: skip nonce validation if Redis not available
            self.logger.warning("Redis not available, skipping nonce validation")
            return

        if "nonce" not in webhook_data:
            raise WebhookSecurityError("Missing nonce field", "MISSING_NONCE")

        nonce = webhook_data["nonce"]

        # Check if nonce has been used before
        nonce_key = f"webhook_nonce:{nonce}"

        try:
            if self.redis_client.exists(nonce_key):
                raise WebhookSecurityError(
                    f"Nonce already used: {nonce}", "NONCE_REUSE"
                )
        except redis.RedisError as e:
            self.logger.error(f"Redis error checking nonce: {e}")
            raise WebhookSecurityError(
                "Failed to validate nonce", "NONCE_VALIDATION_FAILED"
            )

    def _validate_signature(
        self, webhook_data: Dict[str, Any], signature: str, salt_key: str
    ):
        """Validate webhook signature"""
        if not signature:
            raise WebhookSecurityError("Missing signature", "MISSING_SIGNATURE")

        # Extract signature from header (format: "X-VERIFY <signature>")
        if signature.startswith("X-VERIFY "):
            signature = signature[9:]  # Remove "X-VERIFY " prefix

        # Generate expected signature
        payload_str = json.dumps(webhook_data, separators=(",", ":"), sort_keys=True)
        expected_signature = self._generate_sha256_checksum(f"{payload_str}{salt_key}")

        # Compare signatures
        if signature != expected_signature:
            raise WebhookSecurityError("Invalid webhook signature", "INVALID_SIGNATURE")

    def _store_nonce(self, webhook_data: Dict[str, Any]):
        """Store nonce for replay attack prevention"""
        if not self.redis_client:
            return  # Skip if Redis not available

        nonce = webhook_data["nonce"]
        nonce_key = f"webhook_nonce:{nonce}"

        try:
            # Store nonce with expiration
            self.redis_client.setex(nonce_key, self.NONCE_EXPIRY, "1")
        except redis.RedisError as e:
            self.logger.error(f"Failed to store nonce: {e}")
            # Don't fail the webhook if nonce storage fails

    def _generate_sha256_checksum(self, data: str) -> str:
        """Generate SHA256 checksum"""
        return hashlib.sha256(data.encode()).hexdigest()

    def generate_nonce(self) -> str:
        """Generate a unique nonce for webhook requests"""
        import uuid

        return str(uuid.uuid4())

    def add_security_headers(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add security headers to webhook data"""
        # Add timestamp if not present
        if "timestamp" not in webhook_data:
            webhook_data["timestamp"] = int(time.time())

        # Add nonce if not present
        if "nonce" not in webhook_data:
            webhook_data["nonce"] = self.generate_nonce()

        return webhook_data

    def cleanup_expired_nonces(self) -> int:
        """Clean up expired nonces from Redis"""
        if not self.redis_client:
            return 0

        try:
            # Find all nonce keys
            nonce_keys = self.redis_client.keys("webhook_nonce:*")

            if not nonce_keys:
                return 0

            # Check expiration and delete expired ones
            deleted_count = 0
            for key in nonce_keys:
                ttl = self.redis_client.ttl(key)
                if ttl == -1:  # No expiration set, delete it
                    self.redis_client.delete(key)
                    deleted_count += 1

            self.logger.info(f"Cleaned up {deleted_count} expired nonces")
            return deleted_count

        except redis.RedisError as e:
            self.logger.error(f"Failed to cleanup nonces: {e}")
            return 0

    def get_webhook_statistics(self) -> Dict[str, Any]:
        """Get webhook security statistics"""
        stats = {
            "nonce_validation_enabled": self.redis_client is not None,
            "max_webhook_size": self.MAX_WEBHOOK_SIZE,
            "timestamp_tolerance": self.TIMESTAMP_TOLERANCE,
            "nonce_expiry": self.NONCE_EXPIRY,
        }

        if self.redis_client:
            try:
                # Count active nonces
                nonce_keys = self.redis_client.keys("webhook_nonce:*")
                stats["active_nonces"] = len(nonce_keys) if nonce_keys else 0
            except redis.RedisError:
                stats["active_nonces"] = "error"

        return stats


# Global instance
webhook_security = WebhookSecurityManager()
