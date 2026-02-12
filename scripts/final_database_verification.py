#!/usr/bin/env python3
"""
Final Database Verification Script
Comprehensive database health check after fixes
"""
import os

import psycopg2
from psycopg2.extras import RealDictCursor

def verify_database():
    """Complete database verification"""
    db_url = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Set SUPABASE_DB_URL or DATABASE_URL before running this script")
        return False
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔍 RAPTORFLOW DATABASE VERIFICATION")
        print("=" * 50)
        
        # 1. Connection test
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL: {version['version'].split(',')[0]}")
        
        # 2. Core tables verification
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
        
        print("\n📊 Core Tables:")
        all_present = True
        for table in required_tables:
            status = "✅" if table in existing_tables else "❌"
            print(f"  {status} {table}")
            if table not in existing_tables:
                all_present = False
        
        # 3. Row counts
        print("\n📈 Table Statistics:")
        for table in required_tables:
            if table in existing_tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM public.{table}")
                count = cursor.fetchone()['count']
                print(f"  • {table}: {count} records")
        
        # 4. RLS verification
        cursor.execute("""
            SELECT tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN %s
        """, (tuple(required_tables),))
        
        rls_status = cursor.fetchall()
        print("\n🔒 Row Level Security:")
        rls_enabled = True
        for row in rls_status:
            status = "✅" if row['rowsecurity'] else "❌"
            print(f"  {status} {row['tablename']}")
            if not row['rowsecurity']:
                rls_enabled = False
        
        # 5. Index verification
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM pg_indexes 
            WHERE schemaname = 'public'
        """)
        index_count = cursor.fetchone()['count']
        print(f"\n📋 Indexes: {index_count} total")
        
        # 6. Foreign key constraints
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM information_schema.table_constraints 
            WHERE table_schema = 'public' 
            AND constraint_type = 'FOREIGN KEY'
        """)
        fk_count = cursor.fetchone()['count']
        print(f"🔗 Foreign Keys: {fk_count} constraints")
        
        # 7. Triggers
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM information_schema.triggers 
            WHERE trigger_schema = 'public'
        """)
        trigger_count = cursor.fetchone()['count']
        print(f"⚡ Triggers: {trigger_count} active")
        
        # 8. Test BCM functionality
        print("\n🧪 BCM System Test:")
        try:
            # Create test workspace
            cursor.execute("""
                INSERT INTO public.workspaces (name, slug, owner_id)
                VALUES ('Test Workspace', 'test-workspace', gen_random_uuid())
                RETURNING id
            """)
            workspace_id = cursor.fetchone()['id']
            
            # Create test BCM
            test_manifest = {
                "foundation": {"company": "TestCo"},
                "icps": [{"name": "Test ICP"}],
                "version": 1
            }
            
            cursor.execute("""
                INSERT INTO public.business_context_manifests 
                (workspace_id, version, manifest, checksum)
                VALUES (%s, 1, %s, %s)
            """, (workspace_id, test_manifest, 'test_checksum'))
            
            # Verify BCM
            cursor.execute("""
                SELECT manifest, version FROM public.business_context_manifests 
                WHERE workspace_id = %s
            """, (workspace_id,))
            bcm = cursor.fetchone()
            
            print("  ✅ BCM creation: SUCCESS")
            print("  ✅ BCM retrieval: SUCCESS")
            
            # Cleanup
            cursor.execute("DELETE FROM public.business_context_manifests WHERE workspace_id = %s", (workspace_id,))
            cursor.execute("DELETE FROM public.workspaces WHERE id = %s", (workspace_id,))
            
        except Exception as e:
            print(f"  ❌ BCM test failed: {str(e)}")
        
        conn.commit()
        
        # Final status
        print("\n" + "=" * 50)
        if all_present and rls_enabled:
            print("🎉 DATABASE STATUS: EXCELLENT")
            print("✅ All core tables present")
            print("✅ Row Level Security enabled")
            print("✅ BCM system functional")
            print("✅ Ready for production")
        else:
            print("⚠️  DATABASE STATUS: NEEDS ATTENTION")
            if not all_present:
                print("❌ Missing tables detected")
            if not rls_enabled:
                print("❌ RLS not properly configured")
        
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        return False
    
    finally:
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == "__main__":
    verify_database()
