import os
from google.oauth2 import credentials
import vertexai
from vertexai.generative_models import GenerativeModel
from pathlib import Path

def test_token():
    # Manually parse .env
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
        print("❌ Token or Project ID missing in .env")
        return

    print(f"🔑 Using Token: {token[:10]}...")
    print(f"🆔 Project ID: {project_id}")

    # Create credentials object from token
    creds = credentials.Credentials(token=token)

    try:
        vertexai.init(project=project_id, location="us-central1", credentials=creds)
    except Exception as e:
        print(f"❌ vertexai.init failed: {e}")
        return

    models_to_test = [
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash-001",
        "gemini-1.5-flash"
    ]

    for model_name in models_to_test:
        print(f"\n🧪 Testing model: {model_name}")
        try:
            model = GenerativeModel(model_name)
            response = model.generate_content("Hello")
            if response and response.text:
                print(f"✅ Success! Response: {response.text.strip()[:50]}...")
                return model_name
        except Exception as e:
            print(f"❌ Error: {str(e)[:200]}")

    return None

if __name__ == "__main__":
    test_token()
