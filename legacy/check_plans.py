import os
import psycopg2

DATABASE_URL = "postgresql://postgres.vpwwzsanuyhpkvgorcnc:1IMRvR6WC3kbRvp4@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

def check_plans():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Checking for 'plans' table...")
        cur.execute("SELECT to_regclass('public.plans');")
        result = cur.fetchone()
        
        if not result or not result[0]:
            print("ERROR: Table 'public.plans' does NOT exist.")
        else:
            print("Table 'public.plans' exists. Checking record count...")
            cur.execute("SELECT count(*) FROM plans;")
            count = cur.fetchone()[0]
            print(f"Record count: {count}")
            
            if count == 0:
                print("WARNING: Table is empty.")
            else:
                print("SUCCESS: Table has data.")
                
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: Database check failed: {e}")

if __name__ == "__main__":
    check_plans()
