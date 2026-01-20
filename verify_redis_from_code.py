import asyncio
import os
import sys

# Add backend to path so we can import redis_core
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def load_env(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value

load_env('backend/.env')

from redis_core.client import get_redis

async def verify():
    print("Initializing Redis Client...")
    try:
        redis = get_redis()
        print(f"Connecting to: {redis.url}")
        
        # Test PING
        print("Sending PING...")
        is_ready = await redis.ping()
        
        if is_ready:
            print("\n✅ UPSTASH REDIS IS READY AND RESPONDING!")
            
            # Test simple SET/GET
            await redis.set("verification_test", "ready", ex=60)
            val = await redis.get("verification_test")
            print(f"Test Key 'verification_test': {val}")
            
            if val == "ready":
                print("✅ REDIS READ/WRITE TEST PASSED!")
        else:
            print("\n❌ REDIS PING FAILED.")
            
    except Exception as e:
        print(f"\n❌ ERROR DURING VERIFICATION: {e}")

if __name__ == "__main__":
    asyncio.run(verify())
