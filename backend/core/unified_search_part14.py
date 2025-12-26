"""
Part 14: Security and Access Control
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements comprehensive security measures, access control, and
authentication for the unified search system.
"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from core.unified_search_part1 import SearchMode, SearchQuery

logger = logging.getLogger("raptorflow.unified_search.security")


class Permission(Enum):
    """User permissions."""

    SEARCH_BASIC = "search_basic"
    SEARCH_ADVANCED = "search_advanced"
    SEARCH_DEEP = "search_deep"
    RESEARCH_BASIC = "research_basic"
    RESEARCH_ADVANCED = "research_advanced"
    CRAWL_WEB = "crawl_web"
    ACCESS_ANALYTICS = "access_analytics"
    MANAGE_CONFIG = "manage_config"
    ADMIN_ACCESS = "admin_access"


class UserRole(Enum):
    """User roles with predefined permissions."""

    GUEST = "guest"
    USER = "user"
    RESEARCHER = "researcher"
    DEVELOPER = "developer"
    ADMIN = "admin"


@dataclass
class User:
    """User entity."""

    id: str
    username: str
    email: str
    role: UserRole
    permissions: Set[Permission]
    api_key: Optional[str] = None
    rate_limit_per_hour: int = 100
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def has_permission(self, permission: Permission) -> bool:
        """Check if user has permission."""
        return permission in self.permissions

    def has_any_permission(self, permissions: List[Permission]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(p in self.permissions for p in permissions)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (without sensitive data)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "permissions": [p.value for p in self.permissions],
            "rate_limit_per_hour": self.rate_limit_per_hour,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active,
            "metadata": self.metadata,
        }


@dataclass
class APIKey:
    """API key entity."""

    key_id: str
    user_id: str
    name: str
    key_hash: str
    permissions: Set[Permission]
    rate_limit_per_hour: int = 1000
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    def is_expired(self) -> bool:
        """Check if API key is expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (without sensitive data)."""
        return {
            "key_id": self.key_id,
            "user_id": self.user_id,
            "name": self.name,
            "permissions": [p.value for p in self.permissions],
            "rate_limit_per_hour": self.rate_limit_per_hour,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
        }


class RolePermissionMapper:
    """Maps roles to permissions."""

    ROLE_PERMISSIONS = {
        UserRole.GUEST: {
            Permission.SEARCH_BASIC,
        },
        UserRole.USER: {
            Permission.SEARCH_BASIC,
            Permission.SEARCH_ADVANCED,
        },
        UserRole.RESEARCHER: {
            Permission.SEARCH_BASIC,
            Permission.SEARCH_ADVANCED,
            Permission.SEARCH_DEEP,
            Permission.RESEARCH_BASIC,
            Permission.RESEARCH_ADVANCED,
        },
        UserRole.DEVELOPER: {
            Permission.SEARCH_BASIC,
            Permission.SEARCH_ADVANCED,
            Permission.SEARCH_DEEP,
            Permission.RESEARCH_BASIC,
            Permission.RESEARCH_ADVANCED,
            Permission.CRAWL_WEB,
            Permission.ACCESS_ANALYTICS,
        },
        UserRole.ADMIN: {
            Permission.SEARCH_BASIC,
            Permission.SEARCH_ADVANCED,
            Permission.SEARCH_DEEP,
            Permission.RESEARCH_BASIC,
            Permission.RESEARCH_ADVANCED,
            Permission.CRAWL_WEB,
            Permission.ACCESS_ANALYTICS,
            Permission.MANAGE_CONFIG,
            Permission.ADMIN_ACCESS,
        },
    }

    @classmethod
    def get_permissions(cls, role: UserRole) -> Set[Permission]:
        """Get permissions for role."""
        return cls.ROLE_PERMISSIONS.get(role, set())

    @classmethod
    def can_upgrade_role(cls, from_role: UserRole, to_role: UserRole) -> bool:
        """Check if role upgrade is allowed."""
        from_permissions = cls.get_permissions(from_role)
        to_permissions = cls.get_permissions(to_role)
        return from_permissions.issubset(to_permissions)


class RateLimiter:
    """Rate limiting for users and API keys."""

    def __init__(self):
        self.user_limits: Dict[str, List[datetime]] = {}
        self.api_key_limits: Dict[str, List[datetime]] = {}
        self._cleanup_interval = 3600  # 1 hour
        self._cleanup_task: Optional[asyncio.Task] = None

    async def check_user_limit(self, user_id: str, limit_per_hour: int) -> bool:
        """Check if user is within rate limit."""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)

        # Get user's recent requests
        if user_id not in self.user_limits:
            self.user_limits[user_id] = []

        # Clean old requests
        self.user_limits[user_id] = [
            req_time for req_time in self.user_limits[user_id] if req_time > hour_ago
        ]

        # Check limit
        if len(self.user_limits[user_id]) >= limit_per_hour:
            return False

        # Add current request
        self.user_limits[user_id].append(now)
        return True

    async def check_api_key_limit(self, api_key_hash: str, limit_per_hour: int) -> bool:
        """Check if API key is within rate limit."""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)

        # Get API key's recent requests
        if api_key_hash not in self.api_key_limits:
            self.api_key_limits[api_key_hash] = []

        # Clean old requests
        self.api_key_limits[api_key_hash] = [
            req_time
            for req_time in self.api_key_limits[api_key_hash]
            if req_time > hour_ago
        ]

        # Check limit
        if len(self.api_key_limits[api_key_hash]) >= limit_per_hour:
            return False

        # Add current request
        self.api_key_limits[api_key_hash].append(now)
        return True

    async def start_cleanup(self):
        """Start cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop_cleanup(self):
        """Stop cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

    async def _cleanup_loop(self):
        """Cleanup old rate limit entries."""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_old_entries()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Rate limiter cleanup error: {e}")

    async def _cleanup_old_entries(self):
        """Clean up old rate limit entries."""
        cutoff_time = datetime.now() - timedelta(hours=2)

        # Clean user limits
        for user_id in list(self.user_limits.keys()):
            self.user_limits[user_id] = [
                req_time
                for req_time in self.user_limits[user_id]
                if req_time > cutoff_time
            ]
            if not self.user_limits[user_id]:
                del self.user_limits[user_id]

        # Clean API key limits
        for api_key_hash in list(self.api_key_limits.keys()):
            self.api_key_limits[api_key_hash] = [
                req_time
                for req_time in self.api_key_limits[api_key_hash]
                if req_time > cutoff_time
            ]
            if not self.api_key_limits[api_key_hash]:
                del self.api_key_limits[api_key_hash]

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        return {
            "active_users": len(self.user_limits),
            "active_api_keys": len(self.api_key_limits),
            "total_requests": sum(
                len(requests) for requests in self.user_limits.values()
            ),
            "total_api_requests": sum(
                len(requests) for requests in self.api_key_limits.values()
            ),
        }


class AuthenticationManager:
    """Manages user authentication and API keys."""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.users: Dict[str, User] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.api_key_lookup: Dict[str, str] = {}  # key_hash -> key_id
        self.jwt_algorithm = "HS256"
        self.jwt_expiry_hours = 24
        self._encryption_key = self._derive_encryption_key()
        self.cipher = Fernet(self._encryption_key)

    def _derive_encryption_key(self) -> bytes:
        """Derive encryption key from secret key."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"raptorflow_unified_search",
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
        return key

    def create_user(
        self,
        username: str,
        email: str,
        role: UserRole = UserRole.USER,
        custom_permissions: Optional[Set[Permission]] = None,
    ) -> User:
        """Create a new user."""
        user_id = secrets.token_urlsafe(16)

        # Get permissions for role
        permissions = RolePermissionMapper.get_permissions(role)
        if custom_permissions:
            permissions.update(custom_permissions)

        user = User(
            id=user_id,
            username=username,
            email=email,
            role=role,
            permissions=permissions,
        )

        self.users[user_id] = user
        logger.info(f"Created user: {username} ({role.value})")

        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)

    def update_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """Update user role."""
        user = self.users.get(user_id)
        if not user:
            return False

        # Check if upgrade is allowed
        if not RolePermissionMapper.can_upgrade_role(user.role, new_role):
            logger.warning(
                f"Role upgrade not allowed: {user.role.value} -> {new_role.value}"
            )
            return False

        user.role = new_role
        user.permissions = RolePermissionMapper.get_permissions(new_role)

        logger.info(f"Updated user role: {user.username} -> {new_role.value}")
        return True

    def create_api_key(
        self,
        user_id: str,
        name: str,
        permissions: Optional[Set[Permission]] = None,
        expires_in_days: Optional[int] = None,
        rate_limit_per_hour: Optional[int] = None,
    ) -> Tuple[str, APIKey]:
        """Create a new API key."""
        user = self.users.get(user_id)
        if not user:
            raise ValueError("User not found")

        # Generate API key
        api_key = secrets.token_urlsafe(32)
        key_id = secrets.token_urlsafe(8)

        # Hash the key for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        # Set permissions (inherit from user if not specified)
        if permissions is None:
            permissions = user.permissions.copy()

        # Set expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)

        # Set rate limit
        if rate_limit_per_hour is None:
            rate_limit_per_hour = user.rate_limit_per_hour * 10  # 10x user limit

        api_key_obj = APIKey(
            key_id=key_id,
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            permissions=permissions,
            rate_limit_per_hour=rate_limit_per_hour,
            expires_at=expires_at,
        )

        self.api_keys[key_id] = api_key_obj
        self.api_key_lookup[key_hash] = key_id

        logger.info(f"Created API key: {name} for user {user.username}")

        return api_key, api_key_obj

    def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validate API key and return API key object."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        key_id = self.api_key_lookup.get(key_hash)
        if not key_id:
            return None

        api_key_obj = self.api_keys.get(key_id)
        if not api_key_obj:
            return None

        # Check if key is active and not expired
        if not api_key_obj.is_active or api_key_obj.is_expired():
            return None

        # Update last used
        api_key_obj.last_used = datetime.now()

        return api_key_obj

    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke API key."""
        api_key_obj = self.api_keys.get(key_id)
        if not api_key_obj:
            return False

        api_key_obj.is_active = False

        # Remove from lookup
        if api_key_obj.key_hash in self.api_key_lookup:
            del self.api_key_lookup[api_key_obj.key_hash]

        logger.info(f"Revoked API key: {api_key_obj.name}")
        return True

    def generate_jwt_token(self, user_id: str) -> str:
        """Generate JWT token for user."""
        user = self.users.get(user_id)
        if not user:
            raise ValueError("User not found")

        payload = {
            "user_id": user_id,
            "username": user.username,
            "role": user.role.value,
            "permissions": [p.value for p in user.permissions],
            "exp": datetime.now() + timedelta(hours=self.jwt_expiry_hours),
            "iat": datetime.now(),
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.jwt_algorithm)
        return token

    def validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return payload."""
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        encrypted = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        encrypted = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(encrypted)
        return decrypted.decode()

    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics."""
        role_counts = {}
        for user in self.users.values():
            role_counts[user.role.value] = role_counts.get(user.role.value, 0) + 1

        return {
            "total_users": len(self.users),
            "active_users": sum(1 for user in self.users.values() if user.is_active),
            "role_distribution": role_counts,
            "total_api_keys": len(self.api_keys),
            "active_api_keys": sum(
                1 for key in self.api_keys.values() if key.is_active
            ),
        }


class SecurityManager:
    """Main security manager."""

    def __init__(self, secret_key: str):
        self.auth_manager = AuthenticationManager(secret_key)
        self.rate_limiter = RateLimiter()
        self._monitoring_enabled = False
        self._security_events: List[Dict[str, Any]] = []
        self._max_events = 10000

    async def initialize(self):
        """Initialize security components."""
        await self.rate_limiter.start_cleanup()
        self._monitoring_enabled = True
        logger.info("Security manager initialized")

    async def shutdown(self):
        """Shutdown security components."""
        await self.rate_limiter.stop_cleanup()
        self._monitoring_enabled = False
        logger.info("Security manager shutdown")

    def log_security_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        api_key_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log security event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "api_key_id": api_key_id,
            "details": details or {},
        }

        self._security_events.append(event)

        # Keep only recent events
        if len(self._security_events) > self._max_events:
            self._security_events = self._security_events[-self._max_events :]

        logger.info(f"Security event: {event_type}")

    async def check_search_permission(
        self,
        user: Optional[User] = None,
        api_key: Optional[APIKey] = None,
        query: SearchQuery = None,
    ) -> Tuple[bool, str]:
        """Check if user/api key has permission for search query."""
        # Determine required permission based on query mode
        required_permission = {
            SearchMode.LIGHTNING: Permission.SEARCH_BASIC,
            SearchMode.STANDARD: Permission.SEARCH_BASIC,
            SearchMode.DEEP: Permission.SEARCH_ADVANCED,
            SearchMode.EXHAUSTIVE: Permission.SEARCH_DEEP,
        }.get(query.mode, Permission.SEARCH_BASIC)

        # Check permission
        if user and not user.has_permission(required_permission):
            return (
                False,
                f"Insufficient permissions. Required: {required_permission.value}",
            )

        if api_key and not api_key.permissions:
            return False, "API key has no permissions"

        if api_key and required_permission not in api_key.permissions:
            return (
                False,
                f"API key lacks permission. Required: {required_permission.value}",
            )

        # Check rate limits
        if user:
            if not await self.rate_limiter.check_user_limit(
                user.id, user.rate_limit_per_hour
            ):
                return False, "User rate limit exceeded"

        if api_key:
            if not await self.rate_limiter.check_api_key_limit(
                api_key.key_hash, api_key.rate_limit_per_hour
            ):
                return False, "API key rate limit exceeded"

        return True, "Authorized"

    def get_security_report(self) -> Dict[str, Any]:
        """Get comprehensive security report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "user_stats": self.auth_manager.get_user_stats(),
            "rate_limiter_stats": self.rate_limiter.get_stats(),
            "recent_events": self._security_events[-100:],  # Last 100 events
            "monitoring_active": self._monitoring_enabled,
        }


# Global security manager (requires secret key)
security_manager: Optional[SecurityManager] = None


def initialize_security(secret_key: str) -> SecurityManager:
    """Initialize global security manager."""
    global security_manager
    security_manager = SecurityManager(secret_key)
    return security_manager


def get_security_manager() -> SecurityManager:
    """Get global security manager."""
    if security_manager is None:
        raise RuntimeError("Security manager not initialized")
    return security_manager
