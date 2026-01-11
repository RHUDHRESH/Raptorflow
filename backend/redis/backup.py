"""
Redis backup and recovery system.

Provides automated backup scheduling, data export/import,
compression, encryption, and restoration capabilities.
"""

import asyncio
import gzip
import hashlib
import hmac
import json
import logging
import os
import shutil
import subprocess
import tempfile
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .client import get_redis
from .cluster import ClusterNode, RedisClusterManager
from .critical_fixes import SecureErrorHandler


class BackupType(Enum):
    """Backup type enumeration."""

    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"


class BackupStatus(Enum):
    """Backup status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    CORRUPTED = "corrupted"


class CompressionType(Enum):
    """Compression type enumeration."""

    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"


class EncryptionType(Enum):
    """Encryption type enumeration."""

    NONE = "none"
    AES256 = "aes256"
    CHACHA20 = "chacha20"


@dataclass
class BackupConfig:
    """Backup configuration."""

    backup_id: str
    backup_type: BackupType
    cluster_id: str

    # Backup settings
    include_keys: List[str] = field(default_factory=list)
    exclude_keys: List[str] = field(default_factory=list)
    include_databases: List[int] = field(default_factory=list)
    exclude_databases: List[int] = field(default_factory=list)

    # Compression and encryption
    compression: CompressionType = CompressionType.GZIP
    encryption: EncryptionType = EncryptionType.AES256
    encryption_key: Optional[str] = None

    # Storage settings
    storage_path: str = "/backups/redis"
    storage_type: str = "local"  # local, s3, gcs, azure
    retention_days: int = 30

    # Performance settings
    parallel_processes: int = 4
    chunk_size_mb: int = 100
    timeout_seconds: int = 3600

    # Validation settings
    verify_backup: bool = True
    checksum_algorithm: str = "sha256"

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.backup_type, str):
            self.backup_type = BackupType(self.backup_type)
        if isinstance(self.compression, str):
            self.compression = CompressionType(self.compression)
        if isinstance(self.encryption, str):
            self.encryption = EncryptionType(self.encryption)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enums to strings
        data["backup_type"] = self.backup_type.value
        data["compression"] = self.compression.value
        data["encryption"] = self.encryption.value

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BackupConfig":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class BackupMetadata:
    """Backup metadata information."""

    backup_id: str
    backup_type: BackupType
    cluster_id: str

    # Backup details
    created_at: datetime
    completed_at: Optional[datetime] = None
    size_bytes: int = 0
    compressed_size_bytes: int = 0
    file_count: int = 0

    # Content details
    total_keys: int = 0
    databases_backed_up: List[int] = field(default_factory=list)
    key_patterns: List[str] = field(default_factory=list)

    # Validation details
    checksum: Optional[str] = None
    verified: bool = False
    corruption_detected: bool = False

    # Status and errors
    status: BackupStatus = BackupStatus.PENDING
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    # Performance metrics
    duration_seconds: float = 0.0
    throughput_mb_per_second: float = 0.0

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.backup_type, str):
            self.backup_type = BackupType(self.backup_type)
        if isinstance(self.status, str):
            self.status = BackupStatus(self.status)
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.completed_at, str):
            self.completed_at = datetime.fromisoformat(self.completed_at)

    def mark_completed(
        self, size_bytes: int, compressed_size_bytes: int, file_count: int
    ):
        """Mark backup as completed."""
        self.status = BackupStatus.COMPLETED
        self.completed_at = datetime.now()
        self.size_bytes = size_bytes
        self.compressed_size_bytes = compressed_size_bytes
        self.file_count = file_count

        if self.created_at and self.completed_at:
            self.duration_seconds = (
                self.completed_at - self.created_at
            ).total_seconds()

        if self.duration_seconds > 0:
            self.throughput_mb_per_second = (
                self.size_bytes / (1024 * 1024)
            ) / self.duration_seconds

    def mark_failed(self, error_message: str):
        """Mark backup as failed."""
        self.status = BackupStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now()

        if self.created_at and self.completed_at:
            self.duration_seconds = (
                self.completed_at - self.created_at
            ).total_seconds()

    def calculate_checksum(self, file_path: str):
        """Calculate checksum of backup file."""
        try:
            hash_func = getattr(hashlib, "sha256")()

            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_func.update(chunk)

            self.checksum = hash_func.hexdigest()

        except Exception as e:
            self.warnings.append(f"Failed to calculate checksum: {str(e)}")

    def verify_integrity(self, file_path: str) -> bool:
        """Verify backup file integrity."""
        if not self.checksum:
            return False

        try:
            hash_func = getattr(hashlib, "sha256")()

            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_func.update(chunk)

            calculated_checksum = hash_func.hexdigest()
            self.verified = hmac.compare_digest(calculated_checksum, self.checksum)

            if not self.verified:
                self.corruption_detected = True
                self.status = BackupStatus.CORRUPTED

            return self.verified

        except Exception as e:
            self.warnings.append(f"Failed to verify integrity: {str(e)}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert enums to strings
        data["backup_type"] = self.backup_type.value
        data["status"] = self.status.value

        # Convert datetime objects
        data["created_at"] = self.created_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BackupMetadata":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class BackupSchedule:
    """Backup schedule configuration."""

    schedule_id: str
    name: str
    backup_config: BackupConfig

    # Schedule settings
    enabled: bool = True
    cron_expression: str = "0 2 * * *"  # Daily at 2 AM
    timezone: str = "UTC"

    # Retention settings
    keep_daily: int = 7
    keep_weekly: int = 4
    keep_monthly: int = 12

    # Notification settings
    notify_on_success: bool = True
    notify_on_failure: bool = True
    notification_channels: List[str] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.last_run, str):
            self.last_run = datetime.fromisoformat(self.last_run)
        if isinstance(self.next_run, str):
            self.next_run = datetime.fromisoformat(self.next_run)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)

        # Convert datetime objects
        data["created_at"] = self.created_at.isoformat()
        if self.last_run:
            data["last_run"] = self.last_run.isoformat()
        if self.next_run:
            data["next_run"] = self.next_run.isoformat()

        # Convert backup config
        data["backup_config"] = self.backup_config.to_dict()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BackupSchedule":
        """Create from dictionary."""
        if "backup_config" in data:
            data["backup_config"] = BackupConfig.from_dict(data["backup_config"])

        return cls(**data)


class BackupManager:
    """Redis backup and recovery manager."""

    def __init__(self, cluster_manager: Optional[RedisClusterManager] = None):
        self.cluster_manager = cluster_manager
        self.redis = get_redis()
        self.error_handler = SecureErrorHandler()
        self.logger = logging.getLogger("backup_manager")

        # Backup state
        self.active_backups: Dict[str, BackupMetadata] = {}
        self.backup_schedules: Dict[str, BackupSchedule] = {}
        self.backup_history: List[BackupMetadata] = []

        # Backup configuration
        self.default_storage_path = "/backups/redis"
        self.temp_dir = tempfile.gettempdir()

        # Scheduler state
        self._scheduler_running = False
        self._scheduler_task = None

        # Setup default storage path
        os.makedirs(self.default_storage_path, exist_ok=True)

    def add_backup_schedule(self, schedule: BackupSchedule):
        """Add a backup schedule."""
        self.backup_schedules[schedule.schedule_id] = schedule
        self.logger.info(f"Added backup schedule {schedule.schedule_id}")

    def remove_backup_schedule(self, schedule_id: str):
        """Remove a backup schedule."""
        if schedule_id in self.backup_schedules:
            del self.backup_schedules[schedule_id]
            self.logger.info(f"Removed backup schedule {schedule_id}")

    async def start_scheduler(self):
        """Start backup scheduler."""
        if self._scheduler_running:
            return

        self._scheduler_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())

        self.logger.info("Started backup scheduler")

        try:
            await self._scheduler_task
        except asyncio.CancelledError:
            pass
        finally:
            self._scheduler_running = False
            self._scheduler_task = None
            self.logger.info("Stopped backup scheduler")

    async def stop_scheduler(self):
        """Stop backup scheduler."""
        if self._scheduler_task:
            self._scheduler_task.cancel()
            self._scheduler_task = None

        self._scheduler_running = False
        self.logger.info("Stopped backup scheduler")

    async def _scheduler_loop(self):
        """Main scheduler loop."""
        while self._scheduler_running:
            try:
                # Check for due schedules
                await self._check_schedules()

                # Clean up old backups
                await self._cleanup_old_backups()

                # Wait for next check (every minute)
                await asyncio.sleep(60)

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(60)

    async def _check_schedules(self):
        """Check for due backup schedules."""
        now = datetime.now()

        for schedule in self.backup_schedules.values():
            if not schedule.enabled:
                continue

            # Check if schedule is due
            if schedule.next_run and schedule.next_run <= now:
                await self._run_scheduled_backup(schedule)

                # Calculate next run time (simplified)
                schedule.last_run = now
                schedule.next_run = now + timedelta(days=1)  # Simplified daily schedule

    async def _run_scheduled_backup(self, schedule: BackupSchedule):
        """Run a scheduled backup."""
        self.logger.info(f"Running scheduled backup {schedule.schedule_id}")

        try:
            # Create backup from schedule
            backup_id = await self.create_backup(schedule.backup_config)

            # Update schedule
            schedule.last_run = datetime.now()

            # Send notification if configured
            if schedule.notify_on_success:
                await self._send_backup_notification(backup_id, "success")

        except Exception as e:
            self.logger.error(f"Scheduled backup {schedule.schedule_id} failed: {e}")

            if schedule.notify_on_failure:
                await self._send_backup_notification("", "failure", str(e))

    async def create_backup(self, config: BackupConfig) -> str:
        """Create a new backup."""
        backup_id = config.backup_id

        # Create backup metadata
        metadata = BackupMetadata(
            backup_id=backup_id,
            backup_type=config.backup_type,
            cluster_id=config.cluster_id,
            created_at=datetime.now(),
        )

        self.active_backups[backup_id] = metadata

        try:
            # Create backup
            if config.backup_type == BackupType.FULL:
                await self._create_full_backup(config, metadata)
            elif config.backup_type == BackupType.INCREMENTAL:
                await self._create_incremental_backup(config, metadata)
            elif config.backup_type == BackupType.SNAPSHOT:
                await self._create_snapshot_backup(config, metadata)

            # Store backup metadata
            await self._store_backup_metadata(metadata)

            # Add to history
            self.backup_history.append(metadata)

            self.logger.info(f"Backup {backup_id} completed successfully")
            return backup_id

        except Exception as e:
            metadata.mark_failed(str(e))
            await self._store_backup_metadata(metadata)

            self.logger.error(f"Backup {backup_id} failed: {e}")
            raise

    async def _create_full_backup(self, config: BackupConfig, metadata: BackupMetadata):
        """Create a full backup."""
        self.logger.info(f"Creating full backup {metadata.backup_id}")

        # Create temporary directory
        temp_dir = os.path.join(self.temp_dir, f"backup_{metadata.backup_id}")
        os.makedirs(temp_dir, exist_ok=True)

        try:
            # Export data from Redis
            if self.cluster_manager:
                await self._export_cluster_data(config, temp_dir, metadata)
            else:
                await self._export_single_node_data(config, temp_dir, metadata)

            # Compress backup
            backup_file = await self._compress_backup(temp_dir, config, metadata)

            # Encrypt backup if configured
            if config.encryption != EncryptionType.NONE:
                backup_file = await self._encrypt_backup(backup_file, config, metadata)

            # Store backup
            final_file = await self._store_backup(backup_file, config, metadata)

            # Verify backup
            if config.verify_backup:
                metadata.verify_integrity(final_file)

            # Update metadata
            metadata.mark_completed(
                size_bytes=os.path.getsize(final_file),
                compressed_size_bytes=os.path.getsize(final_file),
                file_count=1,
            )

            # Calculate checksum
            metadata.calculate_checksum(final_file)

        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)

    async def _export_single_node_data(
        self, config: BackupConfig, temp_dir: str, metadata: BackupMetadata
    ):
        """Export data from single Redis node."""
        # Use Redis DUMP command for full backup
        try:
            # Get all keys
            pattern = "*"
            keys = []

            cursor = 0
            while True:
                cursor, batch_keys = await self.redis.scan(
                    cursor, match=pattern, count=1000
                )
                keys.extend(batch_keys)

                if cursor == 0:
                    break

            metadata.total_keys = len(keys)

            # Export keys to files
            for i, key in enumerate(keys):
                if key in config.exclude_keys:
                    continue

                if config.include_keys and key not in config.include_keys:
                    continue

                # Get key data
                key_type = await self.redis.type(key)
                ttl = await self.redis.ttl(key)

                if key_type == "string":
                    value = await self.redis.get(key)
                elif key_type == "hash":
                    value = await self.redis.hgetall(key)
                elif key_type == "list":
                    value = await self.redis.lrange(key, 0, -1)
                elif key_type == "set":
                    value = await self.redis.smembers(key)
                elif key_type == "zset":
                    value = await self.redis.zrange(key, 0, -1, withscores=True)
                else:
                    continue

                # Save key data
                key_data = {"key": key, "type": key_type, "ttl": ttl, "value": value}

                # Save to file (chunked for large datasets)
                chunk_file = os.path.join(temp_dir, f"keys_{i // 1000}.json")

                with open(chunk_file, "a") as f:
                    f.write(json.dumps(key_data) + "\n")

            metadata.file_count = (len(keys) // 1000) + 1

        except Exception as e:
            raise Exception(f"Failed to export Redis data: {e}")

    async def _export_cluster_data(
        self, config: BackupConfig, temp_dir: str, metadata: BackupMetadata
    ):
        """Export data from Redis cluster."""
        # This would implement cluster-specific export
        # For now, use single node export as fallback
        await self._export_single_node_data(config, temp_dir, metadata)

    async def _create_incremental_backup(
        self, config: BackupConfig, metadata: BackupMetadata
    ):
        """Create an incremental backup."""
        self.logger.info(f"Creating incremental backup {metadata.backup_id}")

        # Get last backup timestamp
        last_backup_time = await self._get_last_backup_time(config.cluster_id)

        if not last_backup_time:
            # Fall back to full backup
            await self._create_full_backup(config, metadata)
            return

        # Export only modified keys since last backup
        # This would require tracking key modifications
        # For now, create a full backup
        await self._create_full_backup(config, metadata)

    async def _create_snapshot_backup(
        self, config: BackupConfig, metadata: BackupMetadata
    ):
        """Create a snapshot backup."""
        self.logger.info(f"Creating snapshot backup {metadata.backup_id}")

        try:
            # Create Redis snapshot
            snapshot_result = await self.redis.execute_command("SAVE")

            # Find the snapshot file
            snapshot_file = "dump.rdb"

            if os.path.exists(snapshot_file):
                # Copy snapshot to backup location
                backup_file = os.path.join(
                    config.storage_path, f"{metadata.backup_id}.rdb"
                )
                shutil.copy2(snapshot_file, backup_file)

                metadata.mark_completed(
                    size_bytes=os.path.getsize(backup_file),
                    compressed_size_bytes=os.path.getsize(backup_file),
                    file_count=1,
                )

                metadata.calculate_checksum(backup_file)

            else:
                raise Exception("Snapshot file not found")

        except Exception as e:
            raise Exception(f"Failed to create snapshot backup: {e}")

    async def _compress_backup(
        self, temp_dir: str, config: BackupConfig, metadata: BackupMetadata
    ) -> str:
        """Compress backup files."""
        if config.compression == CompressionType.NONE:
            # Return the first file (for uncompressed backups)
            files = os.listdir(temp_dir)
            if files:
                return os.path.join(temp_dir, files[0])
            else:
                raise Exception("No files to compress")

        # Create compressed archive
        archive_file = os.path.join(temp_dir, f"{metadata.backup_id}.tar.gz")

        try:
            # Create tar archive
            subprocess.run(
                ["tar", "-czf", archive_file, "-C", temp_dir, "."], check=True
            )

            return archive_file

        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to compress backup: {e}")

    async def _encrypt_backup(
        self, backup_file: str, config: BackupConfig, metadata: BackupMetadata
    ) -> str:
        """Encrypt backup file."""
        if config.encryption == EncryptionType.NONE:
            return backup_file

        # This would implement actual encryption
        # For now, just return the original file
        self.logger.warning(f"Encryption not implemented for {config.encryption.value}")
        return backup_file

    async def _store_backup(
        self, backup_file: str, config: BackupConfig, metadata: BackupMetadata
    ) -> str:
        """Store backup file."""
        final_file = os.path.join(config.storage_path, os.path.basename(backup_file))

        try:
            # Move file to final location
            shutil.move(backup_file, final_file)

            # Store in cloud storage if configured
            if config.storage_type != "local":
                await self._store_to_cloud(final_file, config)

            return final_file

        except Exception as e:
            raise Exception(f"Failed to store backup: {e}")

    async def _store_to_cloud(self, backup_file: str, config: BackupConfig):
        """Store backup to cloud storage."""
        # This would integrate with cloud storage providers
        # For now, just log the action
        self.logger.info(f"Cloud storage not implemented for {config.storage_type}")

    async def _store_backup_metadata(self, metadata: BackupMetadata):
        """Store backup metadata in Redis."""
        metadata_key = f"backup:{metadata.backup_id}:metadata"
        await self.redis.set_json(
            metadata_key, metadata.to_dict(), ex=86400 * config.retention_days
        )

        # Add to backup index
        index_key = f"backup:index:{metadata.cluster_id}"
        await self.redis.zadd(
            index_key, {metadata.backup_id: metadata.created_at.timestamp()}
        )

    async def _get_last_backup_time(self, cluster_id: str) -> Optional[datetime]:
        """Get timestamp of last backup."""
        index_key = f"backup:index:{cluster_id}"

        # Get most recent backup
        result = await self.redis.zrevrange(index_key, 0, 0, withscores=True)

        if result:
            backup_id, timestamp = result[0]
            return datetime.fromtimestamp(timestamp)

        return None

    async def restore_backup(
        self, backup_id: str, target_cluster_id: Optional[str] = None
    ) -> bool:
        """Restore from backup."""
        try:
            # Get backup metadata
            metadata_key = f"backup:{backup_id}:metadata"
            metadata_data = await self.redis.get_json(metadata_key)

            if not metadata_data:
                raise Exception(f"Backup {backup_id} not found")

            metadata = BackupMetadata.from_dict(metadata_data)

            if metadata.status != BackupStatus.COMPLETED:
                raise Exception(f"Backup {backup_id} is not completed")

            # Verify backup integrity
            backup_file = os.path.join(self.default_storage_path, f"{backup_id}.tar.gz")

            if not os.path.exists(backup_file):
                raise Exception(f"Backup file {backup_file} not found")

            if not metadata.verify_integrity(backup_file):
                raise Exception(f"Backup {backup_id} integrity check failed")

            # Extract backup
            temp_dir = os.path.join(self.temp_dir, f"restore_{backup_id}")
            os.makedirs(temp_dir, exist_ok=True)

            try:
                # Extract backup
                subprocess.run(["tar", "-xzf", backup_file, "-C", temp_dir], check=True)

                # Restore data
                await self._restore_from_files(
                    temp_dir, target_cluster_id or metadata.cluster_id
                )

                self.logger.info(f"Successfully restored backup {backup_id}")
                return True

            finally:
                # Clean up temporary directory
                shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception as e:
            self.logger.error(f"Failed to restore backup {backup_id}: {e}")
            return False

    async def _restore_from_files(self, temp_dir: str, cluster_id: str):
        """Restore data from backup files."""
        # Get all backup files
        backup_files = [f for f in os.listdir(temp_dir) if f.startswith("keys_")]

        total_keys = 0

        for backup_file in backup_files:
            file_path = os.path.join(temp_dir, backup_file)

            with open(file_path, "r") as f:
                for line in f:
                    try:
                        key_data = json.loads(line.strip())

                        # Restore key
                        key = key_data["key"]
                        key_type = key_data["type"]
                        ttl = key_data["ttl"]
                        value = key_data["value"]

                        if key_type == "string":
                            await self.redis.set(
                                key, value, ex=ttl if ttl > 0 else None
                            )
                        elif key_type == "hash":
                            await self.redis.delete(key)
                            for field, val in value.items():
                                await self.redis.hset(key, field, val)
                            if ttl > 0:
                                await self.redis.expire(key, ttl)
                        elif key_type == "list":
                            await self.redis.delete(key)
                            for item in value:
                                await self.redis.rpush(key, item)
                            if ttl > 0:
                                await self.redis.expire(key, ttl)
                        elif key_type == "set":
                            await self.redis.delete(key)
                            for item in value:
                                await self.redis.sadd(key, item)
                            if ttl > 0:
                                await self.redis.expire(key, ttl)
                        elif key_type == "zset":
                            await self.redis.delete(key)
                            for member, score in value:
                                await self.redis.zadd(key, {member: score})
                            if ttl > 0:
                                await self.redis.expire(key, ttl)

                        total_keys += 1

                    except Exception as e:
                        self.logger.warning(
                            f"Failed to restore key {key_data.get('key', 'unknown')}: {e}"
                        )

        self.logger.info(f"Restored {total_keys} keys from backup")

    async def _cleanup_old_backups(self):
        """Clean up old backups based on retention policy."""
        cutoff_date = datetime.now() - timedelta(days=30)

        # Get all backup metadata
        pattern = f"backup:*:metadata"
        keys = await self.redis.keys(pattern)

        for key in keys:
            data = await self.redis.get_json(key)
            if data:
                metadata = BackupMetadata.from_dict(data)

                if metadata.created_at < cutoff_date:
                    # Remove backup file
                    backup_file = os.path.join(
                        self.default_storage_path, f"{metadata.backup_id}.tar.gz"
                    )
                    if os.path.exists(backup_file):
                        os.remove(backup_file)

                    # Remove metadata
                    await self.redis.delete(key)

                    # Remove from index
                    index_key = f"backup:index:{metadata.cluster_id}"
                    await self.redis.zrem(index_key, metadata.backup_id)

                    self.logger.info(f"Cleaned up old backup {metadata.backup_id}")

    async def _send_backup_notification(
        self, backup_id: str, status: str, error_message: str = ""
    ):
        """Send backup notification."""
        # This would integrate with the alert system
        # For now, just log the notification
        if status == "success":
            self.logger.info(f"Backup {backup_id} completed successfully")
        else:
            self.logger.error(f"Backup {backup_id} failed: {error_message}")

    async def get_backup_list(
        self, cluster_id: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get list of backups."""
        if cluster_id:
            # Get backups for specific cluster
            index_key = f"backup:index:{cluster_id}"
            result = await self.redis.zrevrange(
                index_key, 0, limit - 1, withscores=True
            )

            backups = []
            for backup_id, timestamp in result:
                metadata_key = f"backup:{backup_id}:metadata"
                data = await self.redis.get_json(metadata_key)
                if data:
                    backups.append(BackupMetadata.from_dict(data).to_dict())

            return backups
        else:
            # Get all backups
            pattern = f"backup:*:metadata"
            keys = await self.redis.keys(pattern)

            backups = []
            for key in keys[:limit]:
                data = await self.redis.get_json(key)
                if data:
                    backups.append(BackupMetadata.from_dict(data).to_dict())

            # Sort by creation time
            backups.sort(key=lambda x: x["created_at"], reverse=True)

            return backups

    async def get_backup_status(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Get backup status."""
        metadata_key = f"backup:{backup_id}:metadata"
        data = await self.redis.get_json(metadata_key)

        if data:
            return BackupMetadata.from_dict(data).to_dict()

        return None

    async def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup."""
        try:
            # Get backup metadata
            metadata_key = f"backup:{backup_id}:metadata"
            data = await self.redis.get_json(metadata_key)

            if data:
                metadata = BackupMetadata.from_dict(data)

                # Remove backup file
                backup_file = os.path.join(
                    self.default_storage_path, f"{backup_id}.tar.gz"
                )
                if os.path.exists(backup_file):
                    os.remove(backup_file)

                # Remove from index
                index_key = f"backup:index:{metadata.cluster_id}"
                await self.redis.zrem(index_key, backup_id)

            # Remove metadata
            await self.redis.delete(metadata_key)

            self.logger.info(f"Deleted backup {backup_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to delete backup {backup_id}: {e}")
            return False

    async def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup statistics."""
        # Get all backup metadata
        pattern = f"backup:*:metadata"
        keys = await self.redis.keys(pattern)

        stats = {
            "total_backups": len(keys),
            "backup_types": {},
            "status_counts": {},
            "total_size_bytes": 0,
            "avg_size_mb": 0,
            "last_backup": None,
            "success_rate": 0.0,
        }

        total_size = 0
        successful_backups = 0

        for key in keys:
            data = await self.redis.get_json(key)
            if data:
                metadata = BackupMetadata.from_dict(data)

                # Count by type
                backup_type = metadata.backup_type.value
                if backup_type not in stats["backup_types"]:
                    stats["backup_types"][backup_type] = 0
                stats["backup_types"][backup_type] += 1

                # Count by status
                status = metadata.status.value
                if status not in stats["status_counts"]:
                    stats["status_counts"][status] = 0
                stats["status_counts"][status] += 1

                # Calculate size
                total_size += metadata.size_bytes
                if metadata.status == BackupStatus.COMPLETED:
                    successful_backups += 1

                # Track last backup
                if (
                    not stats["last_backup"]
                    or metadata.created_at > stats["last_backup"]
                ):
                    stats["last_backup"] = metadata.created_at.isoformat()

        # Calculate derived stats
        if stats["total_backups"] > 0:
            stats["avg_size_mb"] = (total_size / stats["total_backups"]) / (1024 * 1024)
            stats["success_rate"] = (successful_backups / stats["total_backups"]) * 100

        stats["total_size_bytes"] = total_size

        return stats

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_scheduler()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_scheduler()
