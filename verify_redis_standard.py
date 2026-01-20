import redis
import os

# Load manually to be sure
url = "rediss://default:AYmZAAIncDEwNDA0NjczMDU4OTk0NTc1YTBlNGQ0NzUzZWFjNWI0MXAxMzUyMjU@patient-goshawk-35225.upstash.io:6379"

print(f"Connecting to Redis via redis:// protocol...")

try:
    r = redis.from_url(url)
    print("Sending PING...")
    response = r.ping()
    print(f"Response: {response}")
    
    if response:
        print("\n✅ UPSTASH REDIS IS READY (STANDARD PROTOCOL)!")
    else:
        print("\n❌ REDIS PING FAILED.")
        
except Exception as e:
    print(f"\n❌ FAILED TO TALK TO REDIS: {e}")
