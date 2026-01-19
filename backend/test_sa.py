import os
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account
from pathlib import Path

def test_sa():
    sa_path = Path("raptorflow-storage-key.json")
    if not sa_path.exists():
        print("❌ Service account key not found")
        return

    print(f"🔑 Using Service Account: {sa_path}")

    try:
        creds = service_account.Credentials.from_service_account_file(str(sa_path))
        vertexai.init(project=creds.project_id, location="us-central1", credentials=creds)
        print(f"🆔 Project ID: {creds.project_id}")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
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
    test_sa()
