import { ChatVertexAI } from "@langchain/google-vertexai";

// Ensure environment variables are set
// GOOGLE_APPLICATION_CREDENTIALS (path to json) or standard gcloud auth
// GOOGLE_VERTEX_AI_WEB_CREDENTIALS (if using that flow)

// Check if Vertex AI credentials are available
function hasVertexAICredentials(): boolean {
  return !!(
    process.env.GOOGLE_APPLICATION_CREDENTIALS ||
    process.env.GOOGLE_VERTEX_AI_WEB_CREDENTIALS ||
    process.env.GCLOUD_PROJECT
  );
}

// Lazy-initialized model instances
let _gemini2Flash: ChatVertexAI | null = null;
let _gemini15Pro: ChatVertexAI | null = null;
let _gemini15Flash: ChatVertexAI | null = null;

// Getter functions for lazy initialization
export function getGemini2Flash(): ChatVertexAI | null {
  if (!hasVertexAICredentials()) {
    console.warn("Vertex AI credentials not set - gemini2Flash unavailable");
    return null;
  }
  if (!_gemini2Flash) {
    _gemini2Flash = new ChatVertexAI({
      model: "gemini-2.0-flash-exp",
      temperature: 0.7,
      maxOutputTokens: 8192,
    });
  }
  return _gemini2Flash;
}

export function getGemini15Pro(): ChatVertexAI | null {
  if (!hasVertexAICredentials()) {
    console.warn("Vertex AI credentials not set - gemini15Pro unavailable");
    return null;
  }
  if (!_gemini15Pro) {
    _gemini15Pro = new ChatVertexAI({
      model: "gemini-1.5-pro-002",
      temperature: 0.5,
      maxOutputTokens: 8192,
    });
  }
  return _gemini15Pro;
}

export function getGemini15Flash(): ChatVertexAI | null {
  if (!hasVertexAICredentials()) {
    console.warn("Vertex AI credentials not set - gemini15Flash unavailable");
    return null;
  }
  if (!_gemini15Flash) {
    _gemini15Flash = new ChatVertexAI({
      model: "gemini-1.5-flash-002",
      temperature: 0.3,
      maxOutputTokens: 2048,
    });
  }
  return _gemini15Flash;
}

// Legacy exports for backward compatibility (will fail if credentials not set)
// These are kept for any existing code that imports them directly
export const gemini2Flash = null as unknown as ChatVertexAI;
export const gemini15Pro = null as unknown as ChatVertexAI;
export const gemini15Flash = null as unknown as ChatVertexAI;

export const geminiEmbeddingModel = "text-embedding-004"; // For reference in RAG

