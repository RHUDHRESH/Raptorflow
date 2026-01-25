import { create } from 'zustand';

interface Strategy {
  id: string;
  focus_area: string;
  business_context: string;
  risk_tolerance: number;
  timeline?: string;
  budget_range?: string;
  strategy: string;
  reasoning: string;
  implementation_steps: string[];
  success_metrics: string[];
  created_at: string;
  workspace_id: string;
  user_id: string;
}

interface BlackboxStore {
  strategies: Record<string, Strategy>;
  currentStrategy: Strategy | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setStrategies: (strategies: Strategy[]) => void;
  setCurrentStrategy: (strategy: Strategy | null) => void;
  generateStrategy: (data: {
    focus_area: string;
    business_context: string;
    risk_tolerance?: number;
    timeline?: string;
    budget_range?: string;
    workspace_id: string;
    user_id: string;
  }) => Promise<Strategy>;
  createMoveFromStrategy: (strategyId: string) => Promise<string>;
  fetchStrategies: (workspace_id: string, user_id: string) => Promise<void>;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// API helper functions
const blackboxApi = {
  async generateStrategy(data: {
    focus_area: string;
    business_context: string;
    risk_tolerance?: number;
    timeline?: string;
    budget_range?: string;
    workspace_id: string;
    user_id: string;
  }): Promise<Strategy> {
    const response = await fetch('/api/proxy/api/v1/blackbox/generate-strategy', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      throw new Error('Failed to generate strategy');
    }
    
    const result = await response.json();
    return result.strategy;
  },
  
  async fetchStrategies(workspace_id: string, user_id: string): Promise<Strategy[]> {
    const response = await fetch(`/api/proxy/api/v1/blackbox/strategies?workspace_id=${workspace_id}&user_id=${user_id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch strategies');
    }
    
    const data = await response.json();
    return data.strategies || [];
  },
  
  async createMoveFromStrategy(strategyId: string): Promise<{ move_id: string }> {
    const response = await fetch(`/api/proxy/api/v1/blackbox/${strategyId}/create-move`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      throw new Error('Failed to create move from strategy');
    }
    
    return response.json();
  }
};

export const useBlackboxStore = create<BlackboxStore>((set, get) => ({
  strategies: {},
  currentStrategy: null,
  isLoading: false,
  error: null,

  setStrategies: (strategies) => {
    const strategiesMap = strategies.reduce((acc, strategy) => {
      acc[strategy.id] = strategy;
      return acc;
    }, {} as Record<string, Strategy>);
    
    set({ strategies: strategiesMap });
  },

  setCurrentStrategy: (strategy) => {
    set({ currentStrategy: strategy });
  },

  generateStrategy: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const strategy = await blackboxApi.generateStrategy(data);
      set(state => ({
        strategies: {
          ...state.strategies,
          [strategy.id]: strategy
        },
        currentStrategy: strategy
      }));
      return strategy;
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  createMoveFromStrategy: async (strategyId) => {
    set({ isLoading: true, error: null });
    try {
      const result = await blackboxApi.createMoveFromStrategy(strategyId);
      
      // Also update the moves store if available
      try {
        const { useMovesStore } = await import('./movesStore');
        const movesStore = useMovesStore.getState();
        // This would need to be implemented based on the strategy-to-move conversion logic
        console.log('Created move from strategy:', result.move_id);
      } catch (error) {
        console.warn('Could not update moves store:', error);
      }
      
      return result.move_id;
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  fetchStrategies: async (workspace_id, user_id) => {
    set({ isLoading: true, error: null });
    try {
      const strategies = await blackboxApi.fetchStrategies(workspace_id, user_id);
      get().setStrategies(strategies);
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
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
