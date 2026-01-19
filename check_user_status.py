import os
import psycopg2

DATABASE_URL = "postgresql://postgres.vpwwzsanuyhpkvgorcnc:1IMRvR6WC3kbRvp4@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

def check_status():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Checking users table...")
        cur.execute("SELECT id, email, onboarding_status FROM users;")
        rows = cur.fetchall()
        
        if not rows:
            print("No users found.")
        else:
            print(f"Found {len(rows)} users:")
            for row in rows:
                print(f" - ID: {row[0]}")
                print(f"   Email: {row[1]}")
                print(f"   Status: {row[2]}")
                
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: Database check failed: {e}")

if __name__ == "__main__":
    check_status()
