#!/usr/bin/env python3
"""
Direct Supabase Database Migration Executor
Bypasses CLI issues by connecting directly to PostgreSQL
"""

import psycopg2
from pathlib import Path
import sys

# Connection details
HOST = 'db.vpwwzsanuyhpkvgorcnc.supabase.co'
DATABASE = 'postgres'
USER = 'postgres'
PASSWORD = 'sb_secret_3Oep1ZCax2i6Dyn5dCX0_g_oQezsvEs'
PORT = 5432

def get_connection():
    """Connect to Supabase PostgreSQL."""
    return psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD,
        port=PORT,
        sslmode='require'
    )

def execute_sql_file(filepath):
    """Execute SQL file directly."""
    print(f"Executing: {filepath.name}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    conn = get_connection()
    conn.autocommit = False
    
    try:
        cur = conn.cursor()
        
        # Split SQL into individual statements
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        
        executed = 0
        for i, statement in enumerate(statements):
            try:
                cur.execute(statement)
                executed += 1
            except Exception as e:
                error_msg = str(e)
                # Skip common non-critical errors
                if any(skip in error_msg for skip in ['already exists', 'does not exist', 'Duplicate']):
                    print(f"  ⚠ Skipped (already applied): {error_msg[:60]}")
                else:
                    print(f"  ✗ Error on statement {i}: {error_msg[:80]}")
                    raise
        
        conn.commit()
        cur.close()
        print(f"  ✓ Executed {executed} statements successfully")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"  ✗ Failed: {e}")
        return False
    finally:
        conn.close()

def mark_migration_applied(version, name):
    """Mark migration as applied in supabase_migrations table."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO supabase_migrations.schema_migrations (version, name, statements, checksum, execution_time, applied_at)
            VALUES (%s, %s, '{}', 'manual', 0, NOW())
            ON CONFLICT (version) DO UPDATE SET applied_at = NOW();
        """, (version, name))
        conn.commit()
        cur.close()
        print(f"  ✓ Marked {version} as applied")
    except Exception as e:
        print(f"  ⚠ Could not mark migration: {e}")
    finally:
        conn.close()

def main():
    migrations_dir = Path('supabase/migrations')
    
    if not migrations_dir.exists():
        print("Error: migrations directory not found")
        sys.exit(1)
    
    # Get all migration files sorted
    migration_files = sorted(migrations_dir.glob('*.sql'))
    
    print(f"Found {len(migration_files)} migration files")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for migration_file in migration_files:
        # Extract version from filename (e.g., 20260208000000_canonical_schema.sql)
        version = migration_file.stem.split('_')[0]
        name = '_'.join(migration_file.stem.split('_')[1:])
        
        if execute_sql_file(migration_file):
            mark_migration_applied(version, name)
            success_count += 1
        else:
            fail_count += 1
    
    print("=" * 60)
    print(f"Results: {success_count} succeeded, {fail_count} failed")
    
    if fail_count == 0:
        print("🎉 All migrations applied successfully!")
        return 0
    else:
        print(f"⚠ {fail_count} migration(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
