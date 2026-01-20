import urllib.request
import json
import os

url = "https://selected-lemming-36956.upstash.io/ping"
token = "AZBcAAInCDF3MTZ1NzY3YjE4NjY6dM1yYm=jNTVmk8H1MTU1ZWF1NNAx!2YSNTY"

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
