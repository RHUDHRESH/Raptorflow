"""
SIMPLE UPDATE TO GEMINI-2.0-FLASH-001
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
  COST_PER_TOKEN: 0.000000075,
  MAX_CONTEXT_LENGTH: 1048576,

  // Universal Constants
  UNIVERSAL_MODEL_NAME: 'gemini-2.0-flash-001',
  FALLBACK_MODEL: 'gemini-2.0-flash-001',
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

        content = content.replace(
            'model: str = "gemini-1.5-flash"  # UNIVERSALLY ENFORCED MODEL',
            'model: str = "gemini-2.0-flash-001"  # UNIVERSALLY ENFORCED MODEL',
        )

        content = content.replace(
            'universal_model = "gemini-1.5-flash"',
            'universal_model = "gemini-2.0-flash-001"',
        )

        with open("c:/Users/hp/OneDrive/Desktop/Raptorflow/backend/main.py", "w") as f:
            f.write(content)

        print("✅ Updated backend main.py with gemini-2.0-flash-001")

    except Exception as e:
        print(f"❌ Failed to update backend: {e}")


def update_vertex_ai_service():
    """Update vertex-ai.ts"""

    try:
        with open(
            "c:/Users/hp/OneDrive/Desktop/Raptorflow/frontend/src/lib/vertex-ai.ts", "r"
        ) as f:
            content = f.read()

        content = content.replace("gemini-1.5-flash", "gemini-2.0-flash-001")

        with open(
            "c:/Users/hp/OneDrive/Desktop/Raptorflow/frontend/src/lib/vertex-ai.ts", "w"
        ) as f:
            f.write(content)

        print("✅ Updated vertex-ai.ts with gemini-2.0-flash-001")

    except Exception as e:
        print(f"❌ Failed to update vertex-ai.ts: {e}")


def main():
    """Update all files to use gemini-2.0-flash-001"""

    print("🔧 UPDATING UNIVERSAL MODEL TO GEMINI-2.0-FLASH-001")
    print("=" * 50)

    update_ai_config()
    update_backend_main()
    update_vertex_ai_service()

    print("\n🎉 ALL FILES UPDATED!")
    print("✅ Universal model is now: gemini-2.0-flash-001")
    print("🚀 Ready to test with real Vertex AI!")


if __name__ == "__main__":
    main()
