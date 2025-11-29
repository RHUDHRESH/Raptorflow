import { supabase } from '../lib/supabase';

export interface Campaign {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  objective: string;
  objective_type: 'awareness' | 'consideration' | 'conversion' | 'retention' | 'advocacy';
  status: 'planning' | 'active' | 'paused' | 'completed' | 'archived';
  start_date?: string;
  end_date?: string;
  budget?: number;
  target_metric?: string;
  target_value?: number;
  current_value?: number; // Calculated field from backend
  health_score?: number; // Calculated field from backend
  cohorts?: any[];
  channels?: any[];
  moves?: any[]; // Added for timeline view
}

export interface CampaignCreateInput {
  name: string;
  objective: string;
  objective_type: string;
  target_metric?: string;
  target_value?: number;
  budget?: number;
  start_date?: string;
  end_date?: string;
  positioning_id?: string;
  cohorts?: { cohort_id: string; journey_stage_target: string; priority: number }[];
  channels?: { channel: string; role: string; budget_allocation?: number }[];
}

export const campaignService = {
  async getCampaigns(workspaceId: string): Promise<{ data: Campaign[] | null; error: any }> {
    if (!supabase) return { data: null, error: 'Supabase client not configured' };

    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return { data: null, error: 'User not authenticated' };

      const apiUrl = (import.meta as any).env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
      
      const response = await fetch(`${apiUrl}/campaigns/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch campaigns');
      }

      const data = await response.json();
      // Transform data to match frontend expectations (e.g. add mock health/progress if missing)
      const transformedData = data.map((c: any) => ({
        ...c,
        health_score: c.health_score || 85, // Mock default for now
        current_value: c.current_value || 0,
        pacing_status: 'on_track', // Mock default
        completed_moves: 0, // Needs real count
        total_moves: 0 // Needs real count
      }));

      return { data: transformedData, error: null };
    } catch (error) {
      console.error('Error fetching campaigns:', error);
      return { data: null, error };
    }
  },

  async getCampaign(id: string): Promise<{ data: Campaign | null; error: any }> {
    if (!supabase) return { data: null, error: 'Supabase client not configured' };

    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return { data: null, error: 'User not authenticated' };

      const apiUrl = (import.meta as any).env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
      
      const response = await fetch(`${apiUrl}/campaigns/${id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch campaign');
      }

      const data = await response.json();
      return { data, error: null };
    } catch (error) {
      console.error('Error fetching campaign:', error);
      return { data: null, error };
    }
  },

  async createCampaign(campaignData: CampaignCreateInput): Promise<{ data: Campaign | null; error: any }> {
    if (!supabase) return { data: null, error: 'Supabase client not configured' };

    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return { data: null, error: 'User not authenticated' };

      const apiUrl = (import.meta as any).env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
      
      const response = await fetch(`${apiUrl}/campaigns/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
        body: JSON.stringify(campaignData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create campaign');
      }

      const data = await response.json();
      return { data, error: null };
    } catch (error) {
      console.error('Error creating campaign:', error);
      return { data: null, error };
    }
  },

  async autoplanMoves(campaignId: string): Promise<{ data: any[] | null; error: any }> {
    if (!supabase) return { data: null, error: 'Supabase client not configured' };

    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return { data: null, error: 'User not authenticated' };

      const apiUrl = (import.meta as any).env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
      
      const response = await fetch(`${apiUrl}/campaigns/${campaignId}/autoplan-moves`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to auto-plan moves');
      }

      const data = await response.json();
      return { data, error: null };
    } catch (error) {
      console.error('Error auto-planning moves:', error);
      return { data: null, error };
    }
  }
};
