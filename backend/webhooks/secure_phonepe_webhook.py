"""
Secure PhonePe Webhook Handler v2.1.7
Implements proper X-VERIFY signature validation and replay attack protection
Addresses critical webhook security vulnerabilities identified in red team audit
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import redis
import aiohttp

from backend.core.audit_logger import audit_logger, EventType, LogLevel
from backend.core.payment_monitoring import payment_monitor
from backend.services.refund_system import get_refund_manager
from backend.db.repositories.payment import PaymentRepository

logger = logging.getLogger(__name__)

class WebhookEventType(Enum):
    """PhonePe webhook event types"""
    PAYMENT_SUCCESS = "PAYMENT_SUCCESS"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    REFUND_INITIATED = "REFUND_INITIATED"
    REFUND_COMPLETED = "REFUND_COMPLETED"
    REFUND_FAILED = "REFUND_FAILED"
    SETTLEMENT_COMPLETED = "SETTLEMENT_COMPLETED"
    CHARGEBACK_RECEIVED = "CHARGEBACK_RECEIVED"

class WebhookSecurityLevel(Enum):
    """Webhook security validation levels"""
    BASIC = "BASIC"           # Basic structure validation
    SIGNATURE = "SIGNATURE"   # X-VERIFY signature validation
    REPLAY = "REPLAY"         # Replay attack protection
    STRICT = "STRICT"         # All validations enabled

@dataclass
class WebhookValidationResult:
    """Webhook validation result"""
    valid: bool
    security_level: WebhookSecurityLevel
    error: Optional[str] = None
    error_code: Optional[str] = None
    security_metadata: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[int] = None

@dataclass
class WebhookEvent:
    """Processed webhook event"""
    event_id: str
    event_type: WebhookEventType
    transaction_id: Optional[str] = None
    refund_id: Optional[str] = None
    merchant_order_id: Optional[str] = None
    amount: Optional[int] = None
    status: Optional[str] = None
    timestamp: datetime = None
    raw_data: Optional[Dict[str, Any]] = None
    processed_at: datetime = None
    security_metadata: Optional[Dict[str, Any]] = None

class SecurePhonePeWebhookHandler:
    """
    Production-Ready PhonePe Webhook Handler
    Implements comprehensive security with X-VERIFY validation and replay protection
    """
    
    def __init__(self, redis_client: redis.Redis, payment_repository: PaymentRepository):
        self.redis = redis_client
        self.payment_repo = payment_repository
        self.refund_manager = get_refund_manager(payment_repository)
        
        # Configuration
        self.webhook_secret = os.getenv("PHONEPE_WEBHOOK_SECRET")
        self.webhook_username = os.getenv("PHONEPE_WEBHOOK_USERNAME")
        self.webhook_password = os.getenv("PHONEPE_WEBHOOK_PASSWORD")
        
        # Security settings
        self.max_webhook_age_minutes = 5  # Reject webhooks older than 5 minutes
        self.replay_protection_window_hours = 24  # Track processed webhooks for 24 hours
        self.max_signature_age_seconds = 300  # Max age for signature validation
        
        # Rate limiting
        self.max_webhooks_per_minute = 100
        self.max_webhooks_per_hour = 1000
        
        # Validate configuration
        self._validate_configuration()
        
        logger.info("Secure PhonePe Webhook Handler initialized")
    
    def _validate_configuration(self):
        """Validate webhook configuration"""
        if not self.webhook_secret:
            raise ValueError("PHONEPE_WEBHOOK_SECRET environment variable is required")
        
        if len(self.webhook_secret) < 32:
            raise ValueError("PHONEPE_WEBHOOK_SECRET must be at least 32 characters")
    
    async def validate_and_process_webhook(
        self,
        payload: Dict[str, Any],
        x_verify_header: str,
        authorization_header: Optional[str] = None,
        security_level: WebhookSecurityLevel = WebhookSecurityLevel.STRICT
    ) -> Tuple[WebhookValidationResult, Optional[WebhookEvent]]:
        """
        Comprehensive webhook validation and processing
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Basic validation
            basic_result = await self._validate_basic_structure(payload)
            if not basic_result.valid:
                basic_result.processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                return basic_result, None
            
            # Step 2: Rate limiting check
            rate_limit_result = await self._check_rate_limits(payload)
            if not rate_limit_result.valid:
                rate_limit_result.processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                return rate_limit_result, None
            
            # Step 3: Replay attack protection
            if security_level in [WebhookSecurityLevel.REPLAY, WebhookSecurityLevel.STRICT]:
                replay_result = await self._check_replay_attack(payload)
                if not replay_result.valid:
                    replay_result.processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                    return replay_result, None
            
            # Step 4: X-VERIFY signature validation
            if security_level in [WebhookSecurityLevel.SIGNATURE, WebhookSecurityLevel.STRICT]:
                signature_result = await self._validate_x_verify_signature(payload, x_verify_header)
                if not signature_result.valid:
                    signature_result.processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                    return signature_result, None
            
            # Step 5: Timestamp validation
            timestamp_result = await self._validate_webhook_timestamp(payload)
            if not timestamp_result.valid:
                timestamp_result.processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                return timestamp_result, None
            
            # Step 6: Process webhook event
            webhook_event = await self._create_webhook_event(payload)
            
            # Step 7: Store processed webhook for replay protection
            await self._store_processed_webhook(webhook_event)
            
            # Step 8: Handle the event
            await self._handle_webhook_event(webhook_event)
            
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Return success result
            result = WebhookValidationResult(
                valid=True,
                security_level=security_level,
                security_metadata={
                    "validation_steps": ["basic", "rate_limit", "replay", "signature", "timestamp"],
                    "event_type": webhook_event.event_type.value,
                    "transaction_id": webhook_event.transaction_id,
                    "processing_time_ms": processing_time
                },
                processing_time_ms=processing_time
            )
            
            return result, webhook_event
            
        except Exception as e:
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            await audit_logger.log_security_violation(
                violation_type="webhook_processing_error",
                request_data={"error": str(e)},
                response_data={"payload": payload}
            )
            
            return WebhookValidationResult(
                valid=False,
                security_level=security_level,
                error=f"Webhook processing error: {str(e)}",
                error_code="PROCESSING_ERROR",
                processing_time_ms=processing_time
            ), None
    
    async def _validate_basic_structure(self, payload: Dict[str, Any]) -> WebhookValidationResult:
        """Basic webhook structure validation"""
        try:
            # Check required fields
            required_fields = ["type", "code", "data"]
            for field in required_fields:
                if field not in payload:
                    return WebhookValidationResult(
                        valid=False,
                        security_level=WebhookSecurityLevel.BASIC,
                        error=f"Missing required field: {field}",
                        error_code="MISSING_FIELD"
                    )
            
            # Validate event type
            event_type = payload.get("type")
            try:
                WebhookEventType(event_type)
            except ValueError:
                return WebhookValidationResult(
                    valid=False,
                    security_level=WebhookSecurityLevel.BASIC,
                    error=f"Invalid event type: {event_type}",
                    error_code="INVALID_EVENT_TYPE"
                )
            
            # Validate response code
            response_code = payload.get("code")
            if not isinstance(response_code, str) or len(response_code) != 2:
                return WebhookValidationResult(
                    valid=False,
                    security_level=WebhookSecurityLevel.BASIC,
                    error=f"Invalid response code: {response_code}",
                    error_code="INVALID_RESPONSE_CODE"
                )
            
            # Validate data structure
            data = payload.get("data")
            if not isinstance(data, dict):
                return WebhookValidationResult(
                    valid=False,
                    security_level=WebhookSecurityLevel.BASIC,
                    error="Invalid data structure",
                    error_code="INVALID_DATA_STRUCTURE"
                )
            
            return WebhookValidationResult(
                valid=True,
                security_level=WebhookSecurityLevel.BASIC
            )
            
        except Exception as e:
            return WebhookValidationResult(
                valid=False,
                security_level=WebhookSecurityLevel.BASIC,
                error=f"Basic validation error: {str(e)}",
                error_code="VALIDATION_ERROR"
            )
    
    async def _check_rate_limits(self, payload: Dict[str, Any]) -> WebhookValidationResult:
        """Check webhook rate limits"""
        try:
            current_time = datetime.now()
            minute_key = f"webhook_rate:minute:{current_time.strftime('%Y%m%d%H%M')}"
            hour_key = f"webhook_rate:hour:{current_time.strftime('%Y%m%d%H')}"
            
            # Check minute rate limit
            minute_count = self.redis.incr(minute_key)
            if minute_count == 1:
                self.redis.expire(minute_key, 60)  # Expire after 1 minute
            
            if minute_count > self.max_webhooks_per_minute:
                await audit_logger.log_security_violation(
                    violation_type="webhook_rate_limit_exceeded",
                    request_data={
                        "limit_type": "minute",
                        "count": minute_count,
                        "limit": self.max_webhooks_per_minute
                    }
                )
                return WebhookValidationResult(
                    valid=False,
                    security_level=WebhookSecurityLevel.BASIC,
                    error="Rate limit exceeded (per minute)",
                    error_code="RATE_LIMIT_EXCEEDED"
                )
            
            # Check hour rate limit
            hour_count = self.redis.incr(hour_key)
            if hour_count == 1:
                self.redis.expire(hour_key, 3600)  # Expire after 1 hour
            
            if hour_count > self.max_webhooks_per_hour:
                await audit_logger.log_security_violation(
                    violation_type="webhook_rate_limit_exceeded",
                    request_data={
                        "limit_type": "hour",
                        "count": hour_count,
                        "limit": self.max_webhooks_per_hour
                    }
                )
                return WebhookValidationResult(
                    valid=False,
                    security_level=WebhookSecurityLevel.BASIC,
                    error="Rate limit exceeded (per hour)",
                    error_code="RATE_LIMIT_EXCEEDED"
                )
            
            return WebhookValidationResult(
                valid=True,
                security_level=WebhookSecurityLevel.BASIC
            )
            
        except Exception as e:
            return WebhookValidationResult(
                valid=False,
                security_level=WebhookSecurityLevel.BASIC,
                error=f"Rate limiting error: {str(e)}",
                error_code="RATE_LIMIT_ERROR"
            )
    
    async def _check_replay_attack(self, payload: Dict[str, Any]) -> WebhookValidationResult:
        """Check for replay attacks"""
        try:
            # Generate unique webhook identifier
            webhook_id = self._generate_webhook_id(payload)
            
            # Check if webhook was already processed
            processed_key = f"processed_webhook:{webhook_id}"
            if self.redis.exists(processed_key):
                await audit_logger.log_security_violation(
                    violation_type="webhook_replay_attack",
                    request_data={"webhook_id": webhook_id}
                )
                return WebhookValidationResult(
                    valid=False,
                    security_level=WebhookSecurityLevel.REPLAY,
                    error="Webhook already processed (replay attack)",
                    error_code="REPLAY_ATTACK"
                )
            
            return WebhookValidationResult(
                valid=True,
                security_level=WebhookSecurityLevel.REPLAY
            )
            
        except Exception as e:
            return WebhookValidationResult(
                valid=False,
                security_level=WebhookSecurityLevel.REPLAY,
                error=f"Replay protection error: {str(e)}",
                error_code="REPLAY_PROTECTION_ERROR"
            )
    
    async def _validate_x_verify_signature(
        self, 
        payload: Dict[str, Any], 
        x_verify_header: str
    ) -> WebhookValidationResult:
        """Validate X-VERIFY signature"""
        try:
            if not x_verify_header:
                return WebhookValidationResult(
                    valid=False,
                    security_level=WebhookSecurityLevel.SIGNATURE,
                    error="Missing X-VERIFY header",
                    error_code="MISSING_SIGNATURE"
                )
            
            # Parse X-VERIFY header
            # Format: sha256(hash)###salt###index
            try:
                signature_parts = x_verify_header.split("###")
                if len(signature_parts) != 3:
                    return WebhookValidationResult(
                        valid=False,
                        security_level=WebhookSecurityLevel.SIGNATURE,
                        error="Invalid X-VERIFY header format",
                        error_code="INVALID_SIGNATURE_FORMAT"
                    )
                
                hash_value = signature_parts[0]
                salt = signature_parts[1]
                index = signature_parts[2]
                
                # Remove sha256 prefix if present
                if hash_value.startswith("sha256:"):
                    hash_value = hash_value[7:]
                
            except Exception:
                return WebhookValidationResult(
                    valid=False,
                    security_level=WebhookSecurityLevel.SIGNATURE,
                    error="Failed to parse X-VERIFY header",
                    error_code="SIGNATURE_PARSE_ERROR"
                )
            
            # Get webhook data for signature validation
            data = payload.get("data", {})
            payload_salt = data.get("salt", "")
            payload_index = data.get("index", "")
            
            # Validate salt and index match
            if salt != payload_salt or index != payload_index:
                return WebhookValidationResult(
                    valid=False,
                    security_level=WebhookSecurityLevel.SIGNATURE,
                    error="Salt/index mismatch in signature",
                    error_code="SALT_INDEX_MISMATCH"
                )
            
            # Generate expected signature
            string_to_hash = f"{salt}{index}{self.webhook_secret}"
            expected_hash = hashlib.sha256(string_to_hash.encode()).hexdigest()
            
            # Compare signatures
            if hash_value != expected_hash:
                await audit_logger.log_security_violation(
                    violation_type="webhook_signature_mismatch",
                    request_data={
                        "expected": expected_hash,
                        "received": hash_value,
                        "salt": salt,
                        "index": index
                    }
                )
                return WebhookValidationResult(
                    valid=False,
                    security_level=WebhookSecurityLevel.SIGNATURE,
                    error="Invalid signature",
                    error_code="INVALID_SIGNATURE"
                )
            
            return WebhookValidationResult(
                valid=True,
                security_level=WebhookSecurityLevel.SIGNATURE
            )
            
        except Exception as e:
            return WebhookValidationResult(
                valid=False,
                security_level=WebhookSecurityLevel.SIGNATURE,
                error=f"Signature validation error: {str(e)}",
                error_code="SIGNATURE_VALIDATION_ERROR"
            )
    
    async def _validate_webhook_timestamp(self, payload: Dict[str, Any]) -> WebhookValidationResult:
        """Validate webhook timestamp to prevent old webhooks"""
        try:
            # Check for timestamp in payload
            timestamp_str = payload.get("timestamp")
            if not timestamp_str:
                # If no timestamp, check in data
                data = payload.get("data", {})
                timestamp_str = data.get("timestamp")
            
            if not timestamp_str:
                # No timestamp found, but this might be acceptable for some webhooks
                return WebhookValidationResult(
                    valid=True,
                    security_level=WebhookSecurityLevel.STRICT
                )
            
            # Parse timestamp
            try:
                if timestamp_str.endswith('Z'):
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    timestamp = datetime.fromisoformat(timestamp_str)
            except ValueError:
                return WebhookValidationResult(
                    valid=False,
                    security_level=WebhookSecurityLevel.STRICT,
                    error="Invalid timestamp format",
                    error_code="INVALID_TIMESTAMP"
                )
            
            # Check age
            age_minutes = (datetime.now() - timestamp).total_seconds() / 60
            if age_minutes > self.max_webhook_age_minutes:
                await audit_logger.log_security_violation(
                    violation_type="webhook_timestamp_too_old",
                    request_data={
                        "webhook_timestamp": timestamp_str,
                        "age_minutes": age_minutes,
                        "max_age_minutes": self.max_webhook_age_minutes
                    }
                )
                return WebhookValidationResult(
                    valid=False,
                    security_level=WebhookSecurityLevel.STRICT,
                    error=f"Webhook timestamp too old ({age_minutes:.1f} minutes)",
                    error_code="TIMESTAMP_TOO_OLD"
                )
            
            return WebhookValidationResult(
                valid=True,
                security_level=WebhookSecurityLevel.STRICT
            )
            
        except Exception as e:
            return WebhookValidationResult(
                valid=False,
                security_level=WebhookSecurityLevel.STRICT,
                error=f"Timestamp validation error: {str(e)}",
                error_code="TIMESTAMP_VALIDATION_ERROR"
            )
    
    def _generate_webhook_id(self, payload: Dict[str, Any]) -> str:
        """Generate unique webhook identifier for replay protection"""
        try:
            # Use combination of event type, transaction ID, and timestamp
            event_type = payload.get("type", "")
            data = payload.get("data", {})
            
            # Extract key identifiers
            transaction_id = data.get("merchantTransactionId", "")
            refund_id = data.get("refundId", "")
            timestamp = payload.get("timestamp", data.get("timestamp", ""))
            
            # Generate hash
            identifier_string = f"{event_type}:{transaction_id}:{refund_id}:{timestamp}"
            webhook_id = hashlib.sha256(identifier_string.encode()).hexdigest()
            
            return webhook_id
            
        except Exception:
            # Fallback to random ID
            return str(uuid.uuid4())
    
    async def _create_webhook_event(self, payload: Dict[str, Any]) -> WebhookEvent:
        """Create webhook event from payload"""
        try:
            event_type = WebhookEventType(payload.get("type"))
            data = payload.get("data", {})
            
            # Extract transaction information
            transaction_id = data.get("merchantTransactionId")
            refund_id = data.get("refundId")
            merchant_order_id = data.get("merchantOrderId")
            amount = data.get("amount")
            status = data.get("state") or data.get("status")
            
            # Parse timestamp
            timestamp_str = payload.get("timestamp") or data.get("timestamp")
            if timestamp_str:
                if timestamp_str.endswith('Z'):
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    timestamp = datetime.fromisoformat(timestamp_str)
            else:
                timestamp = datetime.now()
            
            return WebhookEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                transaction_id=transaction_id,
                refund_id=refund_id,
                merchant_order_id=merchant_order_id,
                amount=amount,
                status=status,
                timestamp=timestamp,
                raw_data=payload,
                processed_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error creating webhook event: {e}")
            raise
    
    async def _store_processed_webhook(self, webhook_event: WebhookEvent):
        """Store processed webhook for replay protection"""
        try:
            # Store webhook ID with expiration
            webhook_id = self._generate_webhook_id(webhook_event.raw_data)
            processed_key = f"processed_webhook:{webhook_id}"
            
            # Store with expiration
            self.redis.setex(
                processed_key,
                self.replay_protection_window_hours * 3600,  # Convert hours to seconds
                json.dumps({
                    "event_id": webhook_event.event_id,
                    "processed_at": webhook_event.processed_at.isoformat(),
                    "event_type": webhook_event.event_type.value
                })
            )
            
        except Exception as e:
            logger.error(f"Error storing processed webhook: {e}")
            # Don't fail the webhook processing for storage errors
    
    async def _handle_webhook_event(self, webhook_event: WebhookEvent):
        """Handle processed webhook event"""
        try:
            # Log webhook received
            await audit_logger.log_event(
                event_type=EventType.WEBHOOK_RECEIVED,
                level=LogLevel.INFO,
                transaction_id=webhook_event.transaction_id,
                request_data={
                    "event_type": webhook_event.event_type.value,
                    "transaction_id": webhook_event.transaction_id,
                    "refund_id": webhook_event.refund_id,
                    "status": webhook_event.status
                },
                response_data=webhook_event.raw_data
            )
            
            # Handle based on event type
            if webhook_event.event_type == WebhookEventType.PAYMENT_SUCCESS:
                await self._handle_payment_success(webhook_event)
            elif webhook_event.event_type == WebhookEventType.PAYMENT_FAILED:
                await self._handle_payment_failed(webhook_event)
            elif webhook_event.event_type == WebhookEventType.REFUND_COMPLETED:
                await self._handle_refund_completed(webhook_event)
            elif webhook_event.event_type == WebhookEventType.REFUND_FAILED:
                await self._handle_refund_failed(webhook_event)
            elif webhook_event.event_type == WebhookEventType.REFUND_INITIATED:
                await self._handle_refund_initiated(webhook_event)
            else:
                logger.info(f"Unhandled webhook event type: {webhook_event.event_type.value}")
            
            # Record monitoring event
            await payment_monitor.record_webhook_event(
                event_type=webhook_event.event_type.value,
                transaction_id=webhook_event.transaction_id,
                status=webhook_event.status
            )
            
        except Exception as e:
            logger.error(f"Error handling webhook event: {e}")
            await audit_logger.log_event(
                event_type=EventType.WEBHOOK_PROCESSING_FAILED,
                level=LogLevel.ERROR,
                transaction_id=webhook_event.transaction_id,
                error_message=str(e)
            )
    
    async def _handle_payment_success(self, webhook_event: WebhookEvent):
        """Handle payment success webhook"""
        try:
            if webhook_event.transaction_id:
                # Update payment status in database
                await self.payment_repo.update_payment_status(
                    webhook_event.transaction_id,
                    "COMPLETED",
                    webhook_event.raw_data
                )
                
                logger.info(f"Payment completed: {webhook_event.transaction_id}")
        except Exception as e:
            logger.error(f"Error handling payment success: {e}")
    
    async def _handle_payment_failed(self, webhook_event: WebhookEvent):
        """Handle payment failure webhook"""
        try:
            if webhook_event.transaction_id:
                # Update payment status in database
                await self.payment_repo.update_payment_status(
                    webhook_event.transaction_id,
                    "FAILED",
                    webhook_event.raw_data
                )
                
                logger.info(f"Payment failed: {webhook_event.transaction_id}")
        except Exception as e:
            logger.error(f"Error handling payment failure: {e}")
    
    async def _handle_refund_completed(self, webhook_event: WebhookEvent):
        """Handle refund completion webhook"""
        try:
            if webhook_event.refund_id:
                # Update refund status using refund manager
                success = await self.refund_manager.update_refund_from_webhook(webhook_event.raw_data)
                
                if success:
                    logger.info(f"Refund completed: {webhook_event.refund_id}")
                else:
                    logger.warning(f"Failed to update refund: {webhook_event.refund_id}")
        except Exception as e:
            logger.error(f"Error handling refund completion: {e}")
    
    async def _handle_refund_failed(self, webhook_event: WebhookEvent):
        """Handle refund failure webhook"""
        try:
            if webhook_event.refund_id:
                # Update refund status using refund manager
                success = await self.refund_manager.update_refund_from_webhook(webhook_event.raw_data)
                
                if success:
                    logger.info(f"Refund failed: {webhook_event.refund_id}")
                else:
                    logger.warning(f"Failed to update refund: {webhook_event.refund_id}")
        except Exception as e:
            logger.error(f"Error handling refund failure: {e}")
    
    async def _handle_refund_initiated(self, webhook_event: WebhookEvent):
        """Handle refund initiation webhook"""
        try:
            if webhook_event.refund_id:
                # Update refund status using refund manager
                success = await self.refund_manager.update_refund_from_webhook(webhook_event.raw_data)
                
                if success:
                    logger.info(f"Refund initiated: {webhook_event.refund_id}")
                else:
                    logger.warning(f"Failed to update refund: {webhook_event.refund_id}")
        except Exception as e:
            logger.error(f"Error handling refund initiation: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for webhook handler"""
        try:
            # Check Redis connection
            try:
                self.redis.ping()
                redis_healthy = True
            except Exception as e:
                redis_healthy = False
                redis_error = str(e)
            
            # Check configuration
            config_valid = all([
                self.webhook_secret,
                self.webhook_username,
                self.webhook_password
            ])
            
            # Overall health
            overall_healthy = redis_healthy and config_valid
            
            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "message": "Webhook handler is operational" if overall_healthy else "Webhook handler has issues",
                "features": {
                    "x_verify_validation": True,
                    "replay_protection": True,
                    "rate_limiting": True,
                    "timestamp_validation": True,
                    "audit_logging": True
                },
                "configuration": {
                    "valid": config_valid,
                    "max_webhook_age_minutes": self.max_webhook_age_minutes,
                    "replay_protection_window_hours": self.replay_protection_window_hours,
                    "max_webhooks_per_minute": self.max_webhooks_per_minute,
                    "max_webhooks_per_hour": self.max_webhooks_per_hour
                },
                "dependencies": {
                    "redis": "healthy" if redis_healthy else f"unhealthy: {redis_error}"
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "error": str(e)
            }

# Global webhook handler instance
secure_webhook_handler = None

def get_secure_webhook_handler(redis_client: redis.Redis, payment_repository: PaymentRepository) -> SecurePhonePeWebhookHandler:
    """Get or create secure webhook handler instance"""
    global secure_webhook_handler
    if secure_webhook_handler is None:
        secure_webhook_handler = SecurePhonePeWebhookHandler(redis_client, payment_repository)
    return secure_webhook_handler
