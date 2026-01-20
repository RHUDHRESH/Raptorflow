import redis
import os

# Load manually to be sure
url = "redis://default:AZBcAAInCDF3MTZ1NzY3YjE4NjY6dM1yYm=jNTVmk8H1MTU1ZWF1NNAx!2YSNTY@selected-lemming-36956.upstash.io:6379"

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
