import { ChatVertexAI } from "@langchain/google-vertexai";

// Ensure environment variables are set
// GOOGLE_APPLICATION_CREDENTIALS (path to json) or standard gcloud auth
// GOOGLE_VERTEX_AI_WEB_CREDENTIALS (if using that flow)

// Core Models
export const gemini2Flash = new ChatVertexAI({
  model: "gemini-2.0-flash-exp", // Using experimental tag if available, or fall back to 1.5-flash if 2.0 not publicly scoped yet in this env.
  // Note: Adjust model name based on actual Vertex AI availability in your region.
  temperature: 0.7,
  maxOutputTokens: 8192,
});

export const gemini15Pro = new ChatVertexAI({
  model: "gemini-1.5-pro-002",
  temperature: 0.5, // Better for reasoning
  maxOutputTokens: 8192,
});

export const gemini15Flash = new ChatVertexAI({
  model: "gemini-1.5-flash-002",
  temperature: 0.3, // Fast, deterministic
  maxOutputTokens: 2048,
});

export const geminiEmbeddingModel = "text-embedding-004"; // For reference in RAG
