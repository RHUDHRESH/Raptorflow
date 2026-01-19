import os
import json
import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account
import requests
from pathlib import Path

def test_fresh_token():
    sa_path = Path("raptorflow-storage-key.json")
    if not sa_path.exists():
        print("❌ SA key not found")
        return

    print(f"🔑 Using SA: {sa_path}")
    
    try:
        creds = service_account.Credentials.from_service_account_file(
            str(sa_path),
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        token = creds.token
        print(f"✅ Fresh token generated (length: {len(token)})")
    except Exception as e:
        print(f"❌ Token refresh failed: {e}")
        return

    project_id = creds.project_id
    location = "us-central1"
    model = "gemini-2.0-flash-exp"

    print(f"🧪 Testing REST with fresh token for {model}")
    url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:streamGenerateContent"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [{
            "parts": [{"text": "Hello"}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"✅ SUCCESS! Inference confirmed.")
            # print(response.text[:200])
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text[:500])
    except Exception as e:
        print(f"❌ Error: {e}")

    return False

if __name__ == "__main__":
    test_fresh_token()
