#!/usr/bin/env python3
"""
Subscription Plans Migration Runner

This script executes the subscription plans migration to:
1. Drop the old subscription_plans table
2. Create the archive table structure with appropriate constraints
3. Migrate any existing data into the new schema
4. Update foreign keys in subscriptions and payment_transactions tables
5. Fix duplicate subscription plans and infinite recursion
6. Apply comprehensive security fixes

Usage:
    python run_subscription_migration.py

Environment Variables:
    DB_HOST - Database host (default: localhost)
    DB_PORT - Database port (default: 5432)
    DB_NAME - Database name (default: postgres)
    DB_USER - Database user (default: postgres)
    DB_PASSWORD - Database password (required)
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Tuple

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Migration files to execute in order
MIGRATIONS: List[Tuple[str, str]] = [
    ("Drop old table and adopt archive schema", "supabase/migrations/20260130_drop_old_table_adopt_archive_schema.sql"),
    ("Fix duplicate subscription plans and infinite recursion", "supabase/migrations/20260130_fix_duplicate_subscription_plans.sql"),
    ("Apply comprehensive security fixes", "supabase/migrations/20260130_comprehensive_security_fixes.sql"),
]

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Error as e:
        print_error(f"Failed to connect to database: {e}")
        sys.exit(1)


def check_migration_applied(conn, migration_name: str) -> bool:
    """Check if a migration has already been applied."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM supabase_migrations.schema_migrations
                    WHERE version = %s
                )
            """, (migration_name,))
            return cur.fetchone()[0]
    except Error:
        # If schema_migrations table doesn't exist, assume not applied
        return False


def record_migration(conn, migration_name: str):
    """Record that a migration has been applied."""
    try:
        with conn.cursor() as cur:
            # Ensure schema_migrations table exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS supabase_migrations.schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)

            # Record the migration
            cur.execute("""
                INSERT INTO supabase_migrations.schema_migrations (version)
                VALUES (%s)
                ON CONFLICT (version) DO NOTHING
            """, (migration_name,))
    except Error as e:
        print_warning(f"Could not record migration: {e}")


def execute_migration(conn, migration_file: str, migration_name: str) -> bool:
    """Execute a migration SQL file."""
    migration_path = Path(migration_file)

    if not migration_path.exists():
        print_error(f"Migration file not found: {migration_file}")
        return False

    print_info(f"Reading migration file: {migration_file}")

    try:
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print_info(f"Executing migration ({len(sql_content)} characters)...")

        with conn.cursor() as cur:
            cur.execute(sql_content)

        # Record the migration
        record_migration(conn, migration_name)

        print_success("Migration executed successfully")
        return True

    except Error as e:
        print_error(f"Migration failed: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def verify_migration(conn) -> bool:
    """Verify that the migration was successful."""
    print_info("Verifying migration...")

    try:
        with conn.cursor() as cur:
            # Check if subscription_plans table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'subscription_plans'
                )
            """)
            table_exists = cur.fetchone()[0]

            if not table_exists:
                print_error("subscription_plans table does not exist")
                return False

            print_success("subscription_plans table exists")

            # Check if we have the expected plans
            cur.execute("""
                SELECT name, slug, is_active
                FROM public.subscription_plans
                ORDER BY sort_order
            """)
            plans = cur.fetchall()

            if len(plans) == 0:
                print_warning("No subscription plans found")
            else:
                print_success(f"Found {len(plans)} subscription plan(s):")
                for name, slug, is_active in plans:
                    status = "active" if is_active else "inactive"
                    print(f"  - {name} ({slug}) - {status}")

            # Check foreign key constraints
            cur.execute("""
                SELECT COUNT(*)
                FROM information_schema.table_constraints
                WHERE constraint_type = 'FOREIGN KEY'
                AND table_name IN ('subscriptions', 'payment_transactions')
            """)
            fk_count = cur.fetchone()[0]

            print_success(f"Found {fk_count} foreign key constraint(s) on subscriptions and payment_transactions")

            # Check RLS is enabled
            cur.execute("""
                SELECT relname, relrowsecurity
                FROM pg_class
                WHERE relname IN ('subscription_plans', 'subscriptions', 'payment_transactions')
                AND relnamespace = 'public'::regnamespace
            """)
            rls_status = cur.fetchall()

            for table_name, rls_enabled in rls_status:
                status = "enabled" if rls_enabled else "disabled"
                print_info(f"RLS on {table_name}: {status}")

            return True

    except Error as e:
        print_error(f"Verification failed: {e}")
        return False


def run_migrations():
    """Run all migrations in order."""
    print_header("Subscription Plans Migration")

    # Check environment variables
    print_info("Checking environment variables...")
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print_error(f"Missing environment variables: {', '.join(missing_vars)}")
        print_info("Please set the following environment variables:")
        for var in required_vars:
            print(f"  - {var}")
        sys.exit(1)

    print_success("All environment variables are set")

    # Connect to database
    print_info("Connecting to database...")
    conn = get_db_connection()
    print_success("Connected to database")

    # Display migration plan
    print_info("Migration plan:")
    for i, (description, _) in enumerate(MIGRATIONS, 1):
        print(f"  {i}. {description}")

    # Ask for confirmation
    print_warning("\nThis will modify your database schema.")
    response = input("Do you want to proceed? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print_info("Migration cancelled by user")
        conn.close()
        sys.exit(0)

    # Execute migrations
    print_header("Executing Migrations")
    success_count = 0
    failed_migrations = []

    for description, migration_file in MIGRATIONS:
        print(f"\n{Colors.BOLD}Step: {description}{Colors.ENDC}")
        print("-" * 70)
        migration_name = Path(migration_file).stem

        # Check if already applied
        if check_migration_applied(conn, migration_name):
            print_warning("Migration already applied, skipping...")
            success_count += 1
            continue

        # Execute migration
        start_time = time.time()
        success = execute_migration(conn, migration_file, migration_name)
        elapsed_time = time.time() - start_time

        if success:
            print_success(f"Completed in {elapsed_time:.2f} seconds")
            success_count += 1
        else:
            print_error(f"Failed after {elapsed_time:.2f} seconds")
            failed_migrations.append((description, migration_file))
            break

    # Summary
    print_header("Migration Summary")

    total_migrations = len(MIGRATIONS)

    if success_count == total_migrations:
        print_success(f"All {total_migrations} migration(s) completed successfully!")

        # Verify migration
        if verify_migration(conn):
            print_success("Migration verification passed")
        else:
            print_warning("Migration verification failed, but migration was applied")

        conn.close()
        print_header("Migration Complete")
        print_success("You can now use the new subscription plans schema")
        sys.exit(0)
    else:
        print_error(f"Migration failed: {success_count}/{total_migrations} completed")

        if failed_migrations:
            print_error("\nFailed migrations:")
            for description, migration_file in failed_migrations:
                print(f"  - {description} ({migration_file})")

        conn.close()
        print_header("Migration Failed")
        print_error("Please review the errors above and fix any issues")
        print_info("You may need to manually rollback or fix the database state")
        sys.exit(1)


def main():
    """Main entry point."""
    try:
        run_migrations()
    except KeyboardInterrupt:
        print_warning("\nMigration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
"""
Subscription Plans Migration Runner

This script executes the subscription plans migration to:
1. Drop the old subscription_plans table
2. Create the archive table structure with appropriate constraints
3. Migrate any existing data into the new schema
4. Update foreign keys in subscriptions and payment_transactions tables
5. Fix duplicate subscription plans and infinite recursion
6. Apply comprehensive security fixes

Usage:
    python run_subscription_migration.py

Environment Variables:
    DB_HOST - Database host (default: localhost)
    DB_PORT - Database port (default: 5432)
    DB_NAME - Database name (default: postgres)
    DB_USER - Database user (default: postgres)
    DB_PASSWORD - Database password (required)
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Tuple

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Migration files to execute in order
MIGRATIONS: List[Tuple[str, str]] = [
    ("Drop old table and adopt archive schema", "supabase/migrations/20260130_drop_old_table_adopt_archive_schema.sql"),
    ("Fix duplicate subscription plans and infinite recursion", "supabase/migrations/20260130_fix_duplicate_subscription_plans.sql"),
    ("Apply comprehensive security fixes", "supabase/migrations/20260130_comprehensive_security_fixes.sql"),
]

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Error as e:
        print_error(f"Failed to connect to database: {e}")
        sys.exit(1)


def check_migration_applied(conn, migration_name: str) -> bool:
    """Check if a migration has already been applied."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM supabase_migrations.schema_migrations
                    WHERE version = %s
                )
            """, (migration_name,))
            return cur.fetchone()[0]
    except Error:
        # If schema_migrations table doesn't exist, assume not applied
        return False


def record_migration(conn, migration_name: str):
    """Record that a migration has been applied."""
    try:
        with conn.cursor() as cur:
            # Ensure schema_migrations table exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS supabase_migrations.schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)

            # Record the migration
            cur.execute("""
                INSERT INTO supabase_migrations.schema_migrations (version)
                VALUES (%s)
                ON CONFLICT (version) DO NOTHING
            """, (migration_name,))
    except Error as e:
        print_warning(f"Could not record migration: {e}")


def execute_migration(conn, migration_file: str, migration_name: str) -> bool:
    """Execute a migration SQL file."""
    migration_path = Path(migration_file)

    if not migration_path.exists():
        print_error(f"Migration file not found: {migration_file}")
        return False

    print_info(f"Reading migration file: {migration_file}")

    try:
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print_info(f"Executing migration ({len(sql_content)} characters)...")

        with conn.cursor() as cur:
            cur.execute(sql_content)

        # Record the migration
        record_migration(conn, migration_name)

        print_success("Migration executed successfully")
        return True

    except Error as e:
        print_error(f"Migration failed: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def verify_migration(conn) -> bool:
    """Verify that the migration was successful."""
    print_info("Verifying migration...")

    try:
        with conn.cursor() as cur:
            # Check if subscription_plans table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'subscription_plans'
                )
            """)
            table_exists = cur.fetchone()[0]

            if not table_exists:
                print_error("subscription_plans table does not exist")
                return False

            print_success("subscription_plans table exists")

            # Check if we have the expected plans
            cur.execute("""
                SELECT name, slug, is_active
                FROM public.subscription_plans
                ORDER BY sort_order
            """)
            plans = cur.fetchall()

            if len(plans) == 0:
                print_warning("No subscription plans found")
            else:
                print_success(f"Found {len(plans)} subscription plan(s):")
                for name, slug, is_active in plans:
                    status = "active" if is_active else "inactive"
                    print(f"  - {name} ({slug}) - {status}")

            # Check foreign key constraints
            cur.execute("""
                SELECT COUNT(*)
                FROM information_schema.table_constraints
                WHERE constraint_type = 'FOREIGN KEY'
                AND table_name IN ('subscriptions', 'payment_transactions')
            """)
            fk_count = cur.fetchone()[0]

            print_success(f"Found {fk_count} foreign key constraint(s) on subscriptions and payment_transactions")

            # Check RLS is enabled
            cur.execute("""
                SELECT relname, relrowsecurity
                FROM pg_class
                WHERE relname IN ('subscription_plans', 'subscriptions', 'payment_transactions')
                AND relnamespace = 'public'::regnamespace
            """)
            rls_status = cur.fetchall()

            for table_name, rls_enabled in rls_status:
                status = "enabled" if rls_enabled else "disabled"
                print_info(f"RLS on {table_name}: {status}")

            return True

    except Error as e:
        print_error(f"Verification failed: {e}")
        return False


def run_migrations():
    """Run all migrations in order."""
    print_header("Subscription Plans Migration")

    # Check environment variables
    print_info("Checking environment variables...")
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print_error(f"Missing environment variables: {', '.join(missing_vars)}")
        print_info("Please set the following environment variables:")
        for var in required_vars:
            print(f"  - {var}")
        sys.exit(1)

    print_success("All environment variables are set")

    # Connect to database
    print_info("Connecting to database...")
    conn = get_db_connection()
    print_success("Connected to database")

    # Display migration plan
    print_info("Migration plan:")
    for i, (description, _) in enumerate(MIGRATIONS, 1):
        print(f"  {i}. {description}")

    # Ask for confirmation
    print_warning("\nThis will modify your database schema.")
    response = input("Do you want to proceed? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print_info("Migration cancelled by user")
        conn.close()
        sys.exit(0)

    # Execute migrations
    print_header("Executing Migrations")
    success_count = 0
    failed_migrations = []

    for description, migration_file in MIGRATIONS:
        print(f"\n{Colors.BOLD}Step: {description}{Colors.ENDC}")
        print("-" * 70)
        migration_name = Path(migration_file).stem

        # Check if already applied
        if check_migration_applied(conn, migration_name):
            print_warning("Migration already applied, skipping...")
            success_count += 1
            continue

        # Execute migration
        start_time = time.time()
        success = execute_migration(conn, migration_file, migration_name)
        elapsed_time = time.time() - start_time

        if success:
            print_success(f"Completed in {elapsed_time:.2f} seconds")
            success_count += 1
        else:
            print_error(f"Failed after {elapsed_time:.2f} seconds")
            failed_migrations.append((description, migration_file))
            break

    # Summary
    print_header("Migration Summary")

    total_migrations = len(MIGRATIONS)

    if success_count == total_migrations:
        print_success(f"All {total_migrations} migration(s) completed successfully!")

        # Verify migration
        if verify_migration(conn):
            print_success("Migration verification passed")
        else:
            print_warning("Migration verification failed, but migration was applied")

        conn.close()
        print_header("Migration Complete")
        print_success("You can now use the new subscription plans schema")
        sys.exit(0)
    else:
        print_error(f"Migration failed: {success_count}/{total_migrations} completed")

        if failed_migrations:
            print_error("\nFailed migrations:")
            for description, migration_file in failed_migrations:
                print(f"  - {description} ({migration_file})")

        conn.close()
        print_header("Migration Failed")
        print_error("Please review the errors above and fix any issues")
        print_info("You may need to manually rollback or fix the database state")
        sys.exit(1)


def main():
    """Main entry point."""
    try:
        run_migrations()
    except KeyboardInterrupt:
        print_warning("\nMigration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

Subscription Plans Migration Runner

This script executes the subscription plans migration to:
1. Drop the old subscription_plans table
2. Create the archive table structure with appropriate constraints
3. Migrate any existing data into the new schema
4. Update foreign keys in subscriptions and payment_transactions tables
5. Fix duplicate subscription plans and infinite recursion
6. Apply comprehensive security fixes

Usage:
    python run_subscription_migration.py

Environment Variables:
    DB_HOST - Database host (default: localhost)
    DB_PORT - Database port (default: 5432)
    DB_NAME - Database name (default: postgres)
    DB_USER - Database user (default: postgres)
    DB_PASSWORD - Database password (required)
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Tuple

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Migration files to execute in order
MIGRATIONS: List[Tuple[str, str]] = [
    ("Drop old table and adopt archive schema", "supabase/migrations/20260130_drop_old_table_adopt_archive_schema.sql"),
    ("Fix duplicate subscription plans and infinite recursion", "supabase/migrations/20260130_fix_duplicate_subscription_plans.sql"),
    ("Apply comprehensive security fixes", "supabase/migrations/20260130_comprehensive_security_fixes.sql"),
]

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Error as e:
        print_error(f"Failed to connect to database: {e}")
        sys.exit(1)


def check_migration_applied(conn, migration_name: str) -> bool:
    """Check if a migration has already been applied."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM supabase_migrations.schema_migrations
                    WHERE version = %s
                )
            """, (migration_name,))
            return cur.fetchone()[0]
    except Error:
        # If schema_migrations table doesn't exist, assume not applied
        return False


def record_migration(conn, migration_name: str):
    """Record that a migration has been applied."""
    try:
        with conn.cursor() as cur:
            # Ensure schema_migrations table exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS supabase_migrations.schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)

            # Record the migration
            cur.execute("""
                INSERT INTO supabase_migrations.schema_migrations (version)
                VALUES (%s)
                ON CONFLICT (version) DO NOTHING
            """, (migration_name,))
    except Error as e:
        print_warning(f"Could not record migration: {e}")


def execute_migration(conn, migration_file: str, migration_name: str) -> bool:
    """Execute a migration SQL file."""
    migration_path = Path(migration_file)

    if not migration_path.exists():
        print_error(f"Migration file not found: {migration_file}")
        return False

    print_info(f"Reading migration file: {migration_file}")

    try:
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print_info(f"Executing migration ({len(sql_content)} characters)...")

        with conn.cursor() as cur:
            cur.execute(sql_content)

        # Record the migration
        record_migration(conn, migration_name)

        print_success("Migration executed successfully")
        return True

    except Error as e:
        print_error(f"Migration failed: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def verify_migration(conn) -> bool:
    """Verify that the migration was successful."""
    print_info("Verifying migration...")

    try:
        with conn.cursor() as cur:
            # Check if subscription_plans table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'subscription_plans'
                )
            """)
            table_exists = cur.fetchone()[0]

            if not table_exists:
                print_error("subscription_plans table does not exist")
                return False

            print_success("subscription_plans table exists")

            # Check if we have the expected plans
            cur.execute("""
                SELECT name, slug, is_active
                FROM public.subscription_plans
                ORDER BY sort_order
            """)
            plans = cur.fetchall()

            if len(plans) == 0:
                print_warning("No subscription plans found")
            else:
                print_success(f"Found {len(plans)} subscription plan(s):")
                for name, slug, is_active in plans:
                    status = "active" if is_active else "inactive"
                    print(f"  - {name} ({slug}) - {status}")

            # Check foreign key constraints
            cur.execute("""
                SELECT COUNT(*)
                FROM information_schema.table_constraints
                WHERE constraint_type = 'FOREIGN KEY'
                AND table_name IN ('subscriptions', 'payment_transactions')
            """)
            fk_count = cur.fetchone()[0]

            print_success(f"Found {fk_count} foreign key constraint(s) on subscriptions and payment_transactions")

            # Check RLS is enabled
            cur.execute("""
                SELECT relname, relrowsecurity
                FROM pg_class
                WHERE relname IN ('subscription_plans', 'subscriptions', 'payment_transactions')
                AND relnamespace = 'public'::regnamespace
            """)
            rls_status = cur.fetchall()

            for table_name, rls_enabled in rls_status:
                status = "enabled" if rls_enabled else "disabled"
                print_info(f"RLS on {table_name}: {status}")

            return True

    except Error as e:
        print_error(f"Verification failed: {e}")
        return False


def run_migrations():
    """Run all migrations in order."""
    print_header("Subscription Plans Migration")

    # Check environment variables
    print_info("Checking environment variables...")
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print_error(f"Missing environment variables: {', '.join(missing_vars)}")
        print_info("Please set the following environment variables:")
        for var in required_vars:
            print(f"  - {var}")
        sys.exit(1)

    print_success("All environment variables are set")

    # Connect to database
    print_info("Connecting to database...")
    conn = get_db_connection()
    print_success("Connected to database")

    # Display migration plan
    print_info("Migration plan:")
    for i, (description, _) in enumerate(MIGRATIONS, 1):
        print(f"  {i}. {description}")

    # Ask for confirmation
    print_warning("\nThis will modify your database schema.")
    response = input("Do you want to proceed? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print_info("Migration cancelled by user")
        conn.close()
        sys.exit(0)

    # Execute migrations
    print_header("Executing Migrations")
    success_count = 0
    failed_migrations = []

    for description, migration_file in MIGRATIONS:
        print(f"\n{Colors.BOLD}Step: {description}{Colors.ENDC}")
        print("-" * 70)
        migration_name = Path(migration_file).stem

        # Check if already applied
        if check_migration_applied(conn, migration_name):
            print_warning("Migration already applied, skipping...")
            success_count += 1
            continue

        # Execute migration
        start_time = time.time()
        success = execute_migration(conn, migration_file, migration_name)
        elapsed_time = time.time() - start_time

        if success:
            print_success(f"Completed in {elapsed_time:.2f} seconds")
            success_count += 1
        else:
            print_error(f"Failed after {elapsed_time:.2f} seconds")
            failed_migrations.append((description, migration_file))
            break

    # Summary
    print_header("Migration Summary")

    total_migrations = len(MIGRATIONS)

    if success_count == total_migrations:
        print_success(f"All {total_migrations} migration(s) completed successfully!")

        # Verify migration
        if verify_migration(conn):
            print_success("Migration verification passed")
        else:
            print_warning("Migration verification failed, but migration was applied")

        conn.close()
        print_header("Migration Complete")
        print_success("You can now use the new subscription plans schema")
        sys.exit(0)
    else:
        print_error(f"Migration failed: {success_count}/{total_migrations} completed")

        if failed_migrations:
            print_error("\nFailed migrations:")
            for description, migration_file in failed_migrations:
                print(f"  - {description} ({migration_file})")

        conn.close()
        print_header("Migration Failed")
        print_error("Please review the errors above and fix any issues")
        print_info("You may need to manually rollback or fix the database state")
        sys.exit(1)


def main():
    """Main entry point."""
    try:
        run_migrations()
    except KeyboardInterrupt:
        print_warning("\nMigration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

Subscription Plans Migration Runner

This script executes the subscription plans migration to:
1. Drop the old subscription_plans table
2. Create the archive table structure with appropriate constraints
3. Migrate any existing data into the new schema
4. Update foreign keys in subscriptions and payment_transactions tables
5. Fix duplicate subscription plans and infinite recursion
6. Apply comprehensive security fixes

Usage:
    python run_subscription_migration.py

Environment Variables:
    DB_HOST - Database host (default: localhost)
    DB_PORT - Database port (default: 5432)
    DB_NAME - Database name (default: postgres)
    DB_USER - Database user (default: postgres)
    DB_PASSWORD - Database password (required)
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Tuple

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Migration files to execute in order
MIGRATIONS: List[Tuple[str, str]] = [
    ("Drop old table and adopt archive schema", "supabase/migrations/20260130_drop_old_table_adopt_archive_schema.sql"),
    ("Fix duplicate subscription plans and infinite recursion", "supabase/migrations/20260130_fix_duplicate_subscription_plans.sql"),
    ("Apply comprehensive security fixes", "supabase/migrations/20260130_comprehensive_security_fixes.sql"),
]

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Error as e:
        print_error(f"Failed to connect to database: {e}")
        sys.exit(1)


def check_migration_applied(conn, migration_name: str) -> bool:
    """Check if a migration has already been applied."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM supabase_migrations.schema_migrations
                    WHERE version = %s
                )
            """, (migration_name,))
            return cur.fetchone()[0]
    except Error:
        # If schema_migrations table doesn't exist, assume not applied
        return False


def record_migration(conn, migration_name: str):
    """Record that a migration has been applied."""
    try:
        with conn.cursor() as cur:
            # Ensure schema_migrations table exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS supabase_migrations.schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)

            # Record the migration
            cur.execute("""
                INSERT INTO supabase_migrations.schema_migrations (version)
                VALUES (%s)
                ON CONFLICT (version) DO NOTHING
            """, (migration_name,))
    except Error as e:
        print_warning(f"Could not record migration: {e}")


def execute_migration(conn, migration_file: str, migration_name: str) -> bool:
    """Execute a migration SQL file."""
    migration_path = Path(migration_file)

    if not migration_path.exists():
        print_error(f"Migration file not found: {migration_file}")
        return False

    print_info(f"Reading migration file: {migration_file}")

    try:
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        print_info(f"Executing migration ({len(sql_content)} characters)...")

        with conn.cursor() as cur:
            cur.execute(sql_content)

        # Record the migration
        record_migration(conn, migration_name)

        print_success("Migration executed successfully")
        return True

    except Error as e:
        print_error(f"Migration failed: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def verify_migration(conn) -> bool:
    """Verify that the migration was successful."""
    print_info("Verifying migration...")

    try:
        with conn.cursor() as cur:
            # Check if subscription_plans table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'subscription_plans'
                )
            """)
            table_exists = cur.fetchone()[0]

            if not table_exists:
                print_error("subscription_plans table does not exist")
                return False

            print_success("subscription_plans table exists")

            # Check if we have the expected plans
            cur.execute("""
                SELECT name, slug, is_active
                FROM public.subscription_plans
                ORDER BY sort_order
            """)
            plans = cur.fetchall()

            if len(plans) == 0:
                print_warning("No subscription plans found")
            else:
                print_success(f"Found {len(plans)} subscription plan(s):")
                for name, slug, is_active in plans:
                    status = "active" if is_active else "inactive"
                    print(f"  - {name} ({slug}) - {status}")

            # Check foreign key constraints
            cur.execute("""
                SELECT COUNT(*)
                FROM information_schema.table_constraints
                WHERE constraint_type = 'FOREIGN KEY'
                AND table_name IN ('subscriptions', 'payment_transactions')
            """)
            fk_count = cur.fetchone()[0]

            print_success(f"Found {fk_count} foreign key constraint(s) on subscriptions and payment_transactions")

            # Check RLS is enabled
            cur.execute("""
                SELECT relname, relrowsecurity
                FROM pg_class
                WHERE relname IN ('subscription_plans', 'subscriptions', 'payment_transactions')
                AND relnamespace = 'public'::regnamespace
            """)
            rls_status = cur.fetchall()

            for table_name, rls_enabled in rls_status:
                status = "enabled" if rls_enabled else "disabled"
                print_info(f"RLS on {table_name}: {status}")

            return True

    except Error as e:
        print_error(f"Verification failed: {e}")
        return False


def run_migrations():
    """Run all migrations in order."""
    print_header("Subscription Plans Migration")

    # Check environment variables
    print_info("Checking environment variables...")
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print_error(f"Missing environment variables: {', '.join(missing_vars)}")
        print_info("Please set the following environment variables:")
        for var in required_vars:
            print(f"  - {var}")
        sys.exit(1)

    print_success("All environment variables are set")

    # Connect to database
    print_info("Connecting to database...")
    conn = get_db_connection()
    print_success("Connected to database")

    # Display migration plan
    print_info("Migration plan:")
    for i, (description, _) in enumerate(MIGRATIONS, 1):
        print(f"  {i}. {description}")

    # Ask for confirmation
    print_warning("\nThis will modify your database schema.")
    response = input("Do you want to proceed? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print_info("Migration cancelled by user")
        conn.close()
        sys.exit(0)

    # Execute migrations
    print_header("Executing Migrations")
    success_count = 0
    failed_migrations = []

    for description, migration_file in MIGRATIONS:
        print(f"\n{Colors.BOLD}Step: {description}{Colors.ENDC}")
        print("-" * 70)
        migration_name = Path(migration_file).stem

        # Check if already applied
        if check_migration_applied(conn, migration_name):
            print_warning("Migration already applied, skipping...")
            success_count += 1
            continue

        # Execute migration
        start_time = time.time()
        success = execute_migration(conn, migration_file, migration_name)
        elapsed_time = time.time() - start_time

        if success:
            print_success(f"Completed in {elapsed_time:.2f} seconds")
            success_count += 1
        else:
            print_error(f"Failed after {elapsed_time:.2f} seconds")
            failed_migrations.append((description, migration_file))
            break

    # Summary
    print_header("Migration Summary")

    total_migrations = len(MIGRATIONS)

    if success_count == total_migrations:
        print_success(f"All {total_migrations} migration(s) completed successfully!")

        # Verify migration
        if verify_migration(conn):
            print_success("Migration verification passed")
        else:
            print_warning("Migration verification failed, but migration was applied")

        conn.close()
        print_header("Migration Complete")
        print_success("You can now use the new subscription plans schema")
        sys.exit(0)
    else:
        print_error(f"Migration failed: {success_count}/{total_migrations} completed")

        if failed_migrations:
            print_error("\nFailed migrations:")
            for description, migration_file in failed_migrations:
                print(f"  - {description} ({migration_file})")

        conn.close()
        print_header("Migration Failed")
        print_error("Please review the errors above and fix any issues")
        print_info("You may need to manually rollback or fix the database state")
        sys.exit(1)


def main():
    """Main entry point."""
    try:
        run_migrations()
    except KeyboardInterrupt:
        print_warning("\nMigration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
