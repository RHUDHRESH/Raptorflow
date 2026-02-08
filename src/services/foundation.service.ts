import type { Channel, CoreMessaging, RICP } from "@/types/foundation";
import { apiRequest } from "./http";

export type FoundationState = {
  ricps: RICP[];
  messaging: CoreMessaging | null;
  channels: Channel[];
};

export const foundationService = {
  async get(workspaceId: string): Promise<FoundationState> {
    return apiRequest<FoundationState>("/foundation", {
      method: "GET",
      workspaceId,
    });
  },

  async save(workspaceId: string, state: FoundationState): Promise<FoundationState> {
    return apiRequest<FoundationState>("/foundation", {
      method: "PUT",
      workspaceId,
      body: JSON.stringify(state),
    });
  },
};

