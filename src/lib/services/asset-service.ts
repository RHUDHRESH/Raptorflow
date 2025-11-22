/**
 * Asset Service
 * Handles CRUD operations for content/creative assets
 */

import { supabase } from '../supabase';

export interface Asset {
  id: string;
  workspace_id: string;
  move_id?: string;
  icp_id?: string;
  name: string;
  type: 'case_study' | 'whitepaper' | 'video' | 'blog_post' | 'social_post' | 'email' | 'landing_page' | 'creative' | 'template' | 'other';
  status: 'draft' | 'review' | 'approved' | 'published' | 'archived';
  url?: string;
  file_path?: string;
  thumbnail_url?: string;
  description?: string;
  tags?: string[];
  metadata?: {
    word_count?: number;
    duration?: number;
    platform?: string;
    campaign?: string;
    [key: string]: any;
  };
  created_by?: string;
  created_at?: string;
  updated_at?: string;
  published_at?: string;
}

export interface AssetUsageStats {
  asset_id: string;
  views?: number;
  clicks?: number;
  conversions?: number;
  engagement_rate?: number;
}

export const assetService = {
  /**
   * Get all assets for the current workspace
   */
  async getAll(): Promise<Asset[]> {
    if (!supabase) {
      console.warn('Supabase not configured, returning empty array');
      return [];
    }

    const { data, error } = await supabase
      .from('assets')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching assets:', error);
      throw error;
    }

    return data || [];
  },

  /**
   * Get asset by ID
   */
  async getById(id: string): Promise<Asset | null> {
    if (!supabase) {
      return null;
    }

    const { data, error } = await supabase
      .from('assets')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      console.error('Error fetching asset:', error);
      throw error;
    }

    return data;
  },

  /**
   * Get assets by move ID
   */
  async getByMove(moveId: string): Promise<Asset[]> {
    if (!supabase) {
      return [];
    }

    const { data, error } = await supabase
      .from('assets')
      .select('*')
      .eq('move_id', moveId)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching assets by move:', error);
      return [];
    }

    return data || [];
  },

  /**
   * Get assets by ICP
   */
  async getByICP(icpId: string): Promise<Asset[]> {
    if (!supabase) {
      return [];
    }

    const { data, error } = await supabase
      .from('assets')
      .select('*')
      .eq('icp_id', icpId)
      .order('created_at', { ascending: false});

    if (error) {
      console.error('Error fetching assets by ICP:', error);
      return [];
    }

    return data || [];
  },

  /**
   * Get assets by type
   */
  async getByType(type: Asset['type']): Promise<Asset[]> {
    if (!supabase) {
      return [];
    }

    const { data, error } = await supabase
      .from('assets')
      .select('*')
      .eq('type', type)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching assets by type:', error);
      return [];
    }

    return data || [];
  },

  /**
   * Get assets by status
   */
  async getByStatus(status: Asset['status']): Promise<Asset[]> {
    if (!supabase) {
      return [];
    }

    const { data, error } = await supabase
      .from('assets')
      .select('*')
      .eq('status', status)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching assets by status:', error);
      return [];
    }

    return data || [];
  },

  /**
   * Create a new asset
   */
  async create(asset: Omit<Asset, 'id' | 'created_at' | 'updated_at'>): Promise<Asset> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('assets')
      .insert([asset])
      .select()
      .single();

    if (error) {
      console.error('Error creating asset:', error);
      throw error;
    }

    return data;
  },

  /**
   * Update an asset
   */
  async update(id: string, updates: Partial<Asset>): Promise<Asset> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('assets')
      .update(updates)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      console.error('Error updating asset:', error);
      throw error;
    }

    return data;
  },

  /**
   * Delete an asset
   */
  async delete(id: string): Promise<void> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { error } = await supabase
      .from('assets')
      .delete()
      .eq('id', id);

    if (error) {
      console.error('Error deleting asset:', error);
      throw error;
    }
  },

  /**
   * Update asset status
   */
  async updateStatus(id: string, status: Asset['status']): Promise<Asset> {
    const updates: Partial<Asset> = { status };
    
    if (status === 'published') {
      updates.published_at = new Date().toISOString();
    }

    return this.update(id, updates);
  },

  /**
   * Search assets
   */
  async search(query: string): Promise<Asset[]> {
    if (!supabase) {
      return [];
    }

    const { data, error } = await supabase
      .from('assets')
      .select('*')
      .or(`name.ilike.%${query}%,description.ilike.%${query}%`)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error searching assets:', error);
      return [];
    }

    return data || [];
  },

  /**
   * Get assets by tags
   */
  async getByTags(tags: string[]): Promise<Asset[]> {
    if (!supabase || tags.length === 0) {
      return [];
    }

    const { data, error } = await supabase
      .from('assets')
      .select('*')
      .overlaps('tags', tags)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching assets by tags:', error);
      return [];
    }

    return data || [];
  },

  /**
   * Get asset counts by status
   */
  async getStatusCounts(): Promise<Record<string, number>> {
    if (!supabase) {
      return {};
    }

    const { data, error } = await supabase
      .from('assets')
      .select('status');

    if (error) {
      console.error('Error fetching asset counts:', error);
      return {};
    }

    const counts: Record<string, number> = {
      draft: 0,
      review: 0,
      approved: 0,
      published: 0,
      archived: 0,
    };

    data?.forEach((asset: any) => {
      if (asset.status && counts.hasOwnProperty(asset.status)) {
        counts[asset.status]++;
      }
    });

    return counts;
  },

  /**
   * Get recent assets
   */
  async getRecent(limit: number = 10): Promise<Asset[]> {
    if (!supabase) {
      return [];
    }

    const { data, error } = await supabase
      .from('assets')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(limit);

    if (error) {
      console.error('Error fetching recent assets:', error);
      return [];
    }

    return data || [];
  },
};


