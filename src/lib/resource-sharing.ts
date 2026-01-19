// Resource Sharing System
// Implements cross-workspace sharing, permission grants, and access logs

import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { workspaceIsolation } from './workspace-isolation'

export interface SharedResource {
  id: string
  resource_type: string
  resource_id: string
  resource_name: string
  resource_data: any
  owner_workspace_id: string
  owner_user_id: string
  sharing_level: 'private' | 'workspace' | 'public' | 'custom'
  sharing_settings: {
    allow_copy: boolean
    allow_edit: boolean
    allow_download: boolean
    expires_at?: string
    password_protected?: boolean
    access_code?: string
  }
  created_at: string
  updated_at: string
}

export interface ResourceShare {
  id: string
  resource_id: string
  resource_type: string
  from_workspace_id: string
  to_workspace_id: string
  shared_by: string
  permissions: string[]
  access_level: 'view' | 'edit' | 'admin'
  status: 'active' | 'revoked' | 'expired'
  expires_at?: string
  created_at: string
  updated_at: string
}

export interface AccessLog {
  id: string
  resource_id: string
  resource_type: string
  workspace_id: string
  user_id: string
  action: 'view' | 'edit' | 'download' | 'copy' | 'share' | 'revoke'
  ip_address?: string
  user_agent?: string
  metadata?: any
  created_at: string
}

export interface ShareLink {
  id: string
  resource_id: string
  resource_type: string
  workspace_id: string
  token: string
  permissions: string[]
  access_level: 'view' | 'edit'
  expires_at?: string
  access_count: number
  max_access?: number
  password_protected?: boolean
  access_code?: string
  created_by: string
  created_at: string
}

export class ResourceSharing {
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
   * Create a shareable resource
   */
  async createSharedResource(
    resourceData: Partial<SharedResource>,
    createdBy: string
  ): Promise<SharedResource> {
    try {
      const { data, error } = await this.supabase
        .from('shared_resources')
        .insert({
          resource_type: resourceData.resource_type,
          resource_id: resourceData.resource_id,
          resource_name: resourceData.resource_name,
          resource_data: resourceData.resource_data,
          owner_workspace_id: resourceData.owner_workspace_id,
          owner_user_id: createdBy,
          sharing_level: resourceData.sharing_level || 'private',
          sharing_settings: resourceData.sharing_settings || {
            allow_copy: false,
            allow_edit: false,
            allow_download: false
          }
        })
        .select()
        .single()

      if (error) throw error

      // Log creation
      await this.logAccess(
        resourceData.resource_id!,
        resourceData.resource_type!,
        resourceData.owner_workspace_id!,
        createdBy,
        'share',
        undefined,
        undefined,
        { action: 'create_shared_resource' }
      )

      return data
    } catch (error) {
      console.error('Error creating shared resource:', error)
      throw error
    }
  }

  /**
   * Share resource with another workspace
   */
  async shareWithWorkspace(
    resourceId: string,
    resourceType: string,
    fromWorkspaceId: string,
    toWorkspaceId: string,
    permissions: string[],
    access_level: 'view' | 'edit' | 'admin',
    sharedBy: string,
    expiresAt?: string
  ): Promise<ResourceShare> {
    try {
      // Check if user can share from source workspace
      const canShare = await workspaceIsolation.hasPermission(
        sharedBy,
        fromWorkspaceId,
        'resources.share'
      )

      if (!canShare) {
        throw new Error('Insufficient permissions to share resource')
      }

      // Check if resource exists and user has access
      const hasAccess = await workspaceIsolation.checkResourceAccess(
        sharedBy,
        resourceType,
        resourceId,
        'view'
      )

      if (!hasAccess) {
        throw new Error('No access to resource')
      }

      const { data, error } = await this.supabase
        .from('resource_shares')
        .insert({
          resource_id: resourceId,
          resource_type: resourceType,
          from_workspace_id: fromWorkspaceId,
          to_workspace_id: toWorkspaceId,
          shared_by: sharedBy,
          permissions,
          access_level,
          status: 'active',
          expires_at: expiresAt
        })
        .select()
        .single()

      if (error) throw error

      // Log sharing action
      await this.logAccess(
        resourceId,
        resourceType,
        fromWorkspaceId,
        sharedBy,
        'share',
        undefined,
        undefined,
        {
          to_workspace_id: toWorkspaceId,
          access_level,
          permissions
        }
      )

      return data
    } catch (error) {
      console.error('Error sharing resource:', error)
      throw error
    }
  }

  /**
   * Create public share link
   */
  async createShareLink(
    resourceId: string,
    resourceType: string,
    workspaceId: string,
    permissions: string[],
    access_level: 'view' | 'edit',
    options: {
      expiresAt?: string
      maxAccess?: number
      passwordProtected?: boolean
      accessCode?: string
    } = {},
    createdBy: string
  ): Promise<ShareLink> {
    try {
      // Check if user can create share links
      const canCreateLink = await workspaceIsolation.hasPermission(
        createdBy,
        workspaceId,
        'resources.share'
      )

      if (!canCreateLink) {
        throw new Error('Insufficient permissions to create share links')
      }

      // Generate share token
      const token = this.generateShareToken()

      const { data, error } = await this.supabase
        .from('share_links')
        .insert({
          resource_id: resourceId,
          resource_type: resourceType,
          workspace_id: workspaceId,
          token,
          permissions,
          access_level,
          expires_at: options.expiresAt,
          max_access: options.maxAccess,
          password_protected: options.passwordProtected,
          access_code: options.accessCode,
          created_by: createdBy
        })
        .select()
        .single()

      if (error) throw error

      // Log link creation
      await this.logAccess(
        resourceId,
        resourceType,
        workspaceId,
        createdBy,
        'share',
        undefined,
        undefined,
        {
          action: 'create_share_link',
          token,
          access_level,
          permissions
        }
      )

      return data
    } catch (error) {
      console.error('Error creating share link:', error)
      throw error
    }
  }

  /**
   * Access resource via share link
   */
  async accessViaShareLink(
    token: string,
    accessCode?: string,
    ipAddress?: string,
    userAgent?: string
  ): Promise<{
    resource: SharedResource
    permissions: string[]
    access_level: string
  }> {
    try {
      // Get share link details
      const { data: link, error: linkError } = await this.supabase
        .from('share_links')
        .select('*')
        .eq('token', token)
        .eq('status', 'active')
        .single()

      if (linkError || !link) {
        throw new Error('Invalid or expired share link')
      }

      // Check if link has expired
      if (link.expires_at && new Date(link.expires_at) < new Date()) {
        throw new Error('Share link has expired')
      }

      // Check if max access limit reached
      if (link.max_access && link.access_count >= link.max_access) {
        throw new Error('Share link access limit reached')
      }

      // Check password protection
      if (link.password_protected && link.access_code !== accessCode) {
        throw new Error('Invalid access code')
      }

      // Get resource details
      const { data: resource, error: resourceError } = await this.supabase
        .from('shared_resources')
        .select('*')
        .eq('resource_id', link.resource_id)
        .eq('resource_type', link.resource_type)
        .single()

      if (resourceError || !resource) {
        throw new Error('Resource not found')
      }

      // Update access count
      await this.supabase
        .from('share_links')
        .update({
          access_count: link.access_count + 1
        })
        .eq('id', link.id)

      // Log access
      await this.logAccess(
        link.resource_id,
        link.resource_type,
        link.workspace_id,
        null, // No user ID for anonymous access
        'view',
        ipAddress,
        userAgent,
        {
          access_via: 'share_link',
          token,
          access_level: link.access_level
        }
      )

      return {
        resource,
        permissions: link.permissions,
        access_level: link.access_level
      }
    } catch (error) {
      console.error('Error accessing via share link:', error)
      throw error
    }
  }

  /**
   * Get shared resources for workspace
   */
  async getSharedResources(
    workspaceId: string,
    resourceType?: string
  ): Promise<SharedResource[]> {
    try {
      let query = this.supabase
        .from('shared_resources')
        .select('*')
        .eq('owner_workspace_id', workspaceId)

      if (resourceType) {
        query = query.eq('resource_type', resourceType)
      }

      const { data, error } = await query.order('created_at', { ascending: false })

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting shared resources:', error)
      throw error
    }
  }

  /**
   * Get resources shared with workspace
   */
  async getResourcesSharedWithWorkspace(
    workspaceId: string,
    resourceType?: string
  ): Promise<ResourceShare[]> {
    try {
      let query = this.supabase
        .from('resource_shares')
        .select(`
          *,
          shared_resources (
            resource_name,
            resource_data,
            sharing_level,
            sharing_settings
          ),
          from_workspaces (
            name,
            slug
          )
        `)
        .eq('to_workspace_id', workspaceId)
        .eq('status', 'active')

      if (resourceType) {
        query = query.eq('resource_type', resourceType)
      }

      // Filter out expired shares
      query = query.or('expires_at.is.null,expires_at.gt.now()')

      const { data, error } = await query.order('created_at', { ascending: false })

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting resources shared with workspace:', error)
      throw error
    }
  }

  /**
   * Revoke resource share
   */
  async revokeShare(
    shareId: string,
    revokedBy: string
  ): Promise<void> {
    try {
      // Get share details to check permissions
      const { data: share } = await this.supabase
        .from('resource_shares')
        .select('from_workspace_id, resource_id, resource_type')
        .eq('id', shareId)
        .single()

      if (!share) {
        throw new Error('Share not found')
      }

      // Check if user can revoke shares
      const canRevoke = await workspaceIsolation.hasPermission(
        revokedBy,
        share.from_workspace_id,
        'resources.revoke'
      )

      if (!canRevoke) {
        throw new Error('Insufficient permissions to revoke share')
      }

      const { error } = await this.supabase
        .from('resource_shares')
        .update({
          status: 'revoked',
          updated_at: new Date().toISOString()
        })
        .eq('id', shareId)

      if (error) throw error

      // Log revocation
      await this.logAccess(
        share.resource_id,
        share.resource_type,
        share.from_workspace_id,
        revokedBy,
        'revoke',
        undefined,
        undefined,
        { action: 'revoke_share', share_id: shareId }
      )
    } catch (error) {
      console.error('Error revoking share:', error)
      throw error
    }
  }

  /**
   * Revoke share link
   */
  async revokeShareLink(
    linkId: string,
    revokedBy: string
  ): Promise<void> {
    try {
      // Get link details to check permissions
      const { data: link } = await this.supabase
        .from('share_links')
        .select('workspace_id, resource_id, resource_type')
        .eq('id', linkId)
        .single()

      if (!link) {
        throw new Error('Share link not found')
      }

      // Check if user can revoke links
      const canRevoke = await workspaceIsolation.hasPermission(
        revokedBy,
        link.workspace_id,
        'resources.revoke'
      )

      if (!canRevoke) {
        throw new Error('Insufficient permissions to revoke share link')
      }

      const { error } = await this.supabase
        .from('share_links')
        .update({
          status: 'revoked',
          updated_at: new Date().toISOString()
        })
        .eq('id', linkId)

      if (error) throw error

      // Log revocation
      await this.logAccess(
        link.resource_id,
        link.resource_type,
        link.workspace_id,
        revokedBy,
        'revoke',
        undefined,
        undefined,
        { action: 'revoke_share_link', link_id: linkId }
      )
    } catch (error) {
      console.error('Error revoking share link:', error)
      throw error
    }
  }

  /**
   * Get access logs for resource
   */
  async getAccessLogs(
    resourceId: string,
    resourceType: string,
    workspaceId?: string,
    limit: number = 50
  ): Promise<AccessLog[]> {
    try {
      let query = this.supabase
        .from('resource_access_logs')
        .select(`
          *,
          profiles (
            email,
            full_name,
            avatar_url
          )
        `)
        .eq('resource_id', resourceId)
        .eq('resource_type', resourceType)
        .order('created_at', { ascending: false })
        .limit(limit)

      if (workspaceId) {
        query = query.eq('workspace_id', workspaceId)
      }

      const { data, error } = await query

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting access logs:', error)
      throw error
    }
  }

  /**
   * Log resource access
   */
  async logAccess(
    resourceId: string,
    resourceType: string,
    workspaceId: string,
    userId: string | null,
    action: string,
    ipAddress?: string,
    userAgent?: string,
    metadata?: any
  ): Promise<void> {
    try {
      const { error } = await this.supabase
        .from('resource_access_logs')
        .insert({
          resource_id: resourceId,
          resource_type: resourceType,
          workspace_id: workspaceId,
          user_id: userId,
          action,
          ip_address: ipAddress,
          user_agent: userAgent,
          metadata
        })

      if (error) {
        console.error('Error logging access:', error)
        // Don't throw error for logging failures
      }
    } catch (error) {
      console.error('Error logging access:', error)
      // Don't throw error for logging failures
    }
  }

  /**
   * Get sharing statistics
   */
  async getSharingStats(workspaceId: string): Promise<{
    total_shared: number
    shared_with_others: number
    received_from_others: number
    public_links: number
    total_accesses: number
    recent_activity: number
  }> {
    try {
      // Get resources shared by this workspace
      const { data: sharedResources } = await this.supabase
        .from('shared_resources')
        .select('id')
        .eq('owner_workspace_id', workspaceId)

      // Get shares with other workspaces
      const { data: sharesOut } = await this.supabase
        .from('resource_shares')
        .select('id')
        .eq('from_workspace_id', workspaceId)
        .eq('status', 'active')

      // Get shares from other workspaces
      const { data: sharesIn } = await this.supabase
        .from('resource_shares')
        .select('id')
        .eq('to_workspace_id', workspaceId)
        .eq('status', 'active')

      // Get public share links
      const { data: shareLinks } = await this.supabase
        .from('share_links')
        .select('id')
        .eq('workspace_id', workspaceId)
        .eq('status', 'active')

      // Get access logs count (last 30 days)
      const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()
      const { count: accessCount } = await this.supabase
        .from('resource_access_logs')
        .select('id', { count: 'exact', head: true })
        .eq('workspace_id', workspaceId)
        .gte('created_at', thirtyDaysAgo)

      // Get recent activity (last 7 days)
      const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
      const { count: recentCount } = await this.supabase
        .from('resource_access_logs')
        .select('id', { count: 'exact', head: true })
        .eq('workspace_id', workspaceId)
        .gte('created_at', sevenDaysAgo)

      return {
        total_shared: sharedResources?.length || 0,
        shared_with_others: sharesOut?.length || 0,
        received_from_others: sharesIn?.length || 0,
        public_links: shareLinks?.length || 0,
        total_accesses: accessCount || 0,
        recent_activity: recentCount || 0
      }
    } catch (error) {
      console.error('Error getting sharing stats:', error)
      throw error
    }
  }

  /**
   * Generate share token
   */
  private generateShareToken(): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    let token = ''
    for (let i = 0; i < 32; i++) {
      token += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return token
  }

  /**
   * Clean up expired shares and links
   */
  async cleanupExpiredShares(): Promise<{
    expiredShares: number
    expiredLinks: number
  }> {
    try {
      const now = new Date().toISOString()

      // Clean up expired shares
      const { error: shareError } = await this.supabase
        .from('resource_shares')
        .update({
          status: 'expired',
          updated_at: now
        })
        .lt('expires_at', now)
        .eq('status', 'active')

      // Clean up expired links
      const { error: linkError } = await this.supabase
        .from('share_links')
        .update({
          status: 'expired',
          updated_at: now
        })
        .lt('expires_at', now)
        .eq('status', 'active')

      // Get counts
      const { count: expiredShares } = await this.supabase
        .from('resource_shares')
        .select('id', { count: 'exact', head: true })
        .eq('status', 'expired')

      const { count: expiredLinks } = await this.supabase
        .from('share_links')
        .select('id', { count: 'exact', head: true })
        .eq('status', 'expired')

      return {
        expiredShares: expiredShares || 0,
        expiredLinks: expiredLinks || 0
      }
    } catch (error) {
      console.error('Error cleaning up expired shares:', error)
      return { expiredShares: 0, expiredLinks: 0 }
    }
  }
}

export const resourceSharing = new ResourceSharing()
