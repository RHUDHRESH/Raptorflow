import psycopg2
import json

db_url = "postgresql://postgres.vpwwzsanuyhpkvgorcnc:1IMRvR6WC3kbRvp4@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

def query_db():
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        print("Connected to database.")
        
        # List all tables
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cur.fetchall()
        print(f"Tables: {[t[0] for table in tables for t in [table]]}")
        
        # Check system_settings if it exists
        table_names = [t[0] for t in tables]
        if 'system_settings' in table_names:
            print("\n--- system_settings ---")
            cur.execute("SELECT * FROM system_settings")
            rows = cur.fetchall()
            for row in rows:
                print(row)
        
        # Check any other interesting tables
        for table in ['api_keys', 'secrets', 'config', 'credentials']:
            if table in table_names:
                print(f"\n--- {table} ---")
                cur.execute(f"SELECT * FROM {table}")
                rows = cur.fetchall()
                for row in rows:
                    print(row)
                    
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    query_db()
