from upstash_redis import Redis
import os

url = "https://patient-goshawk-35225.upstash.io"
token = "AYmZAAIncDEwNDA0NjczMDU4OTk0NTc1YTBlNGQ0NzUzZWFjNWI0MXAxMzUyMjU"

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
