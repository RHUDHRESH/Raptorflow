from google import genai
import os
from pathlib import Path

def test_genai_sdk():
    # Manually parse .env
    env_path = Path(".env")
    api_key = None
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                if "VERTEX_AI_API_KEY=" in line:
                    api_key = line.split("=")[1].strip().replace('"', '').replace("'", "")
                    break
    
    if not api_key:
        print("❌ No API key found")
        return

    print(f"🔑 Using Key: {api_key[:10]}...")

    models = ["gemini-2.0-flash-exp", "gemini-2.0-flash", "gemini-1.5-flash"]

    for model_name in models:
        print(f"\n🧪 Testing model: {model_name}")
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model_name,
                contents="Hello, respond with 'OK' if you work."
            )
            if response and response.text:
                print(f"✅ Success! Response: {response.text.strip()}")
                return model_name
        except Exception as e:
            print(f"❌ Failed: {str(e)[:200]}")

    return None

if __name__ == "__main__":
    test_genai_sdk()

