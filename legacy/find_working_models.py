"""
FIND WORKING GEMINI MODELS
Discover what models are actually available in this Vertex AI project
"""

import os
import sys
from typing import List


def list_available_models():
    """List available models in Vertex AI"""
    try:
        import vertexai
        from vertexai import generative_models

        project_id = os.getenv("GCP_PROJECT_ID", "raptorflow-481505")
        region = os.getenv("GCP_REGION", "us-central1")

        print(f"🔍 Listing models for project: {project_id}")
        print(f"📍 Region: {region}")

        # Initialize Vertex AI
        vertexai.init(project=project_id, location=region)

        # Try to list models using the ModelService
        try:
            from google.cloud import aiplatform

            aiplatform.init(project=project_id, location=region)

            # List models
            models = aiplatform.Model.list(filter="display_name~'gemini'")

            print(f"\n📋 Found {len(models)} Gemini models:")
            working_models = []

            for model in models:
                print(f"🤖 {model.display_name} ({model.resource_name})")

                # Try to use this model
                try:
                    # Extract model name from resource name
                    model_name = model.resource_name.split("/")[-1]
                    generative_model = generative_models.GenerativeModel(model_name)

                    # Test generation
                    response = generative_model.generate_content("Say 'test'")
                    print(f"   ✅ WORKS! Response: {response.text[:30]}...")
                    working_models.append(model_name)

                except Exception as e:
                    print(f"   ❌ Failed: {str(e)[:50]}")

            return working_models

        except Exception as e:
            print(f"❌ Failed to list models: {e}")
            return []

    except Exception as e:
        print(f"❌ Vertex AI initialization failed: {e}")
        return []


def test_common_model_names():
    """Test common model names that might work"""

    print("\n🧪 Testing common model names...")

    # Common Gemini model names
    test_models = [
        "gemini-1.0-pro",
        "gemini-1.0-pro-vision",
        "gemini-pro",
        "gemini-pro-vision",
        "text-bison@001",
        "text-bison@latest",
        "chat-bison@001",
        "chat-bison@latest",
    ]

    working_models = []

    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel

        project_id = os.getenv("GCP_PROJECT_ID", "raptorflow-481505")
        region = os.getenv("GCP_REGION", "us-central1")

        vertexai.init(project=project_id, location=region)

        for model_name in test_models:
            try:
                print(f"🔄 Testing: {model_name}")
                model = GenerativeModel(model_name)
                response = model.generate_content("Say 'hello'")
                print(f"   ✅ {model_name} WORKS! Response: {response.text[:30]}...")
                working_models.append(model_name)

            except Exception as e:
                print(f"   ❌ {model_name} failed: {str(e)[:50]}")

        return working_models

    except Exception as e:
        print(f"❌ Failed to test models: {e}")
        return []


def create_universal_config_with_working_model(working_model: str):
    """Update universal configuration with working model"""

    print(f"\n🔧 Updating universal configuration to use: {working_model}")

    # Update ai-config.ts
    config_content = f"""/**
 * UNIVERSAL AI CONFIGURATION
 * This file ensures ALL AI services use {working_model} universally
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
  ENABLE_GEMINI_1_5_FLASH_ONLY: true,
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
    # This would need to be done manually or with additional code

    print(f"🎉 Universal configuration updated to use {working_model}")


if __name__ == "__main__":
    print("🔍 FINDING WORKING GEMINI MODELS")
    print("=" * 50)

    # Test 1: Try to list available models
    working_models = list_available_models()

    if not working_models:
        # Test 2: Try common model names
        working_models = test_common_model_names()

    if working_models:
        print(f"\n🎉 WORKING MODELS FOUND: {working_models}")
        primary_model = working_models[0]
        print(f"🎯 PRIMARY MODEL: {primary_model}")

        # Update universal configuration
        create_universal_config_with_working_model(primary_model)

        print(f"\n✅ SUCCESS! Using {primary_model} as universal model")
    else:
        print("\n❌ NO WORKING MODELS FOUND")
        print("💡 You may need to:")
        print("   1. Enable Gemini API in your GCP project")
        print("   2. Check your service account permissions")
        print("   3. Verify your region supports Gemini models")
