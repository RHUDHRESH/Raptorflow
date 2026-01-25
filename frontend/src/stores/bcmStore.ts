import { create } from 'zustand';
import { authFetch } from '../lib/auth-helpers';

interface BCMContext {
  workspace_id: string;
  business_stage: string;
  industry: string;
  team_size: number;
  revenue_range: string;
  target_market: string;
  current_challenges: string[];
  strengths: string[];
  opportunities: string[];
  evolution_history: Array<{
    timestamp: string;
    event: string;
    insights: string[];
  }>;
  contradictions: Array<{
    id: string;
    description: string;
    severity: string;
    resolution: string;
  }>;
  strategic_priorities: string[];
}

interface BCMStore {
  context: BCMContext | null;
  evolution: any;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setContext: (context: BCMContext) => void;
  setEvolution: (evolution: any) => void;
  fetchContext: (workspaceId: string) => Promise<void>;
  fetchEvolution: (workspaceId: string) => Promise<void>;
  recordInteraction: (data: {
    agent: string;
    action: string;
    context: any;
  }) => Promise<void>;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// API helper functions
const bcmApi = {
  async fetchContext(workspaceId: string): Promise<BCMContext> {
    const response = await authFetch(`/api/proxy/api/v1/bcm/context?workspace_id=${workspaceId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch BCM context');
    }
    
    const data = await response.json();
    return data.context;
  },
  
  async fetchEvolution(workspaceId: string): Promise<any> {
    const response = await authFetch(`/api/proxy/api/v1/bcm/evolution?workspace_id=${workspaceId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch BCM evolution');
    }
    
    const data = await response.json();
    return data.evolution;
  },
  
  async recordInteraction(data: {
    agent: string;
    action: string;
    context: any;
  }): Promise<void> {
    const response = await authFetch('/api/proxy/api/v1/bcm/record-interaction', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      throw new Error('Failed to record BCM interaction');
    }
  }
};

export const useBCMStore = create<BCMStore>((set, get) => ({
  context: null,
  evolution: null,
  isLoading: false,
  error: null,

  setContext: (context) => {
    set({ context });
  },

  setEvolution: (evolution) => {
    set({ evolution });
  },

  fetchContext: async (workspaceId) => {
    set({ isLoading: true, error: null });
    try {
      const context = await bcmApi.fetchContext(workspaceId);
      set({ context });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
    } finally {
      set({ isLoading: false });
    }
  },

  fetchEvolution: async (workspaceId) => {
    set({ isLoading: true, error: null });
    try {
      const evolution = await bcmApi.fetchEvolution(workspaceId);
      set({ evolution });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
    } finally {
      set({ isLoading: false });
    }
  },

  recordInteraction: async (data) => {
    set({ isLoading: true, error: null });
    try {
      await bcmApi.recordInteraction(data);
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },

  setError: (error) => {
    set({ error });
  }
}));
