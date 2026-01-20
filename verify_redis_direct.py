import urllib.request
import json
import os

url = "https://patient-goshawk-35225.upstash.io/ping"
token = "AYmZAAIncDEwNDA0NjczMDU4OTk0NTc1YTBlNGQ0NzUzZWFjNWI0MXAxMzUyMjU"

headers = {
    "Authorization": f"Bearer {token}"
}

print(f"Connecting to Upstash Redis at {url}...")

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        status_code = response.getcode()
        body = response.read().decode('utf-8')
        
        print(f"Status Code: {status_code}")
        print(f"Response Body: {body}")
        
        if body == '{"result":"PONG"}':
            print("\n✅ UPSTASH REDIS IS READY AND RESPONDING!")
        else:
            print("\n⚠️ UNEXPECTED RESPONSE FROM REDIS.")
            
except Exception as e:
    print(f"\n❌ FAILED TO TALK TO REDIS: {e}")
