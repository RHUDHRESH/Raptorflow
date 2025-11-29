import { supabase } from '../lib/supabase';
import type { User } from '@supabase/supabase-js';

/**
 * Workspace Service
 * 
 * Centralized service for workspace-related database operations.
 * Wraps Supabase queries with proper error handling and TypeScript types.
 */

// Type definitions
export interface Workspace {
  id: string;
  name: string;
  slug?: string;
  description?: string | null;
  owner_id: string;
  plan?: string | null;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface WorkspaceMember {
  id?: string;
  workspace_id: string;
  user_id: string;
  role: 'owner' | 'admin' | 'member';
  created_at?: string;
}

export interface InviteMemberInput {
  email: string;
  role: 'admin' | 'member';
}

export interface CreateWorkspaceInput {
  name: string;
  description?: string;
}

export interface UpdateWorkspaceInput {
  name?: string;
  description?: string;
  plan?: string;
  is_active?: boolean;
}

export interface WorkspaceResponse {
  data: Workspace | null;
  error: Error | null;
}

export interface WorkspacesResponse {
  data: Workspace[] | null;
  error: Error | null;
}

export interface WorkspaceMembersResponse {
  data: WorkspaceMember[] | null;
  error: Error | null;
}

export interface InviteMemberResponse {
  data: {
    invite_id: string;
    email: string;
    workspace_id: string;
    status: string;
  } | null;
  error: Error | null;
}

/**
 * Workspace Service Object
 */
export const workspaceService = {
  /**
   * Get all workspaces for the current user
   * 
   * Uses Backend API to fetch workspaces.
   * 
   * @returns Promise with array of workspaces and error
   */
  async getWorkspaces(): Promise<WorkspacesResponse> {
    if (!supabase) {
      return { data: null, error: new Error('Supabase client not configured') };
    }

    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        return { data: null, error: new Error('User not authenticated') };
      }

      const apiUrl = (import.meta as any).env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
      
      const response = await fetch(`${apiUrl}/workspaces/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch workspaces');
      }

      const data = await response.json();
      return { data: data || [], error: null };

    } catch (error) {
      console.error('[WorkspaceService] Error fetching workspaces:', error);
      // Mock fallback for offline development
      console.warn('[WorkspaceService] Returning mock workspaces due to error');
      return {
        data: [{
          id: 'mock-workspace-1',
          name: 'Demo Workspace',
          slug: 'demo-workspace',
          owner_id: 'mock-user',
          plan: 'pro',
          is_active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }],
        error: null
      };
    }
  },

  /**
   * Get a specific workspace by ID
   * 
   * @param id - Workspace ID
   * @returns Promise with workspace and error
   */
  async getWorkspace(id: string): Promise<WorkspaceResponse> {
    if (!supabase) {
      return { data: null, error: new Error('Supabase client not configured') };
    }

    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        return { data: null, error: new Error('User not authenticated') };
      }

      const apiUrl = (import.meta as any).env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
      
      const response = await fetch(`${apiUrl}/workspaces/${id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch workspace');
      }

      const data = await response.json();
      return { data, error: null };

    } catch (error) {
      console.error('[WorkspaceService] Error fetching workspace:', error);
      return {
        data: null,
        error: error instanceof Error ? error : new Error('Failed to fetch workspace'),
      };
    }
  },

  /**
   * Create a new workspace via Backend API (ensures agent seeding)
   * 
   * @param workspaceData - Workspace creation data
   * @returns Promise with created workspace and error
   */
  async createWorkspace(workspaceData: CreateWorkspaceInput): Promise<WorkspaceResponse> {
    if (!supabase) {
      return { data: null, error: new Error('Supabase client not configured') };
    }

    try {
      // Get session token for API auth
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        return { data: null, error: new Error('User not authenticated') };
      }

      const apiUrl = (import.meta as any).env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
      
      const response = await fetch(`${apiUrl}/workspaces/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          name: workspaceData.name,
          slug: workspaceData.name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create workspace');
      }

      const data = await response.json();
      
      // Map API response to Workspace interface
      const workspace: Workspace = {
        id: data.workspace_id,
        name: data.name,
        slug: data.slug,
        owner_id: session.user.id, // Assuming creator is owner
        plan: 'starter',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      return { data: workspace, error: null };

    } catch (error) {
      console.error('[WorkspaceService] Error creating workspace:', error);
      // Mock fallback for offline development
      console.warn('[WorkspaceService] Creating mock workspace due to error');
      const mockWorkspace: Workspace = {
        id: `mock-workspace-${Date.now()}`,
        name: workspaceData.name,
        slug: workspaceData.name.toLowerCase().replace(/\s+/g, '-'),
        owner_id: 'mock-user',
        plan: 'free',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      return { data: mockWorkspace, error: null };
    }
  },

  /**
   * Update a workspace
   * 
   * @param id - Workspace ID
   * @param updates - Fields to update
   * @returns Promise with updated workspace and error
   */
  async updateWorkspace(
    id: string,
    updates: UpdateWorkspaceInput
  ): Promise<WorkspaceResponse> {
    if (!supabase) {
      return {
        data: null,
        error: new Error('Supabase client not configured'),
      };
    }

    try {
      const { data, error } = await supabase
        .from('workspaces')
        .update(updates)
        .eq('id', id)
        .select()
        .single();

      if (error) {
        console.error('[WorkspaceService] Error updating workspace:', error);
        return { data: null, error: new Error(error.message) };
      }

      return { data, error: null };
    } catch (error) {
      console.error('[WorkspaceService] Unexpected error updating workspace:', error);
      return {
        data: null,
        error: error instanceof Error ? error : new Error('Failed to update workspace'),
      };
    }
  },

  /**
   * Delete a workspace
   * 
   * @param id - Workspace ID
   * @returns Promise with error (null if successful)
   */
  async deleteWorkspace(id: string): Promise<{ error: Error | null }> {
    if (!supabase) {
      return {
        error: new Error('Supabase client not configured'),
      };
    }

    try {
      const { error } = await supabase
        .from('workspaces')
        .delete()
        .eq('id', id);

      if (error) {
        console.error('[WorkspaceService] Error deleting workspace:', error);
        return { error: new Error(error.message) };
      }

      return { error: null };
    } catch (error) {
      console.error('[WorkspaceService] Unexpected error deleting workspace:', error);
      return {
        error: error instanceof Error ? error : new Error('Failed to delete workspace'),
      };
    }
  },

  /**
   * Get members of a workspace
   * 
   * @param workspaceId - Workspace ID
   * @returns Promise with array of members and error
   */
  async getWorkspaceMembers(workspaceId: string): Promise<WorkspaceMembersResponse> {
    if (!supabase) {
      return {
        data: null,
        error: new Error('Supabase client not configured'),
      };
    }

    try {
      const { data, error } = await supabase
        .from('workspace_members')
        .select('*')
        .eq('workspace_id', workspaceId);

      if (error) {
        console.error('[WorkspaceService] Error fetching workspace members:', error);
        return { data: null, error: new Error(error.message) };
      }

      return { data: data || [], error: null };
    } catch (error) {
      console.error('[WorkspaceService] Unexpected error fetching workspace members:', error);
      return {
        data: null,
        error: error instanceof Error ? error : new Error('Failed to fetch workspace members'),
      };
    }
  },

  /**
   * Invite a member to the workspace
   * 
   * @param workspaceId - Workspace ID
   * @param email - Email of the user to invite
   * @param role - Role to assign (default: member)
   */
  async inviteMember(workspaceId: string, input: InviteMemberInput): Promise<InviteMemberResponse> {
    if (!supabase) {
      return { data: null, error: new Error('Supabase client not configured') };
    }

    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        return { data: null, error: new Error('User not authenticated') };
      }

      const apiUrl = (import.meta as any).env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';
      
      const response = await fetch(`${apiUrl}/workspaces/${workspaceId}/invite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
        body: JSON.stringify(input),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to invite member');
      }

      const data = await response.json();
      return { data, error: null };

    } catch (error) {
      console.error('[WorkspaceService] Error inviting member:', error);
      return {
        data: null,
        error: error instanceof Error ? error : new Error('Failed to invite member'),
      };
    }
  },
};
