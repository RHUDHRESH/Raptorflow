import requests

# Test single request
try:
    payload = {
        "prompt": "What is 2+2?",
        "user_id": "test",
        "model": "gemini-2.0-flash-001",
    }

    response = requests.post(
        "http://localhost:8002/ai/generate",
        json=payload,
        timeout=15,
        headers={"Content-Type": "application/json"},
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Content: {data.get('content')}")
        print(f"Model: {data.get('model')}")
        print(f"Rate Limiting: {data.get('rate_limiting')}")
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Exception: {e}")
