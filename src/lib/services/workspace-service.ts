/**
 * Workspace Service
 * Handles workspace and multi-user operations
 */

import { supabase } from '../supabase';

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  plan: 'Ascent' | 'Glide' | 'Soar';
  cohorts_limit: number;
  moves_per_sprint_limit: number;
  created_at: string;
  updated_at: string;
}

export interface UserWorkspace {
  id: string;
  user_id: string;
  workspace_id: string;
  role: 'Owner' | 'Strategist' | 'Creator' | 'Analyst' | 'Viewer';
  joined_at: string;
}

export interface WorkspaceMember {
  id: string;
  user_id: string;
  email: string;
  name?: string;
  role: UserWorkspace['role'];
  joined_at: string;
}

export const workspaceService = {
  /**
   * Get current workspace
   */
  async getCurrentWorkspace(): Promise<Workspace | null> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    // First get user's workspace ID from user_workspaces
    const { data: membership, error: memberError } = await supabase
      .from('user_workspaces')
      .select('workspace_id')
      .limit(1)
      .single();

    if (memberError || !membership) {
      console.error('Error fetching user workspace:', memberError);
      return null;
    }

    const { data, error } = await supabase
      .from('workspaces')
      .select('*')
      .eq('id', membership.workspace_id)
      .single();

    if (error) {
      console.error('Error fetching workspace:', error);
      return null;
    }

    return data;
  },

  /**
   * Get all workspaces the current user belongs to
   */
  async getUserWorkspaces(): Promise<Workspace[]> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return [];
    }

    const { data: memberships, error: memberError } = await supabase
      .from('user_workspaces')
      .select('workspace_id');

    if (memberError) {
      console.error('Error fetching user workspaces:', memberError);
      return [];
    }

    const workspaceIds = memberships.map(m => m.workspace_id);

    const { data, error } = await supabase
      .from('workspaces')
      .select('*')
      .in('id', workspaceIds);

    if (error) {
      console.error('Error fetching workspaces:', error);
      return [];
    }

    return data || [];
  },

  /**
   * Create a new workspace
   */
  async createWorkspace(workspace: {
    name: string;
    slug: string;
    plan?: Workspace['plan'];
  }): Promise<Workspace> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('workspaces')
      .insert({
        ...workspace,
        plan: workspace.plan || 'Ascent',
        cohorts_limit: workspace.plan === 'Soar' ? 50 : workspace.plan === 'Glide' ? 10 : 3,
        moves_per_sprint_limit: workspace.plan === 'Soar' ? 20 : workspace.plan === 'Glide' ? 10 : 5
      })
      .select()
      .single();

    if (error) {
      console.error('Error creating workspace:', error);
      throw error;
    }

    // Add current user as owner
    const { data: { user } } = await supabase.auth.getUser();
    if (user) {
      await this.addMember(data.id, user.id, 'Owner');
    }

    return data;
  },

  /**
   * Update workspace
   */
  async updateWorkspace(id: string, updates: Partial<Workspace>): Promise<Workspace> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('workspaces')
      .update(updates)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      console.error('Error updating workspace:', error);
      throw error;
    }

    return data;
  },

  /**
   * Get workspace members
   */
  async getWorkspaceMembers(workspaceId: string): Promise<WorkspaceMember[]> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return [];
    }

    const { data, error } = await supabase
      .from('user_workspaces')
      .select('id, user_id, role, joined_at')
      .eq('workspace_id', workspaceId);

    if (error) {
      console.error('Error fetching workspace members:', error);
      return [];
    }

    // Note: In production, you'd join with a users table to get email/name
    // For now, return with placeholder data
    return (data || []).map(member => ({
      ...member,
      email: `user_${member.user_id.substring(0, 8)}@example.com`,
      name: `User ${member.user_id.substring(0, 8)}`
    }));
  },

  /**
   * Add a member to workspace
   */
  async addMember(
    workspaceId: string,
    userId: string,
    role: UserWorkspace['role'] = 'Viewer'
  ): Promise<UserWorkspace> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('user_workspaces')
      .insert({
        workspace_id: workspaceId,
        user_id: userId,
        role
      })
      .select()
      .single();

    if (error) {
      console.error('Error adding member:', error);
      throw error;
    }

    return data;
  },

  /**
   * Update member role
   */
  async updateMemberRole(
    workspaceId: string,
    userId: string,
    role: UserWorkspace['role']
  ): Promise<UserWorkspace> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('user_workspaces')
      .update({ role })
      .eq('workspace_id', workspaceId)
      .eq('user_id', userId)
      .select()
      .single();

    if (error) {
      console.error('Error updating member role:', error);
      throw error;
    }

    return data;
  },

  /**
   * Remove member from workspace
   */
  async removeMember(workspaceId: string, userId: string): Promise<void> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { error } = await supabase
      .from('user_workspaces')
      .delete()
      .eq('workspace_id', workspaceId)
      .eq('user_id', userId);

    if (error) {
      console.error('Error removing member:', error);
      throw error;
    }
  },

  /**
   * Get user's role in workspace
   */
  async getUserRole(workspaceId: string): Promise<UserWorkspace['role'] | null> {
    if (!supabase) {
      return null;
    }

    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return null;

    const { data, error } = await supabase
      .from('user_workspaces')
      .select('role')
      .eq('workspace_id', workspaceId)
      .eq('user_id', user.id)
      .single();

    if (error) {
      console.error('Error fetching user role:', error);
      return null;
    }

    return data?.role || null;
  },

  /**
   * Invite member by email (placeholder - needs email integration)
   */
  async inviteMember(
    workspaceId: string,
    email: string,
    role: UserWorkspace['role']
  ): Promise<void> {
    // This would send an email invitation
    // For now, just log
    console.log(`Invite sent to ${email} for workspace ${workspaceId} with role ${role}`);
    // Implement with email service (Supabase Auth or external)
  }
};

