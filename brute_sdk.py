import asyncio
import os
from upstash_redis.asyncio import Redis

url = "https://patient-goshawk-35225.upstash.io"
base_token = "AYmZAAIncDEwNDA0NjczMDU4OTk0NTc1YTBlNGQ0NzUzZWFjNWI0MXAxMzUyMjU"

async def test_token(token):
    print(f"Testing token: [{token}]")
    try:
        redis = Redis(url=url, token=token)
        response = await redis.ping()
        print(f"✅ SUCCESS! Response: {response}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

async def run():
    tokens = [
        base_token,
        base_token.strip(),
    ]
    
    for t in tokens:
        if await test_token(t):
            break

if __name__ == "__main__":
    asyncio.run(run())
