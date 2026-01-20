import urllib.request
import os

token = "AZBcAAInCDF3MTZ1NzY3YjE4NjY6dM1yYm=jNTVmk8H1MTU1ZWF1NNAx!2YSNTY"
url = f"https://selected-lemming-36956.upstash.io/ping?_token={token}"

print(f"Trying token as query param...")

try:
    with urllib.request.urlopen(url) as response:
        body = response.read().decode('utf-8')
        print(f"✅ SUCCESS! Response: {body}")
except Exception as e:
    print(f"❌ FAILED: {e}")
