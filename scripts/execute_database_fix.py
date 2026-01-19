#!/usr/bin/env python3
"""
Execute Database Fix Script
"""
import psycopg2
import sys

def execute_fix():
    # Read the final fix script
    with open('database_fix_final.sql', 'r') as f:
        sql_script = f.read()
    
    # Connect to database
    conn = psycopg2.connect(
        host='db.vpwwzsanuyhpkvgorcnc.supabase.co',
        port=5432,
        database='postgres',
        user='postgres',
        password='XByYHcmc9KqxaVln'
    )
    
    try:
        cursor = conn.cursor()
        cursor.execute(sql_script)
        conn.commit()
        print('✅ Database fix executed successfully')
        
        # Get verification results
        cursor.execute("""
            SELECT 'DATABASE FIX COMPLETED SUCCESSFULLY' as status,
                   (SELECT COUNT(*) FROM public.profiles) as profiles_count,
                   (SELECT COUNT(*) FROM public.workspaces) as workspaces_count,
                   (SELECT COUNT(*) FROM public.business_context_manifests) as bcm_count
        """)
        result = cursor.fetchone()
        print(f"📊 Results: {result}")
        
    except Exception as e:
        print(f'❌ Error: {e}')
        conn.rollback()
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    execute_fix()
