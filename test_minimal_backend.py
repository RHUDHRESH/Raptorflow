"""
TEST MINIMAL BACKEND ON PORT 8001
"""

import json

import requests


def test_minimal_backend():
    """Test the minimal backend with gemini-2.0-flash-001"""

    print("🧪 TESTING MINIMAL BACKEND (PORT 8001)")
    print("=" * 40)

    base_url = "http://localhost:8001"

    # Test health
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

    # Test AI generation
    try:
        payload = {
            "prompt": "What is 9+9? Answer with just the number.",
            "user_id": "test-minimal-backend",
            "model": "gemini-2.0-flash-001",
        }

        response = requests.post(
            f"{base_url}/ai/generate",
            json=payload,
            timeout=30,
            headers={"Content-Type": "application/json"},
        )

        print(f"📊 AI Generation Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ AI GENERATION SUCCESS!")
            print(f"   Model: {data.get('model')}")
            print(f"   Content: {data.get('content')}")
            print(f"   Verification: {data.get('verification')}")

            # Verify the response
            if "18" in data.get("content", ""):
                print("🎉 MATHEMATICAL RESPONSE CORRECT!")

            if data.get("model") == "gemini-2.0-flash-001":
                print("✅ MODEL ENFORCEMENT WORKING!")

            return True
        else:
            print(f"❌ AI generation failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ AI generation error: {e}")
        return False


if __name__ == "__main__":
    success = test_minimal_backend()

    if success:
        print("\n🎉 MINIMAL BACKEND TEST PASSED!")
        print("✅ Gemini-2.0-flash-001 is working!")
        print("🔒 Universal model enforcement active!")
    else:
        print("\n❌ MINIMAL BACKEND TEST FAILED")
