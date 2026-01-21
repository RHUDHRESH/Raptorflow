import psycopg2
import sys

# Testing the direct connection from execute_database_fix.py
db_config = {
    'host': 'db.vpwwzsanuyhpkvgorcnc.supabase.co',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'XByYHcmc9KqxaVln'
}

def test_conn():
    try:
        conn = psycopg2.connect(**db_config)
        print("✅ Connection successful!")
        cur = conn.cursor()
        cur.execute("SELECT current_user, current_database();")
        res = cur.fetchone()
        print(f"User: {res[0]}, DB: {res[1]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_conn()
