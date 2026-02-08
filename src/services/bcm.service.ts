import { apiRequest } from "./http";
import type { BCMResponse, BCMVersionSummary } from "@/types/bcm";

export const bcmService = {
  async get(workspaceId: string): Promise<BCMResponse> {
    return apiRequest<BCMResponse>("/context/", { workspaceId });
  },

  async rebuild(workspaceId: string): Promise<BCMResponse> {
    return apiRequest<BCMResponse>("/context/rebuild", {
      method: "POST",
      workspaceId,
    });
  },

  async seed(
    workspaceId: string,
    businessContext: Record<string, unknown>
  ): Promise<BCMResponse> {
    return apiRequest<BCMResponse>("/context/seed", {
      method: "POST",
      workspaceId,
      body: JSON.stringify({ business_context: businessContext }),
    });
  },

  async listVersions(workspaceId: string): Promise<BCMVersionSummary[]> {
    return apiRequest<BCMVersionSummary[]>("/context/versions", {
      workspaceId,
    });
  },
};
