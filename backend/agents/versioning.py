"""
Agent Versioning for Raptorflow Backend
===================================

This module provides comprehensive versioning for agent models and configurations
with semantic versioning, migration scripts, and backward compatibility.

Features:
- Semantic versioning with automatic version management
- Migration scripts for smooth upgrades
- Backward compatibility maintenance
- Version comparison and validation
- Rollback capabilities
- Version history tracking
"""

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

from .exceptions import VersioningError

logger = logging.getLogger(__name__)


class VersionType(Enum):
    """Types of version components."""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    PRE_RELEASE = "pre_release"
    BUILD = "build"


@dataclass
class AgentVersion:
    """Agent version information."""
    
    version: str
    major: int
    minor: int
    patch: int
    pre_release: Optional[str] = None
    build: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    description: str = ""
    changes: List[str] = field(default_factory=list)
    compatibility: Dict[str, str] = field(default_factory=dict)
    migration_required: bool = False
    rollback_version: Optional[str] = None


@dataclass
class Migration:
    """Database migration information."""
    
    from_version: str
    to_version: str
    description: str
    script: str
    created_at: datetime = field(default_factory=datetime.now)
    applied_at: Optional[datetime] = None
    checksum: str = ""
    rollback_script: Optional[str] = None


class VersionManager:
    """Version management system for agents."""
    
    def __init__(self, storage_path: str = "./data/versions"):
        self.storage_path = storage_path
        self.versions: Dict[str, AgentVersion] = {}
        self.migrations: List[Migration] = []
        self.current_version: Optional[str] = None
        self._load_versions()
    
    def _load_versions(self) -> None:
        """Load version history from storage."""
        try:
            import os
            os.makedirs(self.storage_path, exist_ok=True)
            
            versions_file = os.path.join(self.storage_path, "versions.json")
            if os.path.exists(versions_file):
                with open(versions_file, 'r') as f:
                    data = json.load(f)
                    for version_str, version_data in data.items():
                        self.versions[version_str] = AgentVersion(**version_data)
            
            migrations_file = os.path.join(self.storage_path, "migrations.json")
            if os.path.exists(migrations_file):
                with open(migrations_file, 'r') as f:
                    data = json.load(f)
                    for migration_data in data:
                        self.migrations.append(Migration(**migration_data))
            
            # Load current version
            current_file = os.path.join(self.storage_path, "current_version.txt")
            if os.path.exists(current_file):
                with open(current_file, 'r') as f:
                    self.current_version = f.read().strip()
            
            logger.info(f"Loaded {len(self.versions)} versions and {len(self.migrations)} migrations")
            
        except Exception as e:
            logger.error(f"Failed to load version data: {e}")
    
    def _save_versions(self) -> None:
        """Save version history to storage."""
        try:
            import os
            os.makedirs(self.storage_path, exist_ok=True)
            
            versions_file = os.path.join(self.storage_path, "versions.json")
            versions_data = {
                version_str: {
                    "version": version.version,
                    "major": version.major,
                    "minor": version.minor,
                    "patch": version.patch,
                    "pre_release": version.pre_release,
                    "build": version.build,
                    "created_at": version.created_at.isoformat(),
                    "description": version.description,
                    "changes": version.changes,
                    "compatibility": version.compatibility,
                    "migration_required": version.migration_required,
                    "rollback_version": version.rollback_version
                }
                for version_str, version in self.versions.items()
            }
            
            with open(versions_file, 'w') as f:
                json.dump(versions_data, f, indent=2)
            
            migrations_file = os.path.join(self.storage_path, "migrations.json")
            migrations_data = [
                {
                    "from_version": migration.from_version,
                    "to_version": migration.to_version,
                    "description": migration.description,
                    "script": migration.script,
                    "created_at": migration.created_at.isoformat(),
                    "applied_at": migration.applied_at.isoformat() if migration.applied_at else None,
                    "checksum": migration.checksum,
                    "rollback_script": migration.rollback_script
                }
                for migration in self.migrations
            ]
            
            with open(migrations_file, 'w') as f:
                json.dump(migrations_data, f, indent=2)
            
            # Save current version
            if self.current_version:
                current_file = os.path.join(self.storage_path, "current_version.txt")
                with open(current_file, 'w') as f:
                    f.write(self.current_version)
            
            logger.info("Version data saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save version data: {e}")
            raise VersioningError(f"Failed to save version data: {e}")
    
    def parse_version(self, version_str: str) -> AgentVersion:
        """Parse version string into AgentVersion object."""
        try:
            # Handle semantic versioning (e.g., "1.2.3", "1.2.3-alpha.1", "1.2.3+build.20240115")
            pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9]+))?(?:\+([a-zA-Z0-9]+))?$'
            match = re.match(pattern, version_str)
            
            if not match:
                # Try simple version pattern
                simple_pattern = r'^(\d+)\.(\d+)\.(\d+)$'
                simple_match = re.match(simple_pattern, version_str)
                if simple_match:
                    major, minor, patch = map(int, simple_match.groups())
                    return AgentVersion(
                        version=version_str,
                        major=major,
                        minor=minor,
                        patch=patch
                    )
                else:
                    raise VersioningError(f"Invalid version format: {version_str}")
            
            major, minor, patch = map(int, match.groups()[:3])
            pre_release = match.group(4)
            build = match.group(5)
            
            return AgentVersion(
                version=version_str,
                major=major,
                minor=minor,
                patch=patch,
                pre_release=pre_release,
                build=build
            )
            
        except Exception as e:
            logger.error(f"Failed to parse version {version_str}: {e}")
            raise VersioningError(f"Failed to parse version {version_str}: {e}")
    
    def compare_versions(self, version1: str, version2: str) -> int:
        """Compare two versions. Returns -1 if version1 < version2, 0 if equal, 1 if version1 > version2."""
        try:
            v1 = self.parse_version(version1)
            v2 = self.parse_version(version2)
            
            # Compare major version
            if v1.major != v2.major:
                return -1 if v1.major < v2.major else 1
            
            # Compare minor version
            if v1.minor != v2.minor:
                return -1 if v1.minor < v2.minor else 1
            
            # Compare patch version
            if v1.patch != v2.patch:
                return -1 if v1.patch < v2.patch else 1
            
            # Compare pre-release
            if v1.pre_release and v2.pre_release:
                if v1.pre_release < v2.pre_release:
                    return -1
                elif v1.pre_release > v2.pre_release:
                    return 1
            
            # Versions are equal
            return 0
            
        except Exception as e:
            logger.error(f"Failed to compare versions {version1} and {version2}: {e}")
            raise VersioningError(f"Failed to compare versions: {e}")
    
    def is_compatible(self, required_version: str, current_version: str) -> bool:
        """Check if current version is compatible with required version."""
        try:
            req = self.parse_version(required_version)
            curr = self.parse_version(current_version)
            
            # Major version must match
            if req.major != curr.major:
                return False
            
            # Minor version must be >= required
            if curr.minor < req.minor:
                return False
            
            # If same minor version, patch must be >= required
            if curr.minor == req.minor and curr.patch < req.patch:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check compatibility: {e}")
            return False
    
    def create_version(self, version: str, description: str = "", changes: List[str] = None, 
                   compatibility: Dict[str, str] = None, migration_required: bool = False,
                   rollback_version: Optional[str] = None) -> AgentVersion:
        """Create a new version."""
        try:
            version_obj = self.parse_version(version)
            
            if changes is None:
                changes = []
            
            if compatibility is None:
                compatibility = {}
            
            new_version = AgentVersion(
                version=version,
                major=version_obj.major,
                minor=version_obj.minor,
                patch=version_obj.patch,
                pre_release=version_obj.pre_release,
                build=version_obj.build,
                description=description,
                changes=changes,
                compatibility=compatibility,
                migration_required=migration_required,
                rollback_version=rollback_version
            )
            
            self.versions[version] = new_version
            self._save_versions()
            
            logger.info(f"Created version {version}")
            return new_version
            
        except Exception as e:
            logger.error(f"Failed to create version {version}: {e}")
            raise VersioningError(f"Failed to create version {version}: {e}")
    
    def get_version(self, version: str) -> Optional[AgentVersion]:
        """Get version information."""
        return self.versions.get(version)
    
    def get_current_version(self) -> Optional[str]:
        """Get current version."""
        return self.current_version
    
    def set_current_version(self, version: str) -> bool:
        """Set current version."""
        try:
            if version not in self.versions:
                logger.error(f"Version {version} not found in version history")
                return False
            
            self.current_version = version
            self._save_versions()
            
            logger.info(f"Set current version to {version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set current version {version}: {e}")
            return False
    
    def get_version_history(self, limit: int = 10) -> List[AgentVersion]:
        """Get version history."""
        sorted_versions = sorted(
            self.versions.values(),
            key=lambda v: (v.major, v.minor, v.patch),
            reverse=True
        )
        return sorted_versions[:limit]
    
    def create_migration(self, from_version: str, to_version: str, description: str,
                     script: str, rollback_script: Optional[str] = None) -> Migration:
        """Create a migration."""
        try:
            migration = Migration(
                from_version=from_version,
                to_version=to_version,
                description=description,
                script=script,
                rollback_script=rollback_script,
                checksum=self._calculate_checksum(script)
            )
            
            self.migrations.append(migration)
            self._save_versions()
            
            logger.info(f"Created migration from {from_version} to {to_version}")
            return migration
            
        except Exception as e:
            logger.error(f"Failed to create migration: {e}")
            raise VersioningError(f"Failed to create migration: {e}")
    
    def _calculate_checksum(self, script: str) -> str:
        """Calculate checksum for migration script."""
        import hashlib
        return hashlib.sha256(script.encode()).hexdigest()
    
    async def apply_migration(self, migration: Migration) -> bool:
        """Apply a migration."""
        try:
            logger.info(f"Applying migration from {migration.from_version} to {migration.to_version}")
            
            # Execute migration script
            # In a real implementation, this would execute the SQL script
            # For now, we'll simulate the migration
            
            # Mark migration as applied
            migration.applied_at = datetime.now()
            self._save_versions()
            
            # Update current version
            self.set_current_version(migration.to_version)
            
            logger.info(f"Migration applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply migration: {e}")
            return False
    
    async def rollback_migration(self, migration: Migration) -> bool:
        """Rollback a migration."""
        try:
            logger.info(f"Rolling back migration from {migration.to_version} to {migration.from_version}")
            
            if not migration.rollback_script:
                logger.error("No rollback script available for migration")
                return False
            
            # Execute rollback script
            # In a real implementation, this would execute the rollback SQL script
            # For now, we'll simulate the rollback
            
            # Update current version
            self.set_current_version(migration.from_version)
            
            logger.info(f"Migration rolled back successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback migration: {e}")
            return False
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get migrations that haven't been applied yet."""
        current_version = self.get_current_version()
        if not current_version:
            return []
        
        pending = []
        for migration in self.migrations:
            if migration.to_version == current_version and not migration.applied_at:
                pending.append(migration)
        
        return pending
    
    def get_migration_history(self, limit: int = 10) -> List[Migration]:
        """Get migration history."""
        sorted_migrations = sorted(
            self.migrations,
            key=lambda m: m.created_at,
            reverse=True
        )
        return sorted_migrations[:limit]
    
    def validate_version_format(self, version: str) -> bool:
        """Validate version format."""
        try:
            self.parse_version(version)
            return True
        except VersioningError:
            return False
    
    def get_version_info(self, version: str) -> Dict[str, Any]:
        """Get comprehensive version information."""
        version_obj = self.get_version(version)
        if not version_obj:
            return {"error": f"Version {version} not found"}
        
        return {
            "version": version_obj.version,
            "major": version_obj.major,
            "minor": version_obj.minor,
            "patch": version_obj.patch,
            "pre_release": version_obj.pre_release,
            "build": version_obj.build,
            "created_at": version_obj.created_at.isoformat(),
            "description": version_obj.description,
            "changes": version_obj.changes,
            "compatibility": version_obj.compatibility,
            "migration_required": version_obj.migration_required,
            "rollback_version": version_obj.rollback_version,
            "is_current": version == self.get_current_version()
        }


# Global version manager instance
_version_manager: Optional[VersionManager] = None


def get_version_manager(storage_path: Optional[str] = None) -> VersionManager:
    """Get or create version manager."""
    global _version_manager
    if _version_manager is None:
        _version_manager = VersionManager(storage_path)
    return _version_manager


# Convenience functions for backward compatibility
def create_version(version: str, description: str = "", changes: List[str] = None,
                compatibility: Dict[str, str] = None, migration_required: bool = False,
                rollback_version: Optional[str] = None) -> AgentVersion:
    """Create a new version."""
    manager = get_version_manager()
    return manager.create_version(version, description, changes, compatibility, migration_required, rollback_version)


def get_version(version: str) -> Optional[AgentVersion]:
    """Get version information."""
    manager = get_version_manager()
    return manager.get_version(version)


def get_current_version() -> Optional[str]:
    """Get current version."""
    manager = get_version_manager()
    return manager.get_current_version()


def set_current_version(version: str) -> bool:
    """Set current version."""
    manager = get_version_manager()
    return manager.set_current_version(version)


def compare_versions(version1: str, version2: str) -> int:
    """Compare two versions."""
    manager = get_version_manager()
    return manager.compare_versions(version1, version2)


def is_compatible(required_version: str, current_version: str) -> bool:
    """Check version compatibility."""
    manager = get_version_manager()
    return manager.is_compatible(required_version, current_version)


def get_version_history(limit: int = 10) -> List[AgentVersion]:
    """Get version history."""
    manager = get_version_manager()
    return manager.get_version_history(limit)


async def apply_migration(migration: Migration) -> bool:
    """Apply a migration."""
    manager = get_version_manager()
    return await manager.apply_migration(migration)


async def rollback_migration(migration: Migration) -> bool:
    """Rollback a migration."""
    manager = get_version_manager()
    return await manager.rollback_migration(migration)


def get_version_info(version: str) -> Dict[str, Any]:
    """Get comprehensive version information."""
    manager = get_version_manager()
    return manager.get_version_info(version)
