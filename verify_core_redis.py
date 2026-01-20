import asyncio
import os
import sys

# Add current directory to sys.path
sys.path.append(os.getcwd())

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Load environment
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

# Manually override to be sure
os.environ["UPSTASH_REDIS_URL"] = "https://selected-lemming-36956.upstash.io"
os.environ["UPSTASH_REDIS_TOKEN"] = "AZBcAAInCDF3MTZ1NzY3YjE4NjY6dM1yYm=jNTVmk8H1MTU1ZWF1NNAx!2YSNTY"

from backend.redis_core.client import get_redis

async def verify():
    print("Testing backend.redis_core.client...")
    try:
        redis = get_redis()
        # Ping is async in RedisClient
        is_ready = await redis.ping()
        print(f"Ping result: {is_ready}")
        
        if is_ready:
            print("\n✅ REDIS IS READY!")
        else:
            # Try to get more info by calling the async client directly
            print("Ping failed, checking async_client directly...")
            try:
                raw_ping = await redis.async_client.ping()
                print(f"Raw ping: {raw_ping}")
            except Exception as inner_e:
                print(f"Inner error: {inner_e}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
