import type { Channel, CoreMessaging, RICP } from "@/types/foundation";
import { apiRequest } from "./http";

export type FoundationState = {
  ricps: RICP[];
  messaging: CoreMessaging | null;
  channels: Channel[];
};

/** Raw shape returned by the new canonical backend */
interface FoundationAPIResponse {
  id?: string;
  workspace_id?: string;
  company_info?: Record<string, unknown>;
  mission?: string;
  vision?: string;
  value_proposition?: string;
  brand_voice?: Record<string, unknown>;
  messaging?: Record<string, unknown>;
  status?: string;
}

export const foundationService = {
  async get(workspaceId: string): Promise<FoundationState> {
    const raw = await apiRequest<FoundationAPIResponse>("/foundation/", {
      method: "GET",
      workspaceId,
    });
    // Adapt new API shape to the store's expected shape
    return {
      ricps: [],
      messaging: (raw.messaging as unknown as CoreMessaging) ?? null,
      channels: [],
    };
  },

  async save(workspaceId: string, state: FoundationState): Promise<FoundationState> {
    await apiRequest<FoundationAPIResponse>("/foundation/", {
      method: "PUT",
      workspaceId,
      body: JSON.stringify({ messaging: state.messaging }),
    });
    return state;
  },
};

