import asyncio
import os
from upstash_redis.asyncio import Redis

url = "https://selected-lemming-36956.upstash.io"
base_token = "AZBcAAInCDF3MTZ1NzY3YjE4NjY6dM1yYm=jNTVmk8H1MTU1ZWF1NNAx!2YSNTY"

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
        base_token.replace("!", ""),
        base_token.replace("=", ""),
        base_token.replace("!", "").replace("=", ""),
        "AZBcAAInCDF3MTZ1NzY3YjE4NjY6dM1yYm=jNTVmk8H1MTU1ZWF1NNAx%212YSNTY",
        "AZBcAAInCDF3MTZ1NzY3YjE4NjY6dM1yYm%3DjNTVmk8H1MTU1ZWF1NNAx!2YSNTY",
    ]
    
    for t in tokens:
        if await test_token(t):
            break

if __name__ == "__main__":
    asyncio.run(run())
