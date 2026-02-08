import type { RICP } from "@/types/foundation";
import { foundationService } from "@/services/foundation.service";

// Cohorts (ICPs) are currently stored inside Foundation state as `ricps`.
export const cohortsService = {
  async list(workspaceId: string): Promise<RICP[]> {
    const state = await foundationService.get(workspaceId);
    return state.ricps || [];
  },

  async create(workspaceId: string, ricp: RICP): Promise<RICP> {
    const state = await foundationService.get(workspaceId);
    const next = { ...state, ricps: [...(state.ricps || []), ricp] };
    await foundationService.save(workspaceId, next);
    return ricp;
  },

  async update(workspaceId: string, ricpId: string, updates: Partial<RICP>): Promise<RICP> {
    const state = await foundationService.get(workspaceId);
    const existing = (state.ricps || []).find((r) => r.id === ricpId);
    if (!existing) {
      throw new Error("RICP not found");
    }
    const updated = { ...existing, ...updates, updatedAt: Date.now() };
    const next = {
      ...state,
      ricps: (state.ricps || []).map((r) => (r.id === ricpId ? updated : r)),
    };
    await foundationService.save(workspaceId, next);
    return updated;
  },

  async remove(workspaceId: string, ricpId: string): Promise<void> {
    const state = await foundationService.get(workspaceId);
    const next = { ...state, ricps: (state.ricps || []).filter((r) => r.id !== ricpId) };
    await foundationService.save(workspaceId, next);
  },
};

