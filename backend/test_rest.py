import os
import requests
import json
from pathlib import Path

def test_rest():
    env_path = Path(".env")
    token = None
    project_id = None
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                if "VERTEX_AI_API_KEY=" in line:
                    token = line.split("=")[1].strip().replace('"', '').replace("'", "")
                if "VERTEX_AI_PROJECT_ID=" in line:
                    project_id = line.split("=")[1].strip().replace('"', '').replace("'", "")
    
    if not token or not project_id:
        print("❌ Token or Project ID missing")
        return

    models = ["gemini-2.0-flash-exp", "gemini-2.0-flash-001", "gemini-1.5-flash"]
    location = "us-central1"

    for model in models:
        print(f"\n🧪 Testing REST for {model}")
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
                print(f"✅ Success! Response received.")
                # print(response.text[:200])
                return model
            else:
                print(f"❌ Failed: {response.status_code}")
                print(response.text[:200])
        except Exception as e:
            print(f"❌ Error: {e}")

    return None

if __name__ == "__main__":
    test_rest()
