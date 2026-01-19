// Workspace Isolation System
// Implements data segregation, permission boundaries, and resource allocation

import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export interface WorkspaceMember {
  id: string
  user_id: string
  workspace_id: string
  role: 'owner' | 'admin' | 'member' | 'viewer'
  permissions: string[]
  created_at: string
  updated_at: string
}

export interface Workspace {
  id: string
  name: string
  slug: string
  description?: string
  owner_id: string
  created_at: string
  updated_at: string
  is_active: boolean
  settings: {
    allow_invites: boolean
    require_approval: boolean
    max_members?: number
  }
}

export interface ResourcePermission {
  resource_type: string
  resource_id: string
  workspace_id: string
  user_id: string
  permissions: string[]
  granted_by: string
  granted_at: string
  expires_at?: string
}

export class WorkspaceIsolation {
  private supabase: any

  constructor() {
    this.supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return cookies().getAll()
          },
          setAll(cookiesToSet: any[]) {
            try {
              cookiesToSet.forEach(({ name, value, options }) =>
                cookies().set(name, value, options)
              )
            } catch {
              // The `setAll` method was called from a Server Component.
              // This can be ignored.
            }
          },
        },
      }
    )
  }

  /**
   * Get all workspaces a user has access to
   */
  async getUserWorkspaces(userId: string): Promise<Workspace[]> {
    try {
      const { data, error } = await this.supabase
        .from('workspace_members')
        .select(`
          workspace_id,
          role,
          permissions,
          workspaces (
            id,
            name,
            slug,
            description,
            owner_id,
            created_at,
            updated_at,
            is_active,
            settings
          )
        `)
        .eq('user_id', userId)
        .eq('workspaces.is_active', true)

      if (error) throw error

      return data?.map((member: any) => ({
        ...member.workspaces,
        user_role: member.role,
        user_permissions: member.permissions
      })) || []
    } catch (error) {
      console.error('Error getting user workspaces:', error)
      throw error
    }
  }

  /**
   * Check if user has access to a specific workspace
   */
  async hasWorkspaceAccess(userId: string, workspaceId: string): Promise<boolean> {
    try {
      const { data, error } = await this.supabase
        .from('workspace_members')
        .select('id')
        .eq('user_id', userId)
        .eq('workspace_id', workspaceId)
        .single()

      if (error && error.code !== 'PGRST116') throw error

      return !!data
    } catch (error) {
      console.error('Error checking workspace access:', error)
      return false
    }
  }

  /**
   * Get user's role in a workspace
   */
  async getUserRole(userId: string, workspaceId: string): Promise<string | null> {
    try {
      const { data, error } = await this.supabase
        .from('workspace_members')
        .select('role')
        .eq('user_id', userId)
        .eq('workspace_id', workspaceId)
        .single()

      if (error) throw error

      return data?.role || null
    } catch (error) {
      console.error('Error getting user role:', error)
      return null
    }
  }

  /**
   * Check if user has specific permission in workspace
   */
  async hasPermission(
    userId: string,
    workspaceId: string,
    permission: string
  ): Promise<boolean> {
    try {
      const { data, error } = await this.supabase
        .from('workspace_members')
        .select('role, permissions')
        .eq('user_id', userId)
        .eq('workspace_id', workspaceId)
        .single()

      if (error) throw error

      if (!data) return false

      // Owners have all permissions
      if (data.role === 'owner') return true

      // Check explicit permissions
      return data.permissions.includes(permission)
    } catch (error) {
      console.error('Error checking permission:', error)
      return false
    }
  }

  /**
   * Create a new workspace with proper isolation
   */
  async createWorkspace(
    userId: string,
    workspaceData: Partial<Workspace>
  ): Promise<Workspace> {
    try {
      // Start transaction
      const { data: workspace, error: workspaceError } = await this.supabase
        .from('workspaces')
        .insert({
          name: workspaceData.name,
          slug: workspaceData.slug,
          description: workspaceData.description,
          owner_id: userId,
          settings: workspaceData.settings || {
            allow_invites: true,
            require_approval: false
          }
        })
        .select()
        .single()

      if (workspaceError) throw workspaceError

      // Add owner as member
      const { error: memberError } = await this.supabase
        .from('workspace_members')
        .insert({
          user_id: userId,
          workspace_id: workspace.id,
          role: 'owner',
          permissions: ['all']
        })

      if (memberError) throw memberError

      return workspace
    } catch (error) {
      console.error('Error creating workspace:', error)
      throw error
    }
  }

  /**
   * Add member to workspace with proper permissions
   */
  async addMember(
    workspaceId: string,
    userId: string,
    role: string,
    permissions: string[] = [],
    invitedBy: string
  ): Promise<WorkspaceMember> {
    try {
      // Check if inviter has permission to add members
      const canAdd = await this.hasPermission(invitedBy, workspaceId, 'members.add')
      if (!canAdd) {
        throw new Error('Insufficient permissions to add members')
      }

      const { data, error } = await this.supabase
        .from('workspace_members')
        .insert({
          user_id: userId,
          workspace_id: workspaceId,
          role,
          permissions: role === 'owner' ? ['all'] : permissions
        })
        .select()
        .single()

      if (error) throw error

      return data
    } catch (error) {
      console.error('Error adding member:', error)
      throw error
    }
  }

  /**
   * Remove member from workspace
   */
  async removeMember(
    workspaceId: string,
    userId: string,
    removedBy: string
  ): Promise<void> {
    try {
      // Check if remover has permission
      const canRemove = await this.hasPermission(removedBy, workspaceId, 'members.remove')
      if (!canRemove) {
        throw new Error('Insufficient permissions to remove members')
      }

      // Don't allow removing owners
      const memberRole = await this.getUserRole(userId, workspaceId)
      if (memberRole === 'owner') {
        throw new Error('Cannot remove workspace owner')
      }

      const { error } = await this.supabase
        .from('workspace_members')
        .delete()
        .eq('workspace_id', workspaceId)
        .eq('user_id', userId)

      if (error) throw error
    } catch (error) {
      console.error('Error removing member:', error)
      throw error
    }
  }

  /**
   * Update member permissions
   */
  async updateMemberPermissions(
    workspaceId: string,
    userId: string,
    permissions: string[],
    updatedBy: string
  ): Promise<void> {
    try {
      // Check if updater has permission
      const canUpdate = await this.hasPermission(updatedBy, workspaceId, 'members.update')
      if (!canUpdate) {
        throw new Error('Insufficient permissions to update members')
      }

      const { error } = await this.supabase
        .from('workspace_members')
        .update({ permissions })
        .eq('workspace_id', workspaceId)
        .eq('user_id', userId)

      if (error) throw error
    } catch (error) {
      console.error('Error updating member permissions:', error)
      throw error
    }
  }

  /**
   * Get all members of a workspace
   */
  async getWorkspaceMembers(workspaceId: string): Promise<WorkspaceMember[]> {
    try {
      const { data, error } = await this.supabase
        .from('workspace_members')
        .select(`
          id,
          user_id,
          workspace_id,
          role,
          permissions,
          created_at,
          updated_at,
          profiles (
            email,
            full_name,
            avatar_url
          )
        `)
        .eq('workspace_id', workspaceId)
        .order('created_at', { ascending: true })

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting workspace members:', error)
      throw error
    }
  }

  /**
   * Check resource access permissions
   */
  async checkResourceAccess(
    userId: string,
    resourceType: string,
    resourceId: string,
    requiredPermission: string
  ): Promise<boolean> {
    try {
      // First check if user has the permission in any workspace
      const { data, error } = await this.supabase
        .from('resource_permissions')
        .select('workspace_id, permissions')
        .eq('user_id', userId)
        .eq('resource_type', resourceType)
        .eq('resource_id', resourceId)
        .single()

      if (error && error.code !== 'PGRST116') throw error

      if (!data) return false

      return data.permissions.includes(requiredPermission)
    } catch (error) {
      console.error('Error checking resource access:', error)
      return false
    }
  }

  /**
   * Grant resource access permissions
   */
  async grantResourceAccess(
    workspaceId: string,
    userId: string,
    resourceType: string,
    resourceId: string,
    permissions: string[],
    grantedBy: string
  ): Promise<void> {
    try {
      // Check if granter has permission
      const canGrant = await this.hasPermission(grantedBy, workspaceId, 'resources.grant')
      if (!canGrant) {
        throw new Error('Insufficient permissions to grant resource access')
      }

      const { error } = await this.supabase
        .from('resource_permissions')
        .upsert({
          workspace_id: workspaceId,
          user_id: userId,
          resource_type: resourceType,
          resource_id: resourceId,
          permissions,
          granted_by: grantedBy
        })

      if (error) throw error
    } catch (error) {
      console.error('Error granting resource access:', error)
      throw error
    }
  }

  /**
   * Revoke resource access permissions
   */
  async revokeResourceAccess(
    workspaceId: string,
    userId: string,
    resourceType: string,
    resourceId: string,
    revokedBy: string
  ): Promise<void> {
    try {
      // Check if revoker has permission
      const canRevoke = await this.hasPermission(revokedBy, workspaceId, 'resources.revoke')
      if (!canRevoke) {
        throw new Error('Insufficient permissions to revoke resource access')
      }

      const { error } = await this.supabase
        .from('resource_permissions')
        .delete()
        .eq('workspace_id', workspaceId)
        .eq('user_id', userId)
        .eq('resource_type', resourceType)
        .eq('resource_id', resourceId)

      if (error) throw error
    } catch (error) {
      console.error('Error revoking resource access:', error)
      throw error
    }
  }

  /**
   * Get resource access logs
   */
  async getResourceAccessLogs(
    workspaceId: string,
    resourceType?: string,
    resourceId?: string
  ): Promise<any[]> {
    try {
      let query = this.supabase
        .from('resource_access_logs')
        .select(`
          id,
          user_id,
          workspace_id,
          resource_type,
          resource_id,
          action,
          permissions,
          ip_address,
          user_agent,
          created_at,
          profiles (
            email,
            full_name
          )
        `)
        .eq('workspace_id', workspaceId)
        .order('created_at', { ascending: false })

      if (resourceType) {
        query = query.eq('resource_type', resourceType)
      }

      if (resourceId) {
        query = query.eq('resource_id', resourceId)
      }

      const { data, error } = await query

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting resource access logs:', error)
      throw error
    }
  }

  /**
   * Log resource access
   */
  async logResourceAccess(
    userId: string,
    workspaceId: string,
    resourceType: string,
    resourceId: string,
    action: string,
    permissions: string[],
    ipAddress?: string,
    userAgent?: string
  ): Promise<void> {
    try {
      const { error } = await this.supabase
        .from('resource_access_logs')
        .insert({
          user_id: userId,
          workspace_id: workspaceId,
          resource_type: resourceType,
          resource_id: resourceId,
          action,
          permissions,
          ip_address: ipAddress,
          user_agent: userAgent
        })

      if (error) throw error
    } catch (error) {
      console.error('Error logging resource access:', error)
      // Don't throw error for logging failures
    }
  }
}

export const workspaceIsolation = new WorkspaceIsolation()
