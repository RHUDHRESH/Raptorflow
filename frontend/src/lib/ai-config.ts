/**
 * UNIVERSAL AI CONFIGURATION
 * This file ensures ALL AI services use gemini-2.0-flash-001 universally
 */

// Universal AI Model Configuration
export const AI_CONFIG = {
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
} as const;

// Type safety for universal model configuration
export type UniversalModel = 'gemini-2.0-flash-001';

// Helper function to ensure only gemini-2.0-flash-001 is used
export function getUniversalModel(): UniversalModel {
  return AI_CONFIG.MODEL;
}

// Validator function to enforce universal model usage
export function validateModelUsage(model: string): UniversalModel {
  if (model !== AI_CONFIG.MODEL) {
    console.warn(`Model "${model}" is not allowed. Forcing universal model: ${AI_CONFIG.MODEL}`);
    return AI_CONFIG.MODEL;
  }
  return model as UniversalModel;
}

// Export singleton instance
export const universalAI = {
  model: AI_CONFIG.MODEL,
  getModel: () => AI_CONFIG.MODEL,
  validateModel: validateModelUsage,
  isUniversalModel: (model: string) => model === AI_CONFIG.MODEL,
} as const;

// Runtime enforcement
if (typeof window !== 'undefined') {
  // Override any attempts to use other models
  Object.defineProperty(window, 'AI_MODEL_OVERRIDE', {
    value: AI_CONFIG.MODEL,
    writable: false,
    configurable: false
  });
}

export default AI_CONFIG;
