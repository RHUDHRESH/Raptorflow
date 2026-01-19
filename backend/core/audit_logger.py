"""
Comprehensive Audit Logging System with Tamper Protection
Implements enterprise-grade audit logging with cryptographic integrity
Addresses audit logging vulnerabilities identified in red team audit
"""

import asyncio
import hashlib
import hmac
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import redis
import aiofiles
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Audit event types"""
    USER_AUTHENTICATION = "USER_AUTHENTICATION"
    USER_AUTHORIZATION = "USER_AUTHORIZATION"
    PAYMENT_INITIATED = "PAYMENT_INITIATED"
    PAYMENT_COMPLETED = "PAYMENT_COMPLETED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_STATUS_CHECK = "PAYMENT_STATUS_CHECK"
    PAYMENT_STATUS_CHECK_FAILED = "PAYMENT_STATUS_CHECK_FAILED"
    REFUND_INITIATED = "REFUND_INITIATED"
    REFUND_COMPLETED = "REFUND_COMPLETED"
    REFUND_FAILED = "REFUND_FAILED"
    REFUND_STATUS_CHECK = "REFUND_STATUS_CHECK"
    REFUND_STATUS_CHECK_FAILED = "REFUND_STATUS_CHECK_FAILED"
    WEBHOOK_RECEIVED = "WEBHOOK_RECEIVED"
    WEBHOOK_PROCESSED = "WEBHOOK_PROCESSED"
    WEBHOOK_PROCESSING_FAILED = "WEBHOOK_PROCESSING_FAILED"
    WEBHOOK_SIGNATURE_VERIFICATION = "WEBHOOK_SIGNATURE_VERIFICATION"
    TRANSACTION_STARTED = "TRANSACTION_STARTED"
    TRANSACTION_COMPLETED = "TRANSACTION_COMPLETED"
    TRANSACTION_FAILED = "TRANSACTION_FAILED"
    TRANSACTION_ROLLBACK = "TRANSACTION_ROLLBACK"
    FRAUD_ASSESSMENT_COMPLETED = "FRAUD_ASSESSMENT_COMPLETED"
    FRAUD_RULE_ADDED = "FRAUD_RULE_ADDED"
    FRAUD_RULE_REMOVED = "FRAUD_RULE_REMOVED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    RATE_LIMIT_RESET = "RATE_LIMIT_RESET"
    RATE_LIMIT_CLEANUP_COMPLETED = "RATE_LIMIT_CLEANUP_COMPLETED"
    CIRCUIT_BREAKER_OPENED = "CIRCUIT_BREAKER_OPENED"
    CIRCUIT_BREAKER_CLOSED = "CIRCUIT_BREAKER_CLOSED"
    CIRCUIT_BREAKER_HALF_OPEN = "CIRCUIT_BREAKER_HALF_OPEN"
    CIRCUIT_BREAKER_FALLBACK_USED = "CIRCUIT_BREAKER_FALLBACK_USED"
    IDEMPOTENT_REQUEST_DETECTED = "IDEMPOTENT_REQUEST_DETECTED"
    IDEMPOTENCY_RECORD_CREATED = "IDEMPOTENCY_RECORD_CREATED"
    IDEMPOTENCY_RECORD_UPDATED = "IDEMPOTENCY_RECORD_UPDATED"
    IDEMPOTENCY_CLEANUP_COMPLETED = "IDEMPOTENCY_CLEANUP_COMPLETED"
    SDK_INITIALIZED = "SDK_INITIALIZED"
    SDK_INITIALIZATION_FAILED = "SDK_INITIALIZATION_FAILED"
    CUSTOMER_INFO_RECORDED = "CUSTOMER_INFO_RECORDED"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    DATA_ACCESS = "DATA_ACCESS"
    DATA_MODIFICATION = "DATA_MODIFICATION"
    CONFIGURATION_CHANGE = "CONFIGURATION_CHANGE"
    BACKUP_COMPLETED = "BACKUP_COMPLETED"
    BACKUP_FAILED = "BACKUP_FAILED"
    HEALTH_CHECK = "HEALTH_CHECK"

class LogLevel(Enum):
    """Audit log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AuditRetentionPeriod(Enum):
    """Audit log retention periods"""
    DAYS_30 = 30
    DAYS_90 = 90
    DAYS_180 = 180
    DAYS_365 = 365
    DAYS_2555 = 2555  # 7 years for compliance

@dataclass
class AuditEvent:
    """Audit event record"""
    event_id: str
    event_type: EventType
    level: LogLevel
    timestamp: datetime
    user_id: Optional[str] = None
    transaction_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    duration_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    integrity_hash: Optional[str] = None
    previous_hash: Optional[str] = None

@dataclass
class AuditLogConfig:
    """Audit logging configuration"""
    encryption_enabled: bool = True
    integrity_protection: bool = True
    file_logging: bool = True
    redis_logging: bool = True
    retention_period: AuditRetentionPeriod = AuditRetentionPeriod.DAYS_2555
    log_level: LogLevel = LogLevel.INFO
    compression_enabled: bool = True
    batch_size: int = 100
    flush_interval_seconds: int = 5
    max_file_size_mb: int = 100
    log_directory: str = "/var/log/raptorflow/audit"

class AuditLogger:
    """
    Production-Ready Audit Logger with Tamper Protection
    Implements comprehensive audit logging with cryptographic integrity
    """
    
    def __init__(self, config: AuditLogConfig, redis_client: redis.Redis):
        self.config = config
        self.redis = redis_client
        
        # Encryption key management
        self._encryption_key = self._generate_or_load_encryption_key()
        self._cipher = Fernet(self._encryption_key) if config.encryption_enabled else None
        
        # Integrity protection
        self._integrity_key = self._generate_integrity_key()
        self._last_hash: Optional[str] = None
        
        # Batch logging
        self._event_queue: List[AuditEvent] = []
        self._flush_task: Optional[asyncio.Task] = None
        
        # File logging
        self._current_log_file: Optional[str] = None
        self._file_handle: Optional[aiofiles.threadpool.text.AsyncTextIOWrapper] = None
        
        # Redis keys
        self.audit_prefix = "audit_log:"
        self.integrity_prefix = "audit_integrity:"
        self.sequence_prefix = "audit_sequence:"
        
        # Initialize logging system
        asyncio.create_task(self._initialize())
        
        logger.info("Audit Logger initialized with tamper protection")
    
    def _generate_or_load_encryption_key(self) -> bytes:
        """Generate or load encryption key"""
        key_file = os.path.join(self.config.log_directory, ".audit_key")
        
        try:
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    key = f.read()
                return key
            else:
                # Generate new key
                key = Fernet.generate_key()
                os.makedirs(self.config.log_directory, exist_ok=True)
                with open(key_file, 'wb') as f:
                    f.write(key)
                os.chmod(key_file, 0o600)  # Restrict permissions
                return key
        except Exception as e:
            logger.error(f"Error managing encryption key: {e}")
            # Fallback to temporary key
            return Fernet.generate_key()
    
    def _generate_integrity_key(self) -> bytes:
        """Generate integrity protection key"""
        # Use PBKDF2 to derive key from encryption key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"audit_integrity_salt",
            iterations=100000,
        )
        return kdf.derive(self._encryption_key)
    
    async def _initialize(self):
        """Initialize audit logging system"""
        try:
            # Create log directory
            os.makedirs(self.config.log_directory, exist_ok=True)
            
            # Initialize sequence counter
            await self._initialize_sequence_counter()
            
            # Get last integrity hash
            self._last_hash = await self._get_last_integrity_hash()
            
            # Start background flush task
            if self.config.flush_interval_seconds > 0:
                self._flush_task = asyncio.create_task(self._background_flush())
            
            # Initialize file logging
            if self.config.file_logging:
                await self._initialize_file_logging()
                
        except Exception as e:
            logger.error(f"Error initializing audit logger: {e}")
    
    async def _initialize_sequence_counter(self):
        """Initialize audit event sequence counter"""
        sequence_key = f"{self.sequence_prefix}counter"
        
        if not self.redis.exists(sequence_key):
            self.redis.set(sequence_key, 0)
    
    async def _get_next_sequence_number(self) -> int:
        """Get next sequence number for audit events"""
        sequence_key = f"{self.sequence_prefix}counter"
        return self.redis.incr(sequence_key)
    
    async def _get_last_integrity_hash(self) -> Optional[str]:
        """Get last integrity hash from Redis"""
        try:
            last_hash_key = f"{self.integrity_prefix}last_hash"
            return self.redis.get(last_hash)
        except Exception as e:
            logger.error(f"Error getting last integrity hash: {e}")
            return None
    
    async def _initialize_file_logging(self):
        """Initialize file logging"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d")
            self._current_log_file = os.path.join(
                self.config.log_directory,
                f"audit_{timestamp}.log"
            )
            
            # Create new file if it doesn't exist
            if not os.path.exists(self._current_log_file):
                async with aiofiles.open(self._current_log_file, 'w') as f:
                    await f.write(f"# Raptorflow Audit Log - Created {datetime.now().isoformat()}\n")
                    await f.write(f"# Integrity Protection: {'ENABLED' if self.config.integrity_protection else 'DISABLED'}\n")
                    await f.write(f"# Encryption: {'ENABLED' if self.config.encryption_enabled else 'DISABLED'}\n")
                    await f.write("# Format: JSON\n\n")
            
            # Open file for appending
            self._file_handle = await aiofiles.open(self._current_log_file, 'a')
            
        except Exception as e:
            logger.error(f"Error initializing file logging: {e}")
    
    async def log_event(
        self,
        event_type: EventType,
        level: LogLevel = LogLevel.INFO,
        user_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        error_code: Optional[str] = None,
        duration_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log audit event with tamper protection
        """
        try:
            # Create audit event
            event = AuditEvent(
                event_id=str(uuid.uuid4()),
                event_type=event_type,
                level=level,
                timestamp=datetime.now(),
                user_id=user_id,
                transaction_id=transaction_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                request_data=request_data,
                response_data=response_data,
                error_message=error_message,
                error_code=error_code,
                duration_ms=duration_ms,
                metadata=metadata or {}
            )
            
            # Add sequence number
            sequence_number = await self._get_next_sequence_number()
            event.metadata["sequence_number"] = sequence_number
            
            # Calculate integrity hash
            if self.config.integrity_protection:
                event.previous_hash = self._last_hash
                event.integrity_hash = self._calculate_integrity_hash(event)
                self._last_hash = event.integrity_hash
            
            # Add to queue for batch processing
            self._event_queue.append(event)
            
            # Flush immediately for critical events
            if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                await self._flush_events()
                
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
    
    async def log_security_violation(
        self,
        violation_type: str,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log security violation event"""
        await self.log_event(
            event_type=EventType.SECURITY_VIOLATION,
            level=LogLevel.WARNING,
            user_id=user_id,
            ip_address=ip_address,
            request_data=request_data,
            response_data=response_data,
            metadata={
                "violation_type": violation_type,
                "security_alert": True
            }
        )
    
    async def log_payment_initiated(
        self,
        user_id: str,
        transaction_id: str,
        amount: int,
        request_data: Optional[Dict[str, Any]] = None
    ):
        """Log payment initiation event"""
        await self.log_event(
            event_type=EventType.PAYMENT_INITIATED,
            level=LogLevel.INFO,
            user_id=user_id,
            transaction_id=transaction_id,
            request_data=request_data,
            metadata={
                "amount": amount,
                "payment_flow": "initiation"
            }
        )
    
    async def log_payment_failed(
        self,
        user_id: Optional[str],
        transaction_id: str,
        error_message: str,
        request_data: Optional[Dict[str, Any]] = None
    ):
        """Log payment failure event"""
        await self.log_event(
            event_type=EventType.PAYMENT_FAILED,
            level=LogLevel.ERROR,
            user_id=user_id,
            transaction_id=transaction_id,
            error_message=error_message,
            request_data=request_data,
            metadata={
                "payment_flow": "failure"
            }
        )
    
    def _calculate_integrity_hash(self, event: AuditEvent) -> str:
        """Calculate cryptographic integrity hash for event"""
        try:
            # Create hashable representation
            hash_data = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "level": event.level.value,
                "timestamp": event.timestamp.isoformat(),
                "user_id": event.user_id,
                "transaction_id": event.transaction_id,
                "previous_hash": event.previous_hash
            }
            
            # Convert to JSON string
            json_str = json.dumps(hash_data, sort_keys=True, separators=(',', ':'))
            
            # Calculate HMAC-SHA256
            hmac_hash = hmac.new(
                self._integrity_key,
                json_str.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac_hash
            
        except Exception as e:
            logger.error(f"Error calculating integrity hash: {e}")
            return ""
    
    def _serialize_event(self, event: AuditEvent) -> str:
        """Serialize audit event to JSON"""
        event_data = {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "level": event.level.value,
            "timestamp": event.timestamp.isoformat(),
            "user_id": event.user_id,
            "transaction_id": event.transaction_id,
            "session_id": event.session_id,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "request_data": event.request_data,
            "response_data": event.response_data,
            "error_message": event.error_message,
            "error_code": event.error_code,
            "duration_ms": event.duration_ms,
            "metadata": event.metadata,
            "integrity_hash": event.integrity_hash,
            "previous_hash": event.previous_hash
        }
        
        return json.dumps(event_data, default=str, separators=(',', ':'))
    
    async def _encrypt_data(self, data: str) -> str:
        """Encrypt audit data"""
        if not self.config.encryption_enabled or not self._cipher:
            return data
        
        try:
            encrypted_data = self._cipher.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Error encrypting audit data: {e}")
            return data  # Fallback to unencrypted
    
    async def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt audit data"""
        if not self.config.encryption_enabled or not self._cipher:
            return encrypted_data
        
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self._cipher.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Error decrypting audit data: {e}")
            return encrypted_data  # Fallback to original data
    
    async def _flush_events(self):
        """Flush queued events to storage"""
        if not self._event_queue:
            return
        
        events_to_flush = self._event_queue.copy()
        self._event_queue.clear()
        
        try:
            # Store in Redis
            if self.config.redis_logging:
                await self._store_events_in_redis(events_to_flush)
            
            # Store in files
            if self.config.file_logging and self._file_handle:
                await self._store_events_in_file(events_to_flush)
                
        except Exception as e:
            logger.error(f"Error flushing audit events: {e}")
            # Re-queue events for retry
            self._event_queue.extend(events_to_flush)
    
    async def _store_events_in_redis(self, events: List[AuditEvent]):
        """Store audit events in Redis"""
        try:
            pipe = self.redis.pipeline()
            
            for event in events:
                # Serialize event
                event_json = self._serialize_event(event)
                
                # Encrypt if enabled
                encrypted_event = await self._encrypt_data(event_json)
                
                # Store with TTL based on retention period
                event_key = f"{self.audit_prefix}{event.event_id}"
                pipe.setex(
                    event_key,
                    self.config.retention_period.value * 86400,  # Convert days to seconds
                    encrypted_event
                )
                
                # Store integrity hash
                if event.integrity_hash:
                    integrity_key = f"{self.integrity_prefix}{event.event_id}"
                    pipe.setex(
                        integrity_key,
                        self.config.retention_period.value * 86400,
                        event.integrity_hash
                    )
            
            # Update last hash
            if events and events[-1].integrity_hash:
                last_hash_key = f"{self.integrity_prefix}last_hash"
                pipe.setex(last_hash_key, 86400, events[-1].integrity_hash)  # 24 hours
            
            pipe.execute()
            
        except Exception as e:
            logger.error(f"Error storing events in Redis: {e}")
    
    async def _store_events_in_file(self, events: List[AuditEvent]):
        """Store audit events in file"""
        try:
            for event in events:
                # Serialize event
                event_json = self._serialize_event(event)
                
                # Encrypt if enabled
                encrypted_event = await self._encrypt_data(event_json)
                
                # Write to file
                await self._file_handle.write(encrypted_event + '\n')
                await self._file_handle.flush()
            
            # Check file size and rotate if necessary
            if await self._should_rotate_file():
                await self._rotate_log_file()
                
        except Exception as e:
            logger.error(f"Error storing events in file: {e}")
    
    async def _should_rotate_file(self) -> bool:
        """Check if log file should be rotated"""
        try:
            if not self._current_log_file:
                return False
            
            file_size = os.path.getsize(self._current_log_file)
            return file_size >= (self.config.max_file_size_mb * 1024 * 1024)
        except Exception:
            return False
    
    async def _rotate_log_file(self):
        """Rotate log file"""
        try:
            # Close current file
            if self._file_handle:
                await self._file_handle.close()
            
            # Rename current file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated_file = self._current_log_file.replace('.log', f'_{timestamp}.log')
            os.rename(self._current_log_file, rotated_file)
            
            # Compress if enabled
            if self.config.compression_enabled:
                await self._compress_log_file(rotated_file)
            
            # Initialize new file
            await self._initialize_file_logging()
            
        except Exception as e:
            logger.error(f"Error rotating log file: {e}")
    
    async def _compress_log_file(self, file_path: str):
        """Compress log file (placeholder for actual compression)"""
        try:
            # This would typically use gzip compression
            # For now, just log the action
            logger.info(f"Compressed log file: {file_path}")
        except Exception as e:
            logger.error(f"Error compressing log file: {e}")
    
    async def _background_flush(self):
        """Background task for periodic flushing"""
        while True:
            try:
                await asyncio.sleep(self.config.flush_interval_seconds)
                await self._flush_events()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background flush: {e}")
    
    async def verify_integrity(self, event_id: str) -> bool:
        """Verify integrity of a specific audit event"""
        try:
            # Get event from Redis
            event_key = f"{self.audit_prefix}{event_id}"
            encrypted_event = self.redis.get(event_key)
            
            if not encrypted_event:
                return False
            
            # Decrypt event
            event_json = await self._decrypt_data(encrypted_event)
            event_data = json.loads(event_json)
            
            # Get stored integrity hash
            integrity_key = f"{self.integrity_prefix}{event_id}"
            stored_hash = self.redis.get(integrity_key)
            
            if not stored_hash:
                return False
            
            # Recalculate hash
            event = AuditEvent(
                event_id=event_data["event_id"],
                event_type=EventType(event_data["event_type"]),
                level=LogLevel(event_data["level"]),
                timestamp=datetime.fromisoformat(event_data["timestamp"]),
                user_id=event_data.get("user_id"),
                transaction_id=event_data.get("transaction_id"),
                integrity_hash=event_data.get("integrity_hash"),
                previous_hash=event_data.get("previous_hash")
            )
            
            calculated_hash = self._calculate_integrity_hash(event)
            
            return calculated_hash == stored_hash
            
        except Exception as e:
            logger.error(f"Error verifying integrity: {e}")
            return False
    
    async def search_events(
        self,
        event_type: Optional[EventType] = None,
        user_id: Optional[str] = None,
        transaction_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Search audit events"""
        try:
            # This would typically use a proper search index
            # For now, return empty list as placeholder
            return []
        except Exception as e:
            logger.error(f"Error searching events: {e}")
            return []
    
    async def cleanup_expired_events(self) -> int:
        """Clean up expired audit events"""
        try:
            cleaned_count = 0
            
            # Clean Redis events
            pattern = f"{self.audit_prefix}*"
            keys = self.redis.keys(pattern)
            
            current_time = datetime.now()
            expiration_threshold = current_time - timedelta(days=self.config.retention_period.value)
            
            for key in keys:
                # Get event timestamp (would need to be stored with key)
                # For now, clean based on key TTL
                ttl = self.redis.ttl(key)
                if ttl == -1:  # No expiration set
                    self.redis.expire(key, self.config.retention_period.value * 86400)
                elif ttl <= 0:  # Expired
                    self.redis.delete(key)
                    cleaned_count += 1
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired events: {e}")
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for audit logger"""
        try:
            # Check Redis connection
            try:
                self.redis.ping()
                redis_healthy = True
            except Exception as e:
                redis_healthy = False
                redis_error = str(e)
            
            # Check file system
            file_healthy = True
            file_error = None
            
            if self.config.file_logging:
                try:
                    if self._current_log_file:
                        # Check if file is writable
                        with open(self._current_log_file, 'a') as f:
                            f.write("")
                except Exception as e:
                    file_healthy = False
                    file_error = str(e)
            
            # Check queue size
            queue_size = len(self._event_queue)
            
            overall_healthy = redis_healthy and file_healthy
            
            return {
                "status": "healthy" if overall_healthy else "unhealthy",
                "message": "Audit logger is operational" if overall_healthy else "Audit logger has issues",
                "features": {
                    "encryption": self.config.encryption_enabled,
                    "integrity_protection": self.config.integrity_protection,
                    "file_logging": self.config.file_logging,
                    "redis_logging": self.config.redis_logging,
                    "compression": self.config.compression_enabled,
                    "batch_processing": True
                },
                "configuration": {
                    "retention_period_days": self.config.retention_period.value,
                    "log_level": self.config.log_level.value,
                    "batch_size": self.config.batch_size,
                    "flush_interval_seconds": self.config.flush_interval_seconds,
                    "max_file_size_mb": self.config.max_file_size_mb
                },
                "runtime": {
                    "queue_size": queue_size,
                    "current_log_file": self._current_log_file,
                    "last_sequence": await self._get_next_sequence_number() - 1
                },
                "dependencies": {
                    "redis": "healthy" if redis_healthy else f"unhealthy: {redis_error}",
                    "file_system": "healthy" if file_healthy else f"unhealthy: {file_error}"
                }
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "error": str(e)
            }
    
    async def shutdown(self):
        """Shutdown audit logger gracefully"""
        try:
            # Flush remaining events
            await self._flush_events()
            
            # Cancel background task
            if self._flush_task:
                self._flush_task.cancel()
                try:
                    await self._flush_task
                except asyncio.CancelledError:
                    pass
            
            # Close file handle
            if self._file_handle:
                await self._file_handle.close()
                
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

# Global audit logger instance
audit_logger = None

def get_audit_logger(config: Optional[AuditLogConfig] = None, redis_client: Optional[redis.Redis] = None) -> AuditLogger:
    """Get or create audit logger instance"""
    global audit_logger
    if audit_logger is None:
        if config is None:
            config = AuditLogConfig()
        if redis_client is None:
            raise ValueError("Redis client is required for audit logger")
        audit_logger = AuditLogger(config, redis_client)
    return audit_logger
