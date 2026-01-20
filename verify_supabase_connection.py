import os
from supabase import create_client, Client

url: str = "https://vpwwzsanuyhpkvgorcnc.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw"

def verify_supabase():
    print(f"Connecting to Supabase at {url}...")
    try:
        supabase: Client = create_client(url, key)
        # Try to list some tables or just a simple query
        response = supabase.table("users").select("count", count="exact").limit(1).execute()
        print(f"✅ Supabase connection successful!")
        print(f"Users count (test): {response.count}")
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")

if __name__ == "__main__":
    verify_supabase()
