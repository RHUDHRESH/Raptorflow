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
      // Assuming apiClient has a getDashboardSummary method or we use fetch
      const response = await fetch('/api/v1/dashboard/summary');
      if (!response.ok) throw new Error('Failed to fetch dashboard summary');
      
      const data = await response.json();
      if (data.success) {
        set({ summary: data, isLoading: false });
      } else {
        throw new Error(data.error || 'Unknown error');
      }
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Dashboard fetch failed',
        isLoading: false 
      });
    }
  }
}));
