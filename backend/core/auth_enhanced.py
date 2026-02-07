import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("raptorflow.auth.enhanced")


class EnhancedAuthManager:
    """
    Enhanced authentication features built on existing auth infrastructure.
    """

    def __init__(self):
        self.session_tokens: Dict[str, Dict[str, Any]] = {}
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self.stats = {
            "auth_requests": 0,
            "auth_failures": 0,
            "token_issues": 0,
            "api_key_validations": 0,
        }

    async def create_session_token(
        self, user_id: str, tenant_id: str, expires_in: int = 3600
    ) -> str:
        """Create a session token for user."""
        import secrets

        token = secrets.token_urlsafe(32)

        self.session_tokens[token] = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(seconds=expires_in),
            "last_accessed": datetime.utcnow(),
        }

        self.stats["token_issues"] += 1
        return token

    async def validate_session_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate session token."""
        self.stats["auth_requests"] += 1

        if token not in self.session_tokens:
            self.stats["auth_failures"] += 1
            return None

        session = self.session_tokens[token]

        # Check expiration
        if datetime.utcnow() > session["expires_at"]:
            del self.session_tokens[token]
            self.stats["auth_failures"] += 1
            return None

        # Update last accessed
        session["last_accessed"] = datetime.utcnow()

        return session

    async def create_api_key(
        self, user_id: str, tenant_id: str, name: str, permissions: List[str] = None
    ) -> str:
        """Create API key for service-to-service authentication."""
        import secrets

        api_key = f"rpf_{secrets.token_urlsafe(40)}"

        self.api_keys[api_key] = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "name": name,
            "permissions": permissions or [],
            "created_at": datetime.utcnow(),
            "last_used": None,
            "usage_count": 0,
        }

        return api_key

    async def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key."""
        self.stats["api_key_validations"] += 1

        if api_key not in self.api_keys:
            return None

        key_info = self.api_keys[api_key]
        key_info["last_used"] = datetime.utcnow()
        key_info["usage_count"] += 1

        return key_info

    async def revoke_session_token(self, token: str):
        """Revoke session token."""
        if token in self.session_tokens:
            del self.session_tokens[token]

    async def revoke_api_key(self, api_key: str):
        """Revoke API key."""
        if api_key in self.api_keys:
            del self.api_keys[api_key]

    async def cleanup_expired_sessions(self):
        """Clean up expired session tokens."""
        now = datetime.utcnow()
        expired_tokens = [
            token
            for token, session in self.session_tokens.items()
            if now > session["expires_at"]
        ]

        for token in expired_tokens:
            del self.session_tokens[token]

        if expired_tokens:
            logger.debug(f"Cleaned up {len(expired_tokens)} expired session tokens")

    def get_stats(self) -> Dict[str, Any]:
        """Get authentication statistics."""
        return {
            **self.stats,
            "active_sessions": len(self.session_tokens),
            "active_api_keys": len(self.api_keys),
        }


# Global enhanced auth manager
_enhanced_auth_manager: Optional[EnhancedAuthManager] = None


def get_enhanced_auth_manager() -> EnhancedAuthManager:
    """Get the global enhanced auth manager instance."""
    global _enhanced_auth_manager
    if _enhanced_auth_manager is None:
        _enhanced_auth_manager = EnhancedAuthManager()
    return _enhanced_auth_manager


async def start_enhanced_auth():
    """Start enhanced authentication system."""
    auth_manager = get_enhanced_auth_manager()

    # Start cleanup task
    asyncio.create_task(_periodic_session_cleanup())

    logger.info("Enhanced authentication system started")


async def stop_enhanced_auth():
    """Stop enhanced authentication system."""
    logger.info("Enhanced authentication system stopped")


async def _periodic_session_cleanup():
    """Periodic cleanup of expired sessions."""
    while True:
        try:
            await asyncio.sleep(1800)  # Run every 30 minutes
            auth_manager = get_enhanced_auth_manager()
            await auth_manager.cleanup_expired_sessions()
            logger.debug("Completed session cleanup")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")


# Utility functions
async def create_user_session(user_id: str, tenant_id: str) -> str:
    """Create user session token."""
    auth_manager = get_enhanced_auth_manager()
    return await auth_manager.create_session_token(user_id, tenant_id)


async def validate_session(token: str) -> Optional[Dict[str, Any]]:
    """Validate session token."""
    auth_manager = get_enhanced_auth_manager()
    return await auth_manager.validate_session_token(token)


async def get_auth_stats() -> Dict[str, Any]:
    """Get authentication statistics."""
    auth_manager = get_enhanced_auth_manager()
    return auth_manager.get_stats()
