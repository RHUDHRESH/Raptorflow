/**
 * Quick Wins Service
 * Handles daily sweep opportunities and intelligence-driven suggestions
 */

import { supabase } from '../supabase';

export interface QuickWin {
  id: string;
  workspace_id: string;
  title: string;
  summary: string;
  source_type: 'news' | 'internal_asset' | 'trend' | 'support_insight';
  source_url?: string;
  source_data: Record<string, any>;
  target_cohort_ids: string[];
  matched_tags: string[];
  suggested_move_type?: string;
  suggested_assets: string[];
  micro_asset_suggestions: Array<{
    type: string;
    description: string;
    example: string;
  }>;
  status: 'New' | 'Reviewed' | 'Actioned' | 'Dismissed';
  priority_score: number;
  expires_at?: string;
  created_at: string;
  actioned_at?: string;
}

export const quickWinsService = {
  /**
   * Get all quick wins for the current workspace
   */
  async getAll(filters?: {
    status?: QuickWin['status'];
    cohortId?: string;
  }): Promise<QuickWin[]> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return [];
    }

    let query = supabase
      .from('quick_wins')
      .select('*')
      .order('priority_score', { ascending: false })
      .order('created_at', { ascending: false });

    if (filters?.status) {
      query = query.eq('status', filters.status);
    }

    if (filters?.cohortId) {
      query = query.contains('target_cohort_ids', [filters.cohortId]);
    }

    const { data, error } = await query;

    if (error) {
      console.error('Error fetching quick wins:', error);
      throw error;
    }

    return data || [];
  },

  /**
   * Get a single quick win by ID
   */
  async getById(id: string): Promise<QuickWin | null> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    const { data, error } = await supabase
      .from('quick_wins')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      console.error('Error fetching quick win:', error);
      throw error;
    }

    return data;
  },

  /**
   * Create a new quick win
   */
  async create(quickWin: Omit<QuickWin, 'id' | 'workspace_id' | 'created_at'>): Promise<QuickWin> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('quick_wins')
      .insert(quickWin)
      .select()
      .single();

    if (error) {
      console.error('Error creating quick win:', error);
      throw error;
    }

    return data;
  },

  /**
   * Update quick win status
   */
  async updateStatus(id: string, status: QuickWin['status']): Promise<QuickWin> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const updates: any = { status };
    if (status === 'Actioned') {
      updates.actioned_at = new Date().toISOString();
    }

    const { data, error } = await supabase
      .from('quick_wins')
      .update(updates)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      console.error('Error updating quick win:', error);
      throw error;
    }

    return data;
  },

  /**
   * Mark a quick win as actioned
   */
  async markActioned(id: string, actionDetails?: {
    moveId?: string;
    notes?: string;
  }): Promise<QuickWin> {
    return await this.updateStatus(id, 'Actioned');
  },

  /**
   * Dismiss a quick win
   */
  async dismiss(id: string): Promise<QuickWin> {
    return await this.updateStatus(id, 'Dismissed');
  },

  /**
   * Generate quick wins from news items (placeholder for AI integration)
   */
  async generateFromNews(
    newsItems: Array<{ title: string; summary: string; url: string }>,
    cohorts: Array<{ id: string; tags: string[] }>
  ): Promise<QuickWin[]> {
    // TODO: Implement AI integration
    // This would call your AI service to analyze news and match to cohorts
    return [];
  },

  /**
   * Generate quick wins from internal assets (placeholder for AI integration)
   */
  async generateFromInternalAssets(
    searchQuery: string,
    cohorts: Array<{ id: string; tags: string[] }>
  ): Promise<QuickWin[]> {
    // TODO: Implement AI integration
    // This would search internal assets and suggest opportunities
    return [];
  },

  /**
   * Delete expired quick wins (maintenance function)
   */
  async deleteExpired(): Promise<number> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const now = new Date().toISOString();
    
    const { data, error } = await supabase
      .from('quick_wins')
      .delete()
      .lt('expires_at', now)
      .select();

    if (error) {
      console.error('Error deleting expired quick wins:', error);
      throw error;
    }

    return data?.length || 0;
  }
};

