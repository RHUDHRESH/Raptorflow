import { create } from 'zustand';
import type { BusinessContext } from '@/lib/business-context';
import {
  getLatestManifest,
  triggerRebuild,
  getManifestHistory,
  exportManifest,
  type ManifestSummary,
} from '@/lib/bcm-client';

type BcmStatus = 'idle' | 'loading' | 'error' | 'stale';
type StaleReason = 'missing' | 'expired' | 'error';

type FetchOptions = {
  tier?: 'tier0' | 'tier1' | 'tier2';
};

interface BcmState {
  manifest: BusinessContext | null;
  status: BcmStatus;
  lastFetchedAt: number | null;
  staleReason?: StaleReason;
  history: ManifestSummary[];
  error: string | null;
}

interface BcmActions {
  fetchLatest: (workspaceId: string, options?: FetchOptions) => Promise<void>;
  rebuild: (workspaceId: string, force?: boolean) => Promise<void>;
  refreshHistory: (workspaceId: string) => Promise<void>;
  exportManifest: (workspaceId: string, format?: 'json' | 'markdown') => Promise<Blob>;
  markStale: (reason: StaleReason) => void;
  reset: () => void;
}

const initialState: BcmState = {
  manifest: null,
  status: 'idle',
  lastFetchedAt: null,
  history: [],
  error: null,
};

export const useBcmStore = create<BcmState & BcmActions>()((set, get) => ({
  ...initialState,

  async fetchLatest(workspaceId, options) {
    set({ status: 'loading', error: null });
    try {
      const response = await getLatestManifest(workspaceId, {
        tier: options?.tier ?? 'tier0',
      });

      set({
        manifest: response.manifest,
        status: 'idle',
        lastFetchedAt: Date.now(),
        staleReason: undefined,
        error: null,
      });

      // Refresh history lazily to avoid extra load if already cached recently
      if (!get().history.length) {
        await get().refreshHistory(workspaceId);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch BCM';
      set({ status: 'error', error: message, staleReason: 'error' });
    }
  },

  async rebuild(workspaceId, force = false) {
    set({ status: 'loading', error: null });
    try {
      const response = await triggerRebuild(workspaceId, force);
      set({
        manifest: response.manifest,
        status: 'idle',
        lastFetchedAt: Date.now(),
        staleReason: undefined,
      });
      await get().refreshHistory(workspaceId);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to rebuild BCM';
      set({ status: 'error', error: message, staleReason: 'error' });
      throw error;
    }
  },

  async refreshHistory(workspaceId) {
    try {
      const history = await getManifestHistory(workspaceId);
      set({ history });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load history';
      set({ error: message });
    }
  },

  async exportManifest(workspaceId, format = 'json') {
    try {
      return await exportManifest(workspaceId, format);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to export manifest';
      set({ error: message });
      throw error;
    }
  },

  markStale(reason) {
    set({ status: 'stale', staleReason: reason });
  },

  reset() {
    set(initialState);
  },
}));
