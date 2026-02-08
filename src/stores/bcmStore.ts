import { create } from "zustand";
import { bcmService } from "@/services/bcm.service";
import type { BCMManifest, BCMResponse, BCMVersionSummary } from "@/types/bcm";

interface BCMStoreState {
  manifest: BCMManifest | null;
  version: number | null;
  checksum: string | null;
  createdAt: string | null;
  completionPct: number;
  isLoading: boolean;
  isRebuilding: boolean;
  error: string | null;
  versions: BCMVersionSummary[];

  fetchBCM: (workspaceId: string) => Promise<void>;
  rebuildBCM: (workspaceId: string) => Promise<void>;
  fetchVersions: (workspaceId: string) => Promise<void>;
  reset: () => void;
}

const INITIAL: Pick<
  BCMStoreState,
  | "manifest"
  | "version"
  | "checksum"
  | "createdAt"
  | "completionPct"
  | "isLoading"
  | "isRebuilding"
  | "error"
  | "versions"
> = {
  manifest: null,
  version: null,
  checksum: null,
  createdAt: null,
  completionPct: 0,
  isLoading: false,
  isRebuilding: false,
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

  reset: () => set(INITIAL),
}));
