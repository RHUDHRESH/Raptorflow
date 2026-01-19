import os
import psycopg2

DATABASE_URL = "postgresql://postgres.vpwwzsanuyhpkvgorcnc:1IMRvR6WC3kbRvp4@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

def reset_status():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True  # Force autocommit
        cur = conn.cursor()
        
        email = "rhudhresh3697@gmail.com"
        
        print(f"Checking current status for {email}...")
        cur.execute("SELECT onboarding_status FROM users WHERE email = %s;", (email,))
        before = cur.fetchone()
        print(f"Status BEFORE: {before[0] if before else 'NOT FOUND'}")
        
        print(f"Resetting status to 'pending_plan_selection'...")
        cur.execute("UPDATE users SET onboarding_status = 'pending_plan_selection' WHERE email = %s RETURNING onboarding_status;", (email,))
        after = cur.fetchone()
        print(f"Status AFTER: {after[0] if after else 'UPDATE FAILED'}")
        
        # Verify
        cur.execute("SELECT onboarding_status FROM users WHERE email = %s;", (email,))
        verify = cur.fetchone()
        print(f"Verification: {verify[0] if verify else 'NOT FOUND'}")
        
        cur.close()
        conn.close()
        
        if verify and verify[0] == 'pending_plan_selection':
            print("SUCCESS: Status confirmed as 'pending_plan_selection'.")
        else:
            print("ERROR: Status verification failed!")
        
    except Exception as e:
        print(f"ERROR: Reset failed: {e}")

if __name__ == "__main__":
    reset_status()
