import { QdrantClient } from "@qdrant/js-client-rest";

const QDRANT_URL = process.env.RAPTORFLOW_QDRANT_URL ?? "http://localhost:6333";
const QDRANT_API_KEY = process.env.RAPTORFLOW_QDRANT_API_KEY?.trim() || undefined;

export const qdrant = new QdrantClient({
  url: QDRANT_URL,
  ...(QDRANT_API_KEY ? { apiKey: QDRANT_API_KEY } : {}),
  checkCompatibility: false,
});

export const COLLECTION = process.env.RAPTORFLOW_QDRANT_COLLECTION ?? "raptorflow_ripples";

export function getQdrantBaseUrl(): string {
  return QDRANT_URL.replace(/\/$/, "");
}

export function getQdrantHeaders(): Record<string, string> {
  return QDRANT_API_KEY ? { "api-key": QDRANT_API_KEY } : {};
}
