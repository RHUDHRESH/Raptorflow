from upstash_redis import Redis
import os

url = "https://selected-lemming-36956.upstash.io"
token = "AZBcAAInCDF3MTZ1NzY3YjE4NjY6dM1yYm=jNTVmk8H1MTU1ZWF1NNAx!2YSNTY"

print(f"Connecting to {url} using upstash-redis library...")

try:
    redis = Redis(url=url, token=token)
    response = redis.ping()
    print(f"Response: {response}")
    
    if response:
        print("\n✅ UPSTASH REDIS IS READY!")
    else:
        print("\n❌ UPSTASH REDIS PING FAILED.")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
