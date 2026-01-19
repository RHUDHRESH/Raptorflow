import os
import psycopg2

DATABASE_URL = "postgresql://postgres.vpwwzsanuyhpkvgorcnc:1IMRvR6WC3kbRvp4@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

def check_billing_tables():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        tables = ['subscriptions', 'payments', 'audit_logs']
        for table in tables:
            cur.execute(f"SELECT to_regclass('public.{table}');")
            result = cur.fetchone()
            if result and result[0]:
                print(f"✅ Table 'public.{table}' exists.")
            else:
                print(f"❌ Table 'public.{table}' MISSING.")
                
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: Database check failed: {e}")

if __name__ == "__main__":
    check_billing_tables()
