import psycopg2
import sys

# Testing the direct connection via pooler host but on port 5432
db_config = {
    'host': 'aws-1-ap-south-1.pooler.supabase.com',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres.vpwwzsanuyhpkvgorcnc',
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
