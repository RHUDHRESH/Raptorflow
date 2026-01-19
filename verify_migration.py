import requests
import json

# Supabase configuration
supabase_url = "https://vpwwzsanuyhpkvgorcnc.supabase.co"
service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw"

def verify_migration():
    headers = {
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "apikey": service_key
    }
    
    print("Verifying migration...")
    
    # Check if profiles table exists by trying to query it
    try:
        response = requests.get(
            f"{supabase_url}/rest/v1/profiles",
            headers=headers,
            params={"select": "count", "limit": "1"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Profiles table exists and is accessible!")
            print(f"Response: {data}")
            return True
        elif response.status_code == 404:
            print("❌ Profiles table not found (404)")
            print("Migration may not have been actually executed")
            return False
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")
        return False

def check_schema_info():
    # Try to get information about the profiles table
    headers = {
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "apikey": service_key
    }
    
    print("\nChecking schema information...")
    
    # Try to query information_schema
    try:
        response = requests.post(
            f"{supabase_url}/rest/v1/rpc/get_table_info",
            headers=headers,
            json={"table_name": "profiles"}
        )
        
        if response.status_code == 200:
            print(f"Schema info: {response.json()}")
        else:
            print(f"Could not get schema info: {response.status_code}")
            
    except Exception as e:
        print(f"Error getting schema info: {e}")

if __name__ == "__main__":
    success = verify_migration()
    if success:
        check_schema_info()
    else:
        print("\n⚠️ Migration verification failed!")
        print("You may need to run the SQL manually in the Supabase SQL Editor:")
        print("https://app.supabase.com/project/vpwwzsanuyhpkvgorcnc/sql")
