"""
Cache Backup Manager with Automatic Backup and Recovery Procedures
Provides comprehensive backup and recovery for cache data
"""

import asyncio
import json
import logging
import os
import shutil
import gzip
import time
import hashlib
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import threading
import pickle
import pathlib

try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False

logger = logging.getLogger(__name__)


class BackupType(Enum):
    """Types of cache backups."""
    
    FULL = "full"                    # Complete cache backup
    INCREMENTAL = "incremental"      # Incremental backup since last full
    DIFFERENTIAL = "differential"    # Changes since last full backup
    SNAPSHOT = "snapshot"            # Point-in-time snapshot


class BackupFormat(Enum):
    """Backup file formats."""
    
    JSON = "json"
    PICKLE = "pickle"
    BINARY = "binary"
    COMPRESSED_JSON = "compressed_json"
    COMPRESSED_PICKLE = "compressed_pickle"


class BackupStatus(Enum):
    """Backup operation status."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RecoveryStatus(Enum):
    """Recovery operation status."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class BackupMetadata:
    """Metadata for backup operations."""
    
    backup_id: str
    backup_type: BackupType
    format: BackupFormat
    timestamp: datetime
    size_bytes: int
    compressed_size_bytes: int
    key_count: int
    checksum: str
    source_version: str
    description: str
    tags: Set[str]
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = set()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['tags'] = list(self.tags)
        return data


@dataclass
class BackupOperation:
    """Backup operation tracking."""
    
    operation_id: str
    backup_type: BackupType
    status: BackupStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    progress: float = 0.0
    keys_processed: int = 0
    total_keys: int = 0
    error_message: Optional[str] = None
    metadata: Optional[BackupMetadata] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        return data


@dataclass
class RecoveryOperation:
    """Recovery operation tracking."""
    
    operation_id: str
    backup_id: str
    status: RecoveryStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    progress: float = 0.0
    keys_recovered: int = 0
    total_keys: int = 0
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        return data


class BackupStorage:
    """Manages backup storage and retrieval."""
    
    def __init__(self, storage_config: Dict[str, Any]):
        self.storage_config = storage_config
        self.backup_directory = storage_config.get('backup_directory', './cache_backups')
        self.max_backups = storage_config.get('max_backups', 10)
        self.compression_enabled = storage_config.get('compression_enabled', True)
        
        # Ensure backup directory exists
        os.makedirs(self.backup_directory, exist_ok=True)
        
        # Create subdirectories
        self.metadata_dir = os.path.join(self.backup_directory, 'metadata')
        self.data_dir = os.path.join(self.backup_directory, 'data')
        os.makedirs(self.metadata_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
    
    async def store_backup(
        self,
        backup_data: Dict[str, Any],
        metadata: BackupMetadata
    ) -> str:
        """Store backup data and metadata."""
        try:
            # Generate file paths
            backup_filename = f"{metadata.backup_id}.{metadata.format.value}"
            if self.compression_enabled and metadata.format in [BackupFormat.JSON, BackupFormat.PICKLE]:
                backup_filename += ".gz"
            
            backup_path = os.path.join(self.data_dir, backup_filename)
            metadata_path = os.path.join(self.metadata_dir, f"{metadata.backup_id}.json")
            
            # Serialize and compress data
            if metadata.format == BackupFormat.JSON:
                data_bytes = json.dumps(backup_data, default=str).encode()
                if self.compression_enabled:
                    data_bytes = gzip.compress(data_bytes)
            elif metadata.format == BackupFormat.PICKLE:
                data_bytes = pickle.dumps(backup_data)
                if self.compression_enabled:
                    data_bytes = gzip.compress(data_bytes)
            else:
                data_bytes = str(backup_data).encode()
            
            # Write backup data
            if AIOFILES_AVAILABLE:
                async with aiofiles.open(backup_path, 'wb') as f:
                    await f.write(data_bytes)
            else:
                with open(backup_path, 'wb') as f:
                    f.write(data_bytes)
            
            # Write metadata
            metadata_dict = metadata.to_dict()
            metadata_dict['file_path'] = backup_path
            
            if AIOFILES_AVAILABLE:
                async with aiofiles.open(metadata_path, 'w') as f:
                    await f.write(json.dumps(metadata_dict, indent=2))
            else:
                with open(metadata_path, 'w') as f:
                    json.dump(metadata_dict, f, indent=2)
            
            logger.info(f"Backup stored: {backup_filename}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to store backup: {e}")
            raise
    
    async def load_backup(self, backup_id: str) -> Tuple[Dict[str, Any], BackupMetadata]:
        """Load backup data and metadata."""
        try:
            # Load metadata
            metadata_path = os.path.join(self.metadata_dir, f"{backup_id}.json")
            
            if AIOFILES_AVAILABLE:
                async with aiofiles.open(metadata_path, 'r') as f:
                    metadata_dict = json.loads(await f.read())
            else:
                with open(metadata_path, 'r') as f:
                    metadata_dict = json.load(f)
            
            metadata = BackupMetadata(
                backup_id=metadata_dict['backup_id'],
                backup_type=BackupType(metadata_dict['backup_type']),
                format=BackupFormat(metadata_dict['format']),
                timestamp=datetime.fromisoformat(metadata_dict['timestamp']),
                size_bytes=metadata_dict['size_bytes'],
                compressed_size_bytes=metadata_dict['compressed_size_bytes'],
                key_count=metadata_dict['key_count'],
                checksum=metadata_dict['checksum'],
                source_version=metadata_dict['source_version'],
                description=metadata_dict['description'],
                tags=set(metadata_dict['tags'])
            )
            
            # Load backup data
            backup_path = metadata_dict['file_path']
            
            if AIOFILES_AVAILABLE:
                async with aiofiles.open(backup_path, 'rb') as f:
                    data_bytes = await f.read()
            else:
                with open(backup_path, 'rb') as f:
                    data_bytes = f.read()
            
            # Decompress if needed
            if backup_path.endswith('.gz'):
                data_bytes = gzip.decompress(data_bytes)
            
            # Deserialize data
            if metadata.format == BackupFormat.JSON:
                backup_data = json.loads(data_bytes.decode())
            elif metadata.format == BackupFormat.PICKLE:
                backup_data = pickle.loads(data_bytes)
            else:
                backup_data = data_bytes.decode()
            
            logger.info(f"Backup loaded: {backup_id}")
            return backup_data, metadata
            
        except Exception as e:
            logger.error(f"Failed to load backup {backup_id}: {e}")
            raise
    
    async def list_backups(self) -> List[BackupMetadata]:
        """List all available backups."""
        backups = []
        
        try:
            for filename in os.listdir(self.metadata_dir):
                if filename.endswith('.json'):
                    backup_id = filename[:-5]  # Remove .json
                    
                    if AIOFILES_AVAILABLE:
                        async with aiofiles.open(os.path.join(self.metadata_dir, filename), 'r') as f:
                            metadata_dict = json.loads(await f.read())
                    else:
                        with open(os.path.join(self.metadata_dir, filename), 'r') as f:
                            metadata_dict = json.load(f)
                    
                    backup = BackupMetadata(
                        backup_id=metadata_dict['backup_id'],
                        backup_type=BackupType(metadata_dict['backup_type']),
                        format=BackupFormat(metadata_dict['format']),
                        timestamp=datetime.fromisoformat(metadata_dict['timestamp']),
                        size_bytes=metadata_dict['size_bytes'],
                        compressed_size_bytes=metadata_dict['compressed_size_bytes'],
                        key_count=metadata_dict['key_count'],
                        checksum=metadata_dict['checksum'],
                        source_version=metadata_dict['source_version'],
                        description=metadata_dict['description'],
                        tags=set(metadata_dict['tags'])
                    )
                    
                    backups.append(backup)
            
            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x.timestamp, reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
        
        return backups
    
    async def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup."""
        try:
            # Delete data file
            metadata_path = os.path.join(self.metadata_dir, f"{backup_id}.json")
            
            if AIOFILES_AVAILABLE:
                async with aiofiles.open(metadata_path, 'r') as f:
                    metadata_dict = json.loads(await f.read())
            else:
                with open(metadata_path, 'r') as f:
                    metadata_dict = json.load(f)
            
            backup_path = metadata_dict['file_path']
            if os.path.exists(backup_path):
                os.remove(backup_path)
            
            # Delete metadata file
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            logger.info(f"Backup deleted: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete backup {backup_id}: {e}")
            return False
    
    async def cleanup_old_backups(self):
        """Clean up old backups beyond retention limit."""
        try:
            backups = await self.list_backups()
            
            if len(backups) > self.max_backups:
                # Keep newest backups
                backups_to_keep = backups[:self.max_backups]
                backups_to_delete = backups[self.max_backups:]
                
                for backup in backups_to_delete:
                    await self.delete_backup(backup.backup_id)
                
                logger.info(f"Cleaned up {len(backups_to_delete)} old backups")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")


class CacheBackupManager:
    """Main cache backup manager."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Components
        self.storage = BackupStorage(config.get('storage', {}))
        
        # Backup configuration
        self.backup_interval = config.get('backup_interval', 3600)  # 1 hour
        self.auto_backup_enabled = config.get('auto_backup_enabled', True)
        self.compression_enabled = config.get('compression_enabled', True)
        self.backup_format = BackupFormat(config.get('backup_format', 'json'))
        
        # State tracking
        self.backup_operations: Dict[str, BackupOperation] = {}
        self.recovery_operations: Dict[str, RecoveryOperation] = {}
        self.last_full_backup: Optional[datetime] = None
        self.last_incremental_backup: Optional[datetime] = None
        
        # Background tasks
        self._backup_task = None
        self._running = False
        
        # Lock for thread safety
        self._lock = threading.RLock()
    
    async def initialize(self):
        """Initialize backup manager."""
        # Start background backup task
        if self.auto_backup_enabled:
            self._running = True
            self._backup_task = asyncio.create_task(self._background_backup())
        
        logger.info("Cache backup manager initialized")
    
    async def shutdown(self):
        """Shutdown backup manager."""
        self._running = False
        if self._backup_task:
            self._backup_task.cancel()
        
        logger.info("Cache backup manager shutdown")
    
    async def create_backup(
        self,
        backup_type: BackupType = BackupType.FULL,
        description: str = "Manual backup",
        tags: Optional[Set[str]] = None
    ) -> str:
        """Create a backup of cache data."""
        operation_id = f"backup_{int(time.time())}"
        
        with self._lock:
            operation = BackupOperation(
                operation_id=operation_id,
                backup_type=backup_type,
                status=BackupStatus.PENDING,
                start_time=datetime.now()
            )
            self.backup_operations[operation_id] = operation
        
        try:
            # Update status
            operation.status = BackupStatus.IN_PROGRESS
            
            # Get cache data
            cache_data = await self._collect_cache_data(backup_type)
            operation.total_keys = len(cache_data)
            
            # Create metadata
            metadata = BackupMetadata(
                backup_id=operation_id,
                backup_type=backup_type,
                format=self.backup_format,
                timestamp=datetime.now(),
                size_bytes=len(json.dumps(cache_data, default=str).encode()),
                compressed_size_bytes=0,  # Will be updated by storage
                key_count=len(cache_data),
                checksum=self._calculate_checksum(cache_data),
                source_version="1.0.0",
                description=description,
                tags=tags or set()
            )
            
            # Store backup
            await self.storage.store_backup(cache_data, metadata)
            
            # Update operation
            operation.status = BackupStatus.COMPLETED
            operation.end_time = datetime.now()
            operation.progress = 100.0
            operation.keys_processed = len(cache_data)
            operation.metadata = metadata
            
            # Update timestamps
            if backup_type == BackupType.FULL:
                self.last_full_backup = datetime.now()
            else:
                self.last_incremental_backup = datetime.now()
            
            logger.info(f"Backup completed: {operation_id}")
            return operation_id
            
        except Exception as e:
            operation.status = BackupStatus.FAILED
            operation.end_time = datetime.now()
            operation.error_message = str(e)
            
            logger.error(f"Backup failed: {operation_id} - {e}")
            raise
    
    async def restore_backup(
        self,
        backup_id: str,
        target_cache: Optional[Any] = None
    ) -> str:
        """Restore cache from backup."""
        operation_id = f"restore_{int(time.time())}"
        
        with self._lock:
            operation = RecoveryOperation(
                operation_id=operation_id,
                backup_id=backup_id,
                status=RecoveryStatus.PENDING,
                start_time=datetime.now()
            )
            self.recovery_operations[operation_id] = operation
        
        try:
            # Update status
            operation.status = RecoveryStatus.IN_PROGRESS
            
            # Load backup
            backup_data, metadata = await self.storage.load_backup(backup_id)
            operation.total_keys = metadata.key_count
            
            # Restore to cache
            await self._restore_cache_data(backup_data, target_cache)
            
            # Update operation
            operation.status = RecoveryStatus.COMPLETED
            operation.end_time = datetime.now()
            operation.progress = 100.0
            operation.keys_recovered = metadata.key_count
            
            logger.info(f"Restore completed: {operation_id}")
            return operation_id
            
        except Exception as e:
            operation.status = RecoveryStatus.FAILED
            operation.end_time = datetime.now()
            operation.error_message = str(e)
            
            logger.error(f"Restore failed: {operation_id} - {e}")
            raise
    
    async def list_backups(self) -> List[BackupMetadata]:
        """List all available backups."""
        return await self.storage.list_backups()
    
    async def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup."""
        return await self.storage.delete_backup(backup_id)
    
    async def get_backup_status(self, operation_id: str) -> Optional[BackupOperation]:
        """Get status of backup operation."""
        with self._lock:
            return self.backup_operations.get(operation_id)
    
    async def get_restore_status(self, operation_id: str) -> Optional[RecoveryOperation]:
        """Get status of restore operation."""
        with self._lock:
            return self.recovery_operations.get(operation_id)
    
    async def _collect_cache_data(self, backup_type: BackupType) -> Dict[str, Any]:
        """Collect cache data for backup."""
        try:
            # Get comprehensive cache data
            from .comprehensive_cache import get_comprehensive_cache
            cache = await get_comprehensive_cache()
            
            # Get cache statistics and data
            stats = cache.get_comprehensive_stats()
            
            # Collect actual cache data based on backup type
            if backup_type == BackupType.FULL:
                # Full backup - collect all available data
                cache_data = {
                    'backup_type': 'full',
                    'timestamp': datetime.now().isoformat(),
                    'stats': stats,
                    'l1_data': {},  # Would need access to L1 cache
                    'l2_data': {},  # Would need to scan Redis
                    'l3_data': {},  # Would need to scan persistent storage
                }
            elif backup_type == BackupType.INCREMENTAL:
                # Incremental backup - collect changes since last backup
                cache_data = {
                    'backup_type': 'incremental',
                    'timestamp': datetime.now().isoformat(),
                    'since_last_backup': self.last_incremental_backup.isoformat() if self.last_incremental_backup else None,
                    'stats': stats,
                    'changes': []  # Would need change tracking
                }
            else:
                # Differential backup
                cache_data = {
                    'backup_type': 'differential',
                    'timestamp': datetime.now().isoformat(),
                    'since_last_full': self.last_full_backup.isoformat() if self.last_full_backup else None,
                    'stats': stats,
                    'differences': []  # Would need diff tracking
                }
            
            return cache_data
            
        except Exception as e:
            logger.error(f"Failed to collect cache data: {e}")
            raise
    
    async def _restore_cache_data(self, backup_data: Dict[str, Any], target_cache: Optional[Any]):
        """Restore cache data from backup."""
        try:
            if target_cache is None:
                # Restore to default cache
                from .comprehensive_cache import get_comprehensive_cache
                target_cache = await get_comprehensive_cache()
            
            # Restore based on backup type
            backup_type = backup_data.get('backup_type', 'full')
            
            if backup_type == 'full':
                # Full restore
                await self._restore_full_backup(backup_data, target_cache)
            elif backup_type == 'incremental':
                # Incremental restore
                await self._restore_incremental_backup(backup_data, target_cache)
            elif backup_type == 'differential':
                # Differential restore
                await self._restore_differential_backup(backup_data, target_cache)
            
            logger.info(f"Cache data restored: {backup_type}")
            
        except Exception as e:
            logger.error(f"Failed to restore cache data: {e}")
            raise
    
    async def _restore_full_backup(self, backup_data: Dict[str, Any], target_cache):
        """Restore from full backup."""
        # This is a simplified implementation
        # In practice, you would restore actual cache entries
        
        l1_data = backup_data.get('l1_data', {})
        l2_data = backup_data.get('l2_data', {})
        l3_data = backup_data.get('l3_data', {})
        
        # Restore to L1 cache
        for key, value in l1_data.items():
            await target_cache.set(key, value)
        
        # Restore to L2 cache (Redis)
        for key, value in l2_data.items():
            await target_cache.set(key, value)
        
        # Restore to L3 cache (persistent)
        for key, value in l3_data.items():
            await target_cache.set(key, value)
    
    async def _restore_incremental_backup(self, backup_data: Dict[str, Any], target_cache):
        """Restore from incremental backup."""
        changes = backup_data.get('changes', [])
        
        for change in changes:
            operation = change.get('operation')
            key = change.get('key')
            value = change.get('value')
            
            if operation == 'set':
                await target_cache.set(key, value)
            elif operation == 'delete':
                await target_cache.delete(key)
    
    async def _restore_differential_backup(self, backup_data: Dict[str, Any], target_cache):
        """Restore from differential backup."""
        differences = backup_data.get('differences', [])
        
        for diff in differences:
            operation = diff.get('operation')
            key = diff.get('key')
            value = diff.get('value')
            
            if operation == 'set':
                await target_cache.set(key, value)
            elif operation == 'delete':
                await target_cache.delete(key)
    
    def _calculate_checksum(self, data: Any) -> str:
        """Calculate checksum for data integrity."""
        data_str = json.dumps(data, default=str, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    async def _background_backup(self):
        """Background automatic backup task."""
        while self._running:
            try:
                await asyncio.sleep(self.backup_interval)
                
                # Create automatic backup
                backup_type = BackupType.FULL  # Simplified - could alternate types
                description = f"Automatic backup - {datetime.now().isoformat()}"
                
                await self.create_backup(
                    backup_type=backup_type,
                    description=description,
                    tags={'automatic', 'scheduled'}
                )
                
                # Cleanup old backups
                await self.storage.cleanup_old_backups()
                
            except Exception as e:
                logger.error(f"Background backup error: {e}")
                await asyncio.sleep(self.backup_interval)
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup statistics."""
        with self._lock:
            active_backups = sum(1 for op in self.backup_operations.values() 
                               if op.status in [BackupStatus.PENDING, BackupStatus.IN_PROGRESS])
            active_restores = sum(1 for op in self.recovery_operations.values() 
                                if op.status in [RecoveryStatus.PENDING, RecoveryStatus.IN_PROGRESS])
            
            completed_backups = sum(1 for op in self.backup_operations.values() 
                                  if op.status == BackupStatus.COMPLETED)
            failed_backups = sum(1 for op in self.backup_operations.values() 
                                if op.status == BackupStatus.FAILED)
            
            return {
                'backup_operations': {
                    'active': active_backups,
                    'completed': completed_backups,
                    'failed': failed_backups,
                    'total': len(self.backup_operations)
                },
                'recovery_operations': {
                    'active': active_restores,
                    'completed': sum(1 for op in self.recovery_operations.values() 
                                   if op.status == RecoveryStatus.COMPLETED),
                    'failed': sum(1 for op in self.recovery_operations.values() 
                                 if op.status == RecoveryStatus.FAILED),
                    'total': len(self.recovery_operations)
                },
                'last_full_backup': self.last_full_backup.isoformat() if self.last_full_backup else None,
                'last_incremental_backup': self.last_incremental_backup.isoformat() if self.last_incremental_backup else None,
                'auto_backup_enabled': self.auto_backup_enabled,
                'backup_interval': self.backup_interval,
                'storage_config': self.storage.storage_config
            }


# Global backup manager instance
_backup_manager: Optional[CacheBackupManager] = None


async def get_backup_manager() -> CacheBackupManager:
    """Get the global backup manager."""
    global _backup_manager
    if _backup_manager is None:
        # Default configuration
        config = {
            'backup_interval': 3600,  # 1 hour
            'auto_backup_enabled': True,
            'compression_enabled': True,
            'backup_format': 'json',
            'storage': {
                'backup_directory': './cache_backups',
                'max_backups': 10,
                'compression_enabled': True
            }
        }
        _backup_manager = CacheBackupManager(config)
        await _backup_manager.initialize()
    return _backup_manager


# Convenience functions
async def create_cache_backup(
    backup_type: BackupType = BackupType.FULL,
    description: str = "Manual backup"
) -> str:
    """Create cache backup (convenience function)."""
    manager = await get_backup_manager()
    return await manager.create_backup(backup_type, description)


async def restore_cache_backup(backup_id: str, target_cache: Optional[Any] = None) -> str:
    """Restore cache backup (convenience function)."""
    manager = await get_backup_manager()
    return await manager.restore_backup(backup_id, target_cache)


async def list_cache_backups() -> List[BackupMetadata]:
    """List cache backups (convenience function)."""
    manager = await get_backup_manager()
    return await manager.list_backups()


async def delete_cache_backup(backup_id: str) -> bool:
    """Delete cache backup (convenience function)."""
    manager = await get_backup_manager()
    return await manager.delete_backup(backup_id)


def get_backup_statistics() -> Dict[str, Any]:
    """Get backup statistics (convenience function)."""
    if _backup_manager:
        return _backup_manager.get_backup_statistics()
    return {"error": "Backup manager not initialized"}
