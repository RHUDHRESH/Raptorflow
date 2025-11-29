/**
 * Workspace Service
 * Handles workspace and multi-user operations
 * Updated for Phase 2.1 schema
 */

import { supabase } from '../supabase';

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  owner_id: string;
  plan: 'starter' | 'pro' | 'max';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceMember {
  id: string;
  workspace_id: string;
  user_id: string;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  created_at: string;
}

export interface WorkspaceMemberWithProfile extends WorkspaceMember {
  email?: string;
  full_name?: string;
  avatar_url?: string;
}

export const workspaceService = {
  /**
   * Get all workspaces for the current user
   * RLS automatically filters to only workspaces the user is a member of
   */
  async getUserWorkspaces(): Promise<Workspace[]> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return [];
    }

    const { data, error } = await supabase
      .from('workspaces')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching workspaces:', error);
      return [];
    }

    return data || [];
  },

  /**
   * Get current workspace (first workspace or from localStorage)
   */
  async getCurrentWorkspace(): Promise<Workspace | null> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return null;
    }

    // Try to get from localStorage first
    const lastWorkspaceId = localStorage.getItem('lastWorkspaceId');

    if (lastWorkspaceId) {
      const { data, error } = await supabase
        .from('workspaces')
        .select('*')
        .eq('id', lastWorkspaceId)
        .single();

      if (!error && data) {
        return data;
      }
    }

    // Otherwise get first workspace
    const workspaces = await this.getUserWorkspaces();
    return workspaces.length > 0 ? workspaces[0] : null;
  },

  /**
   * Create a new workspace
   * Automatically adds the current user as owner in workspace_members
   */
  async createWorkspace(workspace: {
    name: string;
    slug?: string;
    plan?: Workspace['plan'];
  }): Promise<Workspace> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    // Get current user
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      throw new Error('User not authenticated');
    }

    // Generate slug if not provided
    const slug = workspace.slug || workspace.name.toLowerCase().replace(/\s+/g, '-');

    // Create workspace
    const { data, error } = await supabase
      .from('workspaces')
      .insert({
        name: workspace.name,
        slug,
        owner_id: user.id,
        plan: workspace.plan || 'starter',
        is_active: true
      })
      .select()
      .single();

    if (error) {
      console.error('Error creating workspace:', error);
      throw error;
    }

    // Add current user as owner in workspace_members
    const { error: memberError } = await supabase
      .from('workspace_members')
      .insert({
        workspace_id: data.id,
        user_id: user.id,
        role: 'owner'
      });

    if (memberError) {
      console.error('Error adding owner to workspace_members:', memberError);
      // Note: workspace was created, but member insertion failed
      // In production, you might want to rollback or handle this differently
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
   * Delete workspace (owner only via RLS)
   */
  async deleteWorkspace(id: string): Promise<void> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { error } = await supabase
      .from('workspaces')
      .delete()
      .eq('id', id);

    if (error) {
      console.error('Error deleting workspace:', error);
      throw error;
    }
  },

  /**
   * Get workspace members with profile information
   */
  async getWorkspaceMembers(workspaceId: string): Promise<WorkspaceMemberWithProfile[]> {
    if (!supabase) {
      console.warn('Supabase not configured');
      return [];
    }

    const { data, error } = await supabase
      .from('workspace_members')
      .select(`
        id,
        workspace_id,
        user_id,
        role,
        created_at,
        profiles:user_id (
          full_name,
          avatar_url
        )
      `)
      .eq('workspace_id', workspaceId);

    if (error) {
      console.error('Error fetching workspace members:', error);
      return [];
    }

    // Transform the data to flatten the profile info
    return (data || []).map(member => ({
      id: member.id,
      workspace_id: member.workspace_id,
      user_id: member.user_id,
      role: member.role,
      created_at: member.created_at,
      full_name: member.profiles?.full_name,
      avatar_url: member.profiles?.avatar_url
    }));
  },

  /**
   * Add a member to workspace (owner only via RLS)
   */
  async addMember(
    workspaceId: string,
    userId: string,
    role: WorkspaceMember['role'] = 'member'
  ): Promise<WorkspaceMember> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('workspace_members')
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
   * Update member role (owner only via RLS)
   */
  async updateMemberRole(
    workspaceId: string,
    userId: string,
    role: WorkspaceMember['role']
  ): Promise<WorkspaceMember> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { data, error } = await supabase
      .from('workspace_members')
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
   * Remove member from workspace (owner only via RLS)
   */
  async removeMember(workspaceId: string, userId: string): Promise<void> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    const { error } = await supabase
      .from('workspace_members')
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
  async getUserRole(workspaceId: string): Promise<WorkspaceMember['role'] | null> {
    if (!supabase) {
      return null;
    }

    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return null;

    const { data, error } = await supabase
      .from('workspace_members')
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
   * Check if user is workspace owner
   */
  async isWorkspaceOwner(workspaceId: string): Promise<boolean> {
    if (!supabase) {
      return false;
    }

    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return false;

    const { data, error } = await supabase
      .from('workspaces')
      .select('owner_id')
      .eq('id', workspaceId)
      .single();

    if (error) {
      console.error('Error checking workspace owner:', error);
      return false;
    }

    return data?.owner_id === user.id;
  },

  /**
   * Invite member by email (uses workspace_invites table)
   */
  async inviteMember(
    workspaceId: string,
    email: string,
    role: WorkspaceMember['role']
  ): Promise<void> {
    if (!supabase) {
      throw new Error('Supabase not configured');
    }

    // Generate a random token for the invite
    const token = crypto.randomUUID();
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + 7); // 7 days expiry

    const { error } = await supabase
      .from('workspace_invites')
      .insert({
        workspace_id: workspaceId,
        email,
        role,
        token,
        expires_at: expiresAt.toISOString()
      });

    if (error) {
      console.error('Error creating invite:', error);
      throw error;
    }

    // TODO: Send email with invite link
    // This would integrate with an email service
    console.log(`Invite created for ${email} with token ${token}`);
  }
};

