// Admin Actions System
// Implements user suspension, manual interventions, and bulk operations

import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export interface AdminAction {
  id: string
  admin_id: string
  action_type: 'suspend_user' | 'activate_user' | 'reset_password' | 'force_mfa_reset' | 'impersonate_user' | 'bulk_suspend' | 'bulk_activate' | 'bulk_reset_password'
  target_user_ids?: string[]
  target_user_id?: string
  reason: string
  metadata: any
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  error_message?: string
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface BulkOperation {
  id: string
  admin_id: string
  operation_type: 'suspend_users' | 'activate_users' | 'reset_passwords' | 'force_mfa_reset'
  target_user_ids: string[]
  reason: string
  total_count: number
  completed_count: number
  failed_count: number
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  results: Array<{
    user_id: string
    success: boolean
    error?: string
    metadata?: any
  }>
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface UserSuspension {
  id: string
  user_id: string
  suspended_by: string
  reason: string
  suspensionType: 'temporary' | 'permanent' | 'security'
  expires_at?: string
  is_active: boolean
  created_at: string
  updated_at: string
  ended_at?: string
  ended_by?: string
}

export interface ManualIntervention {
  id: string
  admin_id: string
  interventionType: 'password_reset' | 'mfa_reset' | 'account_recovery' | 'data_access' | 'security_breach'
  target_user_id: string
  reason: string
  metadata: any
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  result?: any
  error_message?: string
  created_at: string
  updated_at: string
  completed_at?: string
}

export class AdminActions {
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
   * Check if user has admin permissions
   */
  async checkAdminPermissions(adminId: string): Promise<boolean> {
    try {
      // Check if user is admin or owner
      const { data: workspaceMembers } = await this.supabase
        .from('workspace_members')
        .select('role')
        .eq('user_id', adminId)
        .in('role', ['owner', 'admin'])

      return workspaceMembers && workspaceMembers.length > 0
    } catch (error) {
      console.error('Error checking admin permissions:', error)
      return false
    }
  }

  /**
   * Suspend user account
   */
  async suspendUser(
    adminId: string,
    targetUserId: string,
    reason: string,
    suspensionType: 'temporary' | 'permanent' | 'security' = 'temporary',
    expiresAt?: string
  ): Promise<UserSuspension> {
    try {
      const hasPermission = await this.checkAdminPermissions(adminId)
      if (!hasPermission) {
        throw new Error('Insufficient permissions to suspend user')
      }

      // Check if user is already suspended
      const { data: existingSuspension } = await this.supabase
        .from('user_suspensions')
        .select('*')
        .eq('target_user_id', targetUserId)
        .eq('is_active', true)
        .single()

      if (existingSuspension) {
        throw new Error('User is already suspended')
      }

      // Create suspension record
      const { data, error } = await this.supabase
        .from('user_suspensions')
        .insert({
          user_id: targetUserId,
          suspended_by: adminId,
          reason,
          suspensionType: suspensionType,
          expires_at: expiresAt,
          is_active: true
        })
        .select('*')
        .single()

      if (error) throw error

      // Update user status in profiles
      await this.supabase
        .from('profiles')
        .update({
          is_suspended: true,
          suspended_at: new Date().toISOString(),
          suspended_by: adminId,
          suspension_reason: reason
        })
        .eq('id', targetUserId)

      // Log admin action
      await this.logAdminAction(adminId, 'suspend_user', [targetUserId], reason, {
        suspensionType,
        expires_at: expiresAt
      })

      // Log security event
      await this.supabase
        .from('security_events')
        .insert({
          user_id: adminId,
          event_type: 'user_suspension',
          severity: suspensionType === 'security' ? 'high' : 'medium',
          message: `User suspended: ${reason}`,
          metadata: {
            target_user_id: targetUserId,
            suspensionType,
            expires_at: expiresAt
          },
          created_at: new Date().toISOString()
        })

      return data
    } catch (error) {
      console.error('Error suspending user:', error)
      throw error
    }
  }

  /**
   * Activate suspended user
   */
  async activateUser(
    adminId: string,
    targetUserId: string,
    reason: string
  ): Promise<void> {
    try {
      const hasPermission = await this.checkAdminPermissions(adminId)
      if (!hasPermission) {
        throw new Error('Insufficient permissions to activate user')
      }

      // End active suspension
      const { error: suspensionError } = await this.supabase
        .from('user_suspensions')
        .update({
          is_active: false,
          ended_at: new Date().toISOString(),
          ended_by: adminId
        })
        .eq('target_user_id', targetUserId)
        .eq('is_active', true)

      if (suspensionError) throw suspensionError

      // Update user status in profiles
      await this.supabase
        .from('profiles')
        .update({
          is_suspended: false,
          suspended_at: null,
          suspended_by: null,
          suspension_reason: null
        })
        .eq('id', targetUserId)

      // Log admin action
      await this.logAdminAction(adminId, 'activate_user', [targetUserId], reason, {})

      // Log security event
      await this.supabase
        .from('security_events')
        .insert({
          user_id: adminId,
          event_type: 'user_activation',
          severity: 'low',
          message: `User activated: ${reason}`,
          metadata: {
            target_user_id: targetUserId
          },
          created_at: new Date().toISOString()
        })
    } catch (error) {
      console.error('Error activating user:', error)
      throw error
    }
  }

  /**
   * Reset user password
   */
  async resetUserPassword(
    adminId: string,
    targetUserId: string,
    reason: string
  ): Promise<string> {
    try {
      const hasPermission = await this.checkAdminPermissions(adminId)
      if (!hasPermission) {
        throw new Error('Insufficient permissions to reset password')
      }

      // Generate temporary password
      const tempPassword = this.generateTempPassword()

      // Hash the password (in production, use proper hashing)
      const hashedPassword = await this.hashPassword(tempPassword)

      // Update user password
      const { error: passwordError } = await this.supabase
        .from('profiles')
        .update({
          password_hash: hashedPassword,
          password_reset_required: true,
          password_reset_by: adminId,
          password_reset_reason: reason,
          password_reset_at: new Date().toISOString()
        })
        .eq('id', targetUserId)

      if (passwordError) throw passwordError

      // Invalidate all user sessions
      await this.invalidateUserSessions(targetUserId)

      // Log admin action
      await this.logAdminAction(adminId, 'reset_password', [targetUserId], reason, {
        tempPassword_length: tempPassword.length
      })

      // Log security event
      await this.supabase
        .from('security_events')
        .insert({
          user_id: adminId,
          event_type: 'password_reset',
          severity: 'medium',
          message: `Password reset by admin: ${reason}`,
          metadata: {
            target_user_id: targetUserId
          },
          created_at: new Date().toISOString()
        })

      return tempPassword
    } catch (error) {
      console.error('Error resetting user password:', error)
      throw error
    }
  }

  /**
   * Force MFA reset for user
   */
  async forceMFAReset(
    adminId: string,
    targetUserId: string,
    reason: string
  ): Promise<void> {
    try {
      const hasPermission = await this.checkAdminPermissions(adminId)
      if (!hasPermission) {
        throw new Error('Insufficient permissions to reset MFA')
      }

      // Disable MFA for user
      const { error: mfaError } = await this.supabase
        .from('user_mfa')
        .update({
          totp_enabled: false,
          totp_secret: null,
          backup_codes: [],
          backup_codes_used: [],
          last_used_at: new Date().toISOString()
        })
        .eq('user_id', targetUserId)

      if (mfaError) throw mfaError

      // Log admin action
      await this.logAdminAction(adminId, 'force_mfa_reset', [targetUserId], reason, {})

      // Log security event
      await this.supabase
        .from('security_events')
        .insert({
          user_id: adminId,
          event_type: 'mfa_reset',
          severity: 'medium',
          message: `MFA reset by admin: ${reason}`,
          metadata: {
            target_user_id: targetUserId
          },
          created_at: new Date().toISOString()
        })
    } catch (error) {
      console.error('Error resetting MFA:', error)
      throw error
    }
  }

  /**
   * Create bulk operation
   */
  async createBulkOperation(
    adminId: string,
    operationType: 'suspend_users' | 'activate_users' | 'reset_passwords' | 'force_mfa_reset',
    targetUserIds: string[],
    reason: string
  ): Promise<BulkOperation> {
    try {
      const hasPermission = await this.checkAdminPermissions(adminId)
      if (!hasPermission) {
        throw new Error('Insufficient permissions for bulk operation')
      }

      const { data, error } = await this.supabase
        .from('bulk_operations')
        .insert({
          admin_id: adminId,
          operation_type: operationType,
          target_user_ids: targetUserIds,
          reason,
          total_count: targetUserIds.length,
          completed_count: 0,
          failed_count: 0,
          status: 'pending',
          results: []
        })
        .select('*')
        .single()

      if (error) throw error

      // Log admin action
      await this.logAdminAction(adminId, `bulk_${operationType}`, targetUserIds, reason, {
        total_count: targetUserIds.length
      })

      // Start processing in background
      this.processBulkOperation(data.id).catch(console.error)

      return data
    } catch (error) {
      console.error('Error creating bulk operation:', error)
      throw error
    }
  }

  /**
   * Process bulk operation
   */
  private async processBulkOperation(operationId: string): Promise<void> {
    try {
      // Update status to in_progress
      await this.supabase
        .from('bulk_operations')
        .update({
          status: 'in_progress',
          updated_at: new Date().toISOString()
        })
        .eq('id', operationId)

      // Get operation details
      const { data: operation } = await this.supabase
        .from('bulk_operations')
        .select('*')
        .eq('id', operationId)
        .single()

      if (!operation) return

      const results = []
      let completedCount = 0
      let failedCount = 0

      // Process each user
      for (const userId of operation.target_user_ids) {
        try {
          let result: any

          switch (operation.operation_type) {
            case 'suspend_users':
              await this.suspendUser(operation.admin_id, userId, operation.reason, 'temporary')
              result = { success: true }
              break
            case 'activate_users':
              await this.activateUser(operation.admin_id, userId, operation.reason)
              result = { success: true }
              break
            case 'reset_passwords':
              const tempPassword = await this.resetUserPassword(operation.admin_id, userId, operation.reason)
              result = { success: true, tempPassword }
              break
            case 'force_mfa_reset':
              await this.forceMFAReset(operation.admin_id, userId, operation.reason)
              result = { success: true }
              break
          }

          results.push({ user_id: userId, success: true, ...result })
          completedCount++
        } catch (error) {
          results.push({ user_id: userId, success: false, error: (error as Error).message })
          failedCount++
        }
      }

      // Update operation status
      const finalStatus = failedCount === 0 ? 'completed' : 'completed_with_errors'
      await this.supabase
        .from('bulk_operations')
        .update({
          status: finalStatus,
          completed_count: completedCount,
          failed_count: failedCount,
          results,
          updated_at: new Date().toISOString(),
          completed_at: new Date().toISOString()
        })
        .eq('id', operationId)

    } catch (error) {
      console.error('Error processing bulk operation:', error)
      
      // Mark as failed
      await this.supabase
        .from('bulk_operations')
        .update({
          status: 'failed',
          error_message: error.message,
          updated_at: new Date().toISOString()
        })
        .eq('id', operationId)
    }
  }

  /**
   * Get bulk operations
   */
  async getBulkOperations(
    adminId?: string,
    status?: string,
    limit: number = 50
  ): Promise<BulkOperation[]> {
    try {
      let query = this.supabase
        .from('bulk_operations')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(limit)

      if (adminId) {
        query = query.eq('admin_id', adminId)
      }

      if (status) {
        query = query.eq('status', status)
      }

      const { data, error } = await query

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting bulk operations:', error)
      throw error
    }
  }

  /**
   * Get user suspensions
   */
  async getUserSuspensions(
    targetUserId?: string,
    activeOnly: boolean = true
  ): Promise<UserSuspension[]> {
    try {
      let query = this.supabase
        .from('user_suspensions')
        .select('*')
        .order('created_at', { ascending: false })

      if (targetUserId) {
        query = query.eq('target_user_id', targetUserId)
      }

      if (activeOnly) {
        query = query.eq('is_active', true)
      }

      const { data, error } = await query

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting user suspensions:', error)
      throw error
    }
  }

  /**
   * Get manual interventions
   */
  async getManualInterventions(
    adminId?: string,
    status?: string,
    limit: number = 50
  ): Promise<ManualIntervention[]> {
    try {
      let query = this.supabase
        .from('manual_interventions')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(limit)

      if (adminId) {
        query = query.eq('admin_id', adminId)
      }

      if (status) {
        query = query.eq('status', status)
      }

      const { data, error } = await query

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting manual interventions:', error)
      throw error
    }
  }

  /**
   * Create manual intervention
   */
  async createManualIntervention(
    adminId: string,
    interventionType: string,
    targetUserId: string,
    reason: string,
    metadata: any = {}
  ): Promise<ManualIntervention> {
    try {
      const hasPermission = await this.checkAdminPermissions(adminId)
      if (!hasPermission) {
        throw new Error('Insufficient permissions for manual intervention')
      }

      const { data, error } = await this.supabase
        .from('manual_interventions')
        .insert({
          admin_id: adminId,
          interventionType,
          target_user_id: targetUserId,
          reason,
          metadata,
          status: 'pending'
        })
        .select('*')
        .single()

      if (error) throw error

      return data
    } catch (error) {
      console.error('Error creating manual intervention:', error)
      throw error
    }
  }

  /**
   * Get admin actions
   */
  async getAdminActions(
    adminId?: string,
    actionType?: string,
    status?: string,
    limit: number = 50
  ): Promise<AdminAction[]> {
    try {
      let query = this.supabase
        .from('admin_actions')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(limit)

      if (adminId) {
        query = query.eq('admin_id', adminId)
      }

      if (actionType) {
        query = query.eq('action_type', actionType)
      }

      if (status) {
        query = query.eq('status', status)
      }

      const { data, error } = await query

      if (error) throw error

      return data || []
    } catch (error) {
      console.error('Error getting admin actions:', error)
      throw error
    }
  }

  /**
   * Log admin action
   */
  private async logAdminAction(
    adminId: string,
    actionType: string,
    targetUserIds: string[],
    reason: string,
    metadata: any = {}
  ): Promise<void> {
    try {
      await this.supabase
        .from('admin_actions')
        .insert({
          admin_id: adminId,
          action_type: actionType,
          target_user_ids: targetUserIds,
          reason,
          metadata,
          status: 'completed',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          completed_at: new Date().toISOString()
        })
    } catch (error) {
      console.error('Error logging admin action:', error)
      // Don't throw error for logging failures
    }
  }

  /**
   * Generate temporary password
   */
  private generateTempPassword(): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
    let password = ''
    for (let i = 0; i < 12; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return password
  }

  /**
   * Hash password (placeholder - use proper hashing in production)
   */
  private async hashPassword(password: string): Promise<string> {
    // In production, use bcrypt or similar
    return `hashed_${password}`
  }

  /**
   * Invalidate all user sessions
   */
  private async invalidateUserSessions(userId: string): Promise<void> {
    try {
      await this.supabase
        .from('user_sessions')
        .update({
          is_active: false,
          last_accessed: new Date().toISOString()
        })
        .eq('user_id', userId)
    } catch (error) {
      console.error('Error invalidating user sessions:', error)
      // Don't throw error for cleanup failures
    }
  }

  /**
   * Get admin statistics
   */
  async getAdminStats(
    adminId?: string,
    days: number = 30
  ): Promise<{
    total_actions: number
    bulk_operations: number
    user_suspensions: number
    manual_interventions: number
    success_rate: number
    recent_activity: number
  }> {
    try {
      const since = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString()

      const [
        totalActions,
        bulkOperations,
        userSuspensions,
        manualInterventions,
        recentActivity
      ] = await Promise.all([
        this.supabase
          .from('admin_actions')
          .select('id', { count: 'exact', head: true })
          .gte('created_at', since)
          .eq(adminId ? 'admin_id' : adminId, adminId),
        this.supabase
          .from('bulk_operations')
          .select('id', { count: 'exact', head: true })
          .gte('created_at', since)
          .eq(adminId ? 'admin_id' : adminId, adminId),
        this.supabase
          .from('user_suspensions')
          .select('id', { count: 'exact', head: true })
          .gte('created_at', since),
        this.supabase
          .from('manual_interventions')
          .select('id', { count: 'exact', head: true })
          .gte('created_at', since)
          .eq(adminId ? 'admin_id' : adminId, adminId),
        this.supabase
          .from('admin_actions')
          .select('id', { count: 'exact', head: true })
          .gte('created_at', since)
          .eq(adminId ? 'admin_id' : adminId, adminId)
      ])

      return {
        total_actions: totalActions || 0,
        bulk_operations: bulkOperations || 0,
        user_suspensions: userSuspensions || 0,
        manual_interventions: manualInterventions || 0,
        success_rate: 95, // Placeholder - would calculate from actual data
        recent_activity: recentActivity || 0
      }
    } catch (error) {
      console.error('Error getting admin stats:', error)
      throw error
    }
  }

  /**
   * Clean up old records
   */
  async cleanupOldRecords(daysOld: number = 90): Promise<{
    adminActions: number
    bulkOperations: number
    userSuspensions: number
    manualInterventions: number
  }> {
    try {
      const cutoffDate = new Date(Date.now() - daysOld * 24 * 60 * 60 * 1000).toISOString()

      const [
        adminActions,
        bulkOperations,
        userSuspensions,
        manualInterventions
      ] = await Promise.all([
        this.supabase
          .from('admin_actions')
          .delete()
          .lt('created_at', cutoffDate),
        this.supabase
          .from('bulk_operations')
          .delete()
          .lt('created_at', cutoffDate),
        this.supabase
          .from('user_suspensions')
          .delete()
          .lt('created_at', cutoffDate),
        this.supabase
          .from('manual_interventions')
          .delete()
          .lt('created_at', cutoffDate)
      ])

      return {
        adminActions: adminActions || 0,
        bulkOperations: bulkOperations || 0,
        userSuspensions: userSuspensions || 0,
        manualInterventions: manualInterventions || 0
      }
    } catch (error) {
      console.error('Error cleaning up old records:', error)
      return {
        adminActions: 0,
        bulkOperations: 0,
        userSuspensions: 0,
        manualInterventions: 0
      }
    }
  }
}

export const adminActions = new AdminActions()
