import { create } from 'zustand';
import { apiClient } from '@/lib/api/client';

export interface DashboardSummary {
  workspace_stats: {
    name: string;
    total_wins: number;
  };
  active_moves: any[];
  active_campaigns: any[];
  recent_muse_assets: any[];
  evolution_index: number;
  daily_wins_streak: number;
}

interface DashboardState {
  summary: DashboardSummary | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchSummary: () => Promise<void>;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  summary: null,
  isLoading: false,
  error: null,

  fetchSummary: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.getDashboardSummary();
      if (response.success) {
        set({ summary: response as unknown as DashboardSummary, isLoading: false });
      } else {
        throw new Error(response.error as string || 'Unknown error');
      }
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Dashboard fetch failed',
        isLoading: false 
      });
    }
  }
}));
