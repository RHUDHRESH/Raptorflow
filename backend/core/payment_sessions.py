"""
Payment Session Manager - Secure Token Lifecycle Management
Enterprise-grade session management with security and compliance
"""

import logging
import json
import secrets
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import redis
import jwt
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import hashlib

logger = logging.getLogger(__name__)

class SessionStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    COMPROMISED = "compromised"

class TokenType(Enum):
    PAYMENT_SESSION = "payment_session"
    TRANSACTION_TOKEN = "transaction_token"
    REFUND_TOKEN = "refund_token"
    ADMIN_TOKEN = "admin_token"

class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PaymentSession:
    session_id: str
    user_id: str
    token_type: TokenType
    security_level: SecurityLevel
    created_at: datetime
    expires_at: datetime
    last_accessed: datetime
    ip_address: str
    user_agent: str
    device_fingerprint: Optional[str]
    metadata: Dict[str, Any]
    status: SessionStatus
    access_count: int
    max_access_count: int
    allowed_operations: List[str]

@dataclass
class SessionValidationResult:
    valid: bool
    session: Optional[PaymentSession] = None
    error: Optional[str] = None
    risk_score: float = 0.0
    warnings: List[str] = None

class PaymentSessionManager:
    """
    Secure payment session management with comprehensive security features
    """
    
    def __init__(self, redis_client: redis.Redis, config: Dict[str, Any]):
        self.redis = redis_client
        self.config = config
        
        # Security configuration
        self.session_secret_key = config.get('session_secret_key', '')
        self.token_expiry_minutes = {
            TokenType.PAYMENT_SESSION: config.get('payment_session_expiry', 30),
            TokenType.TRANSACTION_TOKEN: config.get('transaction_token_expiry', 10),
            TokenType.REFUND_TOKEN: config.get('refund_token_expiry', 60),
            TokenType.ADMIN_TOKEN: config.get('admin_token_expiry', 120)
        }
        
        self.max_sessions_per_user = config.get('max_sessions_per_user', 5)
        self.session_cleanup_interval = config.get('session_cleanup_interval', 300)  # 5 minutes
        self.max_access_attempts = config.get('max_access_attempts', 10)
        self.suspicious_activity_threshold = config.get('suspicious_activity_threshold', 3)
        
        # Initialize encryption
        self._initialize_encryption()
        
        # Background tasks
        self.cleanup_task = None
        self.is_running = False
    
    def _initialize_encryption(self):
        """Initialize encryption for session data"""
        try:
            # Generate encryption key from session secret
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'raptorflow_session_salt',
                iterations=100000,
                backend=default_backend()
            )
            self.encryption_key = kdf.derive(self.session_secret_key.encode())
            
            logger.info("Session encryption initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize session encryption: {e}")
            raise
    
    async def start_session_manager(self):
        """Start session management background tasks"""
        if self.is_running:
            return
        
        self.is_running = True
        self.cleanup_task = asyncio.create_task(self._session_cleanup_loop())
        logger.info("Payment session manager started")
    
    async def stop_session_manager(self):
        """Stop session management background tasks"""
        self.is_running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Payment session manager stopped")
    
    async def create_payment_session(
        self,
        user_id: str,
        token_type: TokenType,
        security_level: SecurityLevel = SecurityLevel.MEDIUM,
        ip_address: str = '',
        user_agent: str = '',
        device_fingerprint: str = None,
        metadata: Dict[str, Any] = None,
        allowed_operations: List[str] = None,
        custom_expiry_minutes: int = None
    ) -> str:
        """Create a new secure payment session"""
        try:
            # Generate secure session ID
            session_id = self._generate_secure_session_id()
            
            # Set expiry time
            expiry_minutes = custom_expiry_minutes or self.token_expiry_minutes.get(token_type, 30)
            expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
            
            # Check user session limits
            await self._enforce_session_limits(user_id)
            
            # Create session object
            session = PaymentSession(
                session_id=session_id,
                user_id=user_id,
                token_type=token_type,
                security_level=security_level,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                last_accessed=datetime.utcnow(),
                ip_address=ip_address,
                user_agent=user_agent,
                device_fingerprint=device_fingerprint,
                metadata=metadata or {},
                status=SessionStatus.ACTIVE,
                access_count=0,
                max_access_count=self._get_max_access_count(token_type, security_level),
                allowed_operations=allowed_operations or self._get_default_operations(token_type)
            )
            
            # Store session securely
            await self._store_session(session)
            
            # Log session creation
            await self._log_session_event('session_created', session_id, user_id, {
                'token_type': token_type.value,
                'security_level': security_level.value,
                'ip_address': ip_address
            })
            
            logger.info(f"Payment session created: {session_id} for user {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create payment session: {e}")
            raise
    
    async def validate_session(
        self,
        session_id: str,
        ip_address: str = '',
        user_agent: str = '',
        operation: str = None
    ) -> SessionValidationResult:
        """Validate a payment session"""
        try:
            # Retrieve session
            session = await self._get_session(session_id)
            
            if not session:
                return SessionValidationResult(
                    valid=False,
                    error="Session not found",
                    risk_score=0.8
                )
            
            warnings = []
            risk_score = 0.0
            
            # Check session status
            if session.status != SessionStatus.ACTIVE:
                return SessionValidationResult(
                    valid=False,
                    session=session,
                    error=f"Session is {session.status.value}",
                    risk_score=0.7
                )
            
            # Check expiry
            if datetime.utcnow() > session.expires_at:
                await self._revoke_session(session_id, "expired")
                return SessionValidationResult(
                    valid=False,
                    session=session,
                    error="Session expired",
                    risk_score=0.6
                )
            
            # Check access count
            if session.access_count >= session.max_access_count:
                await self._revoke_session(session_id, "access_limit_exceeded")
                return SessionValidationResult(
                    valid=False,
                    session=session,
                    error="Access limit exceeded",
                    risk_score=0.8
                )
            
            # Check IP address consistency
            if ip_address and session.ip_address and ip_address != session.ip_address:
                warnings.append("IP address changed")
                risk_score += 0.3
            
            # Check user agent consistency
            if user_agent and session.user_agent and user_agent != session.user_agent:
                warnings.append("User agent changed")
                risk_score += 0.2
            
            # Check operation permissions
            if operation and operation not in session.allowed_operations:
                return SessionValidationResult(
                    valid=False,
                    session=session,
                    error=f"Operation not allowed: {operation}",
                    risk_score=0.9
                )
            
            # Check for suspicious activity
            suspicious_score = await self._check_suspicious_activity(session_id, ip_address)
            risk_score += suspicious_score
            
            if suspicious_score > 0.5:
                warnings.append("Suspicious activity detected")
            
            # Update session access
            await self._update_session_access(session_id, ip_address, user_agent)
            
            # Determine if valid based on risk score
            is_valid = risk_score < 0.7
            
            return SessionValidationResult(
                valid=is_valid,
                session=session,
                error=None if is_valid else "High risk activity detected",
                risk_score=risk_score,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return SessionValidationResult(
                valid=False,
                error=f"Validation error: {str(e)}",
                risk_score=0.5
            )
    
    async def revoke_session(
        self,
        session_id: str,
        reason: str = "manual_revocation",
        revoked_by: str = None
    ) -> bool:
        """Revoke a payment session"""
        try:
            session = await self._get_session(session_id)
            if not session:
                return False
            
            await self._revoke_session(session_id, reason)
            
            # Log revocation
            await self._log_session_event('session_revoked', session_id, session.user_id, {
                'reason': reason,
                'revoked_by': revoked_by,
                'ip_address': session.ip_address
            })
            
            logger.info(f"Session revoked: {session_id} - Reason: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke session: {e}")
            return False
    
    async def revoke_user_sessions(
        self,
        user_id: str,
        reason: str = "user_sessions_revoked",
        revoked_by: str = None
    ) -> int:
        """Revoke all sessions for a user"""
        try:
            # Get all user sessions
            user_sessions = await self._get_user_sessions(user_id)
            
            revoked_count = 0
            for session in user_sessions:
                if await self.revoke_session(session.session_id, reason, revoked_by):
                    revoked_count += 1
            
            logger.info(f"Revoked {revoked_count} sessions for user {user_id}")
            return revoked_count
            
        except Exception as e:
            logger.error(f"Failed to revoke user sessions: {e}")
            return 0
    
    async def extend_session(
        self,
        session_id: str,
        additional_minutes: int = 30
    ) -> bool:
        """Extend session expiry time"""
        try:
            session = await self._get_session(session_id)
            if not session or session.status != SessionStatus.ACTIVE:
                return False
            
            # Extend expiry
            session.expires_at = datetime.utcnow() + timedelta(minutes=additional_minutes)
            await self._store_session(session)
            
            # Log extension
            await self._log_session_event('session_extended', session_id, session.user_id, {
                'additional_minutes': additional_minutes,
                'new_expiry': session.expires_at.isoformat()
            })
            
            logger.info(f"Session extended: {session_id} by {additional_minutes} minutes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to extend session: {e}")
            return False
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information (without sensitive data)"""
        try:
            session = await self._get_session(session_id)
            if not session:
                return None
            
            return {
                'session_id': session.session_id,
                'user_id': session.user_id,
                'token_type': session.token_type.value,
                'security_level': session.security_level.value,
                'created_at': session.created_at.isoformat(),
                'expires_at': session.expires_at.isoformat(),
                'last_accessed': session.last_accessed.isoformat(),
                'status': session.status.value,
                'access_count': session.access_count,
                'max_access_count': session.max_access_count,
                'allowed_operations': session.allowed_operations
            }
            
        except Exception as e:
            logger.error(f"Failed to get session info: {e}")
            return None
    
    async def get_user_sessions(
        self,
        user_id: str,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all sessions for a user"""
        try:
            sessions = await self._get_user_sessions(user_id)
            
            if active_only:
                sessions = [s for s in sessions if s.status == SessionStatus.ACTIVE]
            
            return [
                {
                    'session_id': s.session_id,
                    'token_type': s.token_type.value,
                    'security_level': s.security_level.value,
                    'created_at': s.created_at.isoformat(),
                    'expires_at': s.expires_at.isoformat(),
                    'last_accessed': s.last_accessed.isoformat(),
                    'status': s.status.value,
                    'access_count': s.access_count,
                    'ip_address': s.ip_address
                }
                for s in sessions
            ]
            
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []
    
    def _generate_secure_session_id(self) -> str:
        """Generate a cryptographically secure session ID"""
        return secrets.token_urlsafe(32)
    
    async def _enforce_session_limits(self, user_id: str):
        """Enforce session limits per user"""
        try:
            user_sessions = await self._get_user_sessions(user_id)
            active_sessions = [s for s in user_sessions if s.status == SessionStatus.ACTIVE]
            
            if len(active_sessions) >= self.max_sessions_per_user:
                # Revoke oldest session
                oldest_session = min(active_sessions, key=lambda s: s.created_at)
                await self._revoke_session(oldest_session.session_id, "session_limit_exceeded")
                
        except Exception as e:
            logger.error(f"Failed to enforce session limits: {e}")
    
    def _get_max_access_count(self, token_type: TokenType, security_level: SecurityLevel) -> int:
        """Get maximum access count based on token type and security level"""
        base_counts = {
            TokenType.PAYMENT_SESSION: 10,
            TokenType.TRANSACTION_TOKEN: 1,
            TokenType.REFUND_TOKEN: 5,
            TokenType.ADMIN_TOKEN: 50
        }
        
        multipliers = {
            SecurityLevel.LOW: 0.5,
            SecurityLevel.MEDIUM: 1.0,
            SecurityLevel.HIGH: 2.0,
            SecurityLevel.CRITICAL: 5.0
        }
        
        base = base_counts.get(token_type, 10)
        multiplier = multipliers.get(security_level, 1.0)
        
        return int(base * multiplier)
    
    def _get_default_operations(self, token_type: TokenType) -> List[str]:
        """Get default allowed operations for token type"""
        operations = {
            TokenType.PAYMENT_SESSION: ['initiate_payment', 'check_status'],
            TokenType.TRANSACTION_TOKEN: ['complete_transaction'],
            TokenType.REFUND_TOKEN: ['process_refund'],
            TokenType.ADMIN_TOKEN: ['admin_operations', 'view_reports']
        }
        
        return operations.get(token_type, [])
    
    async def _store_session(self, session: PaymentSession):
        """Store session data securely"""
        try:
            # Serialize session data
            session_data = asdict(session)
            session_data['created_at'] = session.created_at.isoformat()
            session_data['expires_at'] = session.expires_at.isoformat()
            session_data['last_accessed'] = session.last_accessed.isoformat()
            session_data['token_type'] = session.token_type.value
            session_data['security_level'] = session.security_level.value
            session_data['status'] = session.status.value
            
            # Encrypt sensitive data
            encrypted_data = await self._encrypt_session_data(session_data)
            
            # Store in Redis with TTL
            session_key = f"payment_session:{session.session_id}"
            await self.redis.setex(
                session_key,
                int((session.expires_at - datetime.utcnow()).total_seconds()) + 300,  # 5 min buffer
                encrypted_data
            )
            
            # Store user session index
            user_sessions_key = f"user_sessions:{session.user_id}"
            await self.redis.sadd(user_sessions_key, session.session_id)
            await self.redis.expire(user_sessions_key, 86400 * 7)  # 7 days
            
        except Exception as e:
            logger.error(f"Failed to store session: {e}")
            raise
    
    async def _get_session(self, session_id: str) -> Optional[PaymentSession]:
        """Retrieve and decrypt session data"""
        try:
            session_key = f"payment_session:{session_id}"
            encrypted_data = await self.redis.get(session_key)
            
            if not encrypted_data:
                return None
            
            # Decrypt session data
            session_data = await self._decrypt_session_data(encrypted_data)
            
            # Reconstruct session object
            return PaymentSession(
                session_id=session_data['session_id'],
                user_id=session_data['user_id'],
                token_type=TokenType(session_data['token_type']),
                security_level=SecurityLevel(session_data['security_level']),
                created_at=datetime.fromisoformat(session_data['created_at']),
                expires_at=datetime.fromisoformat(session_data['expires_at']),
                last_accessed=datetime.fromisoformat(session_data['last_accessed']),
                ip_address=session_data['ip_address'],
                user_agent=session_data['user_agent'],
                device_fingerprint=session_data.get('device_fingerprint'),
                metadata=session_data.get('metadata', {}),
                status=SessionStatus(session_data['status']),
                access_count=session_data['access_count'],
                max_access_count=session_data['max_access_count'],
                allowed_operations=session_data['allowed_operations']
            )
            
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None
    
    async def _get_user_sessions(self, user_id: str) -> List[PaymentSession]:
        """Get all sessions for a user"""
        try:
            user_sessions_key = f"user_sessions:{user_id}"
            session_ids = await self.redis.smembers(user_sessions_key)
            
            sessions = []
            for session_id in session_ids:
                session = await self._get_session(session_id.decode())
                if session:
                    sessions.append(session)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []
    
    async def _update_session_access(self, session_id: str, ip_address: str, user_agent: str):
        """Update session access information"""
        try:
            session = await self._get_session(session_id)
            if not session:
                return
            
            session.last_accessed = datetime.utcnow()
            session.access_count += 1
            
            # Update IP and user agent if provided
            if ip_address:
                session.ip_address = ip_address
            if user_agent:
                session.user_agent = user_agent
            
            await self._store_session(session)
            
        except Exception as e:
            logger.error(f"Failed to update session access: {e}")
    
    async def _revoke_session(self, session_id: str, reason: str):
        """Revoke a session"""
        try:
            session = await self._get_session(session_id)
            if not session:
                return
            
            session.status = SessionStatus.REVOKED
            session.metadata['revocation_reason'] = reason
            session.metadata['revoked_at'] = datetime.utcnow().isoformat()
            
            await self._store_session(session)
            
        except Exception as e:
            logger.error(f"Failed to revoke session: {e}")
    
    async def _check_suspicious_activity(self, session_id: str, ip_address: str) -> float:
        """Check for suspicious activity patterns"""
        try:
            # Get recent access patterns
            access_key = f"session_access:{session_id}"
            recent_accesses = await self.redis.lrange(access_key, 0, 9)
            
            risk_score = 0.0
            
            # Check for rapid access
            if len(recent_accesses) >= 5:
                # Multiple accesses in short time
                risk_score += 0.3
            
            # Check for multiple IP addresses
            ips = set()
            for access in recent_accesses:
                access_data = json.loads(access)
                ips.add(access_data.get('ip_address', ''))
            
            if len(ips) > 2:
                risk_score += 0.4
            
            # Log current access
            await self.redis.lpush(
                access_key,
                json.dumps({
                    'timestamp': datetime.utcnow().isoformat(),
                    'ip_address': ip_address
                })
            )
            await self.redis.ltrim(access_key, 0, 9)
            await self.redis.expire(access_key, 3600)  # 1 hour
            
            return risk_score
            
        except Exception as e:
            logger.error(f"Failed to check suspicious activity: {e}")
            return 0.0
    
    async def _encrypt_session_data(self, data: Dict[str, Any]) -> str:
        """Encrypt session data"""
        try:
            json_data = json.dumps(data).encode()
            
            # Generate IV
            iv = secrets.token_bytes(16)
            
            # Encrypt
            cipher = Cipher(
                algorithms.AES(self.encryption_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Pad data
            pad_length = 16 - (len(json_data) % 16)
            padded_data = json_data + bytes([pad_length] * pad_length)
            
            encrypted = encryptor.update(padded_data) + encryptor.finalize()
            
            # Combine IV and encrypted data
            combined = iv + encrypted
            
            return base64.urlsafe_b64encode(combined).decode()
            
        except Exception as e:
            logger.error(f"Failed to encrypt session data: {e}")
            raise
    
    async def _decrypt_session_data(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt session data"""
        try:
            combined = base64.urlsafe_b64decode(encrypted_data.encode())
            
            # Extract IV and encrypted data
            iv = combined[:16]
            encrypted = combined[16:]
            
            # Decrypt
            cipher = Cipher(
                algorithms.AES(self.encryption_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            padded_data = decryptor.update(encrypted) + decryptor.finalize()
            
            # Remove padding
            pad_length = padded_data[-1]
            json_data = padded_data[:-pad_length]
            
            return json.loads(json_data.decode())
            
        except Exception as e:
            logger.error(f"Failed to decrypt session data: {e}")
            raise
    
    async def _log_session_event(self, event_type: str, session_id: str, user_id: str, metadata: Dict[str, Any]):
        """Log session events for audit"""
        try:
            event_data = {
                'event_type': event_type,
                'session_id': session_id,
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': metadata
            }
            
            await self.redis.lpush(
                'session_events',
                json.dumps(event_data)
            )
            
            # Keep last 10000 events
            await self.redis.ltrim('session_events', 0, 9999)
            
        except Exception as e:
            logger.error(f"Failed to log session event: {e}")
    
    async def _session_cleanup_loop(self):
        """Background task to clean up expired sessions"""
        while self.is_running:
            try:
                # Clean up expired sessions
                # This is handled by Redis TTL, but we can do additional cleanup
                
                # Clean up old session events
                await self.redis.ltrim('session_events', 0, 9999)
                
                # Sleep for cleanup interval
                await asyncio.sleep(self.session_cleanup_interval)
                
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")
                await asyncio.sleep(60)
    
    async def get_session_metrics(self) -> Dict[str, Any]:
        """Get session management metrics"""
        try:
            # Get active sessions count
            active_sessions = 0
            total_sessions = 0
            
            # This would scan all session keys in production
            # For now, return basic metrics
            
            return {
                'active_sessions': active_sessions,
                'total_sessions': total_sessions,
                'cleanup_interval': self.session_cleanup_interval,
                'max_sessions_per_user': self.max_sessions_per_user,
                'is_running': self.is_running
            }
            
        except Exception as e:
            logger.error(f"Failed to get session metrics: {e}")
            return {'error': str(e)}
