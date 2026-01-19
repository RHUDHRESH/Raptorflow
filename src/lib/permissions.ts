import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

// Permission types
export interface Permission {
  id: string
  name: string
  resource: string
  action: string
  description?: string
  category: string
  is_system: boolean
  created_at: string
  updated_at: string
}

export interface UserPermission {
  permission_name: string
  resource: string
  action: string
  description?: string
  category: string
  granted_at: string
  expires_at?: string
  is_user_specific: boolean
}

export interface PermissionCheck {
  hasPermission: boolean
  source: 'user_specific' | 'role_based' | 'group_based' | 'none'
  expires_at?: string
}

// Server-side permission checking
export async function checkPermission(
  permissionName: string,
  userId?: string
): Promise<PermissionCheck> {
  const cookieStore = cookies()
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { getAll: () => cookieStore.getAll(), setAll: () => {} } }
  )

  try {
    // If userId not provided, get current user
    if (!userId) {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) return { hasPermission: false, source: 'none' }
      
      const { data: dbUser } = await supabase
        .from('users')
        .select('id')
        .eq('auth_user_id', user.id)
        .single()
      
      userId = dbUser?.id
    }

    if (!userId) return { hasPermission: false, source: 'none' }

    // Check user-specific permissions first
    const { data: userPermission } = await supabase
      .rpc('user_has_permission', {
        p_user_id: userId,
        p_permission_name: permissionName
      })

    return {
      hasPermission: !!userPermission,
      source: userPermission ? 'user_specific' : 'none'
    }

  } catch (error) {
    console.error('Permission check error:', error)
    return { hasPermission: false, source: 'none' }
  }
}

// Get all permissions for a user
export async function getUserPermissions(userId: string): Promise<UserPermission[]> {
  const cookieStore = cookies()
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { getAll: () => cookieStore.getAll(), setAll: () => {} } }
  )

  try {
    const { data, error } = await supabase
      .rpc('get_user_permissions', {
        p_user_id: userId
      })

    if (error) throw error
    return data || []

  } catch (error) {
    console.error('Get user permissions error:', error)
    return []
  }
}

// Grant permission to user
export async function grantPermission(
  userId: string,
  permissionName: string,
  granted: boolean = true,
  expiresAt?: string,
  reason?: string
): Promise<boolean> {
  const cookieStore = cookies()
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { getAll: () => cookieStore.getAll(), setAll: () => {} } }
  )

  try {
    const { data, error } = await supabase
      .rpc('grant_user_permission', {
        p_user_id: userId,
        p_permission_name: permissionName,
        p_granted: granted,
        p_expires_at: expiresAt,
        p_reason: reason
      })

    if (error) throw error
    return !!data

  } catch (error) {
    console.error('Grant permission error:', error)
    return false
  }
}

// Get all available permissions
export async function getAllPermissions(): Promise<Permission[]> {
  const cookieStore = cookies()
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { getAll: () => cookieStore.getAll(), setAll: () => {} } }
  )

  try {
    const { data, error } = await supabase
      .from('permissions')
      .select('*')
      .order('category, name')

    if (error) throw error
    return data || []

  } catch (error) {
    console.error('Get permissions error:', error)
    return []
  }
}

// Permission categories for UI organization
export const PERMISSION_CATEGORIES = {
  user: 'User Management',
  workspace: 'Workspace Management',
  icp: 'ICP Profiles',
  campaign: 'Campaigns',
  analytics: 'Analytics',
  admin: 'System Administration',
  billing: 'Billing Management',
  support: 'Customer Support',
  general: 'General'
} as const

// Common permission checks
export const PERMISSIONS = {
  // User permissions
  READ_OWN_PROFILE: 'read:own_profile',
  WRITE_OWN_PROFILE: 'write:own_profile',
  DELETE_OWN_ACCOUNT: 'delete:own_account',
  
  // Workspace permissions
  READ_OWN_WORKSPACE: 'read:own_workspace',
  WRITE_OWN_WORKSPACE: 'write:own_workspace',
  DELETE_OWN_WORKSPACE: 'delete:own_workspace',
  INVITE_WORKSPACE_MEMBERS: 'invite:workspace_members',
  MANAGE_WORKSPACE_MEMBERS: 'manage:workspace_members',
  
  // ICP permissions
  READ_ICP_PROFILES: 'read:icp_profiles',
  WRITE_ICP_PROFILES: 'write:icp_profiles',
  DELETE_ICP_PROFILES: 'delete:icp_profiles',
  
  // Campaign permissions
  READ_CAMPAIGNS: 'read:campaigns',
  WRITE_CAMPAIGNS: 'write:campaigns',
  DELETE_CAMPAIGNS: 'delete:campaigns',
  
  // Analytics permissions
  READ_ANALYTICS: 'read:analytics',
  EXPORT_ANALYTICS: 'export:analytics',
  
  // Admin permissions
  ADMIN_READ_USERS: 'admin:read_users',
  ADMIN_WRITE_USERS: 'admin:write_users',
  ADMIN_DELETE_USERS: 'admin:delete_users',
  ADMIN_READ_WORKSPACES: 'admin:read_workspaces',
  ADMIN_MANAGE_SUBSCRIPTIONS: 'admin:manage_subscriptions',
  ADMIN_READ_AUDIT_LOGS: 'admin:read_audit_logs',
  ADMIN_MANAGE_PERMISSIONS: 'admin:manage_permissions',
  ADMIN_SYSTEM_MONITORING: 'admin:system_monitoring',
  
  // Billing permissions
  BILLING_READ_SUBSCRIPTIONS: 'billing:read_subscriptions',
  BILLING_WRITE_SUBSCRIPTIONS: 'billing:write_subscriptions',
  BILLING_PROCESS_REFUNDS: 'billing:process_refunds',
  BILLING_READ_TRANSACTIONS: 'billing:read_transactions',
  
  // Support permissions
  SUPPORT_READ_USERS: 'support:read_users',
  SUPPORT_READ_WORKSPACES: 'support:read_workspaces',
  SUPPORT_MANAGE_TICKETS: 'support:manage_tickets'
} as const

// Permission groups for easier management
export const PERMISSION_GROUPS = {
  BASIC_USER: [
    PERMISSIONS.READ_OWN_PROFILE,
    PERMISSIONS.WRITE_OWN_PROFILE,
    PERMISSIONS.DELETE_OWN_ACCOUNT,
    PERMISSIONS.READ_OWN_WORKSPACE,
    PERMISSIONS.WRITE_OWN_WORKSPACE,
    PERMISSIONS.DELETE_OWN_WORKSPACE,
    PERMISSIONS.READ_ICP_PROFILES,
    PERMISSIONS.WRITE_ICP_PROFILES,
    PERMISSIONS.DELETE_ICP_PROFILES,
    PERMISSIONS.READ_CAMPAIGNS,
    PERMISSIONS.WRITE_CAMPAIGNS,
    PERMISSIONS.DELETE_CAMPAIGNS,
    PERMISSIONS.READ_ANALYTICS,
    PERMISSIONS.EXPORT_ANALYTICS
  ],
  
  WORKSPACE_ADMIN: [
    ...Object.values(PERMISSIONS).filter(p => 
      !p.startsWith('admin:') && 
      !p.startsWith('billing:') && 
      !p.startsWith('support:')
    )
  ],
  
  SYSTEM_ADMIN: Object.values(PERMISSIONS),
  
  BILLING_MANAGER: [
    PERMISSIONS.READ_OWN_PROFILE,
    PERMISSIONS.WRITE_OWN_PROFILE,
    PERMISSIONS.DELETE_OWN_ACCOUNT,
    PERMISSIONS.READ_OWN_WORKSPACE,
    PERMISSIONS.WRITE_OWN_WORKSPACE,
    PERMISSIONS.BILLING_READ_SUBSCRIPTIONS,
    PERMISSIONS.BILLING_WRITE_SUBSCRIPTIONS,
    PERMISSIONS.BILLING_PROCESS_REFUNDS,
    PERMISSIONS.BILLING_READ_TRANSACTIONS
  ],
  
  SUPPORT_AGENT: [
    PERMISSIONS.READ_OWN_PROFILE,
    PERMISSIONS.WRITE_OWN_PROFILE,
    PERMISSIONS.DELETE_OWN_ACCOUNT,
    PERMISSIONS.READ_OWN_WORKSPACE,
    PERMISSIONS.WRITE_OWN_WORKSPACE,
    PERMISSIONS.SUPPORT_READ_USERS,
    PERMISSIONS.SUPPORT_READ_WORKSPACES,
    PERMISSIONS.SUPPORT_MANAGE_TICKETS
  ]
} as const

// Helper function to check if user has any of the specified permissions
export async function hasAnyPermission(
  permissionNames: string[],
  userId?: string
): Promise<PermissionCheck> {
  for (const permission of permissionNames) {
    const check = await checkPermission(permission, userId)
    if (check.hasPermission) {
      return check
    }
  }
  
  return { hasPermission: false, source: 'none' }
}

// Helper function to check if user has all specified permissions
export async function hasAllPermissions(
  permissionNames: string[],
  userId?: string
): Promise<PermissionCheck> {
  for (const permission of permissionNames) {
    const check = await checkPermission(permission, userId)
    if (!check.hasPermission) {
      return check
    }
  }
  
  return { hasPermission: true, source: 'user_specific' }
}
