"""
TTL (Time To Live) manager for Redis keys.

Provides centralized TTL management with scheduled cleanup jobs
and automatic expiration handling.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set

from .client import get_redis
from .keys import get_ttl_for_service

logger = logging.getLogger(__name__)


@dataclass
class TTLEntry:
    """TTL entry for tracking key expiration."""

    key: str
    ttl_seconds: int
    created_at: datetime
    expires_at: datetime
    service_type: str
    metadata: Dict[str, Any] = None


@dataclass
class TTLStats:
    """TTL management statistics."""

    total_keys: int
    expired_keys: int
    keys_by_service: Dict[str, int]
    average_ttl: float
    cleanup_count: int
    last_cleanup: datetime


class TTLManager:
    """Manages TTL for Redis keys with scheduled cleanup."""

    def __init__(self):
        self.redis = get_redis()
        self.ttl_index_key = "ttl:index"
        self.cleanup_interval_seconds = 300  # 5 minutes
        self.max_cleanup_batch = 1000
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

        # TTL configurations by service type
        self.service_ttls = {
            "session": 1800,  # 30 minutes
            "cache": 3600,  # 1 hour
            "rate_limit": 60,  # 1 minute
            "queue": 86400,  # 24 hours
            "lock": 300,  # 5 minutes
            "usage": 86400 * 90,  # 90 days
            "alert": 86400,  # 24 hours
            "job": 86400,  # 24 hours
            "worker": 3600,  # 1 hour
            "default": 3600,  # 1 hour
        }

    async def set_ttl(
        self,
        key: str,
        ttl_seconds: int,
        service_type: str = "default",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Set TTL for a key and track in index."""
        try:
            # Set TTL on the key
            success = await self.redis.expire(key, ttl_seconds)

            if success:
                # Track in TTL index
                await self._track_ttl(key, ttl_seconds, service_type, metadata)

            return success

        except Exception as e:
            logger.error(f"Failed to set TTL for key {key}: {e}")
            return False

    async def get_ttl(self, key: str) -> int:
        """Get TTL for a key."""
        try:
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error(f"Failed to get TTL for key {key}: {e}")
            return -1

    async def refresh_ttl(
        self,
        key: str,
        ttl_seconds: Optional[int] = None,
        service_type: Optional[str] = None,
    ) -> bool:
        """Refresh TTL for an existing key."""
        try:
            # Get current TTL to determine service type if not provided
            if service_type is None:
                service_type = await self._get_service_type(key)

            # Use service-specific TTL if not provided
            if ttl_seconds is None:
                ttl_seconds = self.service_ttls.get(
                    service_type, self.service_ttls["default"]
                )

            # Refresh TTL
            success = await self.redis.expire(key, ttl_seconds)

            if success:
                # Update TTL index
                await self._update_ttl_index(key, ttl_seconds, service_type)

            return success

        except Exception as e:
            logger.error(f"Failed to refresh TTL for key {key}: {e}")
            return False

    async def extend_ttl(self, key: str, additional_seconds: int) -> bool:
        """Extend TTL by additional seconds."""
        try:
            current_ttl = await self.redis.ttl(key)

            if current_ttl > 0:
                new_ttl = current_ttl + additional_seconds
                return await self.redis.expire(key, new_ttl)

            return False

        except Exception as e:
            logger.error(f"Failed to extend TTL for key {key}: {e}")
            return False

    async def set_ttl_with_pattern(
        self, pattern: str, ttl_seconds: int, service_type: str = "default"
    ) -> int:
        """Set TTL for keys matching pattern."""
        try:
            # Get keys matching pattern
            keys = await self._get_keys_by_pattern(pattern)

            updated_count = 0
            for key in keys:
                if await self.set_ttl(key, ttl_seconds, service_type):
                    updated_count += 1

            return updated_count

        except Exception as e:
            logger.error(f"Failed to set TTL for pattern {pattern}: {e}")
            return 0

    async def get_expiring_keys(
        self, within_seconds: int = 300, service_type: Optional[str] = None
    ) -> List[TTLEntry]:
        """Get keys that will expire within specified time."""
        try:
            cutoff_time = datetime.now() + timedelta(seconds=within_seconds)

            # Get all TTL entries
            entries = await self._get_ttl_entries()

            expiring_entries = []
            for entry in entries:
                if entry.expires_at <= cutoff_time:
                    if service_type is None or entry.service_type == service_type:
                        expiring_entries.append(entry)

            # Sort by expiration time
            expiring_entries.sort(key=lambda x: x.expires_at)

            return expiring_entries

        except Exception as e:
            logger.error(f"Failed to get expiring keys: {e}")
            return []

    async def get_expired_keys(
        self, service_type: Optional[str] = None
    ) -> List[TTLEntry]:
        """Get keys that have already expired."""
        try:
            now = datetime.now()

            # Get all TTL entries
            entries = await self._get_ttl_entries()

            expired_entries = []
            for entry in entries:
                if entry.expires_at <= now:
                    if service_type is None or entry.service_type == service_type:
                        expired_entries.append(entry)

            return expired_entries

        except Exception as e:
            logger.error(f"Failed to get expired keys: {e}")
            return []

    async def cleanup_expired(self) -> int:
        """Clean up expired keys."""
        try:
            expired_entries = await self.get_expired_keys()

            if not expired_entries:
                return 0

            cleaned_count = 0
            batch_size = 100

            # Process in batches
            for i in range(0, len(expired_entries), batch_size):
                batch = expired_entries[i : i + batch_size]

                # Delete expired keys
                keys_to_delete = [entry.key for entry in batch]
                deleted = await self.redis.delete(*keys_to_delete)
                cleaned_count += deleted

                # Remove from TTL index
                for entry in batch:
                    await self._remove_from_ttl_index(entry.key)

                # Small delay to avoid overwhelming Redis
                if i + batch_size < len(expired_entries):
                    await asyncio.sleep(0.01)

            logger.info(f"Cleaned up {cleaned_count} expired keys")
            return cleaned_count

        except Exception as e:
            logger.error(f"Failed to cleanup expired keys: {e}")
            return 0

    async def cleanup_orphaned_ttl_entries(self) -> int:
        """Clean up TTL entries for keys that no longer exist."""
        try:
            # Get all TTL entries
            entries = await self._get_ttl_entries()

            orphaned_count = 0
            batch_size = 100

            for i in range(0, len(entries), batch_size):
                batch = entries[i : i + batch_size]

                for entry in batch:
                    # Check if key still exists
                    if not await self.redis.exists(entry.key):
                        # Remove orphaned TTL entry
                        await self._remove_from_ttl_index(entry.key)
                        orphaned_count += 1

                # Small delay
                if i + batch_size < len(entries):
                    await asyncio.sleep(0.01)

            logger.info(f"Cleaned up {orphaned_count} orphaned TTL entries")
            return orphaned_count

        except Exception as e:
            logger.error(f"Failed to cleanup orphaned TTL entries: {e}")
            return 0

    async def get_ttl_stats(self) -> TTLStats:
        """Get TTL management statistics."""
        try:
            entries = await self._get_ttl_entries()

            total_keys = len(entries)
            expired_keys = len([e for e in entries if e.expires_at <= datetime.now()])

            # Count by service type
            keys_by_service = {}
            total_ttl = 0

            for entry in entries:
                service = entry.service_type
                keys_by_service[service] = keys_by_service.get(service, 0) + 1
                total_ttl += entry.ttl_seconds

            average_ttl = total_ttl / total_keys if total_keys > 0 else 0

            # Get cleanup info
            cleanup_info = await self.redis.get_json("ttl:cleanup_stats") or {}

            return TTLStats(
                total_keys=total_keys,
                expired_keys=expired_keys,
                keys_by_service=keys_by_service,
                average_ttl=average_ttl,
                cleanup_count=cleanup_info.get("cleanup_count", 0),
                last_cleanup=datetime.fromisoformat(
                    cleanup_info.get("last_cleanup", "1970-01-01T00:00:00")
                ),
            )

        except Exception as e:
            logger.error(f"Failed to get TTL stats: {e}")
            return TTLStats(
                total_keys=0,
                expired_keys=0,
                keys_by_service={},
                average_ttl=0.0,
                cleanup_count=0,
                last_cleanup=datetime.now(),
            )

    async def start_cleanup_scheduler(self):
        """Start the automatic cleanup scheduler."""
        if self._running:
            return

        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("TTL cleanup scheduler started")

    async def stop_cleanup_scheduler(self):
        """Stop the automatic cleanup scheduler."""
        if not self._running:
            return

        self._running = False

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        logger.info("TTL cleanup scheduler stopped")

    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while self._running:
            try:
                # Run cleanup
                cleaned = await self.cleanup_expired()
                orphaned = await self.cleanup_orphaned_ttl_entries()

                # Update cleanup stats
                cleanup_stats = {
                    "cleanup_count": (
                        await self.redis.get_json("ttl:cleanup_stats") or {}
                    ).get("cleanup_count", 0)
                    + cleaned,
                    "orphaned_count": orphaned,
                    "last_cleanup": datetime.now().isoformat(),
                }
                await self.redis.set_json("ttl:cleanup_stats", cleanup_stats, ex=86400)

                # Sleep until next cleanup
                await asyncio.sleep(self.cleanup_interval_seconds)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute

    async def _track_ttl(
        self,
        key: str,
        ttl_seconds: int,
        service_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Track TTL entry in index."""
        try:
            entry = TTLEntry(
                key=key,
                ttl_seconds=ttl_seconds,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(seconds=ttl_seconds),
                service_type=service_type,
                metadata=metadata or {},
            )

            # Store in TTL index
            await self.redis.hset(
                self.ttl_index_key,
                key,
                json.dumps(
                    {
                        "key": entry.key,
                        "ttl_seconds": entry.ttl_seconds,
                        "created_at": entry.created_at.isoformat(),
                        "expires_at": entry.expires_at.isoformat(),
                        "service_type": entry.service_type,
                        "metadata": entry.metadata,
                    }
                ),
            )

            # Set TTL on index entry
            await self.redis.expire(
                self.ttl_index_key, ttl_seconds + 3600
            )  # Keep index longer

        except Exception as e:
            logger.error(f"Failed to track TTL for key {key}: {e}")

    async def _update_ttl_index(self, key: str, ttl_seconds: int, service_type: str):
        """Update TTL entry in index."""
        try:
            existing_data = await self.redis.hget(self.ttl_index_key, key)

            if existing_data:
                entry_data = json.loads(existing_data)

                # Update TTL and expiration
                entry_data["ttl_seconds"] = ttl_seconds
                entry_data["expires_at"] = (
                    datetime.now() + timedelta(seconds=ttl_seconds)
                ).isoformat()
                entry_data["service_type"] = service_type

                await self.redis.hset(self.ttl_index_key, key, json.dumps(entry_data))

        except Exception as e:
            logger.error(f"Failed to update TTL index for key {key}: {e}")

    async def _remove_from_ttl_index(self, key: str):
        """Remove key from TTL index."""
        try:
            await self.redis.hdel(self.ttl_index_key, key)
        except Exception as e:
            logger.error(f"Failed to remove {key} from TTL index: {e}")

    async def _get_ttl_entries(self) -> List[TTLEntry]:
        """Get all TTL entries from index."""
        try:
            entries_data = await self.redis.hgetall(self.ttl_index_key)

            entries = []
            for key, data in entries_data.items():
                try:
                    entry_dict = json.loads(data)
                    entry = TTLEntry(
                        key=entry_dict["key"],
                        ttl_seconds=entry_dict["ttl_seconds"],
                        created_at=datetime.fromisoformat(entry_dict["created_at"]),
                        expires_at=datetime.fromisoformat(entry_dict["expires_at"]),
                        service_type=entry_dict["service_type"],
                        metadata=entry_dict.get("metadata", {}),
                    )
                    entries.append(entry)
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.warning(f"Invalid TTL entry for key {key}: {e}")
                    continue

            return entries

        except Exception as e:
            logger.error(f"Failed to get TTL entries: {e}")
            return []

    async def _get_service_type(self, key: str) -> str:
        """Determine service type from key pattern."""
        if "session:" in key:
            return "session"
        elif "cache:" in key:
            return "cache"
        elif "rl:" in key:
            return "rate_limit"
        elif "queue:" in key:
            return "queue"
        elif "lock:" in key:
            return "lock"
        elif "usage:" in key:
            return "usage"
        elif "alert:" in key:
            return "alert"
        elif "job:" in key:
            return "job"
        elif "worker:" in key:
            return "worker"
        else:
            return "default"

    async def _get_keys_by_pattern(self, pattern: str) -> List[str]:
        """Get keys matching pattern."""
        try:
            # Note: Upstash Redis doesn't support KEYS command in production
            # This is a placeholder implementation
            # In production, would maintain a key index
            return []
        except Exception as e:
            logger.error(f"Failed to get keys by pattern {pattern}: {e}")
            return []

    async def set_service_ttl(self, service_type: str, ttl_seconds: int):
        """Set default TTL for a service type."""
        self.service_ttls[service_type] = ttl_seconds

        # Store in Redis for persistence
        await self.redis.hset("ttl:service_configs", service_type, str(ttl_seconds))

    async def get_service_ttl(self, service_type: str) -> int:
        """Get default TTL for a service type."""
        # Try Redis first
        redis_ttl = await self.redis.hget("ttl:service_configs", service_type)
        if redis_ttl:
            return int(redis_ttl)

        # Fall back to local config
        return self.service_ttls.get(service_type, self.service_ttls["default"])

    async def load_service_configs(self):
        """Load service TTL configurations from Redis."""
        try:
            configs = await self.redis.hgetall("ttl:service_configs")

            for service_type, ttl_str in configs.items():
                try:
                    self.service_ttls[service_type] = int(ttl_str)
                except ValueError:
                    logger.warning(f"Invalid TTL for service {service_type}: {ttl_str}")

        except Exception as e:
            logger.error(f"Failed to load service configs: {e}")

    async def save_service_configs(self):
        """Save service TTL configurations to Redis."""
        try:
            for service_type, ttl_seconds in self.service_ttls.items():
                await self.redis.hset(
                    "ttl:service_configs", service_type, str(ttl_seconds)
                )

        except Exception as e:
            logger.error(f"Failed to save service configs: {e}")

    async def get_keys_by_service(
        self, service_type: str, limit: int = 1000
    ) -> List[str]:
        """Get keys for a specific service type."""
        try:
            entries = await self._get_ttl_entries()

            service_keys = [
                entry.key for entry in entries if entry.service_type == service_type
            ]

            return service_keys[:limit]

        except Exception as e:
            logger.error(f"Failed to get keys for service {service_type}: {e}")
            return []

    async def get_ttl_distribution(self) -> Dict[str, int]:
        """Get distribution of TTL values by ranges."""
        try:
            entries = await self._get_ttl_entries()

            distribution = {
                "0-60": 0,  # 0-1 minute
                "60-300": 0,  # 1-5 minutes
                "300-3600": 0,  # 5 minutes - 1 hour
                "3600-86400": 0,  # 1-24 hours
                "86400+": 0,  # 24+ hours
            }

            for entry in entries:
                ttl = entry.ttl_seconds

                if ttl <= 60:
                    distribution["0-60"] += 1
                elif ttl <= 300:
                    distribution["60-300"] += 1
                elif ttl <= 3600:
                    distribution["300-3600"] += 1
                elif ttl <= 86400:
                    distribution["3600-86400"] += 1
                else:
                    distribution["86400+"] += 1

            return distribution

        except Exception as e:
            logger.error(f"Failed to get TTL distribution: {e}")
            return {}

    async def force_cleanup(self, service_type: Optional[str] = None) -> int:
        """Force cleanup of expired keys for specific service."""
        try:
            expired_entries = await self.get_expired_keys(service_type)

            if not expired_entries:
                return 0

            # Delete all expired keys
            keys_to_delete = [entry.key for entry in expired_entries]
            deleted = await self.redis.delete(*keys_to_delete)

            # Remove from TTL index
            for entry in expired_entries:
                await self._remove_from_ttl_index(entry.key)

            logger.info(
                f"Force cleaned up {deleted} expired keys for service {service_type}"
            )
            return deleted

        except Exception as e:
            logger.error(f"Failed to force cleanup: {e}")
            return 0

    async def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics for TTL management."""
        try:
            # Get Redis info
            info = await self.redis.async_client.info()

            # Get TTL index size
            index_size = await self.redis.hlen(self.ttl_index_key)

            # Calculate estimated memory usage
            estimated_memory = index_size * 200  # Rough estimate per entry

            return {
                "ttl_index_entries": index_size,
                "estimated_memory_bytes": estimated_memory,
                "estimated_memory_mb": estimated_memory / (1024 * 1024),
                "redis_memory_used": info.get("used_memory", 0),
                "redis_memory_human": info.get("used_memory_human", "0B"),
                "redis_memory_percentage": (
                    estimated_memory / info.get("used_memory", 1)
                )
                * 100,
            }

        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return {}


# Global TTL manager instance
_ttl_manager = TTLManager()


def get_ttl_manager() -> TTLManager:
    """Get global TTL manager instance."""
    return _ttl_manager


# Convenience functions
async def set_ttl(
    key: str,
    ttl_seconds: int,
    service_type: str = "default",
    metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """Set TTL for a key."""
    return await _ttl_manager.set_ttl(key, ttl_seconds, service_type, metadata)


async def get_ttl(key: str) -> int:
    """Get TTL for a key."""
    return await _ttl_manager.get_ttl(key)


async def refresh_ttl(
    key: str, ttl_seconds: Optional[int] = None, service_type: Optional[str] = None
) -> bool:
    """Refresh TTL for a key."""
    return await _ttl_manager.refresh_ttl(key, ttl_seconds, service_type)


async def extend_ttl(key: str, additional_seconds: int) -> bool:
    """Extend TTL for a key."""
    return await _ttl_manager.extend_ttl(key, additional_seconds)


async def cleanup_expired() -> int:
    """Clean up expired keys."""
    return await _ttl_manager.cleanup_expired()


async def get_ttl_stats() -> TTLStats:
    """Get TTL statistics."""
    return await _ttl_manager.get_ttl_stats()


async def start_ttl_scheduler():
    """Start TTL cleanup scheduler."""
    await _ttl_manager.start_cleanup_scheduler()


async def stop_ttl_scheduler():
    """Stop TTL cleanup scheduler."""
    await _ttl_manager.stop_cleanup_scheduler()
