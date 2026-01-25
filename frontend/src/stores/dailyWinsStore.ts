import { create } from 'zustand';

interface DailyWin {
  id: string;
  content: string;
  platform: string;
  icp_id?: string;
  action_type: string;
  energy_level: 'high' | 'medium' | 'low';
  completed_at?: string;
  created_at: string;
  user_id: string;
  workspace_id: string;
}

interface DailyWinsStore {
  wins: Record<string, DailyWin>;
  currentWin: DailyWin | null;
  isLoading: boolean;
  error: string | null;
  streak: number;

  // Actions
  setWins: (wins: DailyWin[]) => void;
  setCurrentWin: (win: DailyWin | null) => void;
  generateWin: (data: {
    workspace_id: string;
    user_id: string;
    platform?: string;
    force_refresh?: boolean;
  }) => Promise<DailyWin>;
  completeWin: (id: string) => Promise<void>;
  fetchWins: (workspace_id: string, user_id: string) => Promise<void>;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// API helper functions
const dailyWinsApi = {
  async generateWin(data: {
    workspace_id: string;
    user_id: string;
    platform?: string;
    force_refresh?: boolean;
  }): Promise<DailyWin> {
    const response = await fetch('/api/proxy/api/v1/daily_wins/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to generate daily win');
    }

    const result = await response.json();
    return result.win;
  },

  async fetchWins(workspace_id: string, user_id: string): Promise<DailyWin[]> {
    const response = await fetch(`/api/proxy/api/v1/daily_wins/?workspace_id=${workspace_id}&user_id=${user_id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch daily wins');
    }

    const data = await response.json();
    return data.wins || [];
  },

  async completeWin(id: string): Promise<void> {
    const response = await fetch(`/api/proxy/api/v1/daily_wins/${id}/complete`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error('Failed to complete daily win');
    }
  }
};

export const useDailyWinsStore = create<DailyWinsStore>((set, get) => ({
  wins: {},
  currentWin: null,
  isLoading: false,
  error: null,
  streak: 0,

  setWins: (wins) => {
    const winsMap = wins.reduce((acc, win) => {
      acc[win.id] = win;
      return acc;
    }, {} as Record<string, DailyWin>);

    set({ wins: winsMap });
  },

  setCurrentWin: (win) => {
    set({ currentWin: win });
  },

  generateWin: async (data) => {
    set({ isLoading: true, error: null });
    try {
      const win = await dailyWinsApi.generateWin(data);
      set(state => ({
        wins: {
          ...state.wins,
          [win.id]: win
        },
        currentWin: win
      }));
      return win;
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  completeWin: async (id) => {
    set({ isLoading: true, error: null });
    try {
      await dailyWinsApi.completeWin(id);
      set(state => ({
        wins: {
          ...state.wins,
          [id]: {
            ...state.wins[id],
            completed_at: new Date().toISOString()
          }
        }
      }));
    } catch (error) {
      set({ error: error instanceof Error ? error.message : 'Unknown error' });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  fetchWins: async (workspace_id, user_id) => {
    set({ isLoading: true, error: null });
    try {
      const wins = await dailyWinsApi.fetchWins(workspace_id, user_id);
      get().setWins(wins);

      // Calculate streak (simplified - in real app would use proper streak logic)
      const completedWins = wins.filter(win => win.completed_at);
      set({ streak: completedWins.length });
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
