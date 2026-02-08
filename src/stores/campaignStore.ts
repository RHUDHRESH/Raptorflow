"use client";

import { create } from "zustand";
import {
  campaignsService,
  type ApiCampaign,
  type CreateCampaignInput,
  type UpdateCampaignInput,
} from "@/services/campaigns.service";

export type Campaign = {
  id: string;
  title: string;
  description: string;
  objective: string;
  status: string;
  createdAt?: string;
  updatedAt?: string;
};

function mapCampaign(c: ApiCampaign): Campaign {
  return {
    id: c.id,
    title: c.title,
    description: c.description ?? "",
    objective: c.objective,
    status: c.status,
    createdAt: c.created_at,
    updatedAt: c.updated_at,
  };
}

type CampaignStore = {
  campaigns: Campaign[];
  isLoading: boolean;
  error: string | null;

  clearError: () => void;
  fetchCampaigns: (workspaceId: string) => Promise<void>;
  createCampaign: (workspaceId: string, input: CreateCampaignInput) => Promise<Campaign>;
  updateCampaign: (
    workspaceId: string,
    campaignId: string,
    patch: UpdateCampaignInput
  ) => Promise<Campaign>;
  deleteCampaign: (workspaceId: string, campaignId: string) => Promise<void>;
  getCampaignById: (campaignId: string) => Campaign | undefined;
};

export const useCampaignStore = create<CampaignStore>((set, get) => ({
  campaigns: [],
  isLoading: false,
  error: null,

  clearError: () => set({ error: null }),

  fetchCampaigns: async (workspaceId) => {
    set({ isLoading: true, error: null });
    try {
      const campaigns = await campaignsService.list(workspaceId);
      set({ campaigns: campaigns.map(mapCampaign), isLoading: false });
    } catch (e: any) {
      const message = e?.message || "Failed to fetch campaigns";
      console.error("[campaigns] fetch failed:", e);
      set({ error: message, isLoading: false, campaigns: [] });
    }
  },

  createCampaign: async (workspaceId, input) => {
    set({ isLoading: true, error: null });
    try {
      const created = await campaignsService.create(workspaceId, input);
      const mapped = mapCampaign(created);
      set((state) => ({ campaigns: [mapped, ...state.campaigns], isLoading: false }));
      return mapped;
    } catch (e: any) {
      const message = e?.message || "Failed to create campaign";
      console.error("[campaigns] create failed:", e);
      set({ error: message, isLoading: false });
      throw e;
    }
  },

  updateCampaign: async (workspaceId, campaignId, patch) => {
    set({ isLoading: true, error: null });
    try {
      const updated = await campaignsService.update(workspaceId, campaignId, patch);
      const mapped = mapCampaign(updated);
      set((state) => ({
        campaigns: state.campaigns.map((c) => (c.id === mapped.id ? mapped : c)),
        isLoading: false,
      }));
      return mapped;
    } catch (e: any) {
      const message = e?.message || "Failed to update campaign";
      console.error("[campaigns] update failed:", e);
      set({ error: message, isLoading: false });
      throw e;
    }
  },

  deleteCampaign: async (workspaceId, campaignId) => {
    set({ isLoading: true, error: null });
    try {
      await campaignsService.delete(workspaceId, campaignId);
      set((state) => ({
        campaigns: state.campaigns.filter((c) => c.id !== campaignId),
        isLoading: false,
      }));
    } catch (e: any) {
      const message = e?.message || "Failed to delete campaign";
      console.error("[campaigns] delete failed:", e);
      set({ error: message, isLoading: false });
      throw e;
    }
  },

  getCampaignById: (campaignId) => get().campaigns.find((c) => c.id === campaignId),
}));

