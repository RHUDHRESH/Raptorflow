import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Load env manually
def load_env(env_path):
    if not os.path.exists(env_path):
        return
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

load_env('backend/.env')

# Manually set the REST URL and TOKEN since upstash_client uses them
os.environ["UPSTASH_REDIS_REST_URL"] = "https://patient-goshawk-35225.upstash.io"
os.environ["UPSTASH_REDIS_REST_TOKEN"] = "AYmZAAIncDEwNDA0NjczMDU4OTk0NTc1YTBlNGQ0NzUzZWFjNWI0MXAxMzUyMjU"

from services.upstash_client import UpstashClient

async def verify():
    print("Initializing UpstashClient...")
    try:
        client = UpstashClient()
        print(f"Connecting to: {client.config.rest_url}")
        
        # Performance health check
        print("Running health_check()...")
        health = await client.health_check()
        print(f"Health Status: {health}")
        
        if health.get("status") == "healthy":
            print("\n✅ UPSTASH REDIS IS READY AND RESPONDING!")
        else:
            print("\n❌ UPSTASH REDIS IS UNHEALTHY.")
            
    except Exception as e:
        print(f"\n❌ ERROR DURING VERIFICATION: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
