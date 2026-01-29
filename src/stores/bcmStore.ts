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
  activeWorkspaceId: string | null;
  cache: Record<string, WorkspaceCache>;
  manifest: BusinessContext | null;
  status: BcmStatus;
  lastFetchedAt: number | null;
  staleReason?: StaleReason;
  history: ManifestSummary[];
  error: string | null;
}

interface BcmActions {
  setActiveWorkspace: (workspaceId: string | null) => void;
  fetchLatest: (workspaceId: string, options?: FetchOptions) => Promise<void>;
  ensureLatest: (workspaceId: string, options?: FetchOptions) => Promise<void>;
  rebuild: (workspaceId: string, force?: boolean) => Promise<void>;
  refreshHistory: (workspaceId: string) => Promise<void>;
  exportManifest: (workspaceId: string, format?: 'json' | 'markdown') => Promise<Blob>;
  markStale: (reason: StaleReason) => void;
  reset: () => void;
}

const initialState: BcmState = {
  activeWorkspaceId: null,
  cache: {},
  manifest: null,
  status: 'idle',
  lastFetchedAt: null,
  history: [],
  error: null,
};

const defaultWorkspaceState = {
  manifest: null,
  status: 'idle' as BcmStatus,
  lastFetchedAt: null,
  staleReason: undefined as StaleReason | undefined,
  history: [] as ManifestSummary[],
  error: null,
};

const getWorkspaceState = (
  cache: Record<string, WorkspaceCache>,
  workspaceId: string | null,
) => {
  if (!workspaceId) {
    return defaultWorkspaceState;
  }
  return cache[workspaceId] ?? defaultWorkspaceState;
};

type WorkspaceCache = typeof defaultWorkspaceState;

export const useBcmStore = create<BcmState & BcmActions>()((set, get) => ({
  ...initialState,

  setActiveWorkspace(workspaceId) {
    const workspaceState = getWorkspaceState(get().cache, workspaceId);
    set({
      activeWorkspaceId: workspaceId,
      ...workspaceState,
    });
  },

  async fetchLatest(workspaceId, options) {
    set((state) => {
      const workspaceState = state.cache[workspaceId] ?? defaultWorkspaceState;
      return {
        activeWorkspaceId: workspaceId,
        cache: {
          ...state.cache,
          [workspaceId]: {
            ...workspaceState,
            status: 'loading',
            error: null,
          },
        },
        status: 'loading',
        error: null,
      };
    });
    try {
      const response = await getLatestManifest(workspaceId, {
        tier: options?.tier ?? 'tier0',
      });

      set((state) => {
        const nextWorkspaceState: WorkspaceCache = {
          manifest: response.manifest ?? null,
          status: 'idle',
          lastFetchedAt: Date.now(),
          staleReason: undefined,
          history: state.cache[workspaceId]?.history ?? [],
          error: null,
        };
        const cache = {
          ...state.cache,
          [workspaceId]: nextWorkspaceState,
        };
        const activeState = workspaceId === state.activeWorkspaceId
          ? nextWorkspaceState
          : getWorkspaceState(cache, state.activeWorkspaceId);
        return {
          cache,
          ...activeState,
        };
      });

      // Refresh history lazily to avoid extra load if already cached recently
      if (!get().history.length) {
        await get().refreshHistory(workspaceId);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to fetch BCM';
      set((state) => {
        const workspaceState = state.cache[workspaceId] ?? defaultWorkspaceState;
        const nextWorkspaceState: WorkspaceCache = {
          ...workspaceState,
          status: 'error',
          error: message,
          staleReason: 'error',
        };
        const cache = {
          ...state.cache,
          [workspaceId]: nextWorkspaceState,
        };
        const activeState = workspaceId === state.activeWorkspaceId
          ? nextWorkspaceState
          : getWorkspaceState(cache, state.activeWorkspaceId);
        return {
          cache,
          ...activeState,
        };
      });
    }
  },

  async ensureLatest(workspaceId, options) {
    const workspaceState = get().cache[workspaceId];
    if (workspaceState?.manifest && workspaceState.status !== 'stale' && workspaceState.status !== 'error') {
      get().setActiveWorkspace(workspaceId);
      return;
    }
    await get().fetchLatest(workspaceId, options);
  },

  async rebuild(workspaceId, force = false) {
    set((state) => {
      const workspaceState = state.cache[workspaceId] ?? defaultWorkspaceState;
      return {
        activeWorkspaceId: workspaceId,
        cache: {
          ...state.cache,
          [workspaceId]: {
            ...workspaceState,
            status: 'loading',
            error: null,
          },
        },
        status: 'loading',
        error: null,
      };
    });
    try {
      const response = await triggerRebuild(workspaceId, force);
      set((state) => {
        const nextWorkspaceState: WorkspaceCache = {
          manifest: response.manifest ?? null,
          status: 'idle',
          lastFetchedAt: Date.now(),
          staleReason: undefined,
          history: state.cache[workspaceId]?.history ?? [],
          error: null,
        };
        const cache = {
          ...state.cache,
          [workspaceId]: nextWorkspaceState,
        };
        const activeState = workspaceId === state.activeWorkspaceId
          ? nextWorkspaceState
          : getWorkspaceState(cache, state.activeWorkspaceId);
        return {
          cache,
          ...activeState,
        };
      });
      await get().refreshHistory(workspaceId);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to rebuild BCM';
      set((state) => {
        const workspaceState = state.cache[workspaceId] ?? defaultWorkspaceState;
        const nextWorkspaceState: WorkspaceCache = {
          ...workspaceState,
          status: 'error',
          error: message,
          staleReason: 'error',
        };
        const cache = {
          ...state.cache,
          [workspaceId]: nextWorkspaceState,
        };
        const activeState = workspaceId === state.activeWorkspaceId
          ? nextWorkspaceState
          : getWorkspaceState(cache, state.activeWorkspaceId);
        return {
          cache,
          ...activeState,
        };
      });
      throw error;
    }
  },

  async refreshHistory(workspaceId) {
    try {
      const historyResponse = await getManifestHistory(workspaceId);
      const history = historyResponse.versions;
      set((state) => {
        const workspaceState = state.cache[workspaceId] ?? defaultWorkspaceState;
        const nextWorkspaceState: WorkspaceCache = {
          ...workspaceState,
          history,
        };
        const cache = {
          ...state.cache,
          [workspaceId]: nextWorkspaceState,
        };
        const activeState = workspaceId === state.activeWorkspaceId
          ? nextWorkspaceState
          : getWorkspaceState(cache, state.activeWorkspaceId);
        return {
          cache,
          ...activeState,
        };
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to load history';
      set((state) => ({
        error: message,
        cache: {
          ...state.cache,
          ...(state.activeWorkspaceId
            ? {
                [state.activeWorkspaceId]: {
                  ...(state.cache[state.activeWorkspaceId] ?? defaultWorkspaceState),
                  error: message,
                },
              }
            : {}),
        },
      }));
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
    set((state) => {
      if (!state.activeWorkspaceId) {
        return { status: 'stale', staleReason: reason };
      }
      const workspaceState = state.cache[state.activeWorkspaceId] ?? defaultWorkspaceState;
      const nextWorkspaceState: WorkspaceCache = {
        ...workspaceState,
        status: 'stale',
        staleReason: reason,
      };
      const cache = {
        ...state.cache,
        [state.activeWorkspaceId]: nextWorkspaceState,
      };
      return {
        cache,
        ...nextWorkspaceState,
      };
    });
  },

  reset() {
    set(initialState);
  },
}));
