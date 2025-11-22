/**
 * ICP (Ideal Customer Profile / Cohort) Service
 * Handles CRUD operations for customer cohorts/ICPs
 */

import { supabase } from '../supabase';

export interface ICP {
  id: string;
  workspace_id: string;
  name: string;
  executive_summary?: string;
  demographics?: {
    company_size?: string;
    industry?: string;
    revenue?: string;
    location?: string;
  };
  buyer_role?: string;
  psychographics?: {
    values?: string[];
    decision_style?: string;
    priorities?: string[];
  };
  pain_points?: string[];
  goals?: string[];
  behavioral_triggers?: string[];
  communication?: {
    channels?: string[];
    tone?: string;
    format?: string;
  };
  budget?: string;
  timeline?: string;
  decision_structure?: string;
  tags?: string[];
  created_at?: string;
  updated_at?: string;
}

export const icpService = {
  /**
   * Get all ICPs for the current workspace
   */
  async getAll(): Promise<ICP[]> {
    if (!supabase) {
      console.warn('Supabase not configured, returning empty array');
      return [];
    }

    const { data, error } = await supabase
      .from('cohorts')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching ICPs:', error);
      throw error;
    }

    return data || [];
  },

  /**
   * Get a single ICP by ID
   */
  async getById(id: string): Promise<ICP | null> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    const { data, error } = await supabase
      .from('cohorts')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      console.error('Error fetching ICP:', error);
      throw error;
    }

    return data;
  },

  /**
   * Create a new ICP
   */
  async create(icp: Omit<ICP, 'id' | 'created_at' | 'updated_at'>): Promise<ICP> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('cohorts')
      .insert([icp])
      .select()
      .single();

    if (error) {
      console.error('Error creating ICP:', error);
      throw error;
    }

    return data;
  },

  /**
   * Update an existing ICP
   */
  async update(id: string, updates: Partial<ICP>): Promise<ICP> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error} = await supabase
      .from('cohorts')
      .update(updates)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      console.error('Error updating ICP:', error);
      throw error;
    }

    return data;
  },

  /**
   * Delete an ICP
   */
  async delete(id: string): Promise<void> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { error } = await supabase
      .from('cohorts')
      .delete()
      .eq('id', id);

    if (error) {
      console.error('Error deleting ICP:', error);
      throw error;
    }
  },

  /**
   * Search ICPs by name or industry
   */
  async search(query: string): Promise<ICP[]> {
    if (!supabase) {
      console.warn('Supabase not configured, returning empty array');
      return [];
    }

    const { data, error } = await supabase
      .from('cohorts')
      .select('*')
      .or(`name.ilike.%${query}%,demographics->>industry.ilike.%${query}%`)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error searching ICPs:', error);
      throw error;
    }

    return data || [];
  },

  /**
   * Get ICPs by tag
   */
  async getByTag(tag: string): Promise<ICP[]> {
    if (!supabase) {
      console.warn('Supabase not configured, returning empty array');
      return [];
    }

    const { data, error } = await supabase
      .from('cohorts')
      .select('*')
      .contains('tags', [tag])
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching ICPs by tag:', error);
      throw error;
    }

    return data || [];
  },

  /**
   * Add tags to an ICP
   */
  async addTags(id: string, tags: string[]): Promise<ICP> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    // First get current tags
    const { data: current } = await supabase
      .from('cohorts')
      .select('tags')
      .eq('id', id)
      .single();

    const currentTags = current?.tags || [];
    const newTags = [...new Set([...currentTags, ...tags])];

    return this.update(id, { tags: newTags });
  },

  /**
   * Remove tags from an ICP
   */
  async removeTags(id: string, tagsToRemove: string[]): Promise<ICP> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    // Get current tags
    const { data: current } = await supabase
      .from('cohorts')
      .select('tags')
      .eq('id', id)
      .single();

    const currentTags = current?.tags || [];
    const newTags = currentTags.filter((t: string) => !tagsToRemove.includes(t));

    return this.update(id, { tags: newTags });
  },

  /**
   * Get count of ICPs
   */
  async getCount(): Promise<number> {
    if (!supabase) {
      return 0;
    }

    const { count, error } = await supabase
      .from('cohorts')
      .select('*', { count: 'exact', head: true });

    if (error) {
      console.error('Error counting ICPs:', error);
      return 0;
    }

    return count || 0;
  },
};



