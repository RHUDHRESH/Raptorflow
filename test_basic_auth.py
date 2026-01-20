import urllib.request
import base64
import os

url = "https://selected-lemming-36956.upstash.io/ping"
token = "AZBcAAInCDF3MTZ1NzY3YjE4NjY6dM1yYm=jNTVmk8H1MTU1ZWF1NNAx!2YSNTY"

# Try Basic Auth
auth_str = f"default:{token}"
encoded_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')

headers = {
    "Authorization": f"Basic {encoded_auth}"
}

print(f"Trying Basic Auth...")

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        body = response.read().decode('utf-8')
        print(f"✅ SUCCESS! Response: {body}")
except Exception as e:
    print(f"❌ FAILED: {e}")
