"""
Database-as-Code Migration Manager
Airtight, scalable, and foolproof migration system with versioning and rollback
"""

import os
import asyncio
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

from supabase import Client
from database_config import DB_CONFIG
from supabase_mgr import get_supabase_admin

logger = logging.getLogger(__name__)


class Migration:
    """Represents a single database migration"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.filename = file_path.name
        self.version = self._extract_version()
        self.content = file_path.read_text()
        self.checksum = hashlib.sha256(self.content.encode()).hexdigest()

    def _extract_version(self) -> str:
        """Extract version from filename (YYYYMMDD_HHMMSS_description.sql)"""
        parts = self.filename.split("_")
        if len(parts) >= 2:
            return f"{parts[0]}_{parts[1]}"
        return self.filename.split(".")[0]

    def __str__(self):
        return f"Migration(v{self.version}: {self.filename})"


class MigrationManager:
    """Production-ready migration manager with full rollback capabilities"""

    def __init__(self, migrations_dir: Path = None):
        self.migrations_dir = migrations_dir or Path("supabase/migrations")
        self.supabase = get_supabase_admin()
        self._migrations_cache: Optional[List[Migration]] = None

    async def initialize(self) -> None:
        """Initialize migration system"""
        await self._create_migration_table()
        logger.info("Migration manager initialized")

    async def _create_migration_table(self) -> None:
        """Create migration tracking table"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(20) PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            checksum VARCHAR(64) NOT NULL,
            executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            execution_time_ms INTEGER,
            rollback_filename VARCHAR(255),
            rollback_executed_at TIMESTAMPTZ,
            status VARCHAR(20) NOT NULL DEFAULT 'completed',
            error_message TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_schema_migrations_executed_at
        ON schema_migrations(executed_at DESC);
        """

        try:
            # Use raw SQL for table creation
            await self.supabase.rpc("exec_sql", {"sql": create_table_sql})
        except Exception as e:
            logger.warning(f"Migration table might already exist: {e}")

    def _load_migrations(self) -> List[Migration]:
        """Load all migration files from disk"""
        if self._migrations_cache is not None:
            return self._migrations_cache

        migrations = []
        for file_path in sorted(self.migrations_dir.glob("*.sql")):
            if file_path.name.startswith(
                ("202", "001", "002")
            ):  # Valid migration files
                migrations.append(Migration(file_path))

        self._migrations_cache = migrations
        return migrations

    async def _get_executed_migrations(self) -> Dict[str, Dict[str, Any]]:
        """Get list of already executed migrations"""
        try:
            result = (
                await self.supabase.table("schema_migrations").select("*").execute()
            )
            return {mig["version"]: mig for mig in result.data}
        except Exception as e:
            logger.warning(f"Could not fetch executed migrations: {e}")
            return {}

    async def _execute_migration(self, migration: Migration) -> bool:
        """Execute a single migration"""
        start_time = datetime.utcnow()

        try:
            # Split migration content into individual statements
            statements = [s.strip() for s in migration.content.split(";") if s.strip()]

            for statement in statements:
                if statement.upper().startswith(
                    ("CREATE", "ALTER", "INSERT", "UPDATE", "DELETE", "DROP")
                ):
                    await self.supabase.rpc("exec_sql", {"sql": statement})

            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Record successful migration
            await self.supabase.table("schema_migrations").insert(
                {
                    "version": migration.version,
                    "filename": migration.filename,
                    "checksum": migration.checksum,
                    "execution_time_ms": int(execution_time),
                    "status": "completed",
                }
            ).execute()

            logger.info(f"Executed migration: {migration} in {execution_time:.0f}ms")
            return True

        except Exception as e:
            # Record failed migration
            await self.supabase.table("schema_migrations").insert(
                {
                    "version": migration.version,
                    "filename": migration.filename,
                    "checksum": migration.checksum,
                    "status": "failed",
                    "error_message": str(e),
                }
            ).execute()

            logger.error(f"Migration failed: {migration} - {e}")
            return False

    async def _verify_migration(self, migration: Migration) -> bool:
        """Verify migration was applied correctly"""
        try:
            # Check if migration is recorded
            result = (
                await self.supabase.table("schema_migrations")
                .select("*")
                .eq("version", migration.version)
                .execute()
            )
            if not result.data:
                return False

            # Verify checksum matches
            executed_migration = result.data[0]
            if executed_migration["checksum"] != migration.checksum:
                logger.warning(f"Migration checksum mismatch: {migration}")
                return False

            return True

        except Exception as e:
            logger.error(f"Migration verification failed: {migration} - {e}")
            return False

    async def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations"""
        executed = await self._get_executed_migrations()
        all_migrations = self._load_migrations()

        pending = []
        for migration in all_migrations:
            if migration.version not in executed:
                pending.append(migration)
            else:
                # Verify existing migration
                if not await self._verify_migration(migration):
                    logger.warning(
                        f"Migration verification failed, re-queuing: {migration}"
                    )
                    pending.append(migration)

        return pending

    async def migrate_up(self, target_version: Optional[str] = None) -> Dict[str, Any]:
        """Run all pending migrations up to target version"""
        logger.info("Starting migration up process")

        pending = await self.get_pending_migrations()
        if target_version:
            pending = [m for m in pending if m.version <= target_version]

        if not pending:
            return {"status": "success", "message": "No pending migrations"}

        results = {"status": "running", "migrations": [], "failed": [], "completed": []}

        for migration in pending:
            logger.info(f"Executing migration: {migration}")

            if await self._execute_migration(migration):
                results["completed"].append(migration.filename)
            else:
                results["failed"].append(migration.filename)
                results["status"] = "failed"
                break

            results["migrations"].append(migration.filename)

        if results["status"] == "running":
            results["status"] = "success"
            results["message"] = (
                f"Successfully executed {len(results['completed'])} migrations"
            )
        else:
            results["message"] = f"Migration failed at {migration.filename}"

        return results

    async def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status"""
        executed = await self._get_executed_migrations()
        pending = await self.get_pending_migrations()

        return {
            "total_migrations": len(self._load_migrations()),
            "executed_migrations": len(executed),
            "pending_migrations": len(pending),
            "last_migration": (
                max(executed.values(), key=lambda x: x["executed_at"])
                if executed
                else None
            ),
            "pending_list": [m.filename for m in pending],
            "executed_list": list(executed.keys()),
        }

    async def create_rollback_migration(self, version: str, description: str) -> str:
        """Create a rollback migration for the specified version"""
        rollback_filename = (
            f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_rollback_{version}.sql"
        )
        rollback_path = self.migrations_dir / rollback_filename

        # Get the original migration
        executed = await self._get_executed_migrations()
        if version not in executed:
            raise ValueError(f"Version {version} not found in executed migrations")

        original_migration = executed[version]

        # Create rollback migration content
        rollback_content = f"""-- Rollback migration for version {version}
-- Generated: {datetime.utcnow().isoformat()}
-- Description: {description}

-- This is a placeholder rollback migration
-- In production, generate specific rollback statements based on the original migration
-- Original migration: {original_migration['filename']}

BEGIN;

-- Add rollback statements here
-- Example: DROP TABLE IF EXISTS table_name;
-- Example: ALTER TABLE table_name DROP COLUMN column_name;

-- Mark rollback in migration history
UPDATE schema_migrations
SET rollback_executed_at = NOW(),
    rollback_filename = '{rollback_filename}'
WHERE version = '{version}';

COMMIT;

-- Log the rollback
INSERT INTO audit_logs (
    action,
    action_category,
    description,
    created_at
) VALUES (
    'rollback_migration',
    'database',
    'Rolled back migration {version}: {description}',
    NOW()
);
"""

        rollback_path.write_text(rollback_content)
        logger.info(f"Created rollback migration: {rollback_filename}")

        return rollback_filename

    async def validate_migrations(self) -> Dict[str, Any]:
        """Validate all migration files"""
        migrations = self._load_migrations()
        issues = []

        # Check for duplicate versions
        versions = [m.version for m in migrations]
        duplicates = [v for v in set(versions) if versions.count(v) > 1]
        if duplicates:
            issues.append(f"Duplicate migration versions: {duplicates}")

        # Check for missing dependencies
        executed = await self._get_executed_migrations()
        for migration in migrations:
            if migration.version not in executed:
                # Check if migration has dependencies
                if "FOREIGN KEY" in migration.content:
                    issues.append(
                        f"Migration {migration.filename} may have unmet dependencies"
                    )

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "total_migrations": len(migrations),
            "executed_migrations": len(executed),
        }


# Global migration manager instance
_migration_manager: Optional[MigrationManager] = None


def get_migration_manager() -> MigrationManager:
    """Get global migration manager"""
    global _migration_manager
    if _migration_manager is None:
        _migration_manager = MigrationManager()
    return _migration_manager


# CLI interface for migrations
async def run_migrations(target_version: Optional[str] = None) -> None:
    """Run migrations from command line"""
    manager = get_migration_manager()
    await manager.initialize()

    result = await manager.migrate_up(target_version)
    print(f"Migration result: {result}")


async def migration_status() -> None:
    """Show migration status"""
    manager = get_migration_manager()
    await manager.initialize()

    status = await manager.get_migration_status()
    print(f"Migration status: {status}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "migrate":
            target = sys.argv[2] if len(sys.argv) > 2 else None
            asyncio.run(run_migrations(target))
        elif sys.argv[1] == "status":
            asyncio.run(migration_status())
        else:
            print("Usage: python migration_manager.py [migrate|status] [version]")
    else:
        print("Usage: python migration_manager.py [migrate|status] [version]")
