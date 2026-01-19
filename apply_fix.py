import os
import psycopg2

DATABASE_URL = "postgresql://postgres.vpwwzsanuyhpkvgorcnc:1IMRvR6WC3kbRvp4@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

def apply_fix():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Read the SQL file
        with open('fix_rls_correctly.sql', 'r') as f:
            sql_content = f.read()
            
        print("Executing SQL fix...")
        cur.execute(sql_content)
        conn.commit()
        
        print("SUCCESS: PLans table fix applied successfully!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: Failed to apply fix: {e}")
        # Print more details if it's a specific PG error
        if hasattr(e, 'pgcode'):
            print(f"PG Code: {e.pgcode}")
            print(f"PG Error: {e.pgerror}")

if __name__ == "__main__":
    apply_fix()
