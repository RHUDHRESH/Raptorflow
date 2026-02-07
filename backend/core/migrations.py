import asyncio
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("raptorflow.migrations")


class Migration:
    """Represents a database migration."""

    def __init__(
        self,
        version: str,
        description: str,
        sql_up: str,
        sql_down: str,
        dependencies: Optional[List[str]] = None,
    ):
        self.version = version
        self.description = description
        self.sql_up = sql_up
        self.sql_down = sql_down
        self.dependencies = dependencies or []
        self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate checksum of migration content."""
        content = f"{self.version}{self.description}{self.sql_up}{self.sql_down}"
        return hashlib.sha256(content.encode()).hexdigest()


class MigrationManager:
    """
    Production-grade database migration system with rollback support.
    """

    def __init__(self):
        self.migrations: Dict[str, Migration] = {}
        self.applied_migrations: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    def register_migration(self, migration: Migration):
        """Register a migration."""
        self.migrations[migration.version] = migration
        logger.debug(
            f"Registered migration {migration.version}: {migration.description}"
        )

    async def initialize_schema(self):
        """Initialize migration tracking schema."""
        from db import get_db_connection

        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                # Create migrations table if it doesn't exist
                await cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version VARCHAR(50) PRIMARY KEY,
                        description TEXT NOT NULL,
                        checksum VARCHAR(64) NOT NULL,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        execution_time_ms INTEGER
                    )
                """
                )

                # Load applied migrations
                await cur.execute(
                    """
                    SELECT version, description, checksum, applied_at, execution_time_ms
                    FROM schema_migrations
                    ORDER BY version
                """
                )

                rows = await cur.fetchall()
                for row in rows:
                    self.applied_migrations[row[0]] = {
                        "description": row[1],
                        "checksum": row[2],
                        "applied_at": row[3],
                        "execution_time_ms": row[4],
                    }

                logger.info(f"Loaded {len(self.applied_migrations)} applied migrations")

    async def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations."""
        async with self._lock:
            pending = []

            for version, migration in self.migrations.items():
                if version not in self.applied_migrations:
                    # Check dependencies
                    if all(
                        dep in self.applied_migrations for dep in migration.dependencies
                    ):
                        pending.append(migration)
                    else:
                        missing_deps = [
                            dep
                            for dep in migration.dependencies
                            if dep not in self.applied_migrations
                        ]
                        logger.warning(
                            f"Skipping migration {version} due to missing dependencies: {missing_deps}"
                        )

            # Sort by version
            pending.sort(key=lambda m: m.version)
            return pending

    async def migrate_up(self, target_version: Optional[str] = None) -> Dict[str, Any]:
        """Apply pending migrations up to target version."""
        from db import get_db_connection

        start_time = datetime.utcnow()
        applied_migrations = []
        errors = []

        try:
            await self.initialize_schema()
            pending = await self.get_pending_migrations()

            if target_version:
                pending = [m for m in pending if m.version <= target_version]

            if not pending:
                logger.info("No pending migrations to apply")
                return {
                    "success": True,
                    "applied_count": 0,
                    "applied_migrations": [],
                    "errors": [],
                    "execution_time_ms": 0,
                }

            async with get_db_connection() as conn:
                async with conn.cursor() as cur:
                    for migration in pending:
                        try:
                            migration_start = datetime.utcnow()

                            # Apply migration
                            await cur.execute(migration.sql_up)

                            # Record migration
                            execution_time = int(
                                (datetime.utcnow() - migration_start).total_seconds()
                                * 1000
                            )

                            await cur.execute(
                                """
                                INSERT INTO schema_migrations
                                (version, description, checksum, execution_time_ms)
                                VALUES (%s, %s, %s, %s)
                            """,
                                (
                                    migration.version,
                                    migration.description,
                                    migration.checksum,
                                    execution_time,
                                ),
                            )

                            # Update local state
                            self.applied_migrations[migration.version] = {
                                "description": migration.description,
                                "checksum": migration.checksum,
                                "applied_at": datetime.utcnow(),
                                "execution_time_ms": execution_time,
                            }

                            applied_migrations.append(
                                {
                                    "version": migration.version,
                                    "description": migration.description,
                                    "execution_time_ms": execution_time,
                                }
                            )

                            logger.info(
                                f"Applied migration {migration.version}: {migration.description}"
                            )

                        except Exception as e:
                            error_msg = f"Failed to apply migration {migration.version}: {str(e)}"
                            logger.error(error_msg)
                            errors.append(error_msg)
                            break  # Stop on first error

            total_execution_time = int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )

            return {
                "success": len(errors) == 0,
                "applied_count": len(applied_migrations),
                "applied_migrations": applied_migrations,
                "errors": errors,
                "execution_time_ms": total_execution_time,
            }

        except Exception as e:
            error_msg = f"Migration failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "applied_count": len(applied_migrations),
                "applied_migrations": applied_migrations,
                "errors": [error_msg],
                "execution_time_ms": int(
                    (datetime.utcnow() - start_time).total_seconds() * 1000
                ),
            }

    async def migrate_down(self, target_version: str) -> Dict[str, Any]:
        """Rollback migrations down to target version."""
        from db import get_db_connection

        start_time = datetime.utcnow()
        rolled_back_migrations = []
        errors = []

        try:
            await self.initialize_schema()

            # Get migrations to rollback (in reverse order)
            to_rollback = []
            for version in sorted(self.applied_migrations.keys(), reverse=True):
                if version > target_version and version in self.migrations:
                    to_rollback.append(self.migrations[version])

            if not to_rollback:
                logger.info("No migrations to rollback")
                return {
                    "success": True,
                    "rolled_back_count": 0,
                    "rolled_back_migrations": [],
                    "errors": [],
                    "execution_time_ms": 0,
                }

            async with get_db_connection() as conn:
                async with conn.cursor() as cur:
                    for migration in to_rollback:
                        try:
                            migration_start = datetime.utcnow()

                            # Rollback migration
                            await cur.execute(migration.sql_down)

                            # Remove migration record
                            await cur.execute(
                                """
                                DELETE FROM schema_migrations WHERE version = %s
                            """,
                                (migration.version,),
                            )

                            # Update local state
                            del self.applied_migrations[migration.version]

                            execution_time = int(
                                (datetime.utcnow() - migration_start).total_seconds()
                                * 1000
                            )

                            rolled_back_migrations.append(
                                {
                                    "version": migration.version,
                                    "description": migration.description,
                                    "execution_time_ms": execution_time,
                                }
                            )

                            logger.info(
                                f"Rolled back migration {migration.version}: {migration.description}"
                            )

                        except Exception as e:
                            error_msg = f"Failed to rollback migration {migration.version}: {str(e)}"
                            logger.error(error_msg)
                            errors.append(error_msg)
                            break  # Stop on first error

            total_execution_time = int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )

            return {
                "success": len(errors) == 0,
                "rolled_back_count": len(rolled_back_migrations),
                "rolled_back_migrations": rolled_back_migrations,
                "errors": errors,
                "execution_time_ms": total_execution_time,
            }

        except Exception as e:
            error_msg = f"Rollback failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "rolled_back_count": len(rolled_back_migrations),
                "rolled_back_migrations": rolled_back_migrations,
                "errors": [error_msg],
                "execution_time_ms": int(
                    (datetime.utcnow() - start_time).total_seconds() * 1000
                ),
            }

    async def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        await self.initialize_schema()

        pending = await self.get_pending_migrations()

        return {
            "total_migrations": len(self.migrations),
            "applied_migrations": len(self.applied_migrations),
            "pending_migrations": len(pending),
            "current_version": (
                max(self.applied_migrations.keys()) if self.applied_migrations else None
            ),
            "latest_version": max(self.migrations.keys()) if self.migrations else None,
            "applied_list": [
                {
                    "version": version,
                    "description": info["description"],
                    "applied_at": info["applied_at"].isoformat(),
                    "execution_time_ms": info["execution_time_ms"],
                }
                for version, info in sorted(self.applied_migrations.items())
            ],
            "pending_list": [
                {
                    "version": m.version,
                    "description": m.description,
                    "dependencies": m.dependencies,
                }
                for m in pending
            ],
        }

    async def verify_migration_integrity(self) -> Dict[str, Any]:
        """Verify integrity of applied migrations."""
        await self.initialize_schema()

        integrity_issues = []

        for version, info in self.applied_migrations.items():
            if version in self.migrations:
                migration = self.migrations[version]
                if migration.checksum != info["checksum"]:
                    integrity_issues.append(
                        {
                            "version": version,
                            "issue": "Checksum mismatch",
                            "expected": migration.checksum,
                            "actual": info["checksum"],
                        }
                    )
            else:
                integrity_issues.append(
                    {"version": version, "issue": "Migration definition missing"}
                )

        return {
            "integrity_valid": len(integrity_issues) == 0,
            "issues": integrity_issues,
            "verified_migrations": len(self.applied_migrations) - len(integrity_issues),
        }


# Global migration manager
_migration_manager: Optional[MigrationManager] = None


def get_migration_manager() -> MigrationManager:
    """Get the global migration manager instance."""
    global _migration_manager
    if _migration_manager is None:
        _migration_manager = MigrationManager()
    return _migration_manager


def register_migrations():
    """Register all database migrations."""
    manager = get_migration_manager()

    # Initial schema migration
    manager.register_migration(
        Migration(
            version="001_initial_schema",
            description="Create initial database schema",
            sql_up="""
            -- Create workspaces table
            CREATE TABLE IF NOT EXISTS workspaces (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                description TEXT,
                tenant_id VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Create campaigns table
            CREATE TABLE IF NOT EXISTS campaigns (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                title VARCHAR(255) NOT NULL,
                objective TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'draft',
                tenant_id VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                arc_data JSONB,
                kpi_targets JSONB
            );

            -- Create moves table
            CREATE TABLE IF NOT EXISTS moves (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                priority INTEGER DEFAULT 3,
                move_type VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tool_requirements JSONB,
                execution_result JSONB
            );

            -- Create assets table
            CREATE TABLE IF NOT EXISTS assets (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                content TEXT NOT NULL,
                asset_type VARCHAR(50) NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE
            );

            -- Create indexes
            CREATE INDEX IF NOT EXISTS idx_campaigns_tenant_id ON campaigns(tenant_id);
            CREATE INDEX IF NOT EXISTS idx_moves_campaign_id ON moves(campaign_id);
            CREATE INDEX IF NOT EXISTS idx_assets_workspace_id ON assets(workspace_id);
            CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
            CREATE INDEX IF NOT EXISTS idx_moves_status ON moves(status);
        """,
            sql_down="""
            DROP TABLE IF EXISTS assets;
            DROP TABLE IF EXISTS moves;
            DROP TABLE IF EXISTS campaigns;
            DROP TABLE IF EXISTS workspaces;
        """,
        )
    )

    # Memory and vector search migration
    manager.register_migration(
        Migration(
            version="002_memory_schema",
            description="Add memory and vector search tables",
            sql_up="""
            -- Create memories table
            CREATE TABLE IF NOT EXISTS memories (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                content TEXT NOT NULL,
                embedding vector(1536),
                memory_type VARCHAR(50) DEFAULT 'semantic',
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE
            );

            -- Create vector index for similarity search
            CREATE INDEX IF NOT EXISTS idx_memories_embedding ON memories
            USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

            -- Create memory search index
            CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
            CREATE INDEX IF NOT EXISTS idx_memories_workspace ON memories(workspace_id);
        """,
            sql_down="""
            DROP TABLE IF EXISTS memories;
        """,
            dependencies=["001_initial_schema"],
        )
    )

    # Foundation and brand kit migration
    manager.register_migration(
        Migration(
            version="003_foundation_schema",
            description="Add foundation and brand kit tables",
            sql_up="""
            -- Create foundation_state table
            CREATE TABLE IF NOT EXISTS foundation_state (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
                state_data JSONB NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(workspace_id)
            );

            -- Create brand_kits table
            CREATE TABLE IF NOT EXISTS brand_kits (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
                brand_data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Create positioning table
            CREATE TABLE IF NOT EXISTS positioning (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
                positioning_data JSONB NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
            sql_down="""
            DROP TABLE IF EXISTS positioning;
            DROP TABLE IF EXISTS brand_kits;
            DROP TABLE IF EXISTS foundation_state;
        """,
            dependencies=["001_initial_schema"],
        )
    )

    # Audit and logging migration
    manager.register_migration(
        Migration(
            version="004_audit_schema",
            description="Add audit and logging tables",
            sql_up="""
            -- Create audit_logs table
            CREATE TABLE IF NOT EXISTS audit_logs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                action VARCHAR(100) NOT NULL,
                resource_type VARCHAR(50) NOT NULL,
                resource_id VARCHAR(255),
                user_id VARCHAR(255),
                tenant_id VARCHAR(255),
                old_values JSONB,
                new_values JSONB,
                ip_address INET,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Create indexes for audit logs
            CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant ON audit_logs(tenant_id);
            CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
            CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
            CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at);
        """,
            sql_down="""
            DROP TABLE IF EXISTS audit_logs;
        """,
        )
    )

    logger.info(f"Registered {len(manager.migrations)} database migrations")


async def run_migrations(target_version: Optional[str] = None) -> Dict[str, Any]:
    """Run database migrations."""
    register_migrations()
    manager = get_migration_manager()
    return await manager.migrate_up(target_version)


async def rollback_migrations(target_version: str) -> Dict[str, Any]:
    """Rollback database migrations."""
    register_migrations()
    manager = get_migration_manager()
    return await manager.migrate_down(target_version)


async def get_migration_status() -> Dict[str, Any]:
    """Get migration status."""
    register_migrations()
    manager = get_migration_manager()
    return await manager.get_migration_status()
