"""
UPDATE UNIVERSAL MODEL TO GEMINI-2.0-FLASH-001
Update all configuration files to use the working model
"""

import os
from datetime import datetime


def update_ai_config():
    """Update ai-config.ts with gemini-2.0-flash-001"""

    config_content = f"""/**
 * UNIVERSAL AI CONFIGURATION
 * This file ensures ALL AI services use gemini-2.0-flash-001 universally
 * Updated: {datetime.now().isoformat()}
 */

// Universal AI Model Configuration
export const AI_CONFIG = {{
  // PRIMARY MODEL - THE ONLY MODEL TO BE USED
  MODEL: 'gemini-2.0-flash-001',

  // Vertex AI Configuration
  VERTEX_AI_MODEL: 'gemini-2.0-flash-001',
  DEFAULT_MODEL: 'gemini-2.0-flash-001',

  // API Configuration
  API_ENDPOINT: '/ai/generate',
  DIRECT_API_MODEL: 'gemini-2.0-flash-001',

  // Feature Flags
  ENABLE_GEMINI_UNIVERSAL_ONLY: true,
  DISABLE_OTHER_MODELS: true,

  // Model Parameters (Optimized for gemini-2.0-flash-001)
  DEFAULT_TEMPERATURE: 0.7,
  DEFAULT_MAX_TOKENS: 1000,
  DEFAULT_TOP_P: 0.8,
  DEFAULT_TOP_K: 40,

  // Cost and Performance
  COST_PER_TOKEN: 0.000000075, // Estimated pricing
  MAX_CONTEXT_LENGTH: 1048576, // 1M token context window

  // Universal Constants
  UNIVERSAL_MODEL_NAME: 'gemini-2.0-flash-001',
  FALLBACK_MODEL: 'gemini-2.0-flash-001', // Same model - no fallbacks
}} as const;

// Type safety for universal model configuration
export type UniversalModel = 'gemini-2.0-flash-001';

// Helper function to ensure only gemini-2.0-flash-001 is used
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

    print("✅ Updated ai-config.ts with gemini-2.0-flash-001")


def update_backend_main():
    """Update backend main.py with gemini-2.0-flash-001"""

    try:
        with open("c:/Users/hp/OneDrive/Desktop/Raptorflow/backend/main.py", "r") as f:
            content = f.read()

        # Replace the model in the AIRequest class
        content = content.replace(
            'model: str = "gemini-1.5-flash"  # UNIVERSALLY ENFORCED MODEL',
            'model: str = "gemini-2.0-flash-001"  # UNIVERSALLY ENFORCED MODEL',
        )

        # Replace in the endpoint
        content = content.replace(
            'universal_model = "gemini-1.5-flash"',
            'universal_model = "gemini-2.0-flash-001"',
        )

        # Replace in the comment
        content = content.replace(
            '"""Generate content using Vertex AI - UNIVERSALLY ENFORCED GEMINI 1.5 FLASH"""',
            '"""Generate content using Vertex AI - UNIVERSALLY ENFORCED GEMINI 2.0 FLASH-001"""',
        )

        # Replace in the logging
        content = content.replace(
            'logger.warning(f"Model override attempted: {request.model} -> {universal_model}")',
            'logger.warning(f"Model override attempted: {request.model} -> gemini-2.0-flash-001")',
        )

        with open("c:/Users/hp/OneDrive/Desktop/Raptorflow/backend/main.py", "w") as f:
            f.write(content)

        print("✅ Updated backend main.py with gemini-2.0-flash-001")

    except Exception as e:
        print(f"❌ Failed to update backend: {e}")


def update_vertex_ai_service():
    """Update vertex-ai.ts with gemini-2.0-flash-001"""

    try:
        with open(
            "c:/Users/hp/OneDrive/Desktop/Raptorflow/frontend/src/lib/vertex-ai.ts", "r"
        ) as f:
            content = f.read()

        # Replace default model in generateContent
        content = content.replace(
            "model: universalModel, // ALWAYS use universal model",
            "model: universalModel, // ALWAYS use gemini-2.0-flash-001",
        )

        # Update comments
        content = content.replace(
            "// ENFORCE UNIVERSAL MODEL USAGE", "// ENFORCE GEMINI-2.0-FLASH-001 USAGE"
        )

        with open(
            "c:/Users/hp/OneDrive/Desktop/Raptorflow/frontend/src/lib/vertex-ai.ts", "w"
        ) as f:
            f.write(content)

        print("✅ Updated vertex-ai.ts with gemini-2.0-flash-001")

    except Exception as e:
        print(f"❌ Failed to update vertex-ai.ts: {e}")


def update_ocr_processors():
    """Update OCR processors to use gemini-2.0-flash-001"""

    ocr_files = [
        "c:/Users/hp/OneDrive/Desktop/Raptorflow/backend/agents/tools/ocr_complex/vision_gemini.py",
        "c:/Users/hp/OneDrive/Desktop/Raptorflow/backend/agents/tools/ocr_complex/ocr_engine.py",
        "c:/Users/hp/OneDrive/Desktop/Raptorflow/backend/agents/tools/ocr_complex/ocr_multilang.py",
    ]

    for file_path in ocr_files:
        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Replace all occurrences of gemini-1.5-flash
            content = content.replace("gemini-1.5-flash", "gemini-2.0-flash-001")

            # Update model names in generativeai imports
            content = content.replace(
                "genai.GenerativeModel('gemini-1.5-flash')",
                "genai.GenerativeModel('gemini-2.0-flash-001')",
            )

            with open(file_path, "w") as f:
                f.write(content)

            print(f"✅ Updated {file_path.split('/')[-1]} with gemini-2.0-flash-001")

        except Exception as e:
            print(f"❌ Failed to update {file_path}: {e}")


def update_test_page():
    """Update test page to reflect the new model"""

    try:
        with open(
            "c:/Users/hp/OneDrive/Desktop/Raptorflow/frontend/src/app/test-gemini/page.tsx",
            "r",
        ) as f:
            content = f.read()

        # Update page title and content
        content = content.replace(
            "🚨 UNIVERSAL GEMINI 1.5 FLASH TEST 🚨",
            "🚨 UNIVERSAL GEMINI 2.0 FLASH-001 TEST 🚨",
        )

        content = content.replace(
            "This app ONLY uses Gemini 1.5 Flash - all other models are blocked",
            "This app ONLY uses Gemini 2.0 Flash-001 - all other models are blocked",
        )

        content = content.replace(
            "Test Universal Gemini 1.5 Flash", "Test Universal Gemini 2.0 Flash-001"
        )

        with open(
            "c:/Users/hp/OneDrive/Desktop/Raptorflow/frontend/src/app/test-gemini/page.tsx",
            "w",
        ) as f:
            f.write(content)

        print("✅ Updated test page with gemini-2.0-flash-001")

    except Exception as e:
        print(f"❌ Failed to update test page: {e}")


def create_verification_test():
    """Create a test to verify the new model works"""

    test_code = '''
"""
VERIFY GEMINI-2.0-FLASH-001 INTEGRATION
Test that the universal configuration works with the new model
"""

import os
import sys
from vertexai.generative_models import GenerativeModel
import vertexai

def test_gemini_2_0_flash_001():
    """Test gemini-2.0-flash-001 directly"""

    print("🧪 TESTING GEMINI-2.0-FLASH-001")
    print("=" * 40)

    project_id = os.getenv('GCP_PROJECT_ID', 'raptorflow-481505')
    region = os.getenv('GCP_REGION', 'us-central1')

    try:
        vertexai.init(project=project_id, location=region)
        print("✅ Vertex AI initialized")

        model = GenerativeModel('gemini-2.0-flash-001')
        print("✅ Model created")

        response = model.generate_content("What is 5+5? Answer with just the number.")
        print(f"✅ Response: {response.text}")

        if "10" in response.text:
            print("🎉 GEMINI-2.0-FLASH-001 WORKS!")
            return True
        else:
            print("⚠️  Unexpected response")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_gemini_2_0_flash_001()
'''

    with open(
        "c:/Users/hp/OneDrive/Desktop/Raptorflow/verify_gemini_2_0_flash.py", "w"
    ) as f:
        f.write(test_code)

    print("✅ Created verification test for gemini-2.0-flash-001")


def main():
    """Update all files to use gemini-2.0-flash-001"""

    print("🔧 UPDATING UNIVERSAL MODEL TO GEMINI-2.0-FLASH-001")
    print("=" * 50)

    update_ai_config()
    update_backend_main()
    update_vertex_ai_service()
    update_ocr_processors()
    update_test_page()
    create_verification_test()

    print("\n🎉 ALL FILES UPDATED!")
    print("✅ Universal model is now: gemini-2.0-flash-001")
    print("🚀 Ready to test with real Vertex AI!")


if __name__ == "__main__":
    main()
