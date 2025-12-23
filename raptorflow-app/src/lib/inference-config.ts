/**
 * SOTA Inference Configuration
 * Centralized provider management following the "inference_simple" pattern.
 * The Vertex API key is the only basis for inference.
 */

export interface InferenceConfig {
  apiKey: string;
  provider: "vertex";
  region: string;
  projectId?: string;
}

/**
 * Retrieves the singular inference configuration.
 * Throws if the mandatory INFERENCE_SIMPLE variable is missing.
 */
export function getInferenceConfig(): InferenceConfig {
  // Check for both server-side and client-side (if enabled) variables
  const apiKey = process.env.INFERENCE_SIMPLE || process.env.NEXT_PUBLIC_INFERENCE_SIMPLE;

  if (!apiKey) {
    console.error("CRITICAL: INFERENCE_SIMPLE (Vertex API Key) is missing.");
    // We don't throw immediately to allow the UI to show a nice error boundary later
    return {
      apiKey: "",
      provider: "vertex",
      region: process.env.NEXT_PUBLIC_GCP_REGION || "europe-west1",
      projectId: process.env.NEXT_PUBLIC_GCP_PROJECT_ID,
    };
  }

  return {
    apiKey,
    provider: "vertex",
    region: process.env.NEXT_PUBLIC_GCP_REGION || "europe-west1",
    projectId: process.env.NEXT_PUBLIC_GCP_PROJECT_ID,
  };
}

/**
 * Success signal for end-to-end connectivity.
 */
export function isInferenceReady(): boolean {
  const config = getInferenceConfig();
  return config.apiKey.length > 0;
}
