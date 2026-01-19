"""
Idempotency Management for PhonePe Payment Requests
Prevents duplicate transactions and ensures exactly-once processing
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import redis.asyncio as redis
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class IdempotencyStatus(Enum):
    """Idempotency request status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

@dataclass
class IdempotencyRecord:
    """Record for idempotency tracking"""
    key: str
    status: IdempotencyStatus
    request_hash: str
    response_data: Optional[Dict[str, Any]] = None
    error_data: Optional[Dict[str, Any]] = None
    created_at: datetime = None
    updated_at: datetime = None
    expires_at: datetime = None
    user_id: Optional[str] = None
    transaction_id: Optional[str] = None
    merchant_order_id: Optional[str] = None
    request_metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class IdempotencyManager:
    """
    Advanced idempotency manager with Redis backend and encryption
    Ensures exactly-once processing for payment requests
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # Encryption for sensitive data
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Configuration
        self.default_expiry = timedelta(hours=24)  # 24 hours default
        self.max_expiry = timedelta(days=7)       # 7 days maximum
        self.cleanup_interval = timedelta(hours=1)  # Cleanup interval
        
        # Local cache for performance
        self._local_cache: Dict[str, IdempotencyRecord] = {}
        self._cache_lock = asyncio.Lock()
        
        # Background cleanup task
        self._cleanup_task = None

    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for idempotency records"""
        key_file = "phonepe_idempotency_key.enc"
        
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
        """Initialize Redis connection and start background tasks"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Idempotency manager connected to Redis")
            
            # Start background cleanup task
            self._cleanup_task = asyncio.create_task(self._background_cleanup())
            
        except Exception as e:
            logger.warning(f"Redis not available for idempotency: {e}")
            self.redis_client = None

    async def cleanup(self):
        """Cleanup resources"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self.redis_client:
            await self.redis_client.close()

    def _encrypt_data(self, data: Dict[str, Any]) -> str:
        """Encrypt sensitive data"""
        try:
            json_data = json.dumps(data, default=str)
            return self.cipher.encrypt(json_data.encode()).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt data: {e}")
            return ""

    def _decrypt_data(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt sensitive data"""
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode()).decode()
            return json.loads(decrypted)
        except Exception as e:
            logger.error(f"Failed to decrypt data: {e}")
            return {}

    def _generate_request_hash(self, request_data: Dict[str, Any]) -> str:
        """Generate hash of request data for comparison"""
        # Normalize request data for consistent hashing
        normalized_data = json.dumps(request_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(normalized_data.encode()).hexdigest()

    def _generate_idempotency_key(self, user_id: str, operation: str, custom_key: Optional[str] = None) -> str:
        """Generate idempotency key"""
        if custom_key:
            # Use provided custom key
            base_key = custom_key
        else:
            # Generate key from user ID and operation
            base_key = f"{user_id}:{operation}:{datetime.now().strftime('%Y%m%d')}"
        
        # Add UUID for uniqueness
        unique_suffix = str(uuid.uuid4())[:8]
        return f"idemp:{base_key}:{unique_suffix}"

    async def check_and_create_request(
        self,
        user_id: str,
        operation: str,
        request_data: Dict[str, Any],
        custom_key: Optional[str] = None,
        expiry: Optional[timedelta] = None,
        transaction_id: Optional[str] = None,
        merchant_order_id: Optional[str] = None
    ) -> tuple[bool, Optional[IdempotencyRecord]]:
        """
        Check if request exists and create new record if not
        Returns (is_new_request, record)
        """
        idempotency_key = self._generate_idempotency_key(user_id, operation, custom_key)
        request_hash = self._generate_request_hash(request_data)
        expiry_time = expiry or self.default_expiry
        expires_at = datetime.now() + expiry_time

        # Check local cache first
        async with self._cache_lock:
            if idempotency_key in self._local_cache:
                cached_record = self._local_cache[idempotency_key]
                if cached_record.expires_at > datetime.now():
                    # Check if request hash matches
                    if cached_record.request_hash == request_hash:
                        return False, cached_record
                    else:
                        # Different request data, treat as new
                        logger.warning(f"Idempotency key reused with different data: {idempotency_key}")

        # Check Redis
        if self.redis_client:
            try:
                existing_data = await self.redis_client.get(idempotency_key)
                if existing_data:
                    record_data = self._decrypt_data(existing_data)
                    existing_record = IdempotencyRecord(**record_data)
                    
                    if existing_record.expires_at > datetime.now():
                        if existing_record.request_hash == request_hash:
                            # Update local cache
                            async with self._cache_lock:
                                self._local_cache[idempotency_key] = existing_record
                            return False, existing_record
                        else:
                            logger.warning(f"Idempotency key reused with different data: {idempotency_key}")
            except Exception as e:
                logger.error(f"Failed to check idempotency in Redis: {e}")

        # Create new record
        new_record = IdempotencyRecord(
            key=idempotency_key,
            status=IdempotencyStatus.PENDING,
            request_hash=request_hash,
            expires_at=expires_at,
            user_id=user_id,
            transaction_id=transaction_id,
            merchant_order_id=merchant_order_id,
            request_metadata={
                "operation": operation,
                "custom_key": custom_key,
                "request_size": len(str(request_data))
            }
        )

        # Store in Redis
        if self.redis_client:
            try:
                encrypted_data = self._encrypt_data(asdict(new_record))
                await self.redis_client.setex(
                    idempotency_key,
                    int(expiry_time.total_seconds()),
                    encrypted_data
                )
            except Exception as e:
                logger.error(f"Failed to store idempotency record in Redis: {e}")

        # Update local cache
        async with self._cache_lock:
            self._local_cache[idempotency_key] = new_record

        return True, new_record

    async def update_status(
        self,
        idempotency_key: str,
        status: IdempotencyStatus,
        response_data: Optional[Dict[str, Any]] = None,
        error_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update status of idempotency record"""
        # Get current record
        record = await self.get_record(idempotency_key)
        if not record:
            logger.warning(f"Attempted to update non-existent idempotency record: {idempotency_key}")
            return False

        # Update record
        record.status = status
        record.updated_at = datetime.now()
        
        if response_data:
            record.response_data = response_data
        
        if error_data:
            record.error_data = error_data

        # Update Redis
        if self.redis_client:
            try:
                encrypted_data = self._encrypt_data(asdict(record))
                remaining_ttl = int((record.expires_at - datetime.now()).total_seconds())
                if remaining_ttl > 0:
                    await self.redis_client.setex(idempotency_key, remaining_ttl, encrypted_data)
            except Exception as e:
                logger.error(f"Failed to update idempotency record in Redis: {e}")

        # Update local cache
        async with self._cache_lock:
            self._local_cache[idempotency_key] = record

        return True

    async def get_record(self, idempotency_key: str) -> Optional[IdempotencyRecord]:
        """Get idempotency record by key"""
        # Check local cache first
        async with self._cache_lock:
            if idempotency_key in self._local_cache:
                cached_record = self._local_cache[idempotency_key]
                if cached_record.expires_at > datetime.now():
                    return cached_record
                else:
                    # Remove expired record from cache
                    del self._local_cache[idempotency_key]

        # Check Redis
        if self.redis_client:
            try:
                encrypted_data = await self.redis_client.get(idempotency_key)
                if encrypted_data:
                    record_data = self._decrypt_data(encrypted_data)
                    record = IdempotencyRecord(**record_data)
                    
                    if record.expires_at > datetime.now():
                        # Update local cache
                        async with self._cache_lock:
                            self._local_cache[idempotency_key] = record
                        return record
                    else:
                        # Remove expired record from Redis
                        await self.redis_client.delete(idempotency_key)
            except Exception as e:
                logger.error(f"Failed to get idempotency record from Redis: {e}")

        return None

    async def get_user_requests(
        self,
        user_id: str,
        status: Optional[IdempotencyStatus] = None,
        limit: int = 100
    ) -> List[IdempotencyRecord]:
        """Get all requests for a user"""
        records = []
        
        # Get from local cache
        async with self._cache_lock:
            for record in self._local_cache.values():
                if record.user_id == user_id and record.expires_at > datetime.now():
                    if status is None or record.status == status:
                        records.append(record)

        # If Redis is available, get more records
        if self.redis_client and len(records) < limit:
            try:
                # This is a simplified approach - in production, you'd want
                # to maintain an index of user requests
                pattern = f"idemp:{user_id}:*"
                keys = await self.redis_client.keys(pattern)
                
                for key in keys[:limit - len(records)]:
                    encrypted_data = await self.redis_client.get(key)
                    if encrypted_data:
                        record_data = self._decrypt_data(encrypted_data)
                        record = IdempotencyRecord(**record_data)
                        
                        if record.expires_at > datetime.now():
                            if status is None or record.status == status:
                                records.append(record)
            except Exception as e:
                logger.error(f"Failed to get user requests from Redis: {e}")

        return records[:limit]

    async def cleanup_expired_records(self):
        """Clean up expired records"""
        now = datetime.now()
        
        # Clean local cache
        async with self._cache_lock:
            expired_keys = [
                key for key, record in self._local_cache.items()
                if record.expires_at <= now
            ]
            for key in expired_keys:
                del self._local_cache[key]

        # Clean Redis
        if self.redis_client:
            try:
                # This is a simplified cleanup - in production, you'd want
                # to use Redis keyspace notifications or a more efficient approach
                pattern = "idemp:*"
                keys = await self.redis_client.keys(pattern)
                
                for key in keys:
                    encrypted_data = await self.redis_client.get(key)
                    if encrypted_data:
                        try:
                            record_data = self._decrypt_data(encrypted_data)
                            record = IdempotencyRecord(**record_data)
                            
                            if record.expires_at <= now:
                                await self.redis_client.delete(key)
                        except Exception:
                            # If we can't decrypt, just delete the key
                            await self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"Failed to cleanup expired records in Redis: {e}")

    async def _background_cleanup(self):
        """Background task for periodic cleanup"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval.total_seconds())
                await self.cleanup_expired_records()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Background cleanup failed: {e}")

    async def get_statistics(self) -> Dict[str, Any]:
        """Get idempotency manager statistics"""
        now = datetime.now()
        
        # Local cache stats
        async with self._cache_lock:
            total_local = len(self._local_cache)
            expired_local = sum(1 for record in self._local_cache.values() if record.expires_at <= now)
            active_local = total_local - expired_local

        stats = {
            "local_cache": {
                "total_records": total_local,
                "active_records": active_local,
                "expired_records": expired_local
            },
            "redis_connected": self.redis_client is not None
        }

        # Redis stats
        if self.redis_client:
            try:
                # Count total idempotency keys
                pattern = "idemp:*"
                keys = await self.redis_client.keys(pattern)
                
                stats["redis"] = {
                    "total_keys": len(keys),
                    "memory_usage": await self.redis_client.memory_usage("idempotency_manager")
                }
            except Exception as e:
                logger.error(f"Failed to get Redis statistics: {e}")
                stats["redis"] = {"error": str(e)}

        return stats

# Decorator for idempotency protection
def idempotent(
    operation: str,
    key_param: str = "idempotency_key",
    expiry: timedelta = None
):
    """Decorator to make functions idempotent"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user_id and idempotency_key from kwargs
            user_id = kwargs.get("user_id")
            idempotency_key = kwargs.get(key_param)
            
            if not user_id:
                raise ValueError("user_id is required for idempotency")
            
            if not idempotency_key:
                raise ValueError(f"{key_param} is required for idempotency")
            
            # Check if request already exists
            is_new, record = await idempotency_manager.check_and_create_request(
                user_id=user_id,
                operation=operation,
                request_data=kwargs,
                custom_key=idempotency_key,
                expiry=expiry
            )
            
            if not is_new:
                # Request already processed, return cached response
                if record.status == IdempotencyStatus.COMPLETED and record.response_data:
                    return record.response_data
                elif record.status == IdempotencyStatus.FAILED and record.error_data:
                    raise Exception(f"Request previously failed: {record.error_data}")
                elif record.status == IdempotencyStatus.PROCESSING:
                    raise Exception("Request is currently being processed")
                else:
                    raise Exception("Request in invalid state")
            
            # Mark as processing
            await idempotency_manager.update_status(
                record.key,
                IdempotencyStatus.PROCESSING
            )
            
            try:
                # Execute the function
                result = await func(*args, **kwargs)
                
                # Mark as completed
                await idempotency_manager.update_status(
                    record.key,
                    IdempotencyStatus.COMPLETED,
                    response_data=result if isinstance(result, dict) else {"result": result}
                )
                
                return result
                
            except Exception as e:
                # Mark as failed
                await idempotency_manager.update_status(
                    record.key,
                    IdempotencyStatus.FAILED,
                    error_data={"error": str(e), "type": type(e).__name__}
                )
                raise
        
        return wrapper
    return decorator

# Global idempotency manager instance
idempotency_manager = IdempotencyManager()
