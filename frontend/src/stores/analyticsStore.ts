import { create } from 'zustand';
import { authFetch } from '../lib/auth-helpers';

interface AnalyticsDashboard {
  overview: {
    total_users: number;
    active_campaigns: number;
    engagement_rate: number;
    conversion_rate: number;
    revenue_this_month: number;
  };
  performance_metrics: {
    campaign_performance: Array<{
      campaign: string;
      roi: number;
      status: string;
    }>;
    user_engagement: {
      daily_active: number;
      weekly_active: number;
      monthly_active: number;
    };
    content_performance: {
      total_assets: number;
      avg_engagement: number;
      top_performing: string;
    };
  };
  insights: string[];
}

interface AnalyticsStore {
  dashboard: AnalyticsDashboard | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setDashboard: (dashboard: AnalyticsDashboard) => void;
  fetchDashboard: () => Promise<void>;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// API helper functions
const analyticsApi = {
  async fetchDashboard(): Promise<AnalyticsDashboard> {
    const response = await authFetch('/api/proxy/api/v1/analytics/dashboard');

    if (!response.ok) {
      throw new Error('Failed to fetch analytics dashboard');
    }

    const data = await response.json();
    return data.dashboard;
  }
};

export const useAnalyticsStore = create<AnalyticsStore>((set, get) => ({
  dashboard: null,
  isLoading: false,
  error: null,

  setDashboard: (dashboard) => {
    set({ dashboard });
  },

  fetchDashboard: async () => {
    set({ isLoading: true, error: null });
    try {
      const dashboard = await analyticsApi.fetchDashboard();
      set({ dashboard });
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
