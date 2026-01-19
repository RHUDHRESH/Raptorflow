import os
import google.generativeai as genai
from pathlib import Path

def test_models():
    # Manually parse .env to be sure
    env_path = Path(".env")
    api_key = None
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                if "VERTEX_AI_API_KEY=" in line:
                    api_key = line.split("=")[1].strip()
                    break
    
    if not api_key:
        print("❌ Still no API key found after manual parse")
        return

    print(f"🔑 Using API Key: {api_key[:10]}...{api_key[-5:]}")
    
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"❌ genai.configure failed: {e}")
        return

    models_to_test = [
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash",
        "gemini-2.0-flash-001",
        "gemini-1.5-flash"
    ]

    for model_name in models_to_test:
        print(f"\n🧪 Testing model: {model_name}")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello")
            if response and response.text:
                print(f"✅ Success! Response: {response.text.strip()[:50]}...")
                return model_name
        except Exception as e:
            # Print specifically if it's an auth error
            if "API key not valid" in str(e) or "403" in str(e):
                print(f"❌ Auth/Permission Error: {str(e)[:100]}")
            else:
                print(f"❌ Error: {str(e)[:100]}")

    return None

if __name__ == "__main__":
    test_models()