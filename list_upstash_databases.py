import urllib.request
import base64
import json

email = "rhudhreshr@gmail.com"
api_key = "98bd4162-e2fb-480d-b3c9-8591932b707c"

auth_str = f"{email}:{api_key}"
encoded_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')

url = "https://api.upstash.com/v2/redis/databases"

headers = {
    "Authorization": f"Basic {encoded_auth}"
}

print(f"Fetching Upstash databases...")

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        body = response.read().decode('utf-8')
        data = json.loads(body)
        print(f"✅ SUCCESS! Found {len(data)} databases.")
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f"❌ FAILED: {e}")
