// Team Management System
// Implements team invitations, role-based access, and permission inheritance

import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { workspaceIsolation } from './workspace-isolation'

export interface TeamInvitation {
  id: string
  workspace_id: string
  email: string
  role: 'owner' | 'admin' | 'member' | 'viewer'
  permissions: string[]
  invited_by: string
  invitation_token: string
  status: 'pending' | 'accepted' | 'rejected' | 'expired'
  expires_at: string
  accepted_at?: string
  created_at: string
  updated_at: string
}

export interface RolePermission {
  role: string
  permissions: string[]
  inherits_from?: string[]
  can_manage_roles: string[]
}

export interface TeamMember {
  id: string
  user_id: string
  workspace_id: string
  role: string
  permissions: string[]
  invited_by?: string
  invited_at?: string
  accepted_at?: string
  created_at: string
  updated_at: string
  profile?: {
    email: string
    full_name: string
    avatar_url?: string
  }
}

export class TeamManagement {
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
   * Role-based permission definitions
   */
  private readonly ROLE_PERMISSIONS: Record<string, RolePermission> = {
    owner: {
      role: 'owner',
      permissions: ['all'],
      can_manage_roles: ['owner', 'admin', 'member', 'viewer']
    },
    admin: {
      role: 'admin',
      permissions: [
        'members.view',
        'members.invite',
        'members.remove',
        'members.update',
        'resources.view',
        'resources.create',
        'resources.update',
        'resources.delete',
        'resources.grant',
        'resources.revoke',
        'settings.view',
        'settings.update',
        'analytics.view',
        'billing.view',
        'billing.update'
      ],
      can_manage_roles: ['admin', 'member', 'viewer']
    },
    member: {
      role: 'member',
      permissions: [
        'members.view',
        'resources.view',
        'resources.create',
        'resources.update',
        'analytics.view'
      ],
      can_manage_roles: ['member', 'viewer']
    },
    viewer: {
      role: 'viewer',
      permissions: [
        'members.view',
        'resources.view',
        'analytics.view'
      ],
      can_manage_roles: ['viewer']
    }
  }

  /**
   * Get permissions for a specific role
   */
  getRolePermissions(role: string): string[] {
    return this.ROLE_PERMISSIONS[role]?.permissions || []
  }

  /**
   * Check if a role can manage another role
   */
  canManageRole(managerRole: string, targetRole: string): boolean {
    return this.ROLE_PERMISSIONS[managerRole]?.can_manage_roles?.includes(targetRole) || false
  }

  /**
   * Create team invitation
   */
  async createInvitation(
    workspaceId: string,
    email: string,
    role: string,
    permissions: string[] = [],
    invitedBy: string
  ): Promise<TeamInvitation> {
    try {
      // Check if inviter has permission to invite members
      const canInvite = await workspaceIsolation.hasPermission(invitedBy, workspaceId, 'members.invite')
      if (!canInvite) {
        throw new Error('Insufficient permissions to invite members')
      }

      // Check if inviter can assign this role
      const inviterRole = await workspaceIsolation.getUserRole(invitedBy, workspaceId)
      if (!inviterRole || !this.canManageRole(inviterRole, role)) {
        throw new Error(`Cannot assign role '${role}'`)
      }

      // Generate invitation token
      const invitationToken = this.generateInvitationToken()

      // Set default permissions based on role if not provided
      const rolePermissions = permissions.length > 0 ? permissions : this.getRolePermissions(role)

      const { data, error } = await this.supabase
        .from('workspace_invitations')
        .insert({
          workspace_id: workspaceId,
          email: email.toLowerCase(),
          role,
          permissions: rolePermissions,
          invited_by: invitedBy,
          invitation_token: invitationToken,
          expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString() // 7 days
        })
        .select()
        .single()

      if (error) throw error

      return data
    } catch (error) {
      console.error('Error creating invitation:', error)
      throw error
    }
  }

  /**
   * Get pending invitations for a workspace
   */
  async getPendingInvitations(workspaceId: string): Promise<TeamInvitation[]> {
    try {
      const { data, error } = await this.supabase
        .from('workspace_invitations')
        .select(`
          *,
          inviter_profile:profiles!invited_by(
            email,
            full_name,
            avatar_url
          )
        `)
        .eq('workspace_id', workspaceId)
        .eq('status', 'pending')
        .gt('expires_at', new Date().toISOString())
        .order('created_at', { ascending: false })

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting pending invitations:', error)
      throw error
    }
  }

  /**
   * Get invitations for a specific email
   */
  async getInvitationsByEmail(email: string): Promise<TeamInvitation[]> {
    try {
      const { data, error } = await this.supabase
        .from('workspace_invitations')
        .select(`
          *,
          workspaces (
            id,
            name,
            slug,
            description
          ),
          inviter_profile:profiles!invited_by(
            email,
            full_name,
            avatar_url
          )
        `)
        .eq('email', email.toLowerCase())
        .eq('status', 'pending')
        .gt('expires_at', new Date().toISOString())
        .order('created_at', { ascending: false })

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting invitations by email:', error)
      throw error
    }
  }

  /**
   * Accept invitation
   */
  async acceptInvitation(
    invitationToken: string,
    userId: string
  ): Promise<TeamMember> {
    try {
      // Get invitation details
      const { data: invitation, error: invitationError } = await this.supabase
        .from('workspace_invitations')
        .select('*')
        .eq('invitation_token', invitationToken)
        .eq('status', 'pending')
        .gt('expires_at', new Date().toISOString())
        .single()

      if (invitationError || !invitation) {
        throw new Error('Invalid or expired invitation')
      }

      // Check if user email matches invitation
      const { data: profile } = await this.supabase
        .from('profiles')
        .select('email')
        .eq('id', userId)
        .single()

      if (!profile || profile.email.toLowerCase() !== invitation.email.toLowerCase()) {
        throw new Error('Email does not match invitation')
      }

      // Add user to workspace
      const { data: member, error: memberError } = await this.supabase
        .from('workspace_members')
        .insert({
          user_id: userId,
          workspace_id: invitation.workspace_id,
          role: invitation.role,
          permissions: invitation.permissions,
          invited_by: invitation.invited_by,
          invited_at: invitation.created_at,
          accepted_at: new Date().toISOString()
        })
        .select(`
          *,
          profiles (
            email,
            full_name,
            avatar_url
          )
        `)
        .single()

      if (memberError) throw memberError

      // Update invitation status
      await this.supabase
        .from('workspace_invitations')
        .update({
          status: 'accepted',
          accepted_at: new Date().toISOString()
        })
        .eq('id', invitation.id)

      return member
    } catch (error) {
      console.error('Error accepting invitation:', error)
      throw error
    }
  }

  /**
   * Reject invitation
   */
  async rejectInvitation(invitationToken: string): Promise<void> {
    try {
      const { error } = await this.supabase
        .from('workspace_invitations')
        .update({
          status: 'rejected',
          updated_at: new Date().toISOString()
        })
        .eq('invitation_token', invitationToken)

      if (error) throw error
    } catch (error) {
      console.error('Error rejecting invitation:', error)
      throw error
    }
  }

  /**
   * Cancel invitation
   */
  async cancelInvitation(
    invitationId: string,
    cancelledBy: string
  ): Promise<void> {
    try {
      // Get invitation to check workspace
      const { data: invitation } = await this.supabase
        .from('workspace_invitations')
        .select('workspace_id')
        .eq('id', invitationId)
        .single()

      if (!invitation) {
        throw new Error('Invitation not found')
      }

      // Check if user can cancel invitations
      const canCancel = await workspaceIsolation.hasPermission(
        cancelledBy,
        invitation.workspace_id,
        'members.invite'
      )

      if (!canCancel) {
        throw new Error('Insufficient permissions to cancel invitations')
      }

      const { error } = await this.supabase
        .from('workspace_invitations')
        .update({
          status: 'rejected',
          updated_at: new Date().toISOString()
        })
        .eq('id', invitationId)

      if (error) throw error
    } catch (error) {
      console.error('Error cancelling invitation:', error)
      throw error
    }
  }

  /**
   * Update team member role
   */
  async updateMemberRole(
    workspaceId: string,
    userId: string,
    newRole: string,
    updatedBy: string
  ): Promise<void> {
    try {
      // Check if updater can manage this role
      const updaterRole = await workspaceIsolation.getUserRole(updatedBy, workspaceId)
      if (!updaterRole || !this.canManageRole(updaterRole, newRole)) {
        throw new Error(`Cannot assign role '${newRole}'`)
      }

      // Don't allow changing owner role
      const memberRole = await workspaceIsolation.getUserRole(userId, workspaceId)
      if (memberRole === 'owner') {
        throw new Error('Cannot change owner role')
      }

      const newPermissions = this.getRolePermissions(newRole)

      const { error } = await this.supabase
        .from('workspace_members')
        .update({
          role: newRole,
          permissions: newPermissions,
          updated_at: new Date().toISOString()
        })
        .eq('workspace_id', workspaceId)
        .eq('user_id', userId)

      if (error) throw error
    } catch (error) {
      console.error('Error updating member role:', error)
      throw error
    }
  }

  /**
   * Update team member permissions
   */
  async updateMemberPermissions(
    workspaceId: string,
    userId: string,
    permissions: string[],
    updatedBy: string
  ): Promise<void> {
    try {
      // Check if updater can update permissions
      const canUpdate = await workspaceIsolation.hasPermission(
        updatedBy,
        workspaceId,
        'members.update'
      )

      if (!canUpdate) {
        throw new Error('Insufficient permissions to update member permissions')
      }

      const { error } = await this.supabase
        .from('workspace_members')
        .update({
          permissions,
          updated_at: new Date().toISOString()
        })
        .eq('workspace_id', workspaceId)
        .eq('user_id', userId)

      if (error) throw error
    } catch (error) {
      console.error('Error updating member permissions:', error)
      throw error
    }
  }

  /**
   * Remove team member
   */
  async removeMember(
    workspaceId: string,
    userId: string,
    removedBy: string
  ): Promise<void> {
    try {
      // Check if remover can remove members
      const canRemove = await workspaceIsolation.hasPermission(
        removedBy,
        workspaceId,
        'members.remove'
      )

      if (!canRemove) {
        throw new Error('Insufficient permissions to remove members')
      }

      // Don't allow removing owners
      const memberRole = await workspaceIsolation.getUserRole(userId, workspaceId)
      if (memberRole === 'owner') {
        throw new Error('Cannot remove workspace owner')
      }

      await workspaceIsolation.removeMember(workspaceId, userId, removedBy)
    } catch (error) {
      console.error('Error removing member:', error)
      throw error
    }
  }

  /**
   * Get team members with inheritance
   */
  async getTeamMembers(workspaceId: string): Promise<TeamMember[]> {
    try {
      const members = await workspaceIsolation.getWorkspaceMembers(workspaceId)
      
      // Add inherited permissions and role hierarchy
      return members.map(member => ({
        ...member,
        inherited_permissions: this.getInheritedPermissions(member.role),
        can_manage_roles: this.ROLE_PERMISSIONS[member.role]?.can_manage_roles || []
      }))
    } catch (error) {
      console.error('Error getting team members:', error)
      throw error
    }
  }

  /**
   * Get inherited permissions for a role
   */
  private getInheritedPermissions(role: string): string[] {
    const roleConfig = this.ROLE_PERMISSIONS[role]
    if (!roleConfig) return []

    let permissions = [...roleConfig.permissions]
    
    // Add inherited permissions if specified
    if (roleConfig.inherits_from) {
      for (const inheritedRole of roleConfig.inherits_from) {
        const inheritedPerms = this.getRolePermissions(inheritedRole)
        permissions = [...permissions, ...inheritedPerms]
      }
    }

    return Array.from(new Set(permissions)) // Remove duplicates
  }

  /**
   * Check if user has permission through role inheritance
   */
  async hasPermissionWithInheritance(
    userId: string,
    workspaceId: string,
    permission: string
  ): Promise<boolean> {
    try {
      const memberRole = await workspaceIsolation.getUserRole(userId, workspaceId)
      if (!memberRole) return false

      const rolePermissions = this.getInheritedPermissions(memberRole)
      return rolePermissions.includes(permission)
    } catch (error) {
      console.error('Error checking permission with inheritance:', error)
      return false
    }
  }

  /**
   * Get role hierarchy for workspace
   */
  getRoleHierarchy(): Record<string, string[]> {
    const hierarchy: Record<string, string[]> = {}
    
    Object.entries(this.ROLE_PERMISSIONS).forEach(([role, config]) => {
      hierarchy[role] = config.can_manage_roles || []
    })

    return hierarchy
  }

  /**
   * Generate invitation token
   */
  private generateInvitationToken(): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    let token = ''
    for (let i = 0; i < 32; i++) {
      token += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return token
  }

  /**
   * Clean up expired invitations
   */
  async cleanupExpiredInvitations(): Promise<number> {
    try {
      const { error } = await this.supabase
        .from('workspace_invitations')
        .update({
          status: 'expired',
          updated_at: new Date().toISOString()
        })
        .lt('expires_at', new Date().toISOString())
        .eq('status', 'pending')

      if (error) throw error

      // Get count of expired invitations
      const { count } = await this.supabase
        .from('workspace_invitations')
        .select('id', { count: 'exact', head: true })
        .eq('status', 'expired')

      return count || 0
    } catch (error) {
      console.error('Error cleaning up expired invitations:', error)
      return 0
    }
  }

  /**
   * Get invitation statistics
   */
  async getInvitationStats(workspaceId: string): Promise<{
    total: number
    pending: number
    accepted: number
    rejected: number
    expired: number
  }> {
    try {
      const { data, error } = await this.supabase
        .from('workspace_invitations')
        .select('status')
        .eq('workspace_id', workspaceId)

      if (error) throw error

      const stats = {
        total: data?.length || 0,
        pending: 0,
        accepted: 0,
        rejected: 0,
        expired: 0
      }

      data?.forEach((invitation: any) => {
        stats[invitation.status as keyof typeof stats]++
      })

      return stats
    } catch (error) {
      console.error('Error getting invitation stats:', error)
      throw error
    }
  }
}

export const teamManagement = new TeamManagement()
