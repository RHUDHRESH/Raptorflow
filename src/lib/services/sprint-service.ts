/**
 * Sprint Service
 * Handles sprint management and capacity calculations
 */

import { supabase } from '../supabase';

export interface Sprint {
  id: string;
  workspace_id: string;
  name?: string;
  start_date: string;
  end_date: string;
  theme?: string;
  capacity_budget: number;
  current_load: number;
  season_type?: 'High_Season' | 'Low_Season' | 'Shoulder';
  status: 'Planning' | 'Active' | 'Review' | 'Complete';
  created_at?: string;
}

export const sprintService = {
  /**
   * Get all sprints for the current workspace
   */
  async getAll(): Promise<Sprint[]> {
    if (!supabase) {
      console.warn('Supabase not configured, returning empty array');
      return [];
    }

    const { data, error } = await supabase
      .from('sprints')
      .select('*')
      .order('start_date', { ascending: false });

    if (error) {
      console.error('Error fetching sprints:', error);
      throw error;
    }

    return data || [];
  },

  /**
   * Get active sprint
   */
  async getActive(): Promise<Sprint | null> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    const { data, error } = await supabase
      .from('sprints')
      .select('*')
      .eq('status', 'Active')
      .order('start_date', { ascending: false })
      .limit(1)
      .single();

    if (error && error.code !== 'PGRST116') { // PGRST116 = no rows returned
      console.error('Error fetching active sprint:', error);
      throw error;
    }

    return data;
  },

  /**
   * Get sprint by ID
   */
  async getById(id: string): Promise<Sprint | null> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    const { data, error } = await supabase
      .from('sprints')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      console.error('Error fetching sprint:', error);
      throw error;
    }

    return data;
  },

  /**
   * Create a new sprint
   */
  async create(sprint: Omit<Sprint, 'id' | 'created_at'>): Promise<Sprint> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('sprints')
      .insert([sprint])
      .select()
      .single();

    if (error) {
      console.error('Error creating sprint:', error);
      throw error;
    }

    return data;
  },

  /**
   * Update a sprint
   */
  async update(id: string, updates: Partial<Sprint>): Promise<Sprint> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('sprints')
      .update(updates)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      console.error('Error updating sprint:', error);
      throw error;
    }

    return data;
  },

  /**
   * Delete a sprint
   */
  async delete(id: string): Promise<void> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { error } = await supabase
      .from('sprints')
      .delete()
      .eq('id', id);

    if (error) {
      console.error('Error deleting sprint:', error);
      throw error;
    }
  },

  /**
   * Calculate available capacity
   */
  getAvailableCapacity(sprint: Sprint): number {
    return sprint.capacity_budget - sprint.current_load;
  },

  /**
   * Check if sprint has capacity for a move
   */
  hasCapacity(sprint: Sprint, requiredCapacity: number): boolean {
    return this.getAvailableCapacity(sprint) >= requiredCapacity;
  },

  /**
   * Get capacity percentage used
   */
  getCapacityPercentage(sprint: Sprint): number {
    if (sprint.capacity_budget === 0) return 0;
    return Math.round((sprint.current_load / sprint.capacity_budget) * 100);
  },

  /**
   * Update sprint load (when moves are added/removed)
   */
  async updateLoad(sprintId: string, loadChange: number): Promise<Sprint> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    // Get current sprint
    const sprint = await this.getById(sprintId);
    if (!sprint) {
      throw new Error('Sprint not found');
    }

    const newLoad = Math.max(0, sprint.current_load + loadChange);

    return this.update(sprintId, { current_load: newLoad });
  },

  /**
   * Recalculate sprint load from moves
   */
  async recalculateLoad(sprintId: string): Promise<Sprint> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    // Get all moves in this sprint
    const { data: moves, error } = await supabase
      .from('moves')
      .select('*')
      .eq('sprint_id', sprintId);

    if (error) {
      console.error('Error fetching moves for sprint:', error);
      throw error;
    }

    // Sum up intensity scores from move types
    // In production, you'd join with maneuver_types to get intensity_score
    const totalLoad = moves?.length || 0; // Simplified: count of moves
    
    return this.update(sprintId, { current_load: totalLoad });
  },

  /**
   * Complete a sprint
   */
  async complete(id: string): Promise<Sprint> {
    return this.update(id, { status: 'Complete' });
  },

  /**
   * Start a sprint
   */
  async start(id: string): Promise<Sprint> {
    return this.update(id, { status: 'Active' });
  },

  /**
   * Get sprints in date range
   */
  async getInDateRange(startDate: string, endDate: string): Promise<Sprint[]> {
    if (!supabase) {
      console.warn('Supabase not configured, returning empty array');
      return [];
    }

    const { data, error } = await supabase
      .from('sprints')
      .select('*')
      .gte('start_date', startDate)
      .lte('end_date', endDate)
      .order('start_date', { ascending: true });

    if (error) {
      console.error('Error fetching sprints in date range:', error);
      throw error;
    }

    return data || [];
  },

  /**
   * Get upcoming sprints
   */
  async getUpcoming(limit: number = 5): Promise<Sprint[]> {
    if (!supabase) {
      console.warn('Supabase not configured, returning empty array');
      return [];
    }

    const today = new Date().toISOString().split('T')[0];

    const { data, error } = await supabase
      .from('sprints')
      .select('*')
      .gte('start_date', today)
      .order('start_date', { ascending: true })
      .limit(limit);

    if (error) {
      console.error('Error fetching upcoming sprints:', error);
      throw error;
    }

    return data || [];
  },

  /**
   * Get past sprints
   */
  async getPast(limit: number = 10): Promise<Sprint[]> {
    if (!supabase) {
      console.warn('Supabase not configured, returning empty array');
      return [];
    }

    const today = new Date().toISOString().split('T')[0];

    const { data, error } = await supabase
      .from('sprints')
      .select('*')
      .lt('end_date', today)
      .order('end_date', { ascending: false })
      .limit(limit);

    if (error) {
      console.error('Error fetching past sprints:', error);
      throw error;
    }

    return data || [];
  },
};



