"""
MODEL AVAILABILITY TEST
Check what Gemini models are actually available
"""

import os
import sys


def test_available_models():
    """Test what Gemini models are available"""
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel

        print("🔍 Testing available Gemini models...")

        # Get credentials
        project_id = os.getenv("GCP_PROJECT_ID", "raptorflow-481505")
        region = os.getenv("GCP_REGION", "us-central1")

        print(f"📋 Project ID: {project_id}")
        print(f"📍 Region: {region}")

        # Initialize Vertex AI
        print("🚀 Initializing Vertex AI...")
        vertexai.init(project=project_id, location=region)
        print("✅ Vertex AI initialized successfully!")

        # Test different model names
        models_to_test = [
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash-001",
            "gemini-1.5-flash-002",
            "gemini-1.5-pro",
            "gemini-pro",
            "gemini-1.0-pro",
        ]

        working_models = []

        for model_name in models_to_test:
            print(f"\n🤖 Testing model: {model_name}")
            try:
                model = GenerativeModel(model_name)
                # Try a simple generation
                response = model.generate_content("Say 'hello'")
                print(f"✅ {model_name} WORKS! Response: {response.text[:50]}")
                working_models.append(model_name)
            except Exception as e:
                print(f"❌ {model_name} failed: {str(e)[:100]}")

        print(f"\n🎉 WORKING MODELS: {working_models}")

        if working_models:
            print(f"\n✅ RECOMMENDED UNIVERSAL MODEL: {working_models[0]}")
            return working_models[0]
        else:
            print("\n❌ NO MODELS WORKING - Check project access and API key")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    test_available_models()
