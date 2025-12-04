import { VertexAI, GenerativeModel } from '@google-cloud/vertexai';
import { ChatVertexAI } from "@langchain/google-vertexai";
import { env } from '../config/env';

// Initialize Vertex AI (Native SDK)
export const vertexAI = new VertexAI({
  project: env.GOOGLE_CLOUD_PROJECT_ID,
  location: env.GOOGLE_CLOUD_LOCATION,
});

export const getModel = (modelName: string): GenerativeModel => {
  return vertexAI.getGenerativeModel({ model: modelName });
};

// Initialize Vertex AI (LangChain)
export const getLangChainModel = (modelName: string = 'gemini-pro') => {
  return new ChatVertexAI({
    model: modelName,
    location: env.GOOGLE_CLOUD_LOCATION,
    maxOutputTokens: 8192,
    temperature: 0.1,
    // Additional configuration if needed
  });
};
