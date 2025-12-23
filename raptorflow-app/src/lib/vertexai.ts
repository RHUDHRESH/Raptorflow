import { ChatVertexAI } from "@langchain/google-vertexai";
import { getInferenceConfig } from "./inference-config";

// Lazy-initialized model instances
let _gemini2Flash: ChatVertexAI | null = null;
let _gemini15Pro: ChatVertexAI | null = null;
let _gemini15Flash: ChatVertexAI | null = null;

/**
 * SOTA Model Factory.
 * Uses the singular INFERENCE_SIMPLE API key.
 */
function createModel(modelName: string, temperature: number, maxTokens: number): ChatVertexAI | null {
  try {
    const config = getInferenceConfig();
    if (!config.apiKey) return null;

    return new ChatVertexAI({
      model: modelName,
      temperature: temperature,
      maxOutputTokens: maxTokens,
      apiKey: config.apiKey,
      location: config.region,
    });
  } catch (error) {
    console.error(`Failed to create model ${modelName}:`, error);
    return null;
  }
}

// Getter functions for lazy initialization
export function getGemini2Flash(): ChatVertexAI | null {
  if (!_gemini2Flash) {
    _gemini2Flash = createModel("gemini-2.0-flash-exp", 0.7, 8192);
  }
  return _gemini2Flash;
}

export function getGemini15Pro(): ChatVertexAI | null {
  if (!_gemini15Pro) {
    _gemini15Pro = createModel("gemini-1.5-pro-002", 0.5, 8192);
  }
  return _gemini15Pro;
}

export function getGemini15Flash(): ChatVertexAI | null {
  if (!_gemini15Flash) {
    _gemini15Flash = createModel("gemini-1.5-flash-002", 0.3, 2048);
  }
  return _gemini15Flash;
}

// Legacy exports for backward compatibility (will fail if credentials not set)
// These are kept for any existing code that imports them directly
export const gemini2Flash = null as unknown as ChatVertexAI;
export const gemini15Pro = null as unknown as ChatVertexAI;
export const gemini15Flash = null as unknown as ChatVertexAI;

export const geminiEmbeddingModel = "text-embedding-004"; // For reference in RAG

