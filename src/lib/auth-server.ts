import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import type { Session, User as SupabaseUser } from '@supabase/supabase-js'
import { getBaseUrl } from './env-utils'

// =============================================================================
// SERVER-SIDE FUNCTIONS
// =============================================================================

/**
 * Get Supabase client for server-side usage
 */
export function createServerSupabaseClient() {
  const cookieStore = cookies()
  
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          } catch {
            // The `setAll` method was called from a Server Component.
            // This can be ignored if you have middleware refreshing
            // user sessions.
          }
        },
      },
    }
  )
}

/**
 * Get server session
 */
export async function getServerSession(): Promise<Session | null> {
  const supabase = createServerSupabaseClient()
  const { data: { session } } = await supabase.auth.getSession()
  return session
}

/**
 * Get server user
 */
export async function getServerUser(): Promise<SupabaseUser | null> {
  const supabase = createServerSupabaseClient()
  const { data: { user } } = await supabase.auth.getUser()
  return user
}

/**
 * Get current user from database (server-side)
 */
export async function getCurrentUserFromDB() {
  const session = await getServerSession()
  
  if (!session) {
    return null
  }
  
  const supabase = createServerSupabaseClient()
  const { data: user } = await supabase
    .from('users')
    .select('*')
    .eq('auth_user_id', session.user.id)
    .single()
  
  return user
}

/**
 * Require authentication - redirects to login if not authenticated
 */
export async function requireAuth(): Promise<Session> {
  const session = await getServerSession()
  
  if (!session) {
    redirect('/login')
  }
  
  return session
}

/**
 * Require onboarding completion - redirects based on status
 */
export async function requireOnboarding(step?: string) {
  const session = await requireAuth()
  const supabase = createServerSupabaseClient()
  
  const { data: user } = await supabase
    .from('users')
    .select('onboarding_status')
    .eq('auth_user_id', session.user.id)
    .single()
  
  if (!user) {
    redirect('/login')
  }
  
  // If user is fully onboarded, redirect to dashboard
  if (user.onboarding_status === 'active') {
    redirect('/dashboard')
  }
  
  // If specific step is required and user is not at that step
  if (step && user.onboarding_status !== step) {
    const redirectPath = getRedirectPath(user.onboarding_status)
    redirect(redirectPath)
  }
  
  return { session, user }
}

/**
 * Require active user - checks for banned/inactive status
 */
export async function requireActiveUser() {
  const session = await requireAuth()
  const supabase = createServerSupabaseClient()
  
  const { data: user } = await supabase
    .from('users')
    .select('onboarding_status, is_active, is_banned')
    .eq('auth_user_id', session.user.id)
    .single()
  
  if (!user) {
    redirect('/login')
  }
  
  if (user.is_banned) {
    redirect('/account/banned')
  }
  
  if (!user.is_active) {
    redirect('/account/inactive')
  }
  
  if (user.onboarding_status !== 'active') {
    const redirectPath = getRedirectPath(user.onboarding_status)
    redirect(redirectPath)
  }
  
  return { session, user }
}

/**
 * Require admin role
 */
export async function requireAdmin() {
  const session = await requireAuth()
  const supabase = createServerSupabaseClient()
  
  const { data: user } = await supabase
    .from('users')
    .select('role')
    .eq('auth_user_id', session.user.id)
    .single()
  
  if (!user || !['admin', 'super_admin', 'support', 'billing_admin'].includes(user.role)) {
    redirect('/unauthorized')
  }
  
  return { session, user }
}

/**
 * Check if user has specific permission
 */
export async function hasPermission(permission: string): Promise<boolean> {
  const supabase = createServerSupabaseClient()
  const session = await getServerSession()
  
  if (!session) {
    return false
  }
  
  const { data: user } = await supabase
    .from('users')
    .select('role')
    .eq('auth_user_id', session.user.id)
    .single()
  
  if (!user) {
    return false
  }
  
  // Super admin has all permissions
  if (user.role === 'super_admin') {
    return true
  }
  
  // Define role permissions
  const rolePermissions: Record<string, string[]> = {
    admin: ['read:users', 'write:users', 'read:subscriptions', 'write:subscriptions', 'read:payments', 'read:audit_logs'],
    billing_admin: ['read:users', 'read:subscriptions', 'write:subscriptions', 'read:payments', 'refund:payments'],
    support: ['read:users', 'read:subscriptions'],
    user: [],
  }
  
  const permissions = rolePermissions[user.role] || []
  
  return permissions.includes(permission) || permissions.includes('*')
}

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Get redirect path based on onboarding status
 */
export function getRedirectPath(status: string): string {
  switch (status) {
    case 'pending_workspace':
      return '/onboarding'
    case 'pending_storage':
      return '/onboarding/storage'
    case 'pending_plan_selection':
      return '/onboarding/plans'
    case 'pending_payment':
      return '/onboarding/payment'
    case 'active':
      return '/dashboard'
    case 'suspended':
      return '/account/suspended'
    case 'cancelled':
      return '/account/reactivate'
    default:
      return '/onboarding'
  }
}
