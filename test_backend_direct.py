import json

import requests

# Test backend directly
backend_url = "http://localhost:8000"

# Test health
try:
    response = requests.get(f"{backend_url}/health", timeout=5)
    print(f"Backend health: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Backend health failed: {e}")

# Test AI endpoint
try:
    payload = {
        "prompt": "What is 2+2? Answer with just the number.",
        "user_id": "test-verification",
        "model": "gemini-1.5-flash",
    }

    response = requests.post(
        f"{backend_url}/ai/generate",
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json"},
    )

    print(f"\nAI Endpoint Status: {response.status_code}")
    print(f"Response: {response.text}")

    if response.status_code == 200:
        data = response.json()
        print(f"Model used: {data.get('model')}")
        print(f"Content: {data.get('content')}")
        print(f"Usage logged: {data.get('usage_logged')}")

except Exception as e:
    print(f"AI endpoint failed: {e}")
