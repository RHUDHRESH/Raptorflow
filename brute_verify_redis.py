import urllib.request
import os

url = "https://patient-goshawk-35225.upstash.io/ping"
raw_token = "AYmZAAIncDEwNDA0NjczMDU4OTk0NTc1YTBlNGQ0NzUzZWFjNWI0MXAxMzUyMjU"

variations = [
    raw_token,
    raw_token.strip(),
    raw_token.replace(" ", ""),
]

for token in variations:
    print(f"Trying token: [{token}]")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            print(f"✅ SUCCESS! Response: {body}")
            break
    except Exception as e:
        print(f"❌ FAILED: {e}")
