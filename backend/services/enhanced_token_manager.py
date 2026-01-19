"""
Enhanced OAuth Token Management for PhonePe 2026 API
Implements token rotation, refresh, and secure caching
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from cryptography.fernet import Fernet
import redis.asyncio as redis
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TokenInfo:
    """Token information with metadata"""
    access_token: str
    expires_at: datetime
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    scope: Optional[str] = None
    client_id: Optional[str] = None
    created_at: Optional[datetime] = None

class EnhancedTokenManager:
    """
    Enhanced OAuth token manager with rotation, caching, and security features
    """
    
    def __init__(self):
        self.client_id = os.getenv("PHONEPE_CLIENT_ID")
        self.client_secret = os.getenv("PHONEPE_CLIENT_SECRET")
        self.client_version = os.getenv("PHONEPE_CLIENT_VERSION", "1")
        
        # Redis for distributed token caching
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client: Optional[redis.Redis] = None
        
        # Encryption for token storage
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Token rotation settings
        self.refresh_threshold = timedelta(minutes=5)  # Refresh 5 minutes before expiry
        self.max_retry_attempts = 3
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = timedelta(minutes=2)
        
        # Circuit breaker state
        self._circuit_breaker_failures = 0
        self._circuit_breaker_last_failure = None
        self._circuit_breaker_state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
        # Token cache
        self._token_cache: Dict[str, TokenInfo] = {}
        self._cache_lock = asyncio.Lock()

    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for token storage"""
        key_file = "phonepe_token_key.enc"
        
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        
        # Generate new key
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        
        # Set secure permissions
        os.chmod(key_file, 0o600)
        return key

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis connection established for token management")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory cache: {e}")
            self.redis_client = None

    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open"""
        if self._circuit_breaker_state == "OPEN":
            if (datetime.now() - self._circuit_breaker_last_failure) > self.circuit_breaker_timeout:
                self._circuit_breaker_state = "HALF_OPEN"
                return False
            return True
        return False

    def _record_circuit_breaker_failure(self):
        """Record a failure for circuit breaker"""
        self._circuit_breaker_failures += 1
        self._circuit_breaker_last_failure = datetime.now()
        
        if self._circuit_breaker_failures >= self.circuit_breaker_threshold:
            self._circuit_breaker_state = "OPEN"

    def _record_circuit_breaker_success(self):
        """Record a success for circuit breaker"""
        self._circuit_breaker_failures = 0
        self._circuit_breaker_state = "CLOSED"

    def _encrypt_token(self, token_info: TokenInfo) -> str:
        """Encrypt token information for storage"""
        data = json.dumps({
            "access_token": token_info.access_token,
            "expires_at": token_info.expires_at.isoformat(),
            "refresh_token": token_info.refresh_token,
            "token_type": token_info.token_type,
            "scope": token_info.scope,
            "client_id": token_info.client_id,
            "created_at": token_info.created_at.isoformat() if token_info.created_at else None
        }).encode()
        return self.cipher.encrypt(data).decode()

    def _decrypt_token(self, encrypted_data: str) -> TokenInfo:
        """Decrypt token information from storage"""
        data = json.loads(self.cipher.decrypt(encrypted_data.encode()).decode())
        return TokenInfo(
            access_token=data["access_token"],
            expires_at=datetime.fromisoformat(data["expires_at"]),
            refresh_token=data.get("refresh_token"),
            token_type=data.get("token_type", "Bearer"),
            scope=data.get("scope"),
            client_id=data.get("client_id"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        )

    def _generate_cache_key(self, client_id: str) -> str:
        """Generate cache key for token"""
        return f"phonepe_token:{hashlib.sha256(client_id.encode()).hexdigest()}"

    async def _cache_token(self, client_id: str, token_info: TokenInfo):
        """Cache token with encryption"""
        cache_key = self._generate_cache_key(client_id)
        encrypted_token = self._encrypt_token(token_info)
        
        if self.redis_client:
            await self.redis_client.setex(
                cache_key,
                int((token_info.expires_at - datetime.now()).total_seconds()),
                encrypted_token
            )
        else:
            async with self._cache_lock:
                self._token_cache[cache_key] = token_info

    async def _get_cached_token(self, client_id: str) -> Optional[TokenInfo]:
        """Get cached token"""
        cache_key = self._generate_cache_key(client_id)
        
        if self.redis_client:
            encrypted_token = await self.redis_client.get(cache_key)
            if encrypted_token:
                return self._decrypt_token(encrypted_token)
        else:
            async with self._cache_lock:
                return self._token_cache.get(cache_key)
        
        return None

    async def _request_new_token(self) -> TokenInfo:
        """Request new OAuth token from PhonePe"""
        if self._is_circuit_breaker_open():
            raise Exception("Circuit breaker is open - too many recent failures")

        token_url = "https://api-preprod.phonepe.com/apis/pg-sandbox/v1/oauth/token"
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_version": self.client_version,
            "client_secret": self.client_secret,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(token_url, data=data, headers=headers)
                response.raise_for_status()
                
                token_data = response.json()
                access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                
                # Record success for circuit breaker
                self._record_circuit_breaker_success()
                
                return TokenInfo(
                    access_token=access_token,
                    expires_at=datetime.now() + timedelta(seconds=expires_in),
                    token_type="Bearer",
                    client_id=self.client_id,
                    created_at=datetime.now()
                )

        except Exception as e:
            self._record_circuit_breaker_failure()
            logger.error(f"Failed to get OAuth token: {e}")
            raise

    async def get_valid_token(self) -> str:
        """Get valid OAuth token with automatic refresh"""
        if not self.client_id or not self.client_secret:
            raise ValueError("PhonePe client credentials not configured")

        # Try to get cached token
        cached_token = await self._get_cached_token(self.client_id)
        
        if cached_token:
            # Check if token is still valid
            if datetime.now() < (cached_token.expires_at - self.refresh_threshold):
                return cached_token.access_token
            
            # Token is expiring soon, try to refresh
            try:
                new_token = await self._request_new_token()
                await self._cache_token(self.client_id, new_token)
                return new_token.access_token
            except Exception as e:
                # If refresh fails, use old token if still valid
                if datetime.now() < cached_token.expires_at:
                    logger.warning(f"Token refresh failed, using existing token: {e}")
                    return cached_token.access_token
                raise

        # No cached token, request new one
        new_token = await self._request_new_token()
        await self._cache_token(self.client_id, new_token)
        return new_token.access_token

    async def invalidate_token(self):
        """Invalidate cached token"""
        cache_key = self._generate_cache_key(self.client_id)
        
        if self.redis_client:
            await self.redis_client.delete(cache_key)
        else:
            async with self._cache_lock:
                self._token_cache.pop(cache_key, None)

    async def get_token_info(self) -> Optional[TokenInfo]:
        """Get current token information"""
        return await self._get_cached_token(self.client_id)

    async def health_check(self) -> Dict[str, any]:
        """Health check for token manager"""
        try:
            token_info = await self.get_token_info()
            if not token_info:
                return {
                    "status": "unhealthy",
                    "message": "No token available"
                }
            
            time_to_expiry = (token_info.expires_at - datetime.now()).total_seconds()
            
            return {
                "status": "healthy",
                "token_expires_in": time_to_expiry,
                "circuit_breaker_state": self._circuit_breaker_state,
                "redis_connected": self.redis_client is not None
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def cleanup(self):
        """Cleanup resources"""
        if self.redis_client:
            await self.redis_client.close()

# Global instance
enhanced_token_manager = EnhancedTokenManager()
