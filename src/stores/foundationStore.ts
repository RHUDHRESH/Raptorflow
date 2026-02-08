"use client";

import { create } from "zustand";
import type { Channel, CoreMessaging, RICP } from "@/types/foundation";
import { foundationService, type FoundationState } from "@/services/foundation.service";

/* ════════════════════════════════════════════════════════════════════════════════════════
   FOUNDATION STORE — No-Auth Reconstruction
   Source of truth: backend `/api/v1/foundation` (via Next proxy) scoped by `X-Workspace-Id`.
   No Supabase browser client, no onboarding sync, no silent fallbacks.
   ════════════════════════════════════════════════════════════════════════════════════════ */

interface FoundationStoreState extends FoundationState {
  positioningConfidence: number;
  isLoading: boolean;
  error: string | null;

  fetchFoundation: (workspaceId: string) => Promise<void>;
  saveFoundation: (workspaceId: string) => Promise<void>;

  addRICP: (ricp: RICP, workspaceId: string) => Promise<void>;
  updateRICP: (id: string, updates: Partial<RICP>, workspaceId: string) => Promise<void>;
  deleteRICP: (id: string, workspaceId: string) => Promise<void>;
  getRICPById: (id: string) => RICP | undefined;

  updateMessaging: (updates: Partial<CoreMessaging>, workspaceId: string) => Promise<void>;

  addChannel: (channel: Channel, workspaceId: string) => Promise<void>;
  updateChannel: (id: string, updates: Partial<Channel>, workspaceId: string) => Promise<void>;
  deleteChannel: (id: string, workspaceId: string) => Promise<void>;

  reset: () => void;
}

const EMPTY_STATE: FoundationState = {
  ricps: [],
  messaging: null,
  channels: [],
};

export const useFoundationStore = create<FoundationStoreState>((set, get) => ({
  ...EMPTY_STATE,
  positioningConfidence: 0,
  isLoading: false,
  error: null,

  fetchFoundation: async (workspaceId: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await foundationService.get(workspaceId);
      set({
        ricps: data.ricps || [],
        messaging: data.messaging || null,
        channels: data.channels || [],
      });
    } catch (err: any) {
      console.error("Error fetching foundation:", err);
      set({ error: err?.message || "Failed to fetch foundation" });
    } finally {
      set({ isLoading: false });
    }
  },

  saveFoundation: async (workspaceId: string) => {
    const { ricps, messaging, channels } = get();
    try {
      await foundationService.save(workspaceId, { ricps, messaging, channels });
    } catch (err: any) {
      console.error("Error saving foundation:", err);
      set({ error: err?.message || "Failed to save foundation" });
      throw err;
    }
  },

  addRICP: async (ricp: RICP, workspaceId: string) => {
    set((state) => ({
      ricps: [...state.ricps, { ...ricp, createdAt: Date.now(), updatedAt: Date.now() }],
      error: null,
    }));
    await get().saveFoundation(workspaceId);
  },

  updateRICP: async (id, updates, workspaceId) => {
    set((state) => ({
      ricps: state.ricps.map((r) => (r.id === id ? { ...r, ...updates, updatedAt: Date.now() } : r)),
      error: null,
    }));
    await get().saveFoundation(workspaceId);
  },

  deleteRICP: async (id, workspaceId) => {
    set((state) => ({ ricps: state.ricps.filter((r) => r.id !== id), error: null }));
    await get().saveFoundation(workspaceId);
  },

  getRICPById: (id) => get().ricps.find((r) => r.id === id),

  updateMessaging: async (updates, workspaceId) => {
    set((state) => ({
      messaging: state.messaging
        ? { ...state.messaging, ...updates, updatedAt: Date.now() }
        : {
            id: `msg-${Date.now()}`,
            oneLiner: "",
            positioningStatement: {
              target: "",
              situation: "",
              product: "",
              category: "",
              keyBenefit: "",
              alternatives: "",
              differentiator: "",
            },
            valueProps: [],
            brandVoice: { tone: [], doList: [], dontList: [] },
            storyBrand: {
              character: "",
              problemExternal: "",
              problemInternal: "",
              problemPhilosophical: "",
              guide: "",
              plan: [],
              callToAction: "",
              transitionalCTA: "",
              avoidFailure: [],
              success: [],
            },
            updatedAt: Date.now(),
            confidence: 0,
            ...updates,
          },
      error: null,
    }));
    await get().saveFoundation(workspaceId);
  },

  addChannel: async (channel, workspaceId) => {
    set((state) => ({ channels: [...state.channels, channel], error: null }));
    await get().saveFoundation(workspaceId);
  },

  updateChannel: async (id, updates, workspaceId) => {
    set((state) => ({
      channels: state.channels.map((c) => (c.id === id ? { ...c, ...updates } : c)),
      error: null,
    }));
    await get().saveFoundation(workspaceId);
  },

  deleteChannel: async (id, workspaceId) => {
    set((state) => ({ channels: state.channels.filter((c) => c.id !== id), error: null }));
    await get().saveFoundation(workspaceId);
  },

  reset: () =>
    set({
      ...EMPTY_STATE,
      positioningConfidence: 0,
      isLoading: false,
      error: null,
    }),
}));

