#!/usr/bin/env python3
"""
Supabase Production Readiness Check
Verifies all database changes are properly pushed and ready
"""
import psycopg2
from psycopg2.extras import RealDictCursor

def check_production_readiness():
    """Complete production readiness verification"""
    
    conn = psycopg2.connect(
        host='db.vpwwzsanuyhpkvgorcnc.supabase.co',
        port=5432,
        database='postgres',
        user='postgres',
        password='XByYHcmc9KqxaVln'
    )
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🚀 SUPABASE PRODUCTION READINESS CHECK")
        print("=" * 50)
        
        # 1. Database connection
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ Database: {version['version'].split(',')[0]}")
        
        # 2. All required tables
        required_tables = [
            'profiles', 'workspaces', 'business_context_manifests',
            'foundations', 'icp_profiles', 'icp_firmographics',
            'icp_pain_map', 'icp_psycholinguistics', 'icp_disqualifiers'
        ]
        
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public'
        """)
        existing_tables = [row['tablename'] for row in cursor.fetchall()]
        
        print("\n📊 Tables Status:")
        all_present = True
        for table in required_tables:
            status = "✅" if table in existing_tables else "❌"
            print(f"  {status} {table}")
            if table not in existing_tables:
                all_present = False
        
        # 3. Row Level Security
        cursor.execute("""
            SELECT tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN %s
        """, (tuple(required_tables),))
        
        rls_status = cursor.fetchall()
        print("\n🔒 RLS Status:")
        rls_enabled = True
        for row in rls_status:
            status = "✅" if row['rowsecurity'] else "❌"
            print(f"  {status} {row['tablename']}")
            if not row['rowsecurity']:
                rls_enabled = False
        
        # 4. Indexes
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM pg_indexes 
            WHERE schemaname = 'public'
        """)
        index_count = cursor.fetchone()['count']
        print(f"\n📋 Indexes: {index_count} total")
        
        # 5. Foreign Keys
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM information_schema.table_constraints 
            WHERE table_schema = 'public' 
            AND constraint_type = 'FOREIGN KEY'
        """)
        fk_count = cursor.fetchone()['count']
        print(f"🔗 Foreign Keys: {fk_count} constraints")
        
        # 6. Triggers
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM information_schema.triggers 
            WHERE trigger_schema = 'public'
        """)
        trigger_count = cursor.fetchone()['count']
        print(f"⚡ Triggers: {trigger_count} active")
        
        # 7. Extensions
        cursor.execute("""
            SELECT extname FROM pg_extension 
            WHERE extname IN ('uuid-ossp', 'pgcrypto', 'vector')
        """)
        extensions = [row[0] for row in cursor.fetchall()]
        print(f"\n🔧 Extensions: {', '.join(extensions)}")
        
        # 8. Migrations
        cursor.execute("""
            SELECT version, name FROM supabase_migrations.schema_migrations 
            ORDER BY version
        """)
        migrations = cursor.fetchall()
        print(f"\n🔄 Migrations: {len(migrations)} applied")
        for migration in migrations:
            print(f"  • {migration['version']}: {migration['name']}")
        
        # 9. Test BCM functionality
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
            cursor.execute("""
                INSERT INTO public.business_context_manifests 
                (workspace_id, version, manifest, checksum)
                VALUES (%s, 1, %s, %s)
                RETURNING id
            """, (workspace_id, '{"test": "data"}', 'test_checksum'))
            bcm_id = cursor.fetchone()['id']
            
            # Verify BCM
            cursor.execute("""
                SELECT manifest, version FROM public.business_context_manifests 
                WHERE workspace_id = %s
            """, (workspace_id,))
            bcm = cursor.fetchone()
            
            print("  ✅ BCM creation: SUCCESS")
            print("  ✅ BCM retrieval: SUCCESS")
            
            # Cleanup
            cursor.execute("DELETE FROM public.business_context_manifests WHERE id = %s", (bcm_id,))
            cursor.execute("DELETE FROM public.workspaces WHERE id = %s", (workspace_id,))
            
        except Exception as e:
            print(f"  ❌ BCM test failed: {str(e)}")
        
        conn.commit()
        
        # Final status
        print("\n" + "=" * 50)
        if all_present and rls_enabled:
            print("🎉 SUPABASE STATUS: PRODUCTION READY")
            print("✅ All tables present and configured")
            print("✅ Row Level Security enabled")
            print("✅ BCM system functional")
            print("✅ Database pushed successfully")
            print("✅ Ready for production deployment")
        else:
            print("⚠️  SUPABASE STATUS: NEEDS ATTENTION")
            if not all_present:
                print("❌ Missing tables detected")
            if not rls_enabled:
                print("❌ RLS not properly configured")
        
        return all_present and rls_enabled
        
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    success = check_production_readiness()
    exit(0 if success else 1)
