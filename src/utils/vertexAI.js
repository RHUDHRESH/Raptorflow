// Vertex AI utilities for frontend
// These functions redirect to backend API calls instead of direct Vertex AI calls

export const TASK_TYPES = {
  REASONING: 'reasoning',
  FAST: 'fast',
  CREATIVE: 'creative',
  CREATIVE_FAST: 'creative_fast',
  CREATIVE_REASONING: 'creative_reasoning',
  GENERAL_PURPOSE: 'general_purpose'
};

// Get backend API URL for Vertex AI powered endpoints
export const getVertexAIUrl = (taskType) => {
  // The frontend functions will now make requests through backend API
  // which handles the Vertex AI integration
  const baseUrl = import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
  return `${baseUrl}/vertex-ai/${taskType}`;
};
