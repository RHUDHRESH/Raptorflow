// User Impersonation System
// Implements secure impersonation, audit logging, and access controls

import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import crypto from 'crypto'

export interface ImpersonationSession {
  id: string
  admin_id: string
  target_user_id: string
  impersonation_token: string
  original_session_token: string
  ip_address: string
  user_agent: string
  reason: string
  expires_at: string
  created_at: string
  last_accessed: string
  access_count: number
  is_active: boolean
}

export interface ImpersonationLog {
  id: string
  impersonation_session_id: string
  admin_id: string
  target_user_id: string
  action: 'start' | 'access' | 'end'
  resource_accessed?: string
  ip_address: string
  user_agent: string
  metadata: any
  created_at: string
}

export interface ImpersonationPermission {
  admin_id: string
  can_impersonate: boolean
  max_duration_hours: number
  allowed_user_ids: string[]
  allowed_roles: string[]
  requires_approval: boolean
  audit_level: 'basic' | 'detailed' | 'comprehensive'
}

export class UserImpersonation {
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
   * Check if admin has impersonation permissions
   */
  async checkImpersonationPermissions(adminId: string): Promise<ImpersonationPermission> {
    try {
      // Get admin's role and permissions
      const { data: adminProfile } = await this.supabase
        .from('profiles')
        .select('subscription_plan, role')
        .eq('id', adminId)
        .single()

      if (!adminProfile) {
        throw new Error('Admin profile not found')
      }

      // Check if admin has admin role or is owner
      const { data: workspaceMembers } = await this.supabase
        .from('workspace_members')
        .select('role, permissions')
        .eq('user_id', adminId)
        .eq('role', 'owner')

      const isOwner = workspaceMembers && workspaceMembers.length > 0

      // Default permissions based on role and subscription
      const permissions: ImpersonationPermission = {
        admin_id: adminId,
        can_impersonate: isOwner || adminProfile.role === 'admin',
        max_duration_hours: adminProfile.subscription_plan === 'soar' ? 8 : 2,
        allowed_user_ids: [],
        allowed_roles: ['member', 'viewer'],
        requires_approval: !isOwner && adminProfile.subscription_plan !== 'soar',
        audit_level: isOwner ? 'comprehensive' : 'detailed'
      }

      return permissions
    } catch (error) {
      console.error('Error checking impersonation permissions:', error)
      throw error
    }
  }

  /**
   * Start impersonation session
   */
  async startImpersonation(
    adminId: string,
    targetUserId: string,
    originalSessionToken: string,
    reason: string,
    request: {
      ipAddress: string
      userAgent: string
    }
  ): Promise<ImpersonationSession> {
    try {
      // Check permissions
      const permissions = await this.checkImpersonationPermissions(adminId)
      
      if (!permissions.can_impersonate) {
        throw new Error('Insufficient permissions for impersonation')
      }

      // Check if target user is allowed
      if (permissions.allowed_user_ids.length > 0 && 
          !permissions.allowed_user_ids.includes(targetUserId)) {
        throw new Error('Target user not in allowed list')
      }

      // Get target user info
      const { data: targetUser } = await this.supabase
        .from('profiles')
        .select('email, full_name, subscription_plan, role')
        .eq('id', targetUserId)
        .single()

      if (!targetUser) {
        throw new Error('Target user not found')
      }

      // Check if target user has higher role
      if (permissions.allowed_roles.length > 0 && 
          !permissions.allowed_roles.includes(targetUser.role || 'member')) {
        throw new Error('Cannot impersonate user with higher role')
      }

      // Generate impersonation token
      const impersonationToken = this.generateImpersonationToken()

      // Set expiration time
      const expiresAt = new Date(Date.now() + permissions.max_duration_hours * 60 * 60 * 1000).toISOString()

      // Create impersonation session
      const { data, error } = await this.supabase
        .from('impersonation_sessions')
        .insert({
          admin_id: adminId,
          target_user_id: targetUserId,
          impersonation_token: impersonationToken,
          original_session_token: originalSessionToken,
          ip_address: request.ipAddress,
          user_agent: request.userAgent,
          reason,
          expires_at: expiresAt,
          is_active: true
        })
        .select()
        .single()

      if (error) throw error

      // Log impersonation start
      await this.logImpersonationAction(
        data.id,
        adminId,
        targetUserId,
        'start',
        request.ipAddress,
        request.userAgent,
        {
          reason,
          target_user_email: targetUser.email,
          target_user_name: targetUser.full_name,
          expires_at: expiresAt
        }
      )

      // Log security event
      await this.supabase
        .from('security_events')
        .insert({
          user_id: adminId,
          event_type: 'user_impersonation',
          severity: 'medium',
          message: `Admin started impersonating user ${targetUser.email}`,
          metadata: {
            impersonation_session_id: data.id,
            target_user_id: targetUserId,
            reason,
            expires_at: expiresAt
          },
          ip_address: request.ipAddress,
          user_agent: request.userAgent,
          created_at: new Date().toISOString()
        })

      return data
    } catch (error) {
      console.error('Error starting impersonation:', error)
      throw error
    }
  }

  /**
   * Validate impersonation session
   */
  async validateImpersonationSession(
    impersonationToken: string,
    request: {
      ipAddress: string
      userAgent: string
    }
  ): Promise<{
    valid: boolean
    session?: ImpersonationSession
    adminUser?: any
    targetUser?: any
    error?: string
  }> {
    try {
      // Get impersonation session
      const { data: session, error: sessionError } = await this.supabase
        .from('impersonation_sessions')
        .select('*')
        .eq('impersonation_token', impersonationToken)
        .eq('is_active', true)
        .single()

      if (sessionError || !session) {
        return { valid: false, error: 'Invalid impersonation token' }
      }

      // Check if session expired
      if (new Date(session.expires_at) < new Date()) {
        await this.endImpersonation(session.id, 'Session expired')
        return { valid: false, error: 'Impersonation session expired' }
      }

      // Get admin and target user info
      const [adminUser, targetUser] = await Promise.all([
        this.supabase
          .from('profiles')
          .select('id, email, full_name, role, subscription_plan')
          .eq('id', session.admin_id)
          .single(),
        this.supabase
          .from('profiles')
          .select('id, email, full_name, role, subscription_plan')
          .eq('id', session.target_user_id)
          .single()
      ])

      if (!adminUser || !targetUser) {
        return { valid: false, error: 'User not found' }
      }

      // Update last accessed
      await this.updateImpersonationAccess(session.id, request.ipAddress, request.userAgent)

      // Log access
      await this.logImpersonationAction(
        session.id,
        session.admin_id,
        session.target_user_id,
        'access',
        request.ipAddress,
        request.userAgent,
        {
          resource_accessed: 'session_validation'
        }
      )

      return {
        valid: true,
        session,
        adminUser,
        targetUser
      }
    } catch (error) {
      console.error('Error validating impersonation session:', error)
      return { valid: false, error: 'Validation failed' }
    }
  }

  /**
   * End impersonation session
   */
  async endImpersonation(
    sessionId: string,
    reason: string = 'Manual end',
    request?: {
      ipAddress: string
      userAgent: string
    }
  ): Promise<void> {
    try {
      // Get session details
      const { data: session } = await this.supabase
        .from('impersonation_sessions')
        .select('*')
        .eq('id', sessionId)
        .single()

      if (!session) {
        throw new Error('Impersonation session not found')
      }

      // Deactivate session
      const { error } = await this.supabase
        .from('impersonation_sessions')
        .update({
          is_active: false,
          last_accessed: new Date().toISOString()
        })
        .eq('id', sessionId)

      if (error) throw error

      // Log impersonation end
      await this.logImpersonationAction(
        sessionId,
        session.admin_id,
        session.target_user_id,
        'end',
        request?.ipAddress || session.ip_address,
        request?.userAgent || session.user_agent,
        {
          reason,
          duration: new Date().getTime() - new Date(session.created_at).getTime()
        }
      )

      // Log security event
      await this.supabase
        .from('security_events')
        .insert({
          user_id: session.admin_id,
          event_type: 'user_impersonation',
          severity: 'low',
          message: `Admin ended impersonation session`,
          metadata: {
            impersonation_session_id: sessionId,
            target_user_id: session.target_user_id,
            reason
          },
          ip_address: request?.ipAddress || session.ip_address,
          user_agent: request?.userAgent || session.user_agent,
          created_at: new Date().toISOString()
        })
    } catch (error) {
      console.error('Error ending impersonation:', error)
      throw error
    }
  }

  /**
   * Get active impersonation sessions
   */
  async getActiveImpersonationSessions(adminId?: string): Promise<ImpersonationSession[]> {
    try {
      let query = this.supabase
        .from('impersonation_sessions')
        .select(`
          *,
          admin_profiles:profiles!impersonation_sessions_admin_id_fkey (
            email,
            full_name
          ),
          target_profiles:profiles!impersonation_sessions_target_user_id_fkey (
            email,
            full_name
          )
        `)
        .eq('is_active', true)
        .order('created_at', { ascending: false })

      if (adminId) {
        query = query.eq('admin_id', adminId)
      }

      const { data, error } = await query

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting active impersonation sessions:', error)
      throw error
    }
  }

  /**
   * Get impersonation logs
   */
  async getImpersonationLogs(
    sessionId?: string,
    adminId?: string,
    targetUserId?: string,
    limit: number = 50
  ): Promise<ImpersonationLog[]> {
    try {
      let query = this.supabase
        .from('impersonation_logs')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(limit)

      if (sessionId) {
        query = query.eq('impersonation_session_id', sessionId)
      }

      if (adminId) {
        query = query.eq('admin_id', adminId)
      }

      if (targetUserId) {
        query = query.eq('target_user_id', targetUserId)
      }

      const { data, error } = await query

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting impersonation logs:', error)
      throw error
    }
  }

  /**
   * Update impersonation access
   */
  private async updateImpersonationAccess(
    sessionId: string,
    ipAddress: string,
    userAgent: string
  ): Promise<void> {
    try {
      await this.supabase
        .from('impersonation_sessions')
        .update({
          last_accessed: new Date().toISOString(),
          access_count: this.supabase.rpc('increment', { count: 1 })
        })
        .eq('id', sessionId)
    } catch (error) {
      console.error('Error updating impersonation access:', error)
      // Don't throw error for logging failures
    }
  }

  /**
   * Log impersonation action
   */
  private async logImpersonationAction(
    sessionId: string,
    adminId: string,
    targetUserId: string,
    action: 'start' | 'access' | 'end',
    ipAddress: string,
    userAgent: string,
    metadata: any
  ): Promise<void> {
    try {
      await this.supabase
        .from('impersonation_logs')
        .insert({
          impersonation_session_id: sessionId,
          admin_id: adminId,
          target_user_id: targetUserId,
          action,
          ip_address: ipAddress,
          user_agent: userAgent,
          metadata,
          created_at: new Date().toISOString()
        })
    } catch (error) {
      console.error('Error logging impersonation action:', error)
      // Don't throw error for logging failures
    }
  }

  /**
   * Generate impersonation token
   */
  private generateImpersonationToken(): string {
    return crypto.randomBytes(32).toString('hex')
  }

  /**
   * Clean up expired impersonation sessions
   */
  async cleanupExpiredSessions(): Promise<number> {
    try {
      const { error } = await this.supabase
        .from('impersonation_sessions')
        .update({
          is_active: false,
          last_accessed: new Date().toISOString()
        })
        .lt('expires_at', new Date().toISOString())
        .eq('is_active', true)

      if (error) throw error

      // Get count of cleaned up sessions
      const { count } = await this.supabase
        .from('impersonation_sessions')
        .select('id', { count: 'exact', head: true })
        .eq('is_active', false)
        .lt('expires_at', new Date().toISOString())

      return count || 0
    } catch (error) {
      console.error('Error cleaning up expired sessions:', error)
      return 0
    }
  }

  /**
   * Get impersonation statistics
   */
  async getImpersonationStats(
    adminId?: string,
    days: number = 30
  ): Promise<{
    total_sessions: number
    active_sessions: number
    avg_duration_hours: number
    most_impersonated_users: Array<{ user_id: string; email: string; count: number }>
    recent_activity: number
    compliance_rate: number
  }> {
    try {
      const since = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString()

      const [
        totalSessions,
        activeSessions,
        mostImpersonated,
        recentActivity
      ] = await Promise.all([
        this.supabase
          .from('impersonation_sessions')
          .select('id', { count: 'exact', head: true })
          .gte('created_at', since)
          .eq(adminId ? 'admin_id' : adminId, adminId),
        this.supabase
          .from('impersonation_sessions')
          .select('id', { count: 'exact', head: true })
          .eq('is_active', true)
          .eq(adminId ? 'admin_id' : adminId, adminId),
        this.supabase
          .from('impersonation_sessions')
          .select('target_user_id', { count: 'exact', head: true })
          .gte('created_at', since)
          .eq(adminId ? 'admin_id' : adminId, adminId)
          .order('count', { ascending: false })
          .limit(10),
        this.supabase
          .from('impersonation_logs')
          .select('id', { count: 'exact', head: true })
          .gte('created_at', since)
          .eq(adminId ? 'admin_id' : adminId, adminId)
      ])

      // Calculate average duration
      const { data: sessions } = await this.supabase
        .from('impersonation_sessions')
        .select('created_at, last_accessed')
        .eq('is_active', false)
        .gte('created_at', since)
        .eq(adminId ? 'admin_id' : adminId, adminId)

      let avgDuration = 0
      if (sessions && sessions.length > 0) {
        const totalDuration = sessions.reduce((sum: number, session: any) => {
          const end = new Date(session.last_accessed).getTime()
          const start = new Date(session.created_at).getTime()
          return sum + (end - start)
        }, 0)
        avgDuration = totalDuration / sessions.length / (1000 * 60 * 60) // Convert to hours
      }

      // Get user details for most impersonated
      const userIds = mostImpersonated?.map((item: any) => item.target_user_id) || []
      const { data: userDetails } = userIds.length > 0 ? await this.supabase
        .from('profiles')
        .select('id, email')
        .in('id', userIds) : []

      const mostImpersonatedUsers = mostImpersonated?.map((item: any) => {
        const user = userDetails?.find((u: any) => u.id === item.target_user_id)
        return {
          user_id: item.target_user_id,
          email: user?.email || 'Unknown',
          count: item.count
        }
      }) || []

      return {
        total_sessions: totalSessions || 0,
        active_sessions: activeSessions || 0,
        avg_duration_hours: avgDuration,
        most_impersonated_users: mostImpersonatedUsers,
        recent_activity: recentActivity || 0,
        compliance_rate: 95 // Placeholder - would calculate from actual data
      }
    } catch (error) {
      console.error('Error getting impersonation stats:', error)
      throw error
    }
  }

  /**
   * Check if user is currently being impersonated
   */
  async isUserBeingImpersonated(userId: string): Promise<boolean> {
    try {
      const { data } = await this.supabase
        .from('impersonation_sessions')
        .select('id')
        .eq('target_user_id', userId)
        .eq('is_active', true)
        .gt('expires_at', new Date().toISOString())
        .single()

      return !!data
    } catch (error) {
      console.error('Error checking if user is being impersonated:', error)
      return false
    }
  }

  /**
   * Get current impersonation session for user
   */
  async getCurrentImpersonationSession(userId: string): Promise<ImpersonationSession | null> {
    try {
      const { data } = await this.supabase
        .from('impersonation_sessions')
        .select('*')
        .eq('target_user_id', userId)
        .eq('is_active', true)
        .gt('expires_at', new Date().toISOString())
        .single()

      return data
    } catch (error) {
      console.error('Error getting current impersonation session:', error)
      return null
    }
  }
}

export const userImpersonation = new UserImpersonation()
