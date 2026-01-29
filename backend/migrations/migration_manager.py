"""
RaptorFlow Migration Manager
Handles database schema migrations with versioning and rollback capabilities.
"""

import asyncio
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

import asyncpg
from supabase import create_client

from .config import get_settings
from .core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


@dataclass
class Migration:
    """Migration definition."""

    version: str
    name: str
    filename: str
    sql_content: str
    rollback_sql: Optional[str] = None
    dependencies: List[str] = None
    applied_at: Optional[datetime] = None


class MigrationManager:
    """Database migration manager."""

    def __init__(self):
        self.migrations_dir = os.path.join(os.path.dirname(__file__))
        self.applied_migrations_table = "schema_migrations"
        self.db_client = None

    async def _get_db_connection(self):
        """Get database connection."""
        if self.db_client is None:
            # Use direct PostgreSQL connection for migrations
            self.db_client = await asyncpg.connect(
                host=settings.DATABASE_HOST,
                port=settings.DATABASE_PORT,
                database=settings.DATABASE_NAME,
                user=settings.DATABASE_USER,
                password=settings.DATABASE_PASSWORD,
            )
        return self.db_client

    async def initialize_migration_table(self):
        """Initialize the migrations tracking table."""
        conn = await self._get_db_connection()

        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.applied_migrations_table} (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            version VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(255) NOT NULL,
            filename VARCHAR(255) NOT NULL,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            checksum VARCHAR(64),
            execution_time_ms INTEGER
        );
        """

        await conn.execute(create_table_sql)
        logger.info("Migration tracking table initialized")

    async def load_migrations(self) -> List[Migration]:
        """Load all migration files."""
        migrations = []

        # Get all SQL files in migrations directory
        for filename in os.listdir(self.migrations_dir):
            if filename.endswith(".sql") and not filename.startswith("rollback_"):
                version = filename.split("_")[0]
                name = filename.replace(".sql", "").replace("_", " ", 2).title()

                filepath = os.path.join(self.migrations_dir, filename)

                with open(filepath, "r", encoding="utf-8") as f:
                    sql_content = f.read()

                # Check for corresponding rollback file
                rollback_filename = f"rollback_{filename}"
                rollback_filepath = os.path.join(self.migrations_dir, rollback_filename)
                rollback_sql = None

                if os.path.exists(rollback_filepath):
                    with open(rollback_filepath, "r", encoding="utf-8") as f:
                        rollback_sql = f.read()

                migration = Migration(
                    version=version,
                    name=name,
                    filename=filename,
                    sql_content=sql_content,
                    rollback_sql=rollback_sql,
                    dependencies=[],
                )

                migrations.append(migration)

        # Sort by version
        migrations.sort(key=lambda m: m.version)
        return migrations

    async def get_applied_migrations(self) -> Dict[str, Migration]:
        """Get list of applied migrations from database."""
        conn = await self._get_db_connection()

        try:
            rows = await conn.fetch(
                f"""
                SELECT version, name, filename, applied_at, checksum, execution_time_ms
                FROM {self.applied_migrations_table}
                ORDER BY applied_at
            """
            )

            applied = {}
            for row in rows:
                applied[row["version"]] = Migration(
                    version=row["version"],
                    name=row["name"],
                    filename=row["filename"],
                    sql_content="",  # Not stored in database
                    applied_at=row["applied_at"],
                )

            return applied

        except Exception as e:
            # Table might not exist yet
            logger.warning(f"Could not load applied migrations: {e}")
            return {}

    async def apply_migration(self, migration: Migration) -> bool:
        """Apply a single migration."""
        conn = await self._get_db_connection()

        try:
            start_time = datetime.utcnow()

            # Start transaction
            async with conn.transaction():
                # Execute migration SQL
                await conn.execute(migration.sql_content)

                # Record migration
                await conn.execute(
                    f"""
                    INSERT INTO {self.applied_migrations_table}
                    (version, name, filename, applied_at, checksum, execution_time_ms)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """,
                    migration.version,
                    migration.name,
                    migration.filename,
                    start_time,
                    "",
                    0,
                )

            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            logger.info(f"Applied migration {migration.version}: {migration.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to apply migration {migration.version}: {e}")
            return False

    async def rollback_migration(self, migration: Migration) -> bool:
        """Rollback a migration."""
        if not migration.rollback_sql:
            logger.error(f"No rollback SQL available for migration {migration.version}")
            return False

        conn = await self._get_db_connection()

        try:
            start_time = datetime.utcnow()

            # Start transaction
            async with conn.transaction():
                # Execute rollback SQL
                await conn.execute(migration.rollback_sql)

                # Remove migration record
                await conn.execute(
                    f"""
                    DELETE FROM {self.applied_migrations_table}
                    WHERE version = $1
                """,
                    migration.version,
                )

            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            logger.info(f"Rolled back migration {migration.version}: {migration.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to rollback migration {migration.version}: {e}")
            return False

    async def migrate(self) -> Dict[str, any]:
        """Run all pending migrations."""
        await self.initialize_migration_table()

        # Load migrations
        all_migrations = await self.load_migrations()
        applied_migrations = await self.get_applied_migrations()

        # Find pending migrations
        pending_migrations = [
            m for m in all_migrations if m.version not in applied_migrations
        ]

        results = {
            "total_migrations": len(all_migrations),
            "applied_migrations": len(applied_migrations),
            "pending_migrations": len(pending_migrations),
            "executed": [],
            "failed": [],
            "start_time": datetime.utcnow(),
        }

        # Apply pending migrations
        for migration in pending_migrations:
            success = await self.apply_migration(migration)

            if success:
                results["executed"].append(
                    {
                        "version": migration.version,
                        "name": migration.name,
                        "applied_at": datetime.utcnow(),
                    }
                )
            else:
                results["failed"].append(
                    {
                        "version": migration.version,
                        "name": migration.name,
                        "error": "Migration failed",
                    }
                )

        results["end_time"] = datetime.utcnow()
        results["total_time"] = (
            results["end_time"] - results["start_time"]
        ).total_seconds()

        return results

    async def rollback(self, target_version: Optional[str] = None) -> Dict[str, any]:
        """Rollback migrations."""
        await self.initialize_migration_table()

        applied_migrations = await self.get_applied_migrations()

        # If no target version, rollback last migration
        if not target_version and applied_migrations:
            # Get the most recent applied migration
            target_migration = max(
                applied_migrations.values(), key=lambda m: m.applied_at
            )
            target_version = target_migration.version

        results = {
            "target_version": target_version,
            "rolled_back": [],
            "failed": [],
            "start_time": datetime.utcnow(),
        }

        # Rollback migrations in reverse order
        if target_version:
            # Load all migrations to get rollback SQL
            all_migrations = await self.load_migrations()
            migration_dict = {m.version: m for m in all_migrations}

            # Get migrations to rollback (including target and all after it)
            versions_to_rollback = [
                v for v in applied_migrations.keys() if v >= target_version
            ]

            # Sort in reverse order
            versions_to_rollback.sort(reverse=True)

            for version in versions_to_rollback:
                if version in migration_dict:
                    migration = migration_dict[version]
                    success = await self.rollback_migration(migration)

                    if success:
                        results["rolled_back"].append(
                            {
                                "version": version,
                                "name": migration.name,
                                "rolled_back_at": datetime.utcnow(),
                            }
                        )
                    else:
                        results["failed"].append(
                            {
                                "version": version,
                                "name": migration.name,
                                "error": "Rollback failed",
                            }
                        )

        results["end_time"] = datetime.utcnow()
        results["total_time"] = (
            results["end_time"] - results["start_time"]
        ).total_seconds()

        return results

    async def get_migration_status(self) -> Dict[str, any]:
        """Get current migration status."""
        await self.initialize_migration_table()

        all_migrations = await self.load_migrations()
        applied_migrations = await self.get_applied_migrations()

        return {
            "total_migrations": len(all_migrations),
            "applied_migrations": len(applied_migrations),
            "pending_migrations": len(all_migrations) - len(applied_migrations),
            "latest_applied": (
                max(applied_migrations.keys()) if applied_migrations else None
            ),
            "all_migrations": [
                {
                    "version": m.version,
                    "name": m.name,
                    "applied": m.version in applied_migrations,
                    "applied_at": (
                        applied_migrations[m.version].applied_at
                        if m.version in applied_migrations
                        else None
                    ),
                }
                for m in all_migrations
            ],
        }


# CLI interface for migration management
async def run_migrations():
    """Run pending migrations."""
    manager = MigrationManager()
    results = await manager.migrate()

    print(f"Migration Results:")
    print(f"  Total migrations: {results['total_migrations']}")
    print(f"  Applied migrations: {results['applied_migrations']}")
    print(f"  Pending migrations: {results['pending_migrations']}")
    print(f"  Executed: {len(results['executed'])}")
    print(f"  Failed: {len(results['failed'])}")
    print(f"  Total time: {results['total_time']:.2f}s")

    if results["failed"]:
        print("Failed migrations:")
        for failed in results["failed"]:
            print(f"  - {failed['version']}: {failed['error']}")
        return False

    return True


async def rollback_migrations(target_version: Optional[str] = None):
    """Rollback migrations."""
    manager = MigrationManager()
    results = await manager.rollback(target_version)

    print(f"Rollback Results:")
    print(f"  Target version: {results['target_version']}")
    print(f"  Rolled back: {len(results['rolled_back'])}")
    print(f"  Failed: {len(results['failed'])}")
    print(f"  Total time: {results['total_time']:.2f}s")

    if results["failed"]:
        print("Failed rollbacks:")
        for failed in results["failed"]:
            print(f"  - {failed['version']}: {failed['error']}")
        return False

    return True


async def show_migration_status():
    """Show migration status."""
    manager = MigrationManager()
    status = await manager.get_migration_status()

    print(f"Migration Status:")
    print(f"  Total migrations: {status['total_migrations']}")
    print(f"  Applied migrations: {status['applied_migrations']}")
    print(f"  Pending migrations: {status['pending_migrations']}")
    print(f"  Latest applied: {status['latest_applied']}")

    print("\nAll migrations:")
    for migration in status["all_migrations"]:
        status_str = "✓ Applied" if migration["applied"] else "○ Pending"
        applied_at = f" at {migration['applied_at']}" if migration["applied"] else ""
        print(
            f"  {migration['version']}: {migration['name']} - {status_str}{applied_at}"
        )


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python migration_manager.py [migrate|rollback|status] [version]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "migrate":
        success = asyncio.run(run_migrations())
        sys.exit(0 if success else 1)

    elif command == "rollback":
        target = sys.argv[2] if len(sys.argv) > 2 else None
        success = asyncio.run(rollback_migrations(target))
        sys.exit(0 if success else 1)

    elif command == "status":
        asyncio.run(show_migration_status())

    else:
        print("Unknown command. Use: migrate, rollback, or status")
        sys.exit(1)
