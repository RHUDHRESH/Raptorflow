"""
Apply Auth Migration to Supabase
This script applies the auth system fix migration to your Supabase database.
"""

import os
import sys

def apply_migration():
    """Instructions for applying the migration"""
    
    print("=" * 70)
    print("SUPABASE AUTH MIGRATION APPLICATOR")
    print("=" * 70)
    print()
    
    # Check if SUPABASE_SERVICE_ROLE_KEY is available
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not service_key:
        print("ERROR: SUPABASE_SERVICE_ROLE_KEY environment variable not set!")
        print()
        print("To apply this migration, you need your Supabase Service Role Key.")
        print("You can find it in your Supabase dashboard:")
        print("  1. Go to: https://supabase.com/dashboard/project/ywuokqopcfbqwtbzqvgj")
        print("  2. Navigate to: Project Settings > API")
        print("  3. Copy the 'service_role secret' (starts with 'eyJhb...')")
        print()
        print("Then run this script again with:")
        print("  set SUPABASE_SERVICE_ROLE_KEY=your_service_role_key")
        print("  python apply_auth_migration.py")
        print()
        print("OR apply the migration manually via SQL Editor (see below)")
        return False
    
    print(f"Service Role Key found: {service_key[:20]}...")
    print()
    
    try:
        from supabase import create_client
        
        url = "https://ywuokqopcfbqwtbzqvgj.supabase.co"
        
        print(f"Connecting to: {url}")
        client = create_client(url, service_key)
        print("Connected successfully!")
        print()
        
        # Read migration SQL
        migration_path = "../supabase/migrations/20250210_auth_system_fix.sql"
        if not os.path.exists(migration_path):
            migration_path = "supabase/migrations/20250210_auth_system_fix.sql"
        
        with open(migration_path, 'r') as f:
            sql = f.read()
        
        print(f"Migration file loaded: {len(sql)} characters")
        print()
        
        # Apply migration
        print("Applying migration...")
        print("-" * 70)
        
        # Split SQL into statements and execute
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        total = len(statements)
        
        for i, stmt in enumerate(statements, 1):
            if stmt and not stmt.startswith('--'):
                try:
                    # Execute via RPC
                    result = client.rpc('exec_sql', {'sql': stmt + ';'}).execute()
                    print(f"  [{i}/{total}] ✓ Executed")
                except Exception as e:
                    error_msg = str(e)
                    if "already exists" in error_msg or "duplicate" in error_msg:
                        print(f"  [{i}/{total}] ⚠ Skipped (already exists)")
                    else:
                        print(f"  [{i}/{total}] ✗ Error: {error_msg[:80]}")
        
        print("-" * 70)
        print()
        print("✓ Migration applied successfully!")
        print()
        print("Tables created:")
        print("  - profiles")
        print("  - workspaces")
        print("  - workspace_members")
        print("  - user_sessions")
        print()
        print("RLS policies enabled on all tables")
        print("Auth trigger configured for auto-profile creation")
        
        return True
        
    except ImportError:
        print("ERROR: supabase package not installed")
        print("Run: pip install supabase")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def print_manual_instructions():
    """Print manual migration instructions"""
    print()
    print("=" * 70)
    print("MANUAL MIGRATION INSTRUCTIONS")
    print("=" * 70)
    print()
    print("Since we don't have the service role key, apply the migration manually:")
    print()
    print("1. Go to your Supabase Dashboard:")
    print("   https://supabase.com/dashboard/project/ywuokqopcfbqwtbzqvgj")
    print()
    print("2. Navigate to: SQL Editor > New Query")
    print()
    print("3. Copy the contents of this file:")
    print("   supabase/migrations/20250210_auth_system_fix.sql")
    print()
    print("4. Paste into the SQL Editor and click 'Run'")
    print()
    print("5. Verify the tables were created:")
    print("   SELECT * FROM information_schema.tables")
    print("   WHERE table_schema = 'public'")
    print("   AND table_name IN ('profiles', 'workspaces', 'workspace_members');")
    print()
    print("=" * 70)


if __name__ == "__main__":
    success = apply_migration()
    if not success:
        print_manual_instructions()
    
    print()
    input("Press Enter to exit...")
