import { VertexAI, GenerativeModel } from '@google-cloud/vertexai';
import { env } from '../config/env';

// Initialize Vertex AI
export const vertexAI = new VertexAI({
  project: env.GOOGLE_CLOUD_PROJECT_ID,
  location: env.GOOGLE_CLOUD_LOCATION,
});

export const getModel = (modelName: string): GenerativeModel => {
  return vertexAI.getGenerativeModel({ model: modelName });
};
