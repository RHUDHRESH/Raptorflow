"""
Automated database migration runner for RaptorFlow
Handles Supabase database schema migrations with version tracking
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.core.supabase_mgr import get_supabase_client
from supabase import Client

logger = logging.getLogger(__name__)


class Migration:
    """Represents a database migration"""

    def __init__(
        self, version: str, name: str, sql: str, rollback_sql: Optional[str] = None
    ):
        self.version = version
        self.name = name
        self.sql = sql
        self.rollback_sql = rollback_sql
        self.applied_at: Optional[datetime] = None


class MigrationRunner:
    """Database migration runner for Supabase"""

    def __init__(self, client: Optional[Client] = None):
        self.client = client or get_supabase_client()
        self.migrations_table = "schema_migrations"

    async def ensure_migrations_table(self) -> None:
        """Ensure the migrations tracking table exists"""
        try:
            # Check if migrations table exists
            result = (
                self.client.table(self.migrations_table)
                .select("version")
                .limit(1)
                .execute()
            )

            if not result.data:
                # Create migrations table
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    rollback_sql TEXT
                );
                """

                # Execute the table creation
                self.client.rpc("exec_sql", {"sql": create_table_sql}).execute()
                logger.info("Created migrations tracking table")

        except Exception as e:
            logger.error(f"Failed to ensure migrations table: {e}")
            raise

    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions"""
        try:
            result = (
                self.client.table(self.migrations_table)
                .select("version")
                .order("applied_at")
                .execute()
            )
            return [migration["version"] for migration in result.data]
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []

    async def load_migrations(
        self, migrations_dir: str = "supabase/migrations"
    ) -> List[Migration]:
        """Load migration files from directory"""
        migrations = []
        migrations_path = Path(migrations_dir)

        if not migrations_path.exists():
            logger.warning(f"Migrations directory {migrations_dir} not found")
            return migrations

        # Load SQL files in order
        for sql_file in sorted(migrations_path.glob("*.sql")):
            try:
                # Extract version from filename (e.g., 20240101_users.sql)
                version = sql_file.stem

                # Read migration SQL
                with open(sql_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Split into migration and rollback SQL
                parts = content.split("-- ROLLBACK")
                migration_sql = parts[0].strip()
                rollback_sql = parts[1].strip() if len(parts) > 1 else None

                # Extract name from first line comment
                name = sql_file.stem
                lines = migration_sql.split("\n")
                for line in lines:
                    if line.strip().startswith("--"):
                        name = line.strip().replace("--", "").strip()
                        break

                migrations.append(Migration(version, name, migration_sql, rollback_sql))

            except Exception as e:
                logger.error(f"Failed to load migration {sql_file}: {e}")

        return migrations

    async def apply_migration(self, migration: Migration) -> bool:
        """Apply a single migration"""
        try:
            logger.info(f"Applying migration {migration.version}: {migration.name}")

            # Execute migration SQL
            self.client.rpc("exec_sql", {"sql": migration.sql}).execute()

            # Record migration
            migration_record = {
                "version": migration.version,
                "name": migration.name,
                "applied_at": datetime.utcnow().isoformat(),
                "rollback_sql": migration.rollback_sql,
            }

            self.client.table(self.migrations_table).insert(migration_record).execute()

            migration.applied_at = datetime.utcnow()
            logger.info(f"Successfully applied migration {migration.version}")
            return True

        except Exception as e:
            logger.error(f"Failed to apply migration {migration.version}: {e}")
            return False

    async def rollback_migration(self, version: str) -> bool:
        """Rollback a specific migration"""
        try:
            # Get migration record
            result = (
                self.client.table(self.migrations_table)
                .select("*")
                .eq("version", version)
                .execute()
            )

            if not result.data:
                logger.error(f"Migration {version} not found")
                return False

            migration_record = result.data[0]
            rollback_sql = migration_record.get("rollback_sql")

            if not rollback_sql:
                logger.error(f"No rollback SQL available for migration {version}")
                return False

            logger.info(f"Rolling back migration {version}")

            # Execute rollback SQL
            self.client.rpc("exec_sql", {"sql": rollback_sql}).execute()

            # Remove migration record
            self.client.table(self.migrations_table).delete().eq(
                "version", version
            ).execute()

            logger.info(f"Successfully rolled back migration {version}")
            return True

        except Exception as e:
            logger.error(f"Failed to rollback migration {version}: {e}")
            return False

    async def migrate(self, target_version: Optional[str] = None) -> Dict[str, Any]:
        """Run migrations up to target version"""
        try:
            await self.ensure_migrations_table()

            # Load all migrations
            migrations = await self.load_migrations()
            applied_migrations = await self.get_applied_migrations()

            # Determine which migrations to apply
            to_apply = []
            for migration in migrations:
                if migration.version not in applied_migrations:
                    if target_version is None or migration.version <= target_version:
                        to_apply.append(migration)

            # Apply migrations
            applied = []
            failed = []

            for migration in to_apply:
                success = await self.apply_migration(migration)
                if success:
                    applied.append(migration.version)
                else:
                    failed.append(migration.version)
                    break  # Stop on first failure

            return {
                "status": "success" if not failed else "partial_failure",
                "applied": applied,
                "failed": failed,
                "total_to_apply": len(to_apply),
                "already_applied": len(applied_migrations),
            }

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return {"status": "error", "error": str(e), "applied": [], "failed": []}

    async def rollback_to_version(self, target_version: str) -> Dict[str, Any]:
        """Rollback migrations to target version"""
        try:
            applied_migrations = await self.get_applied_migrations()

            # Get migrations to rollback (in reverse order)
            to_rollback = []
            for version in reversed(applied_migrations):
                if version > target_version:
                    to_rollback.append(version)

            # Rollback migrations
            rolled_back = []
            failed = []

            for version in to_rollback:
                success = await self.rollback_migration(version)
                if success:
                    rolled_back.append(version)
                else:
                    failed.append(version)
                    break  # Stop on first failure

            return {
                "status": "success" if not failed else "partial_failure",
                "rolled_back": rolled_back,
                "failed": failed,
                "total_to_rollback": len(to_rollback),
            }

        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return {"status": "error", "error": str(e), "rolled_back": [], "failed": []}

    async def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status"""
        try:
            await self.ensure_migrations_table()

            migrations = await self.load_migrations()
            applied_migrations = await self.get_applied_migrations()

            pending = [m for m in migrations if m.version not in applied_migrations]

            return {
                "total_migrations": len(migrations),
                "applied_count": len(applied_migrations),
                "pending_count": len(pending),
                "applied_migrations": applied_migrations,
                "pending_migrations": [m.version for m in pending],
                "status": "up_to_date" if not pending else "pending_migrations",
            }

        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {"status": "error", "error": str(e)}


# Global migration runner
_migration_runner: Optional[MigrationRunner] = None


def get_migration_runner() -> MigrationRunner:
    """Get global migration runner instance"""
    global _migration_runner
    if _migration_runner is None:
        _migration_runner = MigrationRunner()
    return _migration_runner


async def run_migrations(target_version: Optional[str] = None) -> Dict[str, Any]:
    """Run database migrations"""
    runner = get_migration_runner()
    return await runner.migrate(target_version)


async def rollback_migrations(target_version: str) -> Dict[str, Any]:
    """Rollback database migrations"""
    runner = get_migration_runner()
    return await runner.rollback_to_version(target_version)


async def get_migration_status() -> Dict[str, Any]:
    """Get migration status"""
    runner = get_migration_runner()
    return await runner.get_migration_status()


# CLI command for running migrations
async def main():
    """CLI entry point for migration commands"""
    import sys

    command = sys.argv[1] if len(sys.argv) > 1 else "status"

    runner = get_migration_runner()

    if command == "status":
        status = await runner.get_migration_status()
        print(f"Migration Status: {status['status']}")
        print(f"Applied: {status['applied_count']}/{status['total_migrations']}")
        if status.get("pending_migrations"):
            print(f"Pending: {', '.join(status['pending_migrations'])}")

    elif command == "migrate":
        target = sys.argv[2] if len(sys.argv) > 2 else None
        result = await runner.migrate(target)
        print(f"Migration {result['status']}")
        if result["applied"]:
            print(f"Applied: {', '.join(result['applied'])}")
        if result["failed"]:
            print(f"Failed: {', '.join(result['failed'])}")

    elif command == "rollback":
        target = sys.argv[2] if len(sys.argv) > 2 else None
        if not target:
            print("Error: Target version required for rollback")
            sys.exit(1)

        result = await runner.rollback_to_version(target)
        print(f"Rollback {result['status']}")
        if result["rolled_back"]:
            print(f"Rolled back: {', '.join(result['rolled_back'])}")
        if result["failed"]:
            print(f"Failed: {', '.join(result['failed'])}")

    else:
        print("Usage: python migrate.py [status|migrate [version]|rollback <version>]")


if __name__ == "__main__":
    asyncio.run(main())
