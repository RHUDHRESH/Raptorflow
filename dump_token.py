import base64
import os

def get_token_from_env(path):
    with open(path, 'r') as f:
        for line in f:
            if 'UPSTASH_REDIS_TOKEN=' in line:
                return line.split('=', 1)[1].strip()
    return None

token = get_token_from_env('frontend/.env.local')
if token:
    print(f"Token found: [{token}]")
    b64_token = base64.b64encode(token.encode('utf-8')).decode('utf-8')
    print(f"Base64 Token: {b64_token}")
else:
    print("Token not found in frontend/.env.local")
