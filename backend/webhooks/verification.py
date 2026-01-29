"""
Webhook verification for Raptorflow.

Provides signature verification and validation for incoming
webhooks from external services like Supabase, Stripe, and PhonePe.
"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from infrastructure.cloud_monitoring import get_cloud_monitoring
from infrastructure.logging import get_cloud_logging

from .models import WebhookConfig, WebhookSignature

logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """Result of webhook verification."""

    valid: bool
    error: Optional[str] = None
    signature_matched: bool = False
    timestamp_valid: bool = True
    replay_detected: bool = False


class WebhookVerifier:
    """Webhook signature verifier for external integrations."""

    def __init__(self):
        self.logger = logging.getLogger("webhook_verifier")
        self.logging = get_cloud_logging()
        self.monitoring = get_cloud_monitoring()

        # Cache for recent webhook timestamps to prevent replay attacks
        self.replay_cache: Dict[str, datetime] = {}

        # Cache cleanup interval
        self.cache_cleanup_interval = timedelta(hours=1)
        self.last_cache_cleanup = datetime.utcnow()

    async def verify_signature(
        self, source: str, headers: Dict[str, str], body: bytes, config: WebhookConfig
    ) -> bool:
        """Verify webhook signature based on source."""
        try:
            # Clean up replay cache if needed
            await self._cleanup_replay_cache()

            # Verify based on source
            if source == "supabase":
                return await self._verify_supabase_signature(headers, body, config)
            elif source == "stripe":
                return await self._verify_stripe_signature(headers, body, config)
            elif source == "phonepe":
                return await self._verify_phonepe_signature(headers, body, config)
            else:
                self.logger.warning(f"Unknown webhook source: {source}")
                return False

        except Exception as e:
            self.logger.error(f"Webhook signature verification failed: {e}")
            return False

    async def verify_signature_detailed(
        self, source: str, headers: Dict[str, str], body: bytes, config: WebhookConfig
    ) -> VerificationResult:
        """Verify webhook signature with detailed result."""
        try:
            # Clean up replay cache if needed
            await self._cleanup_replay_cache()

            # Verify based on source
            if source == "supabase":
                return await self._verify_supabase_signature_detailed(
                    headers, body, config
                )
            elif source == "stripe":
                return await self._verify_stripe_signature_detailed(
                    headers, body, config
                )
            elif source == "phonepe":
                return await self._verify_phonepe_signature_detailed(
                    headers, body, config
                )
            else:
                return VerificationResult(
                    valid=False, error=f"Unknown webhook source: {source}"
                )

        except Exception as e:
            return VerificationResult(
                valid=False, error=f"Verification failed: {str(e)}"
            )

    async def _verify_supabase_signature(
        self, headers: Dict[str, str], body: bytes, config: WebhookConfig
    ) -> bool:
        """Verify Supabase webhook signature."""
        try:
            # Get signature from headers
            signature_header = headers.get("x-supabase-signature")
            if not signature_header:
                self.logger.error("Missing Supabase signature header")
                return False

            # Parse signature (format: "t=timestamp,v1=signature")
            parts = signature_header.split(",")
            timestamp = None
            signature = None

            for part in parts:
                if part.startswith("t="):
                    timestamp = int(part[2:])
                elif part.startswith("v1="):
                    signature = part[3:]

            if not timestamp or not signature:
                self.logger.error("Invalid Supabase signature format")
                return False

            # Check timestamp (prevent replay attacks)
            webhook_time = datetime.fromtimestamp(timestamp)
            current_time = datetime.utcnow()

            if abs((current_time - webhook_time).total_seconds()) > 300:  # 5 minutes
                self.logger.error("Supabase webhook timestamp too old")
                return False

            # Check for replay
            replay_key = f"supabase:{timestamp}:{hashlib.sha256(body).hexdigest()}"
            if replay_key in self.replay_cache:
                self.logger.error("Supabase webhook replay detected")
                return False

            # Add to replay cache
            self.replay_cache[replay_key] = webhook_time

            # Verify signature
            secret = config.secret_key.encode("utf-8")
            expected_signature = hmac.new(
                secret, f"{timestamp}.".encode("utf-8") + body, hashlib.sha256
            ).hexdigest()

            is_valid = hmac.compare_digest(signature, expected_signature)

            if not is_valid:
                self.logger.error("Supabase webhook signature mismatch")

            return is_valid

        except Exception as e:
            self.logger.error(f"Supabase signature verification failed: {e}")
            return False

    async def _verify_supabase_signature_detailed(
        self, headers: Dict[str, str], body: bytes, config: WebhookConfig
    ) -> VerificationResult:
        """Verify Supabase webhook signature with detailed result."""
        try:
            # Get signature from headers
            signature_header = headers.get("x-supabase-signature")
            if not signature_header:
                return VerificationResult(
                    valid=False, error="Missing Supabase signature header"
                )

            # Parse signature
            parts = signature_header.split(",")
            timestamp = None
            signature = None

            for part in parts:
                if part.startswith("t="):
                    timestamp = int(part[2:])
                elif part.startswith("v1="):
                    signature = part[3:]

            if not timestamp or not signature:
                return VerificationResult(
                    valid=False, error="Invalid Supabase signature format"
                )

            # Check timestamp
            webhook_time = datetime.fromtimestamp(timestamp)
            current_time = datetime.utcnow()
            timestamp_valid = abs((current_time - webhook_time).total_seconds()) <= 300

            if not timestamp_valid:
                return VerificationResult(
                    valid=False,
                    error="Webhook timestamp too old",
                    timestamp_valid=False,
                )

            # Check for replay
            replay_key = f"supabase:{timestamp}:{hashlib.sha256(body).hexdigest()}"
            replay_detected = replay_key in self.replay_cache

            if replay_detected:
                return VerificationResult(
                    valid=False,
                    error="Webhook replay detected",
                    timestamp_valid=True,
                    replay_detected=True,
                )

            # Add to replay cache
            self.replay_cache[replay_key] = webhook_time

            # Verify signature
            secret = config.secret_key.encode("utf-8")
            expected_signature = hmac.new(
                secret, f"{timestamp}.".encode("utf-8") + body, hashlib.sha256
            ).hexdigest()

            signature_matched = hmac.compare_digest(signature, expected_signature)

            return VerificationResult(
                valid=signature_matched,
                signature_matched=signature_matched,
                timestamp_valid=True,
                replay_detected=False,
            )

        except Exception as e:
            return VerificationResult(
                valid=False, error=f"Verification failed: {str(e)}"
            )

    async def _verify_stripe_signature(
        self, headers: Dict[str, str], body: bytes, config: WebhookConfig
    ) -> bool:
        """Verify Stripe webhook signature."""
        try:
            # Get signature from headers
            signature_header = headers.get("stripe-signature")
            if not signature_header:
                self.logger.error("Missing Stripe signature header")
                return False

            # Parse signature (format: "t=timestamp,v1=signature")
            parts = signature_header.split(",")
            timestamp = None
            signature = None

            for part in parts:
                if part.startswith("t="):
                    timestamp = int(part[2:])
                elif part.startswith("v1="):
                    signature = part[3:]

            if not timestamp or not signature:
                self.logger.error("Invalid Stripe signature format")
                return False

            # Check timestamp (prevent replay attacks)
            webhook_time = datetime.fromtimestamp(timestamp)
            current_time = datetime.utcnow()

            if abs((current_time - webhook_time).total_seconds()) > 300:  # 5 minutes
                self.logger.error("Stripe webhook timestamp too old")
                return False

            # Check for replay
            replay_key = f"stripe:{timestamp}:{hashlib.sha256(body).hexdigest()}"
            if replay_key in self.replay_cache:
                self.logger.error("Stripe webhook replay detected")
                return False

            # Add to replay cache
            self.replay_cache[replay_key] = webhook_time

            # Verify signature
            secret = config.secret_key.encode("utf-8")
            expected_signature = hmac.new(
                secret, f"{timestamp}.".encode("utf-8") + body, hashlib.sha256
            ).hexdigest()

            is_valid = hmac.compare_digest(signature, expected_signature)

            if not is_valid:
                self.logger.error("Stripe webhook signature mismatch")

            return is_valid

        except Exception as e:
            self.logger.error(f"Stripe signature verification failed: {e}")
            return False

    async def _verify_stripe_signature_detailed(
        self, headers: Dict[str, str], body: bytes, config: WebhookConfig
    ) -> VerificationResult:
        """Verify Stripe webhook signature with detailed result."""
        try:
            # Get signature from headers
            signature_header = headers.get("stripe-signature")
            if not signature_header:
                return VerificationResult(
                    valid=False, error="Missing Stripe signature header"
                )

            # Parse signature
            parts = signature_header.split(",")
            timestamp = None
            signature = None

            for part in parts:
                if part.startswith("t="):
                    timestamp = int(part[2:])
                elif part.startswith("v1="):
                    signature = part[3:]

            if not timestamp or not signature:
                return VerificationResult(
                    valid=False, error="Invalid Stripe signature format"
                )

            # Check timestamp
            webhook_time = datetime.fromtimestamp(timestamp)
            current_time = datetime.utcnow()
            timestamp_valid = abs((current_time - webhook_time).total_seconds()) <= 300

            if not timestamp_valid:
                return VerificationResult(
                    valid=False,
                    error="Webhook timestamp too old",
                    timestamp_valid=False,
                )

            # Check for replay
            replay_key = f"stripe:{timestamp}:{hashlib.sha256(body).hexdigest()}"
            replay_detected = replay_key in self.replay_cache

            if replay_detected:
                return VerificationResult(
                    valid=False,
                    error="Webhook replay detected",
                    timestamp_valid=True,
                    replay_detected=True,
                )

            # Add to replay cache
            self.replay_cache[replay_key] = webhook_time

            # Verify signature
            secret = config.secret_key.encode("utf-8")
            expected_signature = hmac.new(
                secret, f"{timestamp}.".encode("utf-8") + body, hashlib.sha256
            ).hexdigest()

            signature_matched = hmac.compare_digest(signature, expected_signature)

            return VerificationResult(
                valid=signature_matched,
                signature_matched=signature_matched,
                timestamp_valid=True,
                replay_detected=False,
            )

        except Exception as e:
            return VerificationResult(
                valid=False, error=f"Verification failed: {str(e)}"
            )

    async def _verify_phonepe_signature(
        self, headers: Dict[str, str], body: bytes, config: WebhookConfig
    ) -> bool:
        """Verify PhonePe webhook signature."""
        try:
            # Get signature from headers
            signature_header = headers.get("x-verify")
            if not signature_header:
                self.logger.error("Missing PhonePe signature header")
                return False

            # PhonePe uses SHA256 with base64 encoding
            try:
                signature = base64.b64decode(signature_header)
            except Exception:
                self.logger.error("Invalid PhonePe signature base64 encoding")
                return False

            # Get checksum from headers (optional)
            checksum_header = headers.get("x-checksum")

            # Verify signature
            secret = config.secret_key.encode("utf-8")

            if checksum_header:
                # Verify with checksum
                expected_signature = hmac.new(
                    secret, checksum_header.encode("utf-8"), hashlib.sha256
                ).digest()
            else:
                # Verify with body
                expected_signature = hmac.new(secret, body, hashlib.sha256).digest()

            is_valid = hmac.compare_digest(signature, expected_signature)

            if not is_valid:
                self.logger.error("PhonePe webhook signature mismatch")

            return is_valid

        except Exception as e:
            self.logger.error(f"PhonePe signature verification failed: {e}")
            return False

    async def _verify_phonepe_signature_detailed(
        self, headers: Dict[str, str], body: bytes, config: WebhookConfig
    ) -> VerificationResult:
        """Verify PhonePe webhook signature with detailed result."""
        try:
            # Get signature from headers
            signature_header = headers.get("x-verify")
            if not signature_header:
                return VerificationResult(
                    valid=False, error="Missing PhonePe signature header"
                )

            # Decode signature
            try:
                signature = base64.b64decode(signature_header)
            except Exception:
                return VerificationResult(
                    valid=False, error="Invalid PhonePe signature base64 encoding"
                )

            # Get checksum from headers
            checksum_header = headers.get("x-checksum")

            # Verify signature
            secret = config.secret_key.encode("utf-8")

            if checksum_header:
                expected_signature = hmac.new(
                    secret, checksum_header.encode("utf-8"), hashlib.sha256
                ).digest()
            else:
                expected_signature = hmac.new(secret, body, hashlib.sha256).digest()

            signature_matched = hmac.compare_digest(signature, expected_signature)

            return VerificationResult(
                valid=signature_matched,
                signature_matched=signature_matched,
                timestamp_valid=True,  # PhonePe doesn't use timestamps
                replay_detected=False,
            )

        except Exception as e:
            return VerificationResult(
                valid=False, error=f"Verification failed: {str(e)}"
            )

    async def _cleanup_replay_cache(self):
        """Clean up old entries from replay cache."""
        current_time = datetime.utcnow()

        if current_time - self.last_cache_cleanup < self.cache_cleanup_interval:
            return

        # Remove entries older than 1 hour
        cutoff_time = current_time - timedelta(hours=1)

        keys_to_remove = [
            key
            for key, timestamp in self.replay_cache.items()
            if timestamp < cutoff_time
        ]

        for key in keys_to_remove:
            del self.replay_cache[key]

        self.last_cache_cleanup = current_time

        if keys_to_remove:
            self.logger.info(
                f"Cleaned up {len(keys_to_remove)} old replay cache entries"
            )

    def generate_test_signature(
        self, source: str, body: bytes, secret: str, timestamp: Optional[int] = None
    ) -> str:
        """Generate test signature for webhook testing."""
        if timestamp is None:
            timestamp = int(datetime.utcnow().timestamp())

        if source in ["supabase", "stripe"]:
            # Generate HMAC signature
            secret_bytes = secret.encode("utf-8")
            message = f"{timestamp}.".encode("utf-8") + body
            signature = hmac.new(secret_bytes, message, hashlib.sha256).hexdigest()

            return f"t={timestamp},v1={signature}"

        elif source == "phonepe":
            # Generate SHA256 signature with base64 encoding
            secret_bytes = secret.encode("utf-8")
            signature = hmac.new(secret_bytes, body, hashlib.sha256).digest()
            signature_b64 = base64.b64encode(signature).decode("utf-8")

            return signature_b64

        else:
            raise ValueError(f"Unknown webhook source: {source}")

    async def validate_webhook_config(
        self, config: WebhookConfig
    ) -> VerificationResult:
        """Validate webhook configuration."""
        try:
            # Check required fields
            if not config.source:
                return VerificationResult(
                    valid=False, error="Missing source in webhook config"
                )

            if not config.secret_key:
                return VerificationResult(
                    valid=False, error="Missing secret key in webhook config"
                )

            # Validate source-specific requirements
            if config.source in ["supabase", "stripe"]:
                # These sources require timestamp-based signatures
                if not config.retry_config:
                    return VerificationResult(
                        valid=False,
                        error="Missing retry config for timestamp-based webhook",
                    )

            # Test signature generation
            test_body = b'{"test": "webhook"}'
            test_signature = self.generate_test_signature(
                config.source, test_body, config.secret_key
            )

            if not test_signature:
                return VerificationResult(
                    valid=False, error="Failed to generate test signature"
                )

            return VerificationResult(valid=True, signature_matched=True)

        except Exception as e:
            return VerificationResult(
                valid=False, error=f"Config validation failed: {str(e)}"
            )

    def get_replay_cache_stats(self) -> Dict[str, Any]:
        """Get replay cache statistics."""
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(hours=1)

        recent_entries = sum(
            1 for timestamp in self.replay_cache.values() if timestamp >= cutoff_time
        )

        return {
            "total_entries": len(self.replay_cache),
            "recent_entries": recent_entries,
            "last_cleanup": self.last_cache_cleanup.isoformat(),
            "cache_age_minutes": (
                current_time - self.last_cache_cleanup
            ).total_seconds()
            / 60,
        }


# Global webhook verifier instance
_webhook_verifier: Optional[WebhookVerifier] = None


def get_webhook_verifier() -> WebhookVerifier:
    """Get the global webhook verifier instance."""
    global _webhook_verifier
    if _webhook_verifier is None:
        _webhook_verifier = WebhookVerifier()
    return _webhook_verifier


# Export all components
__all__ = ["WebhookVerifier", "VerificationResult", "get_webhook_verifier"]
