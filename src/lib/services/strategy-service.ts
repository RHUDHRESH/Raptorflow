/**
 * Strategy Service
 * Handles CRUD operations for global strategy and constitution
 */

import { supabase } from '../supabase';

export interface GlobalStrategy {
  id: string;
  workspace_id: string;
  business_context: {
    company_name: string;
    industry: string;
    stage: string;
    team_size: string;
  };
  offers: Array<{
    name: string;
    description: string;
    pricing: string;
    target_segment: string;
  }>;
  markets: Array<{
    geography: string;
    channels: string[];
    positioning: string;
  }>;
  center_of_gravity: string;
  success_metrics: {
    primary_metric: string;
    target_value: string;
    timeframe: string;
  };
  ninety_day_goal: string;
  constitution: {
    tone_guidelines: string[];
    forbidden_tactics: string[];
    brand_values: string[];
    constraints: string[];
  };
  strategy_state: 'Draft' | 'Active' | 'Archived';
  created_at?: string;
  updated_at?: string;
}

export const strategyService = {
  /**
   * Get the current workspace's strategy
   */
  async getWorkspaceStrategy(): Promise<GlobalStrategy | null> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    const { data, error } = await supabase
      .from('global_strategies')
      .select('*')
      .single();

    if (error) {
      // PGRST116 = no rows returned, which is fine for first-time users
      if (error.code === 'PGRST116') {
        return null;
      }
      console.error('Error fetching strategy:', error);
      throw error;
    }

    return data;
  },

  /**
   * Create a new strategy for the workspace
   */
  async createStrategy(strategy: Partial<GlobalStrategy>): Promise<GlobalStrategy> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('global_strategies')
      .insert({
        ...strategy,
        strategy_state: strategy.strategy_state || 'Draft'
      })
      .select()
      .single();

    if (error) {
      console.error('Error creating strategy:', error);
      throw error;
    }

    return data;
  },

  /**
   * Update an existing strategy
   */
  async updateStrategy(id: string, updates: Partial<GlobalStrategy>): Promise<GlobalStrategy> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('global_strategies')
      .update(updates)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      console.error('Error updating strategy:', error);
      throw error;
    }

    return data;
  },

  /**
   * Update constitution rules
   */
  async updateConstitution(
    constitutionUpdates: Partial<GlobalStrategy['constitution']>
  ): Promise<GlobalStrategy> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    // First get current strategy
    const current = await this.getWorkspaceStrategy();
    if (!current) {
      throw new Error('No strategy found. Create one first.');
    }

    const updatedConstitution = {
      ...current.constitution,
      ...constitutionUpdates
    };

    return await this.updateStrategy(current.id, {
      constitution: updatedConstitution
    });
  },

  /**
   * Activate a draft strategy
   */
  async activateStrategy(id: string): Promise<GlobalStrategy> {
    return await this.updateStrategy(id, { strategy_state: 'Active' });
  },

  /**
   * Archive a strategy
   */
  async archiveStrategy(id: string): Promise<GlobalStrategy> {
    return await this.updateStrategy(id, { strategy_state: 'Archived' });
  },

  /**
   * Check if a workspace has a strategy
   */
  async hasStrategy(): Promise<boolean> {
    const strategy = await this.getWorkspaceStrategy();
    return strategy !== null;
  }
};

