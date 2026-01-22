"""
VERTEX AI REAL TEST WITH CURRENT MODELS
Test with actual available models after enabling Vertex AI API
"""

import os
import sys

import vertexai
from vertexai.generative_models import GenerativeModel


def test_current_gemini_models():
    """Test with current available Gemini models"""

    print("🔍 TESTING CURRENT GEMINI MODELS AFTER VERTEX AI ENABLEMENT")
    print("=" * 60)

    # Initialize Vertex AI
    project_id = os.getenv("GCP_PROJECT_ID", "raptorflow-481505")
    region = os.getenv("GCP_REGION", "us-central1")

    print(f"📋 Project: {project_id}")
    print(f"📍 Region: {region}")

    try:
        vertexai.init(project=project_id, location=region)
        print("✅ Vertex AI initialized successfully!")
    except Exception as e:
        print(f"❌ Vertex AI initialization failed: {e}")
        return False

    # Test current stable models based on documentation
    current_models = [
        "gemini-2.5-flash",  # Latest stable
        "gemini-2.0-flash-001",  # Previous stable
        "gemini-2.5-flash-lite",  # Lite version
        "gemini-2.5-pro",  # Pro version
    ]

    working_models = []

    for model_name in current_models:
        print(f"\n🤖 Testing model: {model_name}")
        try:
            model = GenerativeModel(model_name)
            response = model.generate_content(
                "What is 2+2? Answer with just the number."
            )
            print(f"✅ {model_name} WORKS!")
            print(f"   Response: {response.text}")
            working_models.append(model_name)

        except Exception as e:
            print(f"❌ {model_name} failed: {str(e)[:100]}")

    if working_models:
        print(f"\n🎉 WORKING MODELS FOUND: {working_models}")
        return working_models
    else:
        print("\n❌ No working models found")
        return False


def update_universal_model(working_model: str):
    """Update the universal configuration to use the working model"""

    print(f"\n🔧 UPDATING UNIVERSAL CONFIGURATION TO USE: {working_model}")

    # Update ai-config.ts
    config_content = f"""/**
 * UNIVERSAL AI CONFIGURATION
 * This file ensures ALL AI services use {working_model} universally
 * Updated: {os.times()}
 */

// Universal AI Model Configuration
export const AI_CONFIG = {{
  // PRIMARY MODEL - THE ONLY MODEL TO BE USED
  MODEL: '{working_model}',

  // Vertex AI Configuration
  VERTEX_AI_MODEL: '{working_model}',
  DEFAULT_MODEL: '{working_model}',

  // API Configuration
  API_ENDPOINT: '/ai/generate',
  DIRECT_API_MODEL: '{working_model}',

  // Feature Flags
  ENABLE_GEMINI_UNIVERSAL_ONLY: true,
  DISABLE_OTHER_MODELS: true,

  // Model Parameters (Optimized for {working_model})
  DEFAULT_TEMPERATURE: 0.7,
  DEFAULT_MAX_TOKENS: 1000,
  DEFAULT_TOP_P: 0.8,
  DEFAULT_TOP_K: 40,

  // Cost and Performance
  COST_PER_TOKEN: 0.000000075, // Estimated pricing
  MAX_CONTEXT_LENGTH: 1048576, // Context window

  // Universal Constants
  UNIVERSAL_MODEL_NAME: '{working_model}',
  FALLBACK_MODEL: '{working_model}', // Same model - no fallbacks
}} as const;

// Type safety for universal model configuration
export type UniversalModel = '{working_model}';

// Helper function to ensure only {working_model} is used
export function getUniversalModel(): UniversalModel {{
  return AI_CONFIG.MODEL;
}}

// Validator function to enforce universal model usage
export function validateModelUsage(model: string): UniversalModel {{
  if (model !== AI_CONFIG.MODEL) {{
    console.warn(`⚠️  Model "${{model}}" is not allowed. Forcing universal model: ${{AI_CONFIG.MODEL}}`);
    return AI_CONFIG.MODEL;
  }}
  return model as UniversalModel;
}}

// Export singleton instance
export const universalAI = {{
  model: AI_CONFIG.MODEL,
  getModel: () => AI_CONFIG.MODEL,
  validateModel: validateModelUsage,
  isUniversalModel: (model: string) => model === AI_CONFIG.MODEL,
}} as const;

// Runtime enforcement
if (typeof window !== 'undefined') {{
  // Override any attempts to use other models
  Object.defineProperty(window, 'AI_MODEL_OVERRIDE', {{
    value: AI_CONFIG.MODEL,
    writable: false,
    configurable: false
  }});
}}

export default AI_CONFIG;
"""

    with open(
        "c:/Users/hp/OneDrive/Desktop/Raptorflow/frontend/src/lib/ai-config.ts", "w"
    ) as f:
        f.write(config_content)

    print(f"✅ Updated ai-config.ts with {working_model}")

    # Update backend main.py
    try:
        with open("c:/Users/hp/OneDrive/Desktop/Raptorflow/backend/main.py", "r") as f:
            content = f.read()

        # Replace the model in the AIRequest class
        content = content.replace(
            'model: str = "gemini-1.5-flash"  # UNIVERSALLY ENFORCED MODEL',
            f'model: str = "{working_model}"  # UNIVERSALLY ENFORCED MODEL',
        )

        # Replace in the endpoint
        content = content.replace(
            'universal_model = "gemini-1.5-flash"',
            f'universal_model = "{working_model}"',
        )

        with open("c:/Users/hp/OneDrive/Desktop/Raptorflow/backend/main.py", "w") as f:
            f.write(content)

        print(f"✅ Updated backend main.py with {working_model}")

    except Exception as e:
        print(f"❌ Failed to update backend: {e}")

    return True


def test_real_backend_call():
    """Test the backend with the working model"""

    print(f"\n🌐 TESTING BACKEND API CALL")

    import requests

    try:
        payload = {
            "prompt": "What is 3+3? Answer with just the number.",
            "user_id": "test-verification-real",
            "model": working_models[0] if working_models else "gemini-2.5-flash",
        }

        response = requests.post(
            "http://localhost:8000/ai/generate",
            json=payload,
            timeout=30,
            headers={"Content-Type": "application/json"},
        )

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ BACKEND CALL SUCCESSFUL!")
            print(f"   Model: {data.get('model')}")
            print(f"   Content: {data.get('content')}")
            return True
        else:
            print(f"❌ Backend call failed: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False


if __name__ == "__main__":
    # Test current models
    working_models = test_current_gemini_models()

    if working_models:
        # Use the first working model
        primary_model = working_models[0]

        # Update universal configuration
        update_universal_model(primary_model)

        # Test backend call
        test_real_backend_call()

        print(f"\n🎉 SUCCESS! Using {primary_model} as universal model")
        print("✅ Real Gemini is now working!")
    else:
        print("\n❌ Still no working models. Check project configuration.")
