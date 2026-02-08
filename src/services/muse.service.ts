import { apiRequest } from "@/services/http";

export type MuseGenerateRequest = {
  task: string;
  context?: Record<string, unknown>;
  content_type?: string;
  tone?: string;
  target_audience?: string;
  max_tokens?: number;
  temperature?: number;
};

export type MuseGenerateResponse = {
  success: boolean;
  content: string;
  tokens_used?: number;
  cost_usd?: number;
  suggestions?: string[];
  error?: string;
  metadata?: Record<string, unknown>;
};

export const museService = {
  async health(workspaceId: string): Promise<{ status: string; engine?: string }> {
    return apiRequest("/muse/health", { method: "GET", workspaceId });
  },

  async generate(
    workspaceId: string,
    payload: MuseGenerateRequest
  ): Promise<MuseGenerateResponse> {
    return apiRequest("/muse/generate", {
      method: "POST",
      workspaceId,
      body: JSON.stringify(payload),
    });
  },
};

