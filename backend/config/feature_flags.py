"""
Feature flags management for Raptorflow backend.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from .settings import get_settings

logger = logging.getLogger(__name__)


@dataclass
class FeatureFlag:
    """Feature flag definition."""

    name: str
    enabled: bool
    description: str
    rollout_percentage: int = 100
    user_ids: Optional[Set[str]] = None
    workspace_ids: Optional[Set[str]] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.user_ids is None:
            self.user_ids = set()
        if self.workspace_ids is None:
            self.workspace_ids = set()

    def is_enabled_for_user(
        self, user_id: str = None, workspace_id: str = None
    ) -> bool:
        """Check if feature is enabled for specific user/workspace."""
        if not self.enabled:
            return False

        # Check expiration
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False

        # User-specific targeting
        if user_id and self.user_ids and user_id not in self.user_ids:
            return False

        # Workspace-specific targeting
        if (
            workspace_id
            and self.workspace_ids
            and workspace_id not in self.workspace_ids
        ):
            return False

        # Rollout percentage (if no specific targeting)
        if not self.user_ids and not self.workspace_ids:
            if self.rollout_percentage < 100:
                # Use consistent hash based on user/workspace ID
                target_id = user_id or workspace_id or "anonymous"
                hash_value = hash(target_id) % 100
                return hash_value < self.rollout_percentage

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert feature flag to dictionary."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "description": self.description,
            "rollout_percentage": self.rollout_percentage,
            "user_ids": list(self.user_ids) if self.user_ids else [],
            "workspace_ids": list(self.workspace_ids) if self.workspace_ids else [],
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeatureFlag":
        """Create feature flag from dictionary."""
        return cls(
            name=data["name"],
            enabled=data["enabled"],
            description=data["description"],
            rollout_percentage=data.get("rollout_percentage", 100),
            user_ids=set(data.get("user_ids", [])),
            workspace_ids=set(data.get("workspace_ids", [])),
            expires_at=(
                datetime.fromisoformat(data["expires_at"])
                if data.get("expires_at")
                else None
            ),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


class FeatureFlags:
    """Feature flags management system."""

    def __init__(self):
        self._redis_client = None
        self.settings = get_settings()
        self._cache: Dict[str, FeatureFlag] = {}
        self._cache_ttl = 300  # 5 minutes

    @property
    def redis_client(self):
        """Lazy load redis client"""
        if self._redis_client is None:
            from ..redis_client import redis_manager

            self._redis_client = redis_manager.client
        return self._redis_client

    async def is_enabled(
        self, flag_name: str, user_id: str = None, workspace_id: str = None
    ) -> bool:
        """Check if a feature flag is enabled for the given context."""
        try:
            # Try cache first
            flag = self._cache.get(flag_name)
            if flag is None:
                flag = await self._get_flag(flag_name)
                if flag:
                    self._cache[flag_name] = flag

            if not flag:
                # Fall back to environment variable
                return self.settings.get_feature_flag(flag_name, False)

            return flag.is_enabled_for_user(user_id, workspace_id)

        except Exception as e:
            logger.error(f"Error checking feature flag {flag_name}: {e}")
            # Fall back to environment variable
            return self.settings.get_feature_flag(flag_name, False)

    async def enable_flag(
        self,
        flag_name: str,
        rollout_percentage: int = 100,
        user_ids: List[str] = None,
        workspace_ids: List[str] = None,
        expires_at: datetime = None,
    ) -> bool:
        """Enable a feature flag."""
        try:
            flag = FeatureFlag(
                name=flag_name,
                enabled=True,
                description=f"Feature flag: {flag_name}",
                rollout_percentage=rollout_percentage,
                user_ids=set(user_ids) if user_ids else None,
                workspace_ids=set(workspace_ids) if workspace_ids else None,
                expires_at=expires_at,
            )

            await self._save_flag(flag)
            self._cache[flag_name] = flag

            logger.info(f"Feature flag {flag_name} enabled")
            return True

        except Exception as e:
            logger.error(f"Error enabling feature flag {flag_name}: {e}")
            return False

    async def disable_flag(self, flag_name: str) -> bool:
        """Disable a feature flag."""
        try:
            flag = await self._get_flag(flag_name)
            if flag:
                flag.enabled = False
                flag.updated_at = datetime.utcnow()
                await self._save_flag(flag)
                self._cache[flag_name] = flag

                logger.info(f"Feature flag {flag_name} disabled")
                return True
            else:
                logger.warning(f"Feature flag {flag_name} not found")
                return False

        except Exception as e:
            logger.error(f"Error disabling feature flag {flag_name}: {e}")
            return False

    async def create_flag(
        self,
        flag_name: str,
        description: str,
        enabled: bool = False,
        rollout_percentage: int = 100,
        user_ids: List[str] = None,
        workspace_ids: List[str] = None,
        expires_at: datetime = None,
    ) -> bool:
        """Create a new feature flag."""
        try:
            flag = FeatureFlag(
                name=flag_name,
                enabled=enabled,
                description=description,
                rollout_percentage=rollout_percentage,
                user_ids=set(user_ids) if user_ids else None,
                workspace_ids=set(workspace_ids) if workspace_ids else None,
                expires_at=expires_at,
            )

            await self._save_flag(flag)
            self._cache[flag_name] = flag

            logger.info(f"Feature flag {flag_name} created")
            return True

        except Exception as e:
            logger.error(f"Error creating feature flag {flag_name}: {e}")
            return False

    async def delete_flag(self, flag_name: str) -> bool:
        """Delete a feature flag."""
        try:
            key = f"feature_flag:{flag_name}"
            await self.redis_client.delete(key)

            if flag_name in self._cache:
                del self._cache[flag_name]

            logger.info(f"Feature flag {flag_name} deleted")
            return True

        except Exception as e:
            logger.error(f"Error deleting feature flag {flag_name}: {e}")
            return False

    async def get_all_flags(self) -> Dict[str, FeatureFlag]:
        """Get all feature flags."""
        try:
            pattern = "feature_flag:*"
            keys = await self.redis_client.keys(pattern)

            flags = {}
            for key in keys:
                flag_name = key.replace("feature_flag:", "")
                flag = await self._get_flag(flag_name)
                if flag:
                    flags[flag_name] = flag

            return flags

        except Exception as e:
            logger.error(f"Error getting all feature flags: {e}")
            return {}

    async def get_flag_stats(self) -> Dict[str, Any]:
        """Get statistics about feature flags."""
        try:
            flags = await self.get_all_flags()

            total_flags = len(flags)
            enabled_flags = sum(1 for flag in flags.values() if flag.enabled)
            expired_flags = sum(
                1
                for flag in flags.values()
                if flag.expires_at and datetime.utcnow() > flag.expires_at
            )

            return {
                "total_flags": total_flags,
                "enabled_flags": enabled_flags,
                "disabled_flags": total_flags - enabled_flags,
                "expired_flags": expired_flags,
                "flags": {name: flag.to_dict() for name, flag in flags.items()},
            }

        except Exception as e:
            logger.error(f"Error getting feature flag stats: {e}")
            return {}

    async def _get_flag(self, flag_name: str) -> Optional[FeatureFlag]:
        """Get a feature flag from Redis."""
        try:
            key = f"feature_flag:{flag_name}"
            data = await self.redis_client.get(key)

            if data:
                flag_data = json.loads(data)
                return FeatureFlag.from_dict(flag_data)

            return None

        except Exception as e:
            logger.error(f"Error getting feature flag {flag_name}: {e}")
            return None

    async def _save_flag(self, flag: FeatureFlag) -> None:
        """Save a feature flag to Redis."""
        try:
            key = f"feature_flag:{flag.name}"
            data = json.dumps(flag.to_dict())

            await self.redis_client.set(key, data, ex=86400)  # 24 hours TTL

        except Exception as e:
            logger.error(f"Error saving feature flag {flag.name}: {e}")

    def clear_cache(self) -> None:
        """Clear the feature flags cache."""
        self._cache.clear()


# Global feature flags instance
_feature_flags: FeatureFlags = None


def get_feature_flags() -> FeatureFlags:
    """Get the global feature flags instance."""
    global _feature_flags
    if _feature_flags is None:
        _feature_flags = FeatureFlags()
    return _feature_flags


# Convenience functions
async def is_feature_enabled(
    flag_name: str, user_id: str = None, workspace_id: str = None
) -> bool:
    """Check if a feature flag is enabled."""
    flags = get_feature_flags()
    return await flags.is_enabled(flag_name, user_id, workspace_id)


async def enable_feature_flag(
    flag_name: str,
    rollout_percentage: int = 100,
    user_ids: List[str] = None,
    workspace_ids: List[str] = None,
    expires_at: datetime = None,
) -> bool:
    """Enable a feature flag."""
    flags = get_feature_flags()
    return await flags.enable_flag(
        flag_name, rollout_percentage, user_ids, workspace_ids, expires_at
    )


async def disable_feature_flag(flag_name: str) -> bool:
    """Disable a feature flag."""
    flags = get_feature_flags()
    return await flags.disable_flag(flag_name)


async def disable_feature_flag(flag_name: str) -> bool:
    """Disable a feature flag."""
    flags = get_feature_flags()
    return await flags.disable_flag(flag_name)
