/**
 * Tech Tree Service - Capability unlocking and dependencies
 * Handles logic for the tech tree progression system
 */

import { supabase } from '../supabase';

export interface CapabilityNode {
  id: string;
  workspace_id: string;
  name: string;
  tier: 'Foundation' | 'Traction' | 'Scale' | 'Dominance';
  status: 'Locked' | 'In_Progress' | 'Unlocked';
  parent_node_ids: string[];
  unlocks_maneuver_ids: string[];
  description?: string;
  completion_criteria?: any;
  created_at?: string;
  unlocked_at?: string;
}

export class TechTreeService {
  /**
   * Get all capability nodes for a workspace
   */
  async getCapabilityNodes(workspaceId: string): Promise<CapabilityNode[]> {
    if (!supabase) {
      console.warn('Supabase not configured, returning empty array');
      return [];
    }

    const { data, error } = await supabase
      .from('capability_nodes')
      .select('*')
      .eq('workspace_id', workspaceId)
      .order('tier', { ascending: true });
    
    if (error) {
      console.error('Error fetching capability nodes:', error);
      throw error;
    }

    return data || [];
  }

  /**
   * Get capability node by ID
   */
  async getCapabilityNode(nodeId: string): Promise<CapabilityNode | null> {
    if (!supabase) {
      return null;
    }

    const { data, error } = await supabase
      .from('capability_nodes')
      .select('*')
      .eq('id', nodeId)
      .single();
    
    if (error) {
      console.error('Error fetching capability node:', error);
      throw error;
    }

    return data;
  }

  /**
   * Check if a node can be unlocked
   */
  canUnlock(node: CapabilityNode, allNodes: CapabilityNode[]): boolean {
    // Check if already unlocked
    if (node.status === 'Unlocked') {
      return false;
    }

    // Check if all parent nodes are unlocked
    for (const parentId of node.parent_node_ids) {
      const parent = allNodes.find(n => n.id === parentId);
      if (!parent || parent.status !== 'Unlocked') {
        return false;
      }
    }

    return true;
  }

  /**
   * Unlock a capability node
   */
  async unlockNode(nodeId: string): Promise<CapabilityNode> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('capability_nodes')
      .update({
        status: 'Unlocked',
        unlocked_at: new Date().toISOString(),
      })
      .eq('id', nodeId)
      .select()
      .single();

    if (error) {
      console.error('Error unlocking node:', error);
      throw error;
    }

    return data;
  }

  /**
   * Set node to in progress
   */
  async setInProgress(nodeId: string): Promise<CapabilityNode> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('capability_nodes')
      .update({ status: 'In_Progress' })
      .eq('id', nodeId)
      .select()
      .single();

    if (error) {
      console.error('Error setting node in progress:', error);
      throw error;
    }

    return data;
  }

  /**
   * Get unlockable nodes (prerequisites met, not yet unlocked)
   */
  getUnlockableNodes(allNodes: CapabilityNode[]): CapabilityNode[] {
    return allNodes.filter(node => this.canUnlock(node, allNodes));
  }

  /**
   * Get nodes by tier
   */
  getNodesByTier(
    allNodes: CapabilityNode[],
    tier: 'Foundation' | 'Traction' | 'Scale' | 'Dominance'
  ): CapabilityNode[] {
    return allNodes.filter(n => n.tier === tier);
  }

  /**
   * Get nodes by status
   */
  getNodesByStatus(
    allNodes: CapabilityNode[],
    status: 'Locked' | 'In_Progress' | 'Unlocked'
  ): CapabilityNode[] {
    return allNodes.filter(n => n.status === status);
  }

  /**
   * Calculate tech tree progress
   */
  getProgress(allNodes: CapabilityNode[]): {
    total: number;
    unlocked: number;
    locked: number;
    inProgress: number;
    percentage: number;
  } {
    const total = allNodes.length;
    const unlocked = allNodes.filter(n => n.status === 'Unlocked').length;
    const inProgress = allNodes.filter(n => n.status === 'In_Progress').length;
    const locked = allNodes.filter(n => n.status === 'Locked').length;

    return {
      total,
      unlocked,
      locked,
      inProgress,
      percentage: total > 0 ? Math.round((unlocked / total) * 100) : 0,
    };
  }

  /**
   * Get maneuvers unlocked by a capability
   */
  getUnlockedManeuvers(node: CapabilityNode): string[] {
    return node.unlocks_maneuver_ids || [];
  }

  /**
   * Get next recommended capability to unlock
   */
  getNextRecommended(allNodes: CapabilityNode[]): CapabilityNode | null {
    const unlockable = this.getUnlockableNodes(allNodes);
    
    if (unlockable.length === 0) {
      return null;
    }

    // Priority: Foundation > Traction > Scale > Dominance
    const tierOrder = ['Foundation', 'Traction', 'Scale', 'Dominance'];
    
    for (const tier of tierOrder) {
      const nodesInTier = unlockable.filter(n => n.tier === tier);
      if (nodesInTier.length > 0) {
        return nodesInTier[0];
      }
    }

    return unlockable[0];
  }

  /**
   * Get dependency chain for a node
   */
  getDependencyChain(node: CapabilityNode, allNodes: CapabilityNode[]): CapabilityNode[] {
    const chain: CapabilityNode[] = [];
    const visited = new Set<string>();

    const traverse = (currentId: string) => {
      if (visited.has(currentId)) return;
      visited.add(currentId);

      const current = allNodes.find(n => n.id === currentId);
      if (!current) return;

      for (const parentId of current.parent_node_ids) {
        traverse(parentId);
      }

      chain.push(current);
    };

    traverse(node.id);
    return chain;
  }

  /**
   * Check if maneuver is unlocked (all prerequisites met)
   */
  async isManeuverUnlocked(
    maneuverTypeId: string,
    workspaceId: string
  ): Promise<boolean> {
    if (!supabase) {
      return false;
    }

    // Get required capabilities for this maneuver
    const { data: prerequisites, error: prereqError } = await supabase
      .from('maneuver_prerequisites')
      .select('required_capability_id')
      .eq('maneuver_type_id', maneuverTypeId);

    if (prereqError || !prerequisites || prerequisites.length === 0) {
      // No prerequisites means it's unlocked by default
      return true;
    }

    // Get capability nodes for this workspace
    const nodes = await this.getCapabilityNodes(workspaceId);

    // Check if all required capabilities are unlocked
    const requiredIds = prerequisites.map((p: any) => p.required_capability_id);
    return requiredIds.every(reqId => 
      nodes.some(node => node.id === reqId && node.status === 'Unlocked')
    );
  }

  /**
   * Get locked maneuver types with their missing prerequisites
   */
  async getLockedManeuvers(workspaceId: string): Promise<Array<{
    maneuverTypeId: string;
    missingCapabilities: CapabilityNode[];
  }>> {
    if (!supabase) {
      return [];
    }

    const nodes = await this.getCapabilityNodes(workspaceId);
    const lockedNodes = nodes.filter(n => n.status !== 'Unlocked');

    // Get all prerequisites
    const { data: allPrereqs } = await supabase
      .from('maneuver_prerequisites')
      .select('maneuver_type_id, required_capability_id');

    if (!allPrereqs) return [];

    // Group by maneuver type
    const result: Record<string, Set<string>> = {};
    
    for (const prereq of allPrereqs) {
      if (!result[prereq.maneuver_type_id]) {
        result[prereq.maneuver_type_id] = new Set();
      }
      
      // Check if this capability is locked
      const isLocked = lockedNodes.some(n => n.id === prereq.required_capability_id);
      if (isLocked) {
        result[prereq.maneuver_type_id].add(prereq.required_capability_id);
      }
    }

    // Convert to array format
    return Object.entries(result)
      .filter(([_, capIds]) => capIds.size > 0)
      .map(([maneuverTypeId, capIds]) => ({
        maneuverTypeId,
        missingCapabilities: nodes.filter(n => capIds.has(n.id)),
      }));
  }
}

// Export singleton instance
export const techTreeService = new TechTreeService();
