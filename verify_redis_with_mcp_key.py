import redis
import os

url = "rediss://default:AYmZAAIncDEwNDA0NjczMDU4OTk0NTc1YTBlNGQ0NzUzZWFjNWI0MXAxMzUyMjU@patient-goshawk-35225.upstash.io:6379"

print(f"Connecting to Redis at {url.split('@')[-1]}...")

try:
    r = redis.from_url(url, socket_timeout=5)
    print("Sending PING...")
    response = r.ping()
    if response:
        print("✅ SUCCESS! Redis replied PONG.")
    else:
        print("❌ FAILED: Redis did not reply PONG.")
except Exception as e:
    print(f"❌ ERROR: {e}")
