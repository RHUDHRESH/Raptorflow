"""
CORRECT GEMINI API TEST
Test both Vertex AI and Generative AI endpoints with correct authentication
"""

import json
import os

import requests


def test_vertex_ai_endpoint():
    """Test Vertex AI endpoint with service account or OAuth"""

    print("🔍 Testing Vertex AI endpoint...")

    # The API key we have seems to be a Vertex AI key
    api_key = os.getenv("VERTEX_AI_API_KEY")
    if not api_key:
        print("❌ No API key")
        return False

    # Try Vertex AI REST API endpoint
    project_id = os.getenv("GCP_PROJECT_ID", "raptorflow-481505")
    region = os.getenv("GCP_REGION", "us-central1")

    # Vertex AI REST API endpoint
    url = f"https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/publishers/google/models/gemini-1.5-flash:generateContent"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "contents": [
            {"parts": [{"text": "What is 2+2? Answer with just the number."}]}
        ],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 10},
    }

    try:
        print(f"📡 Testing Vertex AI endpoint: {url}")
        response = requests.post(url, headers=headers, json=payload, timeout=15)

        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text[:500]}")

        if response.status_code == 200:
            data = response.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"✅ Vertex AI WORKS! Response: {content}")
                return True
        else:
            print(f"❌ Vertex AI failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Vertex AI exception: {e}")

    return False


def test_generative_ai_api_key():
    """Test if we need a different API key format"""

    print("\n🔍 Testing API key format...")

    api_key = os.getenv("VERTEX_AI_API_KEY")
    if not api_key:
        return False

    # Check if this looks like a Vertex AI key or Generative AI key
    if api_key.startswith("AQ."):
        print("🔑 This appears to be a Vertex AI API key")
        print(
            "💡 For direct Generative AI API, you need a different key from Google AI Studio"
        )
        print("🔗 Get one at: https://aistudio.google.com/app/apikey")
        return False
    elif len(api_key) > 30 and "." in api_key:
        print("🔑 This might be a Generative AI API key")
        return True
    else:
        print("❓ Unknown API key format")
        return False


def create_working_backend_test():
    """Create a working backend using the correct approach"""

    print("\n🛠️  Creating working backend test...")

    # Since we have Vertex AI access, let's use the Python SDK properly
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel

        project_id = os.getenv("GCP_PROJECT_ID", "raptorflow-481505")
        region = os.getenv("GCP_REGION", "us-central1")

        print(f"🚀 Initializing Vertex AI SDK...")
        vertexai.init(project=project_id, location=region)

        # Try to create the model
        try:
            model = GenerativeModel("gemini-1.5-flash")
            print("✅ Model creation succeeded")

            # Test generation
            response = model.generate_content(
                "What is 3+3? Answer with just the number."
            )
            print(f"✅ Generation succeeded: {response.text}")
            return True

        except Exception as e:
            print(f"❌ Model creation failed: {e}")

            # Try alternative model names
            alt_models = ["gemini-1.5-pro-latest", "gemini-pro-latest", "gemini-pro"]
            for model_name in alt_models:
                try:
                    print(f"🔄 Trying alternative: {model_name}")
                    model = GenerativeModel(model_name)
                    response = model.generate_content("Say 'hello'")
                    print(f"✅ {model_name} works: {response.text}")
                    return True
                except:
                    continue

    except Exception as e:
        print(f"❌ Vertex AI SDK failed: {e}")

    return False


if __name__ == "__main__":
    print("🧪 COMPREHENSIVE GEMINI API TEST")
    print("=" * 50)

    # Test 1: Check API key format
    test_generative_ai_api_key()

    # Test 2: Try Vertex AI REST endpoint
    test_vertex_ai_endpoint()

    # Test 3: Try Python SDK approach
    if create_working_backend_test():
        print("\n🎉 FOUND WORKING CONFIGURATION!")
    else:
        print("\n❌ Need to check API access and model availability")
