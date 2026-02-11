import urllib.request
import os

token = "AYmZAAIncDEwNDA0NjczMDU4OTk0NTc1YTBlNGQ0NzUzZWFjNWI0MXAxMzUyMjU"
url = f"https://patient-goshawk-35225.upstash.io/ping?_token={token}"

print(f"Trying token as query param...")

try:
    with urllib.request.urlopen(url) as response:
        body = response.read().decode('utf-8')
        print(f"✅ SUCCESS! Response: {body}")
except Exception as e:
    print(f"❌ FAILED: {e}")
