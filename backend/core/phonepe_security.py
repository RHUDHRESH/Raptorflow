"""
PhonePe Security Manager - Enterprise-Grade Payment Security
Implements comprehensive webhook signature verification, fraud detection, and security monitoring
"""

import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp
import redis
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
import jwt
import ipaddress
import re

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class WebhookEventType(Enum):
    PAYMENT_SUCCESS = "PAYMENT_SUCCESS"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    REFUND_SUCCESS = "REFUND_SUCCESS"
    REFUND_FAILED = "REFUND_FAILED"
    SETTLEMENT = "SETTLEMENT"
    CHARGEBACK = "CHARGEBACK"

@dataclass
class SecurityContext:
    ip_address: str
    user_agent: str
    request_id: str
    timestamp: datetime
    device_fingerprint: Optional[str] = None
    session_id: Optional[str] = None
    risk_score: float = 0.0

@dataclass
class WebhookValidationResult:
    valid: bool
    event_type: Optional[WebhookEventType] = None
    security_context: Optional[SecurityContext] = None
    risk_score: float = 0.0
    warnings: List[str] = None
    errors: List[str] = None
    processing_time_ms: int = 0

class PhonePeSecurityManager:
    """
    Enterprise-grade PhonePe security manager with comprehensive protection
    """
    
    def __init__(self, redis_client: redis.Redis, config: Dict[str, Any]):
        self.redis = redis_client
        self.config = config
        self.phonepe_salt_key = config.get('phonepe_salt_key', '')
        self.phonepe_app_id = config.get('phonepe_app_id', '')
        self.webhook_secret = config.get('phonepe_webhook_secret', '')
        self.allowed_ips = config.get('phonepe_allowed_ips', [])
        self.max_request_age_seconds = config.get('max_webhook_request_age', 300)
        self.rate_limit_window = config.get('rate_limit_window', 60)
        self.max_requests_per_window = config.get('max_requests_per_window', 1000)
        
        # Security thresholds
        self.risk_thresholds = {
            SecurityLevel.LOW: 0.3,
            SecurityLevel.MEDIUM: 0.6,
            SecurityLevel.HIGH: 0.8,
            SecurityLevel.CRITICAL: 0.9
        }
        
        # Initialize security components
        self._initialize_keys()
        self._initialize_patterns()
        
    def _initialize_keys(self):
        """Initialize encryption and signing keys"""
        try:
            # Load PhonePe public key for webhook verification
            self.phonepe_public_key = self.config.get('phonepe_public_key', '')
            
            # Generate internal signing key
            self.internal_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            self.internal_public_key = self.internal_private_key.public_key()
            
            logger.info("PhonePe security keys initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize security keys: {e}")
            raise
    
    def _initialize_patterns(self):
        """Initialize security patterns and rules"""
        self.suspicious_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS attempts
            r'union.*select',  # SQL injection attempts
            r'javascript:',  # JavaScript URLs
            r'data:text/html',  # Data URLs
        ]
        
        self.high_risk_countries = self.config.get('high_risk_countries', [])
        self.suspicious_user_agents = [
            'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget'
        ]
    
    async def validate_webhook_signature(
        self, 
        authorization_header: str, 
        response_body: str,
        security_context: SecurityContext
    ) -> WebhookValidationResult:
        """
        Comprehensive webhook signature validation with multiple security layers
        """
        start_time = time.time()
        warnings = []
        errors = []
        risk_score = 0.0
        
        try:
            # Step 1: Basic header validation
            if not authorization_header:
                errors.append("Missing authorization header")
                risk_score += 0.8
                return WebhookValidationResult(
                    valid=False, errors=errors, risk_score=risk_score,
                    processing_time_ms=int((time.time() - start_time) * 1000)
                )
            
            # Step 2: Extract and validate X-Verify header
            x_verify = self._extract_x_verify_header(authorization_header)
            if not x_verify:
                errors.append("Invalid X-Verify header format")
                risk_score += 0.7
                return WebhookValidationResult(
                    valid=False, errors=errors, risk_score=risk_score,
                    processing_time_ms=int((time.time() - start_time) * 1000)
                )
            
            # Step 3: Validate request timestamp
            timestamp_validation = await self._validate_request_timestamp(security_context)
            if not timestamp_validation['valid']:
                warnings.extend(timestamp_validation['warnings'])
                risk_score += timestamp_validation['risk_increase']
            
            # Step 4: IP address validation
            ip_validation = await self._validate_ip_address(security_context.ip_address)
            if not ip_validation['valid']:
                warnings.extend(ip_validation['warnings'])
                risk_score += ip_validation['risk_increase']
            
            # Step 5: User agent validation
            ua_validation = await self._validate_user_agent(security_context.user_agent)
            if not ua_validation['valid']:
                warnings.extend(ua_validation['warnings'])
                risk_score += ua_validation['risk_increase']
            
            # Step 6: Rate limiting check
            rate_limit_validation = await self._check_rate_limit(security_context)
            if not rate_limit_validation['valid']:
                warnings.extend(rate_limit_validation['warnings'])
                risk_score += rate_limit_validation['risk_increase']
            
            # Step 7: Content validation
            content_validation = await self._validate_webhook_content(response_body)
            if not content_validation['valid']:
                warnings.extend(content_validation['warnings'])
                risk_score += content_validation['risk_increase']
            
            # Step 8: PhonePe signature verification
            signature_valid = await self._verify_phonepe_signature(
                x_verify, response_body, security_context
            )
            
            if not signature_valid:
                errors.append("Invalid PhonePe signature")
                risk_score += 0.9
                return WebhookValidationResult(
                    valid=False, errors=errors, risk_score=risk_score,
                    processing_time_ms=int((time.time() - start_time) * 1000)
                )
            
            # Step 9: Parse and validate webhook event
            try:
                webhook_data = json.loads(response_body)
                event_type = self._parse_webhook_event_type(webhook_data)
                
                # Event-specific validation
                event_validation = await self._validate_webhook_event(
                    webhook_data, event_type, security_context
                )
                if not event_validation['valid']:
                    warnings.extend(event_validation['warnings'])
                    risk_score += event_validation['risk_increase']
                
            except json.JSONDecodeError:
                errors.append("Invalid JSON in webhook body")
                risk_score += 0.8
                return WebhookValidationResult(
                    valid=False, errors=errors, risk_score=risk_score,
                    processing_time_ms=int((time.time() - start_time) * 1000)
                )
            
            # Step 10: Final risk assessment
            security_level = self._assess_security_level(risk_score)
            
            # Log security event
            await self._log_security_event(
                security_context, risk_score, warnings, errors, security_level
            )
            
            # Determine if request is valid based on risk score
            is_valid = risk_score < self.risk_thresholds[SecurityLevel.HIGH]
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            return WebhookValidationResult(
                valid=is_valid,
                event_type=event_type,
                security_context=security_context,
                risk_score=risk_score,
                warnings=warnings,
                errors=errors,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            logger.error(f"Webhook validation error: {e}")
            errors.append(f"Validation error: {str(e)}")
            return WebhookValidationResult(
                valid=False, errors=errors, risk_score=1.0,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
    
    def _extract_x_verify_header(self, authorization_header: str) -> Optional[str]:
        """Extract X-Verify header from authorization header"""
        try:
            # PhonePe sends signature in Authorization header as:
            # Authorization: <X-Verify>
            if authorization_header.startswith('X-Verify:'):
                return authorization_header[9:].strip()
            elif ':' in authorization_header:
                parts = authorization_header.split(':')
                if len(parts) == 2 and parts[0].strip() == 'X-Verify':
                    return parts[1].strip()
            return None
        except Exception:
            return None
    
    async def _validate_request_timestamp(self, security_context: SecurityContext) -> Dict[str, Any]:
        """Validate request timestamp to prevent replay attacks"""
        warnings = []
        risk_increase = 0.0
        valid = True
        
        try:
            # Check if request is too old
            age_seconds = (datetime.utcnow() - security_context.timestamp).total_seconds()
            
            if age_seconds > self.max_request_age_seconds:
                warnings.append(f"Request too old: {age_seconds}s")
                risk_increase += 0.4
                valid = False
            
            # Check for clock skew (requests from future)
            if age_seconds < -60:  # Allow 60 seconds clock skew
                warnings.append(f"Request timestamp in future: {-age_seconds}s")
                risk_increase += 0.3
            
            # Check for duplicate timestamps (replay attack)
            timestamp_key = f"webhook:timestamp:{security_context.timestamp.isoformat()}"
            if await self.redis.exists(timestamp_key):
                warnings.append("Duplicate timestamp detected")
                risk_increase += 0.6
                valid = False
            else:
                # Store timestamp for 10 minutes
                await self.redis.setex(timestamp_key, 600, "1")
            
        except Exception as e:
            logger.error(f"Timestamp validation error: {e}")
            risk_increase += 0.1
        
        return {
            "valid": valid,
            "warnings": warnings,
            "risk_increase": risk_increase
        }
    
    async def _validate_ip_address(self, ip_address: str) -> Dict[str, Any]:
        """Validate IP address against allowed list and reputation"""
        warnings = []
        risk_increase = 0.0
        valid = True
        
        try:
            # Check if IP is in allowed list
            if self.allowed_ips and ip_address not in self.allowed_ips:
                warnings.append(f"IP not in allowed list: {ip_address}")
                risk_increase += 0.3
            
            # Check for private IP ranges (shouldn't come from internet)
            ip_obj = ipaddress.ip_address(ip_address)
            if ip_obj.is_private:
                warnings.append(f"Private IP address: {ip_address}")
                risk_increase += 0.2
            
            # Check IP reputation (if service available)
            reputation_key = f"ip:reputation:{ip_address}"
            reputation_score = await self.redis.get(reputation_key)
            
            if reputation_score:
                score = float(reputation_score)
                if score > 0.7:
                    warnings.append(f"High-risk IP reputation: {score}")
                    risk_increase += 0.4
            
        except Exception as e:
            logger.error(f"IP validation error: {e}")
            risk_increase += 0.1
        
        return {
            "valid": valid,
            "warnings": warnings,
            "risk_increase": risk_increase
        }
    
    async def _validate_user_agent(self, user_agent: str) -> Dict[str, Any]:
        """Validate user agent for suspicious patterns"""
        warnings = []
        risk_increase = 0.0
        valid = True
        
        try:
            if not user_agent:
                warnings.append("Missing user agent")
                risk_increase += 0.2
                return {"valid": valid, "warnings": warnings, "risk_increase": risk_increase}
            
            # Check for suspicious user agents
            user_agent_lower = user_agent.lower()
            for suspicious in self.suspicious_user_agents:
                if suspicious in user_agent_lower:
                    warnings.append(f"Suspicious user agent: {suspicious}")
                    risk_increase += 0.3
                    break
            
            # Check for very short user agents (often automated)
            if len(user_agent) < 20:
                warnings.append("Very short user agent")
                risk_increase += 0.2
            
        except Exception as e:
            logger.error(f"User agent validation error: {e}")
            risk_increase += 0.1
        
        return {
            "valid": valid,
            "warnings": warnings,
            "risk_increase": risk_increase
        }
    
    async def _check_rate_limit(self, security_context: SecurityContext) -> Dict[str, Any]:
        """Check rate limiting for webhook requests"""
        warnings = []
        risk_increase = 0.0
        valid = True
        
        try:
            # Rate limit by IP
            ip_key = f"rate_limit:webhook:ip:{security_context.ip_address}"
            ip_count = await self.redis.incr(ip_key)
            
            if ip_count == 1:
                await self.redis.expire(ip_key, self.rate_limit_window)
            
            if ip_count > self.max_requests_per_window:
                warnings.append(f"Rate limit exceeded: {ip_count} requests")
                risk_increase += 0.5
                valid = False
            
            # Rate limit globally
            global_key = "rate_limit:webhook:global"
            global_count = await self.redis.incr(global_key)
            
            if global_count == 1:
                await self.redis.expire(global_key, self.rate_limit_window)
            
            global_limit = self.max_requests_per_window * 10  # 10x per IP limit
            if global_count > global_limit:
                warnings.append(f"Global rate limit exceeded: {global_count}")
                risk_increase += 0.3
                valid = False
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            risk_increase += 0.1
        
        return {
            "valid": valid,
            "warnings": warnings,
            "risk_increase": risk_increase
        }
    
    async def _validate_webhook_content(self, response_body: str) -> Dict[str, Any]:
        """Validate webhook content for malicious patterns"""
        warnings = []
        risk_increase = 0.0
        valid = True
        
        try:
            # Check for suspicious patterns
            for pattern in self.suspicious_patterns:
                if re.search(pattern, response_body, re.IGNORECASE):
                    warnings.append(f"Suspicious content pattern detected")
                    risk_increase += 0.6
                    valid = False
                    break
            
            # Check content size
            if len(response_body) > 1024 * 1024:  # 1MB
                warnings.append("Webhook content too large")
                risk_increase += 0.3
            
            # Check for valid JSON structure
            try:
                json.loads(response_body)
            except json.JSONDecodeError:
                warnings.append("Invalid JSON structure")
                risk_increase += 0.4
                valid = False
            
        except Exception as e:
            logger.error(f"Content validation error: {e}")
            risk_increase += 0.1
        
        return {
            "valid": valid,
            "warnings": warnings,
            "risk_increase": risk_increase
        }
    
    async def _verify_phonepe_signature(
        self, 
        x_verify: str, 
        response_body: str,
        security_context: SecurityContext
    ) -> bool:
        """Verify PhonePe X-Verify signature"""
        try:
            # PhonePe signature format: sha256(base64_encoded_string) + "###" + salt_index
            if "###" not in x_verify:
                return False
            
            signature_part, salt_index_part = x_verify.split("###")
            
            # Reconstruct the signed string
            # PhonePe signs: base64_encode(response_body) + "/v3/validate" + salt_key
            import base64
            
            encoded_body = base64.b64encode(response_body.encode()).decode()
            string_to_sign = f"{encoded_body}/v3/validate{self.phonepe_salt_key}"
            
            # Calculate expected signature
            expected_hash = hashlib.sha256(string_to_sign.encode()).hexdigest()
            
            # Compare signatures
            return signature_part == expected_hash
            
        except Exception as e:
            logger.error(f"PhonePe signature verification error: {e}")
            return False
    
    def _parse_webhook_event_type(self, webhook_data: Dict[str, Any]) -> Optional[WebhookEventType]:
        """Parse webhook event type from data"""
        try:
            event_code = webhook_data.get('code', '')
            response_data = webhook_data.get('data', {})
            
            # Map PhonePe response codes to event types
            if event_code == 'PAYMENT_SUCCESS':
                return WebhookEventType.PAYMENT_SUCCESS
            elif event_code == 'PAYMENT_FAILED':
                return WebhookEventType.PAYMENT_FAILED
            elif event_code == 'PAYMENT_PENDING':
                return WebhookEventType.PAYMENT_PENDING
            elif event_code == 'REFUND_SUCCESS':
                return WebhookEventType.REFUND_SUCCESS
            elif event_code == 'REFUND_FAILED':
                return WebhookEventType.REFUND_FAILED
            elif event_code == 'SETTLEMENT':
                return WebhookEventType.SETTLEMENT
            elif event_code == 'CHARGEBACK':
                return WebhookEventType.CHARGEBACK
            
            return None
            
        except Exception:
            return None
    
    async def _validate_webhook_event(
        self, 
        webhook_data: Dict[str, Any], 
        event_type: Optional[WebhookEventType],
        security_context: SecurityContext
    ) -> Dict[str, Any]:
        """Validate specific webhook event data"""
        warnings = []
        risk_increase = 0.0
        valid = True
        
        try:
            if not event_type:
                warnings.append("Unknown webhook event type")
                risk_increase += 0.3
                return {"valid": False, "warnings": warnings, "risk_increase": risk_increase}
            
            # Validate required fields based on event type
            data = webhook_data.get('data', {})
            
            if event_type in [WebhookEventType.PAYMENT_SUCCESS, WebhookEventType.PAYMENT_FAILED]:
                # Check for transaction ID
                if not data.get('transactionId'):
                    warnings.append("Missing transaction ID")
                    risk_increase += 0.2
                
                # Check for merchant order ID
                if not data.get('merchantOrderId'):
                    warnings.append("Missing merchant order ID")
                    risk_increase += 0.2
                
                # Validate amount format
                amount = data.get('amount')
                if amount and (not isinstance(amount, (int, float)) or amount <= 0):
                    warnings.append("Invalid amount format")
                    risk_increase += 0.3
            
            elif event_type in [WebhookEventType.REFUND_SUCCESS, WebhookEventType.REFUND_FAILED]:
                # Check for refund transaction ID
                if not data.get('refundTransactionId'):
                    warnings.append("Missing refund transaction ID")
                    risk_increase += 0.2
            
            # Check for duplicate events
            event_key = f"webhook:event:{webhook_data.get('transactionId', 'unknown')}:{event_type.value}"
            if await self.redis.exists(event_key):
                warnings.append("Duplicate webhook event detected")
                risk_increase += 0.4
            else:
                # Store event for 24 hours
                await self.redis.setex(event_key, 86400, "1")
            
        except Exception as e:
            logger.error(f"Event validation error: {e}")
            risk_increase += 0.1
        
        return {
            "valid": valid,
            "warnings": warnings,
            "risk_increase": risk_increase
        }
    
    def _assess_security_level(self, risk_score: float) -> SecurityLevel:
        """Assess security level based on risk score"""
        if risk_score >= self.risk_thresholds[SecurityLevel.CRITICAL]:
            return SecurityLevel.CRITICAL
        elif risk_score >= self.risk_thresholds[SecurityLevel.HIGH]:
            return SecurityLevel.HIGH
        elif risk_score >= self.risk_thresholds[SecurityLevel.MEDIUM]:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW
    
    async def _log_security_event(
        self,
        security_context: SecurityContext,
        risk_score: float,
        warnings: List[str],
        errors: List[str],
        security_level: SecurityLevel
    ):
        """Log security event for monitoring and compliance"""
        try:
            event_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": security_context.request_id,
                "ip_address": security_context.ip_address,
                "user_agent": security_context.user_agent,
                "risk_score": risk_score,
                "security_level": security_level.value,
                "warnings": warnings,
                "errors": errors,
                "device_fingerprint": security_context.device_fingerprint,
                "session_id": security_context.session_id
            }
            
            # Store in Redis for real-time monitoring
            await self.redis.lpush(
                "security:events:webhook",
                json.dumps(event_data)
            )
            
            # Keep only last 1000 events
            await self.redis.ltrim("security:events:webhook", 0, 999)
            
            # Log to application logger
            logger.info(
                f"Webhook security event - Level: {security_level.value}, "
                f"Risk: {risk_score:.2f}, IP: {security_context.ip_address}, "
                f"Warnings: {len(warnings)}, Errors: {len(errors)}"
            )
            
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    async def generate_secure_webhook_response(
        self, 
        success: bool, 
        message: str,
        request_id: str
    ) -> Dict[str, Any]:
        """Generate secure webhook response with signature"""
        try:
            response_data = {
                "success": success,
                "message": message,
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Sign the response
            response_json = json.dumps(response_data, separators=(',', ':'))
            signature = self._sign_response(response_json)
            
            return {
                "data": response_data,
                "signature": signature,
                "timestamp": response_data["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Failed to generate secure response: {e}")
            return {"error": "Internal server error"}
    
    def _sign_response(self, response_json: str) -> str:
        """Sign response with internal private key"""
        try:
            signature = self.internal_private_key.sign(
                response_json.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return signature.hex()
        except Exception as e:
            logger.error(f"Failed to sign response: {e}")
            return ""
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics for monitoring"""
        try:
            # Get recent security events
            events = await self.redis.lrange("security:events:webhook", 0, 99)
            
            metrics = {
                "total_events": len(events),
                "risk_distribution": {
                    "low": 0,
                    "medium": 0,
                    "high": 0,
                    "critical": 0
                },
                "average_risk_score": 0.0,
                "top_warnings": {},
                "top_errors": {},
                "blocked_requests": 0
            }
            
            total_risk = 0.0
            warnings_count = {}
            errors_count = {}
            
            for event_json in events:
                try:
                    event = json.loads(event_json)
                    
                    # Risk distribution
                    level = event.get('security_level', 'low')
                    metrics["risk_distribution"][level] += 1
                    
                    # Risk score
                    risk_score = event.get('risk_score', 0.0)
                    total_risk += risk_score
                    
                    # Count warnings
                    for warning in event.get('warnings', []):
                        warnings_count[warning] = warnings_count.get(warning, 0) + 1
                    
                    # Count errors
                    for error in event.get('errors', []):
                        errors_count[error] = errors_count.get(error, 0) + 1
                    
                    # Blocked requests
                    if risk_score >= self.risk_thresholds[SecurityLevel.HIGH]:
                        metrics["blocked_requests"] += 1
                        
                except json.JSONDecodeError:
                    continue
            
            # Calculate averages
            if events:
                metrics["average_risk_score"] = total_risk / len(events)
            
            # Top warnings and errors
            metrics["top_warnings"] = dict(sorted(warnings_count.items(), key=lambda x: x[1], reverse=True)[:5])
            metrics["top_errors"] = dict(sorted(errors_count.items(), key=lambda x: x[1], reverse=True)[:5])
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get security metrics: {e}")
            return {"error": str(e)}
