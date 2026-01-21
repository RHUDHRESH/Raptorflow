import psycopg2
import sys

db_url = "postgresql://postgres.vpwwzsanuyhpkvgorcnc:1IMRvR6WC3kbRvp4@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

def test_conn():
    try:
        conn = psycopg2.connect(db_url)
        print("✅ Connection successful!")
        cur = conn.cursor()
        cur.execute("SELECT current_user, current_database();")
        res = cur.fetchone()
        print(f"User: {res[0]}, DB: {res[1]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_conn()
