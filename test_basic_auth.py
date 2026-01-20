import urllib.request
import base64
import os

url = "https://patient-goshawk-35225.upstash.io/ping"
token = "AYmZAAIncDEwNDA0NjczMDU4OTk0NTc1YTBlNGQ0NzUzZWFjNWI0MXAxMzUyMjU"

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
