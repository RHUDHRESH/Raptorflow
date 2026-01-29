"""
Idempotency Manager for Payment System
Implements comprehensive idempotency with Redis storage and key expiration
Addresses critical idempotency vulnerabilities identified in red team audit
"""

import asyncio
import hashlib
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import redis
from functools import wraps
import inspect

from .core.audit_logger import audit_logger, EventType, LogLevel

logger = logging.getLogger(__name__)


class IdempotencyStatus(Enum):
    """Idempotency operation status"""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"


class IdempotencyScope(Enum):
    """Idempotency key scope"""

    USER = "USER"  # User-specific idempotency
    GLOBAL = "GLOBAL"  # Global idempotency
    SESSION = "SESSION"  # Session-specific idempotency
    REQUEST = "REQUEST"  # Request-specific idempotency


@dataclass
class IdempotencyKey:
    """Idempotency key information"""

    key: str
    scope: IdempotencyScope
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    operation_type: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IdempotencyRecord:
    """Idempotency operation record"""

    key: str
    status: IdempotencyStatus
    request_hash: str
    request_data: Dict[str, Any]
    response_data: Optional[Dict[str, Any]] = None
    error_data: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    processing_time_ms: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class IdempotencyManager:
    """
    Production-Ready Idempotency Manager
    Implements comprehensive idempotency with Redis storage and expiration
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

        # Configuration
        self.default_ttl_hours = 24  # Default TTL for idempotency records
        self.max_ttl_days = 30  # Maximum TTL allowed
        self.cleanup_interval_hours = 6  # Cleanup interval for expired records
        self.max_request_size_kb = 100  # Maximum request size to store
        self.max_response_size_kb = 500  # Maximum response size to store

        # Redis keys
        self.idempotency_prefix = "idempotency:"
        self.key_index_prefix = "idempotency_key:"
        self.cleanup_lock_key = "idempotency_cleanup_lock"

        logger.info("Idempotency Manager initialized")

    def generate_idempotency_key(
        self,
        operation_type: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        scope: IdempotencyScope = IdempotencyScope.USER,
        custom_key: Optional[str] = None,
    ) -> IdempotencyKey:
        """
        Generate idempotency key with proper scope and validation
        """
        if custom_key:
            # Use provided custom key
            key = custom_key
        else:
            # Generate key based on operation and context
            key_parts = [operation_type]

            if scope == IdempotencyScope.USER and user_id:
                key_parts.append(f"user:{user_id}")
            elif scope == IdempotencyScope.SESSION and session_id:
                key_parts.append(f"session:{session_id}")
            elif scope == IdempotencyScope.GLOBAL:
                pass  # No additional context for global scope

            # Add timestamp for uniqueness
            key_parts.append(str(int(datetime.now().timestamp())))

            key = ":".join(key_parts)

        # Create idempotency key object
        idempotency_key = IdempotencyKey(
            key=key,
            scope=scope,
            user_id=user_id,
            session_id=session_id,
            operation_type=operation_type,
            expires_at=datetime.now() + timedelta(hours=self.default_ttl_hours),
        )

        return idempotency_key

    def hash_request_data(self, request_data: Dict[str, Any]) -> str:
        """
        Generate hash for request data to detect identical requests
        """
        try:
            # Normalize request data for consistent hashing
            normalized_data = self._normalize_request_data(request_data)

            # Convert to JSON string
            json_str = json.dumps(
                normalized_data, sort_keys=True, separators=(",", ":")
            )

            # Generate SHA-256 hash
            hash_value = hashlib.sha256(json_str.encode()).hexdigest()

            return hash_value

        except Exception as e:
            logger.error(f"Error hashing request data: {e}")
            # Fallback to simple hash
            return str(hash(str(request_data)))

    async def check_idempotency(
        self, idempotency_key: str, request_data: Dict[str, Any]
    ) -> Optional[IdempotencyRecord]:
        """
        Check if operation with idempotency key already exists
        """
        try:
            # Generate request hash
            request_hash = self.hash_request_data(request_data)

            # Get idempotency record
            record_key = f"{self.idempotency_prefix}{idempotency_key}"
            record_data = self.redis.get(record_key)

            if not record_data:
                return None  # No existing record

            # Parse record
            record_dict = json.loads(record_data)

            # Check if record is expired
            if record_dict.get("expires_at"):
                expires_at = datetime.fromisoformat(record_dict["expires_at"])
                if datetime.now() > expires_at:
                    # Mark as expired and cleanup
                    await self._mark_record_expired(idempotency_key)
                    return None

            # Check if request hash matches (detect duplicate requests)
            if record_dict.get("request_hash") != request_hash:
                # Different request data for same key - potential security issue
                await audit_logger.log_security_violation(
                    violation_type="idempotency_key_collision",
                    request_data={
                        "idempotency_key": idempotency_key,
                        "expected_hash": record_dict.get("request_hash"),
                        "actual_hash": request_hash,
                    },
                )
                return None

            # Create record object
            record = IdempotencyRecord(
                key=record_dict["key"],
                status=IdempotencyStatus(record_dict["status"]),
                request_hash=record_dict["request_hash"],
                request_data=record_dict["request_data"],
                response_data=record_dict.get("response_data"),
                error_data=record_dict.get("error_data"),
                created_at=datetime.fromisoformat(record_dict["created_at"]),
                updated_at=datetime.fromisoformat(record_dict["updated_at"]),
                completed_at=(
                    datetime.fromisoformat(record_dict["completed_at"])
                    if record_dict.get("completed_at")
                    else None
                ),
                expires_at=(
                    datetime.fromisoformat(record_dict["expires_at"])
                    if record_dict.get("expires_at")
                    else None
                ),
                processing_time_ms=record_dict.get("processing_time_ms"),
                metadata=record_dict.get("metadata", {}),
            )

            # Log idempotency hit
            await audit_logger.log_event(
                event_type=EventType.IDEMPOTENT_REQUEST_DETECTED,
                level=LogLevel.INFO,
                request_data={
                    "idempotency_key": idempotency_key,
                    "status": record.status.value,
                    "processing_time_ms": record.processing_time_ms,
                },
            )

            return record

        except Exception as e:
            logger.error(f"Error checking idempotency: {e}")
            return None

    async def create_idempotency_record(
        self,
        idempotency_key: str,
        request_data: Dict[str, Any],
        ttl_hours: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Create new idempotency record
        """
        try:
            # Validate request size
            request_size = len(json.dumps(request_data).encode())
            if request_size > self.max_request_size_kb * 1024:
                raise ValueError(
                    f"Request too large: {request_size} bytes (max: {self.max_request_size_kb * 1024})"
                )

            # Set TTL
            if ttl_hours is None:
                ttl_hours = self.default_ttl_hours
            elif ttl_hours > self.max_ttl_days * 24:
                ttl_hours = self.max_ttl_days * 24

            expires_at = datetime.now() + timedelta(hours=ttl_hours)

            # Generate request hash
            request_hash = self.hash_request_data(request_data)

            # Create record
            record = IdempotencyRecord(
                key=idempotency_key,
                status=IdempotencyStatus.PENDING,
                request_hash=request_hash,
                request_data=request_data,
                expires_at=expires_at,
                metadata=metadata or {},
            )

            # Store in Redis with expiration
            record_key = f"{self.idempotency_prefix}{idempotency_key}"
            record_data = {
                "key": record.key,
                "status": record.status.value,
                "request_hash": record.request_hash,
                "request_data": record.request_data,
                "created_at": record.created_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
                "expires_at": record.expires_at.isoformat(),
                "metadata": record.metadata,
            }

            success = self.redis.setex(
                record_key,
                ttl_hours * 3600,  # Convert hours to seconds
                json.dumps(record_data),
            )

            if success:
                # Add to key index for cleanup
                await self._add_to_key_index(idempotency_key, expires_at)

                await audit_logger.log_event(
                    event_type=EventType.IDEMPOTENCY_RECORD_CREATED,
                    level=LogLevel.DEBUG,
                    request_data={
                        "idempotency_key": idempotency_key,
                        "ttl_hours": ttl_hours,
                    },
                )

                return True
            else:
                return False

        except Exception as e:
            logger.error(f"Error creating idempotency record: {e}")
            return False

    async def update_idempotency_record(
        self,
        idempotency_key: str,
        status: IdempotencyStatus,
        response_data: Optional[Dict[str, Any]] = None,
        error_data: Optional[Dict[str, Any]] = None,
        processing_time_ms: Optional[int] = None,
    ) -> bool:
        """
        Update existing idempotency record
        """
        try:
            # Get existing record
            record_key = f"{self.idempotency_prefix}{idempotency_key}"
            existing_data = self.redis.get(record_key)

            if not existing_data:
                return False  # Record doesn't exist

            record_dict = json.loads(existing_data)

            # Validate response size
            if response_data:
                response_size = len(json.dumps(response_data).encode())
                if response_size > self.max_response_size_kb * 1024:
                    logger.warning(
                        f"Response too large, truncating: {response_size} bytes"
                    )
                    # Truncate response data
                response_data = self._truncate_large_data(
                    response_data, self.max_response_size_kb * 1024
                )

            # Update record
            record_dict.update(
                {
                    "status": status.value,
                    "updated_at": datetime.now().isoformat(),
                    "processing_time_ms": processing_time_ms,
                }
            )

            if status in [IdempotencyStatus.COMPLETED, IdempotencyStatus.FAILED]:
                record_dict["completed_at"] = datetime.now().isoformat()

            if response_data:
                record_dict["response_data"] = response_data

            if error_data:
                record_dict["error_data"] = error_data

            # Store updated record
            success = self.redis.set(
                record_key,
                json.dumps(record_data),
                xx=True,  # Only update if key exists
            )

            if success:
                await audit_logger.log_event(
                    event_type=EventType.IDEMPOTENCY_RECORD_UPDATED,
                    level=LogLevel.DEBUG,
                    request_data={
                        "idempotency_key": idempotency_key,
                        "status": status.value,
                        "processing_time_ms": processing_time_ms,
                    },
                )

                return True
            else:
                return False

        except Exception as e:
            logger.error(f"Error updating idempotency record: {e}")
            return False

    async def get_response(
        self, operation_type: str, idempotency_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached response for idempotent operation
        """
        try:
            record = await self.check_idempotency(idempotency_key, {})

            if not record:
                return None

            if record.status != IdempotencyStatus.COMPLETED:
                return None

            return record.response_data

        except Exception as e:
            logger.error(f"Error getting cached response: {e}")
            return None

    async def store_response(
        self, operation_type: str, idempotency_key: str, response_data: Dict[str, Any]
    ) -> bool:
        """
        Store response for idempotent operation
        """
        try:
            return await self.update_idempotency_record(
                idempotency_key=idempotency_key,
                status=IdempotencyStatus.COMPLETED,
                response_data=response_data,
            )

        except Exception as e:
            logger.error(f"Error storing response: {e}")
            return False

    def idempotent(
        self,
        operation_type: str,
        key_param: str = "idempotency_key",
        ttl_hours: Optional[int] = None,
        scope: IdempotencyScope = IdempotencyScope.USER,
    ):
        """
        Decorator for making functions idempotent
        """

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract idempotency key
                idempotency_key = kwargs.get(key_param)

                if not idempotency_key:
                    # Generate key if not provided
                    user_id = kwargs.get("user_id")
                    session_id = kwargs.get("session_id")

                    key_obj = self.generate_idempotency_key(
                        operation_type=operation_type,
                        user_id=user_id,
                        session_id=session_id,
                        scope=scope,
                    )
                    idempotency_key = key_obj.key

                    # Add to kwargs
                    kwargs[key_param] = idempotency_key

                # Prepare request data for hashing
                request_data = {
                    "args": args,
                    "kwargs": {k: v for k, v in kwargs.items() if k != key_param},
                }

                # Check idempotency
                existing_record = await self.check_idempotency(
                    idempotency_key, request_data
                )

                if existing_record:
                    if existing_record.status == IdempotencyStatus.COMPLETED:
                        # Return cached response
                        return existing_record.response_data
                    elif existing_record.status == IdempotencyStatus.PROCESSING:
                        # Wait for completion (with timeout)
                        return await self._wait_for_completion(
                            idempotency_key, timeout_seconds=30
                        )
                    elif existing_record.status == IdempotencyStatus.FAILED:
                        # Return cached error
                        raise Exception(
                            f"Operation failed: {existing_record.error_data}"
                        )
                    else:
                        # Record in unknown state, proceed with execution
                        pass

                # Create new record
                await self.create_idempotency_record(
                    idempotency_key=idempotency_key,
                    request_data=request_data,
                    ttl_hours=ttl_hours,
                )

                # Mark as processing
                await self.update_idempotency_record(
                    idempotency_key=idempotency_key, status=IdempotencyStatus.PROCESSING
                )

                start_time = datetime.now()

                try:
                    # Execute function
                    result = await func(*args, **kwargs)

                    processing_time = int(
                        (datetime.now() - start_time).total_seconds() * 1000
                    )

                    # Store successful result
                    await self.update_idempotency_record(
                        idempotency_key=idempotency_key,
                        status=IdempotencyStatus.COMPLETED,
                        response_data=(
                            result if isinstance(result, dict) else {"result": result}
                        ),
                        processing_time_ms=processing_time,
                    )

                    return result

                except Exception as e:
                    processing_time = int(
                        (datetime.now() - start_time).total_seconds() * 1000
                    )

                    # Store error
                    await self.update_idempotency_record(
                        idempotency_key=idempotency_key,
                        status=IdempotencyStatus.FAILED,
                        error_data={"error": str(e), "type": type(e).__name__},
                        processing_time_ms=processing_time,
                    )

                    raise

            return wrapper

        return decorator

    async def _wait_for_completion(
        self, idempotency_key: str, timeout_seconds: int = 30
    ) -> Any:
        """Wait for idempotent operation to complete"""
        start_time = datetime.now()

        while (datetime.now() - start_time).total_seconds() < timeout_seconds:
            record = await self.check_idempotency(idempotency_key, {})

            if record and record.status == IdempotencyStatus.COMPLETED:
                return record.response_data
            elif record and record.status == IdempotencyStatus.FAILED:
                raise Exception(f"Operation failed: {record.error_data}")

            await asyncio.sleep(0.1)  # Wait 100ms

        raise TimeoutError(
            f"Operation did not complete within {timeout_seconds} seconds"
        )

    async def _add_to_key_index(self, idempotency_key: str, expires_at: datetime):
        """Add key to index for cleanup"""
        try:
            index_key = f"{self.key_index_prefix}{expires_at.strftime('%Y%m%d')}"
            self.redis.sadd(index_key, idempotency_key)
            self.redis.expireat(index_key, expires_at)
        except Exception as e:
            logger.error(f"Error adding to key index: {e}")

    async def _mark_record_expired(self, idempotency_key: str):
        """Mark record as expired"""
        try:
            await self.update_idempotency_record(
                idempotency_key=idempotency_key, status=IdempotencyStatus.EXPIRED
            )
        except Exception as e:
            logger.error(f"Error marking record expired: {e}")

    def _normalize_request_data(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize request data for consistent hashing"""
        try:
            # Remove fields that shouldn't affect idempotency
            normalized = {}

            for key, value in request_data.items():
                # Skip timestamp fields
                if key in ["timestamp", "created_at", "updated_at"]:
                    continue

                # Normalize values
                if isinstance(value, dict):
                    normalized[key] = self._normalize_request_data(value)
                elif isinstance(value, list):
                    normalized[key] = [
                        (
                            self._normalize_request_data(item)
                            if isinstance(item, dict)
                            else item
                        )
                        for item in value
                    ]
                elif isinstance(value, (int, float, str, bool)) or value is None:
                    normalized[key] = value
                else:
                    # Convert other types to string
                    normalized[key] = str(value)

            return normalized

        except Exception as e:
            logger.error(f"Error normalizing request data: {e}")
            return request_data

    def _truncate_large_data(
        self, data: Dict[str, Any], max_size: int
    ) -> Dict[str, Any]:
        """Truncate large data to fit size limits"""
        try:
            data_str = json.dumps(data)
            if len(data_str.encode()) <= max_size:
                return data

            # Truncate by removing less important fields
            truncated = data.copy()

            # Remove metadata first
            if "metadata" in truncated:
                del truncated["metadata"]

            # Remove audit fields
            audit_fields = ["audit_log", "debug_info", "trace"]
            for field in audit_fields:
                if field in truncated:
                    del truncated[field]

            # Check size again
            if len(json.dumps(truncated).encode()) <= max_size:
                return truncated

            # If still too large, truncate string fields
            for key, value in truncated.items():
                if isinstance(value, str) and len(value) > 1000:
                    truncated[key] = value[:1000] + "...[truncated]"

            return truncated

        except Exception as e:
            logger.error(f"Error truncating data: {e}")
            return {"error": "Data too large to store"}

    async def cleanup_expired_records(self) -> int:
        """Clean up expired idempotency records"""
        try:
            # Acquire cleanup lock
            lock_acquired = self.redis.set(
                self.cleanup_lock_key, "locked", nx=True, ex=3600  # 1 hour lock
            )

            if not lock_acquired:
                return 0  # Cleanup already running

            try:
                cleaned_count = 0
                current_date = datetime.now().strftime("%Y%m%d")

                # Check past dates
                for days_ago in range(1, 32):  # Check last 31 days
                    date_key = f"{self.key_index_prefix}{(datetime.now() - timedelta(days=days_ago)).strftime('%Y%m%d')}"

                    keys = self.redis.smembers(date_key)

                    for key in keys:
                        record_key = f"{self.idempotency_prefix}{key}"
                        record_data = self.redis.get(record_key)

                        if record_data:
                            record_dict = json.loads(record_data)

                            if record_dict.get("expires_at"):
                                expires_at = datetime.fromisoformat(
                                    record_dict["expires_at"]
                                )

                                if datetime.now() > expires_at:
                                    # Delete expired record
                                    self.redis.delete(record_key)
                                    cleaned_count += 1

                    # Clean up index key
                    self.redis.delete(date_key)

                await audit_logger.log_event(
                    event_type=EventType.IDEMPOTENCY_CLEANUP_COMPLETED,
                    level=LogLevel.INFO,
                    request_data={"cleaned_count": cleaned_count},
                )

                return cleaned_count

            finally:
                # Release cleanup lock
                self.redis.delete(self.cleanup_lock_key)

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0

    async def health_check(self) -> Dict[str, Any]:
        """Health check for idempotency manager"""
        try:
            # Check Redis connection
            try:
                self.redis.ping()
                redis_healthy = True
            except Exception as e:
                redis_healthy = False
                redis_error = str(e)

            # Check active records
            try:
                active_keys = self.redis.keys(f"{self.idempotency_prefix}*")
                active_records = len(active_keys)
            except Exception:
                active_records = 0

            # Check index size
            try:
                index_keys = self.redis.keys(f"{self.key_index_prefix}*")
                index_size = len(index_keys)
            except Exception:
                index_size = 0

            overall_healthy = redis_healthy

            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "message": (
                    "Idempotency manager is operational"
                    if overall_healthy
                    else "Idempotency manager has issues"
                ),
                "features": {
                    "request_hashing": True,
                    "response_caching": True,
                    "automatic_cleanup": True,
                    "decorator_support": True,
                    "size_limits": True,
                    "audit_logging": True,
                },
                "configuration": {
                    "default_ttl_hours": self.default_ttl_hours,
                    "max_ttl_days": self.max_ttl_days,
                    "max_request_size_kb": self.max_request_size_kb,
                    "max_response_size_kb": self.max_response_size_kb,
                    "cleanup_interval_hours": self.cleanup_interval_hours,
                },
                "runtime": {"active_records": active_records, "index_size": index_size},
                "dependencies": {
                    "redis": "healthy" if redis_healthy else f"unhealthy: {redis_error}"
                },
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "error": str(e),
            }


# Global idempotency manager instance
idempotency_manager = None


def get_idempotency_manager(redis_client: redis.Redis) -> IdempotencyManager:
    """Get or create idempotency manager instance"""
    global idempotency_manager
    if idempotency_manager is None:
        idempotency_manager = IdempotencyManager(redis_client)
    return idempotency_manager
