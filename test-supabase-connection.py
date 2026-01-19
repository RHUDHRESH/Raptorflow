import os
from supabase import create_client
from dotenv import load_dotenv

# Use the key from apply-migrations.js
SUPABASE_URL = 'https://vpwwzsanuyhpkvgorcnc.supabase.co'
SUPABASE_SERVICE_ROLE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw'

def test_connection():
    print(f"🔗 Connecting to {SUPABASE_URL}...")
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # Test basic query
        print("🔍 Testing basic query (users table)...")
        result = supabase.table("users").select("id").limit(1).execute()
        print(f"✅ Connection successful!")
        
        # Test exec_sql RPC
        print("🔍 Testing exec_sql RPC...")
        try:
            rpc_result = supabase.rpc("exec_sql", {"sql_query": "SELECT 1"}).execute()
            print("✅ exec_sql(sql_query) exists!")
        except Exception as e:
            print(f"⚠️ exec_sql(sql_query) failed: {e}")
            
            try:
                rpc_result = supabase.rpc("exec_sql", {"sql": "SELECT 1"}).execute()
                print("✅ exec_sql(sql) exists!")
            except Exception as e2:
                print(f"⚠️ exec_sql(sql) failed: {e2}")
                
                try:
                    rpc_result = supabase.rpc("execute_sql", {"query": "SELECT 1"}).execute()
                    print("✅ execute_sql(query) exists!")
                except Exception as e3:
                    print(f"❌ All standard SQL execution RPCs failed.")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()