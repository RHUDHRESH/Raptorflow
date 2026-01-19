"""
Enhanced Security Module for PhonePe Integration
Implements HMAC signing, rate limiting, and advanced security features
"""

import asyncio
import hashlib
import hmac
import ipaddress
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import secrets
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    hmac_algorithm: str = "SHA256"
    hmac_key_rotation_interval: timedelta = timedelta(hours=24)
    rate_limit_window: timedelta = timedelta(minutes=1)
    rate_limit_max_requests: int = 100
    webhook_signature_algorithms: List[str] = None
    ip_whitelist_enabled: bool = True
    request_fingerprinting_enabled: bool = True
    audit_logging_enabled: bool = True

class HMACSigner:
    """HMAC request signing for additional security"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self._hmac_key = None
        self._key_rotation_time = None
        self._initialize_hmac_key()

    def _initialize_hmac_key(self):
        """Initialize or rotate HMAC key"""
        key_file = "phonepe_hmac_key.enc"
        
        # Check if key exists and needs rotation
        if os.path.exists(key_file):
            try:
                with open(key_file, "rb") as f:
                    key_data = json.loads(f.read())
                    key_created = datetime.fromisoformat(key_data["created_at"])
                    
                    if (datetime.now() - key_created) < self.config.hmac_key_rotation_interval:
                        self._hmac_key = base64.b64decode(key_data["key"])
                        self._key_rotation_time = key_created
                        return
            except Exception as e:
                logger.warning(f"Failed to load HMAC key: {e}")
        
        # Generate new key
        self._generate_new_hmac_key(key_file)

    def _generate_new_hmac_key(self, key_file: str):
        """Generate new HMAC key"""
        # Generate cryptographically secure key
        self._hmac_key = secrets.token_bytes(32)
        
        # Save key with metadata
        key_data = {
            "key": base64.b64encode(self._hmac_key).decode(),
            "created_at": datetime.now().isoformat(),
            "algorithm": self.config.hmac_algorithm
        }
        
        with open(key_file, "w") as f:
            json.dump(key_data, f)
        
        # Set secure permissions
        os.chmod(key_file, 0o600)
        self._key_rotation_time = datetime.now()
        
        logger.info("HMAC key generated and rotated")

    def sign_request(self, method: str, url: str, body: str, timestamp: str, nonce: str) -> str:
        """Sign HTTP request with HMAC"""
        if self._hmac_key is None:
            self._initialize_hmac_key()
        
        # Create canonical string to sign
        canonical_string = f"{method.upper()}&{url}&{body}&{timestamp}&{nonce}"
        
        # Generate HMAC signature
        if self.config.hmac_algorithm.upper() == "SHA256":
            signature = hmac.new(
                self._hmac_key,
                canonical_string.encode('utf-8'),
                hashlib.sha256
            ).digest()
        elif self.config.hmac_algorithm.upper() == "SHA512":
            signature = hmac.new(
                self._hmac_key,
                canonical_string.encode('utf-8'),
                hashlib.sha512
            ).digest()
        else:
            raise ValueError(f"Unsupported HMAC algorithm: {self.config.hmac_algorithm}")
        
        return base64.b64encode(signature).decode()

    def verify_signature(self, method: str, url: str, body: str, timestamp: str, nonce: str, signature: str) -> bool:
        """Verify HMAC signature"""
        try:
            expected_signature = self.sign_request(method, url, body, timestamp, nonce)
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False

class RateLimiter:
    """Advanced rate limiting with Redis backend"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.redis_client = None
        self._local_cache: Dict[str, List[datetime]] = {}

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            import redis.asyncio as redis
            self.redis_client = redis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Rate limiter connected to Redis")
        except Exception as e:
            logger.warning(f"Redis not available for rate limiting: {e}")

    def _get_client_identifier(self, request_data: Dict) -> str:
        """Get client identifier for rate limiting"""
        # Use IP address, user ID, or API key as identifier
        return request_data.get("client_ip", "anonymous")

    async def is_allowed(self, client_id: str, endpoint: str) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is allowed based on rate limits"""
        key = f"rate_limit:{client_id}:{endpoint}"
        now = datetime.now()
        window_start = now - self.config.rate_limit_window
        
        if self.redis_client:
            # Use Redis sliding window
            try:
                # Remove old entries
                await self.redis_client.zremrangebyscore(key, 0, window_start.timestamp())
                
                # Count current requests
                current_count = await self.redis_client.zcard(key)
                
                if current_count >= self.config.rate_limit_max_requests:
                    return False, {
                        "allowed": False,
                        "limit": self.config.rate_limit_max_requests,
                        "remaining": 0,
                        "reset_time": (window_start + self.config.rate_limit_window).timestamp()
                    }
                
                # Add current request
                await self.redis_client.zadd(key, {str(now.timestamp()): now.timestamp()})
                await self.redis_client.expire(key, int(self.config.rate_limit_window.total_seconds()))
                
                return True, {
                    "allowed": True,
                    "limit": self.config.rate_limit_max_requests,
                    "remaining": self.config.rate_limit_max_requests - current_count - 1,
                    "reset_time": (now + self.config.rate_limit_window).timestamp()
                }
                
            except Exception as e:
                logger.error(f"Redis rate limiting failed: {e}")
        
        # Fallback to in-memory rate limiting
        if client_id not in self._local_cache:
            self._local_cache[client_id] = []
        
        # Remove old entries
        self._local_cache[client_id] = [
            req_time for req_time in self._local_cache[client_id]
            if req_time > window_start
        ]
        
        if len(self._local_cache[client_id]) >= self.config.rate_limit_max_requests:
            return False, {
                "allowed": False,
                "limit": self.config.rate_limit_max_requests,
                "remaining": 0,
                "reset_time": (window_start + self.config.rate_limit_window).timestamp()
            }
        
        self._local_cache[client_id].append(now)
        return True, {
            "allowed": True,
            "limit": self.config.rate_limit_max_requests,
            "remaining": self.config.rate_limit_max_requests - len(self._local_cache[client_id]),
            "reset_time": (now + self.config.rate_limit_window).timestamp()
        }

class WebhookValidator:
    """Enhanced webhook signature validation"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.webhook_secret = os.getenv("PHONEPE_WEBHOOK_SECRET")
        self.supported_algorithms = config.webhook_signature_algorithms or ["SHA256", "SHA512"]

    def validate_webhook_signature(self, payload: str, signature: str, algorithm: str = "SHA256") -> bool:
        """Validate webhook signature with multiple algorithms"""
        if not self.webhook_secret:
            logger.warning("Webhook secret not configured")
            return False
        
        if algorithm not in self.supported_algorithms:
            logger.error(f"Unsupported webhook signature algorithm: {algorithm}")
            return False
        
        try:
            # PhonePe uses X-VERIFY header with SHA256
            if algorithm == "SHA256":
                expected_signature = hmac.new(
                    self.webhook_secret.encode(),
                    payload.encode(),
                    hashlib.sha256
                ).hexdigest()
            elif algorithm == "SHA512":
                expected_signature = hmac.new(
                    self.webhook_secret.encode(),
                    payload.encode(),
                    hashlib.sha512
                ).hexdigest()
            else:
                return False
            
            # Remove algorithm prefix if present (e.g., "sha256=")
            if signature.startswith(f"{algorithm.lower()}="):
                signature = signature.split("=", 1)[1]
            
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"Webhook signature validation failed: {e}")
            return False

    def validate_webhook_structure(self, webhook_data: Dict) -> Tuple[bool, List[str]]:
        """Validate webhook payload structure"""
        errors = []
        
        # Required fields for PhonePe webhooks
        required_fields = ["type", "code", "data"]
        for field in required_fields:
            if field not in webhook_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate data structure
        if "data" in webhook_data:
            data = webhook_data["data"]
            if not isinstance(data, dict):
                errors.append("Webhook data must be an object")
            else:
                # Check for common payment fields
                if "transactionId" in data and not isinstance(data["transactionId"], str):
                    errors.append("transactionId must be a string")
                if "amount" in data and not isinstance(data["amount"], (int, float)):
                    errors.append("amount must be a number")
        
        return len(errors) == 0, errors

class IPWhitelist:
    """IP whitelisting for webhook endpoints"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.whitelisted_ips = self._load_whitelist()

    def _load_whitelist(self) -> List[ipaddress.IPv4Network]:
        """Load whitelisted IP ranges"""
        whitelist_file = "phonepe_ip_whitelist.txt"
        whitelisted = []
        
        # Default PhonePe webhook IPs (these should be updated with actual PhonePe IPs)
        default_ips = [
            "203.95.208.0/24",  # Example PhonePe range
            "203.95.209.0/24",
        ]
        
        if os.path.exists(whitelist_file):
            try:
                with open(whitelist_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            try:
                                whitelisted.append(ipaddress.IPv4Network(line))
                            except ValueError as e:
                                logger.warning(f"Invalid IP range in whitelist: {line} - {e}")
            except Exception as e:
                logger.error(f"Failed to load IP whitelist: {e}")
        
        # Add default IPs if file doesn't exist or is empty
        if not whitelisted:
            for ip_range in default_ips:
                try:
                    whitelisted.append(ipaddress.IPv4Network(ip_range))
                except ValueError:
                    pass
        
        return whitelisted

    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP address is whitelisted"""
        if not self.config.ip_whitelist_enabled:
            return True
        
        try:
            ip = ipaddress.IPv4Address(ip_address)
            return any(ip in network for network in self.whitelisted_ips)
        except ValueError:
            logger.warning(f"Invalid IP address: {ip_address}")
            return False

class RequestFingerprinter:
    """Request fingerprinting for fraud detection"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config

    def generate_fingerprint(self, request_data: Dict) -> str:
        """Generate unique fingerprint for request"""
        if not self.config.request_fingerprinting_enabled:
            return ""
        
        # Combine various request attributes
        fingerprint_data = {
            "user_agent": request_data.get("user_agent", ""),
            "accept_language": request_data.get("accept_language", ""),
            "timezone": request_data.get("timezone", ""),
            "screen_resolution": request_data.get("screen_resolution", ""),
            "platform": request_data.get("platform", ""),
            "client_ip": request_data.get("client_ip", ""),
        }
        
        # Create hash
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()

class SecurityManager:
    """Main security manager combining all security features"""
    
    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self.hmac_signer = HMACSigner(self.config)
        self.rate_limiter = RateLimiter(self.config)
        self.webhook_validator = WebhookValidator(self.config)
        self.ip_whitelist = IPWhitelist(self.config)
        self.fingerprinter = RequestFingerprinter(self.config)

    async def initialize(self):
        """Initialize security components"""
        await self.rate_limiter.initialize()
        logger.info("Security manager initialized")

    def sign_request(self, method: str, url: str, body: str, timestamp: str, nonce: str) -> str:
        """Sign request with HMAC"""
        return self.hmac_signer.sign_request(method, url, body, timestamp, nonce)

    async def validate_request(self, request_data: Dict, endpoint: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate request with rate limiting and security checks"""
        client_id = self.rate_limiter._get_client_identifier(request_data)
        
        # Rate limiting
        rate_limit_result = await self.rate_limiter.is_allowed(client_id, endpoint)
        if not rate_limit_result[0]:
            return False, {"error": "Rate limit exceeded", "rate_limit": rate_limit_result[1]}
        
        # IP whitelist check for webhooks
        if "webhook" in endpoint.lower():
            client_ip = request_data.get("client_ip")
            if client_ip and not self.ip_whitelist.is_ip_allowed(client_ip):
                return False, {"error": "IP not whitelisted"}
        
        # Generate fingerprint
        fingerprint = self.fingerprinter.generate_fingerprint(request_data)
        
        return True, {
            "fingerprint": fingerprint,
            "rate_limit": rate_limit_result[1]
        }

    def validate_webhook(self, payload: str, signature: str, algorithm: str = "SHA256") -> Tuple[bool, List[str]]:
        """Validate webhook signature and structure"""
        errors = []
        
        # Signature validation
        if not self.webhook_validator.validate_webhook_signature(payload, signature, algorithm):
            errors.append("Invalid webhook signature")
        
        # Structure validation
        try:
            webhook_data = json.loads(payload)
            structure_valid, structure_errors = self.webhook_validator.validate_webhook_structure(webhook_data)
            if not structure_valid:
                errors.extend(structure_errors)
        except json.JSONDecodeError:
            errors.append("Invalid JSON payload")
        
        return len(errors) == 0, errors

# Global security manager instance
security_manager = SecurityManager()
