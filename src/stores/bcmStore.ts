import { create } from "zustand";
import { bcmService } from "@/services/bcm.service";
import type { BCMManifest, BCMResponse, BCMVersionSummary } from "@/types/bcm";

interface BCMStoreState {
  manifest: BCMManifest | null;
  version: number | null;
  checksum: string | null;
  createdAt: string | null;
  completionPct: number;
  synthesized: boolean;
  isLoading: boolean;
  isRebuilding: boolean;
  isSeeding: boolean;
  isReflecting: boolean;
  error: string | null;
  versions: BCMVersionSummary[];

  fetchBCM: (workspaceId: string) => Promise<void>;
  rebuildBCM: (workspaceId: string) => Promise<void>;
  fetchVersions: (workspaceId: string) => Promise<void>;
  seedBCM: (workspaceId: string, businessContext: Record<string, unknown>) => Promise<void>;
  reflectBCM: (workspaceId: string) => Promise<void>;
}

const INITIAL: Pick<
  BCMStoreState,
  | "manifest"
  | "version"
  | "checksum"
  | "createdAt"
  | "completionPct"
  | "synthesized"
  | "isLoading"
  | "isRebuilding"
  | "isSeeding"
  | "isReflecting"
  | "error"
  | "versions"
> = {
  manifest: null,
  version: null,
  checksum: null,
  createdAt: null,
  completionPct: 0,
  synthesized: false,
  isLoading: false,
  isRebuilding: false,
  isSeeding: false,
  isReflecting: false,
  error: null,
  versions: [],
};

function applyResponse(resp: BCMResponse) {
  return {
    manifest: resp.manifest,
    version: resp.version,
    checksum: resp.checksum,
    createdAt: resp.created_at,
    completionPct: resp.completion_pct,
    synthesized: resp.synthesized,
    error: null,
  };
}

export const useBCMStore = create<BCMStoreState>((set) => ({
  ...INITIAL,

  fetchBCM: async (workspaceId: string) => {
    set({ isLoading: true, error: null });
    try {
      const resp = await bcmService.get(workspaceId);
      set({ ...applyResponse(resp), isLoading: false });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to fetch BCM";
      set({ isLoading: false, error: msg });
    }
  },

  rebuildBCM: async (workspaceId: string) => {
    set({ isRebuilding: true, error: null });
    try {
      const resp = await bcmService.rebuild(workspaceId);
      set({ ...applyResponse(resp), isRebuilding: false });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to rebuild BCM";
      set({ isRebuilding: false, error: msg });
    }
  },

  fetchVersions: async (workspaceId: string) => {
    try {
      const versions = await bcmService.listVersions(workspaceId);
      set({ versions });
    } catch {
      /* silent */
    }
  },

  seedBCM: async (workspaceId: string, businessContext: Record<string, unknown>) => {
    set({ isSeeding: true, error: null });
    try {
      const resp = await bcmService.seed(workspaceId, businessContext);
      set({ ...applyResponse(resp), isSeeding: false });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to seed BCM";
      set({ isSeeding: false, error: msg });
    }
  },

  reflectBCM: async (workspaceId: string) => {
    set({ isReflecting: true, error: null });
    try {
      await bcmService.reflect(workspaceId);
      // Refetch BCM to pick up updated memory_count + last_reflection_at
      const resp = await bcmService.get(workspaceId);
      set({ ...applyResponse(resp), isReflecting: false });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to reflect BCM";
      set({ isReflecting: false, error: msg });
    }
  },
}));
