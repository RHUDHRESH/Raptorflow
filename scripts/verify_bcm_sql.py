import psycopg2
from pprint import pprint
import os

def verify_bcm_structure():
    """Verify the BCM table structure matches requirements"""
    try:
        db_url = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("Set SUPABASE_DB_URL or DATABASE_URL before running this script")

        conn = psycopg2.connect(db_url)
        
        with conn.cursor() as cur:
            # 1. Check table structure
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'business_context_manifests'
            """)
            print("\n=== Table Structure ===")
            pprint(cur.fetchall())
            
            # 2. Check indexes
            cur.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'business_context_manifests'
            """)
            print("\n=== Indexes ===")
            pprint(cur.fetchall())
            
            # 3. Check RLS policies
            cur.execute("""
                SELECT policyname, cmd, permissive, roles, qual
                FROM pg_policies
                WHERE tablename = 'business_context_manifests'
            """)
            print("\n=== Row-Level Security Policies ===")
            pprint(cur.fetchall())
            
            # 4. Check sample data
            cur.execute("SELECT * FROM business_context_manifests LIMIT 1")
            print("\n=== Sample Data ===")
            pprint(cur.fetchone())
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"Verification failed: {e}")
        return False

if __name__ == "__main__":
    verify_bcm_structure()
