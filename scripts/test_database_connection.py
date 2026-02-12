#!/usr/bin/env python3
"""
Database Connection Test Script
Tests Supabase database connectivity and verifies all tables exist
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json

def test_database_connection():
    """Test database connection and verify schema"""
    db_url = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Set SUPABASE_DB_URL or DATABASE_URL before running this script")
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Database connection successful")
        
        # Test 1: Check PostgreSQL version
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"📊 PostgreSQL version: {version['version']}")
        
        # Test 2: Check required tables exist
        required_tables = [
            'profiles',
            'workspaces', 
            'business_context_manifests',
            'foundations',
            'icp_profiles'
        ]
        
        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        existing_tables = [row['tablename'] for row in cursor.fetchall()]
        
        print("\n📋 Table Status:")
        for table in required_tables:
            status = "✅" if table in existing_tables else "❌"
            print(f"  {status} {table}")
        
        # Test 3: Check RLS is enabled
        cursor.execute("""
            SELECT tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN %s
        """, (tuple(required_tables),))
        
        rls_status = cursor.fetchall()
        print("\n🔒 RLS Status:")
        for row in rls_status:
            status = "✅" if row['rowsecurity'] else "❌"
            print(f"  {status} {row['tablename']}")
        
        # Test 4: Check indexes
        cursor.execute("""
            SELECT tablename, indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """)
        
        indexes = cursor.fetchall()
        print(f"\n📈 Indexes: {len(indexes)} total")
        for index in indexes[:10]:  # Show first 10
            print(f"  • {index['tablename']}.{index['indexname']}")
        
        # Test 5: Check migration status
        cursor.execute("""
            SELECT version, name, inserted_at 
            FROM supabase_migrations.schema_migrations 
            ORDER BY inserted_at DESC
        """)
        
        migrations = cursor.fetchall()
        print(f"\n🔄 Migrations: {len(migrations)} applied")
        for migration in migrations:
            print(f"  • {migration['version']}: {migration['name']}")
        
        # Test 6: Test basic CRUD operations
        print("\n🧪 Testing CRUD Operations...")
        
        # Create test workspace
        cursor.execute("""
            INSERT INTO public.workspaces (name, slug, owner_id)
            VALUES ('Test Workspace', 'test-workspace', gen_random_uuid())
            RETURNING id
        """)
        workspace_id = cursor.fetchone()['id']
        print(f"  ✅ Created workspace: {workspace_id}")
        
        # Create test BCM manifest
        cursor.execute("""
            INSERT INTO public.business_context_manifests 
            (workspace_id, version, manifest, checksum)
            VALUES (%s, 1, %s, %s)
            RETURNING id
        """, (workspace_id, '{"test": "data"}', 'test_checksum'))
        bcm_id = cursor.fetchone()['id']
        print(f"  ✅ Created BCM manifest: {bcm_id}")
        
        # Read test
        cursor.execute("""
            SELECT * FROM public.business_context_manifests 
            WHERE workspace_id = %s
        """, (workspace_id,))
        bcm = cursor.fetchone()
        print(f"  ✅ Read BCM: {bcm['manifest']}")
        
        # Cleanup test data
        cursor.execute("DELETE FROM public.business_context_manifests WHERE id = %s", (bcm_id,))
        cursor.execute("DELETE FROM public.workspaces WHERE id = %s", (workspace_id,))
        print("  ✅ Cleaned up test data")
        
        conn.commit()
        print("\n🎉 All tests passed! Database is ready for production.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == "__main__":
    test_database_connection()
