import urllib.request
import os

url = "https://selected-lemming-36956.upstash.io/ping"
raw_token = "AZBcAAInCDF3MTZ1NzY3YjE4NjY6dM1yYm=jNTVmk8H1MTU1ZWF1NNAx!2YSNTY"

variations = [
    raw_token,
    raw_token.strip(),
    raw_token.replace(" ", ""),
    "AZBcAAInCDF3MTZ1NzY3YjE4NjY6dM1yYm=jNTVmk8H1MTU1ZWF1NNAx", # Removed !2YSNTY
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
