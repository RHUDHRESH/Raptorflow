/**
 * Move Service - Supabase client operations for Move System
 * Handles CRUD operations for moves, maneuver types, and related entities
 */

import { supabase } from '../supabase';

export interface Move {
  id: string;
  workspace_id: string;
  maneuver_type_id: string;
  sprint_id?: string;
  line_of_operation_id?: string;
  name: string;
  primary_icp_id: string;
  secondary_icp_ids?: string[];
  status: string;
  ooda_config?: any;
  fogg_config?: any;
  goal?: string;
  channels?: string[];
  content_frequency?: string;
  action_types?: string[];
  key_metrics?: any;
  decision_checkpoints?: any;
  start_date?: string;
  end_date?: string;
  progress_percentage?: number;
  owner_id?: string;
  health_status?: 'green' | 'amber' | 'red';
  created_at?: string;
  updated_at?: string;
}

export interface ManeuverType {
  id: string;
  name: string;
  category: string;
  base_duration_days: number;
  fogg_role?: string;
  intensity_score?: number;
  risk_profile?: string;
  description?: string;
  default_config?: any;
  created_at?: string;
}

export interface LineOfOperation {
  id: string;
  workspace_id: string;
  name: string;
  strategic_objective?: string;
  seasonality_tag?: string;
  center_of_gravity?: string;
  status?: string;
  start_date?: string;
  target_date?: string;
  created_at?: string;
}

export interface MoveAnomaly {
  id: string;
  move_id: string;
  type: string;
  severity: number;
  description?: string;
  detected_at?: string;
  resolution?: string;
  resolved_at?: string;
  status?: string;
}

export class MoveService {
  /**
   * Get all maneuver types (templates)
   */
  async getManeuverTypes(): Promise<ManeuverType[]> {
    if (!supabase) {
      console.warn('Supabase not configured, returning empty array');
      return [];
    }

    const { data, error } = await supabase
      .from('maneuver_types')
      .select('*')
      .order('name');
    
    if (error) {
      console.error('Error fetching maneuver types:', error);
      throw error;
    }

    return data || [];
  }

  /**
   * Get maneuver type by ID
   */
  async getManeuverType(id: string): Promise<ManeuverType | null> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    const { data, error } = await supabase
      .from('maneuver_types')
      .select('*')
      .eq('id', id)
      .single();
    
    if (error) {
      console.error('Error fetching maneuver type:', error);
      throw error;
    }

    return data;
  }

  /**
   * Get maneuver types by category
   */
  async getManeuverTypesByCategory(category: string): Promise<ManeuverType[]> {
    if (!supabase) {
      return [];
    }

    const { data, error } = await supabase
      .from('maneuver_types')
      .select('*')
      .eq('category', category)
      .order('name');
    
    if (error) {
      console.error('Error fetching maneuver types by category:', error);
      return [];
    }

    return data || [];
  }

  /**
   * Get all moves for a workspace
   */
  async getMoves(workspaceId: string): Promise<Move[]> {
    if (!supabase) {
      console.warn('Supabase not configured, returning empty array');
      return [];
    }

    const { data, error } = await supabase
      .from('moves')
      .select('*')
      .eq('workspace_id', workspaceId)
      .order('created_at', { ascending: false });
    
    if (error) {
      console.error('Error fetching moves:', error);
      throw error;
    }

    return data || [];
  }

  /**
   * Get move by ID
   */
  async getMove(moveId: string): Promise<Move | null> {
    if (!supabase) {
      return null;
    }

    const { data, error } = await supabase
      .from('moves')
      .select('*')
      .eq('id', moveId)
      .single();
    
    if (error) {
      console.error('Error fetching move:', error);
      throw error;
    }

    return data;
  }

  /**
   * Create a new move
   */
  async createMove(move: Omit<Move, 'id' | 'created_at' | 'updated_at'>): Promise<Move> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('moves')
      .insert([move])
      .select()
      .single();
    
    if (error) {
      console.error('Error creating move:', error);
      throw error;
    }

    return data;
  }

  /**
   * Update a move
   */
  async updateMove(moveId: string, updates: Partial<Move>): Promise<Move> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('moves')
      .update(updates)
      .eq('id', moveId)
      .select()
      .single();
    
    if (error) {
      console.error('Error updating move:', error);
      throw error;
    }

    return data;
  }

  /**
   * Delete a move
   */
  async deleteMove(moveId: string): Promise<void> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { error } = await supabase
      .from('moves')
      .delete()
      .eq('id', moveId);
    
    if (error) {
      console.error('Error deleting move:', error);
      throw error;
    }
  }

  /**
   * Get moves by sprint
   */
  async getMovesBySprint(sprintId: string): Promise<Move[]> {
    if (!supabase) {
      return [];
    }

    const { data, error } = await supabase
      .from('moves')
      .select('*')
      .eq('sprint_id', sprintId)
      .order('created_at', { ascending: false });
    
    if (error) {
      console.error('Error fetching moves by sprint:', error);
      return [];
    }

    return data || [];
  }

  /**
   * Get lines of operation for a workspace
   */
  async getLinesOfOperation(workspaceId: string): Promise<LineOfOperation[]> {
    if (!supabase) {
      return [];
    }

    const { data, error } = await supabase
      .from('lines_of_operation')
      .select('*')
      .eq('workspace_id', workspaceId)
      .order('created_at', { ascending: false });
    
    if (error) {
      console.error('Error fetching lines of operation:', error);
      return [];
    }

    return data || [];
  }

  /**
   * Create a line of operation
   */
  async createLineOfOperation(loo: Omit<LineOfOperation, 'id' | 'created_at'>): Promise<LineOfOperation> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('lines_of_operation')
      .insert([loo])
      .select()
      .single();
    
    if (error) {
      console.error('Error creating line of operation:', error);
      throw error;
    }

    return data;
  }

  /**
   * Get anomalies for a move
   */
  async getMoveAnomalies(moveId: string): Promise<MoveAnomaly[]> {
    if (!supabase) {
      return [];
    }

    const { data, error } = await supabase
      .from('move_anomalies')
      .select('*')
      .eq('move_id', moveId)
      .order('detected_at', { ascending: false });
    
    if (error) {
      console.error('Error fetching move anomalies:', error);
      return [];
    }

    return data || [];
  }

  /**
   * Create anomaly for a move
   */
  async createAnomaly(anomaly: Omit<MoveAnomaly, 'id' | 'detected_at'>): Promise<MoveAnomaly> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('move_anomalies')
      .insert([{
        ...anomaly,
        detected_at: new Date().toISOString(),
      }])
      .select()
      .single();
    
    if (error) {
      console.error('Error creating anomaly:', error);
      throw error;
    }

    return data;
  }

  /**
   * Update anomaly status
   */
  async updateAnomaly(anomalyId: string, updates: Partial<MoveAnomaly>): Promise<MoveAnomaly> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('move_anomalies')
      .update(updates)
      .eq('id', anomalyId)
      .select()
      .single();
    
    if (error) {
      console.error('Error updating anomaly:', error);
      throw error;
    }

    return data;
  }

  /**
   * Get prerequisites for a maneuver type
   */
  async getManeuverPrerequisites(maneuverTypeId: string): Promise<string[]> {
    if (!supabase) {
      return [];
    }

    const { data, error } = await supabase
      .from('maneuver_prerequisites')
      .select('required_capability_id')
      .eq('maneuver_type_id', maneuverTypeId);
    
    if (error) {
      console.error('Error fetching prerequisites:', error);
      return [];
    }

    return (data || []).map((p: any) => p.required_capability_id);
  }
}

// Export singleton instance
export const moveService = new MoveService();


