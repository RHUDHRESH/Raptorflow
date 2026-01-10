"""
DIRECT GEMINI API TEST
Test the real Google Generative AI API with the provided API key
"""

import json
import os

import requests


def test_direct_gemini_api():
    """Test direct Gemini API calls"""

    api_key = os.getenv("VERTEX_AI_API_KEY")
    if not api_key:
        print("❌ No VERTEX_AI_API_KEY found")
        return False

    print(f"🔑 API Key found: {api_key[:20]}...")
    print("🔍 Testing direct Gemini API...")

    # Test the real API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    payload = {
        "contents": [
            {"parts": [{"text": "What is 2+2? Answer with just the number."}]}
        ],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 10},
    }

    try:
        print("📡 Making API call...")
        response = requests.post(url, json=payload, timeout=15)

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ API CALL SUCCESSFUL!")

            if "candidates" in data and len(data["candidates"]) > 0:
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"🤖 Response: {content}")

                # Check if it's the expected answer
                if "4" in content:
                    print("✅ Correct mathematical response!")
                else:
                    print(f"⚠️  Unexpected response: {content}")

                # Test usage metadata
                if "usageMetadata" in data:
                    usage = data["usageMetadata"]
                    print(f"📈 Usage: {usage}")

                return True
            else:
                print("❌ No candidates in response")
                print(f"Response: {json.dumps(data, indent=2)}")
                return False

        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_model_override_with_direct_api():
    """Test that we can force gemini-1.5-flash in direct API calls"""

    api_key = os.getenv("VERTEX_AI_API_KEY")
    if not api_key:
        return False

    print("\n🔒 Testing model enforcement...")

    # Test with different model names (should all use gemini-1.5-flash)
    test_models = ["gemini-1.5-flash", "gemini-pro", "gpt-4"]

    for model in test_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

        payload = {
            "contents": [
                {"parts": [{"text": f"Testing with model {model}. Say 'hello'."}]}
            ]
        }

        try:
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if "candidates" in data:
                    content = data["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"✅ {model}: {content[:30]}...")
                else:
                    print(f"❌ {model}: No candidates")
            else:
                print(f"❌ {model}: {response.status_code} - {response.text[:50]}")

        except Exception as e:
            print(f"❌ {model}: Exception - {e}")


if __name__ == "__main__":
    print("🧪 DIRECT GEMINI API VERIFICATION")
    print("=" * 50)

    success = test_direct_gemini_api()

    if success:
        test_model_override_with_direct_api()
        print("\n🎉 DIRECT API WORKS - Gemini 1.5 Flash is REAL!")
    else:
        print("\n❌ DIRECT API FAILED - Check API key and access")
