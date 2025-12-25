"""
S.W.A.R.M. Phase 2: Advanced MLOps - Feature Versioning System
Production-ready feature versioning and lineage tracking
"""

import asyncio
import hashlib
import json
import logging
import os
import pickle
import shutil
import sqlite3
import time
import uuid
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import numpy as np
import pandas as pd
import yaml

logger = logging.getLogger("raptorflow.feature_versioning")


class VersionStatus(Enum):
    """Feature version status."""

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class StorageBackend(Enum):
    """Storage backend types."""

    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"
    AZURE_BLOB = "azure_blob"


@dataclass
class FeatureVersion:
    """Feature version metadata."""

    version_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    feature_name: str = ""
    version_number: str = "1.0.0"
    status: VersionStatus = VersionStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    description: str = ""
    data_shape: Tuple[int, ...] = field(default_factory=tuple)
    data_hash: str = ""
    schema_version: str = "1.0"
    dependencies: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    file_path: str = ""
    size_bytes: int = 0
    checksum: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version_id": self.version_id,
            "feature_name": self.feature_name,
            "version_number": self.version_number,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "description": self.description,
            "data_shape": self.data_shape,
            "data_hash": self.data_hash,
            "schema_version": self.schema_version,
            "dependencies": self.dependencies,
            "tags": list(self.tags),
            "metadata": self.metadata,
            "file_path": self.file_path,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
        }


@dataclass
class FeatureLineage:
    """Feature lineage information."""

    lineage_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    feature_name: str = ""
    source_versions: List[str] = field(default_factory=list)
    target_version: str = ""
    transformation_type: str = ""
    transformation_params: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "lineage_id": self.lineage_id,
            "feature_name": self.feature_name,
            "source_versions": self.source_versions,
            "target_version": self.target_version,
            "transformation_type": self.transformation_type,
            "transformation_params": self.transformation_params,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "description": self.description,
        }


@dataclass
class VersioningConfig:
    """Feature versioning configuration."""

    storage_backend: StorageBackend = StorageBackend.LOCAL
    storage_path: str = "feature_store"
    max_versions_per_feature: int = 10
    auto_cleanup: bool = True
    compression: bool = True
    encryption: bool = False
    backup_enabled: bool = True
    backup_retention_days: int = 30

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "storage_backend": self.storage_backend.value,
            "storage_path": self.storage_path,
            "max_versions_per_feature": self.max_versions_per_feature,
            "auto_cleanup": self.auto_cleanup,
            "compression": self.compression,
            "encryption": self.encryption,
            "backup_enabled": self.backup_enabled,
            "backup_retention_days": self.backup_retention_days,
        }


class StorageManager(ABC):
    """Abstract storage manager for feature versions."""

    @abstractmethod
    def save_feature(self, data: pd.DataFrame, version: FeatureVersion) -> str:
        """Save feature data to storage."""
        pass

    @abstractmethod
    def load_feature(self, version: FeatureVersion) -> pd.DataFrame:
        """Load feature data from storage."""
        pass

    @abstractmethod
    def delete_feature(self, version: FeatureVersion) -> bool:
        """Delete feature data from storage."""
        pass

    @abstractmethod
    def list_features(self) -> List[str]:
        """List all available features."""
        pass

    @abstractmethod
    def list_versions(self, feature_name: str) -> List[str]:
        """List all versions for a feature."""
        pass


class LocalStorageManager(StorageManager):
    """Local file system storage manager."""

    def __init__(self, base_path: str = "feature_store"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)

        # Create subdirectories
        (self.base_path / "features").mkdir(exist_ok=True)
        (self.base_path / "metadata").mkdir(exist_ok=True)
        (self.base_path / "lineage").mkdir(exist_ok=True)
        (self.base_path / "backups").mkdir(exist_ok=True)

    def save_feature(self, data: pd.DataFrame, version: FeatureVersion) -> str:
        """Save feature data to local storage."""
        feature_dir = self.base_path / "features" / version.feature_name
        feature_dir.mkdir(exist_ok=True)

        # Save data
        file_path = feature_dir / f"{version.version_number}.parquet"
        data.to_parquet(file_path, index=False)

        # Calculate checksum
        version.checksum = self._calculate_checksum(file_path)
        version.file_path = str(file_path)
        version.size_bytes = file_path.stat().st_size

        # Save metadata
        metadata_path = self.base_path / "metadata" / f"{version.version_id}.json"
        with open(metadata_path, "w") as f:
            json.dump(version.to_dict(), f, indent=2, default=str)

        return str(file_path)

    def load_feature(self, version: FeatureVersion) -> pd.DataFrame:
        """Load feature data from local storage."""
        if not version.file_path:
            raise ValueError("No file path specified for version")

        file_path = Path(version.file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Feature file not found: {file_path}")

        # Verify checksum
        current_checksum = self._calculate_checksum(file_path)
        if current_checksum != version.checksum:
            logger.warning(
                f"Checksum mismatch for {version.feature_name} version {version.version_number}"
            )

        return pd.read_parquet(file_path)

    def delete_feature(self, version: FeatureVersion) -> bool:
        """Delete feature data from local storage."""
        try:
            # Delete data file
            if version.file_path:
                file_path = Path(version.file_path)
                if file_path.exists():
                    file_path.unlink()

            # Delete metadata
            metadata_path = self.base_path / "metadata" / f"{version.version_id}.json"
            if metadata_path.exists():
                metadata_path.unlink()

            return True
        except Exception as e:
            logger.error(f"Failed to delete feature version: {str(e)}")
            return False

    def list_features(self) -> List[str]:
        """List all available features."""
        features_dir = self.base_path / "features"
        if not features_dir.exists():
            return []

        return [d.name for d in features_dir.iterdir() if d.is_dir()]

    def list_versions(self, feature_name: str) -> List[str]:
        """List all versions for a feature."""
        feature_dir = self.base_path / "features" / feature_name
        if not feature_dir.exists():
            return []

        versions = []
        for file_path in feature_dir.glob("*.parquet"):
            # Extract version number from filename
            version_num = file_path.stem
            versions.append(version_num)

        return sorted(versions)

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()


class FeatureVersioningSystem:
    """Main feature versioning system."""

    def __init__(self, config: Optional[VersioningConfig] = None):
        self.config = config or VersioningConfig()
        self.storage_manager = self._create_storage_manager()
        self.versions: Dict[str, FeatureVersion] = {}
        self.lineage: Dict[str, FeatureLineage] = {}
        self.active_versions: Dict[str, str] = {}  # feature_name -> version_id

        # Initialize database for metadata
        self.db_path = Path(self.config.storage_path) / "feature_versioning.db"
        self._init_database()

    def _create_storage_manager(self) -> StorageManager:
        """Create storage manager based on configuration."""
        if self.config.storage_backend == StorageBackend.LOCAL:
            return LocalStorageManager(self.config.storage_path)
        else:
            raise NotImplementedError(
                f"Storage backend {self.config.storage_backend} not implemented"
            )

    def _init_database(self):
        """Initialize SQLite database for metadata."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS feature_versions (
                    version_id TEXT PRIMARY KEY,
                    feature_name TEXT NOT NULL,
                    version_number TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    created_by TEXT,
                    description TEXT,
                    data_shape TEXT,
                    data_hash TEXT,
                    schema_version TEXT,
                    dependencies TEXT,
                    tags TEXT,
                    metadata TEXT,
                    file_path TEXT,
                    size_bytes INTEGER,
                    checksum TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS feature_lineage (
                    lineage_id TEXT PRIMARY KEY,
                    feature_name TEXT NOT NULL,
                    source_versions TEXT,
                    target_version TEXT NOT NULL,
                    transformation_type TEXT,
                    transformation_params TEXT,
                    created_at TEXT NOT NULL,
                    created_by TEXT,
                    description TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS active_versions (
                    feature_name TEXT PRIMARY KEY,
                    version_id TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """
            )

    def create_version(
        self,
        feature_name: str,
        data: pd.DataFrame,
        version_number: Optional[str] = None,
        description: str = "",
        created_by: str = "",
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FeatureVersion:
        """Create a new feature version."""
        # Generate version number if not provided
        if version_number is None:
            version_number = self._generate_version_number(feature_name)

        # Create version object
        version = FeatureVersion(
            feature_name=feature_name,
            version_number=version_number,
            description=description,
            created_by=created_by,
            data_shape=data.shape,
            data_hash=self._calculate_data_hash(data),
            tags=tags or set(),
            metadata=metadata or {},
        )

        # Save data to storage
        self.storage_manager.save_feature(data, version)

        # Save to database
        self._save_version_to_db(version)

        # Update in-memory cache
        self.versions[version.version_id] = version

        logger.info(f"Created version {version_number} for feature {feature_name}")
        return version

    def load_version(self, version_id: str) -> Tuple[pd.DataFrame, FeatureVersion]:
        """Load a specific feature version."""
        if version_id not in self.versions:
            # Load from database
            version = self._load_version_from_db(version_id)
            if version is None:
                raise ValueError(f"Version {version_id} not found")
            self.versions[version_id] = version
        else:
            version = self.versions[version_id]

        # Load data from storage
        data = self.storage_manager.load_feature(version)

        return data, version

    def get_active_version(
        self, feature_name: str
    ) -> Optional[Tuple[pd.DataFrame, FeatureVersion]]:
        """Get the active version of a feature."""
        if feature_name not in self.active_versions:
            return None

        version_id = self.active_versions[feature_name]
        return self.load_version(version_id)

    def set_active_version(self, version_id: str):
        """Set a version as active for its feature."""
        if version_id not in self.versions:
            version = self._load_version_from_db(version_id)
            if version is None:
                raise ValueError(f"Version {version_id} not found")
            self.versions[version_id] = version
        else:
            version = self.versions[version_id]

        # Update database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO active_versions (feature_name, version_id, updated_at)
                VALUES (?, ?, ?)
            """,
                (version.feature_name, version_id, datetime.now().isoformat()),
            )

        # Update in-memory cache
        self.active_versions[version.feature_name] = version_id

        logger.info(
            f"Set version {version.version_number} as active for feature {version.feature_name}"
        )

    def list_versions(self, feature_name: str) -> List[FeatureVersion]:
        """List all versions for a feature."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM feature_versions WHERE feature_name = ? ORDER BY created_at DESC
            """,
                (feature_name,),
            )

            versions = []
            for row in cursor.fetchall():
                version = self._row_to_version(row)
                versions.append(version)
                self.versions[version.version_id] = version

            return versions

    def create_lineage(
        self,
        feature_name: str,
        source_versions: List[str],
        target_version: str,
        transformation_type: str,
        transformation_params: Dict[str, Any],
        created_by: str = "",
        description: str = "",
    ) -> FeatureLineage:
        """Create feature lineage record."""
        lineage = FeatureLineage(
            feature_name=feature_name,
            source_versions=source_versions,
            target_version=target_version,
            transformation_type=transformation_type,
            transformation_params=transformation_params,
            created_by=created_by,
            description=description,
        )

        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO feature_lineage (
                    lineage_id, feature_name, source_versions, target_version,
                    transformation_type, transformation_params, created_at, created_by, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    lineage.lineage_id,
                    lineage.feature_name,
                    json.dumps(lineage.source_versions),
                    lineage.target_version,
                    lineage.transformation_type,
                    json.dumps(lineage.transformation_params),
                    lineage.created_at.isoformat(),
                    lineage.created_by,
                    lineage.description,
                ),
            )

        # Update in-memory cache
        self.lineage[lineage.lineage_id] = lineage

        logger.info(f"Created lineage for feature {feature_name}")
        return lineage

    def get_lineage(self, feature_name: str) -> List[FeatureLineage]:
        """Get lineage for a feature."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT * FROM feature_lineage WHERE feature_name = ? ORDER BY created_at DESC
            """,
                (feature_name,),
            )

            lineage_records = []
            for row in cursor.fetchall():
                lineage = self._row_to_lineage(row)
                lineage_records.append(lineage)
                self.lineage[lineage.lineage_id] = lineage

            return lineage_records

    def compare_versions(self, version_id_1: str, version_id_2: str) -> Dict[str, Any]:
        """Compare two versions of a feature."""
        data_1, version_1 = self.load_version(version_id_1)
        data_2, version_2 = self.load_version(version_id_2)

        comparison = {
            "version_1": {
                "version_id": version_1.version_id,
                "version_number": version_1.version_number,
                "created_at": version_1.created_at.isoformat(),
                "data_shape": version_1.data_shape,
                "data_hash": version_1.data_hash,
            },
            "version_2": {
                "version_id": version_2.version_id,
                "version_number": version_2.version_number,
                "created_at": version_2.created_at.isoformat(),
                "data_shape": version_2.data_shape,
                "data_hash": version_2.data_hash,
            },
            "differences": {
                "shape_changed": version_1.data_shape != version_2.data_shape,
                "hash_changed": version_1.data_hash != version_2.data_hash,
                "schema_changed": version_1.schema_version != version_2.schema_version,
            },
        }

        # Statistical comparison if data is numerical
        if len(data_1) > 0 and len(data_2) > 0:
            try:
                # Compare summary statistics
                stats_1 = data_1.describe()
                stats_2 = data_2.describe()

                comparison["statistics"] = {
                    "version_1": stats_1.to_dict(),
                    "version_2": stats_2.to_dict(),
                }
            except Exception as e:
                logger.warning(f"Statistical comparison failed: {str(e)}")

        return comparison

    def cleanup_old_versions(self, feature_name: Optional[str] = None) -> int:
        """Clean up old versions beyond retention limit."""
        cleaned_count = 0

        features_to_clean = (
            [feature_name] if feature_name else self.storage_manager.list_features()
        )

        for feat_name in features_to_clean:
            versions = self.list_versions(feat_name)

            # Keep only the most recent versions
            if len(versions) > self.config.max_versions_per_feature:
                versions_to_remove = versions[self.config.max_versions_per_feature :]

                for version in versions_to_remove:
                    if version.status != VersionStatus.ACTIVE:
                        # Delete from storage
                        self.storage_manager.delete_feature(version)

                        # Delete from database
                        with sqlite3.connect(self.db_path) as conn:
                            conn.execute(
                                "DELETE FROM feature_versions WHERE version_id = ?",
                                (version.version_id,),
                            )

                        # Remove from cache
                        if version.version_id in self.versions:
                            del self.versions[version.version_id]

                        cleaned_count += 1
                        logger.info(
                            f"Cleaned up version {version.version_number} of feature {feat_name}"
                        )

        return cleaned_count

    def _generate_version_number(self, feature_name: str) -> str:
        """Generate next version number for a feature."""
        versions = self.list_versions(feature_name)

        if not versions:
            return "1.0.0"

        # Parse existing versions and find the highest
        max_version = max(
            versions, key=lambda v: tuple(map(int, v.version_number.split(".")))
        )

        # Increment patch version
        major, minor, patch = map(int, max_version.version_number.split("."))
        patch += 1

        return f"{major}.{minor}.{patch}"

    def _calculate_data_hash(self, data: pd.DataFrame) -> str:
        """Calculate hash of feature data."""
        # Use a combination of shape and sample data for hashing
        shape_hash = hashlib.md5(str(data.shape).encode()).hexdigest()

        # Sample some data for content hash
        if len(data) > 0:
            sample_data = data.head(100).to_string()
            content_hash = hashlib.md5(sample_data.encode()).hexdigest()
        else:
            content_hash = ""

        combined = f"{shape_hash}_{content_hash}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _save_version_to_db(self, version: FeatureVersion):
        """Save version to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO feature_versions (
                    version_id, feature_name, version_number, status, created_at, created_by,
                    description, data_shape, data_hash, schema_version, dependencies,
                    tags, metadata, file_path, size_bytes, checksum
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    version.version_id,
                    version.feature_name,
                    version.version_number,
                    version.status.value,
                    version.created_at.isoformat(),
                    version.created_by,
                    version.description,
                    json.dumps(version.data_shape),
                    version.data_hash,
                    version.schema_version,
                    json.dumps(version.dependencies),
                    json.dumps(list(version.tags)),
                    json.dumps(version.metadata),
                    version.file_path,
                    version.size_bytes,
                    version.checksum,
                ),
            )

    def _load_version_from_db(self, version_id: str) -> Optional[FeatureVersion]:
        """Load version from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM feature_versions WHERE version_id = ?", (version_id,)
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_version(row)

    def _row_to_version(self, row) -> FeatureVersion:
        """Convert database row to FeatureVersion."""
        return FeatureVersion(
            version_id=row[0],
            feature_name=row[1],
            version_number=row[2],
            status=VersionStatus(row[3]),
            created_at=datetime.fromisoformat(row[4]),
            created_by=row[5] or "",
            description=row[6] or "",
            data_shape=tuple(json.loads(row[7] or "[]")),
            data_hash=row[8] or "",
            schema_version=row[9] or "1.0",
            dependencies=json.loads(row[10] or "[]"),
            tags=set(json.loads(row[11] or "[]")),
            metadata=json.loads(row[12] or "{}"),
            file_path=row[13] or "",
            size_bytes=row[14] or 0,
            checksum=row[15] or "",
        )

    def _row_to_lineage(self, row) -> FeatureLineage:
        """Convert database row to FeatureLineage."""
        return FeatureLineage(
            lineage_id=row[0],
            feature_name=row[1],
            source_versions=json.loads(row[2] or "[]"),
            target_version=row[3],
            transformation_type=row[4] or "",
            transformation_params=json.loads(row[5] or "{}"),
            created_at=datetime.fromisoformat(row[6]),
            created_by=row[7] or "",
            description=row[8] or "",
        )


# Example usage
async def demonstrate_feature_versioning():
    """Demonstrate feature versioning system."""
    print("Demonstrating S.W.A.R.M. Phase 2 Advanced MLOps - Feature Versioning...")

    # Create versioning system
    config = VersioningConfig(
        storage_path="feature_store_demo", max_versions_per_feature=5
    )
    versioning_system = FeatureVersioningSystem(config)

    # Create sample feature data
    np.random.seed(42)
    feature_data_v1 = pd.DataFrame(
        {
            "customer_age": np.random.randint(18, 80, 1000),
            "income": np.random.normal(50000, 15000, 1000),
            "spending_score": np.random.uniform(1, 100, 1000),
        }
    )

    feature_data_v2 = pd.DataFrame(
        {
            "customer_age": np.random.randint(18, 80, 1000),
            "income": np.random.normal(52000, 16000, 1000),  # Slight drift
            "spending_score": np.random.uniform(1, 100, 1000),
            "credit_score": np.random.randint(300, 850, 1000),  # New feature
        }
    )

    # Create versions
    print("Creating feature versions...")
    version_1 = versioning_system.create_version(
        feature_name="customer_features",
        data=feature_data_v1,
        version_number="1.0.0",
        description="Initial customer features",
        created_by="data_engineer",
        tags={"production", "v1"},
    )

    version_2 = versioning_system.create_version(
        feature_name="customer_features",
        data=feature_data_v2,
        version_number="1.1.0",
        description="Added credit score feature",
        created_by="data_engineer",
        tags={"production", "enhanced"},
    )

    print(f"Created version {version_1.version_number}")
    print(f"Created version {version_2.version_number}")

    # Set active version
    versioning_system.set_active_version(version_2.version_id)
    print(f"Set version {version_2.version_number} as active")

    # Load active version
    active_data, active_version = versioning_system.get_active_version(
        "customer_features"
    )
    print(f"Loaded active version: {active_version.version_number}")
    print(f"Data shape: {active_data.shape}")

    # Create lineage
    lineage = versioning_system.create_lineage(
        feature_name="customer_features",
        source_versions=[version_1.version_id],
        target_version=version_2.version_id,
        transformation_type="feature_addition",
        transformation_params={"added_features": ["credit_score"]},
        created_by="data_engineer",
        description="Added credit score to customer features",
    )

    print(f"Created lineage record: {lineage.lineage_id}")

    # Compare versions
    comparison = versioning_system.compare_versions(
        version_1.version_id, version_2.version_id
    )
    print(f"\nVersion Comparison:")
    print(f"  Shape changed: {comparison['differences']['shape_changed']}")
    print(f"  Hash changed: {comparison['differences']['hash_changed']}")
    print(f"  Schema changed: {comparison['differences']['schema_changed']}")

    # List all versions
    versions = versioning_system.list_versions("customer_features")
    print(f"\nAll versions for customer_features:")
    for version in versions:
        status = (
            "ACTIVE"
            if version.version_id
            == versioning_system.active_versions.get("customer_features")
            else version.status.value
        )
        print(f"  {version.version_number} - {status} - {version.description}")

    # Get lineage
    lineage_records = versioning_system.get_lineage("customer_features")
    print(f"\nLineage for customer_features:")
    for record in lineage_records:
        print(f"  {record.transformation_type}: {record.description}")

    print("\nFeature Versioning demonstration complete!")


if __name__ == "__main__":
    asyncio.run(demonstrate_feature_versioning())
