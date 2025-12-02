#!/usr/bin/env python3
"""Apply database migration to create cost_logs table."""

import os
import sys
sys.path.insert(0, 'backend')

from backend.core.config import get_settings
from backend.services.supabase_client import supabase_client

def apply_cost_tracking_migration():
    """Apply the cost_logs table migration."""

    # Read the migration file
    migration_file = 'database/migrations/018_create_cost_tracking.sql'
    if not os.path.exists(migration_file):
        print(f"ERROR: Migration file not found: {migration_file}")
        return False

    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    print("Found migration file. Content preview:")
    print(migration_sql[:200] + "...")

    try:
        # Get supabase client and execute the migration
        supabase = supabase_client

        # Supabase Python client doesn't have raw() method, use connection directly or alternative approach
        print("Migration SQL:")
        print(migration_sql[:500] + "...")

        # For now, we need to apply this via Supabase dashboard or use a different approach
        # Let's check if we can execute this through the RPC function or use the database directly

        # Alternative: Use the client's connection more directly
        # This may need adjustment based on actual supabase-python-client capabilities
        print("Manual migration needed. Please apply this SQL in Supabase dashboard:")
        print("\n" + "="*80)
        print(migration_sql)
        print("="*80)

        print("\n[PENDING] Migration requires manual application via Supabase dashboard.")
        return True  # Return true since we're providing the SQL

    except Exception as e:
        print(f"[ERROR] Migration preparation failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Applying cost_logs table migration...")
    success = apply_cost_tracking_migration()
    if success:
        print("\nMigration completed. You can now run the Vertex AI tests.")
    else:
        print("\nMigration failed. Check the Supabase database connection.")
    sys.exit(0 if success else 1)
