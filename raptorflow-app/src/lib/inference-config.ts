/**
 * SOTA Inference Configuration
 * Centralized provider management following the "inference_simple" pattern.
 * Accepts INFERENCE_SIMPLE or VERTEX_AI_API_KEY (server) with optional public fallbacks.
 */

export interface InferenceConfig {
  apiKey: string;
  provider: "vertex";
  region: string;
  projectId?: string;
  models: {
    ultra: string;
    high: string;
    reasoning: string;
    general: string;
  }
}

function hasDefaultCredentials(): boolean {
  return Boolean(
    process.env.GOOGLE_APPLICATION_CREDENTIALS ||
      process.env.VERTEX_AI_USE_ADC === "true" ||
      process.env.NEXT_PUBLIC_VERTEX_AI_USE_ADC === "true"
  );
}

/**
 * Retrieves the singular inference configuration.
 * Returns an empty apiKey when no credentials are configured.
 */
export function getInferenceConfig(): InferenceConfig {
  // Check for both server-side and client-side (if enabled) variables
  const apiKey =
    process.env.INFERENCE_SIMPLE ||
    process.env.VERTEX_AI_API_KEY ||
    process.env.NEXT_PUBLIC_INFERENCE_SIMPLE ||
    process.env.NEXT_PUBLIC_VERTEX_AI_API_KEY;

  // Default to Flash for all tiers during development if env vars are missing
  const defaultModel =
    process.env.MODEL_GENERAL ||
    process.env.NEXT_PUBLIC_MODEL_GENERAL ||
    "gemini-2.5-flash-lite";

  const models = {
    ultra:
      process.env.MODEL_REASONING_ULTRA ||
      process.env.NEXT_PUBLIC_MODEL_REASONING_ULTRA ||
      defaultModel,
    high:
      process.env.MODEL_REASONING_HIGH ||
      process.env.NEXT_PUBLIC_MODEL_REASONING_HIGH ||
      defaultModel,
    reasoning:
      process.env.MODEL_REASONING ||
      process.env.NEXT_PUBLIC_MODEL_REASONING ||
      defaultModel,
    general:
      process.env.MODEL_GENERAL ||
      process.env.NEXT_PUBLIC_MODEL_GENERAL ||
      defaultModel,
  };

  const normalizedKey = apiKey?.trim() || "";
  const region = process.env.NEXT_PUBLIC_GCP_REGION || process.env.GCP_REGION || "europe-west1";
  const projectId =
    process.env.NEXT_PUBLIC_GCP_PROJECT_ID ||
    process.env.GCP_PROJECT_ID ||
    process.env.GOOGLE_CLOUD_PROJECT;

  if (!normalizedKey && !hasDefaultCredentials()) {
    console.warn("WARNING: Vertex API key is missing. Inference is disabled.");
    return {
      apiKey: "",
      provider: "vertex",
      region,
      projectId,
      models,
    };
  }

  return {
    apiKey: normalizedKey,
    provider: "vertex",
    region,
    projectId,
    models,
  };
}

/**
 * Success signal for end-to-end connectivity.
 */
export function isInferenceReady(): boolean {
  const config = getInferenceConfig();
  return config.apiKey.length > 0 || hasDefaultCredentials();
}
